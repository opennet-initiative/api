import re
import socket
import ssl
import urllib.error
import urllib.request

from django.core.management.base import BaseCommand

from on_geronimo.oni_model.models import AccessPoint


VERSION_05 = re.compile(
    br'<h2><a id="content" name="content">Opennet[ -]Firmware [Vv]ersion ([^ ]+)')
AIROS_IDENTIFIER_MAP = {
    b"/110411.1153/login.css": "opennet0.2.sdk",
    b"/110622.1735/login.css": "opennet0.4.sdk",
    b"/110904.1324/login.css": "opennet0.4.sdk",
    b"/111102.1143/login.css": "opennet0.5.sdk",
    # real version string: oni_v0.1.9634.120804.0933
    b"/120803.2222/login.css": "opennet0.6.sdk",
    # real version string: XM.v5.5.8.0xFF.v29
    b"/140123.1659/login.css": "opennet0.7.sdk",
}


def _retrieve_body_from_url(url, timeout):
    ctx = ssl.SSLContext()
    ctx.check_hostname = False
    try:
        response = urllib.request.urlopen(url, timeout=timeout, context=ctx)
    except urllib.error.HTTPError:
        # not found or some other failure
        return None
    except urllib.error.URLError:
        # invalid URL or a connection issue (no route, refused, ...)
        return None
    except socket.timeout:
        # SSL connection timeout
        return None
    return response.read()


def parse_firmware_version_via_status_page(host, timeout=5):
    luci_status_body = _retrieve_body_from_url("http://{}/cgi-bin/luci".format(host), timeout)
    if luci_status_body:
        match = VERSION_05.search(luci_status_body)
        if match:
            return match.groups()[0].decode()
    airos_login_body = _retrieve_body_from_url("http://{}/login.cgi".format(host), timeout)
    if airos_login_body:
        for match_key, version in AIROS_IDENTIFIER_MAP.items():
            if match_key in airos_login_body:
                return version
    return None


class Command(BaseCommand):

    help = "Ermitteln der Firmware-Version eines AccessPoint durch Parsen der Status-Seite"

    def handle(self, *args, **options):
        for ap in AccessPoint.online_objects.filter(opennet_version__isnull=True):
            parsed_version = parse_firmware_version_via_status_page(ap.main_ip)
            if parsed_version is not None:
                print("Parsed version from {}: {}".format(ap.main_ip, parsed_version),
                      file=self.stdout)
                ap.opennet_version = parsed_version
                ap.save()
            else:
                print("Failed to retrieve or parse version from {}".format(ap.main_ip),
                      file=self.stderr)

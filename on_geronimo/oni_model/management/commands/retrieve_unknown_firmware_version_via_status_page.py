import re
import socket
import ssl
import urllib.error
import urllib.request

from django.core.management.base import BaseCommand

from on_geronimo.oni_model.models import AccessPoint


VERSION_05 = re.compile(
    br'<h2><a id="content" name="content">Opennet[ -]Firmware [Vv]ersion ([^ ]+)')


def parse_firmware_version_via_status_page(host, timeout=5):
    ctx = ssl.SSLContext()
    ctx.check_hostname = False
    try:
        response = urllib.request.urlopen("http://{}/cgi-bin/luci".format(host), timeout=timeout,
                                          context=ctx)
    except urllib.error.HTTPError:
        # not found or some other failure
        return None
    except urllib.error.URLError:
        # invalid URL or a connection issue (no route, refused, ...)
        return None
    except socket.timeout:
        # SSL connection timeout
        return None
    body = response.read()
    match = VERSION_05.search(body)
    if match:
        return match.groups()[0].decode()
    else:
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

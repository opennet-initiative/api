import asyncio
import collections
import contextlib
import json
import ssl
import sys
import urllib

import aiohttp
from django.db import transaction

from on_geronimo.data_import.import_ondataservice import (import_accesspoint,
                                                          import_network_interface)
from on_geronimo.oni_model.models import AccessPoint


CONNECTION_TIMEOUT = 5


OndataserviceResult = collections.namedtuple(
    "OndataserviceResult", ("accesspoint", "accesspoint_data", "interfaces_data"))


@contextlib.contextmanager
def suppress_ssl_exception_report():
    """ work around a bug regarding logging in Python's SSL handling

    see https://bugs.python.org/issue34506
    """
    loop = asyncio.get_event_loop()
    old_handler = loop.get_exception_handler()
    if old_handler is None:
        old_handler_fn = lambda _loop, ctx: loop.default_exception_handler(ctx)
    else:
        old_handler_fn = old_handler

    def ignore_exc(_loop, ctx):
        exc = ctx.get('exception')
        if isinstance(exc, ssl.SSLError):
            return
        old_handler_fn(loop, ctx)

    loop.set_exception_handler(ignore_exc)
    try:
        yield
    finally:
        loop.set_exception_handler(old_handler)


class OndataserviceParseError(ValueError):
    """ any problem encountered while reading and parsing the ondataservice content """


class TemporaryRetrievalError(ValueError):
    """ a non-deterministic problem encountered while reading the ondataservice content """


def parse_body(body):
    accesspoint_data = None
    interfaces_data = []
    for line in body.strip().splitlines():
        line = line.replace(b"\t", b" ")
        try:
            line_data = json.loads(line)
        except ValueError:
            raise OndataserviceParseError("Failed to parse JSON line: {}".format(line))
        if "nodes" in line_data:
            if accesspoint_data is not None:
                raise OndataserviceParseError("Encountered multiple 'nodes' items")
            accesspoint_data = line_data["nodes"]
        elif "ifaces" in line_data:
            interfaces_data.append(line_data["ifaces"])
        else:
            raise OndataserviceParseError("Encountered line without a known key: {}"
                                          .format(" / ".join(line_data.keys())))
    if accesspoint_data is None:
        raise OndataserviceParseError("Missing 'nodes' item")
    return accesspoint_data, interfaces_data


async def download_and_parse_json(http_client, url, use_async):
    if use_async:
        for context in (ssl.SSLContext(), ssl.SSLContext(ssl.PROTOCOL_TLSv1)):
            try:
                async with http_client.get(
                        url, ssl=context, allow_redirects=False, chunked=0,
                        timeout=aiohttp.ClientTimeout(sock_connect=CONNECTION_TIMEOUT,
                                                      sock_read=CONNECTION_TIMEOUT)) as response:
                    if response.status != 200:
                        continue
                    try:
                        body = await response.read()
                    except aiohttp.client_exceptions.ClientPayloadError:
                        raise TemporaryRetrievalError("Failed to read the full body")
                    else:
                        # the data was retrieved successfully
                        break
            except ssl.SSLError:
                pass
            except aiohttp.client_exceptions.ClientResponseError as exc:
                if (exc.code == 400) and (exc.message == "unexpected content-length header"):
                    raise TemporaryRetrievalError(
                        "Failed to handle response headers cleanly from {}: {}".format(url, exc))
                else:
                    raise OndataserviceParseError(
                        "Failed to download ondataservice data from {}: {}".format(url, exc))
        raise TemporaryRetrievalError("Failed to connect")
    else:
        ssl_no_check_context = ssl.create_default_context()
        ssl_no_check_context.check_hostname = False
        ssl_no_check_context.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(url, context=ssl_no_check_context,
                                        timeout=CONNECTION_TIMEOUT) as request:
                body = request.read()
        except (ssl.SSLError, OSError):
            raise TemporaryRetrievalError("Failed to Connect")
    return parse_body(body)


async def retrieve_ondataservice_worker(incoming_queue, results, failures, stdout, stderr):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200,
                                                                   connect=1200)) as http_client:
        while True:
            try:
                accesspoint = incoming_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            https_url = "https://{}/opennet-ondataservice-export.json".format(accesspoint.main_ip)
            http_url = "http://{}/opennet-ondataservice-export.json".format(accesspoint.main_ip)
            for url, use_async in ((https_url, True),
                                   (http_url, True),
                                   (https_url, False),
                                   (http_url, False)):
                try:
                    for _ in range(3):
                        # retry in case of temporary errors
                        try:
                            node_data, interfaces_data = await download_and_parse_json(
                                http_client, url, use_async)
                            break
                        except aiohttp.client_exceptions.ServerDisconnectedError:
                            pass
                        except TemporaryRetrievalError:
                            pass
                    else:
                        continue
                except OndataserviceParseError as exc:
                    print("Failed to parse ondataservice data for {}: {}"
                          .format(accesspoint.main_ip, exc))
                    failures.append("parse")
                    incoming_queue.task_done()
                    break
                except aiohttp.client_exceptions.ClientOSError:
                    pass
                except aiohttp.client_exceptions.ClientConnectorError:
                    # something like "no connection to host"
                    failures.append("no connect")
                    incoming_queue.task_done()
                    break
                except (ssl.SSLError, aiohttp.client_exceptions.ServerTimeoutError):
                    # some kind of connection error
                    pass
                else:
                    print("Finished downloading ondataservice dataset via http from: {}"
                          .format(accesspoint.main_ip), file=stdout)
                    await results.put(OndataserviceResult(accesspoint, node_data, interfaces_data))
                    incoming_queue.task_done()
                    # the download finished successfully - go for the next item
                    break
            else:
                print("Failed to download ondataservice dataset via http from {}"
                      .format(accesspoint.main_ip), file=stderr)
                failures.append("download")
                incoming_queue.task_done()


@transaction.atomic
@suppress_ssl_exception_report()
def import_from_ondataservice_via_http(parallel_count=20, dry_run=False, stdout=sys.stdout,
                                       stderr=sys.stderr):
    loop = asyncio.get_event_loop()
    unprocessed_accesspoints = asyncio.Queue()
    results = []
    failures = []
    for accesspoint in AccessPoint.online_objects.order_by("main_ip"):
        unprocessed_accesspoints.put_nowait(accesspoint)

    async def retrieve_from_all():
        parsed_accesspoints = asyncio.Queue()
        async def handle_incoming_results():
            while True:
                item = await parsed_accesspoints.get()
                if item is None:
                    break
                else:
                    if dry_run:
                        print("{}: {}".format(item.accesspoint_data["on_olsr_mainip"],
                                              " | ".join(" ".join(iface["ip_addr"].split()[:1])
                                                         for iface in item.interfaces_data)))
                    else:
                        import_accesspoint(item.accesspoint_data)
                        for iface_data in item.interfaces_data:
                            import_network_interface(item.accesspoint.main_ip, iface_data)
                results.append(item)

        injection_task = asyncio.ensure_future(handle_incoming_results())
        await asyncio.gather(*[
            asyncio.ensure_future(retrieve_ondataservice_worker(
                unprocessed_accesspoints, parsed_accesspoints, failures, stdout, stderr))
            for _ in range(parallel_count)])
        await parsed_accesspoints.put(None)
        asyncio.gather(injection_task)
    loop.run_until_complete(retrieve_from_all())
    loop.close()
    print("Successes: {:d}".format(len(results)))
    print("Download failures: {:d}".format(failures.count("download")))
    print("No connect: {:d}".format(failures.count("no connect")))
    print("Parse failures: {:d}".format(failures.count("parse")))


if __name__ == "__main__":
    import_from_ondataservice_via_http(dry_run=True)

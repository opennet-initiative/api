#!/usr/bin/python3
#
# JSON generator for Freifunk API nodelist specification:
#    https://github.com/freifunk/api.freifunk.net/
#
# Data source: geronimo (v2) API
#

import datetime
import json
import os
import urllib.request

import iso8601


GERONIMO_API_URL = os.getenv("GERONIMO_API", "https://api.on-i.de/api/v1/accesspoint/")
MAX_AP_ALIVE_TIMEOUT = datetime.timedelta(minutes=15)


def get_accesspoints():
    source = urllib.request.urlopen(GERONIMO_API_URL)
    data = source.read().decode("utf-8")
    return json.loads(data)


def get_freifunk_nodes():
    result = []
    for ap in get_accesspoints():
        last_seen_timestamp = iso8601.iso8601.parse_date(ap["lastseen_timestamp"])
        now_utc = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
        is_alive = (now_utc - last_seen_timestamp > MAX_AP_ALIVE_TIMEOUT)
        if ap["position"]:
            position = {"lon": ap["position"]["coordinates"][0],
                        "lat": ap["position"]["coordinates"][1]}
        else:
            position = None
        item = {"id": ap["main_ip"],
                "name": ap["main_ip"],
                "node_type": "AccessPoint",
                "status": {"online": is_alive, "lastcontact": last_seen_timestamp.isoformat()},
                "position": position}
        result.append(item)
    return result


def get_freifunk_api_nodelist():
    dataset = {"version": "1.0.0",
               "updated_at": datetime.datetime.now().isoformat(),
               "community": {
                   "href": "https://api.opennet-initiative.de/freifunk/dynamic/nodelist.json",
                   "name": "Opennet Initiative e.V.",
               },
               "nodes": get_freifunk_nodes()}
    return json.dumps(dataset, indent=4)


if __name__ == "__main__":
    print(get_freifunk_api_nodelist())

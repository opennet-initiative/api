#!/bin/bash

#
# Opennet Geronimo Scripts
# Martin Garbe, created 2014/12/31
# Mathias Mahnke, reworked 2015/01/01
# Opennet Admin Group <admin@opennet-initiative.de>
#

# This scripts generates Freifunk Nodelist API JSON
# see also https://wiki.opennet-initiative.de/wiki/Freifunk_API
#
# Data source: geronimo (v1) API
#

# stop on error and unset variables
set -eu


GERONIMO_API=${GERONIMO_API:-http://www.opennet-initiative.de/api/}

# get current script dir
HOME="$(dirname "$(readlink -f "$0")")"


# Convert old API timestamps from Geronimo v1 (UTC) to ISO format
# Consume JSON data (dictionary of "online" and "offline" nodes) from stdin.
# Output result on stdout.
#   source time format: 23.09.2017 (15:21:05)
#   target time format: 2017-09-23T15:21:05UTC
format_geronimo_v1_date_to_iso() {
    python3 -c '
import datetime
import json
import sys

def date_converter(orig):
    return datetime.datetime.strptime(orig, "%d.%m.%Y (%H:%M:%S)").isoformat() + "UTC"

nodes = json.load(sys.stdin)
for node in nodes:
    contact_raw = node["status"]["lastcontact"]
    node["status"]["lastcontact"] = date_converter(contact_raw)
print(json.dumps(nodes))'
}


# translate the old (geronimo v1) API into the freifunk API specification
get_geronimo_v1_nodelist() {
    {
        echo '{ "online": '
        wget -q -O - "$GERONIMO_API/nodes/online" | jq '[.features[] | {
            id: .properties.id,
            name: .properties.id,
            node_type: "AccessPoint",
            status: {
                online: true,
                lastcontact: .properties.lastonline
            },
            position: {
                lat: .geometry.coordinates[1],
                lon: .geometry.coordinates[0]
            }
          }
        ]'

        # process list of offline nodes
        echo ', "offline": '
        wget -q -O - "$GERONIMO_API/nodes/offline" | jq '[.features[] | {
            id: .properties.id,
            name: .properties.id,
            node_type: "AccessPoint",
            status: {
                online: false,
                lastcontact: .properties.lastonline
            },
            position: {
                lat: .geometry.coordinates[1],
                lon: .geometry.coordinates[0]
            }
          }
        ]'
        echo "}"
    # merge the "online" and the "offline" lists into a flat one
    } | jq "add"
}


generate_json_nodelist() {
    get_geronimo_v1_nodelist | format_geronimo_v1_date_to_iso
}


add_header_and_footer() {
    local date
    date=$(date "+%Y-%m-%d %H:%M")
    echo '{
        "version": "1.0.0",
        "updated_at": "'"$date"'",
        "community": {
            "href": "https://api.opennet-initiative.de/freifunk/dynamic/nodelist.json",
            "name": "Opennet Initiative e.V."
        },
        "nodes": '
    # insert the generated list of nodes
    cat
    echo "}"
}


# the final "jq" adds pretty linebreaks into the JSON data
generate_json_nodelist | add_header_and_footer | jq "."

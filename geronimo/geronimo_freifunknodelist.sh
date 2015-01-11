#!/bin/bash

#
# Opennet Geronimo Scripts
# Martin Garbe, created 2014/12/31
# Mathias Mahnke, reworked 2015/01/01
# Opennet Admin Group <admin@opennet-initiative.de>
#

# This scripts generates Freifunk Nodelist API JSON
# see also https://wiki.opennet-initiative.de/wiki/Freifunk_API

# stop on error and unset variables
set -eu

# config file
CFG=geronimo_freifunknodelist.cfg

# get current script dir
HOME="$(dirname $(readlink -f "$0"))"

# read variables
. "$HOME/$CFG"

# process list of online nodes
wget -q "$GERONIMO_API/nodes/online" -O "$TMP_ONLINE"
echo "{ \"online\": " > "$TMP_OUTPUT" 
cat "$TMP_ONLINE" | jq '[.features[] | {
    id: .properties.id,
    name: .properties.id,
    node_type: "AccessPoint",
    status: {
        online: "true",
        lastcontact: .properties.lastonline
    }, 
    position: {
        lat: .geometry.coordinates[1],
        lon: .geometry.coordinates[0]
    }
  }
]' >> "$TMP_OUTPUT"

# process list of offline nodes
wget -q "$GERONIMO_API/nodes/offline" -O "$TMP_OFFLINE"
echo ", \"offline\": " >> "$TMP_OUTPUT"
cat "$TMP_OFFLINE" | jq '[.features[] | {
    id: .properties.id,
    name: .properties.id,
    node_type: "AccessPoint",
    status: {
        online: "false",
        lastcontact: .properties.lastonline
    }, 
    position: {
        lat: .geometry.coordinates[1],
        lon: .geometry.coordinates[0]
    	}
  }
]' >> "$TMP_OUTPUT"
echo "}" >> "$TMP_OUTPUT"

# output to stdout, add header and trailer
date=$(date "+%Y-%m-%d %H:%M")
echo '{
    "version": "1.0.0",
    "updated_at": "'$date'",
    "community": {
        "href": "https://www.opennet-initiative.de/freifunk/api.freifunk.net-nodelist.json",
        "name": "Opennet Initiative e.V."
    },
    "nodes": ' > "$TMP_RESULT"
cat "$TMP_OUTPUT" | jq 'add' >> "$TMP_RESULT"
echo "}" >> "$TMP_RESULT"
cat "$TMP_RESULT" | jq '.'

# clear temporary files
rm "$TMP_ONLINE"
rm "$TMP_OFFLINE"
rm "$TMP_OUTPUT"
rm "$TMP_RESULT"

exit 0

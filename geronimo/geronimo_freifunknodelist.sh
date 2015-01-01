#!/bin/bash

##
## +++ Geronimo +++ 
## Opennet Datawarehouse + API
## geronimo_freifunknodelist.sh
## Freifunk Nodelist API Generator
##

# This script generates a list of online node compatible with Freifunk API
# see http://freifunk.net/en/blog/2014/02/the-freifunk-api/
# Format to output: https://gist.githubusercontent.com/StilgarBF/c21826994b775787f739/raw/71944597080bd05bb970534afcc1f0c347fab1a8/gistfile1.js
#
# In addition a "daily?" cronjob has to create the input file and execute this script.
#

# process list of online nodes
# see http://www.opennet-initiative.de/api/nodes/online
wget -q http://www.opennet-initiative.de/api/nodes/online -O /tmp/freifunk-api-input.json
cat /tmp/freifunk-api-input.json | jq '[.features[] |
  {
    id: .properties.id,
    name: .properties.id,
    node_type: "AccessPoint",
    status: {
        online: "true",
        lastcontact: .properties.lastonline
        } ,
    position: {
        lat: .geometry.coordinates[1],
        lon: .geometry.coordinates[0]
    }
  }
]' > /tmp/freifunk-api-output.json

# output to stdout, add header and trailer
date=$(date "+%Y-%m-%d %H:%M")
echo '{
    "version": "1.0.0",
    "updated_at": "'$date'",
    "community": {
        "href": "https://www.opennet-initiative.de/freifunk/freifunk-api-nodelist.json",
        "name": "Opennet Initiative e.V."
    },
    "nodes": '
cat /tmp/freifunk-api-output.json
echo "}" 

# clear temporary files
rm /tmp/freifunk-api-input.json
rm /tmp/freifunk-api-output.json

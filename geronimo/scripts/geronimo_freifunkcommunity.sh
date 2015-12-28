#!/bin/bash

#
# Opennet Geronimo Scripts
# Mathias Mahnke, created 2015/12/27
# Opennet Admin Group <admin@opennet-initiative.de>
#

# This scripts generates Freifunk Community API JSON
# see also https://wiki.opennet-initiative.de/wiki/Freifunk_API

# stop on error and unset variables
set -eu

# config file
CFG=geronimo_freifunkcommunity.cfg
JSON=geronimo_freifunkcommunity.json

# get current script dir
HOME="$(dirname $(readlink -f "$0"))"

# prepare array
declare -A COMMUNITY_LIST

# read variables
. "$HOME/$CFG"

# default json variables
COMMUNITY_LIST_KEY="rostock"
COMMUNITY_LIST_NAME="rostock"
COMMUNITY_LIST_LAT=54.0914
COMMUNITY_LIST_LON=12.1151
DATEISO=$(date "+%FT%T%Z")

# retrieve requested key via input
if [ $# -gt 0 ]; then
    COMMUNITY_LIST_KEY="$1"
fi

# set json variables from cfg
[ -z "${COMMUNITY_LIST["$COMMUNITY_LIST_KEY"]+exists}" ] && echo -e >&2 "Error - key '$COMMUNITY_LIST_KEY' not found in cfg file" && exit 1
COMMUNITY_LIST_ARRAY="${COMMUNITY_LIST["$COMMUNITY_LIST_KEY"]}"
echo "$COMMUNITY_LIST_ARRAY"

# process json template
OUTPUT="$JSON_TMP/$JSON_NAME$COMMUNITY_LIST_NAME.json"
TMP_OUTPUT="$OUTPUT.tmp"
echo > "$TMP_OUTPUT"
while read LINE; do
   eval echo "$LINE" >> "$TMP_OUTPUT" 
done < "$HOME/$JSON"

# format output
#cat "$TMP_OUTPUT" | jq '.'

# clear temporary files
rm "$TMP_OUTPUT"

exit 0

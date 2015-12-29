#!/bin/bash

#
# Opennet Geronimo Scripts
# Mathias Mahnke, created 2015/12/27
# Opennet Admin Group <admin@opennet-initiative.de>
#

# This scripts generates Freifunk Community API JSON
# see also https://wiki.opennet-initiative.de/wiki/Freifunk_API

# usage: geronimo_freifunkcommunity.sh [city-key]
# - generates community api json file for city
# - output to stdout, errors to stderr
# - default city key is "rostock"
# - ready all needed values from cfg file
# usage: geronimo_freifunkcommunity.sh --batch
# - generates all community api json files
# - uses city list as in cfg file
# - output to file in local dir, errors to stderr

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
COMMUNITY_LIST_NAME="Rostock"
COMMUNITY_LIST_LAT=54.0914
COMMUNITY_LIST_LON=12.1151
COMMUNITY_LIST_NODES=300
DATEISO=$(date "+%FT%T%Z")

# retrieve requested key via input
if [ $# -gt 0 ]; then
    COMMUNITY_LIST_KEY="$1"
fi

# check if batch processing is been requested
# and iterate thru all cities in cfg file
if [ "$COMMUNITY_LIST_KEY" = "--batch" ]; then
    for KEY in "${!COMMUNITY_LIST[@]}"
    do
        echo -n "Processing '$KEY'.."
	$0 "$KEY" > "$HOME/$JSON_NAME$KEY.json"
        echo " done."
    done
    exit 0
fi

# set json variables from cfg
[ -z "${COMMUNITY_LIST["$COMMUNITY_LIST_KEY"]+exists}" ] && echo -e >&2 "Error - key '$COMMUNITY_LIST_KEY' not found in cfg file" && exit 1
COMMUNITY_LIST_VALUE="${COMMUNITY_LIST["$COMMUNITY_LIST_KEY"]}"
IFS=","
COMMUNITY_LIST_ARRAY=($COMMUNITY_LIST_VALUE)
unset IFS
COMMUNITY_LIST_NAME="${COMMUNITY_LIST_ARRAY[0]}"
COMMUNITY_LIST_LAT="${COMMUNITY_LIST_ARRAY[1]}"
COMMUNITY_LIST_LON="${COMMUNITY_LIST_ARRAY[2]}"
COMMUNITY_LIST_NODES="${COMMUNITY_LIST_ARRAY[3]}"

# process json template, replace variables via eval
OUTPUT="$JSON_TMP/$JSON_NAME$COMMUNITY_LIST_KEY.json"
TMP_OUTPUT="$OUTPUT.tmp"
echo > "$TMP_OUTPUT"
while read LINE; do
   eval echo "$LINE" >> "$TMP_OUTPUT" 
done < "$HOME/$JSON"

# format output via jq to stdout
cat "$TMP_OUTPUT" | jq '.'

# clear temporary files
rm "$TMP_OUTPUT"

exit 0

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

# process json template
COMMUNITY_LIST_NAME="Rostock"
COMMUNITY_LIST_LAT=54
COMMUNITY_LIST_LON=14
DATEISO=$(date "+%FT%T%Z")
while read LINE; do
   eval echo "$LINE" 
done < "$HOME/$JSON"

exit 0

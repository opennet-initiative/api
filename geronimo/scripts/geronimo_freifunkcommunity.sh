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

# get current script dir
HOME="$(dirname $(readlink -f "$0"))"

# prepare array
declare -A COMMUNITY_LIST

# read variables
. "$HOME/$CFG"

exit 0

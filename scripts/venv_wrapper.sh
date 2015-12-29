#!/bin/sh

set -eu

BASE_DIR=$(cd "$(dirname "$0")/.."; pwd)

VENV="$1"
ACTION="$2"
shift 2

set +eu

. "$HOME/.virtualenvs/$VENV/bin/activate"
python "$BASE_DIR/manage.py" "$ACTION" "$@"

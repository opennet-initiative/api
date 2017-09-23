# aktiviere shell-Stil-Pruefungen
DISABLE_SHELL_CHECK =

include makefilet-download-ondemand.mk

SHELLCHECK_CALL = shellcheck -x --exclude=SC2034

default: help

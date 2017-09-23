# aktiviere shell-Stil-Pruefungen
DISABLE_SHELL_CHECK =

include makefilet-download-ondemand.mk

SHELLCHECK_CALL = shellcheck -x --exclude=SC2034


# the deb packaging relies on "make" (without target) building the package
default: build

build: build-freifunk-api-data
install: install-freifunk-api-data
clean: clean-freifunk-api-data


.PHONY: build-freifunk-api-data
build-freifunk-api-data:
	scripts/geronimo_freifunkcommunity.sh --batch


.PHONY: install-freifunk-api-data
install-freifunk-api-data:
	install -d "$(DESTDIR)/usr/share/on-freifunk-api/public"
	find scripts -type f -name "api.freifunk.net-*" -print0 \
		| xargs -0 install -t "$(DESTDIR)/usr/share/on-freifunk-api/public" 
	install -d "$(DESTDIR)/usr/bin"
	install scripts/geronimo_freifunknodelist.sh \
		"$(DESTDIR)/usr/bin/on-freifunk-api-update-nodelist"


.PHONY: clean-freifunk-api-data
clean-freifunk-api-data:
	find scripts/ -type f -name "api.freifunk.net-*" -delete

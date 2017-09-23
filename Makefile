# aktiviere shell-Stil-Pruefungen
DISABLE_SHELL_CHECK =

include makefilet-download-ondemand.mk

SHELLCHECK_CALL = shellcheck -x --exclude=SC2034
DIR_FREIFUNK_API = freifunk-api


# the deb packaging relies on "make" (without target) building the package
default: build

build: build-freifunk-api-data
install: install-freifunk-api-data
clean: clean-freifunk-api-data
help: help-on-geronimo


.PHONY: help-on-geronimo
help-on-geronimo:
	@echo "on-geronimo packaging targets:"
	@echo "    deploy-deb-remote"
	@echo "    build-freifunk-api-data"
	@echo "    install-freifunk-api-data"
	@echo "    clean-freifunk-api-data"
	@echo


.PHONY: deploy-deb-remote
deploy-deb-remote: dist-deb-packages-directory
	@if [ -z "$(DEPLOY_TARGET)" ]; then \
		echo >&2 "Missing 'DEPLOY_TARGET' environment variable (e.g. 'root@jun.on')."; \
		exit 1; fi
	scp "$(DIR_DEBIAN_SIMPLIFIED_PACKAGE_FILES)"/*.deb "$(DEPLOY_TARGET):/tmp/"
	ssh "$(DEPLOY_TARGET)" \
		'for fname in python3-on-geronimo on-geronimo-api on-freifunk-api; do \
			dpkg -i "/tmp/$$fname.deb" && rm "/tmp/$$fname.deb" || exit 1; done'


.PHONY: build-freifunk-api-data
build-freifunk-api-data:
	"$(DIR_FREIFUNK_API)/geronimo_freifunkcommunity.sh" --batch


.PHONY: install-freifunk-api-data
install-freifunk-api-data:
	install -d "$(DESTDIR)/usr/share/on-freifunk-api/public"
	find "$(DIR_FREIFUNK_API)" -type f -name "api.freifunk.net-*" -print0 \
		| xargs -0 install -t "$(DESTDIR)/usr/share/on-freifunk-api/public" 
	install -d "$(DESTDIR)/usr/bin"
	install "$(DIR_FREIFUNK_API)/geronimo_freifunknodelist.sh" \
		"$(DESTDIR)/usr/bin/on-freifunk-api-update-nodelist"


.PHONY: clean-freifunk-api-data
clean-freifunk-api-data:
	find "$(DIR_FREIFUNK_API)/" -type f -name "api.freifunk.net-*" -delete

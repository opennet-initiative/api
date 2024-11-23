# Opennet API (Geronimo)
[![CodeQL](https://github.com/opennet-initiative/api/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/opennet-initiative/api/actions/workflows/codeql-analysis.yml)

Geronimo verwaltet die Daten eines Mesh-Netzwerks mit besonderem Fokus auf die Infrastruktur
der [Opennet Initiative e.V.](https://opennet-initiative.de/).

Die Django-basierte Web-Anwendung erfüllt folgende Aufgaben:

* Sammeln von Daten aus verschiedenen Quellen (OLSR, ondataservice, Wiki)
* Bereitstellung von Informationen mittels einer API
* Zusammenfassung von relevanten Informationen

Alle Informationen werden in einer Datenbank dauerhaft gespeichert.

## Abhängigkeiten installieren

### Als Debian-Pakete

```shell
apt install python3-django-filters python3-django-model-utils python3-djangorestframework-gis \
	libsqlite3-mod-spatialite spatialite-bin
git clone git@github.com:opennet-initiative/api.git
cd api/on_geronimo
```

### Via virtualenv/pip

```shell
# getestet mit Debian12
apt install python3-venv python3-pip libgeos++-dev libproj-dev gdal-bin spatialite-bin wget
git clone git@github.com:opennet-initiative/api.git
cd api
make virtualenv-update
. build/venv/bin/activate
```

## API starten / aktualisieren

```shell
./manage.py migrate
./manage.py runserver
```
## Manueller Datenimport

* `./manage.py import_wiki`
* `./manage.py import_olsr http://192.168.2.76:2006`
* `./manage.py import_ondataservice tests/assets/ondataservice.db`

## URL-Beispiele

Siehe https://api.opennet-initiative.de/

## Entwicklung
* Prüfung des Code-Stils: `make lint`
* triviale Tests: `make test`
* deb-Paketerstellung: `make dist-deb`
* Release erstellen: `make release-{patch,minor,major}`

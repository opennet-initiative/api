= Installationsanleitung =

== Installation mit deb-Paketen ==

* Pakete bauen: `make dist-deb`
* Pakete bauen und halb-automatisch auf entferntem Host installieren:
  `make deploy-deb DEPLOY_TARGET=root@example.org`

== Manuelle Installation (auf Debian) ==

```shell
apt install python3-django-filters python3-django-model-utils python3-djangorestframework-gis \
	libsqlite3-mod-spatialite spatialite-bin
git clone git@dev.opennet-initiative.de:on_geronimo.git
cd on_geronimo
```


== Manuelle Installation (virtualenv/pip) ==

```shell
aptitude install virtualenvwrapper libgeos++-dev libproj-dev gdal-bin spatialite-bin
git clone git@dev.opennet-initiative.de:on_geronimo.git
cd on_geronimo
mkvirtualenv --python /usr/bin/python3 on-geronimo
pip install -r requirements.txt
```


= API starten / aktualisieren =
```shell
./manage.py migrate
./manage.py runserver
```


= Manueller Datenimport =

* `./manage.py import_wiki`
* `./manage.py import_olsr`
* `./manage.py import_ondataservice SQLITE_DATABASE`


= URL-Beispiele =

* http://api.opennet-initiative.de/api/v1/accesspoint
* http://api.opennet-initiative.de/api/v1/accesspoint/192.168.2.151
* http://api.opennet-initiative.de/api/v1/accesspoint/192.168.2.151/interfaces
* http://api.opennet-initiative.de/api/v1/accesspoint/192.168.2.151/links
* http://api.opennet-initiative.de/api/v1/link
* http://api.opennet-initiative.de/api/v1/interface


= Entwicklung =
* deb-Paketerstellung: `make dist-deb`
* Release erstellen: `make release-{patch,minor,major}`
* triviale Tests: `make test`

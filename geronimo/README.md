= Installationsanleitung =

* aptitude install virtualenvwrapper libgeos++-dev libproj-dev gdal-bin spatialite-bin python3-django-model-utils
** django-model-utils muss in Version > 2.2 vorliegen
* git clone git@dev.opennet-initiative.de:on_geronimo.git
* cd on_geronimo
* mkvirtualenv --python /usr/bin/python3 geronimo
* pip install -r requirements.txt
* spatialite db.sqlite3 "SELECT InitSpatialMetaData();"
* ./manage.py migrate
* ./manage.py runserver


= Manueller Datenimport =

* ./manage.py import_wiki
* ./manage.py import_olsr
* ./manage.py import_ondataservice SQLITE_DATABASE


= URL-Beispiele =

* http://api.opennet-initiative.de/api/v1/accesspoint
* http://api.opennet-initiative.de/api/v1/accesspoint/192.168.2.151
* http://api.opennet-initiative.de/api/v1/accesspoint/192.168.2.151/interfaces
* http://api.opennet-initiative.de/api/v1/accesspoint/192.168.2.151/links
* http://api.opennet-initiative.de/api/v1/link
* http://api.opennet-initiative.de/api/v1/interface


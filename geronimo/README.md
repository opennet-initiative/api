= Installationsanleitung =

* aptitude install libgeos++-dev libproj-dev gdal-bin spatialite-bin python3-django-model-utils
** django-model-utils muss in Version > 2.2 vorliegen
* git clone git@git.opennet-initiative.de:on_geronimo.git
* cd on_geronimo
* mkvirtualenv --python /usr/bin/python3 geronimo
* pip install -r requirements.txt
* spatialite db.sqlite3 "SELECT InitSpatialMetaData();"
* ./manage.py migrate
* ./manage.py runserver


= Manueller Datenimport =

* ./manage.py import_wiki
* ./manage.py import_ondataservice SQLITE_DATABASE


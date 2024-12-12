#
# For testing the api you can use this docker container setup:
#
# Build docker image:
#   docker buildx build -t debian/on-geronimo .
# Start docker container in background:
#   docker run -p 8000:8000 -dit debian/on-geronimo
# Open website:
#   open in browser: http://localhost:8000/
# (for debugging) Attach with interactive console
#   docker exec -it ..INSERT_CONTAINER_ID... /bin/bash
#

FROM debian:12

EXPOSE 8000

COPY . /api

RUN apt update && \
  apt install --yes python3-venv python3-pip libgeos++-dev libproj-dev gdal-bin spatialite-bin libsqlite3-mod-spatialite wget git && \
  cd api && \
  make virtualenv-update

ENV PATH="/api/build/venv/bin:$PATH"
WORKDIR /api
CMD ["python3", "manage.py","runserver","0.0.0.0:8000"]


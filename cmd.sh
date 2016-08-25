#!/bin/bash
set -e

CONFIG=${CONFIG:-/opt/visualiser/docker_production.ini}

if [ "$ENV" = 'UNIT' ]; then
  echo "Running Unit Tests"
  cd /opt/visualiser/
  mkdir -p /tmp/bccvl/map_data_files
  chown -R visualiser:visualiser /tmp/bccvl
  PYTHONWARNINGS="ignore:Unverified HTTPS request" /usr/bin/nosetests -v -v --with-xunit --xunit-file=/tmp/nosetests.xml --with-coverage --cover-package=bccvl_visualiser --cover-xml --cover-xml-file=/tmp/coverage.xml
else
  echo "Running BCCVL Visualisation Server"
  mkdir -p $BCCVL_MAPSCRIPT_MAP_DATA_FILES_ROOT_PATH
  chown -R visualiser:visualiser $BCCVL_MAPSCRIPT_MAP_DATA_FILES_ROOT_PATH
  mkdir -p $BCCVL_DATA_MOVER_PUBLIC_DIR
  chown -R visualiser:visualiser $BCCVL_DATA_MOVER_PUBLIC_DIR
  /usr/bin/gunicorn --workers $NWORKERS \
                    --threads $NTHREADS \
                    --paste ${CONFIG} \
                    --user visualiser \
                    --group visualiser \
                    $@
fi

#!/bin/bash
set -e

if [ "$ENV" = 'UNIT' ]; then
  echo "Running Unit Tests"
  cd /bccvl_visualiser/BCCVL_Visualiser/
  PYTHONWARNINGS="ignore:Unverified HTTPS request" /usr/bin/nosetests -v -v --with-xunit --xunit-file=/tmp/nosetests.xml --with-coverage --cover-package=bccvl_visualiser --cover-xml --cover-xml-file=/tmp/coverage.xml
else
  echo "Running BCCVL Visualisation Server"
  mkdir -p $BCCVL_MAPSCRIPT_MAP_DATA_FILES_ROOT_PATH
  mkdir -p $BCCVL_DATA_MOVER_PUBLIC_DIR
  /usr/bin/gunicorn --workers $NWORKERS \
                      --threads $NTHREADS \
                      --paste /bccvl_visualiser/BCCVL_Visualiser/docker_production.ini

fi

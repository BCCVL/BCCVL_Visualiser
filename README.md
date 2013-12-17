[![Build Status](https://travis-ci.org/BCCVL/BCCVL_Visualiser.png?branch=master)](https://travis-ci.org/BCCVL/BCCVL_Visualiser)

BCCVL_Visualiser
================

A Pyramid web app to act as the Geo Server (Maps and Features) for the client. Expected to support WFS, GeoJSON, and WMS.

Getting Started
-------------------

1. Install the latset version of git.

    _ubuntu_ instructions:

        sudo apt-get install git-core

2. Install dependencies:

    _ubuntu_:

        sudo apt-add-repository -y ppa:ubuntugis/ppa
        sudo apt-get update
        sudo apt-get install build-essential libcurl4-gnutls-dev libpng12-dev libgd2-xpm-dev libgif-dev libjpeg-dev libblas-dev libsuitesparse-dev libatlas-base-dev liblapack-dev swig gfortran libgdal-dev proj libproj-dev libgeos-dev

    _OSX_:

        brew install cloog gdbm isl libspatialite mapserver proj freetype geos jpeg libtiff mpfr python swig freexl gfortran libgeotiff libxml2 openssl wget gd giflib libmpc libyaml pcre readline xz gdal gmp libpng lzlib pkg-config

3. Clone this repo.

    _read only_:

        git clone git://github.com/BCCVL/BCCVL_Visualiser.git

    _read and write_:

        git clone git@github.com:BCCVL/BCCVL_Visualiser.git

4. Change into the BCCVL_Visualiser sub-folder within this directory (the repo you just cloned)

        cd BCCVL_Visualiser/BCCVL_Visualiser

5. Create a virtualenv here

        virtualenv .

6. Upgrade setuptools

        ./bin/pip install setuptools --upgrade

7. Bootstrap

        ./bin/python bootstrap.py

8. Buildout

        ./bin/buildout

9. Run the tests

        ./bin/test

10. Serve (with auto-reload on file change)

        ./bin/pserve development.ini --reload

[![Build Status](http://118.138.242.168/job/bccvl_visualiser/badge/icon)](http://118.138.242.168/job/bccvl_visualiser/)

BCCVL_Visualiser
================

A Pyramid web app to act as the Geo Server (Maps and Features) for the client. Expected to support WFS, GeoJSON, and WMS.

Getting Started
-------------------

1. Install the latset version of git.

    _ubuntu_ instructions:

        sudo apt-get install git-core

    _centos_ instructions:

        sudo yum install git

2. Install dependencies:

    _ubuntu 12.04_:

        sudo apt-add-repository -y ppa:ubuntugis/ppa
        sudo apt-get update
        sudo apt-get install build-essential libcurl4-gnutls-dev libpng12-dev libgd2-xpm-dev libgif-dev libjpeg-dev libblas-dev libsuitesparse-dev libatlas-base-dev liblapack-dev swig gfortran libgdal-dev proj libproj-dev libgeos-dev

    _ubuntu_14.04_:

        sudo apt-add-repository -y ppa:ubuntugis/ubuntugis-unstable
        sudo apt-get update
        sudo apt-get install build-essential libcurl4-gnutls-dev libpng12-dev libgd2-xpm-dev libgif-dev libjpeg-dev libblas-dev libsuitesparse-dev libatlas-base-dev liblapack-dev swig gfortran libgdal-dev lib-proj libproj-dev libgeos-dev python-pip python-dev
        sudo pip install pip --upgrade
        sudo ln -s /usr/local/bin/pip /usr/bin/pip
        sudo pip install virtualenv

    (pip seemed cantankerous when last tested on Ubuntu 12.04, the symlinking got around it, but this should be investigated further)

    _ubuntu 14.04_:

        sudo apt-add-repository -y ppa:ubuntugis/ubuntugis-unstable
        sudo apt-get update
        sudo apt-get install build-essential libcurl4-gnutls-dev libpng12-dev libgd2-xpm-dev libgif-dev libjpeg-dev libblas-dev libsuitesparse-dev libatlas-base-dev liblapack-dev swig gfortran libgdal-dev lib-proj libproj-dev libgeos-dev python-pip python-dev
        sudo pip install pip --upgrade
        sudo pip install virtualenv
        
    At the time of last edit (15th June, 2014), the ubuntugis ppa didn't have a stable stream for Ubuntu 14.04. If the stable stream is available for 14.04 at the time of your install, you should use it instead.

    _OSX_:

        brew install cloog gdbm isl libspatialite mapserver proj freetype geos jpeg libtiff mpfr python swig freexl gfortran libgeotiff libxml2 openssl wget gd giflib libmpc libyaml pcre readline xz gdal gmp libpng lzlib pkg-config

3. Clone this repo.

    _read only_:

        git clone git://github.com/jcu-eresearch/BCCVL_Visualiser.git

    _read and write_:

        git clone git@github.com:jcu-eresearch/BCCVL_Visualiser.git

4. Change into the BCCVL_Visualiser sub-folder within this directory (the repo you just cloned)

        cd BCCVL_Visualiser/BCCVL_Visualiser

5. Create a virtualenv here

        virtualenv .

6. Upgrade setuptools

        ./bin/pip install setuptools --upgrade

7. Install (or upgrade) the numpy egg.

        ./bin/pip install numpy --upgrade
    
    You may get a lot of warnings on this step - ignore them. As long as you get "Successfully installed numpy" at the end, it should be fine.

8. Bootstrap

        ./bin/python bootstrap.py

9. Buildout

        ./bin/buildout

10. Run the tests

        ./bin/test

11. Serve (with auto-reload on file change)

        ./bin/pserve development.ini --reload

12. Testing your server:

    The following are some quick tests you can run against your server to see the visualiser in action. These tests use the project's test fixtures.
    
    1. Go to http://localhost:10600/api/auto_detect/1/default?data_url=https%3A%2F%2Fraw.github.com%2FBCCVL%2FBCCVL_Visualiser%2Fmaster%2FBCCVL_Visualiser%2Fbccvl_visualiser%2Ftests%2Ffixtures%2Fraster.tif
    
       This should present an OpenLayers map with some visible raster data in QLD, Australia.
    
    2. Go to http://localhost:10600/api/point/1/default?data_url=https%3A%2F%2Fraw.github.com%2FBCCVL%2FBCCVL_Visualiser%2Fmaster%2FBCCVL_Visualiser%2Fbccvl_visualiser%2Ftests%2Ffixtures%2Fmagpies.csv
    
       This should present an OpenLayers map with some visible point data. Note: This input contains ~ 500 thousand points, and so additionaly acts a stress test.
    
    

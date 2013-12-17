[![Build Status](https://travis-ci.org/BCCVL/BCCVL_Visualiser.png?branch=master)](https://travis-ci.org/BCCVL/BCCVL_Visualiser)

BCCVL_Visualiser
================

A Pyramid web app to act as the Geo Server (Maps and Features) for the client. Expected to support WFS, GeoJSON, and WMS.

Getting Started
-------------------

1. Install the latset version of git.

    _ubuntu_ instructions:

        sudo apt-get install git-core

2. Clone this repo.

    _read only_:

        git clone git://github.com/BCCVL/BCCVL_Visualiser.git

    _read and write_:

        git clone git@github.com:BCCVL/BCCVL_Visualiser.git

3. Change into the BCCVL_Visualiser sub-folder within this directory (the repo you just cloned)

    cd BCCVL_Visualiser/BCCVL_Visualiser

4. Create a virtualenv here

    virtualenv .

5. Upgrade setuptools

    ./bin/pip install setuptools --upgrade

6. Bootstrap

    ./bin/python bootstrap.py

7. Buildout

    ./bin/buildout

8. Run the tests

    ./bin/test

9. Serve (with auto-reload on file change)

    ./bin/pserve development.ini --reload

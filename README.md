PyramidGeoVis
=============

A Pyramid web app to act as the Geo Server (Maps and Features) for the Plone client (PloneGeoVis). Expected to support WFS, GeoJSON, and WMS.

Getting Started
===============

Install the latset version of git.

_ubuntu_ instructions:

    sudo apt-get install git-core


Install the latest version of VirtualBox: https://www.virtualbox.org/wiki/Downloads


Install the latest version of Vagrant: http://downloads.vagrantup.com/


Add the vagrant-vbguest to ensure that your VM has guest additions installed

    vagrant plugin install vagrant-vbguest

Note: If you don't do this, your guest additions will be removed by the first
yum update, and won't return :(


Clone this repo.

_read only_ instructions:

    git clone git://github.com/BCCVL/PyramidGeoVis.git

_read and write_ instructions:

    git clone git@github.com:BCCVL/PyramidGeoVis.git


Now start your VM, this should be done from your repo folder (where the Vagrantfile is)

    vagrant up

Note: The first time you do this, it will download the _box_. The _box_ is
CentOS 6 (x64). It will only download it once. Once it's downloaded, it will store it
locally for future use.


Now your VM is up and running. You can ssh into your VM:

    vagrant ssh

And you can stop your VM with:

    vagrant halt


Once halted, you can restart it at anytime with:

    vagrant up


For more info, see the vagrant instructions.

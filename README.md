[![Build Status](https://travis-ci.org/BCCVL/BCCVL_Visualiser.png)](https://travis-ci.org/BCCVL/BCCVL_Visualiser)

BCCVL_Visualiser
================

A Pyramid web app to act as the Geo Server (Maps and Features) for the client. Expected to support WFS, GeoJSON, and WMS.

Getting Started
-------------------

1. Install the latset version of git.

    _ubuntu_ instructions:

        sudo apt-get install git-core

2. Install the latest version of VirtualBox: https://www.virtualbox.org/wiki/Downloads


3. Install the latest version of Vagrant: http://downloads.vagrantup.com/


4. Add the vagrant-vbguest plugin to ensure that your VM has guest additions installed

        vagrant plugin install vagrant-vbguest

    Note: If you don't do this, your guest additions will be removed by the first
    yum update, and won't return without manual intervention :(


5. Clone this repo.

    _read only_:

        git clone git://github.com/BCCVL/BCCVL_Visualiser.git

    _read and write_:

        git clone git@github.com:BCCVL/BCCVL_Visualiser.git


6. Now start your VM, this should be done from your repo folder (where the Vagrantfile is)

        vagrant up

    Note: The first time you do this, it will download the _box_. The _box_ is
    CentOS 6 (x64). It will only download it once. Once it's downloaded, it will store it
    locally for future use. Once the machine comes up, it will be provisioned.


7. Now your VM is up and running. You can ssh into your VM:

        vagrant ssh

   And you can stop your VM with:

        vagrant halt


8. Once halted, you can restart it at anytime with:

        vagrant up


For more info, see the vagrant instructions.

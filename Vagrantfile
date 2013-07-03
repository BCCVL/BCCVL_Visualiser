# -*- mode: ruby -*-
# vi: set ft=ruby :

# The settings that will be used to create a postgresql environment for your pyramid webapp.
# This includes a superuser, and a database that will have the postgis2 extensions.
# When you change these, don't forget to also change them inside your app config.
POSTGRESQL_SUPERUSER_USERNAME      = "pyramid"
POSTGRESQL_SUPERUSER_PASSWORD      = "pyramid_password"
POSTGRESQL_PYRAMID_DATABASE        = "pyramid_db"
POSTGRESQL_PYRAMID_TEST_DATABASE   = "pyramid_test_db"

Vagrant::Config.run do |config|
  config.vm.box     = "centos-64-x64-vbox4210"
  config.vm.box_url = "http://puppet-vagrant-boxes.puppetlabs.com/centos-64-x64-vbox4210.box"

  config.vm.forward_port 5432, 5432
  config.vm.forward_port 6543, 6543 # forward pyramid webapp

  # Run yum update as a separate step in order to avoid
  # package install errors
  config.vm.provision :puppet do |puppet|
    puppet.manifest_file  = "yum_update.pp"
    puppet.manifests_path = "puppet/manifests"
  end

  # Configure the firewall
  config.vm.provision :shell do |shell|
    shell.path = "puppet/manifests/configure_firewall.sh"
  end

  # Install CentOS dependencies
  config.vm.provision :puppet do |puppet|
    puppet.manifest_file  = "centos_dependencies.pp"
    puppet.manifests_path = "puppet/manifests"
  end

  # Install Pythons
  config.vm.provision :puppet do |puppet|
    puppet.manifest_file  = "install_pythons.pp"
    puppet.manifests_path = "puppet/manifests"
  end

  # Install PostGIS2
  config.vm.provision :puppet do |puppet|
    puppet.facter = {
      "postgresql_superuser_username"       => POSTGRESQL_SUPERUSER_USERNAME,
      "postgresql_superuser_password"       => POSTGRESQL_SUPERUSER_PASSWORD,
      "postgresql_pyramid_database"         => POSTGRESQL_PYRAMID_DATABASE,
      "postgresql_pyramid_test_database"    => POSTGRESQL_PYRAMID_TEST_DATABASE,
    }
    puppet.manifest_file  = "install_postgis2.pp"
    puppet.manifests_path = "puppet/manifests"
  end

  # Install Pyramid
  config.vm.provision :puppet do |puppet|
    puppet.manifest_file  = "install_pyramid.pp"
    puppet.manifests_path = "puppet/manifests"
  end


end

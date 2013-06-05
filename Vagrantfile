# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box     = "centos-64-x64-vbox4210"
  config.vm.box_url = "http://puppet-vagrant-boxes.puppetlabs.com/centos-64-x64-vbox4210.box"

  config.vm.forward_port 8080, 8088
  config.vm.forward_port 5432, 5432

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

  # Install Pyramid 
  config.vm.provision :puppet do |puppet|
    puppet.manifest_file  = "install_pyramid.pp"
    puppet.manifests_path = "puppet/manifests"
  end

  # Install PostGIS2
  config.vm.provision :puppet do |puppet|
    puppet.manifest_file  = "install_postgis2.pp"
    puppet.manifests_path = "puppet/manifests"
  end

end

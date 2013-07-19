# -*- mode: ruby -*-
# vi: set ft=ruby :

# Remove this once bitbucket certificates are updated for the various
# python download sites (pypi, etc.).
PYTHON_WGET_FLAGS = "--no-check-certificate"
USER = 'vagrant'

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
    puppet.facter = {
      "python_wget_flags"       => PYTHON_WGET_FLAGS,
      "user"                    => USER,
    }
    puppet.manifest_file  = "install_pythons.pp"
    puppet.manifests_path = "puppet/manifests"
  end

  # Install Pyramid
  config.vm.provision :puppet do |puppet|
    puppet.facter = {
      "user"                    => USER,
    }
    puppet.manifest_file  = "install_pyramid.pp"
    puppet.manifests_path = "puppet/manifests"
  end


end

class centos_dependencies{

  # Install CentOS Dependencies

  # Group install Development Tools
  exec { 'yum groupinstall "Development Tools"':
    command => 'yum groupinstall -y "Development Tools"',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    timeout => 0                                  # Disable the command timeout
  }

  package { "readline-devel":
    ensure => present,
  }

  package { "libpng-devel.x86_64":
    ensure => present,
  }

  package { "gd-devel":
    ensure => present,
  }

  package { "giflib-devel.x86_64":
    ensure => present,
  }

  package { "patch":
    ensure => present,
  }

  package { "zlib-devel":
    ensure => present,
  }

  package { "bzip2-devel":
    ensure => present,
  }

  package { "openssl-devel":
    ensure => present,
  }

  package { "ncurses-devel":
    ensure => present,
  }

  package { "sqlite-devel":
    ensure => present,
  }

  package { "tk-devel":
    ensure => present,
  }

  package { "python-devel.x86_64":
    ensure => present,
  }

  package { "libjpeg-turbo-devel.x86_64":
    ensure => present,
  }

  # Allows for 'import setuptools' in python
  package { "python-setuptools.noarch":
    ensure    => present,
  }

  # Install virtualenv package
  exec { 'easy_install virtualenv':
    command => 'easy_install virtualenv',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    require => Package['python-setuptools.noarch'],
  }

  # Install Extra Packages for Enterprise Linux repos
  package { 'epel-release-6-8':
    ensure => present,
    source => 'http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm',
    provider => rpm,
  }

  # Install Enterprise Linux GIS repos
  package { 'elgis-release-6-6_0':
    ensure => present,
    source => 'http://elgis.argeo.org/repos/6/elgis-release-6-6_0.noarch.rpm',
    provider => rpm,
  }


  # Install PostgreSQL and PostGIS repos
  package { 'pgdg-centos92-9.2-6':
    ensure => present,
    source => 'http://yum.postgresql.org/9.2/redhat/rhel-6-x86_64/pgdg-centos92-9.2-6.noarch.rpm',
    provider => rpm,
  }

}

include centos_dependencies

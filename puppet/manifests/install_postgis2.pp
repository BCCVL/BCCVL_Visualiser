class install_postgis2 {

  package { 'postgresql92.x86_64':
    ensure => latest,
  }

  package { 'postgresql92-libs':
    ensure => latest,
  }

#  package { 'postgresql-devel.x86_64':
#    ensure => latest,
#  }

  package { 'postgresql92-devel.x86_64':
    ensure => latest,
  }

  # setup postgresql92-server
  package { 'postgresql92-server':
    ensure => latest,
  }

  # setup postgis2_92
  package { 'postgis2_92':
    ensure => latest,
    require => Package['postgresql92-server'],
  }

  # setup the postgresql service
  # only do this when postgis is installed
  exec { 'service postgresql-9.2 initdb':
    subscribe   => Package["postgis2_92"],
    refreshonly => true,
    path        => '/sbin/',
  }

  # start the postgresql service
  # also set it to auto-start
  service { 'postgresql-9.2':
    enable   => true,
    ensure   => 'running',
    require  => Exec['service postgresql-9.2 initdb'],
  }

  # setup the pyramid postgis user
  # only do this when postgis is first installed
  # Require the postgresql service to be already running
  exec { "sudo -u postgres psql -c \"create role $postgresql_superuser_username LOGIN PASSWORD '$postgresql_superuser_password';\"":
    path        => '/usr/bin',
    refreshonly => true,
    subscribe   => Package["postgis2_92"],
    require     => Service['postgresql-9.2'],
  }~>
  # Add the pyramid db
  exec { "sudo -u postgres createdb $postgresql_pyramid_database -O $postgresql_superuser_username":
    path        => '/usr/bin',
    refreshonly => true,
  }~>
  # Create the PostGIS extension in the db
  exec { "sudo -u postgres psql -d $postgresql_pyramid_database -c \"CREATE EXTENSION POSTGIS;\"":
    path        => '/usr/bin',
    refreshonly => true,
  }
  # Add the pyramid test db
  exec { "sudo -u postgres createdb $postgresql_pyramid_test_database -O $postgresql_superuser_username":
    path        => '/usr/bin',
    refreshonly => true,
  }~>
  # Create the PostGIS extension in the db
  exec { "sudo -u postgres psql -d $postgresql_pyramid_test_database -c \"CREATE EXTENSION POSTGIS;\"":
    path        => '/usr/bin',
    refreshonly => true,
  }

}

include install_postgis2

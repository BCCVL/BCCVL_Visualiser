class install_postgis2 {

  # setup postgresql92-server
  package { 'postgresql92-server':
    ensure => present,
  }

  # setup postgis2_92
  package { 'postgis2_92':
    ensure  => present,
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

}

include install_postgis2

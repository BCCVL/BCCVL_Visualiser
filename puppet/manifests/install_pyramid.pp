class install_pyramid {

  exec { 'python2.7 bootstrap.py':
    cwd     => '/vagrant/BCCVL_Visualiser',
    path    => '/vagrant/env/bin/',
    timeout => 30 * 60,                        # Allow 30 mins to install
    creates => '/vagrant/BCCVL_Visualiser/bin',
  }
  ~>
  exec { 'buildout':
    cwd     => '/vagrant/BCCVL_Visualiser',
    path    => '/vagrant/BCCVL_Visualiser/bin/:/usr/local/bin/:/usr/bin/:/bin/:/usr/pgsql-9.2/bin/',
    timeout => 120 * 60,                        # Allow 2 hours to install
  }

}

include install_pyramid

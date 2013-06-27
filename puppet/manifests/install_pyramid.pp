class install_pyramid {

  # setup virtualenv
  exec { 'virtualenv --no-site-packages env':
    command => 'virtualenv --no-site-packages env',
    cwd     => '/vagrant',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    timeout => 10 * 60,                        # Allow 10 mins to install
    creates => '/vagrant/env',
  }

  # install the pyramid libraries
  exec { 'easy_install pyramid':
    command => 'easy_install pyramid',
    cwd     => '/vagrant/env/bin',
    path    => '/vagrant/env/bin/',
    timeout => 30 * 60,                        # Allow 30 mins to install
    require => Exec['virtualenv --no-site-packages env'],
    creates => '/vagrant/env/bin/pcreate',
  }

}

include install_pyramid

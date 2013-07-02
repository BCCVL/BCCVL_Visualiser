class install_pythons {

  ##
  # Install python 2.7.3
  ##

  # Download the python source
  exec { 'wget http://python.org/ftp/python/2.7.3/Python-2.7.3.tar.bz2 -O Python-2.7.3.tar.bz2':
    cwd     => '/tmp',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    timeout => 10 * 60,                        # Allow 10 mins to download
    creates => '/tmp/Python-2.7.3.tar.bz2',
  }
  ~>
  exec { 'tar xf Python-2.7.3.tar.bz2':
    cwd     => '/tmp',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    creates => '/tmp/Python-2.7.3',
  }
  ~>
  exec { 'install python 2.7.3':
    command => 'configure --prefix=/usr/local && make && make altinstall',
    cwd     => '/tmp/Python-2.7.3',
    path    => '/tmp/Python-2.7.3/:/usr/local/bin/:/usr/bin/:/bin/',
  }

  ##
  # Install python 3.3.0
  ##

  # Download the python source
  exec { 'wget http://python.org/ftp/python/3.3.0/Python-3.3.0.tar.bz2 -O Python-3.3.0.tar.bz2':
    cwd     => '/tmp',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    timeout => 10 * 60,                        # Allow 10 mins to download
    creates => '/tmp/Python-3.3.0.tar.bz2',
  }
  ~>
  exec { 'tar xf Python-3.3.0.tar.bz2':
    cwd     => '/tmp',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    creates => '/tmp/Python-3.3.0',
  }
  ~>
  exec { 'install python 3.3.0':
    command => 'configure --prefix=/usr/local && make && make altinstall',
    cwd     => '/tmp/Python-3.3.0',
    path    => '/tmp/Python-3.3.0/:/usr/local/bin/:/usr/bin/:/bin/',
  }

}

include install_pythons

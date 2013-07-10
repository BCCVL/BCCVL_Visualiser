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
    creates => '/usr/local/bin/python2.7',
  }

  ##
  # Install virtual env, and upgrade its setuptools version
  ##
  exec { "wget https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.1.tar.gz $python_wget_flags":
    cwd     => '/tmp',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    require => Exec['install python 2.7.3'],
  }
  ~>
  exec { 'tar xvfz virtualenv-1.9.1.tar.gz':
    cwd     => '/tmp',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    creates => '/tmp/virtualenv-1.9.1',
  }
  ~>
  exec { 'python2.7 virtualenv.py --distribute /vagrant/env':
    cwd     => '/tmp/virtualenv-1.9.1',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    creates => '/vagrant/env',
  }
  ~>
  exec { 'pip install setuptools --upgrade':
    path    => '/vagrant/env/bin/',
    cwd     => '/tmp',
  }


}

include install_pythons

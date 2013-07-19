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
    user    => $user,
    cwd     => '/tmp',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    require => Exec['install python 2.7.3'],
  }
  ~>
  exec { 'tar xvfz virtualenv-1.9.1.tar.gz':
    user    => $user,
    cwd     => '/tmp',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    creates => '/tmp/virtualenv-1.9.1',
  }
  ~>
  exec { 'python2.7 virtualenv.py --distribute /vagrant/env':
    user    => $user,
    cwd     => '/tmp/virtualenv-1.9.1',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    creates => '/vagrant/env',
  }
  ~>
  exec { 'pip install setuptools --upgrade':
    user    => $user,
    path    => '/vagrant/env/bin/:/usr/local/bin/:/usr/bin/:/bin/',
    cwd     => '/tmp',
  }
  ~>
  ###
  # Install numpy
  # This needs to occur outside of the buildout process
  # as STUPIDLY, matplotlib uses introspection to 
  # see if numpy is already instaled. This introspection doesn't work
  # as during the buildout process, the egg isn't available to 
  # the environment.
  # ANYWAY.. install numpy prior to the buildout
  ###
  exec { 'pip install numpy':
    user    => $user,
    path    => '/vagrant/env/bin/:/usr/local/bin/:/usr/bin/:/bin/',
    cwd     => '/tmp',
  }


}

include install_pythons

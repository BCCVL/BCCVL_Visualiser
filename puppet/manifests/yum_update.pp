class yum_update {

  # Run yum update
  exec { 'yum update':
    command => 'yum update -y',
    path    => '/usr/local/bin/:/usr/bin/:/bin/',
    timeout => 0,                                # Disable the command timeout
  }

}

include yum_update

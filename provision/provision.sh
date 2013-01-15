#!/bin/bash

export INSTALL_HOME="/home/vagrant"
if [ $USER != 'root' ]; then
  export INSTALL_HOME=$HOME
fi

if [ -f "/etc/apt/sources.list.d/sid.list" ]; then
  echo 'Has sid packages'
else
  echo 'Some packages may depend on sid and may not be installed'
  echo 'Please add the following to /etc/apt/sources.list.d/sid.list'
  echo 'deb http://ftp.us.debian.org/debian/ sid main'
fi

sudo apt-get update
sudo apt-get -y install bzip2 less lsof vim
sudo apt-get -y install gcc g++ make gdb
sudo apt-get -y install zlib1g-dev
sudo apt-get -y install sendmail
sudo apt-get -y install git curl build-essential
sudo apt-get -y install python2.7 python2.7-doc python2.7-dev python-pip python-setuptools

# install python virtualenv
echo 'Installing/Updating virtualenv'
sudo pip install virtualenv
sudo pip install virtualenvwrapper

# mysql
if [ -d "/var/lib/mysql/mysql" ]; then
  echo "MySQL already installed"
else
  sudo DEBIAN_FRONTEND=noninteractive apt-get -y install mysql-server-5.5
  sudo mysqladmin -u root password password
  sudo apt-get -y install mysql-client-5.5
  sudo apt-get -y install libmysqlclient-dev
fi

# setup database
if [ -d "/var/lib/mysql/giraffe_dev" ]; then
  echo "Test database already exists"
else
  echo "CREATE DATABASE giraffe_dev CHARACTER SET 'utf8';" | mysql -u root -ppassword
fi


OS Packages
===========

Debian
------

First you need to install the VPAC Debian Archive signing key

::

    wget http://code.vpac.org/debian/vpac-debian-key.gpg -O - | apt-key add -

Then create a /etc/apt/sources.list.d/vpac.list containing:

::

    deb     http://code.vpac.org/debian  wheezy main
    deb-src http://code.vpac.org/debian  wheezy main

Currently supports following

-  squeeze - current stable
-  wheezy - testing version

CentOS
------

Add the VPAC CentOS repo

::

    wget http://code.vpac.org/centos/vpac.repo -O /etc/yum.repos.d/vpac.repo


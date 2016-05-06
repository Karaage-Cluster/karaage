Cluster tools
=============
.. note::

    You should have the karaage-usage plugin installed before continuing.

Debian Installation
-------------------
#.  If you require a proxy server for out going connections, set it up now.

    .. code-block:: bash

        export http_proxy=http://proxy.example.org

#.  You need to install the VPAC Debian Archive signing key:

    .. code-block:: bash

        wget http://linuxpenguins.xyz/debian/vpac-debian-key.gpg -O - | apt-key add -

#.  Create a /etc/apt/sources.list.d/karaage.list containing::

        deb     http://linuxpenguins.xyz/debian  jessie main
        deb-src http://linuxpenguins.xyz/debian  jessie main

#.  Update your apt database and install the packages:

    .. code-block:: bash

        apt-get update

#.  Install the the packages:

    .. code-block:: bash

        apt-get install karaage-cluster-tools


Configuring
-----------
#. Ensure Karaage is working, with karaage-usage plugin configured.
#. Create a machine category if not already defined.
#. Create a machine, and get its password with the reset password operation.
#. Edit ``/etc/karaage/karaage-cluster-tools.cfg`` with appropriate values.
#. Test.

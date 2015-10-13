Setting up Development Environment
==================================
This section talks about setting up schroot, for releasing new Karaage
versions and for testing Karaage with Karaage-test.

It is assumed the system is running Debian Jessie; other build systems may be
possible, but will require variations.

These steps only need to be done once for a system.

#.  Ensure required packages installed:

    .. code-block:: bash

        apt-get install dput dpkg-dev schroot sbuild slapd
        apt-get install python-django python3-django
        apt-get install python-tldap python3-tldap
        apt-get install python-schroot python3-schroot

    The above list is probably incomplete. Any omissions will cause
    errors when running Karaage tests.

#.  Stop and disable slapd, it will prevent slapd running in a schroot:

    .. code-block:: bash

        service slapd stop
        systemctl disable slapd

#.  Add yourself to the sbuild group. Replace ``brian`` with your unix user
    id.

    .. code-block:: bash

        adduser brian sbuild

    Logout and login again for this to work.

#.  Run the following commands:

    .. code-block:: bash

        cd tree
        git clone https://github.com/brianmay/bampkgbuild.git
        cd bampkgbuild
        git checkout 67c81afcb3dcdd8dfa8adf9f105a0bd06a0eed25
        cd ..
        sudo ~/tree/bampkgbuild/create_schroot debian sid amd64
        sudo ~/tree/bampkgbuild/create_schroot debian sid i386
        sudo ~/tree/bampkgbuild/create_schroot debian jessie amd64
        sudo ~/tree/bampkgbuild/create_schroot debian jessie i386
        sudo ~/tree/bampkgbuild/create_schroot debian wheezy amd64
        sudo ~/tree/bampkgbuild/create_schroot debian wheezy i386

#.  Add the following to ``/etc/schroot/schroot.conf``, replacing
    ``brian`` with your unix user id.

    .. code-block:: text

        [wheezy-i386]
        type=directory
        directory=/srv/chroot/wheezy-i386
        description=Debian Jessie (i386)
        users=brian
        root-users=brian
        union-type=overlay
        personality=linux32
        [wheezy-amd64]
        type=directory
        directory=/srv/chroot/wheezy-amd64
        description=Debian Jessie (amd64)
        users=brian
        root-users=brian
        union-type=overlay

        [jessie-i386]
        type=directory
        directory=/srv/chroot/jessie-i386
        description=Debian Jessie (i386)
        users=brian
        root-users=brian
        union-type=overlay
        personality=linux32
        [jessie-amd64]
        type=directory
        directory=/srv/chroot/jessie-amd64
        description=Debian Jessie (amd64)
        users=brian
        root-users=brian
        union-type=overlay

        [sid-i386]
        type=directory
        directory=/srv/chroot/sid-i386
        description=Debian Jessie (i386)
        users=brian
        root-users=brian
        union-type=overlay
        personality=linux32
        [sid-amd64]
        type=directory
        directory=/srv/chroot/sid-amd64
        description=Debian Jessie (amd64)
        users=brian
        root-users=brian
        union-type=overlay

    .. note::

        The ``overlay`` union type requires a new kernel. If this does not
        work for you, try ``overlayfs`` or ``aufs`` instead.

#.  Test schroot is in working order. Changes should disappear after exiting
    the schroot.

    .. code-block:: bash

        schroot --chroot jessie-amd64
        schroot --chroot jessie-amd64 --user root

#.  To make changes to the underlying chroot (you shouldn't have to do this)
    use:

    .. code-block:: bash

        schroot --chroot source:jessie-amd64

#.  Add the following to ``~/dput.cf`` (requires you can ssh into code.vpac.org
    as repo):

    .. code-block:: text

        [vpac]
        login                   = repo
        fqdn                    = code.vpac.org
        method                  = scp
        incoming                = /var/www/debian/incoming/
        allow_dcut              = 0
        allowed_distributions   = (?!UNRELEASED|.*-security)

#.  Add the following to ``~/.gitconfig``:

    .. code-block:: text

        [merge "dpkg-mergechangelogs"]
        name = debian/changelog merge driver
        driver = dpkg-mergechangelogs -m %O %A %B %A

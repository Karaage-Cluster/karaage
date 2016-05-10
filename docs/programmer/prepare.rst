Setting up Development Environment
==================================
This section talks about setting up schroot, for releasing new Karaage
versions and for testing Karaage with Karaage-test.

It is assumed the system is running Debian Jessie; other build systems may be
possible, but will require variations.

These steps only need to be done once for a system.

#.  Ensure required packages installed:

    .. code-block:: bash

        apt-get install dput-ng dpkg-dev schroot sbuild slapd
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
        sudo ~/tree/bampkgbuild/create_schroot debian sid amd64
        sudo ~/tree/bampkgbuild/create_schroot debian sid i386
        sudo ~/tree/bampkgbuild/create_schroot debian jessie amd64
        sudo ~/tree/bampkgbuild/create_schroot debian jessie i386

#.  Test schroot is in working order. Changes should disappear after exiting
    the schroot.

    .. code-block:: bash

        schroot --chroot jessie-amd64
        schroot --chroot jessie-amd64 --user root

#.  To make changes to the underlying chroot (you shouldn't have to do this)
    use:

    .. code-block:: bash

        schroot --chroot source:jessie-amd64

#.  If making releases you will need to have a GPG key to use to distribute
    the changes and this should have an established web of trust. If not,
    create a key and get other trusted people to sign it.

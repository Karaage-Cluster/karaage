Creating new Karaage release
============================
This section talks about the steps involved in creating a new official
release of Karaage.

It is assumed the system is running Debian Jessie; other build systems may be
possible, but will require variations.


Preparing system
----------------
These steps only need to be done once for a system.

#.  Ensure required packages installed:

    .. code-block:: bash

        apt-get install dput dpkg-dev schroot sbuild slapd
        apt-get install python-django python3-django
        apt-get install python-tldap python3-tldap
        apt-get install python-schroot python3-schroot

    The above list is probably incomplete. Any omissions will cause
    errors when running Karaage tests.

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

Make release
------------

Assume we are releasing version X.Y.Z. Obviously this needs to be
replaced with the actual version.

#.  Ensure schroot are up to date:

    .. code-block:: bash

        sudo ~/tree/bampkgbuild/update_schroot

#.  Ensure we are in the karaage tree on the master branch.

    .. code-block:: bash

        cd tree/karaage/karaage

#.  Ensure there are no git uncommited git changes or staged changes.

    .. code-block:: bash

        git status

#.  Run tests, ensure everything passes.

    .. code-block:: bash

        ./run_tests.sh

#.  Write X.Y.Z to ``VERSION.txt``.
#.  Update ``debian/changelog`` using `dch` command. Create a new entry for
    version X.Y.Z-1. The debian postfix should almost always be -1.
#.  Run tests, ensure everything still passes.

    .. code-block:: bash

        ./run_tests.sh

#.  Commit changes, using something like:

    .. code-block:: bash

        git commit -a -m "Release version X.Y.Z"

#.  Create a release tag (requires a GPG key for signing):

    .. code-block:: bash

        git tag -s X.Y.Z

    Ensure the message contains the string "Version X.Y.Z" at the top.
    Typically I copy and paste the contents of the most recent
    ``debian/changelog`` here, but this isn't essential.

#.  Build package and upload to VPAC repository (requires permission to upload
    to VPAC repository):

    .. code-block:: bash

        ~/tree/bampkgbuild/release --upload vpac --arch amd64 --working .

#.  When sure everything is ok, push changes to github:

    .. code-block:: bash

        git push origin
        git push origin --tags

#.  Merge changes into ``karaage4`` branch:

    .. code-block:: bash

        git checkout karaage4
        git merge origin

    There will be some minor conflicts, e.g. ``VERSION.txt`` will
    probably need to be manually fixed.

#.  Run tests, ensure everything still works.

    .. code-block:: bash

        ./run_tests.sh

#.  When sure everything is ok, push changes to github:

    .. code-block:: bash

        git push origin
        git push origin --tags
        git checkout master

Creating new Karaage release
============================
This section talks about the steps involved in creating a new official
release of Karaage.

It is assumed the system is running Debian Jessie; other build systems may be
possible, but will require variations.


Preparing system
----------------
These steps only need to be done once for a system.

Follow the instructions under :doc:`prepare`.


Make upstream release
---------------------
This needs to happen first before building the Debian packages. You will need
to have write access to the github repository for Karaage and PyPI.

#.  Check all changes pushed to github and
    [travis tests](https://travis-ci.org/Karaage-Cluster/karaage/builds) for
    the appropriate branch pass.

#.  Check ``CHANGES.rst`` has entry for new release.

#.  Create a tag for the new release.

    .. code-block:: bash

        git tag --sign x.y.z

#.  Check version is correct.

    .. code-block:: bash

        ./setup.py --version

#.  Push and upload.

    .. code-block:: bash

        python ./setup.py sdist upload -s -i 0xGPGKEY
        git push
        git push --tags


Make Debian release
-------------------
This needs to happen after the upstream release. You will need to have write
access to the github repository for Karaage Debian and somewhere to upload the
changes to.

#.  Ensure schroot are up to date:

    .. code-block:: bash

        sudo ~/tree/bampkgbuild/update_schroot

#.  Ensure we are in the karaage-debian tree on the master branch.

    .. code-block:: bash

        cd tree/karaage/karaage-debian

#.  Ensure there are no git uncommited git changes or staged changes.

    .. code-block:: bash

        git status

#.  Ensure all branches are up to date.

    .. code-block:: bash

        git pull --ff-only --all

#.  Download and merge new upstream source.

    .. code-block:: bash

        git checkout master
        uscan --verbose
        git-dpm import-new-upstream --ptc --rebase-patched ../karaage3_X.Y.Z.orig.tar.gz

#.  Update ``debian/changelog`` command.

    .. code-block:: bash

        dch -v "X.Y.Z-1" "New upstream version."
        git commit debian/changelog -m "Version X.Y.Z-1"
        git push --all

#.  Check Debian package builds.

#.  Make changelog for release.

    .. code-block:: bash

        dch --release
        git commit debian/changelog -m "Release version X.Y.Z"

#.  Build and upload package.

#.  When sure everything is ok, push changes to github:

    .. code-block:: bash

        git push origin
        git push origin --tags

#.  Merge changes into ``karaage4`` branch:

    .. code-block:: bash

        git checkout karaage4
        git merge origin

#.  When sure everything is ok, push changes to github:

    .. code-block:: bash

        git push origin
        git checkout master

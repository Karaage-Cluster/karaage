Creating new Karaage release
============================
This section talks about the steps involved in creating a new official
release of Karaage.

It is assumed the system is running Debian Jessie; other build systems may be
possible, but will require variations.

.. note::

    Karaage is current developed using `Gerrit <https://code.vpac.org/gerrit>`_.
    However, after 2015-06-19, this may no longer be the case. In which case
    commits should sent as github pull requests. Please check before submitting
    changes if the procedure documented here is still releveant.

    If github is no longer used, the ``git review`` commands should be
    replaced with something more appropriate, e.g. ``git push``.


Preparing system
----------------
These steps only need to be done once for a system.

Follow the instructions under :doc:`prepare`.


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

        git review

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

        git review
        git checkout master

#.  When changes are approved in gerrit, push the tags to github. Ideally this
    should be done via gerrit, but this doesn't seem to happen at present.

    .. code-block:: bash

        git fetch origin  # check changes have been pushed to origin.
        git push origin --tags

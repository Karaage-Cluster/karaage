Contributing Code
=================

.. note::

    Karaage is current developed using `Gerrit <https://code.vpac.org/gerrit>`_.
    However, after 2015-06-19, this may no longer be the case. In which case
    commits should sent as github pull requests. Please check before submitting
    changes if the procedure documented here is still releveant.

Getting Started
---------------

#.  Login to `Gerrit <https://code.vpac.org/gerrit>`_ using your favorite OpenID provider.
#.  Checkout the latest version of Karaage:

    .. code-block:: bash

        git clone https://github.com/Karaage-Cluster/karaage.git
        cd karaage

    You can test that you've setup the commit-msg script correctly by doing a
    commit and then looking at the log. You should see a "Change-Id: I[hex]"
    line show up in your commit message text.

#.  Obtain the commit-msg script.

    .. code-block:: bash

        scp -p -P 29418 code.vpac.org:hooks/commit-msg .git/hooks/

Making a change
---------------

#.  Get the latest version.

    .. code-block:: bash

        git checkout master
        git fetch origin master
        git merge --ff-only origin/master

#.  Create a new branch. Every change should be submitted as a distinct
    independant submission on a separate branch. Please try to ensure that each
    submission only changes one aspect of Karaage, submissions that merge may
    unrelated changes will be frowned upon.

    .. code-block:: bash

        git checkout -b bug_404

#.  Make changes to code.

#.  Test your changes.

    .. code-block:: bash

        export PYTHONPATH=$PWD:$PYTHONPATH
        cd test
        ./manage.py test
        cd ..

#.  Commit the changes.

    .. code-block:: bash

        git add ...
        git commit

#.  Send the patches for review:

    .. code-block:: bash

        git review

#.  Fix any problems with the patch.

#.  Amend previous commit.

    .. code-block:: bash

        git add ...
        git commit --amend

#.  Send the patches for review.

    .. code-block:: bash

        git review

#.  If you want to get back to main branch.

    .. code-block:: bash

        git checkout master
        git fetch origin master
        git merge --ff-only origin/master

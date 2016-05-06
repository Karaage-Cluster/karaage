Contributing Code
=================

github pull requests should be used.


Getting Started
---------------

#.  Checkout the latest version of Karaage:

    .. code-block:: bash

        git clone https://github.com/Karaage-Cluster/karaage.git
        cd karaage

    You can test that you've setup the commit-msg script correctly by doing a
    commit and then looking at the log. You should see a "Change-Id: I[hex]"
    line show up in your commit message text.

#.  Make changes, commit, and submit as github pull request.

#.  After the pull request is created, travis will run a complete set of tests
    against the request to ensure it doesn't break Karaage.

Karaage 4
=========

**Cluster account management tool.**

.. contents :: Table of Contents

Overview
--------

Karaage manages users and projects in a cluster and can store the data in
various backends.


Project background
------------------

Karaage 4 will extend Karaage 3 to allow management of resource allocations to
projects based on grants. It will also make Karaage faster and more responsive.


Karaage 4 proposal
------------------

A Karaage Enhancement Proposal -- KEP 4000 -- similar to a `Python Enhancement
Proposal <https://www.python.org/dev/peps/pep-0001/#what-is-a-pep>`_ is being
developed.

A link to KEP 4000 will being added to this README once the draft is complete,
and comment from the Karaage community will be sought.


Documentation
-------------

The Karaage 4 documentation will be available soon on `ReadTheDocs
<http://readthedocs.org/>`_.

Mailing list: `<http://lists.vpac.org/cgi-bin/mailman/listinfo/karaage>`_

Old gerrit code review tool (not used anymore): `<https://code.vpac.org/gerrit>`_

Karaage 2.7.x: <http://karaage.readthedocs.org/en/2.7.stable/>`_.

Karaage 3.x User documentation:
`<http://karaage.readthedocs.org/projects/karaage-user/en/latest/>`_

Karaage 3.x Programmer documentation:
`<http://karaage.readthedocs.org/projects/karaage-programmer/en/latest/>`_

Karaage 3.x Admin documentation: `<http://karaage.readthedocs.org/en/latest/>`_

Software requirements specification:
`<http://karaage.readthedocs.org/projects/karaage-srs/en/latest/>`_



Components
----------

Prior to Karaage 3.1.11, the various Karaage modules had been in seperate
repositories. They have now been brought together into one repo.

These modules are:

- karaage-applications (also see `Karaage 3 karaage-applications
  <https://github.com/Karaage-Cluster/karaage-applications>`_)
- karaage-cluster-tools  (also see `Karaage 3 karaage-cluster-tools
  <https://github.com/Karaage-Cluster/karaage-cluster-tools>`_)
- karaage-software (also see `Karaage 3 karaage-software
  <https://github.com/Karaage-Cluster/karaage-software>`_)
- karaage-usage (also see `Karaage 3 karaage-usage
  <https://github.com/Karaage-Cluster/karaage-usage>`_)


Plugins
-------

karaage-usage
^^^^^^^^^^^^^

.. todo:: Write paragraph about what the usage plugin does.

The karaage-usage plugin provides monitoring of usage information.

karaage-applications
^^^^^^^^^^^^^^^^^^^^

This plugin allows users to self register accounts with Karaage.


karaage-software
^^^^^^^^^^^^^^^^

.. todo:: Write paragraph about what the software plugin does.


Contact
-------

The lead developer for Karaage 3 is `Brian May
<mailto:"brian@v3.org.au">`_.

Setting up a development instance
---------------------------------

The steps below will guide you through setting up an instance of Karaage 4.

Step 1. Install system dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ sudo apt-get remove karaage\*
    $ sudo apt-get install libcrack2-dev csstidy slapd ldap-utils
    $ sudo apt-get build-dep python-cracklib

Step 2. Install pip, virtualenv and virtualenvwrapper
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You may already have these installed. If so, skip this step.

::

    $ sudo apt-get install python-pip
    $ sudo pip install virtualenv virtualenvwrapper

Add these lines to the end of your ``~/.bashrc`` file::

    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh

Reload ``~/.bashrc``::

    $ source ~/.bashrc

Step 3. Set up a virtualenv
^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ mkvirtualenv karaage4

Add these lines to the end of ``~/.virtualenvs/karaage4/bin/postactivate``::

    export KARAAGE_SECRET_KEY='d4-5vjhdyi)673gd56#ge@3r8t#*)+s8z-z0l!_sy94ol!m'
    export KARAAGE_DEBUG='True'
    export DJANGO_PIPELINE_ENABLED='False'
    export KARAAGE_DB_ENGINE='django.db.backends.mysql'

Restart the virtualenv so that these setting take effect:

::

    $ deactivate
    $ workon karaage4

Step 4. Install Karaage 4
^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ pip install -e 'git+https://github.com/vlsci/karaage#egg=karaage4[usage,applications,software]'

Step 5. Migrate database
^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ kg-manage migrate

Step 6. Start the server
^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ kg-manage runsslserver 0:8000

Step 7. Open Karaage
^^^^^^^^^^^^^^^^^^^^

Browse to ``https://localhost:8000``

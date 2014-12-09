Karaage 4
=========

**Cluster account management tool.**


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


Components
----------

Prior to Karaage 4, the various Karaage modules had been in seperate
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


Software requirements specification
-----------------------------------

The software requirements specification for Karaage 3 is `here
<https://github.com/Karaage-Cluster/karaage-srs>`_.

This document will be updated for Karaage 4 soon.


Installation
------------

To install Karaage from PyPi without any optional plugins::

        $ pip install karaage4

To install with all optional plugins::

        $ pip install karaage4[applications,usage,software]

Plugins
-------

karaage-usage
^^^^^^^^^^^^^

.. todo:: Write paragraph about what the usage plugin does.

The karaage-usage plugin provides monitoring of usage information, 
install with::

    $ pip install 'karaage4[usage]'

karaage-applications
^^^^^^^^^^^^^^^^^^^^

.. todo:: Write paragraph about what the applications plugin does.

The karaage-applications plugin, install with::

    $ pip install 'karaage4[applications]'

karaage-software
^^^^^^^^^^^^^^^^

.. todo:: Write paragraph about what the software plugin does.

The karaage-software plugin, install with::

    $ pip install 'karaage4[software]'

Contact
-------

The lead developer for Karaage 4 is `Tyson Clugg
<mailto:"tyson@commoncode.com.au">`_.

Karaage Architecture
====================

This document describes the basic Karaage architecture.

Karaage core
------------
.. py:module:: karaage.models

The core Karaage defines the following db models in the
:py:mod:`karaage.models` module.

.. py:class:: LogEntry

   Represents a log entry for any action or comment left on an object.

.. py:class:: Institute

   Represents an institute for a user.

.. py:class:: InstituteQuota

   Represents the quota for a machine category for an institute.

.. py:class:: InstituteDelegate

   Represents a delegate for an institute with extra attributes.

.. py:class:: MachineCategory

   Represents a machine category. Each machine category in Karaage in
   considered distinct with its own data stores and monitoring.

.. py:class:: Machine

   Represents an individual machine or cluster in a machine category.

.. py:class:: Account

   Represents an account for a particular person on a particular machine
   category.

.. py:class:: Person

   Represents a person who may have one or more accounts. A person is global
   across all machine categories.

.. py:class:: Group

   Represents a group of people. A group is global accross all machine
   categories.

.. py:class:: Project

   Represents a project for a set of machine categories. A project is
   considered global, although is only active on given machine categories.

.. py:class:: ProjectQuota

   Represents the quota for a project on a particular machine category.  If
   there is no :py:class:`ProjectQuota` for a particular project on a
   particular machine category, then the project is not active on that machine
   category.

Karaage Applications
--------------------
.. py:module:: kgapplications.models

Karaage Applications is a plugin that defines additional functionality
used for applications. It defines the following db models in the
:py:mod:`kgapplications.models` module.

.. py:class:: Application

   Abstract class that represents any application. Further classes should
   inherit from this class.

.. py:class:: ProjectApplication

   Class that is derived from :py:class:`Application` for project applications.

.. py:class:: Applicant

   An applicant for an application who doesn't already have a
   :py:class:`karaage.models.Person` entry.


Karaage Software
----------------
.. py:module:: kgsoftware.models

Karaage Software is a plugin that defines additional functionality
used for tracking software. It defines the following db models in the
:py:mod:`kgsoftware.models` module.

.. py:class:: Software

   Represents a particular software package.

.. py:class:: SoftwareCategory

   Represents a category of software, for easy searching.

.. py:class:: SoftwareVersion

   Repesents a specific version of a software package.

.. py:class:: SoftwareLicense

   Represents a license for a software package. A software package may have
   zero or more licenses. If there are none, the user' won't be able to
   add the software. There there are more then one, the latest is used by
   default.

.. py:class:: SoftwareLicenseAgreement

   Represents the fact a person agreed to a particular
   :py:class:`SoftwareLicense` at a particular point in time.

.. py:class:: SoftwareApplication

   Class that is derived from :py:class:`kgapplications.models.Application` for
   applications to access restricted software.


Karaage Usage
--------------
Karaage Usage is a plugin that defines additional functionality
used for tracking cluster usage. It may get rewritten in the future, and
you should not rely on anything remaining the same.

Glossary
========

..  glossary::
    :sorted:

    person
      A person who has access to the Karaage system. A person could have
      one/more accounts, be an administrator, be a project leader, be an
      :term:`institute delegate`. These are optional.

    machine
      A single cluster or computer which is managed as a distinct unit.

    machine category
      A group of :term:`machines <machine>` that share the same authentication
      systems.

    data store
      A list of external databases that we should link to and update
      automatically.  Supported databases include LDAP, MAM, and Slurm.

    global data store
      A :term:`data store` for storing global data.  The global datastores are
      responsible for writing global data, such as :term:`people <person>` (not
      :term:`accounts <account>`) to external databases such as LDAP.

    machine category data store
      A :term:`data store` for storing :term:`machine category` specific data
      The machine category datastores are specific to a given machine machine,
      and are responsible for writing machine category specific data, such as
      :term:`accounts <account>` (not :term:`people <person>`) to external
      databases such as LDAP.

    account
      A person may have one or more accounts. An account allows a person to
      access :term:`machines <machine>` on a given :term:`machine category`.

    group
      A list of :term:`people <person>`. Usually maps directly to an LDAP
      Group, but this depends on the data stores used.

    project
      A list of :term:`people <person>` who share a common goal.

    project leader
      A person who manages a :term:`project`, and can allow new user's to use
      the project.

    institute
      An entity that represents the organisation or group that every
      :term:`person` and :term:`project` belongs to.

    institute delegate
      A person who manages an term:`institute`, and can allow new
      :term:`project's <project>` for the institute.

    administrator
      A person who has unlimited access to Karaage.

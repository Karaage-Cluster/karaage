Glossary
========

..  glossary::
    :sorted:

    person
    people
      A person who has access to the Karaage system. A person could have one/more
      accounts, be an administrator, be a project leader, be an institute
      delegate. These are optional.

    machine
      A single cluster or computer which is managed as a distinct unit.

    machine category
      A group of machines that share the same authentication systems.

    data store
      A list of external databases that we should link to and update automatically.
      Supported databases include LDAP, Gold, and Slurm.

    account
      A person may have one or more accounts. An account allows a person to access
      machines on a given machine_category.

    group
      A list of people. Usually maps directly to an LDAP Group, but this depends on
      the data stores used.

    project
      A list of people who share the common goal.

    project leader
      A person who manages a project, and can allow new user's to use the project.

    institute
      An Institute is just a group of projects.

    institute delegate
      A person who manages an institute, and can allow new project's for the
      institute.

    administrator
      A person who has unlimited access to Karaage.

Datastores
==========

::

    DATASTORES = {
        'ldap' : [
            {
                'DESCRIPTION': 'Default LDAP datastore',
                'ENGINE': 'karaage.datastores.ldap_datastore.AccountDataStore',
                'LDAP': 'default',
                'ACCOUNT': 'karaage.datastores.ldap_schemas.openldap_account',
                'GROUP': 'karaage.datastores.ldap_schemas.openldap_group',
                'PRIMARY_GROUP': "institute",
                'DEFAULT_PRIMARY_GROUP': "dummy",
                'HOME_DIRECTORY': "/home/%(uid)s",
                'LOCKED_SHELL': "/usr/local/sbin/locked",
            },
            {
                'DESCRIPTION': 'Default Gold datastore',
                'ENGINE': 'karaage.datastores.gold.GoldDataStore',
                'PREFIX': ['/bin/true'],
                'PATH': '/ohmygod',
                'NULL_PROJECT': 'dummy',
            },
        ],
        'dummy' : [
        ],
    }


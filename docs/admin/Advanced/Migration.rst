Migrating Users to Karaage
==========================

*New in Karaage 2.4.14*

If you already have users in an LDAP or LDAP like system (NIS etc.) you
can migrate your users into karaage by a couple of means.

Karaage has a command line interface that can be used to script
importing users.

1st create a csv file like the following.

::

    username,password,first_name,last_name,email,institute,project
    sam,secret,Joe,Bloggs,joe@example.com,Test,TestProject2
    bob,secret2,Bob,Smith,bob@example.com,Example University

Notes: \* You need to specify the headers. \* You can leave out the
project for a user and they will be created in Karaage but with no
cluster account.

Run the karaage csv import

::

    kg-manage import_csv_users /path/to/file.csv


Apply database migrations
=========================

Normally if you are using the Debian packages, you should be able to
skip this section, as this should happen automatically when you update
the karaage-admin and karaage-registration packages.

To see a list of database migrations

::

    kg-manage --list

Applied migrations will have a '\*' next to them

To apply all pending migrations do

::

    kg-manage migrate

If you need to apply a specific migration do

::

    kg-manage migrate <appname>

 will be the name of the karaage app eg. people

You should always backup your database before upgrading karaage.

After you have done all this you will need to reload apache.

Enabling Database transaction support
=====================================

Karaage has built in DB transaction support.

If you are using MySQL however you need to use InnoDB as the default
storage engine MyISAM doesn't support transactions.

You should enable it on all tables except for the cpu\_job table as it
isn't needed and also for perfomance reasons.

To get a list of the commands to run do: (on debian with database
name=karaage. modify to suit)

::

    echo 'SHOW TABLES;'  | mysql --defaults-file=/etc/mysql/debian.cnf karaage  | awk '!/^Tables_in_/ {print "ALTER TABLE `"$0"` ENGINE = InnoDB;"}'  | column -t


# Copyright 2012-2014 Brian May
#
# This file is part of python-tldap.
#
# python-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-tldap  If not, see <http://www.gnu.org/licenses/>.

""" DB model for a counter to keep track of next uidNumber and gidNumber to use
for new LDAP objects. """

from django.db import models, transaction


class Counters(models.Model):
    """ Keep track of next uidNumber and gidNumber to use for new LDAP objects.
    """
    scheme = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=20, db_index=True)
    count = models.IntegerField()

    class Meta:
        db_table = 'tldap_counters'

    @classmethod
    @transaction.atomic
    def get_and_increment(cls, scheme, name, default, test):
        entry, c = cls.objects.select_for_update().get_or_create(
            scheme=scheme, name=name, defaults={'count': default})

        while not test(entry.count):
            entry.count = entry.count + 1

        n = entry.count

        entry.count = entry.count + 1
        entry.save()

        return n

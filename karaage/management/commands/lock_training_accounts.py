# Copyright 2012-2015 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import BaseCommand
from django.conf import settings

from karaage.people.models import Person

import django.db.transaction
import tldap.transaction


class Command(BaseCommand):
    help = "Lock all training accounts"

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, **options):

        verbose = int(options.get('verbosity'))
        training_prefix = getattr(settings, 'TRAINING_ACCOUNT_PREFIX', 'train')

        query = Person.active.all()
        query = query.filter(username__startswith=training_prefix)
        query = query.order_by('username')

        for person in query.all():
            try:
                person.lock()
                if verbose > 1:
                    print("%s: Locked" % person.username)
            except Exception as e:
                print("%s: Failed to lock: %s" % (person, e))

# Copyright 2010-2011, 2013-2015 VPAC
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
import django.db.transaction
import tldap.transaction


class Command(BaseCommand):
    help = "Lock expired accounts"

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        from karaage.common import log
        from karaage.people.models import Person
        from django.core.mail import mail_admins
        import datetime
        today = datetime.date.today()

        verbose = int(options.get('verbosity'))

        for p in Person.objects.filter(expires__lte=today):
            try:
                if not p.is_locked():
                    p.lock()
                    p.expires = None
                    p.save()
                    message = "%s's account has expired and their account " \
                        "has been locked. %s does not know this" % (p, p)
                    mail_admins(
                        'Locked expired user %s' % p,
                        message, fail_silently=False)
                    log.change(p, 'Account auto expired')
                    if verbose >= 1:
                        print("Locked account for %s - %s" % (p.username, p))
            except:
                print("Failed to lock %s" % p)

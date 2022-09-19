# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

import sys

import django.db.transaction
import tldap.transaction
from django.conf import settings
from django.core.management.base import BaseCommand

from karaage.people.models import Person


# Generate a human readable 'random' password
# password  will be generated in the form 'word'+digits+'word'
# eg.,nice137pass
# parameters: number of 'characters' , number of 'digits'
# Pradeep Kishore Gowda <pradeep at btbytes.com >
# License : GPL
# Date : 2005.April.15
# Revision 1.2
# ChangeLog:
# 1.1 - fixed typos
# 1.2 - renamed functions _apart & _npart to a_part
#       & n_part as zope does not allow functions to
# start with _
def nicepass(alpha=8, numeric=4):
    """
    returns a human-readble password (say rol86din instead of
    a difficult to remember K8Yn9muL )
    """
    import random
    import string

    vowels = ["a", "e", "i", "o", "u"]
    consonants = [a for a in string.ascii_lowercase if a not in vowels]
    digits = string.digits

    # utility functions
    def a_part(slen):
        ret = ""
        for i in range(slen):
            if i % 2 == 0:
                randid = random.randint(0, 20)  # number of consonants
                ret += consonants[randid]
            else:
                randid = random.randint(0, 4)  # number of vowels
                ret += vowels[randid]
        return ret

    def n_part(slen):
        ret = ""
        for i in range(slen):
            randid = random.randint(0, 9)  # number of digits
            ret += digits[randid]
        return ret

    ####
    fpl = alpha / 2
    if alpha % 2:
        fpl = int(alpha / 2) + 1
    lpl = alpha - fpl

    start = a_part(fpl)
    mid = n_part(numeric)
    end = a_part(lpl)

    return "%s%s%s" % (start, mid, end)


class Command(BaseCommand):
    help = "Unlock all training accounts and reset password."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password", dest="password", action="store_true", default=False, help="Read password to use on stdin."
        ),
        parser.add_argument("--number", dest="number", type=int, help="Number of accounts to unlock"),

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, *args, **options):
        verbose = int(options.get("verbosity"))
        training_prefix = getattr(settings, "TRAINING_ACCOUNT_PREFIX", "train")

        # If training accounts are system users, they will be found by
        # Person.objects.all() but not Person.active.all()
        query = Person.objects.all()
        query = query.filter(username__iregex=training_prefix)
        query = query.order_by("username")

        if options["number"] is not None:
            query = query[: options["number"]]

        password = None
        if options["password"]:
            password = sys.stdin.readline().strip()
        else:
            password = nicepass(8, 4)
            print("New password: %s" % password)

        for person in query.all():
            try:
                if password is not None:
                    if verbose > 1:
                        print("%s: Setting password" % person.username)
                    person.set_password(password)
                    # person.unlock() will call person.save()

                if verbose > 1:
                    print("%s: Unlocking" % person.username)
                person.unlock()

            except Exception as e:
                print("%s: Failed to unlock: %s" % (person.username, e))

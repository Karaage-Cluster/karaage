# Copyright 2007-2013 VPAC
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

import datetime

from karaage.projects.models import Project
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.machines.models import MachineCategory
import karaage.cache.usage as cache
import django.db.transaction
import tldap.transaction


PERIODS = [ 7, 90, 365 ]

def pop_project_cache(period):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=period)

    for p in Project.active.all():
        for machine_category in MachineCategory.objects.all():
            cache.get_project_usage(p, start, end, machine_category)


def pop_institute_cache(period):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=period)
    
    for i in Institute.active.all():
        for machine_category in MachineCategory.objects.all():
            cache.get_institute_usage(i, start, end, machine_category)


def pop_user_cache(period):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=period)

    for u in Person.active.all():
        for p in u.projects.all():
            for machine_category in MachineCategory.objects.all():
                cache.get_person_usage(u, p, start, end, machine_category)

def gen_last_usage_project():
    for p in Project.objects.all():
        try:
            date = p.cpujob_set.all()[:1][0].date
        except:
            date = None
        p.last_usage = date
        p.save()


def gen_last_usage_user():
    for person in Person.active.all():
        date = None
        
        for ua in person.account_set.all():

            try:
                d = ua.cpujob_set.all()[:1][0].date
            except:
                d = None

            if date is None:
                if d is not None:
                    date = d
            else:
                if d is not None and d > date:
                    date = d
        person.last_usage = date
        person.save()
    

class Command(BaseCommand):
    help = "Populate usage cache"
    
    @django.db.transaction.commit_on_success
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        verbose = int(options.get('verbosity'))

        for p in PERIODS:
            if verbose > 1:
                print "Populating Project cache for last %s days" % p
            pop_project_cache(p)
            if verbose > 1:
                print "Populating Institute cache for last %s days" % p
            pop_institute_cache(p)
            if verbose > 1:
                print "Populating User cache for last %s days" % p
            pop_user_cache(p)

        if verbose > 1:
            print "Populating last usage date for projects"
        gen_last_usage_project()
        if verbose > 1:
            print "Populating last usage date for users"
        gen_last_usage_user()

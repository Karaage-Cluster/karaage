from django.core.management.base import BaseCommand, CommandError

PERIODS = [ 7, 90, 365 ]

from karaage.machines.models import Machine
from karaage.projects.models import Project
from karaage.people.models import Institute, Person
import datetime

def pop_project_cache(period):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=period)

    for p in Project.active.all():
        p.get_usage(start, end)


def pop_institute_cache(period):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=period)
    
    for i in Institute.active.all():
        i.get_usage(start, end)


def pop_user_cache(period):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=period)

    for u in Person.active.all():
        for p in u.project_set.all():
            u.get_usage(p, start,end)

def gen_last_usage_project():
    for p in Project.objects.all():
        try:
            date = p.cpujob_set.all()[:1][0].date
        except:
            date = None
        p.last_usage = date
        p.save()


def gen_last_usage_user():
    for user in Person.active.all():
        date = None
        
        for ua in user.useraccount_set.all():

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
        user.last_usage = date
        user.save(update_datastore=False)
    

class Command(BaseCommand):
    help = "Populate usage cache"
    
    def handle(self, **options):
        verbose = int(options.get('verbosity'))

        for p in PERIODS:
            if verbose >= 1:
                print "Populating Project cache for last %s days" % p
            pop_project_cache(p)
            if verbose >= 1:
                print "Populating Institute cache for last %s days" % p
            pop_institute_cache(p)
            if verbose >= 1:
                print "Populating User cache for last %s days" % p
            pop_user_cache(p)

        if verbose >= 1:
            print "Populating last usage date for projects"
        gen_last_usage_project()
        if verbose >= 1:
            print "Populating last usage date for users"
        gen_last_usage_user()

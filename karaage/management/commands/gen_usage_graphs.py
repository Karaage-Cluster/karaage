from django.core.management.base import BaseCommand, CommandError

PERIODS = [ 7, 90, 365 ]

def gen_all_project_graphs(period):
    from karaage.projects.models import Project
    from karaage.graphs import gen_project_graph
    import datetime
    project_list = Project.objects.all()

    end = datetime.date.today()
    start = end - datetime.timedelta(days=period)

    for p in project_list:
        for mc in p.machine_categories.all():
            gen_project_graph(p, start, end, mc)


class Command(BaseCommand):
    help = "Generates usage graphs"
    
    def handle(self, **options):
        verbose = int(options.get('verbosity'))

        for p in PERIODS:
            if verbose > 1:
                print "Generating project graphs for last %s days" % p
            gen_all_project_graphs(p)


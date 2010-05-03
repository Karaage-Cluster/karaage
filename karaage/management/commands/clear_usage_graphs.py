from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
GRAPH_BASE_DIR = settings.GRAPH_ROOT

class Command(BaseCommand):
    help = "Deletes all usage graphs"
    
    def handle(self, **options):
        verbose = int(options.get('verbosity'))

        if verbose >= 1:
            print "Cleaning all Project graphs"

        PROJECT_DIR = '%s/projects/' % GRAPH_BASE_DIR
        file_list = os.listdir(PROJECT_DIR)
        for f in file_list:
            if not f == '.svn':
                os.remove('%s%s' % (PROJECT_DIR,f))
            
        if verbose >= 1:
            print "Cleaning all Institute graphs"

        INSTITUTE_DIR = '%s/institutes/' % GRAPH_BASE_DIR
        file_list = os.listdir(INSTITUTE_DIR)
        for f in file_list:
            if not f == '.svn':
                os.remove('%s%s' % (INSTITUTE_DIR,f))

        if verbose >= 1:
            print "Cleaning all trend graphs"
        

        TRENDS_DIR = '%s/trends/' % GRAPH_BASE_DIR
        file_list = os.listdir(TRENDS_DIR)
        for f in file_list:
            if not f == '.svn':
                os.remove('%s%s' % (TRENDS_DIR,f))

        if verbose >= 1:
            print "Cleaning all institute trend graphs"

        I_TRENDS_DIR = '%s/i_trends/' % GRAPH_BASE_DIR
        file_list = os.listdir(I_TRENDS_DIR)
        for f in file_list:
            if not f == '.svn':
                os.remove('%s%s' % (I_TRENDS_DIR,f))



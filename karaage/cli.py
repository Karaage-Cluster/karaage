import os
import sys
from django.core.management import execute_from_command_line

def manage():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karaage.conf.settings')
    execute_from_command_line(sys.argv)

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Cleans up usage cache"
    
    def handle(self, **options):
        verbose = int(options.get('verbosity'))
        from karaage.cache.models import ProjectCache, InstituteCache, UserCache, MachineCache
        if verbose >= 1:
            print "Clearing project cache"
        ProjectCache.objects.all().delete()
        if verbose >= 1:
            print "Clearing institute cache"
        InstituteCache.objects.all().delete()
        if verbose >= 1:
            print "Clearing user cache"
        UserCache.objects.all().delete()
        if verbose >= 1:
            print "Clearing machine cache"
        MachineCache.objects.all().delete()
        
        

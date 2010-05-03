from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Lock expired accounts"
    
    def handle(self, **options):
        from karaage.util import log_object as log
        from karaage.people.models import Person
        from django.core.mail import mail_admins  
        import datetime
        today = datetime.date.today()
        
        verbose = int(options.get('verbosity'))
        
        for p in Person.objects.filter(expires__lte=today):
            try:
                if not p.is_locked():
                    p.lock()
                    p.expires = ""
                    p.save()
                    message = "%s's account has expired and their account has been locked. %s does not know this" % (p, p)
                    mail_admins('Locked expired user %s' % p,  message, fail_silently=False)
                    log(p.user, p, 2, 'Account auto expired')
                    if verbose >= 1:
                        print "Locked account for %s - %s" % (p.user.username, p)
            except:
                print "Failed to lock %s" % p

        

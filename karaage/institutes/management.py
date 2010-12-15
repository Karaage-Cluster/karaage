"""
Creates the default Site object.
"""

# Shouldn't really be here but need somewhere that isn't managed by south and will execute.
from django.db.models import signals
from django.contrib.sites.models import Site
from django.contrib.sites import models as site_app

def create_secondary_site(app, created_models, verbosity, db, **kwargs):
    if Site in created_models:
        if verbosity >= 2:
            print "Creating registration Site object"
        s = Site(domain="example.com", name="registration")
        s.save(using=db)
    Site.objects.clear_cache()

signals.post_syncdb.connect(create_secondary_site, sender=site_app)

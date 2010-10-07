"""
Creates the default MachineCategory object.
"""

from django.db.models import signals
from karaage.machines.models import MachineCategory
from karaage.machines import models as machines_app

def create_default_machinecategory(app, created_models, verbosity, db, **kwargs):
    if MachineCategory in created_models:
        if verbosity >= 2:
            print "Creating Default MachineCategory object"
        mc = MachineCategory(name='Default')
        mc.save(using=db)
    MachineCategory.objects.clear_cache()

signals.post_syncdb.connect(create_default_machinecategory, sender=machines_app)

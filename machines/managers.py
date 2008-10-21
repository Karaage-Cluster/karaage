from django.db import models
import datetime

class MachineCategoryManager(models.Manager):
    def get_default(self):
        from django.conf import settings
        return self.get(pk=settings.DEFAULT_MC)


class ActiveMachineManager(models.Manager):
    def get_query_set(self):
        today = datetime.datetime.today()
        return super(ActiveMachineManager, self).get_query_set().filter(end_date__isnull=True)

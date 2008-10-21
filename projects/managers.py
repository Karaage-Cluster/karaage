from django.db import models

class ActiveProjectManager(models.Manager):
    def get_query_set(self):
        return super(ActiveProjectManager, self).get_query_set().filter(is_active=True)


class DeletedProjectManager(models.Manager):
    def get_query_set(self):
        return super(DeletedProjectManager, self).get_query_set().filter(is_active=False)



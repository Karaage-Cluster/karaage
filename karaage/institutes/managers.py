from django.db import models

class PrimaryInstituteManager(models.Manager):
    """
    Returns only 'primary' institutes.
    Primary institute is one that can host projects.
    """
    def get_query_set(self):
        return super(PrimaryInstituteManager, self).get_query_set().filter(delegate__isnull=False)


class ValidChoiceManager(models.Manager):
    """
    Returns only 'primary' institutes.
    Primary institute is one that can host projects.
    """
    def get_query_set(self):
        removed_ids = [ 40, 11 ]
        return super(self.__class__, self).get_query_set().filter(delegate__isnull=False).exclude(id__in=removed_ids)
    

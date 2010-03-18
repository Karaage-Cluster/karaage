from django.db import models


class ActiveUserManager(models.Manager):
    def get_query_set(self):
        return super(ActiveUserManager, self).get_query_set().filter(user__is_active=True)


class DeletedUserManager(models.Manager):
    def get_query_set(self):
        return super(DeletedUserManager, self).get_query_set().filter(user__is_active=False)

class LeaderManager(models.Manager):
    def get_query_set(self):
        leader_ids= []
        for l in super(LeaderManager, self).get_query_set().filter(user__is_active=True):
            if l.is_leader():
                leader_ids.append(l.id)

        from karaage.people.models import Person
        return Person.objects.filter(id__in=leader_ids)
        
       

from django.db import models

import datetime

from karaage.people.models import Person

from managers import MachineCategoryManager, ActiveMachineManager


class MachineCategory(models.Model):
    name = models.CharField(max_length=100)
    objects = MachineCategoryManager()

    class Meta:
        verbose_name_plural ='machine categories'
        db_table = 'machine_category'

    def __unicode__(self):
        return self.name


class Machine(models.Model):
    name = models.CharField(max_length=50)
    no_cpus = models.IntegerField()
    no_nodes = models.IntegerField()
    type = models.CharField(max_length=100)
    category = models.ForeignKey(MachineCategory)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    pbs_server_host = models.CharField(max_length=50, null=True, blank=True)
    mem_per_core = models.IntegerField(help_text="In GB", null=True, blank=True)
    objects = models.Manager()
    active = ActiveMachineManager()

    class Meta:
        db_table = 'machine'

    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('kg_machine_detail', [self.id])

    def get_usage(self, start=datetime.date.today()-datetime.timedelta(days=90), end=datetime.date.today()):
        from karaage.util.usage import get_machine_usage
        return get_machine_usage(self, start, end)



from karaage.projects.models import Project

class UserAccount(models.Model):
    user = models.ForeignKey(Person)
    username = models.CharField(max_length=100)
    machine_category = models.ForeignKey(MachineCategory)
    default_project = models.ForeignKey(Project, null=True, blank=True)
    date_created = models.DateField()
    date_deleted = models.DateField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True)
    previous_shell = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['user',]
        db_table = 'user_account'

    def __unicode__(self):
        return '%s %s' % (self.user.get_full_name(), self.machine_category.name)
    
    def get_absolute_url(self):
        return self.user.get_absolute_url()
    
    def project_list(self):
        return self.user.project_set.filter(machine_category=self.machine_category)
    
    def get_latest_usage(self):
        try:
            return self.cpujob_set.all()[:5]
        except:
            return None

    def deactivate(self):
        from karaage.datastores import delete_account
        delete_account(self)

    def change_shell(self, shell):
        from karaage.datastores import change_shell
        change_shell(self, shell)

    def get_disk_quota(self):
        if self.disk_quota:
            return self.disk_quota
        try:
            iq = self.user.institute.institutechunk_set.get(machine_category=self.machine_category)
        except:
            return None
        
        return iq.disk_quota
    
    def loginShell(self):
        try:
            from placard.connection import LDAPConnection
            conn = LDAPConnection()
            try:
                ldap_user = conn.get_user('uid=%s' % self.username)
            except:
                return ''
            try:
                return ldap_user.loginShell
            except:
                return ''
        except:
            pass

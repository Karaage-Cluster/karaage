from django.db import models

import datetime

from karaage.people.models import Person, Institute
from karaage.machines.models import MachineCategory

from managers import ActiveProjectManager, DeletedProjectManager


class Project(models.Model):
    pid = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(Person, blank=True, null=True)
    institute = models.ForeignKey(Institute)
    leader = models.ForeignKey(Person, related_name='leader')
    description = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_expertise = models.BooleanField()
    additional_req = models.TextField(null=True, blank=True)
    machine_category = models.ForeignKey(MachineCategory)
    is_active = models.BooleanField()
    approved_by = models.ForeignKey(Person, related_name='project_approver', null=True, blank=True, editable=False)
    date_approved = models.DateField(null=True, blank=True, editable=False)
    deleted_by = models.ForeignKey(Person, related_name='project_deletor', null=True, blank=True, editable=False)
    date_deleted = models.DateField(null=True, blank=True, editable=False)
    last_usage = models.DateField(null=True, blank=True, editable=False)
    cap = models.IntegerField(null=True, blank=True)
    objects = models.Manager()
    active = ActiveProjectManager()
    deleted = DeletedProjectManager()

    class Meta:
        ordering = ['institute', 'pid']
        
    def __unicode__(self):
        return '%s - %s' % (self.pid, self.name)
    
    def get_absolute_url(self):
        site = Site.objects.get_current()
        if site.id == 3:
            from accounts.user import settings as user_settings
            site = Site.objects.get(pk=user_settings.SITE_ID)
            return "%s/%sprojects/%s/" % (site.domain, user_settings.BASE_URL, self.pid)
        else:
            return reverse('ac_project_detail', args=[self.pid])
        
    def get_usage_url(self):
        site = Site.objects.get_current()
        if site.id == 2:
            from accounts.user import usage_settings
            site = Site.objects.get(pk=usage_settings.SITE_ID)
            return '%s/%susage/%i/institute/%i/%s/' % (site.domain, usage_settings.BASE_URL, self.machine_category.id, self.institute.id, self.pid)
        else:
            return reverse('ac_project_usage', args=[self.institute.id, self.pid])
        
    def deactivate(self):
        #from accounts.util.email_messages import send_removed_from_project_email
        self.is_active = False
        deletor = get_current_user()    
        self.deleted_by = deletor.get_profile()
        self.date_deleted = datetime.datetime.today()
        #for u in self.users.all():
        #    send_removed_from_project_email(u, self)
        self.users.clear()
        self.save()

    def get_usage(self, start=datetime.date.today()-datetime.timedelta(days=90), end=datetime.date.today()):
        from accounts.util.usage import get_project_usage
        return get_project_usage(self, start, end)

    def gen_usage_graph(self, start, end, machine_category=None):
        if machine_category is None:
            machine_category = self.machine_category
        from accounts.graphs import gen_project_graph
        gen_project_graph(self, start, end, machine_category)

    def get_latest_usage(self):
        return self.cpujob_set.all()[:5]

    def get_cap(self):
        try:
            iq = self.institute.institutequota_set.filter(machine_category=self.machine_category)[0]
        except:
            return None

        if self.cap is not None:
            return self.cap
        if iq.cap is not None:
            return iq.cap
        return iq.quota * 1000

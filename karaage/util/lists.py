from andsome.util import unique

from karaage.people.models import Person
from karaage.machines.models import MachineCategory

def get_ml_vpac_users():
    mc = MachineCategory.objects.get(name='VPAC')
    emails = []
    for u in Person.active.all():
        if not u.is_locked():
            if u.has_account(mc):
                if u.email:
                    if u.email != 'unknown@vpac.org':
                        emails.append(u.email)
                        
    emails = unique(emails)
    emails.sort()
    
    return emails

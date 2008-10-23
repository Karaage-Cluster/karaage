from django.conf import settings

module = __import__(settings.PERSONAL_DATASTORE, {}, {}, [''])

pds = module.PersonalDataStore()

def create_new_user(data, hashed_password=None):
    return pds.create_new_user(data, hashed_password)

def activate_user(person):
    pds.activate_user(person)

def delete_user(person):
    pds.delete_user(person)

def update_user(person):
    pds.update_user(person)

account_datastores = settings.ACCOUNT_DATASTORES

def create_account(person, default_project, machine_category):
    ads_module = __import__(account_datastores[machine_category.id], {}, {}, [''])
    ads = module.AccountDataStore(machine_category)
    ads.create_account(person, default_project)


def delete_account(ua):
    ads_module = __import__(account_datastores[ua.machine_category.id], {}, {}, [''])
    ads = module.AccountDataStore(ua.machine_category)
    ads.delete_account(ua)

def update_account(ua):
    ads_module = __import__(account_datastores[ua.machine_category.id], {}, {}, [''])

    ads = module.AccountDataStore(ua.machine_category)
    ads.update_account(ua)

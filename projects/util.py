from karaage.datastores import create_account

def add_user_to_project(person, project):

    project.users.add(person)
    
    for mc in project.machine_categories.all():
        if not person.has_account(mc):
            create_account(person, project, mc)

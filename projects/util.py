from karaage.datastores import create_account

from models import Project


def add_user_to_project(person, project):

    project.users.add(person)
    
    for mc in project.machine_categories.all():
        if not person.has_account(mc):
            create_account(person, project, mc)


def get_new_pid(institute, is_expertise=False):
    """ Return a new Project ID                                                                                                                                         Keyword arguments:                                                                                                                                               
    institute_id -- Institute id                                                                                                                                     
    is_expertise -- is project an expertise                                                                                                                          
    """
    no = 1
    number = '0001'
    if is_expertise:
        prefix = 'eppn%s' % institute.name.replace(' ', '')[:4]
    else:
        prefix = 'p%s' % institute.name.replace(' ', '')[:4]

    found = True
    while found:
        try:
            project = Project.objects.get(pid=prefix+number)
            number = str(int(number) + 1)
            if len(number) == 1:
                number = '000' + number
            elif len(number) == 2:
                number = '00' + number
            elif len(number) == 3:
                number = '0' + number
        except:
            found = False

    return prefix+number

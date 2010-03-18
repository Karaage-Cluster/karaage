import datetime
from django.contrib.contenttypes.models import ContentType

def unique(seq):
    """Makes a list unique"""
    # Not order preserving
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()



def get_date_range(request, default_start=(datetime.date.today()-datetime.timedelta(days=90)), default_end=datetime.date.today()):

    today = datetime.date.today()

    if request.REQUEST.has_key('start'):
        try:
            years, months, days = request.GET['start'].split('-')
            start = datetime.datetime(int(years), int(months), int(days))
            start = start.date()
        except:
            start = today - datetime.timedelta(days=90)
    else:
        start = default_start

    if request.REQUEST.has_key('end'):
        try:
            years, months, days = request.GET['end'].split('-')
            end = datetime.datetime(int(years), int(months), int(days))
            end = end.date()
        except:
            end = today
    else:
        end = default_end

    return start, end




def log_object(user, object, flag, message):

    user.logentry_set.create(
        content_type = ContentType.objects.get_for_model(object.__class__),
        object_id=object._get_pk_val(),
        object_repr=object.__unicode__(),
        action_flag=flag,
        change_message=message
        )
    

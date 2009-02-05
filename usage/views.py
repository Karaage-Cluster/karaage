from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.conf import settings
from django.db.models import Q
from django.db import connection
from django.core.urlresolvers import reverse
from django.template.defaultfilters import dictsortreversed

import datetime

from karaage.util.helpers import get_available_time
from karaage.util.graphs import *
from karaage.people.models import Person, Institute
from karaage.projects.models import Project
from karaage.machines.models import UserAccount, Machine, MachineCategory
from karaage.pbsmoab.models import InstituteChunk
from karaage.usage.forms import UsageSearchForm
from karaage.cache.models import UserCache
from karaage.util import get_date_range
from karaage.graphs.util import get_colour

from models import CPUJob


def usage_index(request):
    
    mc_list = MachineCategory.objects.all()
    start, end = get_date_range(request)

    querystring = request.META['QUERY_STRING']

    return render_to_response('usage/mc_list.html', locals(), context_instance=RequestContext(request))



def index(request, machine_category_id=settings.DEFAULT_MC):

    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)
    mc_list = MachineCategory.objects.exclude(id__exact=settings.DEFAULT_MC)
    
    show_zeros = True
    if machine_category.id == settings.DEFAULT_MC:
        show_zeros = True

    institute_list = Institute.primary.all()
    total, total_jobs = 0, 0
    i_list = []
    m_list = []
    start, end = get_date_range(request)

    querystring = request.META['QUERY_STRING']

    available_time, avg_cpus = get_available_time(start, end, machine_category)
    
    for m in machine_category.machine_set.all():
        time, jobs = m.get_usage(start, end)
        if time is None:
            time = 0
        if jobs > 0:
            m_list.append({ 'machine': m, 'usage': time, 'jobs': jobs})
            
    for i in institute_list:
        time, jobs = i.get_usage(start, end, machine_category)
        if time is None:
            time = 0
    
        total = total + time
        total_jobs = total_jobs + jobs
        try:
            quota = InstituteChunk.objects.get(institute=i, machine_category=machine_category)
        except:
            continue
        if show_zeros or jobs > 0:
            i_list.append({ 'institute': i, 'usage': time, 'jobs': jobs, 'quota': quota.quota})
            
    for i in i_list:
        i['percent'] = (i['usage'] / available_time) * 100
        try:
            i['p_used'] = (i['percent'] / i['quota']) * 100
        except:
            i['p_used'] = 0
        i['diff'] = i['percent'] - i['quota']
        if i['diff'] <= 0:
            i['class'] = 'green'
        else:
            i['class'] = 'red'

    # Unused Entry
    unused = { 'usage': available_time - total, 'quota': 0 }
    unused['percent'] = (unused['usage'] / available_time) * 100
    unused['diff'] = unused['percent'] - unused['quota'] / 100
    if unused['diff'] <= 0:
        unused['class'] = 'green'
    else:
        unused['class'] = 'red'

    utilization = (total / available_time) * 100
        
    graph = get_institute_graph_url(start, end, machine_category)
    trend_graph = get_trend_graph_url(start, end, machine_category)
    
    return render_to_response('usage/usage_institue_list.html', locals(), context_instance=RequestContext(request))


def institute_usage(request, institute_id, machine_category_id=settings.DEFAULT_MC):

    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)
    institute = get_object_or_404(Institute, pk=institute_id)
    project_list = []
    start, end = get_date_range(request)
    institute_list = Institute.primary.all()

    available_usage, ave_cpus = get_available_time(start, end, machine_category)

    querystring = request.META['QUERY_STRING']

    quota = get_object_or_404(InstituteChunk, institute=institute, machine_category=machine_category)

    i_usage, i_jobs = institute.get_usage(start, end, machine_category)

    if i_jobs > 0:

        for p in institute.project_set.filter(machine_category=machine_category):
            p_usage, p_jobs = p.get_usage(start, end)
            chunk = p.projectchunk
            if p_jobs > 0:
                project_list.append(
                    {'project': p, 
                     'usage': p_usage, 
                     'jobs': p_jobs, 
                     'percent': ((chunk.get_mpots()/chunk.get_cap())*100), 
                     'quota_percent': (p_usage/(available_usage*quota.quota)*10000),
                     })


        user_list = []
        user_total, user_total_jobs = 0, 0
        if i_usage:
            for u in UserCache.objects.order_by('-cpu_hours').filter(start=start, end=end).filter(project__institute=institute).filter(project__machine_category=machine_category)[:5]:
                user_total += u.cpu_hours
                user_total_jobs += u.no_jobs
                user_list.append(
                    {'user': u.user, 
                     'project': u.project, 
                     'usage': u.cpu_hours, 
                     'jobs': u.no_jobs, 
                     'percent': ((u.cpu_hours/i_usage)*100),
                     'quota_percent': (u.cpu_hours/(available_usage*quota.quota)*10000),
                     }) 
                
            user_percent = (user_total / i_usage) * 100

        graph = get_institute_trend_graph_url(institute, start, end, machine_category)

    return render_to_response('usage/usage_institute_detail.html', locals(), context_instance=RequestContext(request))


def project_usage(request, project_id, institute_id=None, machine_category_id=settings.DEFAULT_MC):
    
    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)
    project = get_object_or_404(Project, pk=project_id)
    machine_category = project.machine_category
    usage_list = []
    total, total_jobs = 0, 0

    querystring = request.META['QUERY_STRING']
    start, end = get_date_range(request)
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    mc_ids = tuple([(int(m.id)) for m in machine_category.machine_set.all()])
    if len(mc_ids) == 1:
        mc_ids = "(%i)" % mc_ids[0]

    # Custom SQL as need to get users that were remove from project too
#    for u in project.users.all():
    cursor = connection.cursor()
    SQL = "SELECT user_id from cpu_job where project_id = '%s' and `machine_id` IN %s AND `date` >= '%s' AND `date` <= '%s' GROUP BY user_id" % (str(project.pid), mc_ids, start_str, end_str)
    cursor.execute(SQL)
    rows = list(cursor.fetchall())
    cursor.close()

    for uid in rows:
        u = UserAccount.objects.get(id=uid[0]).user
        time, jobs = u.get_usage(project, start, end)
        total += time
        total_jobs += jobs
        if jobs > 0:
            usage_list.append({ 'user': u, 'usage': time, 'jobs': jobs,})

    for u in usage_list:
        if total == 0:
            u['percent'] = 0
        else:
            u['percent'] = (u['usage'] / total) * 100
    
    usage_list = dictsortreversed(usage_list, 'usage')

    c = 0
    for i in usage_list:
        i['colour'] = get_colour(c)
        c += 1

    graph = get_project_trend_graph_url(project, start, end, machine_category)

    return render_to_response('usage/project_usage.html', locals(), context_instance=RequestContext(request))



def unknown_usage(request):

    project_list = Project.objects.all()
    user_list = Person.objects.all()

    if request.method == 'POST':

        try:
            project_s = Project.objects.get(pk=request.POST['project'])
        except:
            project_s = False
        try:
            person = Person.objects.get(pk=request.POST['user'])
        except:
           person = False
        
        jobs = CPUJob.objects.filter(id__in=request.POST.getlist('uid'))

        if project_s:
            for job in jobs:
                job.project = project_s
                job.save()

        if person:
            for job in jobs:
                machine_category = job.machine.category 
                ua = person.get_user_account(machine_category)
                if ua:
                    job.user = ua
                    job.save()
                
                
            
    project = Project.objects.get(pid='Unknown_Project')

    year_ago = datetime.date.today() - datetime.timedelta(days=365)
    usage_list = project.cpujob_set.filter(date__gte=year_ago)
        

    return render_to_response('usage/unknown_usage.html', locals(), context_instance=RequestContext(request))


def search(request):


    if request.method == 'POST':

        form = UsageSearchForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            project_list = Project.objects.all()
            institute_list = Institute.objects.all()
            #user_list = Person.objects.all()
            
            terms = data['terms'].lower()

            start = data['start_date']
            end = data['end_date']
            start_str = start.strftime('%Y-%m-%d')
            end_str = end.strftime('%Y-%m-%d')
            if terms:

            # search for projects
                query = Q()
                for term in terms.split(' '):
                    q = Q(pid__icontains=term) | Q(name__icontains=term)
                    query = query & q
        
                project_list = project_list.filter(query)
            
            # search for institutes
                query = Q()
                for term in terms.split(' '):
                    q = Q(name__icontains=term)
                    query = query & q
                institute_list = institute_list.filter(query)
    
                for p in project_list:
                    time, jobs = p.get_usage(start, end)
                    p = p.__dict__
                    p['time'] = time
                    p['jobs'] = jobs

                for i in institute_list:
                    time, jobs = i.get_usage(start, end)
                    i = i.__dict__
                    i['time'] = time
                    i['jobs'] = jobs

            else:
                return HttpResponseRedirect('%s?start=%s&end=%s' % (reverse('kg_usage_list'), start_str, end_str)) 

    else:

        form = UsageSearchForm()


    return render_to_response('usage/search.html', locals(), context_instance=RequestContext(request))
    

def project_search(request):

    if request.method == 'POST':

        form = UsageSearchForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            project = get_object_or_404(Project, pk=data['terms'])
            start = data['start_date'].strftime('%Y-%m-%d')
            end = data['end_date'].strftime('%Y-%m-%d')
            
            return HttpResponseRedirect('%s?start=%s&end=%s' % (project.get_usage_url(), start, end))    

    else:
        return HttpResponseRedirect(reverse('kg_admin_index'))

        

def top_users(request, machine_category_id=settings.DEFAULT_MC, count=20):

    machine_category = MachineCategory.objects.get(pk=machine_category_id)


    start, end = get_date_range(request)

    available_time, cpus = get_available_time(start, end, machine_category)

    user_list = []

    user_total, user_total_jobs = 0,0
    for u in UserCache.objects.order_by('-cpu_hours').filter(start=start, end=end).filter(project__machine_category=machine_category)[:count]:
        user_total += u.cpu_hours
        user_total_jobs += u.no_jobs
        user_list.append({'user': u.user, 'project': u.project, 'usage': u.cpu_hours, 'jobs': u.no_jobs, 'percent': ((u.cpu_hours/available_time)*100)}) 
        
    user_percent = (user_total / available_time) * 100
    
    querystring = request.META['QUERY_STRING']
    
    return render_to_response('usage/top_users.html', locals(), context_instance=RequestContext(request))



def institute_trends(request):

    start, end = get_date_range(request)
    graph_list = get_institutes_trend_graph_urls(start, end)
    
    return render_to_response('usage/institute_trends.html', locals(), context_instance=RequestContext(request))


def job_list(request, object_id, model):

    obj = get_object_or_404(model, pk=object_id)

    if model == Project:
        type = 'project'
    elif model == UserAccount:
        type = 'user'
    
    job_list = obj.cpujob_set.all()

    date_list = job_list.dates('date', 'year')

    return render_to_response('usage/job_list.html', locals(), context_instance=RequestContext(request))

        
def job_list_year(request, object_id, model, year):

    obj = get_object_or_404(model, pk=object_id)

    if model == Project:
        type = 'project'
    elif model == UserAccount:
        type = 'user'
    
    job_list = obj.cpujob_set.filter(date__year=year)

    date_list = job_list.dates('date', 'month')
     
    return render_to_response('usage/job_list_year.html', locals(), context_instance=RequestContext(request))

def job_list_month(request, object_id, model, year, month):

    obj = get_object_or_404(model, pk=object_id)

    if model == Project:
        type = 'project'
    elif model == UserAccount:
        type = 'user'
    
    job_list = obj.cpujob_set.filter(date__year=year)        
    job_list = job_list.filter(date__month=month)
    
    date_list = job_list.dates('date', 'day')

    return render_to_response('usage/job_list_month.html', locals(), context_instance=RequestContext(request))


def job_list_day(request, object_id, model, year, month, day):

    obj = get_object_or_404(model, pk=object_id)

    if model == Project:
        type = 'project'
    elif model == UserAccount:
        type = 'user'
    
    job_list = obj.cpujob_set.filter(date__year=year)    
    job_list = job_list.filter(date__month=month)
    job_list = job_list.filter(date__day=day)


    return render_to_response('usage/job_list_day.html', locals(), context_instance=RequestContext(request))


def institute_users(request, institute_id, machine_category_id=1):

    machine_category = MachineCategory.objects.get(pk=machine_category_id)
    institute = get_object_or_404(Institute, pk=institute_id)
    
    start, end = get_date_range(request)

    available_time, cpus = get_available_time(start, end, machine_category)

    user_list = []

    user_total, user_total_jobs = 0,0
    for u in UserCache.objects.order_by('-cpu_hours').filter(start=start, end=end).filter(project__machine_category=machine_category).filter(user__institute=institute).filter(no_jobs__gt=0):
        user_total = user_total + u.cpu_hours
        user_total_jobs = user_total_jobs + u.no_jobs
        user_list.append({'user': u.user, 'project': u.project, 'usage': u.cpu_hours, 'jobs': u.no_jobs, 'percent': ((u.cpu_hours/available_time)*100)}) 
        
    user_percent = (user_total / available_time) * 100
    
    querystring = request.META['QUERY_STRING']
    
    return render_to_response('usage/institute_users.html', locals(), context_instance=RequestContext(request))

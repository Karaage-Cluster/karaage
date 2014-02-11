# Copyright 2007-2013 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

import datetime
from decimal import Decimal
from celery.task import Task
import json

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.conf import settings
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.core.urlresolvers import reverse
from django.template.defaultfilters import dictsortreversed
from django.core.paginator import Paginator

from karaage.common.decorators import admin_required, login_required, usage_required
from karaage.common.filterspecs import Filter, FilterBar, DateFilter
from karaage.people.models import Person
from karaage.institutes.models import Institute, InstituteQuota
from karaage.projects.models import Project, ProjectQuota
from karaage.machines.models import Account, MachineCategory, Machine
from karaage.usage.models import CPUJob, Queue
from karaage.usage.forms import UsageSearchForm
import karaage.cache.models as cache
import karaage.cache.graphs as graphs
import karaage.cache.tasks as tasks
import karaage.cache.usage as usage
from karaage.common import get_date_range


def progress(request):
    if 'delete' in request.GET:
        cache.TaskMachineCategoryCache.objects.all().delete()
        cache.TaskCacheForMachineCategory.objects.all().delete()
        cache.MachineCategoryCache.objects.all().delete()
        cache.MachineCache.objects.all().delete()
        cache.InstituteCache.objects.all().delete()
        cache.PersonCache.objects.all().delete()
        cache.ProjectCache.objects.all().delete()
        return render_to_response(
                'main.html',
                {'content': 'Deleted'},
                context_instance=RequestContext(request))

    if request.method == 'POST':
        if 'task_id' in request.POST:
            result = Task.AsyncResult(request.POST['task_id'])
            if result.failed():
                value = {
                        'info': {},
                        'ready': result.ready(),
                }
            else:
                value = {
                        'info': result.info,
                        'ready': result.ready(),
                }
            return HttpResponse(json.dumps(value), content_type="application/json")
    return None


def gen_machine_category_cache(request, start, end):
    try:
        with transaction.atomic():
            tc = cache.TaskMachineCategoryCache.objects.create(date=datetime.date.today(), start=start, end=end,
                celery_task_id="")
            result = tasks.gen_machine_category_cache.delay(start, end)
            tc.celery_task_id = result.task_id
            tc.save()

    except IntegrityError:
        tc = cache.TaskMachineCategoryCache.objects.get(date=datetime.date.today(), start=start, end=end)
        if tc.ready:
            return None
        result = Task.AsyncResult(tc.celery_task_id)
        print result.state, result.info
        if result.failed():
            result.forget()
            tc.delete()
            return render_to_response(
                    'usage/failed.html',
                    context_instance=RequestContext(request))
        if result.ready():
            result.forget()
            tc.ready = True
            tc.save()
            return None

    return render_to_response(
            'usage/progress.html',
            { 'task_id': result.task_id },
            context_instance=RequestContext(request))


def gen_cache_for_machine_category(request, start, end, machine_category):
    try:
        with transaction.atomic():
            tc = cache.TaskCacheForMachineCategory.objects.create(date=datetime.date.today(), start=start, end=end,
                machine_category=machine_category,
                celery_task_id="")
            result = tasks.gen_cache_for_machine_category.delay(start, end, machine_category)
            tc.celery_task_id = result.task_id
            tc.save()

    except IntegrityError:
        tc = cache.TaskCacheForMachineCategory.objects.get(date=datetime.date.today(), start=start, end=end,
                machine_category=machine_category)
        if tc.ready:
            return None
        result = Task.AsyncResult(tc.celery_task_id)
        if result.failed():
            result.forget()
            tc.delete()
            return render_to_response(
                    'usage/failed.html',
                    context_instance=RequestContext(request))
        if result.ready():
            result.forget()
            tc.ready = True
            tc.save()
            return None

    return render_to_response(
            'usage/progress.html',
            { 'task_id': result.task_id },
            context_instance=RequestContext(request))


def gen_cache_for_project(request, start, end, project, machine_category):
    try:
        with transaction.atomic():
            tc = cache.TaskCacheForProject.objects.create(date=datetime.date.today(), start=start, end=end,
                project=project, machine_category=machine_category,
                celery_task_id="")
            result = tasks.gen_cache_for_project.delay(start, end, project, machine_category)
            tc.celery_task_id = result.task_id
            tc.save()

    except IntegrityError:
        tc = cache.TaskCacheForProject.objects.get(date=datetime.date.today(), start=start, end=end,
                project=project, machine_category=machine_category)
        if tc.ready:
            return None
        result = Task.AsyncResult(tc.celery_task_id)
        if result.failed():
            result.forget()
            tc.delete()
            return render_to_response(
                    'usage/failed.html',
                    context_instance=RequestContext(request))
        if result.ready():
            result.forget()
            tc.ready = True
            tc.save()
            return None

    return render_to_response(
            'usage/progress.html',
            { 'task_id': result.task_id },
            context_instance=RequestContext(request))


def gen_cache_for_institute(request, start, end, institute, machine_category):
    try:
        with transaction.atomic():
            tc = cache.TaskCacheForInstitute.objects.create(date=datetime.date.today(), start=start, end=end,
                institute=institute, machine_category=machine_category,
                celery_task_id="")
            result = tasks.gen_cache_for_institute.delay(start, end, institute, machine_category)
            tc.celery_task_id = result.task_id
            tc.save()

    except IntegrityError:
        tc = cache.TaskCacheForInstitute.objects.get(date=datetime.date.today(), start=start, end=end,
                institute=institute, machine_category=machine_category)
        if tc.ready:
            return None
        result = Task.AsyncResult(tc.celery_task_id)
        if result.failed():
            result.forget()
            tc.delete()
            return render_to_response(
                    'usage/failed.html',
                    context_instance=RequestContext(request))
        if result.ready():
            result.forget()
            tc.ready = True
            tc.save()
            return None

    return render_to_response(
            'usage/progress.html',
            { 'task_id': result.task_id },
            context_instance=RequestContext(request))


def usage_index(request):
    if not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    result = progress(request)
    if result is not None:
        return result

    start, end = get_date_range(request)

    result = gen_machine_category_cache(request, start, end)
    if result is not None:
        return result

    mc_list = []
    for machine_category in MachineCategory.objects.all():
        mc_list.append({
            'obj': machine_category,
            'graph': graphs.get_machine_graph_url(start, end, machine_category),
        })

    return render_to_response('usage/mc_list.html', locals(), context_instance=RequestContext(request))


@usage_required
def index(request, machine_category_id):
    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)
    mc_list = MachineCategory.objects.exclude(id__exact=machine_category_id)

    result = progress(request)
    if result is not None:
        return result

    start, end = get_date_range(request)

    result = gen_cache_for_machine_category(request, start, end, machine_category)
    if result is not None:
        return result

    show_zeros = True

    institute_list = Institute.active.all()
    i_list = []
    m_list = []

    mc_cache = usage.get_machine_category_usage(machine_category, start, end)
    total = mc_cache.cpu_time
    total_jobs = mc_cache.no_jobs
    available_time = mc_cache.available_time
    avg_cpus = available_time / (60*24*24) / ((end-start).days + 1)

    for m_cache in cache.MachineCache.objects.filter(machine__category=machine_category,
            date=datetime.date.today(), start=start, end=end):
        m = m_cache.machine
        time = m_cache.cpu_time
        jobs = m_cache.no_jobs
        m_list.append({'machine': m, 'usage': time, 'jobs': jobs})

    for i_cache in cache.InstituteCache.objects.filter(machine_category=machine_category,
            date=datetime.date.today(), start=start, end=end):
        i = i_cache.institute
        time = i_cache.cpu_time
        jobs = i_cache.no_jobs

        try:
            quota = InstituteQuota.objects.get(institute=i, machine_category=machine_category)
            display_quota = quota.quota
        except InstituteQuota.DoesNotExist:
            display_quota = None

        if display_quota is None and time==0 and jobs==0:
            continue

        data_row = {'institute': i, 'usage': time, 'jobs': jobs, 'quota': display_quota}
        if available_time != 0:
            data_row['percent'] = Decimal(time) / Decimal(available_time) * 100
        else:
            data_row['percent'] = 0
        if data_row['quota'] is not None:
            if data_row['quota'] != 0:
                data_row['p_used'] = (data_row['percent'] / data_row['quota']) * 100
            else:
                data_row['p_used'] = None
            data_row['diff'] = data_row['percent'] - data_row['quota']
            if data_row['diff'] <= 0:
                data_row['class'] = 'green'
            else:
                data_row['class'] = 'red'
        else:
            data_row['class'] = 'green'
            data_row['diff'] = None
            data_row['p_used'] = None

        i_list.append(data_row)

    # Unused Entry
    unused = {'usage': available_time - total, 'quota': 0}
    try:
        unused['percent'] = (unused['usage'] / available_time) * 100
    except ZeroDivisionError:
        unused['percent'] = 0
    unused['diff'] = unused['percent'] - unused['quota'] / 100
    if unused['diff'] <= 0:
        unused['class'] = 'green'
    else:
        unused['class'] = 'red'

    if available_time != 0:
        utilization = (Decimal(total) / available_time) * 100
    else:
        utilization = 0

    institutes_graph = graphs.get_institute_graph_url(start, end, machine_category)
    machines_graph = graphs.get_machine_graph_url(start, end, machine_category)
    trend_graph = graphs.get_trend_graph_url(start, end, machine_category)

    return render_to_response('usage/usage_institute_list.html', locals(), context_instance=RequestContext(request))


@usage_required
def institute_usage(request, institute_id, machine_category_id):
    result = progress(request)
    if result is not None:
        return result

    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)
    institute = get_object_or_404(Institute, pk=institute_id)
    start, end = get_date_range(request)

    result = gen_cache_for_machine_category(request, start, end, machine_category)
    if result is not None:
        return result

    result = gen_cache_for_institute(request, start, end, institute, machine_category)
    if result is not None:
        return result

    project_list = []
    institute_list = Institute.active.all()

    if not institute.can_view(request.user) and not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    mc_cache = usage.get_machine_category_usage(machine_category, start, end)
    available_time = mc_cache.available_time

    quota = get_object_or_404(InstituteQuota, institute=institute, machine_category=machine_category)

    i_usage, i_jobs = usage.get_institute_usage(institute, start, end, machine_category)

    for p_cache in cache.ProjectCache.objects.filter(project__institute=institute,
            machine_category=machine_category,
            date=datetime.date.today(), start=start, end=end):
        p = p_cache.project
        p_usage = p_cache.cpu_time
        p_jobs = p_cache.no_jobs

        try:
            chunk = p.projectquota_set.get(machine_category=machine_category)
        except ProjectQuota.DoesNotExist:
            chunk = None

        if chunk is None and p_usage==0 and p_jobs==0:
            continue

        if chunk is not None:
            mpots = mc_cache.get_project_mpots(chunk, start, end)
            percent = mc_cache.get_project_cap_percent(chunk, start, end)
        else:
            mpots = None
            percent = None
        if available_time > 0 and quota.quota > 0:
            quota_percent = p_usage / (available_time * quota.quota) * 10000
        else:
            quota_percent = 0
        project_list.append(
            {'project': p,
             'usage': p_usage,
             'jobs': p_jobs,
             'percent': percent,
             'quota_percent': quota_percent,
             })

    person_list = []
    person_total, person_total_jobs = 0, 0
    for u in cache.PersonCache.objects.order_by('-cpu_time').filter(project__institute=institute,
            machine_category=machine_category,
            date=datetime.date.today(), start=start, end=end)[:5]:
        person_total += u.cpu_time
        person_total_jobs += u.no_jobs
        if i_usage > 0:
            i_percent = (u.cpu_time / i_usage) * 100
        else:
            i_percent = None
        if available_time > 0 and quota.quota > 0:
            quota_percent = u.cpu_time / (available_time * quota.quota) * 10000
        else:
            quota_percent = 0
        person_list.append(
            {'person': u.person,
             'project': u.project,
             'usage': u.cpu_time,
             'jobs': u.no_jobs,
             'percent': i_percent,
             'quota_percent': quota_percent,
             })

    if i_usage > 0:
        person_percent = (person_total / i_usage) * 100
    else:
        person_percent = None

    graph = graphs.get_institute_trend_graph_url(institute, start, end, machine_category)

    return render_to_response('usage/usage_institute_detail.html', locals(), context_instance=RequestContext(request))


@usage_required
def project_usage(request, project_id, machine_category_id):
    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)
    project = get_object_or_404(Project, pid=project_id)
    if not project.can_view(request.user) and not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    result = progress(request)
    if result is not None:
        return result

    start, end = get_date_range(request)

    result = gen_cache_for_machine_category(request, start, end, machine_category)
    if result is not None:
        return result

    result = gen_cache_for_project(request, start, end, project, machine_category)
    if result is not None:
        return result

    usage_list = []
    total, total_jobs = 0, 0

    # Custom SQL as need to get users that were removed from project too
    rows = CPUJob.objects.filter(
            project=project,
            machine__category=machine_category,
            date__range=(start, end)
            ).values('account').annotate().order_by('account')

    for row in rows:
        u = Account.objects.get(id=row['account']).person
        time, jobs = usage.get_person_usage(u, project, start, end, machine_category)
        if time:
            total += time
            total_jobs += jobs
            if jobs > 0:
                usage_list.append({'person': u, 'usage': time, 'jobs': jobs})

    for u in usage_list:
        if total == 0:
            u['percent'] = 0
        else:
            u['percent'] = (u['usage'] / total) * 100

    usage_list = dictsortreversed(usage_list, 'usage')

    count = 0
    for i in usage_list:
        i['colour'] = graphs.get_colour(count)
        count += 1

    graph = graphs.get_project_trend_graph_url(project, start, end, machine_category)

    return render_to_response('usage/project_usage.html', locals(), context_instance=RequestContext(request))


@admin_required
def unknown_usage(request):
    if not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    showall = request.REQUEST.get('showall', False)
    project_list = Project.objects.all()
    person_list = Person.objects.all()

    if request.method == 'POST':

        try:
            project_s = Project.objects.get(pid=request.POST['project'])
        except Project.DoesNotExist:
            project_s = False
        try:
            person = Person.objects.get(pk=request.POST['person'])
        except Person.DoesNotExist:
            person = False
        
        if request.POST.getlist('uid'):
            jobs = CPUJob.objects.filter(id__in=request.POST.getlist('uid'))
        else:
            jobs = []
        if project_s:
            for job in jobs:
                job.project = project_s
                job.save()

        if person:
            for job in jobs:
                machine_category = job.machine.category
                ua = person.get_account(machine_category)
                if ua:
                    job.account = ua
                    job.save()
    usage_list = CPUJob.objects.filter(Q(project__isnull=True) | Q(account__isnull=True))

    if not showall:
        year_ago = datetime.date.today() - datetime.timedelta(days=365)
        usage_list = usage_list.filter(date__gte=year_ago)

    return render_to_response('usage/unknown_usage.html', locals(), context_instance=RequestContext(request))


@usage_required
def search(request):
    if not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    if request.method == 'POST':

        form = UsageSearchForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            project_query = Project.objects.all()
            institute_query = Institute.objects.all()
            #person_list = Person.objects.all()
            
            terms = data['terms'].lower()

            start = data['start_date']
            end = data['end_date']
            machine_category = data['machine_category']
            start_str = start.strftime('%Y-%m-%d')
            end_str = end.strftime('%Y-%m-%d')
            if terms:

            # search for projects
                query = Q()
                for term in terms.split(' '):
                    q = Q(pid__icontains=term) | Q(name__icontains=term)
                    query = query & q
        
                project_query = project_query.filter(query)
            
            # search for institutes
                query = Q()
                for term in terms.split(' '):
                    q = Q(name__icontains=term)
                    query = query & q
                institute_query = institute_query.filter(query)
    
                project_list = []
                for p in project_query:
                    time, jobs = usage.get_project_usage(p, start, end, machine_category)
                    project_list.append({
                        'obj': p,
                        'time': time,
                        'jobs': jobs,
                    })
                del project_query

                institute_list = []
                for i in institute_query:
                    time, jobs = usage.get_institute_usage(i, start, end, machine_category)
                    institute_list.append({
                        'obj': i,
                        'time': time,
                        'jobs': jobs,
                    })
                del institute_query

            else:
                return HttpResponseRedirect('%s?start=%s&end=%s' % (reverse('kg_usage_list'), start_str, end_str))
    else:
        start, end = get_date_range(request)
        initial = {
            'start_date': start,
            'end_date': end,
            'machine_category': request.GET.get('machine_category', None)
        }
        form = UsageSearchForm(initial=initial)

    return render_to_response('usage/search.html', locals(), context_instance=RequestContext(request))


@usage_required
def top_users(request, machine_category_id, count=20):
    if not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    result = progress(request)
    if result is not None:
        return result

    machine_category = MachineCategory.objects.get(pk=machine_category_id)
    start, end = get_date_range(request)

    result = gen_cache_for_machine_category(request, start, end, machine_category)
    if result is not None:
        return result

    start, end = get_date_range(request)
    mc_cache = usage.get_machine_category_usage(machine_category, start, end)
    available_time = mc_cache.available_time
    person_list = []

    person_total, person_total_jobs = 0, 0
    for u in cache.PersonCache.objects.order_by('-cpu_time').filter(start=start, end=end).filter(
            machine_category=machine_category)[:count]:
        if u.cpu_time:
            person_total += u.cpu_time
            person_total_jobs += u.no_jobs
            person_list.append({
                'person': u.person,
                'project': u.project,
                'usage': u.cpu_time,
                'jobs': u.no_jobs,
                'percent': ((u.cpu_time / available_time) * 100)
            })

    person_percent = (person_total / available_time) * 100

    return render_to_response('usage/top_users.html', locals(), context_instance=RequestContext(request))


@usage_required
def institute_trends(request, machine_category_id):
    if not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    result = progress(request)
    if result is not None:
        return result

    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)
    start, end = get_date_range(request)

    result = gen_cache_for_machine_category(request, start, end, machine_category)
    if result is not None:
        return result

    graph_list = graphs.get_institutes_trend_graph_urls(start, end, machine_category)

    return render_to_response('usage/institute_trends.html', locals(), context_instance=RequestContext(request))


@usage_required
def institute_users(request, machine_category_id, institute_id):
    if not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    result = progress(request)
    if result is not None:
        return result

    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)
    start, end = get_date_range(request)

    result = gen_cache_for_machine_category(request, start, end, machine_category)
    if result is not None:
        return result

    institute = get_object_or_404(Institute, pk=institute_id)

    if not institute.can_view(request.user) and not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    start, end = get_date_range(request)

    mc_cache = usage.get_machine_category_usage(machine_category, start, end)
    available_time = mc_cache.available_time

    person_list = []

    person_total, person_total_jobs = 0, 0
    for u in cache.PersonCache.objects.order_by('-cpu_time').filter(start=start, end=end).filter(
            machine_category=machine_category).filter(person__institute=institute).filter(no_jobs__gt=0):
        person_total = person_total + u.cpu_time
        person_total_jobs = person_total_jobs + u.no_jobs
        person_list.append({'person': u.person, 'project': u.project, 'usage': u.cpu_time, 'jobs': u.no_jobs, 'percent': ((u.cpu_time / available_time) * 100)})

    if available_time != 0:
        person_percent = (person_total / available_time) * 100
    else:
        person_percent = 0

    return render_to_response('usage/institute_users.html', locals(), context_instance=RequestContext(request))


@usage_required
def core_report(request, machine_category_id):
    if not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)

    start, end = get_date_range(request)

    job_list = CPUJob.objects.filter(date__gte=start, date__lte=end, machine__category=machine_category)
    core_1 = job_list.filter(cores=1).count()
    core_2_4 = job_list.filter(cores__gte=2, cores__lte=4).count()
    core_5_8 = job_list.filter(cores__gte=5, cores__lte=8).count()
    core_9_16 = job_list.filter(cores__gte=9, cores__lte=16).count()
    core_17_32 = job_list.filter(cores__gte=17, cores__lte=32).count()
    core_33_64 = job_list.filter(cores__gte=33, cores__lte=64).count()
    core_65_128 = job_list.filter(cores__gte=65, cores__lte=128).count()
    core_128 = job_list.filter(cores__gte=128).count()
    data = [core_1, core_2_4, core_5_8, core_9_16, core_17_32, core_33_64, core_65_128, core_128]
    total = sum(data)

#    x_labels = ['1', '2-4', '5-8', '9-16', '17-32', '33-64', '65-128', '128+']
#    max_y = max(data)
#    data = {'Total jobs': data}
#    g = GraphGenerator()
#    graph = g.bar_chart(data, x_labels, max_y, bar_width=50).get_url()

    return render_to_response('usage/core_report.html', locals(), context_instance=RequestContext(request))


@usage_required
def mem_report(request, machine_category_id):

    machine_category = get_object_or_404(MachineCategory, pk=machine_category_id)
    
    start, end = get_date_range(request)

    job_list = CPUJob.objects.filter(date__gte=start, date__lte=end, machine__category=machine_category)
    mem_0_4 = job_list.filter(mem__lte=4 * 1024 * 1024).count()
    mem_4_8 = job_list.filter(mem__gt=4 * 1024 * 1024, mem__lte=8 * 1024 * 1024).count()
    mem_8_16 = job_list.filter(mem__gt=8 * 1024 * 1024, mem__lte=16 * 1024 * 1024).count()
    mem_16_32 = job_list.filter(mem__gt=16 * 1024 * 1024, mem__lte=32 * 1024 * 1024).count()
    mem_32_64 = job_list.filter(mem__gt=32 * 1024 * 1024, mem__lte=64 * 1024 * 1024).count()
    mem_64_128 = job_list.filter(mem__gt=64 * 1024 * 1024, mem__lte=128 * 1024 * 1024).count()
    mem_128 = job_list.filter(mem__gt=128 * 1024 * 1024).count()
    data = [mem_0_4, mem_4_8, mem_8_16, mem_16_32, mem_32_64, mem_64_128, mem_128]
    total = sum(data)

#    x_labels = ['0-4', '4-8', '8-16', '16-32', '32-64', '64-128', '128+']
#    labels = []
#    max_y = max(data)
#    data = {'Total jobs': data}
#    g = GraphGenerator()
#    graph = g.bar_chart(data, x_labels, max_y, bar_width=50).get_url()

    return render_to_response('usage/mem_report.html', locals(), context_instance=RequestContext(request))


@usage_required
def job_detail(request, jobid):
    if not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    job = get_object_or_404(CPUJob, jobid=jobid)

    if not job.project.can_view(request.user) and not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    return render_to_response('usage/job_detail.html', {'job': job}, context_instance=RequestContext(request))


@usage_required
def job_list(request):
    if not getattr(settings, 'USAGE_IS_PUBLIC', False):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    page_no = int(request.GET.get('page', 1))

    job_list = CPUJob.objects.select_related()
    
    if 'machine' in request.REQUEST:
        job_list = job_list.filter(machine__id=int(request.GET['machine']))

    if 'queue' in request.REQUEST:
        job_list = job_list.filter(queue=request.GET['queue'])

    if 'software' in request.REQUEST:
        job_list = job_list.filter(software__software__id=int(request.GET['software']))

    if 'account' in request.REQUEST:
        job_list = job_list.filter(account__person__username=request.GET['account'])

    if 'project' in request.REQUEST:
        job_list = job_list.filter(project__pid=request.GET['project'])
   
    params = dict(request.GET.items())
    m_params = dict([(str(k), str(v)) for k, v in params.items() if k.startswith('date__')])
    job_list = job_list.filter(**m_params)

    if 'search' in request.REQUEST:
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(jobid=term)
            q = q | Q(account__person__username__icontains=term)
            q = q | Q(project__pid__icontains=term)
            query = query & q
        
        job_list = job_list.filter(query)
    else:
        terms = ""

    filter_list = []
    filter_list.append(DateFilter(request, 'date'))
    filter_list.append(Filter(request, 'machine', Machine.objects.all()))
    filter_list.append(Filter(request, 'queue', Queue.objects.all()))
    filter_bar = FilterBar(request, filter_list)

    p = Paginator(job_list, 50)
    page = p.page(page_no)
    
    return render_to_response(
            'usage/job_list.html',
            {'page': page, 'filter_bar': filter_bar, 'terms': terms},
            context_instance=RequestContext(request))

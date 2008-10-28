from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from django.db.models import Q
from django.core.paginator import QuerySetPaginator
from django_common.util.filterspecs import Filter, FilterBar

from karaage.people.models import Person, Institute
from karaage.requests.models import ProjectRequest
from karaage.projects.models import Project
from karaage.projects.forms import ProjectForm
from karaage.util.email_messages import send_removed_from_project_email
from karaage.util import log_object as log
from karaage.usage.forms import UsageSearchForm


@login_required
def add_edit_project(request, project_id=None):

    if project_id is None:
        project = False
    else:
        project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        
        if form.is_valid():
            
            if project:
                form.save(project)
                request.user.message_set.create(message="Project '%s' edited succesfully" % project)
            else:
                project = form.save()
                request.user.message_set.create(message="Project '%s' added succesfully" % project)
            return HttpResponseRedirect(project.get_absolute_url())        
    else:        
        form = ProjectForm()
        
        if project:
            form.initial = project.__dict__
            form.initial['machine_category'] = form.initial['machine_category_id']
            form.initial['leader'] = form.initial['leader_id']
            form.initial['institute'] = form.initial['institute_id']
            
    return render_to_response('projects/project_form.html', locals(), context_instance=RequestContext(request))

add_edit_project = permission_required('main.add_project')(add_edit_project)

@login_required
def delete_project(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        
        project.deactivate()
        log(request.user, project, 3, 'Deleted')
        request.user.message_set.create(message="Project '%s' deleted succesfully" % project)
        return HttpResponseRedirect(project.get_absolute_url()) 

    return render_to_response('projects/project_confirm_delete.html', locals(), context_instance=RequestContext(request))

delete_project = permission_required('main.delete_project')(delete_project)
    
@login_required
def project_detail(request, project_id):

    project = get_object_or_404(Project, pk=project_id)
    user_list = Person.active.all()

    if request.REQUEST.has_key('showall'):
        showall = True

    form = UsageSearchForm()
    
    if request.method == 'POST':
        # Post means adding a user to this project
        if not request.user.has_perm('main.change_project'):
            return HttpResponseForbidden('<h1>Access Denied</h1>')
        
        data = request.POST.copy()     
        person = Person.objects.get(pk=data['person'])

        if person.has_account(project.machine_category):
            project.users.add(person)
            request.user.message_set.create(message="User '%s' added succesfully" % person)
            log(request.user, project, 1, 'Added user %s' % person)
        else:
            no_account_error = "%s has no account on %s. Please create one first" % (person, project.machine_category)
    
    return render_to_response('projects/project_detail.html', locals(), context_instance=RequestContext(request))

@login_required
def project_list(request, queryset=Project.objects.all()):

    project_list = queryset

    page_no = int(request.GET.get('page', 1))

    if request.REQUEST.has_key('institute'):
        project_list = project_list.filter(institute=int(request.GET['institute']))

    if request.REQUEST.has_key('status'):
        project_list = project_list.filter(is_active=int(request.GET['status']))

    if request.method == 'POST':
        new_data = request.POST.copy()
        terms = new_data['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(pid__icontains=term) | Q(name__icontains=term) | Q(description__icontains=term) | Q(leader__user__first_name__icontains=term) | Q(leader__user__last_name__icontains=term) | Q(institute__name__icontains=term)
            query = query & q
        
        project_list = project_list.filter(query)
    else:
        terms = ""


    filter_list = []
    filter_list.append(Filter(request, 'status', {1: 'Active', 0: 'Deleted'}))
    filter_list.append(Filter(request, 'institute', Institute.primary.all()))
    filter_bar = FilterBar(request, filter_list)

    p = QuerySetPaginator(project_list, 50)
    page = p.page(page_no)

    return render_to_response('projects/project_list.html', locals(), context_instance=RequestContext(request))


@login_required
def remove_user(request, project_id, username):
    site = Site.objects.get_current()

    project = get_object_or_404(Project, pk=project_id)
    user = get_object_or_404(Person, user__username=username)

    if site.id == 2:
        if not request.user.get_profile() == project.leader:
            return HttpResponseForbidden('<h1>Access Denied</h1>')

    project.users.remove(user)
    request.user.message_set.create(message="User '%s' removed succesfully from project %s" % (user, project.pid))
    
    log(request.user, project, 3, 'Removed %s from project' % user)
    log(request.user, user, 3, 'Removed from project %s' % project)

   # send_removed_from_project_email(user, project)
    
    if site.id == 2:
        return HttpResponseRedirect(project.get_absolute_url())
    return HttpResponseRedirect(user.get_absolute_url())

@login_required
def no_users(request):

    project_ids = []
    for p in Project.active.all():
        if p.users.count() == 0:
            project_ids.append(p.pid)

    return project_list(request, Project.objects.filter(pid__in=project_ids))


@login_required
def over_quota(request):

    project_ids = []

    for p in Project.active.all():
        if p.is_over_quota():
            project_ids.append(p.pid)

    return project_list(request, Project.objects.filter(pid__in=project_ids))


def project_logs(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    log_list = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(project.__class__),
        object_id=project_id
    )

    short = True
    return render_to_response('log_list.html', locals(), context_instance=RequestContext(request))


@login_required       
def pending_requests(request):
    request_list = ProjectRequest.objects.all()

    return render_to_response('projects/pending_requests.html', locals(), context_instance=RequestContext(request))

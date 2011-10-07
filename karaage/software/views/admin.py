# Copyright 2007-2010 VPAC
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

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count, Sum

import datetime
from andsome.util.filterspecs import Filter, FilterBar, DateFilter

from karaage.software.models import SoftwareCategory, SoftwarePackage, SoftwareVersion, SoftwareLicense, SoftwareAccessRequest, SoftwareLicenseAgreement
from karaage.software.forms import AddPackageForm, LicenseForm, SoftwareVersionForm
from karaage.people.models import Person
from karaage.machines.models import Machine
from karaage.usage.models import CPUJob
from karaage.util import get_date_range, log_object as log
from karaage.util.email_messages import send_software_request_approved_email


def software_list(request):
    software_list = SoftwarePackage.objects.all()
    page_no = int(request.GET.get('page', 1))

    if request.REQUEST.has_key('category'):
        software_list = software_list.filter(category=int(request.GET['category']))
    if request.REQUEST.has_key('machine'):
        software_list = software_list.filter(softwareversion__machines=int(request.GET['machine']))

    params = dict(request.GET.items())
    m_params = dict([(str(k), str(v)) for k, v in params.items() if k.startswith('softwareversion__last_used_')])
    software_list = software_list.filter(**m_params)
        
    if request.REQUEST.has_key('search'):
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(name__icontains=term) | Q(description__icontains=term) | Q(gid__icontains=term) | Q(homepage__icontains=term) 
            query = query & q
        
        software_list = software_list.filter(query)
    else:
        terms = ""

    filter_list = []
    filter_list.append(Filter(request, 'category', SoftwareCategory.objects.all()))
    filter_bar = FilterBar(request, filter_list)
    filter_list.append(Filter(request, 'machine', Machine.objects.all()))
    filter_list.append(DateFilter(request, 'softwareversion__last_used'))
    
    p = Paginator(software_list, 50)
    page = p.page(page_no)

    return render_to_response('software/software_list.html', locals(), context_instance=RequestContext(request))


def software_detail(request, package_id):
    package = get_object_or_404(SoftwarePackage, pk=package_id)

    members = package.get_group_members()
    non_ids = []
    member_list = []
    if members:
        for member in members:
            try:
                person = Person.objects.get(user__username=member.uid)
                non_ids.append(person.id)
            except Person.DoesNotExist:
                person = None
            
            member_list.append({
                'username': member.uid,
                'person': person,
                })

    not_member_list = Person.objects.select_related().exclude(id__in=non_ids)

    if request.method == 'POST' and 'member-add' in request.POST:
        person = get_object_or_404(Person, pk=request.POST['member'])
        from karaage.datastores.software import add_member
        add_member(package, person)

        messages.success(request, "User %s added to group" % person)
        log(request.user, package, 1, "User %s added to group manually" % person)
        return HttpResponseRedirect(package.get_absolute_url())

    return render_to_response('software/software_detail.html', locals(), context_instance=RequestContext(request))


@permission_required('software.add_softwarepackage')
def add_package(request):

    if request.method == 'POST':
        form = AddPackageForm(request.POST)

        if form.is_valid():
            package = form.save()
            log(request.user, package, 1, "Added")
            return HttpResponseRedirect(package.get_absolute_url())
    else:
        form = AddPackageForm()
        
    return render_to_response('software/add_package_form.html', locals(), context_instance=RequestContext(request))


@login_required
def license_detail(request, license_id):
    l = get_object_or_404(SoftwareLicense, pk=license_id)
    return render_to_response('software/license_detail.html', locals(), context_instance=RequestContext(request))


@permission_required('software.delete_softwarelicense')
def add_edit_license(request, package_id, license_id=None):

    package = get_object_or_404(SoftwarePackage, pk=package_id)
    
    if license_id is None:
        l = None
    else:
        l = get_object_or_404(SoftwareLicense, pk=license_id)
    
    if request.method == 'POST':
        form = LicenseForm(request.POST, instance=l)
        if form.is_valid():
            l = form.save()
            if license_id is None:
                log(request.user, package, 1, "license: %s added" % l)
            package.save()
            return HttpResponseRedirect(package.get_absolute_url())
    else:
        form = LicenseForm(instance=l)
        
    return render_to_response('software/license_form.html', locals(), context_instance=RequestContext(request))


@permission_required('software.delete_softwareversion')
def delete_version(request, package_id, version_id):
    
    version = get_object_or_404(SoftwareVersion, pk=version_id)
    
    if request.method == 'POST':
        version.delete()
        log(request.user, version.package, 3, 'Deleted version: %s' % version)
        
        messages.success(request, "Version '%s' was deleted succesfully" % version)
        return HttpResponseRedirect(version.get_absolute_url())
    
    return render_to_response('software/version_confirm_delete.html', locals(), context_instance=RequestContext(request))


@permission_required('software.change_softwareversion')
def add_edit_version(request, package_id, version_id=None):

    package = get_object_or_404(SoftwarePackage, pk=package_id)
    
    if version_id is None:
        version = None
    else:
        version = get_object_or_404(SoftwareVersion, pk=version_id)

    if request.method == 'POST':
        form = SoftwareVersionForm(request.POST, instance=version)
        if form.is_valid():
            version = form.save()
            return HttpResponseRedirect(package.get_absolute_url())
    else:
        form = SoftwareVersionForm(instance=version)
        
    return render_to_response('software/version_form.html', locals(), context_instance=RequestContext(request))


def category_list(request):
    category_list = SoftwareCategory.objects.all()   
    return render_to_response('software/category_list.html', locals(), context_instance=RequestContext(request))
    

@permission_required('software.change_softwarepackage')
def remove_member(request, package_id, user_id):

    package = get_object_or_404(SoftwarePackage, pk=package_id)
    person = get_object_or_404(Person, pk=user_id)

    from karaage.datastores.software import remove_member as ds_remove_member
    ds_remove_member(package, person)

    log(request.user, package, 3, 'Removed %s from group' % person)
    log(request.user, person, 3, 'Removed from software group %s' % package)
        
    messages.success(request, "User '%s' removed successfuly" % person)

    return HttpResponseRedirect(package.get_absolute_url())


@permission_required('software.change_softwareaccessrequest')
def softwarerequest_list(request):
    page_no = int(request.GET.get('page', 1))
    softwarerequest_list = SoftwareAccessRequest.objects.all()  
    p = Paginator(softwarerequest_list, 50)
    page = p.page(page_no)
    return render_to_response('software/request_list.html', {'softwarerequest_list': softwarerequest_list, 'page': page,}, context_instance=RequestContext(request))
    

@permission_required('software.change_softwareaccessrequest')
def softwarerequest_approve(request, softwarerequest_id):
    softwarerequest = get_object_or_404(SoftwareAccessRequest, pk=softwarerequest_id)

    if request.method == 'POST':
        
        SoftwareLicenseAgreement.objects.create(
            user=softwarerequest.person,
            license=softwarerequest.software_license,
            date=datetime.datetime.today(),
            )
        from karaage.datastores.software import add_member
        add_member(softwarerequest.software_license.package, softwarerequest.person)

        messages.success(request, "Software request approved successfully")
        send_software_request_approved_email(softwarerequest)
        log(request.user, softwarerequest.software_license.package, 1, "User %s approved" % softwarerequest.person)
        softwarerequest.delete()
        return HttpResponseRedirect(reverse('kg_softwarerequest_list'))

    return render_to_response('software/request_approve.html', {'softwarerequest': softwarerequest,}, context_instance=RequestContext(request))


@permission_required('software.change_softwareaccessrequest')
def softwarerequest_delete(request, softwarerequest_id):
    softwarerequest = get_object_or_404(SoftwareAccessRequest, pk=softwarerequest_id)
    
    if request.method == 'POST':
        
        softwarerequest.delete()
        messages.success(request, "Software request deleted successfully")
        return HttpResponseRedirect(reverse('kg_softwarerequest_list'))

    return render_to_response('software/request_delete.html', {'softwarerequest': softwarerequest,}, context_instance=RequestContext(request))


def software_stats(request, package_id):
    package = get_object_or_404(SoftwarePackage, pk=package_id)
    start, end = get_date_range(request)
    querystring = request.META.get('QUERY_STRING', '')
    if package.softwareversion_set.count() == 1:
        return HttpResponseRedirect(reverse('kg_softwareversion_stats', args=[package.id, package.softwareversion_set.all()[0].id]))
    version_stats = SoftwareVersion.objects.filter(package=package, cpujob__date__range=(start, end)).annotate(jobs=Count('cpujob'), usage=Sum('cpujob__cpu_usage')).filter(usage__isnull=False)
    version_totaljobs = version_stats.aggregate(Sum('jobs'))['jobs__sum']
    #version_totalusage = version_stats.aggregate(Sum('usage'))
    person_stats = Person.objects.filter(useraccount__cpujob__software__package=package, useraccount__cpujob__date__range=(start, end)).annotate(jobs=Count('useraccount__cpujob'), usage=Sum('useraccount__cpujob__cpu_usage'))

    context = {
        'package': package,
        'version_stats': version_stats,
        'version_totaljobs': version_totaljobs,
        'person_stats': person_stats,
        'start': start,
        'end': end,
        'querystring': querystring,
    }
    return render_to_response('software/software_stats.html', context, context_instance=RequestContext(request))


def version_stats(request, package_id, version_id):
    version = get_object_or_404(SoftwareVersion, pk=version_id)
    start, end = get_date_range(request)
    querystring = request.META.get('QUERY_STRING', '')

    person_stats = Person.objects.filter(useraccount__cpujob__software=version, useraccount__cpujob__date__range=(start, end)).annotate(jobs=Count('useraccount__cpujob'), usage=Sum('useraccount__cpujob__cpu_usage'))

    context = {
        'version': version,
        'person_stats': person_stats,
        'start': start,
        'end': end,
        'querystring': querystring,
    }
    return render_to_response('software/version_stats.html', context, context_instance=RequestContext(request))

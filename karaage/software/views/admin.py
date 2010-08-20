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

from andsome.util.filterspecs import Filter, FilterBar
from placard.client import LDAPClient

from karaage.software.models import SoftwareCategory, SoftwarePackage, SoftwareVersion, SoftwareLicense, SoftwareAccessRequest
from karaage.software.forms import AddPackageForm, LicenseForm, SoftwareVersionForm
from karaage.people.models import Person
from karaage.util import log_object as log


def software_list(request):

    software_list = SoftwarePackage.objects.all()
    page_no = int(request.GET.get('page', 1))

    if request.REQUEST.has_key('category'):
        software_list = software_list.filter(category=int(request.GET['category']))

    if request.method == 'POST':
        new_data = request.POST.copy()
        terms = new_data['search'].lower()
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

    not_member_list = Person.objects.exclude(id__in=non_ids)

    if request.method == 'POST' and 'member-add' in request.POST:
        person = get_object_or_404(Person, pk=request.POST['member'])
        conn = LDAPClient()
        conn.add_group_member('gidNumber=%s' % package.gid, str(person.username))

        request.user.message_set.create(message="User %s added to LDAP group" % person)
        log(request.user, package, 1, "User %s added to LDAP group manually" % person)
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
        
        request.user.message_set.create(message="Version '%s' was deleted succesfully" % version)
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

    conn = LDAPClient()
    conn.remove_group_member('gidNumber=%s' % package.gid, str(person.username))

    log(request.user, package, 3, 'Removed %s from group' % person)
    log(request.user, person, 3, 'Removed from software group %s' % package)
        
    request.user.message_set.create(message="User '%s' removed successfuly" % person)

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
        conn = LDAPClient()
        conn.add_group_member('gidNumber=%s' % (softwarerequest.software_license.package.gid, softwarerequest.person.username))
        messages.add_message(request, messages.INFO, "Software request approved successfully ")
        log(request.user, softwarerequest.software_license.package, 1, "User %s approved" % person)
        return HttpResponseRedirect(reverse('kg_softwarerequest_list'))

    return render_to_response('software/request_approve.html', {'softwarerequest': softwarerequest,}, context_instance=RequestContext(request))


@permission_required('software.change_softwareaccessrequest')
def softwarerequest_delete(request, softwarerequest_id):
    softwarerequest = get_object_or_404(SoftwareAccessRequest, pk=softwarerequest_id)
    
    if request.method == 'POST':
        
        softwarerequest.delete()
        messages.add_message(request, messages.INFO, "Software request declined successfully")
        return HttpResponseRedirect(reverse('kg_softwarerequest_list'))

    return render_to_response('software/request_delete.html', {'softwarerequest': softwarerequest,}, context_instance=RequestContext(request))


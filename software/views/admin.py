from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django import forms
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Q
from django.core.paginator import QuerySetPaginator

from django_common.util.filterspecs import Filter, FilterBar
#from placard.connection import LDAPConnection

from karaage.software.models import *
from karaage.software.forms import AddPackageForm
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

    p = QuerySetPaginator(software_list, 50)
    page = p.page(page_no)


    return render_to_response('software/software_list.html', locals(), context_instance=RequestContext(request))



def software_detail(request, package_id):
    package = get_object_or_404(SoftwarePackage, pk=package_id)

    members = package.get_group_members()
    non_ids = []
    member_list = []
    if members:
        for m in members:
            try:
                person = Person.objects.get(user__username=m.uid)
                non_ids.append(person.id)
            except:
                person = None
            
            member_list.append({
                'username': m.uid,
                'person': person,
                })

    not_member_list = Person.objects.exclude(id__in=non_ids)


    if request.method == 'POST' and 'member-add' in request.POST:
        p = get_object_or_404(Person, pk=request.POST['member'])
#        conn = LDAPConnection()
#        conn.add_group_member(package.gid, str(p.username))

        request.user.message_set.create(message="User %s added to LDAP group" % p)
        log(request.user, package, 1, "User %s added to LDAP group manually" % p)
        return HttpResponseRedirect(package.get_absolute_url())
        


    return render_to_response('software/software_detail.html', locals(), context_instance=RequestContext(request))

@login_required
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

add_package = permission_required('software.add_softwarepackage')(add_package)


@login_required
def license_detail(request, license_id):
    l = get_object_or_404(SoftwareLicense, pk=license_id)

    return render_to_response('software/license_detail.html', locals(), context_instance=RequestContext(request))


@login_required
def add_edit_license(request, package_id, license_id=None):

    class LicenseForm(forms.ModelForm):
        class Meta:
            model = SoftwareLicense


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

add_edit_license = permission_required('software.delete_softwarelicense')(add_edit_license)

@login_required
def delete_version(request, package_id, version_id):
    
    v = get_object_or_404(SoftwareVersion, pk=version_id)

    if request.method == 'POST':
        v.delete()
        log(request.user, v.package, 3, 'Deleted version: %s' % v)
        
        request.user.message_set.create(message="Version '%s' was deleted succesfully" % v)
        return HttpResponseRedirect(v.get_absolute_url())

    return render_to_response('software/version_confirm_delete.html', locals(), context_instance=RequestContext(request))
    
delete_version = permission_required('software.delete_softwareversion')(delete_version)

@login_required
def add_edit_version(request, package_id, version_id=None):

    class SoftwareVersionForm(forms.ModelForm):
        class Meta:
            model = SoftwareVersion


    package = get_object_or_404(SoftwarePackage, pk=package_id)
    
    if version_id is None:
        v= None
    else:
        v = get_object_or_404(SoftwareVersion, pk=version_id)

    
    if request.method == 'POST':
        form = SoftwareVersionForm(request.POST, instance=v)
        if form.is_valid():
            v = form.save()
            return HttpResponseRedirect(package.get_absolute_url())
    else:
        form = SoftwareVersionForm(instance=v)
        
    return render_to_response('software/version_form.html', locals(), context_instance=RequestContext(request))

add_edit_version = permission_required('software.change_softwareversion')(add_edit_version)

def category_list(request):

    category_list = SoftwareCategory.objects.all()
    
    return render_to_response('software/category_list.html', locals(), context_instance=RequestContext(request))
    

@login_required
def remove_member(request, package_id, user_id):

    package = get_object_or_404(SoftwarePackage, pk=package_id)
    person = get_object_or_404(Person, pk=user_id)

#    conn = LDAPConnection()
#    conn.remove_group_member(package.gid, str(person.username))

    log(request.user, package, 3, 'Removed %s from group' % person)
    log(request.user, person, 3, 'Removed from software group %s' % package)
        
    request.user.message_set.create(message="User '%s' removed successfuly" % person)

    return HttpResponseRedirect(package.get_absolute_url())

remove_member = permission_required('software.change_softwarepackage')(remove_member)

# Copyright 2015 VPAC
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

import six
import datetime

import django_tables2 as tables

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template.defaultfilters import wordwrap
from django.apps import apps

from karaage.common.decorators import admin_required, login_required
from karaage.people.models import Person
from karaage.common import log
import karaage.common as util

from .models import SoftwareCategory, Software, SoftwareVersion
from .models import SoftwareLicense, SoftwareLicenseAgreement
from .forms import SoftwareForm, AddPackageForm, LicenseForm
from .forms import SoftwareVersionForm, SoftwareCategoryForm
from .tables import SoftwareFilter, SoftwareTable


if apps.is_installed("karaage.plugins.kgsoftware.applications"):
    from karaage.plugins.kgapplications.tables import ApplicationTable
    from .applications.views import new_application
    from .applications.models import SoftwareApplication

    def is_application_pending(person, software_license):
        query = SoftwareApplication.objects.get_for_applicant(person)
        query = query.filter(software_license=software_license)
        if query.count() > 0:
            return True

    def get_applications(software_license):
        applications = SoftwareApplication.objects.filter(
            software_license=software_license)
        applications = applications.exclude(state='C')
        return applications

    def get_applications_for_person(person, software_license):
        applications = SoftwareApplication.objects.get_for_applicant(person)
        applications = applications.filter(software_license=software_license)
        return applications

    def get_application_table(request, applications):
        applications_table = ApplicationTable(applications)
        config = tables.RequestConfig(request, paginate={"per_page": 5})
        config.configure(applications_table)
        return applications_table

else:
    from django.http import HttpResponseBadRequest

    def is_application_pending(person, software_license):
        return False

    def get_applications(software_license):
        return []

    def get_applications_for_person(person, software_license):
        return []

    def get_application_table(request, applications):
        return None

    @login_required
    def new_application(request, software_license):
        return HttpResponseBadRequest("<h1>Restricted Software denied.</h1>")


@login_required
def profile_software(request):
    person = request.user
    agreement_list = person.softwarelicenseagreement_set.all()
    return render_to_response(
        'kgsoftware/profile_software.html',
        {'person': person, 'agreement_list': agreement_list},
        context_instance=RequestContext(request))


@login_required
def software_list(request):
    if not util.is_admin(request):
        return _software_list_non_admin(request)

    queryset = Software.objects.all().select_related()
    q_filter = SoftwareFilter(request.GET, queryset=queryset)
    table = SoftwareTable(q_filter.qs)
    tables.RequestConfig(request).configure(table)

    spec = []
    for name, value in six.iteritems(q_filter.form.cleaned_data):
        if value is not None and value != "":
            name = name.replace('_', ' ').capitalize()
            spec.append((name, value))

    return render_to_response(
        'kgsoftware/software_list.html',
        {
            'table': table,
            'filter': q_filter,
            'spec': spec,
            'title': "Software list",
        },
        context_instance=RequestContext(request))


@login_required
def _software_list_non_admin(request):

    person = request.user

    query = Software.objects.filter(softwarelicense__isnull=False).distinct()
    software_list = []
    for software in query:
        data = {'software': software}
        license_agreements = SoftwareLicenseAgreement.objects.filter(
            person=person, license__software=software)
        if license_agreements.count() > 0:
            la = license_agreements.latest()
            data['accepted'] = True
            data['accepted_date'] = la.date

        software_license = software.get_current_license()
        data['pending'] = is_application_pending(person, software_license)
        software_list.append(data)

    return render_to_response(
        'kgsoftware/add_package_list.html',
        locals(),
        context_instance=RequestContext(request))


@login_required
def software_detail(request, software_id):
    software = get_object_or_404(Software, pk=software_id)
    software_license = software.get_current_license()
    person = request.user
    license_agreements = SoftwareLicenseAgreement.objects \
        .filter(person=person, license=software_license)
    agreement = None
    if license_agreements.count() > 0:
        agreement = license_agreements.latest()

    # we only list applications for current software license

    applications = get_applications(software_license)
    application_table = get_application_table(request, applications)
    open_applications = get_applications_for_person(person, software_license)

    if agreement is None and software_license is not None \
            and len(open_applications) == 0 and request.method == 'POST':

        if software.restricted and not util.is_admin(request):
            log.add(software, "New application created for %s" % request.user)
            return new_application(request, software_license)

        SoftwareLicenseAgreement.objects.create(
            person=person,
            license=software_license,
            date=datetime.datetime.today(),
        )
        person.add_group(software.group)
        log.add(
            software,
            "Approved join (not restricted) for %s" % request.user)
        messages.success(request, "Approved access to %s." % software)
        return HttpResponseRedirect(reverse('kg_profile_software'))

    return render_to_response(
        'kgsoftware/software_detail.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def add_package(request):
    if request.method == 'POST':
        form = AddPackageForm(request.POST)

        if form.is_valid():
            software = form.save()
            return HttpResponseRedirect(software.get_absolute_url())
    else:
        form = AddPackageForm()

    return render_to_response(
        'kgsoftware/add_package_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def software_edit(request, software_id):
    from karaage.common.create_update import update_object
    return update_object(
        request, object_id=software_id, model=Software,
        form_class=SoftwareForm)


@admin_required
def software_delete(request, software_id):
    from karaage.common.create_update import delete_object
    return delete_object(
        request, post_delete_redirect=reverse('kg_software_list'),
        object_id=software_id, model=Software)


@admin_required
def software_logs(request, software_id):
    obj = get_object_or_404(Software, pk=software_id)
    breadcrumbs = [
        ("Softwares", reverse("kg_software_list")),
        (six.text_type(obj), reverse("kg_software_detail", args=[obj.pk]))
    ]
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, software_id):
    obj = get_object_or_404(Software, pk=software_id)
    breadcrumbs = [
        ("Softwares", reverse("kg_software_list")),
        (six.text_type(obj), reverse("kg_software_detail", args=[obj.pk]))
    ]
    return util.add_comment(request, breadcrumbs, obj)


@login_required
def license_detail(request, license_id):
    l = get_object_or_404(SoftwareLicense, pk=license_id)
    return render_to_response(
        'kgsoftware/license_detail.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def add_license(request, software_id):
    software = get_object_or_404(Software, pk=software_id)

    form = LicenseForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            l = form.save()
            log.add(software, "license: %s added" % l)
            return HttpResponseRedirect(software.get_absolute_url())

    return render_to_response(
        'kgsoftware/license_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def edit_license(request, license_id):
    l = get_object_or_404(SoftwareLicense, pk=license_id)
    software = l.software

    form = LicenseForm(request.POST or None, instance=l)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(software.get_absolute_url())

    return render_to_response(
        'kgsoftware/license_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def license_delete(request, license_id):
    from karaage.common.create_update import delete_object
    return delete_object(
        request,
        post_delete_redirect=reverse('kg_software_list'),
        object_id=license_id, model=SoftwareLicense)


@admin_required
def delete_version(request, version_id):
    version = get_object_or_404(SoftwareVersion, pk=version_id)

    if request.method == 'POST':
        version.delete()
        log.delete(version.software, 'Deleted version: %s' % version)

        messages.success(
            request, "Version '%s' was deleted succesfully" % version)
        return HttpResponseRedirect(version.get_absolute_url())

    return render_to_response(
        'kgsoftware/version_confirm_delete.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def add_version(request, software_id):
    software = get_object_or_404(Software, pk=software_id)

    form = SoftwareVersionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            version = form.save()
            return HttpResponseRedirect(software.get_absolute_url())

    return render_to_response(
        'kgsoftware/version_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def edit_version(request, version_id):
    version = get_object_or_404(SoftwareVersion, pk=version_id)
    software = version.software

    form = SoftwareVersionForm(request.POST or None, instance=version)
    if request.method == 'POST':
        if form.is_valid():
            version = form.save()
            return HttpResponseRedirect(software.get_absolute_url())

    return render_to_response(
        'kgsoftware/version_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def category_list(request):
    category_list = SoftwareCategory.objects.all()
    return render_to_response(
        'kgsoftware/category_list.html',
        {'category_list': category_list},
        context_instance=RequestContext(request))


@admin_required
def category_create(request):
    from karaage.common.create_update import create_object
    return create_object(
        request, model=SoftwareCategory,
        form_class=SoftwareCategoryForm)


@admin_required
def category_edit(request, category_id):
    from karaage.common.create_update import update_object
    return update_object(
        request, object_id=category_id, model=SoftwareCategory,
        form_class=SoftwareCategoryForm)


@admin_required
def remove_member(request, software_id, person_id):
    software = get_object_or_404(Software, pk=software_id)
    person = get_object_or_404(Person, pk=person_id)

    if request.method == 'POST':
        person.remove_group(software.group)
        messages.success(request, "User '%s' removed successfuly" % person)

        return HttpResponseRedirect(software.get_absolute_url())

    return render_to_response(
        'kgsoftware/person_confirm_remove.html',
        locals(),
        context_instance=RequestContext(request))


@login_required
def license_txt(request, software_id):

    software = get_object_or_404(Software, pk=software_id)
    software_license = software.get_current_license()

    if software_license is None:
        raise Http404('No license found for software')

    return HttpResponse(
        wordwrap(software_license.text, 80),
        content_type="text/plain")

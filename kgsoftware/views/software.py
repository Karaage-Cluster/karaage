# Copyright 2007-2014 VPAC
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

import django_tables2 as tables
import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count, Sum
from django.template.defaultfilters import wordwrap

from karaage.common.decorators import admin_required, login_required
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.common import get_date_range, log
import karaage.common as util

from kgapplications.tables import ApplicationTable

from ..models import SoftwareCategory, Software, SoftwareVersion
from ..models import SoftwareLicense, SoftwareLicenseAgreement
from ..models import SoftwareApplication
from ..forms import AddPackageForm, LicenseForm
from ..forms import SoftwareVersionForm
from ..tables import SoftwareFilter, SoftwareTable

from .applications import new_application


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
    filter = SoftwareFilter(request.GET, queryset=queryset)
    table = SoftwareTable(filter.qs)
    tables.RequestConfig(request).configure(table)

    spec = []
    for name, value in filter.form.cleaned_data.iteritems():
        if value is not None and value != "":
            name = name.replace('_', ' ').capitalize()
            spec.append((name, value))

    return render_to_response(
        'kgsoftware/software_list.html',
        {
            'table': table,
            'filter': filter,
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
        query = SoftwareApplication.objects.get_for_applicant(person)
        query = query.filter(software_license=software_license)
        if query.count() > 0:
            data['pending'] = True
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

    applications = SoftwareApplication.objects.filter(
        software_license__software=software_license)
    applications = applications.exclude(state='C')
    applications_table = ApplicationTable(applications)
    config = tables.RequestConfig(request, paginate={"per_page": 5})
    config.configure(applications_table)

    open_applications = SoftwareApplication.objects.get_for_applicant(person)
    open_applications = open_applications.filter(
        software_license=software_license)

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
def software_verbose(request, software_id):
    software = get_object_or_404(Software, pk=software_id)

    from karaage.datastores import machine_category_get_software_details
    package_details = machine_category_get_software_details(software)

    return render_to_response(
        'kgsoftware/software_verbose.html',
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
        request, object_id=software_id, model=Software)


@admin_required
def software_delete(request, software_id):
    from karaage.common.create_update import delete_object
    return delete_object(
        request, post_delete_redirect=reverse('software_list'),
        object_id=software_id, model=Software)


@admin_required
def software_logs(request, software_id):
    obj = get_object_or_404(Software, pk=software_id)
    breadcrumbs = []
    breadcrumbs.append(
        ("Softwares", reverse("kg_software_list")))
    breadcrumbs.append(
        (six.text_type(obj), reverse("kg_software_detail", args=[obj.pk])))
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, software_id):
    obj = get_object_or_404(Software, pk=software_id)
    breadcrumbs = []
    breadcrumbs.append(
        ("Softwares", reverse("kg_software_list")))
    breadcrumbs.append(
        (six.text_type(obj), reverse("kg_software_detail", args=[obj.pk])))
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
        request, model=SoftwareCategory)


@admin_required
def category_edit(request, category_id):
    from karaage.common.create_update import update_object
    return update_object(
        request, object_id=category_id, model=SoftwareCategory)


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


@admin_required
def software_stats(request, software_id):
    software = get_object_or_404(Software, pk=software_id)
    start, end = get_date_range(request)
    querystring = request.META.get('QUERY_STRING', '')
    if software.softwareversion_set.count() == 1:
        sv = software.softwareversion_set.all()[0]
        url = reverse('kg_software_version_stats', args=[sv.id])
        return HttpResponseRedirect(url)
    version_stats = SoftwareVersion.objects \
        .filter(software=software, cpujob__date__range=(start, end)) \
        .annotate(jobs=Count('cpujob'), usage=Sum('cpujob__cpu_usage')) \
        .filter(usage__isnull=False)
    version_totaljobs = version_stats.aggregate(Sum('jobs'))['jobs__sum']
    # version_totalusage = version_stats.aggregate(Sum('usage'))
    person_stats = Person.objects \
        .filter(account__cpujob__software__software=software,
                account__cpujob__date__range=(start, end)) \
        .annotate(jobs=Count('account__cpujob'),
                  usage=Sum('account__cpujob__cpu_usage'))
    institute_stats = Institute.objects \
        .filter(person__account__cpujob__software__software=software,
                person__account__cpujob__date__range=(start, end)) \
        .annotate(jobs=Count('person__account__cpujob'),
                  usage=Sum('person__account__cpujob__cpu_usage'))

    context = {
        'software': software,
        'version_stats': version_stats,
        'version_totaljobs': version_totaljobs,
        'person_stats': person_stats,
        'institute_stats': institute_stats,
        'start': start,
        'end': end,
        'querystring': querystring,
    }
    return render_to_response(
        'kgsoftware/software_stats.html',
        context,
        context_instance=RequestContext(request))


@admin_required
def version_stats(request, version_id):
    version = get_object_or_404(SoftwareVersion, pk=version_id)
    start, end = get_date_range(request)
    querystring = request.META.get('QUERY_STRING', '')

    person_stats = Person.objects \
        .filter(account__cpujob__software=version,
                account__cpujob__date__range=(start, end)) \
        .annotate(jobs=Count('account__cpujob'),
                  usage=Sum('account__cpujob__cpu_usage'))
    institute_stats = Institute.objects \
        .filter(person__account__cpujob__software=version,
                person__account__cpujob__date__range=(start, end)) \
        .annotate(jobs=Count('person__account__cpujob'),
                  usage=Sum('person__account__cpujob__cpu_usage'))

    context = {
        'version': version,
        'person_stats': person_stats,
        'institute_stats': institute_stats,
        'start': start,
        'end': end,
        'querystring': querystring,
    }

    return render_to_response(
        'kgsoftware/version_stats.html',
        context,
        context_instance=RequestContext(request))


@login_required
def license_txt(request, software_id):

    software = get_object_or_404(Software, pk=software_id)
    software_license = software.get_current_license()

    return HttpResponse(
        wordwrap(software_license.text, 80),
        mimetype="text/plain")

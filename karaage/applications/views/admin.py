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

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect

from karaage.common.filterspecs import Filter, FilterBar

from karaage.common.decorators import admin_required
from karaage.people.models import Person
from karaage.applications.models import Applicant, Application
from karaage.applications.forms import ApplicantForm
import karaage.applications.views.base as base
from karaage.common import log
import karaage.common as util


@admin_required
def application_list(request):

    try:
        page_no = int(request.GET.get('page', 1))
    except ValueError:
        page_no = 1

    if 'search' in request.REQUEST:
        apps = Application.objects.select_related().order_by('-id')
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(short_name__icontains=term)
            q = q | Q(full_name__icontains=term)
            q = q | Q(email=term)

            persons = Person.objects.filter(q)
            applicants = Applicant.objects.filter(q)

            query = query & (Q(applicant__in=persons) | Q(applicant__in=applicants))

        apps = apps.filter(query)
    else:
        apps = Application.objects.requires_admin().order_by('-id')
        terms = ""

    p = Paginator(apps, 50)

    try:
        page = p.page(page_no)
    except (EmptyPage, InvalidPage):
        page = p.page(p.num_pages)

    return render_to_response(
            'applications/application_list_for_admin.html',
            {'page': page, 'terms': terms},
            context_instance=RequestContext(request))


#@admin_required
#def applicant_edit(request, applicant_id):
#    
#    applicant = get_object_or_404(Applicant, id=applicant_id)
#
#    form = ApplicantForm(request.POST or None, instance=applicant)
#    if request.method == 'POST':
#        if form.is_valid():
#            applicant = form.save()
#            log(request.user, applicant, 2, 'Edited')
#            messages.success(request, "%s modified successfully." % applicant)
#            return HttpResponseRedirect(reverse('kg_application_list'))
#
#    return render_to_response('applications/applicant_form.html',
#            {'form': form}, context_instance=RequestContext(request))
#
#
#@admin_required
#def new_application(request):
#    return render_to_response('applications/application_invite_admin.html',
#            {},
#            context_instance=RequestContext(request))
#
#
#@admin_required
#def application_logs(request, application_id):
#    obj = get_object_or_404(Application, pk=application_id)
#    breadcrumbs = []
#    breadcrumbs.append( ("Applications", reverse("kg_application_list")) )
#    breadcrumbs.append( (unicode(obj), reverse("kg_application_detail", args=[obj.pk])) )
#    return util.log_list(request, breadcrumbs, obj)
#
#
#@admin_required
#def add_comment(request, application_id):
#    obj = get_object_or_404(Application, pk=application_id)
#    breadcrumbs = []
#    breadcrumbs.append( ("Applications", reverse("kg_application_list")) )
#    breadcrumbs.append( (unicode(obj), reverse("kg_application_detail", args=[obj.pk])) )
#    return util.add_comment(request, breadcrumbs, obj)
#
#
#@admin_required
#def application_detail(request, application_id, state=None, label=None):
#    """ An authenticated admin is trying to access an application. """
#    application = base.get_application(pk=application_id)
#    state_machine = base.get_state_machine(application)
#    return state_machine.process(request, application, state, label, { 'is_admin': True })
#

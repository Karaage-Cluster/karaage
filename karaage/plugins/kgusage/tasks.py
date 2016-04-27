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

from .dirs import GRAPH_TMP, GRAPH_ROOT

import os
import os.path

import logging

import six
import csv
import datetime

from djcelery.app import app

from django.conf import settings
from django.db.models import Sum, Count
from django.db import transaction, IntegrityError

from karaage.machines.models import MachineCategory
from karaage.institutes.models import Institute
from karaage.projects.models import Project

from .models import CPUJob
from .models import InstituteCache, ProjectCache, PersonCache
from .models import MachineCache, MachineCategoryCache
from . import usage, graphs

import matplotlib
os.environ['MPLCONFIGDIR'] = GRAPH_TMP
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # NOQA
import matplotlib.dates as mdates  # NOQA

logger = logging.getLogger(__name__)
# app.conf.update(CELERYD_HIJACK_ROOT_LOGGER = False)


@app.task()
def gen_machine_category_cache(start, end):
    current = gen_machine_category_cache

    logger.info("gen_machine_category_cache")

    total = 2 + MachineCategory.objects.count()
    i = 0

    logger.info("caching machines")
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'caching machines', })
    _gen_machine_cache(start, end)
    i = i + 1

    logger.info("caching categories")
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'caching categories', })
    _gen_machine_category_cache(start, end)
    i = i + 1

    query = MachineCategory.objects.all()
    for machine_category in query.iterator():
        logger.info("generating category graphs %s" % machine_category)
        current.update_state(
            state='PROGRESS',
            meta={'completed': i, 'total': total,
                  'message': 'generating category graphs'})
        _gen_machine_graph(start, end, machine_category, force_overwrite=False)
        i = i + 1

    logger.info("finished")


@app.task()
def gen_cache_for_machine_category(start, end, machine_category_pk):
    machine_category = MachineCategory.objects.get(pk=machine_category_pk)

    current = gen_cache_for_machine_category

    total = 6
    i = 0

    logger.info("caching machines")
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'caching machines', })
    _gen_machine_cache(start, end)
    i = i + 1

    logger.info("caching categories")
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'caching categories', })
    _gen_machine_category_cache(start, end)
    i = i + 1

    logger.info("caching institutes")
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'caching institutes'})
    _gen_institute_cache(start, end, machine_category)
    i = i + 1

    logger.info("caching projects")
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'caching projects'})
    _gen_project_cache(start, end, machine_category)
    i = i + 1

    logger.info("caching people")
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'caching people'})
    _gen_person_cache(start, end, machine_category)
    i = i + 1

    logger.info("generating machine category graph")
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'generating machine category graphs', })
    _gen_institute_graph(start, end, machine_category, force_overwrite=False)
    _gen_trend_graph(start, end, machine_category, force_overwrite=False)
    i = i + 1

    logger.info("finished")


@app.task()
def gen_cache_for_project(start, end, project_pk, machine_category_pk):
    project = Project.objects.get(pk=project_pk)
    machine_category = MachineCategory.objects.get(pk=machine_category_pk)

    current = gen_cache_for_project
    total = 1
    i = 0

    logger.info("generating project graphs %s" % project)
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'generating project graphs'})
    _gen_project_trend_graph(
        project, start, end, machine_category, force_overwrite=False)
    i = i + 1


@app.task()
def gen_cache_for_institute(start, end, institute_pk, machine_category_pk):
    institute = Institute.objects.get(pk=institute_pk)
    machine_category = MachineCategory.objects.get(pk=machine_category_pk)

    current = gen_cache_for_institute
    total = 1
    i = 0

    logger.info("generating institute graphs %s" % institute)
    current.update_state(
        state='PROGRESS',
        meta={'completed': i, 'total': total,
              'message': 'generating institute graphs'})
    _gen_institute_trend_graph(
        institute, start, end, machine_category, force_overwrite=False)
    i = i + 1


@app.task()
def gen_cache_for_all_institutes(start, end, machine_category_pk):
    machine_category = MachineCategory.objects.get(pk=machine_category_pk)

    current = gen_cache_for_all_institutes
    total = len(machine_category.institutequota_set.all())
    i = 0

    for iq in machine_category.institutequota_set.all():
        institute = iq.institute
        logger.info("generating institute graphs %s" % institute)
        current.update_state(
            state='PROGRESS',
            meta={'completed': i, 'total': total,
                  'message': 'generating institute graphs'})
        _gen_institute_trend_graph(
            institute, start, end, machine_category, force_overwrite=False)
        i = i + 1


# -----------------------------------------------------------------------


def _gen_machine_category_cache(start, end):
    query = MachineCategory.objects.all()
    for machine_category in query.iterator():
        try:
            with transaction.atomic():
                cache = MachineCategoryCache.objects.create(
                    machine_category=machine_category,
                    start=start, end=end,
                    cpu_time=0, no_jobs=0,
                    available_time=0)
                machines = machine_category.machine_set.all()
                total_time = 0
                for machine in machines:
                    m_start = machine.start_date
                    m_end = machine.end_date
                    if not m_end:
                        m_end = end

                    assert start <= end
                    assert m_start <= m_end

                    if start > m_end or m_start > end:
                        continue
                    if end < m_start or m_end < start:
                        continue

                    this_start = start
                    if start < m_start:
                        this_start = m_start
                    this_end = end
                    if end > m_end:
                        this_end = m_end

                    num_days = (this_end - this_start).days + 1
                    total_time += (machine.no_cpus * num_days * 24 * 60 * 60)

                query = CPUJob.objects.filter(
                    machine__category=machine_category,
                    date__range=(start, end))
                data = query.aggregate(
                    usage=Sum('cpu_usage'),
                    jobs=Count('id'))

                data['usage'] = data['usage'] or 0

                cache.cpu_time = data['usage']
                cache.no_jobs = data['jobs']
                cache.available_time = total_time
                cache.save()
        except IntegrityError:
            # entry already exists
            pass


def _gen_machine_cache(start, end):
    query = CPUJob.objects.filter(date__range=(start, end))
    query = query.values('machine')
    query = query.annotate(usage=Sum('cpu_usage'), jobs=Count('id'))
    query = query.order_by()

    for data in query.iterator():
        data['usage'] = data['usage'] or 0
        machine = data['machine']
        try:
            with transaction.atomic():
                MachineCache.objects.create(
                    machine_id=machine,
                    start=start, end=end,
                    cpu_time=data['usage'], no_jobs=data['jobs'])
        except IntegrityError:
            # entry already exists
            pass


def _gen_institute_cache(start, end, machine_category):
    query = CPUJob.objects.filter(
        date__range=(start, end),
        machine__category=machine_category,
    )
    query = query.values('project__institute')
    query = query.annotate(usage=Sum('cpu_usage'), jobs=Count('id'))
    query = query.order_by()

    for data in query.iterator():
        data['usage'] = data['usage'] or 0
        institute = data['project__institute']
        try:
            with transaction.atomic():
                InstituteCache.objects.create(
                    institute_id=institute,
                    machine_category=machine_category,
                    start=start, end=end,
                    cpu_time=data['usage'], no_jobs=data['jobs'])
        except IntegrityError:
            # entry already exists
            pass


def _gen_project_cache(start, end, machine_category):
    query = CPUJob.objects.filter(
        date__range=(start, end),
        machine__category=machine_category,
    )
    query = query.values('project')
    query = query.annotate(usage=Sum('cpu_usage'), jobs=Count('id'))
    query = query.order_by()

    for data in query.iterator():
        data['usage'] = data['usage'] or 0
        project = data['project']
        try:
            with transaction.atomic():
                ProjectCache.objects.create(
                    project_id=project,
                    machine_category=machine_category,
                    start=start, end=end,
                    cpu_time=data['usage'], no_jobs=data['jobs'])
        except IntegrityError:
            # entry already exists
            pass


def _gen_person_cache(start, end, machine_category):
    query = CPUJob.objects.filter(
        date__range=(start, end),
        machine__category=machine_category,
    )
    query = query.values('project', 'account__person')
    query = query.annotate(usage=Sum('cpu_usage'), jobs=Count('id'))
    query = query.order_by()

    for data in query.iterator():
        data['usage'] = data['usage'] or 0
        project = data['project']
        person = data['account__person']
        try:
            with transaction.atomic():
                PersonCache.objects.create(
                    person_id=person, project_id=project,
                    machine_category=machine_category,
                    start=start, end=end,
                    cpu_time=data['usage'], no_jobs=data['jobs'])
        except IntegrityError:
            # entry already exists
            pass


# -----------------------------------------------------------------------

def _check_directory_exists(filename):
    base_path = os.path.dirname(filename)
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def _gen_project_trend_graph(project,
                             start,
                             end,
                             machine_category,
                             force_overwrite=False):
    """Generates a bar graph for a project

    Keyword arguments:
    project -- Project
    start -- start date
    end -- end date
    machine_category -- MachineCategory object

    """
    filename = graphs.get_project_trend_graph_filename(
        project, start, end, machine_category)
    csv_filename = os.path.join(GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(GRAPH_ROOT, filename + '.png')

    _check_directory_exists(csv_filename)
    _check_directory_exists(png_filename)

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return

    query = CPUJob.objects.filter(
        project=project,
        machine__category=machine_category,
        date__range=(start, end)
    )
    query = query.values('account', 'account__username', 'date')
    query = query.annotate(Sum('cpu_usage')).order_by('account', 'date')

    t_start = start
    t_end = end

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlim(start, end + datetime.timedelta(days=1))
    ax.set_title('%s   %s - %s' % (project.pid, start_str, end_str))
    ax.set_ylabel("CPU Time (hours)")
    ax.set_xlabel("Date")

    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    ax.xaxis.set_minor_locator(mdates.DayLocator())

    data = {}
    x_data = {}
    y_data = {}

    with open(csv_filename, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in query.iterator():
            csv_writer.writerow([
                row['account__username'],
                row['date'], row['cpu_usage__sum'] / 3600.00
            ])

            account = row['account']
            date = row['date']

            if account not in data:
                data[account] = {}
                x_data[account] = []
                y_data[account] = []

            data[account][date] = row['cpu_usage__sum']

    for account, dates in six.iteritems(data):
        start = t_start
        end = t_end
        while start <= end:
            total = 0
            if start in dates:
                total = dates[start]
            x_data[account].append(start)
            y_data[account].append(total / 3600.00)
            start = start + datetime.timedelta(days=1)

    del data

    totals = []
    start = t_start
    end = t_end
    while start <= end:
        totals.append(0)
        start = start + datetime.timedelta(days=1)

    count = 0
    for account in x_data.keys():
        ax.bar(
            x_data[account], y_data[account],
            bottom=totals,
            color=graphs.get_colour(count),
            edgecolor=graphs.get_colour(count),
            align='edge')
        count = count + 1

        i = 0
        start = t_start
        end = t_end
        while start <= end:
            totals[i] += y_data[account][i]
            i = i + 1
            start = start + datetime.timedelta(days=1)

    del x_data
    del y_data
    del totals

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_filename)
    plt.close()


def _gen_institute_graph(start, end, machine_category,
                         force_overwrite=False):
    """ Pie chart comparing institutes usage. """
    filename = graphs.get_institute_graph_filename(
        start, end, machine_category)
    csv_filename = os.path.join(GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(GRAPH_ROOT, filename + '.png')

    _check_directory_exists(csv_filename)
    _check_directory_exists(png_filename)

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return

    institute_list = Institute.active.all()

    plt.subplots(figsize=(4, 4))

    data = []
    labels = []

    total = 0
    with open(csv_filename, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        for institute in institute_list.iterator():
            hours, jobs = usage.get_institute_usage(
                institute, start, end, machine_category)
            total = total + int(hours)
            if hours > 0:
                csv_writer.writerow([institute.name, hours, jobs])
                data.append(hours)
                labels.append(institute.name)

        mcu = usage.get_machine_category_usage(machine_category, start, end)
        hours = int(mcu.available_time - total)
        csv_writer.writerow(["unused", hours])
        data.append(hours)
        labels.append('Unused')

    plt.pie(data, labels=labels, autopct='%1.1f%%', shadow=True)
    plt.tight_layout()
    plt.savefig(png_filename)
    plt.close()


def _gen_machine_graph(start, end, machine_category,
                       force_overwrite=False):
    """ Pie chart comparing machines usage. """
    filename = graphs.get_machine_graph_filename(start, end, machine_category)
    csv_filename = os.path.join(GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(GRAPH_ROOT, filename + '.png')

    _check_directory_exists(csv_filename)
    _check_directory_exists(png_filename)

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return

    machine_list = machine_category.machine_set.all()

    plt.subplots(figsize=(4, 4))

    data = []
    labels = []

    with open(csv_filename, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        for machine in machine_list.iterator():
            hours, jobs = usage.get_machine_usage(machine, start, end)
            if hours > 0:
                csv_writer.writerow([machine.name, hours, jobs])
                data.append(hours)
                labels.append(machine.name)

    plt.pie(data, labels=labels, autopct='%1.1f%%', shadow=True)

    del data
    del labels

    plt.tight_layout()
    plt.savefig(png_filename)
    plt.close()


def _gen_trend_graph(start, end, machine_category,
                     force_overwrite=False):
    """ Total trend graph for machine category. """
    filename = graphs.get_trend_graph_filename(start, end, machine_category)
    csv_filename = os.path.join(GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(GRAPH_ROOT, filename + '.png')

    _check_directory_exists(csv_filename)
    _check_directory_exists(png_filename)

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return

    query = CPUJob.objects.filter(
        machine__category=machine_category,
        date__range=(start, end)
    )
    query = query.values('date').annotate(Sum('cpu_usage'))
    query = query.order_by('date')

    t_start = start
    t_end = end

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlim(start, end)
    ax.set_title('%s - %s' % (start_str, end_str))
    ax.set_ylabel("CPU Time (hours)")
    ax.set_xlabel("Date")

    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    ax.xaxis.set_minor_locator(mdates.DayLocator())

    data = {}
    x_data = []
    y_data = []

    with open(csv_filename, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in query.iterator():
            csv_writer.writerow([
                row['date'], row['cpu_usage__sum'] / 3600.00
            ])

            date = row['date']

            data[date] = row['cpu_usage__sum']

    start = t_start
    end = t_end
    while start <= end:
        total = 0
        if start in data:
            total = data[start]
        x_data.append(start)
        y_data.append(total / 3600.00)
        start = start + datetime.timedelta(days=1)

    del data

    ax.plot(x_data, y_data)

    del x_data
    del y_data

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_filename)
    plt.close()


def _gen_institute_trend_graph(institute,
                               start,
                               end,
                               machine_category,
                               force_overwrite=False):
    """ Institute trend graph for machine category. """
    filename = graphs.get_institute_trend_graph_filename(
        institute, start, end, machine_category)
    csv_filename = os.path.join(GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(GRAPH_ROOT, filename + '.png')

    _check_directory_exists(csv_filename)
    _check_directory_exists(png_filename)

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return

    query = CPUJob.objects.filter(
        project__institute=institute,
        machine__category=machine_category,
        date__range=(start, end)
    )
    query = query.values('date').annotate(Sum('cpu_usage'))
    query = query.order_by('date')

    t_start = start
    t_end = end

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlim(start, end)
    ax.set_title('%s - %s' % (start_str, end_str))
    ax.set_ylabel("CPU Time (hours)")
    ax.set_xlabel("Date")

    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    ax.xaxis.set_minor_locator(mdates.DayLocator())

    data = {}
    x_data = []
    y_data = []

    with open(csv_filename, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in query.iterator():
            csv_writer.writerow([
                row['date'], row['cpu_usage__sum'] / 3600.00
            ])

            date = row['date']

            data[date] = row['cpu_usage__sum']

    start = t_start
    end = t_end
    while start <= end:
        total = 0
        if start in data:
            total = data[start]
        x_data.append(start)
        y_data.append(total / 3600.00)
        start = start + datetime.timedelta(days=1)

    del data

    ax.plot(x_data, y_data)

    del x_data
    del y_data

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_filename)
    plt.close()

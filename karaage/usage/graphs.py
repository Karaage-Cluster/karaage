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

import csv
import datetime
import os.path

from django.conf import settings
from django.db.models import Sum

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from karaage.usage.models import CPUJob
from karaage.institutes.models import Institute


def get_colour(index):
    """ get color number index. """
    colours = [
            'red', 'blue', 'green', 'pink',
            'yellow', 'magenta','orange', 'cyan',
    ]
    default_colour = 'purple'
    if index < len(colours):
        return colours[index]
    else:
        return default_colour


def get_project_trend_graph_url(project,
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
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
            "projects",
            "%s_%s_%s_%i" % (
                project.pid, start_str, end_str, machine_category.id)
    )
    csv_filename = os.path.join(settings.GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(settings.GRAPH_ROOT, filename + '.png')

    urls = {
        'graph_url': os.path.join(settings.GRAPH_URL, filename + ".png"),
        'data_url': os.path.join(settings.GRAPH_URL, filename + ".csv"),
    }

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return urls

    rows = CPUJob.objects.filter(
            project=project,
            machine__category=machine_category,
            date__range=(start_str, end_str)
            ).values('account', 'account__username', 'date').annotate(Sum('cpu_usage')).order_by('account', 'date')

    t_start = start
    t_end = end

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
        for row in rows:
            csv_writer.writerow([
                row['account__username'],
                row['date'], row['cpu_usage__sum']/3600.00
            ])

            account = row['account']
            date = row['date']

            if account not in data:
                data[account] = {}
                x_data[account] = []
                y_data[account] = []

            data[account][date] = row['cpu_usage__sum']

    for account, dates in data.iteritems():
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
            color=get_colour(count),
            edgecolor=get_colour(count),
            align='edge')
        count = count + 1

        i = 0
        start = t_start
        end = t_end
        while start <= end:
            totals[i] += y_data[account][i]
            i = i + 1
            start = start + datetime.timedelta(days=1)

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_filename)

    return urls


def get_institute_graph_url(start, end, machine_category,
        force_overwrite=False):
    """ Pie chart comparing institutes usage. """

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    filename = os.path.join(
            "institutes",
            "%s_%s_%i" % (
                start_str, end_str, machine_category.id)
    )
    csv_filename = os.path.join(settings.GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(settings.GRAPH_ROOT, filename + '.png')

    urls = {
        'graph_url': os.path.join(settings.GRAPH_URL, filename + ".png"),
        'data_url': os.path.join(settings.GRAPH_URL, filename + ".csv"),
    }

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return urls

    institute_list = Institute.active.all()

    plt.subplots(figsize=(4, 4))

    data = []
    labels = []

    with open(csv_filename, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        for institute in institute_list:
            usage = institute.get_usage(start, end, machine_category)
            if usage[0] is not None:
                csv_writer.writerow([institute.name, usage[0]])
                data.append(usage[0])
                labels.append(institute.name)

    plt.pie(data, labels=labels, autopct='%1.1f%%', shadow=True)
    plt.tight_layout()
    plt.savefig(png_filename)

    return urls


def get_machine_graph_url(start, end, machine_category,
        force_overwrite=False):
    """ Pie chart comparing machines usage. """

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    filename = os.path.join(
            "machines",
            "%s_%s_%i" % (
                start_str, end_str, machine_category.id)
    )
    csv_filename = os.path.join(settings.GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(settings.GRAPH_ROOT, filename + '.png')

    urls = {
        'graph_url': os.path.join(settings.GRAPH_URL, filename + ".png"),
        'data_url': os.path.join(settings.GRAPH_URL, filename + ".csv"),
    }

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return urls

    machine_list = machine_category.machine_set.all()

    plt.subplots(figsize=(4, 4))

    data = []
    labels = []

    with open(csv_filename, 'wb') as csv_file:
        csv_writer = csv.writer(csv_file)
        for machine in machine_list:
            usage = machine.get_usage(start, end)
            if usage[0] is not None:
                csv_writer.writerow([machine.name, usage[0]])
                data.append(usage[0])
                labels.append(machine.name)

    plt.pie(data, labels=labels, autopct='%1.1f%%', shadow=True)
    plt.tight_layout()
    plt.savefig(png_filename)

    return urls

def get_trend_graph_url(start, end, machine_category,
        force_overwrite=False):
    """ Total trend graph for machine category. """

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    filename = os.path.join(
            "trends",
            "%s_%s_%i" % (
                start_str, end_str, machine_category.id)
    )
    csv_filename = os.path.join(settings.GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(settings.GRAPH_ROOT, filename + '.png')

    urls = {
        'graph_url': os.path.join(settings.GRAPH_URL, filename + ".png"),
        'data_url': os.path.join(settings.GRAPH_URL, filename + ".csv"),
    }

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return urls

    rows = CPUJob.objects.filter(
            machine__category=machine_category,
            date__range=(start_str, end_str)
            ).values('date').annotate(Sum('cpu_usage')).order_by('date')

    t_start = start
    t_end = end

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
        for row in rows:
            csv_writer.writerow([
                row['date'], row['cpu_usage__sum']/3600.00
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

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_filename)

    return urls


def get_institute_trend_graph_url(institute,
                                  start,
                                  end,
                                  machine_category,
                                  force_overwrite=False):
    """ Institute trend graph for machine category. """

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    filename = os.path.join(
            "i_trends",
            "%s_%s_%s_%i" % (
                institute.name.replace(' ', '').replace('/', '-').lower(),
                start_str, end_str, machine_category.id)
    )
    csv_filename = os.path.join(settings.GRAPH_ROOT, filename + '.csv')
    png_filename = os.path.join(settings.GRAPH_ROOT, filename + '.png')

    urls = {
        'graph_url': os.path.join(settings.GRAPH_URL, filename + ".png"),
        'data_url': os.path.join(settings.GRAPH_URL, filename + ".csv"),
    }

    if not settings.GRAPH_DEBUG or force_overwrite:
        if os.path.exists(csv_filename):
            if os.path.exists(png_filename):
                return urls

    rows = CPUJob.objects.filter(
            project__institute=institute,
            machine__category=machine_category,
            date__range=(start_str, end_str)
            ).values('date').annotate(Sum('cpu_usage')).order_by('date')

    t_start = start
    t_end = end

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
        for row in rows:
            csv_writer.writerow([
                row['date'], row['cpu_usage__sum']/3600.00
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

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_filename)

    return urls


def get_institutes_trend_graph_urls(start, end, machine_category,
        force_overwrite=False):
    """ Get all institute trend graphs. """

    graph_list = []
    for institute in Institute.active.all():
        urls = get_institute_trend_graph_url(
            institute, start, end, machine_category, force_overwrite)
        graph_list.append(urls)

    return graph_list

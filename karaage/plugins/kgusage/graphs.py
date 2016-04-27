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

import os.path
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from .dirs import GRAPH_URL


def get_colour(index):
    """ get color number index. """
    colours = [
        'red', 'blue', 'green', 'pink',
        'yellow', 'magenta', 'orange', 'cyan',
    ]
    default_colour = 'purple'
    if index < len(colours):
        return colours[index]
    else:
        return default_colour


# -----------------------------------------------------------------------


def get_project_trend_graph_filename(project,
                                     start, end,
                                     machine_category):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "projects",
        "%s_%s_%s_%i" % (
            project.pid, start_str, end_str, machine_category.id)
    )
    return filename


def get_institute_graph_filename(start, end, machine_category):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "institutes",
        "%s_%s_%i" % (
            start_str, end_str, machine_category.id)
    )
    return filename


def get_machine_graph_filename(start, end, machine_category):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "machines",
        "%s_%s_%i" % (
            start_str, end_str, machine_category.id)
    )
    return filename


def get_trend_graph_filename(start, end, machine_category):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "trends",
        "%s_%s_%i" % (
            start_str, end_str, machine_category.id)
    )
    return filename


def get_institute_trend_graph_filename(institute,
                                       start, end,
                                       machine_category):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "i_trends",
        "%s_%s_%s_%i" % (
            institute.name.replace(' ', '').replace('/', '-').lower(),
            start_str, end_str, machine_category.id)
    )
    return filename


# -----------------------------------------------------------------------

def get_project_trend_graph_url(project,
                                start, end,
                                machine_category):
    """Generates a bar graph for a project. """

    filename = get_project_trend_graph_filename(
        project, start, end, machine_category)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_institute_graph_url(start, end, machine_category):
    """ Pie chart comparing institutes usage. """

    filename = get_institute_graph_filename(start, end, machine_category)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_machine_graph_url(start, end, machine_category):
    """ Pie chart comparing machines usage. """

    filename = get_machine_graph_filename(start, end, machine_category)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_trend_graph_url(start, end, machine_category):
    """ Total trend graph for machine category. """

    filename = get_trend_graph_filename(start, end, machine_category)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_institute_trend_graph_url(institute,
                                  start, end,
                                  machine_category):
    """ Institute trend graph for machine category. """

    filename = get_institute_trend_graph_filename(
        institute, start, end, machine_category)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_institutes_trend_graph_urls(start, end, machine_category):
    """ Get all institute trend graphs. """

    graph_list = []
    for iq in machine_category.institutequota_set.all():
        institute = iq.institute
        urls = get_institute_trend_graph_url(
            institute, start, end, machine_category)
        urls['institute'] = institute
        graph_list.append(urls)

    return graph_list

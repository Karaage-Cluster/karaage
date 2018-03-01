# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

from karaage.institutes.models import Institute

from .dirs import GRAPH_URL


try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


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


def get_project_trend_graph_filename(project, start, end):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "projects",
        "%s_%s_%s" % (project.pid, start_str, end_str)
    )
    return filename


def get_institute_graph_filename(start, end):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "institutes",
        "%s_%s" % (start_str, end_str)
    )
    return filename


def get_machine_graph_filename(start, end):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "machines",
        "%s_%s" % (start_str, end_str)
    )
    return filename


def get_trend_graph_filename(start, end):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "trends",
        "%s_%s" % (start_str, end_str)
    )
    return filename


def get_institute_trend_graph_filename(institute, start, end):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    filename = os.path.join(
        "i_trends",
        "%s_%s_%s" % (
            institute.name.replace(' ', '').replace('/', '-').lower(),
            start_str, end_str)
    )
    return filename


# -----------------------------------------------------------------------

def get_project_trend_graph_url(project, start, end):
    """Generates a bar graph for a project. """

    filename = get_project_trend_graph_filename(project, start, end)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_institute_graph_url(start, end):
    """ Pie chart comparing institutes usage. """

    filename = get_institute_graph_filename(start, end)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_machine_graph_url(start, end):
    """ Pie chart comparing machines usage. """

    filename = get_machine_graph_filename(start, end)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_trend_graph_url(start, end):
    """ Total trend graph for machine category. """

    filename = get_trend_graph_filename(start, end)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_institute_trend_graph_url(institute, start, end):
    """ Institute trend graph for machine category. """

    filename = get_institute_trend_graph_filename(institute, start, end)
    urls = {
        'graph_url': urlparse.urljoin(GRAPH_URL, filename + ".png"),
        'data_url': urlparse.urljoin(GRAPH_URL, filename + ".csv"),
    }

    return urls


def get_institutes_trend_graph_urls(start, end):
    """ Get all institute trend graphs. """

    graph_list = []
    for institute in Institute.objects.all():
        urls = get_institute_trend_graph_url(institute, start, end)
        urls['institute'] = institute
        graph_list.append(urls)

    return graph_list

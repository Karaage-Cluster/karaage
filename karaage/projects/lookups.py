from django.db.models import Q
from django.utils.html import escape

from karaage.projects.models import Project

class ProjectLookup(object):

    def get_query(self, q, request):
        """ return a query set.  you also have access to request.user if needed """

        if not request.user.is_staff:
            return Project.objects.none()

        return Project.objects.filter(Q(pid__icontains=q) | Q(name__icontains=q))

    def format_result(self, p):
        """ the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  """
        return escape(u"%s" % (p))

    def format_item(self, p):
        """ the display of a currently selected object in the area below the search box. html is OK """
        return escape(u"%s" % (p))

    def get_objects(self, ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return Project.objects.filter(pk__in=ids)

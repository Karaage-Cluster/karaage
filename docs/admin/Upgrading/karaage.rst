Upgrading Karaage
=================

When upgrading karaage there are issues that you may need to be aware
of. Please read all the relevant sections. e.g. if upgrading from 2.5.6
to 2.6.5, the sections on 2.5.7 and 2.6.5 are relevant.

Also read :doc:`migrations`.

Upgrading to 2.5.7 or beyond
----------------------------

-  You may need to change your apache config to point to the new default
   graph location. Before this was /kgadmin\_graphs/ and /kgreg\_graphs/
   Now these are located at /karaage\_graphs/
-  The directory for matplotlib is now set to /var/www/.matplotlib
-  Please see the default apache config under /etc/karaage

Upgrading to 2.6.5 or beyond
----------------------------

-  Upgraded to support staticfiles.
-  Requires Django 1.4 or greater. If using Debian Squeeze, you can
   obtain Django 1.4 from Debian backports.
-  Any references to MEDIA\_URL in locate templates needs to be replaced
   with STATIC\_URL for correct functionality.
-  Installing the Debian packages should run collectstatic to
   automatically collect the static files.

Upgrading to 2.7.0 or beyond
----------------------------

-  Read the instructions below fully before upgrading.
-  Requires django-andsome 1.3.1, django-pbs 1.2.3, django-placard 2.0,
   karaaage-admin 1.4.0 and karaage-register 1.1.0 (or later versions).
-  Changes to templates.
-  Beadcrumbs changed. Rename block from bread\_crumbs\_1 to
   breadcrumbs, add div element, add link to home page. For example,
   change:

   ::

           {% block bread_crumbs_1 %}
           &rsaquo; <a href="{% url kg_application_list %}">Applications</a>
           &rsaquo; {{ application }}
           {% endblock %}

   to:

   ::

           {% block breadcrumbs %}
           <div class="breadcrumbs">
           <a href='{{ base_url|default:"/" }}'>Home</a>
           &rsaquo; <a href="{% url kg_application_list %}">Applications</a>
           &rsaquo; {{ application }}
           </div>
           {% endblock %}

-  The top line should be {% extends X %}, where X is normally a base
   page. There are a limited set of base pages:

   -  main.html is for most pages with the sidebar.
   -  forms.html is for a form without a side bar.
   -  forms-side.html is for a form with a sidebar.

   All of these pages use base\_site.html, which in turn extends from
   base.html, these pages should not be used directly however. In
   general:

   -  replace {% extends base\_site.html %} by {% extends forms.html %}
   -  replace {% extends threecol.html %} with {% extends main.html %}.
   -  Some pages might extend other pages e.g.
      applications/application\_detail\_base.html, which extends
      main.html. These are fine. There should not be any other base
      types however.

-  content\_title block no longer used, and should be deleted.
-  The content block (except for forms.html usage) should have <div
   id="content-main">....</div> at the top level.
-  (karaage-admin only) All object tools belong in a block called
   object-tools, not in the content block or anywhere else. These need
   to be inside a div element with a class of module. The class of the
   ul must be "object-tools". For example:

   ::

           {% block object-tools %}
           {% if perms.applications.add_application %}
           <div class="module object-tools">
           <h2>Object links</h2>
           <ul>
           <li><a class="addlink" href="{% url kg_userapplication_invite %}">Send invitation</a></li>
           </ul>
           </div>
           {% endif %}
           {% endblock %}

-  A command, upgrade\_template has been developed to try and
   automatically update your templates. Note that you should *ensure*
   you have a *valid backup* first. You should not run this on base
   templates that exist in the root template directory (these should be
   skipped automatically).

   ::

       kg-manage upgrade_template <files>

-  upgrade\_template will get some details wrong. For example, if a
   block depends on a prior tag, upgrade\_template may incorrectly move
   the block without moving the required tag.
-  upgrade\_template may also get confused if the HTML is invalid,
   resulting in a broken template.
-  As such it is important to check the rendered pages to make sure they
   look ok and have no missing pieces of information. e.g. "Comments ()"
   is missing the number of comments within the brackets.

-  base\_site.html might also need updating. For example:

   ::

       {% extends "base.html" %}
       {% load i18n %}

       {% block site_name_title %}{% trans 'Karaage' %}{% endblock %}

       {% block branding %}
       <h1 id="site-name">{% trans 'Karaage' %}</h1>
       {% endblock %}

-  Changes to LDAP layer. Need to create a /etc/karaage/ldap\_schemas.py
   file to define the LDAP model.
-  If it doesn't break, it isn't my fault.

-  New HOME\_DIRECTORY setting. For example:

   ::

       HOME_DIRECTORY = "/vpac/%(default_project)s/%(uid)s"

Upgrading to Django 1.4 or beyond
---------------------------------

Django 1.5 removes some depreciated stuff. So changes may be required.
The following changes allow everything to work with both Django 1.4 and
Django 1.5.

-  url in templates:
-  Add {% load url from future %} to templates.
-  Arguments should be space separated, not comma separated.
-  Add quotes to first argument in {% url ... %}.

Upgrading to 3.0.0 or beyond
----------------------------

-  Please see http://karaage.readthedocs.org/


"""
Sphinx plugins for Karaage documentation. Copied from Django.
"""
import json
import os
import re

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx import addnodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.domains.std import Cmdoption
from sphinx.util import logging
from sphinx.util.console import bold
from sphinx.writers.html import HTMLTranslator

logger = logging.getLogger(__name__)
# RE for option descriptions without a '--' prefix
simple_option_desc_re = re.compile(
    r'([-_a-zA-Z0-9]+)(\s*.*?)(?=,\s+(?:/|-|--)|$)')


def setup(app):
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )
    app.add_crossref_type(
        directivename="templatetag",
        rolename="ttag",
        indextemplate="pair: %s; template tag"
    )
    app.add_crossref_type(
        directivename="templatefilter",
        rolename="tfilter",
        indextemplate="pair: %s; template filter"
    )
    app.add_crossref_type(
        directivename="fieldlookup",
        rolename="lookup",
        indextemplate="pair: %s; field lookup type",
    )
    app.add_object_type(
        directivename="django-admin",
        rolename="djadmin",
        indextemplate="pair: %s; django-admin command",
        parse_node=parse_django_admin_node,
    )
    app.add_directive('django-admin-option', Cmdoption)
    app.add_config_value('karaage_next_version', '0.0', True)
    app.add_directive('versionadded', VersionDirective)
    app.add_directive('versionchanged', VersionDirective)
    app.add_builder(KaraageStandaloneHTMLBuilder)


class VersionDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        if len(self.arguments) > 1:
            msg = """Only one argument accepted for directive '{directive_name}::'.
            Comments should be provided as content,
            not as an extra argument.""".format(directive_name=self.name)
            raise self.error(msg)

        env = self.state.document.settings.env
        ret = []
        node = addnodes.versionmodified()
        ret.append(node)

        if self.arguments[0] == env.config.karaage_next_version:
            node['version'] = "Development version"
        else:
            node['version'] = self.arguments[0]

        node['type'] = self.name
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        try:
            env.get_domain('changeset').note_changeset(node)
        except ExtensionError:
            # Sphinx < 1.8: Domain 'changeset' is not registered
            env.note_versionchange(node['type'], node['version'], node, self.lineno)
        return ret


class KaraageHTMLTranslator(HTMLTranslator):
    """
    Karaage-specific reST to HTML tweaks.
    """

    # Don't use border=1, which docutils does by default.
    def visit_table(self, node):
        self.context.append(self.compact_p)
        self.compact_p = True
        self._table_row_index = 0  # Needed by Sphinx
        self.body.append(self.starttag(node, 'table', CLASS='docutils'))

    def depart_table(self, node):
        self.compact_p = self.context.pop()
        self.body.append('</table>\n')

    def visit_desc_parameterlist(self, node):
        self.body.append('(')  # by default sphinx puts <big> around the "("
        self.first_param = 1
        self.optional_param_level = 0
        self.param_separator = node.child_text_separator
        self.required_params_left = sum(isinstance(c, addnodes.desc_parameter) for c in node.children)

    def depart_desc_parameterlist(self, node):
        self.body.append(')')

    #
    # Turn the "new in version" stuff (versionadded/versionchanged) into a
    # better callout -- the Sphinx default is just a little span,
    # which is a bit less obvious that I'd like.
    #
    # FIXME: these messages are all hardcoded in English. We need to change
    # that to accommodate other language docs, but I can't work out how to make
    # that work.
    #
    version_text = {
        'versionchanged': 'Changed in Karaage %s',
        'versionadded': 'New in Karaage %s',
    }

    def visit_versionmodified(self, node):
        self.body.append(
            self.starttag(node, 'div', CLASS=node['type'])
        )
        version_text = self.version_text.get(node['type'])
        if version_text:
            title = "%s%s" % (
                version_text % node['version'],
                ":" if node else "."
            )
            self.body.append('<span class="title">%s</span> ' % title)

    def depart_versionmodified(self, node):
        self.body.append("</div>\n")

    # Give each section a unique ID -- nice for custom CSS hooks
    def visit_section(self, node):
        old_ids = node.get('ids', [])
        node['ids'] = ['s-' + i for i in old_ids]
        node['ids'].extend(old_ids)
        super().visit_section(node)
        node['ids'] = old_ids


def parse_django_admin_node(env, sig, signode):
    command = sig.split(' ')[0]
    env.ref_context['std:program'] = command
    title = "kg-manage %s" % sig
    signode += addnodes.desc_name(title, title)
    return command


class KaraageStandaloneHTMLBuilder(StandaloneHTMLBuilder):
    """
    Subclass to add some extra things we need.
    """

    name = 'djangohtml'

    def finish(self):
        super().finish()
        logger.info(bold("writing templatebuiltins.js..."))
        xrefs = self.env.domaindata["std"]["objects"]
        templatebuiltins = {
            "ttags": [
                n for ((t, n), (k, a)) in xrefs.items()
                if t == "templatetag" and k == "ref/templates/builtins"
            ],
            "tfilters": [
                n for ((t, n), (k, a)) in xrefs.items()
                if t == "templatefilter" and k == "ref/templates/builtins"
            ],
        }
        outfilename = os.path.join(self.outdir, "templatebuiltins.js")
        with open(outfilename, 'w') as fp:
            fp.write('var django_template_builtins = ')
            json.dump(templatebuiltins, fp)
            fp.write(';\n')

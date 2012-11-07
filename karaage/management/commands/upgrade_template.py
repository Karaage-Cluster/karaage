# Copyright 2007-2010 VPAC
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

from django.core.management.base import BaseCommand, CommandError
import django.template.base
import sys
import re
import os
import filecmp
import bs4
import codecs

class Command(BaseCommand):
    help = 'Upgrade one/more template files'
    args = '<file> <file> ...'

    def handle(self, *args, **options):
        self.block = []

        for name in args:
            self.in_breadcrumbs = False
            self.found_object_tools = False
            self.object_tools = None

            print "processing %s" % name
            with codecs.open(name, "r", "utf-8") as f:
                content = f.read()

            l = django.template.base.Lexer(content, name)
            self.tokens = l.tokenize()
            text, stop = self.do_tokens()
            end = self.get_end()
            assert stop is None

            tmp_file = name + ".tmp"
            with codecs.open(tmp_file, "w", "utf-8") as f:
                f.write(text)
                f.write(end)
            if os.path.exists(name) and filecmp.cmp(tmp_file, name, shallow=False):
                os.remove(tmp_file)
            else:
                os.rename(tmp_file, name)


    def do_tokens(self, stop=None):
        text = []

        while self.tokens:
            token = self.tokens.pop(0)

            if token.token_type == 0:
                value = self.do_text(token)

            elif token.token_type == 1:
                value = self.do_var(token)

            elif token.token_type == 2:
                value = self.do_block(token, stop)

            elif token.token_type == 3:
                value = self.do_comment(token)

            if value is None:
                return "".join(text), token

            text.extend(value)

        return "".join(text), None

    def do_text(self, token):
        return token.contents

    def do_var(self, token):
        split = token.contents.split(" ")

        if split[0] == "block.super" and self.in_breadcrumbs:
            return ""

        return [ "{{ %s }}"% token.contents ]

    def do_comment(self, token):
        return [ "{#%s#}"% token.contents ]

    def do_block(self, token, stop):
        text = []

        split = token.contents.split(" ")

        if stop is not None and split[0] == stop:
            return None
        elif split[0] == "extends":
            new_name = None
            if split[1] == '"forms.html"':
                self.extends = "forms.html"
            elif split[1] == '"base_site.html"':
                new_name = '"forms.html"'
                self.extends = "forms.html"
            elif split[1] == '"changelist.html"':
                self.extends = "main.html"
            elif split[1] == '"main.html"':
                self.extends = "main.html"
            elif split[1] == '"people/profile_base.html"':
                self.extends = "main.html"
            elif split[1] == '"applications/application_detail_base.html"':
                self.extends = "main.html"
            elif split[1] == '"institutes/institute_base.html"':
                self.extends = "main.html"
            elif split[1] == '"forms-side.html"':
                self.extends = "main.html"
            elif split[1] == '"threecol.html"':
                new_name = '"main.html"'
                self.extends = "main.html"
            else:
                raise ValueError("Unknown extends of %s" % split[1])

            if new_name is not None:
                split[1] = new_name
                text.append("{%% %s %%}" % " ".join(split))
            else:
                text.append("{%% %s %%}" % token.contents)

        elif split[0] == "block":
            if split[1] == "bread_crumbs_1" or split[1] == "breadcrumbs":
                self.in_breadcrumbs = True
                value, stop_token = self.do_tokens("endblock")
                self.in_breadcrumbs = False
                nl_at_start = re.search("^ *\n", value) is not None
                nl_at_end = re.search("\n *$", value) is not None

                soup = bs4.BeautifulSoup(value, "lxml")
                kwargs = { 'class': 'breadcrumbs' }
                bc = soup.find('div', **kwargs)

                split[1] = "breadcrumbs"
                text.append("{%% %s %%}" % " ".join(split))

                if bc is None:
                    bc = soup.new_tag("div", **kwargs)

                    a = soup.new_tag("a", href='{{ base_url|default:"/" }}')
                    a.string = "Home"
                    bc.append(a)

                    a = soup.new_string("&nbsp;")
                    bc.append(a)

                    body = soup.body
                    p = body.contents[0]
                    if p is not None and p.name == 'p':
                        p.extract()
                        contents = p.contents
                    else:
                        contents = body.contents
                    for child in list(contents):
                        bc.append(child.extract())
                    body.append(bc)

#                if "<div" not in value:
#                    text.append('\n<div class="breadcrumbs">\n')
#                    text.append('<a href="{{ base_url|default:"/" }}">Home</a>')
#                    if not nl_at_start:
#                        text.append('\n')
#                    text.append(value)
#                    if not nl_at_end:
#                        text.append('\n')
#                    text.append('</div>\n')
#                else:
#                    text.append(value)

                text.extend(self.soup_to_text(soup.body.children))

                text.append(self.do_end_block(stop_token, "endblock"))

            elif (split[1] == "content" or split[1] == "content_main") and self.extends == "forms.html":
                value, stop_token = self.do_tokens("endblock")

                split[1] = "content"
                text.append("{%% %s %%}" % " ".join(split))
                text.append(value)
                text.append(self.do_end_block(stop_token, "endblock"))

            elif (split[1] == "content" or split[1] == "content_main") and self.extends == "main.html":
                value, stop_token = self.do_tokens("endblock")
                nl_at_start = re.search("^ *\n", value) is not None
                nl_at_end = re.search("\n *$", value) is not None

                soup = bs4.BeautifulSoup(value, "lxml")
                cm = soup.find('div', id="content-main")
                cre = soup.find('div', id="content-related-extra")
                kwargs = { 'class': 'object-tools' }
                ot_ul = soup.find('ul', **kwargs)
                if cre is not None:
                    self.object_tools = cre.div
                    cre.extract()

                elif ot_ul is not None:
                    kwargs = { 'class': 'module' }
                    module = soup.new_tag("div", **kwargs)
                    title = soup.new_tag("h2")
                    title.string="Object links"
                    module.insert(0, title)
                    module.append(ot_ul.extract())
                    self.object_tools = module

                split[1] = "content"
                text.append("{%% %s %%}" % " ".join(split))

                if cm is None:
                    cm = soup.new_tag("div", id="content-main")
                    body = soup.body
                    for child in list(body.contents):
                        cm.append(child.extract())
                    body.append(cm)

#                cm = "meow"
#                if cm is None:
#                    raise RuntimeError("ddd:")
#                    text.append('\n<div id="content-main">')
#                    if not nl_at_start:
#                        text.append('\n')
#                    text.append(value)
#                    if not nl_at_end:
#                        text.append('\n')
#                    text.append('</div>\n')
#                else:
#                    text.append(value)

                text.extend(self.soup_to_text(soup.body.children))

                text.append(self.do_end_block(stop_token, "endblock"))

            elif split[1] == "content_title":
                value, stop_token = self.do_tokens("endblock")
                value = value.strip()
                if value != "" and value != "&nbsp;":
                    text.append("{%% %s %%}" % token.contents)
                    text.append(value)
                    text.append(self.do_end_block(stop_token, "endblock"))

            elif split[1] == "objecttools" or split[1] == "object-tools":
                value, stop_token = self.do_tokens("endblock")
                split[1] = "object-tools"

                soup = bs4.BeautifulSoup(value, "lxml")
                kwargs = { "class": "module" }
                module = soup.find('div', **kwargs)

                if module is None:
                    module = soup.new_tag("div", **kwargs)
                    title = soup.new_tag("h2")
                    title.string="Object links"
                    module.insert(0, title)
                    body = soup.body
                    for child in list(body.contents):
                        module.append(child.extract())
                    body.append(module)

                text.append("{%% %s %%}" % " ".join(split))
                text.extend(self.soup_to_text(soup.body.children))
                text.append(self.do_end_block(stop_token, "endblock"))
                self.found_object_tools = True

            elif split[1] == "sidebar_extra":
                value, stop_token = self.do_tokens("endblock")
                text.append("{%% %s %%}" % token.contents)
                text.append(value)
                text.append(self.do_end_block(stop_token, "endblock"))

            else:
                value, stop_token = self.do_tokens("endblock")
                text.append("{%% %s %%}" % token.contents)
                text.append(value)
                text.append(self.do_end_block(stop_token, "endblock"))

        else:
            text.append("{%% %s %%}" % token.contents)

        return text

    def do_end_block(self, token, expected):
        if token is None:
            raise ValueError("Could not find end for %s" % expected)

        split = token.contents.split(" ")
        assert split[0] == expected
        return "{%% %s %%}" % token.contents

    def get_end(self):
        text = []
        if self.object_tools is not None and not self.found_object_tools:

            ot = self.object_tools

            for i in ot.find_all("li"):
                if i.string is not None:
                    if i.string.strip() == "":
                        i.decompose()
                elif len(i.contents)==0:
                    i.decompose()

            for i in ot.find_all("br"):
                if i.string is not None:
                    if i.string.strip() == "":
                        i.decompose()
                elif len(i.contents)==0:
                    i.decompose()

            ul = ot.find("ul")
            del ul['class']

            text.append("\n{% block sidebar_extra %}\n")
            text.extend(self.soup_to_text([ ot ]))
            text.append("{% endblock %}\n")
        return "".join(text)

    def soup_to_text(self, children):
        text = []
        for i in children:
            text.append(unicode(i))
        return text

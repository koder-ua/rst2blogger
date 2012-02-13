#!/usr/bin/env python
# encoding: utf-8
"""Convert an RST file to HTML suitable for posting to a blogger blog.

Requires BeautifulSoup 3.0.8.1 and docutils.

If you're a Mac user, see also http://pypi.python.org/pypi/rst2marsedit
"""

from pyquery import PyQuery

from docutils.core import publish_string

from common import hide_show_func, html_escape

import rest_plugins

footer =  u'''
Исходники этого и других постов со скриптами лежат тут - `my blog at github`_
При использовании их, пожалуйста, ссылайтесь на `koder-ua.blogspot.com`_

.. _my blog at github: https://github.com/koder-ua/python-lectures
.. _koder-ua.blogspot.com: http://koder-ua.blogspot.com/
'''


class RST2Blogspot(object):
    def __init__(self, initial_header_level=4):
        self.initial_header_level = initial_header_level 
        self.clear()

    def clear(self):
        self.found_splitter = False
        self.post_body = []

    def write_raw(self, text):
        self.post_body.append(text)

    def write(self, text, esc_all=False):
        self.write_raw(html_escape(text))

    def get_result(self):
        return "".join(self.post_body)

    def format_post(self, rst_file):
        """Read the rst file and return a tuple containing the title and
        an HTML string for the post.
        """
        self.clear()
        body = open(rst_file).read() + '\n' + footer
        return self.format_post_from_string(body)

    def format_post_from_string(self, body):
        """Returns a tuple containing the title and an HTML string for the
        post body.
        """
        try:
            html = publish_string(
                body,
                writer_name='html',
                settings_overrides={'initial_header_level': \
                                        self.initial_header_level,
                                    'generator':False,
                                    'traceback':True,
                                    },
                )
            if not html:
                raise ValueError('No HTML produced by docutils')
        except Exception as err:
            raise RuntimeError('Could not convert input file to HTML: %s' % err)

        # Pull out the body of the HTML to make the blog post,
        # removing the H1 element with the title.
        d = PyQuery(html, parser='html')
        title = d('body').find('h1:first').html()
        d('body').find('h1:first').remove()


        self.write_raw('<script type="text/javascript" ' + \
                           'src="http://ajax.googleapis.com/ajax/' + \
                           'libs/jquery/1.7.1/jquery.min.js"></script>\n')
        self.write_raw(d('body').html())
        self.write_raw(hide_show_func)

        if not self.found_splitter:
            print "WARNING: no text splitter found!"

        return title, self.get_result()

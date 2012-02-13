# -*- coding:utf8 -*-
# code from pygments

import uuid

from docutils import nodes
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from common import hide_show2, hide_show, check_python_code, hide_show_span

formatter = HtmlFormatter(noclasses=True)

class Pygments(Directive):
    """ Source code syntax hightlighting.
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True

    def run(self):
        self.assert_has_content()
        lexer = get_lexer_by_name(self.arguments[0])
        code = u'\n'.join(self.content)
        line = 0

        if self.arguments[0] == 'python':
            check_python_code(code, line, 
                                use_lint='use_lint' in self.options, 
                                imp_mod='imp_mod' in self.options
                                )
        
        hightlited_code = highlight(code, lexer, formatter)

        if 'hide' in self.options:
            pass
        else:
            pass

        oid_code = str(uuid.uuid1()).replace("-", "")
        oid_raw = str(uuid.uuid1()).replace("-", "")

        res = [
            hide_show2.format(hided_text=u"С подсветкой синтаксиса", 
                              visible_text=u"Без подсветки синтаксиса",
                              hided_id1=oid_code,
                              hided_id2=oid_raw,
                              default_text=u"Без подсветки синтаксиса")]

        res.append("<br>")
        res.append(hide_show_span.format(hided_id=oid_code, default_style=""))
        res.append(hightlited_code.strip())
        res.append("</span>")
        res.append(hide_show_span.format(hided_id=oid_raw, 
                            default_style='style="line-height:100%;display:none"'))
        res.append(code)
        res.append("</span>")

        return [nodes.raw('', "\n".join(res), format='html')]

directives.register_directive('sourcecode', Pygments)

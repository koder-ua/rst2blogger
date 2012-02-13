import sys
import os.path
import warnings
import traceback

from pylint import lint
import logilab.astng.builder


hide_show_func = """
    <script  type="text/javascript">
        function on_hidabble_click()
        {
            var me = $(this);
            var hide_id = me.attr("objtohide");
            var controlled_object = $('#' + hide_id);
            controlled_object.toggle();

            if ( controlled_object.is(":visible") )
                me.html(me.attr("visible_text"));
            else
                me.html(me.attr("hided_text"));

            return false;
        }
        $(".hidder").click(on_hidabble_click);

        function on_double_hidabble_click()
        {
            var me = $(this);
            
            var hide_id1 = me.attr("objtohide1");
            var hide_id2 = me.attr("objtohide2");
            
            var controlled_object1 = $('#' + hide_id1);
            var controlled_object2 = $('#' + hide_id2);
            
            controlled_object1.toggle();
            controlled_object2.toggle();

            if ( controlled_object1.is(":visible") )
                me.html(me.attr("visible_text"));
            else
                me.html(me.attr("hided_text"));

            return false;
        }
        $(".dhidder").click(on_double_hidabble_click);
    </script>
"""

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    ">": "&gt;",
    "<": "&lt;",
}

def html_escape(text, esc_all=False):
    loc_html_escape_table = html_escape_table.copy()

    if esc_all:
        html_escape_table["'"] = '&#39;'
    
    return "".join( loc_html_escape_table.get(c, c) for c in text)

hide_show = u'<a hided_text="{hided_text}" ' + \
            u'visible_text="{visible_text}" ' + \
            u'style="border-bottom: 2px dotted #2020B0; ' + \
                    u'color: #2020B0; font-style:italic; font-size: 90%" ' + \
            u'class="hidder" objtohide="{hided_id}">{default_text}</a>'

hide_show_span = '<span {default_style} id="{hided_id}">'

hide_show2 = u'<a hided_text="{hided_text}" ' + \
             u'visible_text="{visible_text}" ' + \
             u'style="border-bottom: 2px dotted #2020B0; ' + \
                   u'color: #2020B0; font-style:italic; font-size: 90%" ' + \
             u'class="dhidder" objtohide1="{hided_id1}" objtohide2="{hided_id2}" >{default_text}</a>'

def check_python_code(code, line, use_lint=True, imp_mod=False):

    code = "# -*- coding:utf8 -*-\nfrom oktest import ok\n" + code.encode("utf8")

    try:
        compile(code, "<opt_file>", 'exec')
    except SyntaxError as err:
        err.lineno += line - 2
        err.args = (err.args[0], (err.args[1][0], err.args[1][1] + line - 2, err.args[1][2]))
        raise err

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dname = os.tmpnam()

    os.mkdir(dname)
    fname = os.path.join(dname, "module.py")
    
    open(fname, 'w').write(code)

    try:
        if use_lint:
            rep = Reporter()

            try:
                stderr = sys.stderr
                sys.stderr = Stdout_replacer()  
                logilab.astng.builder.MANAGER.astng_cache.clear()
                rcfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), "pylintrc")
                lint.Run( [fname, '--rcfile=' + rcfile], rep, exit=False)
                #lint.PyLinter( [fname], rep)
            finally:
                sys.stderr = stderr

            for tp, data, msg in rep.messages:
                if tp not in ('C0111',):
                    if tp == 'W0611' and msg == "Unused import ok":
                        continue
                    print "Python block in line {0}: {1} {2}".format(
                            line + data[3] - 2, # we add two lines to the top og the file
                            tp, msg)
        
        if imp_mod:
            try:
                sys.path.insert(0, dname)
                import module
            except:
                traceback.print_exc()
            finally:
                del sys.path[0]
                del sys.modules['module']

    finally:    
        os.unlink(fname)
        os.rmdir(dname)

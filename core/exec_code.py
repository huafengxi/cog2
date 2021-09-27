import itertools
tfile_count = itertools.count(1)
def gen_tfile():
    return '/tmp/tfile.{}'.format(tfile_count.next())

def write_tfile(code):
    tfile = gen_tfile()
    with open(tfile, 'w') as f:
        f.write(code)
    return tfile

import parser
def is_expr(t):
    try: return parser.expr(t)
    except: return

def eval_expr(code, env):
    if is_expr(code):
        return eval(code, env, env)
    return code

import sys
from parse import pymix_parse
pymix_parse.wrap_tpl = 'o("""%s """, locals())'
pymix_parse.comment_char = ''
def exec_code(code, env, path=None):
    code = pymix_parse.parse(code)
    if not path: path = write_tfile(code)
    exec compile(code, path, 'exec') in env, env

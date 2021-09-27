#!/usr/bin/env python2
'''
reference: https://www.python.org/about/success/cog/
mark=// ./cog.py file1 file2... # update generated code
clean=1 ./cog.py file1 file2... # remove generated code

# single line form, no output insert
//cog gen_xxx() //end

# single line form
//cog 'hello, world!'
//end

# multiline form
//cog
o<<'### header ###'
for i in range(10):
    echo $i
//output
//end

# the 'a.py' to generate newfile
for i in range(10):
   $i
o>>'a.txt' # write output to file
'''
import sys, os
base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
def cog_path(x): return os.path.realpath(os.path.join(base_path, x))
for p in ',core,ext'.split(','):
    sys.path.insert(0, cog_path(p))
import os
import logging

def help(): print __doc__
len(sys.argv) > 1 or help() or sys.exit(1)
mark = os.getenv('mark', '//')
begin_mark, output_mark, end_mark = mark + 'cog', mark + 'output', mark + 'end'
log_level = os.getenv('log') or 'info'
logging.basicConfig(level=getattr(logging, log_level.upper(), None), format="%(asctime)s %(levelname)s %(message)s")

import exec_code as ex
from output import Output
o = Output(globals())
class Cog:
    def __init__(self):
        self.cur_file = None
    def cur_dir(self):
        return os.path.dirname(self.cur_file)
    def is_cur_file(self, x):
        return os.path.realpath(x) == os.path.realpath(self.cur_file)
cog = Cog()

def cog_render(code):
    if os.getenv('clean', '0') == '1': return ''
    logging.info('cog render: %s', code.strip())
    if '\n' in code:
        ex.exec_code(code, globals())
        return o.fetch()
    else:
        ret = ex.eval_expr(code.strip(), globals())
        if ret == None: return o.fetch()
        return ret

def cog_transform(text):
    def add_newline(s):
        if not s: return ''
        return s if s[-1] == '\n' else s + '\n'
    logging.debug('transform: %s', text)
    sep = re.search('(^.*{}.*\n)'.format(output_mark), text, re.M)
    if '\n' not in text:
        cog_render(text)
        return text
    sep = sep.group(1) if sep else '\n'
    code, output = text.split(sep, 1)
    pycode = code.split('\n', 1)[1] if '\n' in code else code
    out = cog_render(pycode) or ''
    return '{}{}{}'.format(code, sep, add_newline(out))

import re
def update_file(path, old_text, new_text):
    if new_text == old_text:
        logging.info('file %s not change.', path)
        return
    logging.info('file %s updated.', path)
    with open(path, 'w') as f:
        f.write(new_text)

cog_search_path = ['.', base_path, os.path.realpath(base_path + '/ext')]
def find_file(p):
    for d in cog_search_path:
        np = os.path.join(d, p)
        if os.path.exists(np):
            return np, file(np).read()
    pack = globals().get('__pack__', None)
    return pack and pack.find_file(p)
def do_handle_file(file_name):
    path_and_content = find_file(file_name)
    if not path_and_content:
        logging.error('not found file: %s, search_path: %s', file_name, cog_search_path)
        return
    p, text = path_and_content
    logging.debug('handle file: %s', p)
    cog.cur_file = p
    if p.endswith('.py'):
        logging.info('load whole file: %s', p)
        ex.exec_code(text, globals())
    elif begin_mark in text and end_mark in text:
        logging.info('load inline cog: %s', p)
        new_text = re.sub('^([^\n]*{})(.+?)((?: *|^[^\n]*){})'.format(begin_mark, end_mark), lambda m: '{}{}{}'.format(m.group(1), cog_transform(m.group(2)),m.group(3)), text, flags=re.S|re.M)
        update_file(p, text, new_text)
    else:
        logging.debug('no cog mark in file: %s', p)

def load(plist):
    if type(plist) == str:
        plist = plist.split()
    for p in plist:
        do_handle_file(p)
load('init.py')
for p in sys.argv[1:]:
    load(p)

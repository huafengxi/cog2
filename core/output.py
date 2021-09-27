import inspect
import traceback
import logging
class CallerInfo:
    def __init__(self, depth=1):
        frame = None
        try:
            frame, self.filename, self.lineno, self.function, code_ctx, index = inspect.stack(1)[depth]
            self.env = frame.f_locals
            self.code = code_ctx[0] if code_ctx else None
        finally:
            del frame
    def __repr__(self):
        return 'file={} lineno={} func={} code={}'.format(self.filename, self.lineno, self.function, self.code)

import re
def sub(template, ns, globals=globals(), max_iter=50):
    def epath(ns): return id(ns)
    '''no exception should happen'''
    if '$' not in template: return template
    def template_substitute(template, ns, substitute_handler):
        '''magic marker example: $word ${abc.def} ${{1+2}}'''
        return re.sub('(?s)(?<![$])(?:\${{(.+?)}}|\${(.+?)}|\$(\w+))', lambda m: substitute_handler(ns, m.group(1) or m.group(2) or m.group(3), m.group(0)), template)
    def format_ret(x, orig):
        if (type(x) == list or type(x) == tuple) and all(type(x) == str for x in x):
            return ' '.join(x)
        if x == None or type(x) != str and type(x) != unicode and type(x) != int and type(x) != float and type(x) != long:
            return orig
        else:
            return str(x)
    old, cur = "", template
    def substitute_handler(ns, expr, orig_expr):
        try:
            ret = handle_interpolate(expr, ns, globals)
        except Exception as e:
            logging.info('interpolate fail: expr=%s, ns=%s, %s', expr, epath(ns), traceback.format_exc())
            ret = orig_expr
        return format_ret(ret, orig_expr)
    for i in range(max_iter):
        if cur == old: break
        old, cur = cur, template_substitute(cur, ns, substitute_handler)
    return cur

def handle_interpolate(expr, ns, g_env):
    if expr.count('\n') > 0:
        exec expr in g_env, ns
        return ''
    return eval(expr, g_env, ns)

class Output(list):
    def __init__(self, g_env):
        self.g_env = g_env
        list.__init__(self)
    def clone(self):
        return Output(self.g_env)
    def __call__(self, text, env=None):
        return self.out(text, CallerInfo(2).env if env == None else env)
    def out(self, text, env=None):
        text = text.rstrip()
        def add_newline(s):
            if not s: return ''
            return s if s[-1] == '\n' else s + '\n'
        if not env: env = CallerInfo(3).env
        line = sub(text, env, globals=self.g_env)
        self.append(add_newline(line))
        return self
    def __lshift__(self, text):
        return self.out(text)
    def __rshift__(self, path):
        def safe_read(p):
            try:
                return file(p).read()
            except IOError:
                return
        new_text = self.fetch()
        if new_text == safe_read(path):
            logging.info('{} not need update'.format(path))
            return
        with open(path, 'w') as f:
            logging.info('{} updated'.format(path))
            f.write(new_text)
    def clear(self): del self[:]
    def get(self): return ''.join(self)
    def fetch(self):
        s = self.get()
        self.clear()
        return s


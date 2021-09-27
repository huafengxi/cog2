import re
class BlockParser:
    def __init__(self):
        self.block = []
    def emit(self):
        ret = self.block
        self.block = []
        return ret
    def append(self, line):
        begin, end = self.parse(line)
        if begin or self.block:
            self.block.append(line)
        return self.block, end

class CommentDetector(BlockParser):
    def parse(self, line):
        return re.match('\s*/[*]', line), re.search('[*]/\s*$', line)

class MacroDetector(BlockParser):
    def parse(self, line):
        return line.startswith('#'), not line.rstrip().endswith('\\')

class StructDetector(BlockParser):
    def parse(self, line):
        return line.rstrip().endswith('{'), line.startswith('}')

class SingleLineDetector(BlockParser):
    def parse(self, line):
        return True, True

class ChainParser:
    def __init__(self, *parser_list):
        self.parser_list = parser_list
    def append(self, line):
        for p in self.parser_list:
            consumed, finished = p.append(line)
            if not consumed: continue
            if not finished: return []
            return p.emit()
        raise Exception("unrecognize block: %s", line)
    def parse(self, f):
        for lineno, line in enumerate(file(f)):
            body = self.append(line)
            if body: yield lineno - len(body) + 2, body

symbol_match_rule = '''
macro: #define ID
struct: ANY ID {$
func: ANY ID\(
scalar_assign: ANY ID = ANY;
scalar: ANY ID;
array: ANY ID\[\w+\];
func_typedef: ANY \(\*ID\)\(ANY\);
'''
def preprocess_rexp(r):
    return r.replace('ANY', '[_a-zA-Z0-9&* ]*?').replace(' ', '\s+').replace('ID', '(\w+)')
symbol_match_rexp_list = [(t, preprocess_rexp(r)) for t, r in re.findall('^(\w+): ([^\n]+)$', symbol_match_rule, re.M)]
def parse_symbol(line):
    if '//keep' in line: return ''
    for t,r in symbol_match_rexp_list:
        m = re.match(r, line)
        if m: return m.group(1)
    return ''

def parse_explict_global(line):
    mark = '// #global:'
    m = re.search(mark + '(.+)$', line)
    return m.group(1).split() if m else []

def add_prefix(s, prefix):
    return re.sub('^(_*)(\w+)', r'\1{0}\2'.format(s.islower() and prefix or prefix.upper()), s)

def scan_file(f):
    p = ChainParser(CommentDetector(), MacroDetector(), StructDetector(), SingleLineDetector())
    for lineno, body in p.parse(f):
        for s in parse_explict_global(body[0]):
            yield lineno, s, body
        yield lineno, parse_symbol(body[0]), body

class Sym:
    def __init__(self, file, lineno, name, body):
        self.file, self.lineno, self.name, self.body = file, lineno, name, body
    def doc(self):
        return '{} {}:{} {}'.format(self.name, self.file, self.lineno, self.body[0])
    def is_macro(self):
        return self.body[0].startswith('#define ')
    def prefixed(self, p):
        return add_prefix(self.name, p)

def scan_file_list(filelist):
    def is_my_xxx(s): return re.match('^_*(my_|MY_)', s)
    def is_good_sym(s, body):
        return s and 'nonsym' not in body[0] and s[0] not in '0123456789' and s not in ('main', 'enum', 'struct', '_GNU_SOURCE') and not is_my_xxx(s)
    all_sym = set()
    for f in filelist:
        if file(f).read().startswith('//keep'): continue
        for lineno, sym, body in scan_file(f):
            if is_good_sym(sym, body) and sym not in all_sym:
                all_sym.add(sym)
                yield Sym(f, lineno, sym, body)

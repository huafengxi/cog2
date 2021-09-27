from scan_sym import scan_file_list

def rename_sym(s, remap_table):
    def sym_translate(content, handler): return re.sub(r'\b(\w+)\b', lambda m: handler(m.group(1)), content)
    return sym_translate(s, lambda x: remap_table.get(x, x))

def macro_redef(s, rename_table):
    def mkpath(p): return os.path.normpath(os.path.join('.', p))
    return '#line {lineno} "{filename}"\n{new_macro}'.format(lineno=s.lineno, filename=mkpath(s.file), new_macro=rename_sym(''.join(s.body), rename_table))

def gen_ns(prefix, ns_file):
    filelist = filter(lambda x: not is_tpl_file(x), get_include_list(cog.cur_file, [os.path.join('.', ns_file)]))
    symlist = list(scan_file_list(filelist))
    #if !defined(__NS_PREFIX__)
    #define __NS_PREFIX__ ${prefix.upper()}
    #define __ns_prefix__ ${prefix}
    for s in symlist:
        #pragma push_macro("${s.name}")
        #undef ${s.name}
    for s in symlist:
        if not s.is_macro():
            #define ${s.name} ${s.prefixed(prefix)} // ${s.doc()}
    #else
    for s in symlist:
        #pragma pop_macro("${s.name}")
    rename_table = dict((s.name, s.prefixed(prefix)) for s in symlist)
    for s in symlist:
        if s.is_macro():
            ${macro_redef(s, rename_table)}
    #endif
    o>>ns_file

def remap_prefix(s, p1, p2):
    'p1,p2 are prefix, this func remap sym: p1XXX -> p2XXX'
    return re.sub('\W(_*)({}|{})'.format(p1, p1.upper()), lambda m: m.group(1) + p2.upper() if m.group(2).isupper() else p2, s)

def unprefix(prefix, *filelist):
    if not filelist:
        return remove_prefix(sys.stdin.read(), prefix)
    for p in filelist:
        with open(p, 'w') as f:
             f.write(remove_prefix(file(p).read(), prefix))

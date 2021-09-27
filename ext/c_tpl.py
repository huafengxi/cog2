def parse_my_token(p):
    token_list = re.findall('\w+', read_include(p))
    return list(sorted(set(s for s in token_list if re.match('^_*(my|MY)_', s))))

def gen_tpl(o, path):
    def remove_prefix(s): return re.sub('^(my|MY)', '', s)
    symlist = parse_my_token(path)
    for s in symlist:
        #define $s tns(${remove_prefix(s)})
    #include "${os.path.basename(path)}"
    for s in symlist:
        #undef $s
    o>>(path + '.gen')

def use_tpl(prefix, *file_list):
    def rename(s, p):
        return re.sub('^(_*)(my_|MY_)', lambda m: m.group(1) + p.upper() if m.group(2).isupper() else p, s)
    #define tns(x) $prefix ## x
    for p in file_list:
        rp = os.path.join(cog.cur_dir(), p)
        gen_tpl(o.clone(), rp)
        symlist = parse_my_token(rp)
        real_symlist = [rename(s, prefix + '_') for s in symlist]
        #include "$p.gen" // #global: $real_symlist
    #undef tns

def is_tpl_file(p): return p.endswith('.gen')

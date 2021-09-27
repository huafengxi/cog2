def perf(expr):
    import cProfile, pstats
    cProfile.run(expr, 'pstat')
    p = pstats.Stats('pstat')
    p.sort_stats('time').print_stats(30)

def is_same_file(p1, p2): return os.path.realpath(p1) == os.path.realpath(p2)
def popen(cmd): return os.popen(cmd).read()

def read_multiple_file(filelist):
    return '\n'.join(file(p).read() for p in filelist)

def get_direct_include_list(p):
    dirname = os.path.dirname(p)
    flist = [os.path.join(dirname, i) for i in re.findall('^ # include "([^"]+)"'.replace(' ', ' *'), file(p).read(), re.M)]
    return flist

def get_include_list(path, exclude_list=[]):
    flist, to_process,  = set(), [path]
    while to_process:
       p = to_process.pop(0)
       if p in flist or p in exclude_list: continue
       to_process.extend(get_direct_include_list(p))
       flist.add(p)
    return flist

def read_include(path):
    return read_multiple_file(get_include_list(path))

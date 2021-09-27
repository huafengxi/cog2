def assemble_section(name):
    .u.$name : {
    _${name}_section_start = .;
    KEEP(*(.u.${name}));
    _${name}_section_end = .;
    }
def gen_assemble_section(filelist):
    if type(filelist) == str:
        filelist = filelist.split()
    section_list = sorted(re.findall('^USECTION_DEF\((.+)\)', read_multiple_file(filelist), re.M))
    for s in section_list:
        assemble_section(s)

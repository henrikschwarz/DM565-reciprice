from os import listdir

extensions = ['py', 'html']
linecount = 0
a = [i for i in listdir()]
a.remove('venv')

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def check_dir(dname):
    count = 0
    for s in listdir(dname):
        if s.lower() in ['venv', 'lib']:
            continue
        if '.' not in s:
            count += check_dir(dname+'/'+s)
        elif s.split('.')[-1] in extensions:
            c = file_len(dname+'/'+s)
            print(dname,s,c)
            count += c
    return count


print(check_dir('.'))
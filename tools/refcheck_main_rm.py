import re,subprocess,sys,difflib
d=sys.argv[1]
def show(ref,fn): return subprocess.run(['git','-C',d,'show','%s:%s'%(ref,fn)],capture_output=True,check=True).stdout.decode('utf-8')
def mp(m):
    m=int(m)
    if m in (29,80): return 'X%d'%m
    return str(m if m<29 else (m-1 if m<80 else m-2))
def conv(s):
    def f(m):
        out='%s %s'%(m.group(1),mp(m.group(2)))
        if m.group(3): out+=m.group(3)+mp(m.group(4))
        return out
    s=re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?',f,s)
    s=re.sub(r'(?m)^\| \[(\d+)\]\(',lambda m:'| [%s]('%mp(m.group(1)),s)
    return s
for fn in sys.argv[2:]:
    a=conv(show('HEAD',fn)).splitlines(); b=open(d+'/'+fn,encoding='utf-8').read().splitlines()
    print('=====',fn)
    for l in difflib.unified_diff(a,b,lineterm='',n=0):
        if l.startswith(('---','+++')): continue
        print(l[:170])

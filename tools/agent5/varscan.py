import re,sys
src=open('apply_patches.ps1',encoding='ascii').read().splitlines()
# split into function bodies by brace tracking (approximate): find "function Name" lines, then track braces
funcs=[]  # (name,start,end)
i=0
n=len(src)
cur=None
depth=0
for idx,line in enumerate(src):
    m=re.match(r'^function\s+([A-Za-z0-9_-]+)',line)
    if cur is None and m:
        cur=(m.group(1),idx); depth=0
    if cur is not None:
        # strip strings roughly
        l=re.sub(r"'[^']*'","''",line)
        l=re.sub(r'#.*$','',l)
        depth+=l.count('{')-l.count('}')
        if depth<=0 and '{' in l or (depth<=0 and idx>cur[1]):
            if depth<=0:
                funcs.append((cur[0],cur[1],idx)); cur=None
# top-level = lines not in any function
inf=set()
for f in funcs:
    for k in range(f[1],f[2]+1): inf.add(k)
var=re.compile(r'\$\{?(?:script:|global:|local:|private:)?([A-Za-z_][A-Za-z0-9_]*)\}?')
def scan(lines,label):
    names={}
    for ln,line in lines:
        l=re.sub(r"'[^']*'","''",line)
        l=re.sub(r'(?<!`)#.*$','',l)
        for m in var.finditer(l):
            nm=m.group(1)
            if nm in ('_','args','matches','null','true','false','PSItem'): continue
            names.setdefault(nm.lower(),{}).setdefault(nm,set()).add(ln+1)
    for low,d in names.items():
        if len(d)>1:
            print(label, {k:sorted(v)[:5] for k,v in d.items()})
for name,s,e in funcs:
    scan([(k,src[k]) for k in range(s,e+1)], 'FUNC '+name)
scan([(k,src[k]) for k in range(n) if k not in inf], 'TOPLEVEL')
print('functions:',len(funcs))

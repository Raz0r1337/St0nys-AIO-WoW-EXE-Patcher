import re,os,glob,json
root='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/awrepo'
files=[f for f in glob.glob(root+'/src/**/*.*',recursive=True)+glob.glob(root+'/include/**/*.*',recursive=True) if f.endswith(('.h','.cpp','.hpp'))]
def strip(s):
    s=re.sub(r'/\*.*?\*/','',s,flags=re.S); s=re.sub(r'//[^\n]*','',s); return s
txt={f:strip(open(f,encoding='utf-8',errors='replace').read()) for f in files}
def scopes(s):
    # returns list of (pos, scope-path) changes; compute scope at each position via stack
    stack=[]; out=[]; pending=None
    tok=re.finditer(r'(namespace|struct|class)\s+(\w+)[^;{(]*\{|\{|\}',s)
    for m in tok:
        if m.group(1): stack.append(m.group(2))
        elif m.group(0)=='{': stack.append(None)
        else:
            if stack: stack.pop()
        out.append((m.end(),[x for x in stack if x]))
    return out
def scope_at(sc,pos):
    cur=[]
    for p,st in sc:
        if p>pos: break
        cur=st
    return cur
decl={}
for f,s in txt.items():
    sc=scopes(s)
    for m in re.finditer(r'HOOKKIT_(HOOK|HOOK_HANDLE|HOOK_WILD|HOOK_WILD_HANDLE|HOOK_BIND|NAMED_HOOK|NAMED_BIND_RAW|SITE_HOOK_HANDLE)\(\s*(\w+)\s*,\s*(0x[0-9A-Fa-f]+)',s):
        path=scope_at(sc,m.start())
        decl.setdefault(m.group(2),[]).append((path,int(m.group(3),16),m.group(1),os.path.relpath(f,root)))
res=[];amb=[]
for f,s in txt.items():
    for m in re.finditer(r'tx\.attach\(',s):
        i=m.end(); depth=1; j=i
        while depth:
            c=s[j]; depth+= c=='('; depth-= c==')'; j+=1
        for q in re.findall(r'([\w:]+)\{\}',s[i:j-1]):
            parts=q.split('::'); n=parts[-1]
            base=n[:-5] if n.endswith('_hook') and n[:-5] in decl else n
            cands=decl.get(base,[])
            if len(parts)>1:
                cands=[c for c in cands if parts[-2] in c[0]] or cands
            if len(cands)!=1: amb.append((q,[(c[0],hex(c[1])) for c in cands]))
            for c in cands[:1]: res.append({'name':q,'addr':c[1],'kind':c[2],'file':os.path.relpath(f,root)})
    for m in re.finditer(r'HOOKKIT_HOOK_BIND\(\s*(\w+)\s*,\s*(0x[0-9A-Fa-f]+)',s):
        res.append({'name':m.group(1),'addr':int(m.group(2),16),'kind':'HOOK_BIND','file':os.path.relpath(f,root)})
    for m in re.finditer(r'tx\.patchBytes\(reinterpret_cast<void\*>\((0x[0-9A-Fa-f]+)\),\s*(\w+)\.data\(\)',s):
        res.append({'name':'patchBytes '+m.group(2),'addr':int(m.group(1),16),'kind':'PATCH','file':os.path.relpath(f,root)})
    for m in re.finditer(r'tx\.forceWrite<[^>]*>\(\s*(0x[0-9A-Fa-f]+)\s*\+\s*(\d+)',s):
        res.append({'name':'forceWrite','addr':int(m.group(1),16)+int(m.group(2)),'kind':'PATCH','file':os.path.relpath(f,root)})
print('resolved',len(res)); print('ambiguous',amb)
json.dump(res,open(root+'/../cmp/aw.json','w'),indent=0)
for r in sorted(res,key=lambda r:r['addr']): print('%08X %-18s %-55s %s'%(r['addr'],r['kind'],r['name'][:55],r['file']))

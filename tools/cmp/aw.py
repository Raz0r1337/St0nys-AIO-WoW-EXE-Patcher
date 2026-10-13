import re,os,glob,json
root='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/awrepo'
files=[f for f in glob.glob(root+'/src/**/*.*',recursive=True)+glob.glob(root+'/include/**/*.*',recursive=True) if f.endswith(('.h','.cpp','.hpp'))]
txt={f:re.sub(r'//[^\n]*','',open(f,encoding='utf-8',errors='replace').read()) for f in files}
decl={}
for f,s in txt.items():
    for m in re.finditer(r'HOOKKIT_(HOOK|HOOK_HANDLE|HOOK_WILD|HOOK_WILD_HANDLE|HOOK_BIND|NAMED_HOOK|NAMED_BIND_RAW|SITE_HOOK_HANDLE)\(\s*(\w+)\s*,\s*(0x[0-9A-Fa-f]+)',s):
        decl.setdefault(m.group(2),[]).append((int(m.group(3),16),m.group(1),os.path.relpath(f,root)))
attached=[]
for f,s in txt.items():
    for m in re.finditer(r'tx\.attach\(',s):
        i=m.end(); depth=1; j=i
        while depth:
            c=s[j]; depth+= c=='('; depth-= c==')'; j+=1
        for n in re.findall(r'([\w:]+?)(?:_hook)?\{\}',s[i:j-1]):
            attached.append((n.split('::')[-1],os.path.relpath(f,root)))
# HOOKKIT_HOOK_BIND and BIND_RAW globals are bound statically (attached via StaticBinder?) - collect too
res=[]
miss=[]
for n,f in attached:
    if n in decl:
        for a,kind,df in decl[n]: res.append({'name':n,'addr':a,'kind':kind,'file':f})
    else: miss.append((n,f))
for f,s in txt.items():
    for m in re.finditer(r'HOOKKIT_HOOK_BIND\(\s*(\w+)\s*,\s*(0x[0-9A-Fa-f]+)',s):
        res.append({'name':m.group(1),'addr':int(m.group(2),16),'kind':'HOOK_BIND(static)','file':os.path.relpath(f,root)})
    for m in re.finditer(r'tx\.patchBytes\(reinterpret_cast<void\*>\((0x[0-9A-Fa-f]+)\),\s*(\w+)\.data\(\),\s*\w+\.size\(\)',s):
        name=m.group(2); mm=re.search(r'%s\s*=\s*\{([^}]*)\}'%name,s) or re.search(r'%s\s*\{([^}]*)\}'%name,s)
        n=len([x for x in mm.group(1).split(',') if x.strip()]) if mm else 0
        res.append({'name':'patchBytes '+name,'addr':int(m.group(1),16),'kind':'PATCH','len':n,'file':os.path.relpath(f,root)})
    for m in re.finditer(r'tx\.forceWrite<[^>]*>\(\s*(0x[0-9A-Fa-f]+)\s*\+\s*(\d+)',s):
        res.append({'name':'forceWrite','addr':int(m.group(1),16)+int(m.group(2)),'kind':'PATCH','len':4,'file':os.path.relpath(f,root)})
json.dump(res,open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/cmp/aw.json','w'),indent=0)
print('attached',len(attached),'resolved',len(res),'missing',miss)
from collections import Counter
print(Counter(r['kind'] for r in res))

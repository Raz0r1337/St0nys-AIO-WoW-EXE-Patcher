import re,glob,os,json
S='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/'
root=S+'hot/repo/WotLKExtensions'
files=[f for f in glob.glob(root+'/**/*.*',recursive=True) if f.endswith(('.cpp','.h','.hpp'))]
def strip(s):
    s=re.sub(r'/\*.*?\*/','',s,flags=re.S); return re.sub(r'//[^\n]*','',s)
T={f:strip(open(f,encoding='utf-8',errors='replace').read()) for f in files}
funcs={}
for f,s in T.items():
    for m in re.finditer(r'CLIENT_FUNCTION\(\s*(\w+)\s*,\s*(0x[0-9A-Fa-f]+)',s): funcs.setdefault(m.group(1),set()).add(int(m.group(2),16))
det=[];wr=[]
for f,s in T.items():
    rel=os.path.relpath(f,root)
    for m in re.finditer(r'CLIENT_DETOUR(?:_THISCALL)?(?:_NOARGS)?\(\s*(\w+)\s*,\s*(0x[0-9A-Fa-f]+|[\w:]+)',s):
        a=m.group(2)
        if a.startswith('0x'): det.append((int(a,16),m.group(1),rel))
        else:
            n=a.split('::')[-1]
            for v in funcs.get(n,[]) or []: det.append((v,m.group(1),rel))
            if n not in funcs:
                # constexpr symbol
                mm=None
                for s2 in T.values():
                    mm=re.search(r'%s\s*=\s*(0x[0-9A-Fa-f]+)'%re.escape(n),s2)
                    if mm: break
                if mm: det.append((int(mm.group(1),16),m.group(1),rel))
                else: print('?? unresolved',a,rel)
    for m in re.finditer(r'ClientDetours::Add\(\s*"([^"]+)"\s*,\s*&?([\w:]+)',s):
        n=m.group(2).split('::')[-1]
        vs=funcs.get(n)
        if vs:
            for v in vs: det.append((v,m.group(1),rel))
        else: print('?? add unresolved',m.group(2),rel)
    arrays={m.group(1):len([x for x in m.group(2).split(',') if x.strip()]) for m in re.finditer(r'uint8_t\s+(\w+)\s*\[\s*\d*\s*\]\s*=\s*\{([^}]*)\}',s)}
    for m in re.finditer(r'Util::(OverwriteUInt32AtAddress|SetByteAtAddress|OverwriteBytesAtAddress)\s*\(([^;]*)\)\s*;',s):
        fn,args=m.groups(); a=re.search(r'0x([0-9A-Fa-f]+)',args)
        if not a: print('?? noaddr',rel,args[:60]); continue
        addr=int(a.group(1),16)
        if fn=='OverwriteUInt32AtAddress': n=4
        elif fn=='SetByteAtAddress': n=1
        else:
            parts=[p.strip() for p in args.split(',')]
            if len(parts)==3 and parts[1] in arrays: n=arrays[parts[1]]
            elif len(parts)==3 and re.match(r'^(0x[0-9A-Fa-f]+|\d+)$',parts[2]): n=int(parts[2],0)
            elif len(parts)>=2 and 'sizeof' in args: n=8
            else: n=8; print('?? size',rel,args[:80])
        wr.append((addr,n,rel))
json.dump({'detours':det,'writes':wr},open(S+'cmp/hot.json','w'))
print('detours',len(det),'writes',len(wr))
aw=json.load(open(S+'cmp/aw.json'))
print('--- awesome hook span vs HoT byte writes')
for r in aw:
    for a,n,f in wr:
        if a<r['end'] and r['addr']<a+n: print('  ',r['name'],hex(r['addr']),'-',hex(r['end']),'<->',f,hex(a),n)
print('--- same function detoured by both (prologue hooks)')
for r in aw:
    for a,name,f in det:
        if r['addr']<=a<r['end'] or a<=r['addr']<a+5: print('   %08X aw:%-45s hot:%s (%s)'%(a,r['name'],name,f))

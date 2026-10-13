from lib import *
import pickle, os, re
xrefs,insn_starts,raw=pickle.load(open('xref.pkl','rb'))
MINE=['keyprop','globalsv','awesome','voicedll','areatrigger','swing','npcanim','spellanim','ghostattack','naked','forcereaction','mail','deadchat','follow','level101','raceclass','namecheck','maxchars']
rows=table()
ids_in_order=[]
src=open(PS1,encoding='utf-8',errors='replace').read()
for m in re.finditer(r"@\{ Id = '(\w+)'",src[src.index('$patches = @('):]): ids_in_order.append(m.group(1))
menu={i:n+1 for n,i in enumerate(ids_in_order)}
def pe_sections(d):
    e=struct.unpack_from('<I',d,0x3C)[0]; n=struct.unpack_from('<H',d,e+6)[0]; opt=struct.unpack_from('<H',d,e+20)[0]
    base=e+24+opt; secs=[]
    for k in range(n):
        s=base+40*k; name=d[s:s+8].rstrip(b'\0').decode(errors='replace')
        vs,va,rs,ro=struct.unpack_from('<IIII',d,s+8)
        secs.append((name,ro,0x400000+va,rs,vs))
    return secs
def mk_off2va(secs):
    def f(o):
        for n,ro,va,rs,vs in secs:
            if ro<=o<ro+rs: return va+o-ro
        return None
    return f
# my functions (original exe) : list of (id, range_off, range_len, fs_off, fe_off)
myfuncs=[]
for id,off,ob,uniq in rows:
    if id not in MINE: continue
    if off<0x400: myfuncs.append((id,off,len(ob),off,off+len(ob))); continue
    if all(c==0xCC for c in ob): fs,fe=off,off+len(ob)   # code cave
    else:
        fs=func_start(orig,off); fe=func_end(orig,off+len(ob))
        if fs is None: fs=max(off-0x40,0x400)
        if fe is None: fe=off+len(ob)+0x40
    myfuncs.append((id,off,len(ob),fs,fe))
    print(f'{menu[id]:>2} {id:14s} range f{off:X}+{len(ob)} VA {off2va(off):X}  func f{fs:X}-f{fe:X} (VA {off2va(fs):X}-{off2va(fe):X})')
print()
print('### A. other table rows writing into my functions / my rows writing into other rows functions')
for id,off,ln,fs,fe in myfuncs:
    for id2,off2,ob2,u2 in rows:
        if id2==id: continue
        a,b=off2,off2+len(ob2)
        if a<fe and b>fs:
            kind='OVERLAPS RANGE' if (a<off+ln and b>off) else 'same function'
            print(f'  {menu[id]} {id} func f{fs:X}-f{fe:X}  <->  {menu.get(id2)} {id2} writes f{off2:X}+{len(ob2)}  [{kind}]')
print()
print('### B. original branches landing strictly inside my ranges (not at start)')
for id,off,ln,fs,fe in myfuncs:
    if off<0x400: continue
    v=off2va(off)
    for t in range(v+1,v+ln):
        for s,m in xrefs.get(t,[]): print(f'  {menu[id]} {id}: SWEEP {m} from {s:X} -> {t:X}')
        for s,k in raw.get(t,[]):
            if s in insn_starts: print(f'  {menu[id]} {id}: RAW {k} from {s:X} -> {t:X}')
print()
print('### C. branches of OTHER patches new code into my functions (decode diff ranges of out/N.exe)')
targets_mine=[(id,off2va(fs),off2va(fe)) for id,off,ln,fs,fe in myfuncs if off>=0x400]
mdx=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for n in range(1,len(ids_in_order)+1):
    pid=ids_in_order[n-1]
    if pid in MINE: continue
    fn=f'{OUT}/{n}.exe'
    if not os.path.exists(fn): print('  missing',n); continue
    p=open(fn,'rb').read(); secs=pe_sections(p); o2v=mk_off2va(secs)
    m=min(len(p),len(orig)); i=0; ranges=[]
    while i<m:
        if orig[i]!=p[i]:
            j=i
            while j<m and orig[j]!=p[j]: j+=1
            ranges.append((i,j)); i=j
        else: i+=1
    if len(p)>len(orig): ranges.append((len(orig),len(p)))
    for a,b in ranges:
        if a==0x72DE20: continue  # watermark
        va=o2v(a)
        if va is None: continue
        # decode new bytes (merge adjacent ranges roughly by extending window a bit)
        for ins in mdx.disasm(p[a:b],va):
            if (ins.mnemonic.startswith('j') or ins.mnemonic=='call') and ins.op_str.startswith('0x'):
                t=int(ins.op_str,16)
                for id,fa,fb in targets_mine:
                    if fa<=t<fb: print(f'  {n} {pid} new code at {ins.address:X} ({ins.mnemonic} {ins.op_str}) -> into function of {menu[id]} {id} ({fa:X}-{fb:X})')
print()
print('### D. my new code branch targets vs other rows (function containing target)')
mytargets={'awesome':[0x4E5CB0,0x86C4E0,0x406D70,0x40B7D8,0x9DF248],'voicedll':[0x944B45,0x9DF248,0x40BA9B]}
for id,ts in mytargets.items():
    for t in ts:
        o=va2off(t)
        if o is None or o<0x400 or o>=0x5DD800: 
            # rdata target: check direct overlap
            for id2,off2,ob2,u2 in rows:
                if id2!=id and off2<=o<off2+len(ob2): print(f'  {id} target {t:X} written by {id2}')
            continue
        fs=func_start(orig,o); fe=func_end(orig,o)
        for id2,off2,ob2,u2 in rows:
            if id2==id: continue
            if off2<fe and off2+len(ob2)>fs: print(f'  {id} target {t:X} (func f{fs:X}-f{fe:X}) : row {menu.get(id2)} {id2} f{off2:X}+{len(ob2)}')

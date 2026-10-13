import re,struct,capstone
exec(open('global.py').read().split("# 3) branch-into-range")[0].replace("print(","(lambda *a,**k:None)("))
T0,T1=0x400,0x400+0x5dd3b3
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def func_start(fo):
    o=fo
    while o>T0 and not (d[o-1] in (0xCC,) and d[o] not in (0xCC,)): o-=1
    return o
print('== .text ranges grouped by function (file offset of function start) ==')
groups={}
for idn,off,n,own in ents:
    if idn in ('pe','watermark') or not (T0<=off<T1): continue
    fs=func_start(off)
    groups.setdefault(fs,set()).add(idn)
for fs in sorted(groups):
    if len(groups[fs])>1: print('  func 0x%06X (VA %08X): %s'%(fs,fs+0x400C00,sorted(groups[fs])))
print('  (functions touched by more than one patch listed above; total functions:',len(groups),')')
# caves: must be free (CC or 00) in original and no branch target
caves={'afk':(0x54AD02,24),'voicedll':(0x543F45,27),'sliders':(0x528AED,18),'mouse':(0x528AA2,25),'textcave':(0x5DD7B3,77),'awesome-cave?':(0xE50B0,68)}
rd={'sound':(0x6B3F80,6),'sliders-table':(0x6B3E80,36)}
print('\n== cave content in original ==')
for k,(o,n) in caves.items():
    bs=set(d[o:o+n]); print('  %-14s 0x%06X +%d bytes: %s'%(k,o,n,' '.join('%02X'%b for b in sorted(bs))))
for k,(o,n) in rd.items():
    bs=set(d[o:o+n]); print('  %-14s 0x%06X +%d bytes: %s'%(k,o,n,' '.join('%02X'%b for b in sorted(bs))))
text=d[T0:T1]
def targets_into(lo,hi):
    out=[]
    for i in range(len(text)-6):
        b=text[i]; src=T0+i
        if b in (0xE8,0xE9): t=src+5+struct.unpack_from('<i',text,i+1)[0]
        elif b==0x0F and 0x80<=text[i+1]<=0x8F: t=src+6+struct.unpack_from('<i',text,i+2)[0]
        elif 0x70<=b<=0x7F or b==0xEB: t=src+2+struct.unpack_from('<b',text,i+1)[0]
        else: continue
        if lo<=t<hi:
            ok=False
            for k in (0x80,0x60,0x40,0x30,0x20,0x10):
                if src-k<T0: continue
                if src in {x.address for x in md.disasm(d[src-k:src+8],src-k)}: ok=True; break
            if ok: out.append((src,t))
    return out
print('\n== branches into caves (instruction-boundary sources) ==')
for k,(o,n) in caves.items():
    print('  %-14s %s'%(k,[('0x%X'%s,'0x%X'%t) for s,t in targets_into(o,o+n)] or 'none'))
# absolute pointer refs into caves and rdata paddings
print('\n== absolute dword refs (whole file) into caves/paddings ==')
for k,(o,n) in list(caves.items())+list(rd.items()):
    sn,va=sec_of(o); hits=[]
    if va:
        for v in range(va,va+n):
            p=struct.pack('<I',v); j=d.find(p)
            while j>=0: hits.append('0x%X->%08X'%(j,v)); j=d.find(p,j+1)
    print('  %-14s %s'%(k,hits[:8] or 'none'))
# awesome: callers of 0x4E5CB0 and 0x4DCCF0, 0x40B7D0
print('\n== callers (rel32) of awesome-related functions ==')
for tgt in (0x4E5CB0,0x4DCCF0,0x40B7D0,0x406D70):
    hits=[]
    for i in range(len(text)-5):
        if text[i] in (0xE8,0xE9):
            if 0x401005+i+struct.unpack_from('<i',text,i+1)[0]==tgt: hits.append('%08X'%(0x401000+i))
    p=struct.pack('<I',tgt); j=d.find(p); ab=[]
    while j>=0: ab.append('0x%X'%j); j=d.find(p,j+1)
    print('  %08X rel: %s abs: %s'%(tgt,hits,ab))

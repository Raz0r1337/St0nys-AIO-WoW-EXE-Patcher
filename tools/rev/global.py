import re,struct,capstone
SRC='/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1'
W='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
d=open(W,'rb').read()
s=open(SRC,encoding='ascii').read()
a=s.rindex('# BEGIN ORIGINAL-BYTES'); z=s.rindex('# END ORIGINAL-BYTES')
ents=[]
for line in s[a:z].splitlines():
    m=re.match(r'^([a-z0-9]+);([0-9A-F]+);([0-9A-F]*);(\d)$',line.strip())
    if m: ents.append((m.group(1),int(m.group(2),16),len(m.group(3))//2,m.group(4)=='1'))
ids=[]
for e in ents:
    if e[0] not in ids: ids.append(e[0])
print('ids in table:',len(ids))
# 1) shared ranges
print('\n== shared ranges (flag 0) ==')
for idn,off,n,own in ents:
    if not own:
        others=[(j,hex(o),m) for j,o,m,_ in ents if j!=idn and o<off+n and o+m>off]
        print('  %-14s 0x%06X +%-4d shared with %s'%(idn,off,n,others))
# verify flags: recompute overlaps
print('\n== overlap check (independent of flags) ==')
for i,(idn,off,n,own) in enumerate(ents):
    for j,(idn2,off2,n2,own2) in enumerate(ents):
        if j<=i or idn==idn2: continue
        if off<off2+n2 and off2<off+n:
            print('  OVERLAP %s 0x%X+%d  <->  %s 0x%X+%d'%(idn,off,n,idn2,off2,n2))
# 2) section helpers
SECS=[('.text',0x1000,0x5dd3b3,0x400,0x5dd400),('.rdata',0x5df000,0xd6679,0x5dd800,0xd6800),('.data',0x6b6000,0x31a508,0x6b4000,0x78e00),('.zdata',0x9d1000,0x1000,0x72ce00,0x1000),('.tls',0x9d2000,0x19,0x72de00,0x200),('.rsrc',0x9d3000,0x29ad0,0x72e000,0x29c00)]
def sec_of(fo):
    for n,va,vs,ra,rs in SECS:
        if ra<=fo<ra+rs: return n,va+0x400000+fo-ra
    return 'hdr',None
print('\n== ranges by section ==')
for idn,off,n,own in ents:
    sn,va=sec_of(off)
    extra=''
    if sn=='.text' and va is not None and off-0x400+0x1000 >= 0x5dd3b3: extra=' (beyond .text VirtualSize)'
    if sn=='.rdata' and off-0x5dd800 >= 0xd6679: extra=' (beyond .rdata VirtualSize)'
    print('  %-14s 0x%06X +%-4d %-7s VA %s%s'%(idn,off,n,sn,('%08X'%va) if va else '-',extra))
# 3) branch-into-range scan over .text (original), excluding branches from inside the same patch's ranges
T0,T1=0x400,0x400+0x5dd3b3
text=d[T0:T1]
rngs=[(idn,off,off+n) for idn,off,n,own in ents if T0<=off<T1 and idn not in ('pe','watermark')]
def hit(t):
    for idn,a_,b_ in rngs:
        if a_<t<b_: return (idn,a_,b_)   # strictly inside
    return None
cands=[]
for i in range(len(text)-6):
    b=text[i]; src=T0+i
    if b in (0xE8,0xE9):
        t=src+5+struct.unpack_from('<i',text,i+1)[0]
    elif b==0x0F and 0x80<=text[i+1]<=0x8F:
        t=src+6+struct.unpack_from('<i',text,i+2)[0]
    elif 0x70<=b<=0x7F or b==0xEB:
        t=src+2+struct.unpack_from('<b',text,i+1)[0]
    else: continue
    h=hit(t)
    if h and not (h[1]<=src<h[2]): cands.append((src,t,h))
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
print('\n== original branches landing strictly inside a patched range (file offsets) ==')
real=0
for src,t,h in cands:
    # is src an instruction boundary? sync decode from several starts
    ok=False
    for k in (0x80,0x60,0x40,0x30,0x20,0x10):
        if src-k<T0: continue
        addrs={i.address for i in md.disasm(d[src-k:src+8],src-k)}
        if src in addrs: ok=True; break
    if ok:
        real+=1
        print('  from 0x%06X (VA %08X) -> 0x%06X (VA %08X) inside %s 0x%X..0x%X'%(src,src+0x400C00,t,t+0x400C00,h[0],h[1],h[2]))
print('  candidates:',len(cands),'on instruction boundary:',real)

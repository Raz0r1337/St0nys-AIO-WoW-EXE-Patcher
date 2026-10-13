# Build branch-target index over .text of the ORIGINAL exe (linear sweep from each int3-run end) + raw pattern scan
from lib import *
import pickle, time
fo,va0,rs,vs=SECS['.text']
d=orig
start=fo; end=fo+vs
t=time.time()
md2=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md2.detail=False
xrefs={}   # target VA -> list of (src VA, mnemonic)
insn_starts=set()
# linear sweep over entire .text, resync at CC runs
o=start
while o<end:
    if d[o]==0xCC:
        o+=1; continue
    # disassemble until the next CC run
    q=o
    while q<end and not (d[q]==0xCC and d[q+1]==0xCC): q+=1
    for i in md2.disasm(d[o:q],off2va(o)):
        insn_starts.add(i.address)
        if i.mnemonic.startswith('j') or i.mnemonic=='call' or i.mnemonic.startswith('loop'):
            op=i.op_str
            if op.startswith('0x'):
                try: xrefs.setdefault(int(op,16),[]).append((i.address,i.mnemonic))
                except: pass
    o=q
print('sweep done',time.time()-t,len(xrefs),len(insn_starts))
# raw pattern scan: every byte offset as potential E8/E9 rel32, 0F8x rel32, 7x/EB rel8
raw={}  # target VA -> list of (src VA, kind)
for o in range(start,end):
    b=d[o]
    if b in (0xE8,0xE9) and o+5<=end:
        rel=struct.unpack_from('<i',d,o+1)[0]; tgt=off2va(o)+5+rel
        raw.setdefault(tgt,[]).append((off2va(o),'E8' if b==0xE8 else 'E9'))
    elif b==0x0F and 0x80<=d[o+1]<=0x8F and o+6<=end:
        rel=struct.unpack_from('<i',d,o+2)[0]; tgt=off2va(o)+6+rel
        raw.setdefault(tgt,[]).append((off2va(o),'0F%02X'%d[o+1]))
    elif (0x70<=b<=0x7F or b==0xEB) and o+2<=end:
        rel=struct.unpack_from('<b',d,o+1)[0]; tgt=off2va(o)+2+rel
        raw.setdefault(tgt,[]).append((off2va(o),'%02X'%b))
print('raw done',time.time()-t)
pickle.dump((xrefs,insn_starts,raw),open('xref.pkl','wb'))

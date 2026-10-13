from lib import *
import re
def fend(f):
    a=f+1
    while True:
        o=off(a)
        if d[o-1]==0xcc and d[o]!=0xcc and d[o-2]==0xcc: return a
        a+=1
M=[0x834900,0x834940,0x834990,0x8349e0,0x834d90,0x834dc0,0x834f60,0x8350a0,0x835280,0x8353d0,0x8355d0,0x835750,0x4e2730,0x81e400,0x873ca0,0x7a9160,0x8a38b0,0x872900,0x790440,0x7b0f10,0x8248c0,0x824380,0x824550,0x81f800]
F=set(M)
for t in M:
    for c in calls.get(t,[]): F.add(fstart(c))
F|={0x4e3a20,0x780cd0,0x616bc0,0x9363c0,0x960070,0x7b3f30,0x7c3db0,0x7d4f40,0x81f1d0,0x821100,0x81fb10,0x823130,0x821a20,0x831af0,0x82be60,0x828a00}
res=[]
for f in sorted(F):
    e=fend(f)
    for i in dis(f,e-f,out=False):
        if re.search(r'\[[^\]]*\+ 0x14\]',i.op_str):
            res.append((f,i.address,i.mnemonic,i.op_str))
print(len(F),'functions')
cur=None
for f,a,m,o in res:
    if f!=cur: print('## func %x'%f); cur=f
    print('   %08X %s %s'%(a,m,o))

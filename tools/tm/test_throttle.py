import sys,os,struct,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu import Emu
import h
from unicorn.x86_const import *
ORIG=bytes(h.d)
print('sha256 original',hashlib.sha256(ORIG).hexdigest().upper())
def run(data,label):
    e=Emu(data)
    e.stub(0x433830,lambda em,a: 0,1,0)       # name registration (cdecl)
    e.stub(0x670210,lambda em,a: 0,0,0)       # inner hash ctor (thiscall, no args)
    out=[]
    for i in range(15):
        ctor=0x675C80+0x130*i
        call=h.callers(ctor)[0]
        # initializer start: scan back to the int3 padding
        s=call
        while h.d[h.v2f(s)-1]!=0xCC: s-=1
        obj=None
        def stop(em): em.mu.emu_stop()
        e.watch_at(call+5,stop)
        e.mu.reg_write(UC_X86_REG_ESP,0x200F0000)
        e.mu.emu_start(s,0x31000000,count=100000)
        # ecx was loaded by "mov ecx, obj" right before the call
        objva=struct.unpack_from('<I',h.d,h.v2f(call)-4)[0]
        name=h.cstr(struct.unpack_from('<I',h.d,h.v2f(call)-15+1)[0]) if False else None
        lim=e.r32(objva+0x48)
        out.append((i,hex(s),hex(objva),lim))
    return out
fn=[]
for i in range(15):
    call=h.callers(0x675C80+0x130*i)[0]
    import re
    seg=h.d[h.v2f(call)-0x30:h.v2f(call)]
    m=[x for x in re.finditer(rb'\x68(....)',seg,re.S)]
    names=[h.cstr(struct.unpack('<I',x.group(1))[0]) for x in m]
    fn.append([n.decode() for n in names if n and n.endswith(b'.wdb')][0])
o=run(ORIG,'orig')
# patched: apply Nr. 6 bytes
P=bytearray(ORIG)
for i in range(15):
    off=(0x675C80+0x130*i+0x6E)-0x400C00
    assert P[off]==0x56 and P[off-1]==0x89 and P[off+1]==0x48, (i,P[off-1:off+2].hex())
    P[off]=0x4E
p=run(bytes(P),'patched')
for (i,s,obj,lim),(_,_,_,lim2),n in zip(o,p,fn):
    print('%2d %-20s init %s obj %s  Original [obj+48h]=%-4d (=%d/min)  mit Nr.6=%d'%(i,n,s,obj,lim,lim*2,lim2))

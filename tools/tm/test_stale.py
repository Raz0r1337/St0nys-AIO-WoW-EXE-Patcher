import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu2 import *
O=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
P=bytearray(open(sys.argv[1],"rb").read()) if len(sys.argv)>1 else bytearray(O)
if len(sys.argv)<=1: P[0x81E548-0x400C00]=0xEB
H=0x30000000; SC=H+0x1000; GRID=H+0x10000; L=H+0x2000; LT=H+0x3000; SPH=H+0x4000
def run(data,stamp):
    e=Emu2(bytes(data))
    for nm,va,vs,rs,ro,ch in sections(bytes(data)):
        if va>0xDD3000:
            try: e.mu.mem_map(va,(vs+0xFFF)&~0xFFF)
            except UcError: pass
            e.mu.mem_write(va,bytes(data[ro:ro+min(rs,vs)]))
    e.w32(0x9DF238,H+0x5000); e.stub(H+0x5000,lambda em,a: H+0x40000,4,16)
    e.mu.mem_write(H,b"\0"*0x100000); e.mu.mem_write(0x88CE30,bytes.fromhex("DD442404D9FCC3"))
    e.w32(SC+0x14,5); e.w32(SC+0x20,0); e.w32(SC+0x24,GRID)
    for c in range(64*64): e.w32(GRID+4*c,LT)
    e.w32(LT,SC); e.w32(LT+4,stamp); e.w32(LT+8,1); e.mu.mem_write(LT+0xC,struct.pack('<3f',1,2,3)); e.w32(LT+0x60,1)
    e.mu.mem_write(SPH,struct.pack('<4f',0,0,0,5))
    e.call(0x834900,(SC,SPH),regs={UC_X86_REG_ECX:L})
    e.call(0x81E400,(L,),regs={UC_X86_REG_ECX:SC})
    return e.r32(L+0xA4), e.r32(LT+0x60)
for nm,data in (('original',O),('gepatcht',P)):
    for st in (5,4):
        n,en=run(data,st)
        print('%-9s stempel %s: Lichter=%d, Licht aktiv=%d'%(nm,'aktuell ' if st==5 else 'veraltet',n,en))

import sys,struct
sys.path.insert(0,'.')
from cif import *
from unicorn import *
from unicorn.x86_const import *
SECS=[(0x401000,0x5dd3b3,0x400,0x5dd400),(0x9DF000,0xd6679,0x5dd800,0xd6800),(0xAB6000,0x31a508,0x6b4000,0x78e00)]
# test data: id -> (class, subclass, display, invtype, material, sheath)
CACHE={50001:(2,7,40001,13,1,3), 1001:(4,1,55555,5,6,0)}   # 1001 also in DBC with other values
DBC={1001:(4,2,11111,7,5,1), 1002:(2,4,22222,17,1,2)}
EXP_C=lambda i:CACHE.get(i)
def expect(i,field):
    k={'class':0,'subclass':1,'display':2,'inv':3,'material':4,'sheath':5}[field]
    if i in CACHE: return CACHE[i][k]
    if i in DBC: return DBC[i][k]
    return 0
class Emu:
    def __init__(s,data):
        mu=s.mu=Uc(UC_ARCH_X86,UC_MODE_32)
        for vaa,vs,ra,rs in SECS:
            size=(vs+0xfff)&~0xfff; mu.mem_map(vaa,size); mu.mem_write(vaa,data[ra:ra+min(rs,vs)])
        mu.mem_map(0x100000,0x20000); mu.mem_map(0x200000,0x40000)
        s.heap=0x200000
        # DBC tables
        lo,hi=1000,1010
        rows=s.alloc(4*(hi-lo+1))
        for i,(c,sc,dsp,inv,mat,sh) in DBC.items():
            r=s.alloc(0x20); mu.mem_write(r,struct.pack('<8I',i,c,sc,0,mat,dsp,inv,sh))
            mu.mem_write(rows+4*(i-lo),struct.pack('<I',r))
        mu.mem_write(0xAD3D5C,struct.pack('<I',lo)); mu.mem_write(0xAD3D58,struct.pack('<I',hi)); mu.mem_write(0xAD3D6C,struct.pack('<I',rows))
        s.crec={}
        for i,(c,sc,dsp,inv,mat,sh) in CACHE.items():
            r=s.alloc(0x200); mu.mem_write(r+4,struct.pack('<II',c,sc)); mu.mem_write(r+0x10,struct.pack('<I',dsp))
            mu.mem_write(r+0x28,struct.pack('<I',inv)); mu.mem_write(r+0x194,struct.pack('<II',mat,sh)); s.crec[i]=r
        s.calls=[]; s.iconarg=None
        mu.hook_add(UC_HOOK_CODE,s.hook)
    def alloc(s,n):
        p=s.heap; s.heap+=(n+15)&~15; return p
    def r32(s,a): return struct.unpack('<I',s.mu.mem_read(a,4))[0]
    def hook(s,mu,addr,size,u):
        if addr==0x67CA30:
            esp=mu.reg_read(UC_X86_REG_ESP); ret=s.r32(esp); i=s.r32(esp+4)
            assert mu.reg_read(UC_X86_REG_ECX)==0xC5D828, 'bad cache this'
            s.calls.append(i)
            mu.reg_write(UC_X86_REG_EAX,s.crec.get(i,0)); mu.reg_write(UC_X86_REG_ESP,esp+4+0x14); mu.reg_write(UC_X86_REG_EIP,ret)
        elif addr==0x70A910:   # icon path from display id (cdecl)
            esp=mu.reg_read(UC_X86_REG_ESP); s.iconarg=s.r32(esp+4)
            mu.reg_write(UC_X86_REG_EAX,0x12345678); mu.reg_write(UC_X86_REG_ESP,esp+4); mu.reg_write(UC_X86_REG_EIP,s.r32(esp))
    def regs(s,**kw):
        m={'eax':UC_X86_REG_EAX,'ebx':UC_X86_REG_EBX,'ecx':UC_X86_REG_ECX,'edx':UC_X86_REG_EDX,'esi':UC_X86_REG_ESI,'edi':UC_X86_REG_EDI,'ebp':UC_X86_REG_EBP,'esp':UC_X86_REG_ESP}
        for k,v in kw.items(): s.mu.reg_write(m[k],v)
    def get(s,r):
        return s.mu.reg_read({'eax':UC_X86_REG_EAX,'ebx':UC_X86_REG_EBX,'esi':UC_X86_REG_ESI,'edi':UC_X86_REG_EDI,'ebp':UC_X86_REG_EBP,'esp':UC_X86_REG_ESP}[r])

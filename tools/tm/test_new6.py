from emu import *
from patches2 import P
X=bytes(apply(ORIG,P['mirrorfix']+P['wmocube']))
def cstr(E,a):
    s=b''
    while True:
        c=bytes(E.mu.mem_read(a,1))
        if c==b'\0': return s.decode()
        s+=c; a+=1
# --- Mirror: Aufruf ueber die gepatchte Aufrufstelle simulieren -> direkt Stub mit esi=Einheit rufen
E=Emu(X); log=[]
E.stub(0x4F16C0,lambda E,a: log.append(('free',hex(a[0]))) or 0,1,0)       # cdecl
E.stub(0x4F0980,lambda E,a: log.append(('alloc',)) or 0x55AA55AA,0,0)
U=0x30005000
for old in (0x12345678,0):
    log.clear(); E.w32(U+0xB4C,old)
    r,dsp=E.call(0x86BF10,(),regs={UC_X86_REG_ESI:U,UC_X86_REG_EBX:0x11111111,UC_X86_REG_EDI:0x33333333})
    print('old=%x'%old,log,'ret=%x'%r,'slot=%x'%E.r32(U+0xB4C),'esp delta',dsp,'esi ok',E.reg(UC_X86_REG_ESI)==U)
# --- SafeOpen: Datei fehlt -> ErrorCube
for avail in ({'Spells\\ErrorCube.mdx'},{'world\\x.wmo','Spells\\ErrorCube.mdx'},set()):
    E=Emu(X); calls=[]
    def op(E,a):
        n=cstr(E,a[0]); calls.append(n)
        if n in avail: E.w32(a[1],0xF11E); return 1
        return 0
    E.stub(0x424F80,op,2,8)                    # stdcall
    E.stub(0x5EEB70,lambda E,a: 0,0,0)         # Log
    E.stub(0x772AA0,lambda E,a: calls.append('FATAL') or 0,0,0)
    E.mu.mem_write(0x30006000,b'world\\x.wmo\0'); H=0x30006100; E.w32(H,0)
    r,dsp=E.call(0x7BD480,(0x30006000,H,1))
    print('avail',sorted(avail),'ret',r,'handle %x'%E.r32(H),'opens',len(calls),'last',calls[-1],'fatal' in calls or 'FATAL' in calls,'esp',dsp)

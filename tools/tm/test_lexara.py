import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu2 import *
D=open(sys.argv[1],'rb').read()
fails=0
def ok(c,m):
    global fails; print(('OK   ' if c else 'FAIL ')+m); fails+= (not c)
e=Emu2(D); H=0x30000000; log=[]
def lla(em,a):
    s=bytes(em.mu.mem_read(a[0],32)).split(b'\0')[0].decode(); log.append(('LoadLibraryA',s)); return 0x12340000
e.w32(0x9DF248,H+0x100); e.stub(H+0x100,lla,1,4)
e.stub(0x76E490,lambda em,a: log.append(('cookie',)) ,0,0)
# stop when reaching __tmainCRTStartup
e.stub(0x40BA9B,lambda em,a: log.append(('crt',)),0,0)
voice='voicedll' in sys.argv[2:] 
mu=e.mu
sp=0x200F0000; mu.mem_write(sp-4,struct.pack('<I',0x31000000)); sp-=4
regs={UC_X86_REG_EBX:0x11111111,UC_X86_REG_ESI:0x22222222,UC_X86_REG_EDI:0x33333333,UC_X86_REG_EBP:0x44444444}
for r,v in regs.items(): mu.reg_write(r,v)
mu.reg_write(UC_X86_REG_ESP,sp)
mu.emu_start(0x401000,0x31000000,count=2000)
print(log)
order=[x[0] if x[0]!='LoadLibraryA' else x[1] for x in log]
exp=['Lexara.dll','cookie']+(['voice.dll'] if voice else [])+['crt']
ok(order==exp,'order: '+' -> '.join(order))
ok(mu.reg_read(UC_X86_REG_ESP)==sp+4,'stack balanced')
ok(all(mu.reg_read(r)==v for r,v in regs.items()),'ebx/esi/edi/ebp preserved')
sys.exit(1 if fails else 0)

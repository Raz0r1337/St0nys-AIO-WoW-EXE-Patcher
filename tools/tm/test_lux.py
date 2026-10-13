# Emulation des Startcodes mit Lux-Lader (Nr. 31), optional mit wow_optimize (27),
# Lexara (30) und voice.dll (32). Aufruf: test_lux.py <exe> [wowoptimize] [lexara] [lux] [voicedll]
import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu2 import *
D=open(sys.argv[1],'rb').read()
fails=0
def ok(c,m):
    global fails; print(('OK   ' if c else 'FAIL ')+m); fails+=(not c)
e=Emu2(D); H=0x30000000; log=[]
def rd(em,a):
    raw=bytes(em.mu.mem_read(a,40)); return raw.split(b'\0')[0].decode()
def lla(em,a): log.append(('LoadLibraryA',rd(em,a[0]))); return 0x12340000
def ct(em,a): log.append(('CreateThread',a)); return 0x5555
def ch(em,a): log.append(('CloseHandle',a[0])); return 1
def sl(em,a): log.append(('Sleep',a[0])); return 0
for k,(slot,fn,n) in enumerate(((0x9DF248,lla,1),(0x9DF338,ct,6),(0x9DF124,ch,1),(0x9DF264,sl,1))):
    stub=H+0x100+0x100*k
    e.w32(slot,stub); e.stub(stub,fn,n,4*n)
e.stub(0x7755F0,lambda em,a: log.append(('init',)),0,0)
e.stub(0x5EEB70,lambda em,a: log.append(('thunk',)),0,0)
e.stub(0x40BA9B,lambda em,a: log.append(('crt',)),0,0)
mu=e.mu
sp=0x200F0000; mu.mem_write(sp-4,struct.pack('<I',0x31000000)); sp-=4
regs={UC_X86_REG_EBX:0x11111111,UC_X86_REG_ESI:0x22222222,UC_X86_REG_EDI:0x33333333,UC_X86_REG_EBP:0x44444444}
for r,v in regs.items(): mu.reg_write(r,v)
mu.reg_write(UC_X86_REG_ESP,sp)
mu.emu_start(0x401000,0x31000000,count=5000)
names=[x[0] if x[0]!='LoadLibraryA' else x[1] for x in log]
f=sys.argv[2:]
wo,lex,lux,voice=('wowoptimize' in f),('lexara' in f),('lux' in f),('voicedll' in f)
exp=(['Lexara.dll'] if lex else [])+(['CreateThread','CloseHandle'] if wo else [])+['init']+(['LuxShoulderCam.dll'] if lux else ['thunk'])+(['voice.dll'] if voice else [])+['crt']
ok(names==exp,'start: '+' -> '.join(names))
ok(mu.reg_read(UC_X86_REG_EIP)==0x31000000,'start: zurueck beim Aufrufer')
ok(mu.reg_read(UC_X86_REG_ESP)==sp+4,'start: stack balanced')
ok(all(mu.reg_read(r)==v for r,v in regs.items()),'start: ebx/esi/edi/ebp preserved')
sys.exit(1 if fails else 0)

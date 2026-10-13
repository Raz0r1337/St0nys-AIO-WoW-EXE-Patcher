# Emulation des wow_optimize-Laders (Startpfad + Thread), optional mit Lexara/voice.dll.
import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu2 import *
D=open(sys.argv[1],'rb').read()
fails=0
def ok(c,m):
    global fails; print(('OK   ' if c else 'FAIL ')+m); fails+=(not c)
e=Emu2(D); H=0x30000000; log=[]; thr={}
def rd(em,a): return bytes(em.mu.mem_read(a,40)).split(b'\0')[0].decode()
def lla(em,a): log.append(('LoadLibraryA',rd(em,a[0]))); return 0x12340000
def ct(em,a): thr['start']=a[2]; thr['param']=a[3]; log.append(('CreateThread',a)); return 0x5555
def ch(em,a): log.append(('CloseHandle',a[0])); return 1
def sl(em,a): log.append(('Sleep',a[0])); return 0
for slot,fn,n in ((0x9DF248,lla,1),(0x9DF338,ct,6),(0x9DF124,ch,1),(0x9DF264,sl,1)):
    stub=H+0x100+0x10*len(log)+n*0x40+slot%0x1000
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
lex='lexara' in sys.argv[2:]; voice='voicedll' in sys.argv[2:]
exp=(['Lexara.dll'] if lex else [])+['CreateThread','CloseHandle','init','thunk']+(['voice.dll'] if voice else [])+['crt']
ok(names==exp,'start: '+' -> '.join(names))
ct_args=[x for x in log if x[0]=='CreateThread']
ok(bool(ct_args) and ct_args[0][1][0]==0 and ct_args[0][1][1]==0 and ct_args[0][1][4]==0 and ct_args[0][1][5]==0,'CreateThread(NULL,0,proc,NULL,0,NULL)')
ok(('CloseHandle',0x5555) in log,'CloseHandle(thread handle)')
ok(mu.reg_read(UC_X86_REG_ESP)==sp+4,'start: stack balanced')
ok(all(mu.reg_read(r)==v for r,v in regs.items()),'start: ebx/esi/edi/ebp preserved')
# Thread-Prozedur
log.clear()
r,delta=e.call(thr['start'],args=(thr['param'],))
names=[x for x in log]
ok(names==[('Sleep',3000),('LoadLibraryA','wow_optimize.dll')],'thread: '+repr(names))
ok(r==0,'thread: returns 0')
ok(delta==8,'thread: ret 4 (stack delta %d)'%delta)
ok(all(mu.reg_read(rg)==v for rg,v in {UC_X86_REG_EBX:0x11111111,UC_X86_REG_ESI:0x22222222,UC_X86_REG_EDI:0x33333333,UC_X86_REG_EBP:0x44444444}.items()),'thread: ebx/esi/edi/ebp preserved')
sys.exit(1 if fails else 0)

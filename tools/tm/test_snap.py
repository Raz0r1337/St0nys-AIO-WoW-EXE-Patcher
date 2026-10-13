import sys,os,struct,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu2 import *
D=open(sys.argv[1],'rb').read()
fails=0
def ok(c,msg):
    global fails
    print(('OK   ' if c else 'FAIL ')+msg)
    if not c: fails+=1
H=0x30000000
f2u=lambda f: struct.unpack('<I',struct.pack('<f',f))[0]
u2f=lambda u: struct.unpack('<f',struct.pack('<I',u))[0]
def run(vals,parsed,height,font,cw=0x027F):
    e=Emu2(D); e.mu.mem_write(H,b'\0'*0x10000)
    info=H+0x100
    for k,v in enumerate(vals): e.w32(info+0x18+4*k,f2u(v))
    e.w32(info+0x10,f2u(99.25)); e.w32(info+0x28,f2u(7.75))
    got={}
    def orig(em):
        mu=em.mu; ebp=mu.reg_read(UC_X86_REG_EBP)
        got['args']=[em.r32(ebp+8+4*k) for k in range(5)]
        r=em.r32(ebp+4); old=em.r32(ebp)
        mu.reg_write(UC_X86_REG_ESP,ebp+8); mu.reg_write(UC_X86_REG_EBP,old); mu.reg_write(UC_X86_REG_EIP,r)
        mu.reg_write(UC_X86_REG_EAX,0xABCD0000|parsed)
    e.watch_at(0x6C0E86,orig)
    e.mu.reg_write(UC_X86_REG_FPCW,cw)
    sw0=e.mu.reg_read(UC_X86_REG_FPSW)
    args=(H+0x50,info,f2u(height),f2u(1.0),f2u(font))
    r,dsp=e.call(0x6C0E80,args)
    out=[u2f(e.r32(info+0x18+4*k)) for k in range(4)]
    side=(e.r32(info+0x10)==f2u(99.25) and e.r32(info+0x28)==f2u(7.75))
    fp=(e.mu.reg_read(UC_X86_REG_FPCW)==cw and ((e.mu.reg_read(UC_X86_REG_FPSW)>>11)&7)==((sw0>>11)&7))
    regs=(e.reg(UC_X86_REG_ESI)==0x22222222 and e.reg(UC_X86_REG_EBX)==0x11111111 and e.reg(UC_X86_REG_EDI)==0x33333333 and e.reg(UC_X86_REG_EBP)==0x44444444)
    return out,r,dsp,got.get('args'),list(args),side,fp,regs
fl=lambda x: math.floor(x+0.5)
cases=[([12.4,0.3,-2.5,3.5],1,14.0,12.0),([7.5,20.49,0.5,-0.49],1,10.0,12.0),([0.0,-3.0,100.5,-100.5],1,9.0,12.0),([16.6,16.6,1.2,1.7],1,12.0,12.0),([16.6,16.6,1.2,1.7],0,14.0,12.0)]
for vals,parsed,h,font in cases:
    out,r,dsp,ga,args,side,fp,regs=run(vals,parsed,h,font)
    if parsed and h!=font:
        exp=[max(fl(vals[0]),1),max(fl(vals[1]),1),fl(vals[2]),fl(vals[3])]
    else: exp=[struct.unpack('<f',struct.pack('<f',v))[0] for v in vals]
    ok(out==exp and r==(0xABCD0000|parsed) and dsp==4 and ga==args and side and fp and regs,
       'parsed=%d hoehe=%s schrift=%s: %s -> %s (erwartet %s), Rueckgabe/Stack/FPU/Register ok=%s'%(parsed,h,font,vals,out,exp,(r==(0xABCD0000|parsed),dsp,ga==args,side,fp,regs)))
# with game-like single-precision control word
out,r,dsp,ga,args,side,fp,regs=run([12.4,0.3,-2.5,3.5],1,14.0,12.0,cw=0x007F)
ok(out==[12,1,-2,4] and fp,'einfache Genauigkeit (FPU-CW 0x007F): %s, CW wiederhergestellt'%out)
e=Emu2(D); b=bytes(e.mu.mem_read(0x6C0E80,6)); ok(b[0]==0xE9 and b[5]==0x90,'Hook 6C0E80: %s'%b.hex())
print('FAILS',fails)

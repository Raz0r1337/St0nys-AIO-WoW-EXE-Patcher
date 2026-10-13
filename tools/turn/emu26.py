import sys, struct, itertools
sys.path.insert(0,'ml'); sys.path.insert(0,'turn')
from h import *
from build26 import build, START
from unicorn import *
from unicorn.x86_const import *
TEXT_VA=0x401000; TEXT_SZ=0x5DD000
def make_image(variant):
    img=bytearray(d[0x400:0x400+TEXT_SZ])
    def put(va,b): img[va-TEXT_VA:va-TEXT_VA+len(b)]=bytes(b)
    if variant=='robinsch': put(0x73E3C9,[0xEB])
    if variant=='st0ny': put(START,build())
    # stubs
    put(0x71DE90,[0xA1,0x00,0x00,0x30,0x10,0xC3])   # mov eax,[0x10300000]; ret
    put(0x73AC30,[0xC2,0x08,0x00])                 # ret 8
    return bytes(img)
IMGS={v:make_image(v) for v in ('orig','robinsch','st0ny')}
def run(variant, mflags, aflags, cur, can, player):
    mu=Uc(UC_ARCH_X86,UC_MODE_32)
    mu.mem_map(TEXT_VA,0x5DE000); mu.mem_write(TEXT_VA,IMGS[variant])
    mu.mem_map(0x10000000,0x400000); mu.mem_map(0x20000000,0x10000)
    esi=0x10000000
    mu.mem_write(esi+0xd8,struct.pack('<I',0x10002000))
    mu.mem_write(0x10002000+0x44,struct.pack('<I',mflags))
    mu.mem_write(esi+0xa38,struct.pack('<I',aflags))
    mu.mem_write(esi+8,struct.pack('<I',0x10003000))
    mu.mem_write(0x10003000+8,struct.pack('<I',0x19 if player else 0x09))
    mu.mem_write(0x10300000,struct.pack('<I',can))
    log=[]
    def hook(uc,addr,size,ud):
        if addr==0x71DE90: log.append(('can',uc.reg_read(UC_X86_REG_ECX)))
        if addr==0x73AC30:
            sp=uc.reg_read(UC_X86_REG_ESP)
            a1,a2=struct.unpack('<II',bytes(uc.mem_read(sp+4,8)))
            log.append(('refresh',uc.reg_read(UC_X86_REG_ECX),a1,a2))
    mu.hook_add(UC_HOOK_CODE,hook,begin=0x71DE90,end=0x71DE90)
    mu.hook_add(UC_HOOK_CODE,hook,begin=0x73AC30,end=0x73AC30)
    sp0=0x20008000
    mu.reg_write(UC_X86_REG_ESP,sp0); mu.reg_write(UC_X86_REG_ESI,esi)
    mu.reg_write(UC_X86_REG_EAX,cur); mu.reg_write(UC_X86_REG_EBX,0x1234); mu.reg_write(UC_X86_REG_EDI,0x5678); mu.reg_write(UC_X86_REG_EBP,0x20009000)
    mu.emu_start(0x73E379,0x73E3D6,count=200)
    assert mu.reg_read(UC_X86_REG_EIP)==0x73E3D6
    regs=(mu.reg_read(UC_X86_REG_ESP),mu.reg_read(UC_X86_REG_ESI),mu.reg_read(UC_X86_REG_EBX),mu.reg_read(UC_X86_REG_EDI),mu.reg_read(UC_X86_REG_EBP))
    assert regs==(sp0,esi,0x1234,0x5678,0x20009000), regs
    return log
n=0; diffs=0
for mf,af,cur,can,pl in itertools.product(
        [0,0x10,0x20,0x30,0x01,0x11,0x21,0xFFFFFFCF,0xFFFFFFFF],
        [0,0x800,0x1000,0x1800,0x80,0x880,0xFFFFE7FF,0xFFFFFFFF],
        [0,5,0xB,0xC,0x1FA,0x10B],[0,1],[False,True]):
    o=run('orig',mf,af,cur,can,pl); r=run('robinsch',mf,af,cur,can,pl); s=run('st0ny',mf,af,cur,can,pl)
    n+=1
    o_can=[x for x in o if x[0]=='can']; o_ref=[x for x in o if x[0]=='refresh']
    # Robinsch: gleiche CanShuffle-Aufrufe, nie refresh
    assert [x for x in r if x[0]=='can']==o_can and not [x for x in r if x[0]=='refresh'], (mf,af,cur,can,pl,o,r)
    # St0ny: gleiche CanShuffle-Aufrufe; refresh wie Original bei Spielern, nie bei NPCs
    exp=o if pl else o_can
    if s!=exp: diffs+=1; print('DIFF',hex(mf),hex(af),hex(cur),can,pl,o,s)
print('cases',n,'diffs',diffs)
print('example player turning:',run('orig',0x10,0,0,1,True),run('st0ny',0x10,0,0,1,True))

import sys,struct; sys.path.insert(0,'.')
from emu import *
FIX2=dict(FIX); FIX2[0x1AAAFA]=bytes.fromhex('89E1E84FD71A0083C404')
GOOD=build(FIX2)
IDS=[50001,1001,1002,1005,99999]
fails=0
def chk(name,got,exp):
    global fails
    ok=got==exp
    if not ok: fails+=1
    print('  %-46s %s got=%s exp=%s'%(name,'OK ' if ok else 'BAD',got,exp))
STK=0x110000
def fresh(): return Emu(GOOD)
# 1) helpers called like thiscall(ecx=&id), plain ret
for fn,field in [(0x758D30,'class'),(0x758D80,'subclass'),(0x758DD0,'inv'),(0x758E50,'display'),(0x758F50,'sheath')]:
    print('helper %X (%s)'%(fn,field))
    for i in IDS:
        e=fresh(); idp=e.alloc(4); e.mu.mem_write(idp,struct.pack('<I',i))
        esp=STK; e.mu.mem_write(esp,struct.pack('<I',0x300000)); e.mu.mem_map(0x300000,0x1000)
        e.regs(ecx=idp,esp=esp,ebp=0xBEEF0000,esi=0x5151,ebx=0xB0B0,edi=0xD1D1)
        e.mu.emu_start(fn,0x300000,count=5000)
        res=(e.get('eax'),e.get('esp')==esp+4,e.get('ebp'),e.get('esi'),e.get('ebx'),e.get('edi'))
        chk('id %d'%i,res,(expect(i,field),True,0xBEEF0000,0x5151,0xB0B0,0xD1D1))
# 2) CGItem methods (ecx=object, [obj+8]=descriptors, [desc+0xC]=entry)
for fn,field in [(0x707220,'class'),(0x707250,'subclass'),(0x707280,'inv'),(0x707300,'display'),(0x707330,'sheath')]:
    print('CGItem method %X (%s)'%(fn,field))
    for i in IDS:
        e=fresh(); obj=e.alloc(0x20); desc=e.alloc(0x40)
        e.mu.mem_write(obj+8,struct.pack('<I',desc)); e.mu.mem_write(desc+0xC,struct.pack('<I',i))
        esp=STK; e.mu.mem_write(esp,struct.pack('<I',0x300000)); e.mu.mem_map(0x300000,0x1000)
        e.regs(ecx=obj,esp=esp,ebp=0xBEEF0000,esi=0x5151,ebx=0xB0B0,edi=0xD1D1)
        e.mu.emu_start(fn,0x300000,count=5000)
        res=(e.get('eax'),e.get('esp')==esp+4,e.get('ebp'),e.get('esi'),e.get('ebx'),e.get('edi'))
        chk('id %d'%i,res,(expect(i,field),True,0xBEEF0000,0x5151,0xB0B0,0xD1D1))
# 3) CGItem icon (0x70AA00): passes display id to 0x70A910
print('CGItem icon 70AA00')
for i in IDS:
    e=fresh(); obj=e.alloc(0x20); desc=e.alloc(0x40)
    e.mu.mem_write(obj+8,struct.pack('<I',desc)); e.mu.mem_write(desc+0xC,struct.pack('<I',i))
    esp=STK; e.mu.mem_write(esp,struct.pack('<I',0x300000)); e.mu.mem_map(0x300000,0x1000)
    e.regs(ecx=obj,esp=esp)
    e.mu.emu_start(0x70AA00,0x300000,count=5000)
    chk('id %d'%i,(e.iconarg,e.get('esp')==esp+4),(expect(i,'display'),True))
# 4) call sites
def site(name,start,end,setup,result,field_exp):
    print(name)
    for i in IDS:
        e=fresh(); esp=STK; ebp=STK+0x800
        e.regs(esp=esp,ebp=ebp,esi=0x5151,ebx=0xB0B0,edi=0xD1D1,eax=0xAAAA)
        setup(e,i,esp,ebp)
        e.mu.emu_start(start,end,count=5000)
        got=result(e,i,esp,ebp); exp=field_exp(i,esp,ebp)
        chk('id %d'%i,got,exp)
r32=lambda e,a: e.r32(a)
# region 1 (51706D): esi=id -> esi=display, esp unchanged, ends at 517088 (test esi,esi)
site('site 51706D',0x51706D,0x517088,lambda e,i,esp,ebp: e.regs(esi=i),
     lambda e,i,esp,ebp:(e.get('esi'),e.get('esp')==esp), lambda i,esp,ebp:(expect(i,'display'),True))
# region 2 (522FF7): esi=id -> edi=display or 0 at 523020
site('site 522FF7',0x522FF7,0x523020,lambda e,i,esp,ebp: e.regs(esi=i),
     lambda e,i,esp,ebp:(e.get('edi'),e.get('esp')==esp), lambda i,esp,ebp:(expect(i,'display'),True))
# region 3 (5A60EF): [ebp-0xc]=id -> [ebp-0xc]=display, eax=display, at 5A6102
site('site 5A60EF',0x5A60EF,0x5A6102,lambda e,i,esp,ebp: e.mu.mem_write(ebp-0xc,struct.pack('<I',i)),
     lambda e,i,esp,ebp:(e.get('eax'),r32(e,ebp-0xc),e.get('esp')==esp), lambda i,esp,ebp:(expect(i,'display'),expect(i,'display'),True))
# region 4 (5A632E): ebx=&id -> [ebp-8]=display at 5A6340
def s4(e,i,esp,ebp):
    p=e.alloc(4); e.mu.mem_write(p,struct.pack('<I',i)); e.regs(ebx=p)
site('site 5A632E',0x5A632E,0x5A6340,s4,
     lambda e,i,esp,ebp:(r32(e,ebp-8),e.get('esp')==esp), lambda i,esp,ebp:(expect(i,'display'),True))
# region 5 (5A88F5): a pushed arg on stack (cleaned by add esp,4), esi=id -> eax=invtype at 5A891E, esp=esp0+4
def s5(e,i,esp,ebp): e.regs(esi=i)
site('site 5A88F5',0x5A88F5,0x5A891E,s5,
     lambda e,i,esp,ebp:(e.get('eax'),e.get('esp')==esp+4), lambda i,esp,ebp:(expect(i,'inv'),True))
# regions 6,7,9,10,11,13: push eax at start (eax=id) -> join point eax=display (or 0)
for name,start,join in [('site 5A988D',0x5A988D,0x5A98A3),('site 5AB2D3',0x5AB2D3,0x5AB2E9),('site 5AB5CF',0x5AB5CF,0x5AB5E5),
                        ('site 5AB6F9 (fixed line 0x1AAAFA)',0x5AB6F9,0x5AB70F),('site 5ABF15',0x5ABF15,0x5ABF2B)]:
    site(name,start,join,lambda e,i,esp,ebp: e.regs(eax=i),
         lambda e,i,esp,ebp:(e.get('eax'),e.get('esp')==esp), lambda i,esp,ebp:(expect(i,'display'),True))
# region 9 (5AB4A1 push edi): edi=id -> at 5AB4B3 eax=display when found; je to 5AB4CF when 0
def r9(e,i,esp,ebp): return (e.get('eax'),e.get('esp')==esp)
print('site 5AB4A1')
for i in IDS:
    e=fresh(); esp=STK; e.regs(esp=esp,edi=i)
    exp=expect(i,'display'); end=0x5AB4B3 if exp else 0x5AB4CF
    e.mu.emu_start(0x5AB4A1,end,count=5000)
    chk('id %d'%i,(e.get('eax'),e.get('esp')==esp,e.mu.reg_read(UC_X86_REG_EIP)),(exp,True,end))
# region 8 (5AB421): [ebp+8]=id -> edi=inv, eax=display at 5AB433; then 5AB46C..5AB46F eax=edi
print('site 5AB421 (+ trampoline 707298)')
for i in IDS:
    e=fresh(); esp=STK; ebp=STK+0x800; e.mu.mem_write(ebp+8,struct.pack('<I',i)); e.regs(esp=esp,ebp=ebp)
    e.mu.emu_start(0x5AB421,0x5AB433,count=5000)
    got=(e.get('edi'),e.get('eax'),e.get('esp')==esp)
    e.mu.emu_start(0x5AB46C,0x5AB46F,count=10)
    chk('id %d'%i,got+(e.get('eax'),),(expect(i,'inv'),expect(i,'display'),True,expect(i,'inv')))
# region 12 (5ABC75 push esi): esi=id -> ebx=inv, eax=display at 5ABC84 (via trampoline 5A8906)
print('site 5ABC75 (+ trampoline 5A8906)')
for i in IDS:
    e=fresh(); esp=STK; e.regs(esp=esp,esi=i)
    e.mu.emu_start(0x5ABC75,0x5ABC84,count=5000)
    chk('id %d'%i,(e.get('ebx'),e.get('eax'),e.get('esp')==esp,e.get('esi')),(expect(i,'inv'),expect(i,'display'),True,i))
print('FAILS:',fails)

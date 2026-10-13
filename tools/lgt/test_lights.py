import sys,os,struct,random
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,'/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/gen'); sys.path.insert(0,'/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/lgt'); sys.path.insert(0,'/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/tm')
from emu2 import *
import lights as LG
D=open(sys.argv[1],'rb').read()
ORIGD=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
fails=0
def ok(c,msg):
    global fails
    print(('OK   ' if c else 'FAIL ')+msg)
    if not c: fails+=1
so=[s for s in sections(D) if s[0]=='.lght'][0]
SEC=so[1]
def mk(data,patched):
    e=Emu2(data)
    if patched:
        try: e.mu.mem_map(SEC,0x1000)
        except UcError: pass
        e.mu.mem_write(SEC,data[so[4]:so[4]+so[3]])
    return e
H=0x30000000
LGT=H+0x1000; LIGHTS=H+0x10000; SCENE=H+0x8000; RINGMEM=H+0x90000
def setup(e):
    e.allocs=[]
    def valloc(em,a):
        em.allocs.append(a); return RINGMEM
    e.w32(0x9DF238,H+0x3000); e.stub(H+0x3000,valloc,4,16)
def light(e,i,pos,col=(1,1,1),att=(0,0.7,0.03),en=1,typ=1):
    a=LIGHTS+i*0x80
    e.mu.mem_write(a,b'\0'*0x80)
    e.w32(a+8,typ); e.mu.mem_write(a+0xC,struct.pack('<3f',*pos)); e.mu.mem_write(a+0x3C,struct.pack('<3f',*col))
    e.mu.mem_write(a+0x54,struct.pack('<3f',*att)); e.w32(a+0x60,en)
    return a
def init(e,scene=0):
    sph=H+0x2000; e.mu.mem_write(sph,struct.pack('<4f',0,0,0,10))
    e.call(0x834900,(scene,sph),regs={UC_X86_REG_ECX:LGT})
def add(e,a): e.call(0x834F60,(a,),regs={UC_X86_REG_ECX:LGT})
def inline(e):
    n=e.r32(LGT+0xA4); return [e.r32(LGT+0x84+4*i) for i in range(n)]
def entry(e):
    idx=struct.unpack('<H',bytes(e.mu.mem_read(LGT+0x16,2)))[0]
    if not idx: return None
    ent=RINGMEM+(idx-1)*0x28
    if e.r32(ent)!=LGT: return None
    n=e.r32(ent+4); return [e.r32(ent+8+4*i) for i in range(n)]
eo=mk(ORIGD,False); ep=mk(D,True); setup(ep)
random.seed(7)
allgood=True; extra_good=True
for trial in range(60):
    n=random.randint(0,12)
    pts=[(random.uniform(-30,30),random.uniform(-30,30),random.uniform(-5,5)) for _ in range(n)]
    if trial%7==0 and n>2: pts[1]=pts[0]           # gleiche Abstaende
    for e in (eo,ep): init(e)
    addrs=[]
    for i,p in enumerate(pts):
        en=0 if (trial%5==0 and i==2) else 1
        for e in (eo,ep): a=light(e,i,p,en=en)
        addrs.append((a,en,p))
        for e in (eo,ep): add(e,a)
    io,ip=inline(eo),inline(ep)
    if io!=ip: allgood=False; print('  inline differs',trial,io,ip)
    # expected: lights sorted by d2 (stable order like insertion), 5th..8th
    live=[(p[0]**2+p[1]**2+p[2]**2,k,a) for k,(a,en,p) in enumerate(addrs) if en]
    live_sorted=sorted(live,key=lambda t:t[0])
    exp=[a for _,_,a in live_sorted[4:8]]
    got=entry(ep) or []
    if [d2 for d2,_,a in live_sorted[4:8]]!=[ (pts[(a-LIGHTS)//0x80][0]**2+pts[(a-LIGHTS)//0x80][1]**2+pts[(a-LIGHTS)//0x80][2]**2) for a in got]:
        extra_good=False; print('  extras differ',trial,[hex(x) for x in exp],[hex(x) for x in got])
    if len(live)<=4 and entry(ep) not in (None,[]): extra_good=False; print('  unexpected extras',trial)
ok(allgood,'AddLight: nearest 4 inline identical to original (60 random scenes)')
ok(extra_good,'AddLight: lights 5-8 sorted in side list')
ok(len(ep.allocs)==1 and ep.allocs[0]==(0,LG.RINGBYTES,0x3000,4),'ring allocated once via VirtualAlloc(0,%#x,MEM_COMMIT|RESERVE,RW)'%LG.RINGBYTES)
# Initialize clears the slot
init(ep); ok(entry(ep) is None and inline(ep)==[],'Initialize clears side list link')
# directional light still goes to ambient path
init(ep); a=light(ep,0,(1,2,3),typ=0); add(ep,a); ok(inline(ep)==[] and entry(ep) is None,'directional light untouched')
# 10 lights at distances 1..10
def ten(e,scene=0,order=None):
    init(e,scene)
    order=order or list(range(10))
    res=[]
    for i in order: res.append(light(e,i,(float(i+1),0,0),col=(0.1*(i+1),0.2,0.3),att=(1.0+i,0.5,0.25)))
    for a in res: add(e,a)
    return [LIGHTS+i*0x80 for i in range(10)]
L10=ten(ep,order=[9,3,7,0,5,1,8,2,6,4])
ok(inline(ep)==L10[:4] and entry(ep)==L10[4:8],'10 lights in random order -> inline 1-4, extras 5-8')
# TransformLights for extras
M=[1,0,0,0, 0,1,0,0, 0,0,1,0, 100,200,300,1]
ep.mu.mem_write(SCENE+0x84,struct.pack('<16f',*M))
L10=ten(ep,scene=SCENE)
for a in L10: ep.mu.mem_write(a+0x18,struct.pack('<3f',-1,-1,-1))
ep.call(0x8350A0,(),regs={UC_X86_REG_ECX:LGT})
tp=[struct.unpack('<3f',bytes(ep.mu.mem_read(a+0x18,12))) for a in L10]
ok(all(tp[i]==(i+1+100.0,200.0,300.0) for i in range(8)),'TransformLights: inline and extra lights transformed')
ok(tp[8]==(-1,-1,-1) and tp[9]==(-1,-1,-1),'TransformLights: lights 9/10 untouched')
ok(ep.r32(LGT+0x14)&1==1,'TransformLights finished (flag 1 set)')
# shader upload
DEV=H+0x40000; VT=H+0x41000; calls=[]
ep.w32(0xC5DF88,DEV); ep.w32(DEV,VT); ep.w32(VT+0x118,H+0x42000); ep.w32(DEV+0x2E0,256)
def setc(em,a):
    calls.append((em.mu.reg_read(UC_X86_REG_ECX),a[0],a[1],a[3],struct.unpack('<%df'%(4*a[3]),bytes(em.mu.mem_read(a[2],16*a[3])))))
ep.stub(H+0x42000,setc,4,16)
CLL=SEC+LG.LAB['cll_ex']
OUTB=H+0x50000
r,_=ep.call(CLL,(OUTB,4,LGT+0x84,0))
base=struct.unpack('<44f',bytes(ep.mu.mem_read(OUTB,176)))
ok(len(calls)==1 and calls[0][:4]==(DEV,0,0xEC,0xB),'upload 11 VS registers at c236 (thiscall on device)')
v=calls[0][4] if calls else [0]*44
def reg(buf,r): return buf[4*r:4*r+4]
okc=all(abs(reg(v,i)[0]-0.1*(i+5))<1e-6 and reg(v,i)[3]==1.0 for i in range(4))
okp=all(reg(v,4+i)[:3]==(i+5+100.0,200.0,300.0) for i in range(4))
oka=reg(v,8)==tuple(1.0+i+4 for i in range(4)) and reg(v,9)==(0.5,)*4 and reg(v,10)==(0.25,)*4
ok(okc and okp and oka,'c236-239 colour, c240-243 view position, c244-246 attenuation of lights 5-8')
ok(all(abs(reg(base,i)[0]-0.1*(i+1))<1e-6 for i in range(4)) and reg(base,4)[:3]==(101.0,200.0,300.0),'original c17-c27 buffer unchanged (lights 1-4)')
# only 6 lights -> extras 2, rest colour 0
calls.clear(); init(ep,SCENE)
for i in range(6): add(ep,light(ep,i,(float(i+1),0,0),col=(1,1,1)))
ep.call(0x8350A0,(),regs={UC_X86_REG_ECX:LGT}); ep.call(CLL,(OUTB,4,LGT+0x84,0))
v=calls[0][4]
ok(reg(v,0)[0]==1.0 and reg(v,1)[0]==1.0 and reg(v,2)==(0,0,0,0) and reg(v,3)==(0,0,0,0),'6 lights: 2 extra colours, unused slots colour 0')
# no extras -> all colour 0
calls.clear(); init(ep,SCENE)
for i in range(3): add(ep,light(ep,i,(float(i+1),0,0)))
ep.call(CLL,(OUTB,3,LGT+0x84,0)); v=calls[0][4]
ok(all(reg(v,i)==(0,0,0,0) for i in range(4)),'3 lights: all extra colours 0')
# too few constants -> no upload
calls.clear(); ep.w32(DEV+0x2E0,192); ep.call(CLL,(OUTB,3,LGT+0x84,0))
ok(calls==[],'card with < 247 VS constants: no extra upload')
ep.w32(DEV+0x2E0,256)
# patched call sites
def callt(data,va):
    o=va-0x400C00; return va+5+struct.unpack_from('<i',data,o+1)[0]
ok(D[0x873E85-0x400C00]==0xE8 and callt(D,0x873E85)==CLL,'M2 SetLocalLighting -> cll_ex')
ok(D[0x7A91A9-0x400C00]==0xE8 and callt(D,0x7A91A9)==CLL,'WMO lighting -> cll_ex')
# fixed function: real SetupGxLights with real LightSet / LightEnable
GX=SEC+LG.DO['GX']
GDEV=H+0x60000; ep.w32(0xC5DF88,GDEV)
ep.call(0x682C50,(),regs={UC_X86_REG_ECX:GDEV})
ok(all(ep.r32(GX+i*0x48+0x40)==0 and ep.r32(GX+i*0x48+0x44)==0x00FF00FF for i in range(8)),'ResetLights: 8 slots enable 0, dirty 0xFF, mask 0xFF')
def ff(e,n,data_orig=False):
    init(e,SCENE)
    for i in range(n): add(e,light(e,i,(float(i+1),0,0),col=(0.1*(i+1),0,0)))
    e.call(0x8350A0,(),regs={UC_X86_REG_ECX:LGT})
    e.call(0x8353D0,(0,),regs={UC_X86_REG_ECX:LGT})
def slots(e,base,cnt):
    return [(e.r32(base+i*0x48+0x40), round(struct.unpack('<f',bytes(e.mu.mem_read(base+i*0x48,4)))[0],3)) for i in range(cnt)]
ff(ep,10)
s=slots(ep,GX,8)
ok(s[0][0]==1 and [x for _,x in s[1:]]==[101.0+i for i in range(7)] and all(en==1 for en,_ in s[1:]),'FF 10 lights: slot 0 sun, slots 1-7 = 7 nearest (nearest first)')
ff(ep,4); s=slots(ep,GX,8)
ok([x for _,x in s[1:5]]==[101.0,102.0,103.0,104.0] and [en for en,_ in s[1:5]]==[1]*4 and [en for en,_ in s[5:]]==[0]*3,'FF 4 lights: all 4 used (nearest no longer dropped), 5-7 off')
ff(ep,0); s=slots(ep,GX,8)
ok([en for en,_ in s[1:]]==[0]*7,'FF no lights: slots 1-7 off')
# D3D9 path: real CGxDeviceD3d light flush (0x6A43D0) sends all 8 slots
D9=H+0x70000; D9VT=H+0x71000; RS=H+0x72000; api=[]
ep.mu.mem_write(GDEV+0x2000,b'\0'*0x2000)
ep.w32(GDEV+0x397C,D9); ep.w32(D9,D9VT); ep.w32(GDEV+0x28F4,RS); ep.w32(RS+0x108,1); ep.w32(GDEV+0x2758,1)
for off,nm,na in ((0xE4,'SRS',3),(0xCC,'SetLight',3),(0xD4,'LightEnable',3)):
    ep.w32(D9VT+off,H+0x73000+off)
    def mkf(nm):
        def f(em,a):
            rec=(nm,a[1],a[2]) if nm!='SetLight' else (nm,a[1],(lambda t:(t[0],t[1],t[13]))(struct.unpack('<I13f',bytes(em.mu.mem_read(a[2],56)))))
            api.append(rec); return 0
        return f
    ep.stub(H+0x73000+off,mkf(nm),na,4*na)
ff(ep,10); ep.call(0x6A43D0,(),regs={UC_X86_REG_ECX:GDEV})
sl=[r for r in api if r[0]=='SetLight']; le=[r for r in api if r[0]=='LightEnable']
ok(sorted(r[1] for r in sl)==list(range(8)) and sorted((r[1],r[2]) for r in le)==[(i,1) for i in range(8)],'D3D9: SetLight + LightEnable(TRUE) for lights 0-7')
pt=dict((r[1],r[2]) for r in sl)
ok(pt[1][0]==1 and abs(pt[1][2]-101.0)<1e-4 and pt[0][0]==3 and abs(pt[7][2]-107.0)<1e-4 and abs(pt[7][1]-0.7)<1e-6,'D3D9: light 0 directional, 1-7 point lights at the 7 nearest positions')
api.clear(); ff(ep,2); ep.call(0x6A43D0,(),regs={UC_X86_REG_ECX:GDEV})
le=[(r[1],r[2]) for r in api if r[0]=='LightEnable']
ok(sorted(le)==[(i,0) for i in range(3,8)],'D3D9: with 2 lights, slots 3-7 switched off')
# original behaviour for comparison (documents the bug)
eo.w32(0xC5DF88,GDEV); eo.mu.mem_write(SCENE+0x84,struct.pack('<16f',*M))
eo.call(0x682C50,(),regs={UC_X86_REG_ECX:GDEV})
ff(eo,4); s=slots(eo,GDEV+0x2548,4)
ok([x for _,x in s[1:4]]==[104.0,103.0,102.0],'original FF with 4 lights uses 4,3,2 (nearest dropped) - bug confirmed')
print('fails',fails)
sys.exit(1 if fails else 0)

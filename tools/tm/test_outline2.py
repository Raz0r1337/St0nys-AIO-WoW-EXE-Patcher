import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu2 import *
D=open(sys.argv[1],'rb').read()
fails=0
def ok(c,msg):
    global fails
    print(('OK   ' if c else 'FAIL ')+msg)
    if not c: fails+=1
secs={nm:va for nm,va,vs,rs,ro,ch in sections(D)}
OUT=secs['.outl']
e=Emu2(D)
try: e.mu.mem_map(OUT,0x1000)
except UcError: pass
so=[s for s in sections(D) if s[0]=='.outl'][0]
e.mu.mem_write(OUT,D[so[4]:so[4]+so[3]])
H=0x30000000; e.mu.mem_write(H,b'\0'*0x100000)
DEV=H+0x10000; D3D=H+0x1000; VT=H+0x2000; STUBS=H+0x3000
GPU=H+0x30000
e.w32(0xC5DF88,DEV); e.w32(DEV,0xA2E718); e.w32(DEV+0x1CC,5); e.w32(DEV+0x397C,D3D); e.w32(DEV+0x2900,GPU)
e.w32(D3D,VT)
calls=[]
names={0x148:'DIP',0xE4:'SRS',0x178:'SetVSConst',0x1A8:'CreatePS',0x170:'SetVS',0x1AC:'SetPS',0x164:'SetFVF',0x14C:'DPUP',0xAC:'Clear'}
nargs={0x148:7,0xE4:3,0x178:4,0x1A8:3,0x170:2,0x1AC:2,0x164:2,0x14C:5,0xAC:7}
for off,nm in names.items():
    a=STUBS+off; e.w32(VT+off,a)
    def mk(nm,off):
        def f(em,args):
            rec=(nm,)+tuple(args[1:])
            if nm=='SetVSConst': rec=rec+(struct.unpack('<16f',bytes(em.mu.mem_read(args[2],64))),)
            if nm=='DPUP': rec=rec+(bytes(em.mu.mem_read(args[3],80)),)
            if nm=='CreatePS': em.w32(args[2],0x5050); rec=rec+(bytes(em.mu.mem_read(args[1],20)),)
            calls.append(rec); return 0
        return f
    e.stub(a,mk(nm,off),nargs[off],4*nargs[off])
# VS constant cache c2..c5 (dp4 layout projection)
P=[1.5,0,0,0, 0,2.0,0,0, 0,0,1.001,-0.1, 0,0,1.0,0]
e.mu.mem_write(0xC5F008,struct.pack('<16f',*P))
# engine functions
ST={}
e.stub(0x8203B0,lambda em,a: ST.setdefault('db',[]).append(em.r32(OUT+0x18)),0,0)
TOBJ=H+0x40000; MOBJ=H+0x41000; TM=H+0x50000; TMOUNT=H+0x51000; MM=H+0x52000; WEAP=H+0x53000; OTHER=H+0x54000
e.w32(TOBJ+0xB4,TM); e.w32(TOBJ+0x98C,TMOUNT); e.w32(MOBJ+0xB4,MM); e.w32(MOBJ+0x98C,0); e.w32(WEAP+0x48,TM)
def objptr(em,a):
    ST.setdefault('obj',[]).append(a)
    return {0x111:TOBJ,0x222:MOBJ}.get(a[0],0)
e.stub(0x4D4DB0,objptr,5,0)
def selcol(em,a):
    g=em.r32(a[0]); em.w32(a[1],{0x111:0xFFFF0000,0x222:0xFF00FF00}[g]); ST.setdefault('col',[]).append(a[2])
e.stub(0x521BF0,selcol,3,0)
e.stub(0x685970,lambda em,a: ST.setdefault('dirty',[]).append(a[0]),1,4)
e.stub(0x685A70,lambda em,a: ST.__setitem__('force',ST.get('force',0)+1),0,0)
e.stub(0x4F6F90,lambda em,a: ST.__setitem__('circles',em.mu.reg_read(UC_X86_REG_ECX)),0,0)
SCENE=H+0x60000; e.w32(0xCD754C,SCENE)
e.w32(0xBD07B0,0x111); e.w32(0xBD07B4,0x0F000000); e.w32(0xBD07A0,0x222); e.w32(0xBD07A4,0x0F000000)
e.w32(0xD43020,1)
mu=e.mu
def run(start,stop,regs,stack=()):
    sp=0x200F0000
    for v in reversed(stack): sp-=4; mu.mem_write(sp,struct.pack('<I',v))
    for r,v in regs.items(): mu.reg_write(r,v)
    mu.reg_write(UC_X86_REG_ESP,sp)
    mu.emu_start(start,stop,count=200000)
    return sp
# 1) viewport capture
FR=0x200E0000; mu.mem_write(FR-0x24,struct.pack('<4I2f',0,0,1920,1080,0.0,1.0))
run(0x6A9B10,0x6A9B16,{UC_X86_REG_EBP:FR,UC_X86_REG_ESI:DEV})
ok(bytes(mu.mem_read(OUT,24))==struct.pack('<4I2f',0,0,1920,1080,0.0,1.0),'viewport captured')
ok(mu.reg_read(UC_X86_REG_EAX)==D3D,'eax = d3d device after vp hook')
# 2) batch hook
REN=H+0x70000
def batch(model,scene=SCENE):
    e.w32(REN+0x40,scene); e.w32(REN+0x60,model); ST['db']=[]
    run(0x823A81,0x823AD3,{UC_X86_REG_ESI:REN,UC_X86_REG_EDI:7,UC_X86_REG_EBX:9})
    return ST['db'], mu.reg_read(UC_X86_REG_ESI)==REN and mu.reg_read(UC_X86_REG_EDI)==7 and mu.reg_read(UC_X86_REG_EBX)==9
r,keep=batch(TM); ok(r==[1] and keep,'target model -> CUR 1, regs kept')
ok(e.r32(OUT+0x18)==0,'CUR reset after batch')
ok(len(ST['obj'])==2 and e.r32(OUT+0x34)==0xFFFF0000 and e.r32(OUT+0x38)==0xFF00FF00 and ST['col']==[1,1],'lookup once per frame, colors')
r,_=batch(TMOUNT); ok(r==[1],'mount model -> 1')
r,_=batch(WEAP); ok(r==[1],'attached weapon (parent=target) -> 1')
r,_=batch(MM); ok(r==[2],'mouseover model -> 2')
r,_=batch(OTHER); ok(r==[0],'other model -> 0')
r,_=batch(TM,scene=H+0x61000); ok(r==[0],'other scene -> 0')
ok(len(ST['obj'])==2,'no extra lookups within frame')
# 3) dip unmarked: tail-jump
calls.clear(); e.w32(OUT+0x18,0)
sp=run(OUT+0x2DC if False else OUT+0,0,{}) if False else None
LAB={}
import importlib.util
spec=importlib.util.spec_from_file_location('outline','/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/gen/outline.py')
sys.path.insert(0,'/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/gen')
o=importlib.util.module_from_spec(spec); spec.loader.exec_module(o)
DIP=OUT+o.LAB['dip']; POST=OUT+o.LAB['post']
RET=0x31000000
args=[D3D,4,0,0,100,0,50]
sp=run(DIP,RET,{UC_X86_REG_EBX:1,UC_X86_REG_ESI:2,UC_X86_REG_EDI:3,UC_X86_REG_EBP:4},[RET]+args)
ok([c[0] for c in calls]==['DIP'] and calls[0][1:]==tuple(args[1:]),'unmarked: one plain DIP')
ok(mu.reg_read(UC_X86_REG_ESP)==sp+4+28,'unmarked: stack balanced (ret 0x1C)')
# 4) dip marked target
calls.clear(); e.w32(OUT+0x18,1); e.w32(DEV+0x3E60,0); e.w32(DEV+0x3E88,4); ST['dirty']=[]
sp=run(DIP,RET,{UC_X86_REG_EBX:1,UC_X86_REG_ESI:2,UC_X86_REG_EDI:3,UC_X86_REG_EBP:4},[RET]+args)
seq=[c[0] for c in calls]
ok(mu.reg_read(UC_X86_REG_ESP)==sp+4+28 and [mu.reg_read(r) for r in (UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP)]==[1,2,3,4],'marked: stack + callee-saved regs')
ok(seq.count('DIP')==10,'marked: real + ring pass + 8 copies (%d)'%seq.count('DIP'))
srs=[c[1:3] for c in calls if c[0]=='SRS']
fi=seq.index('DIP')
before=[c[1:3] for c in calls[:fi] if c[0]=='SRS']
ok((52,1) in before and (56,8) in before and (57,4) in before and (55,3) in before,'real draw with stencil ALWAYS/REPLACE 4')
dips=[k for k,c in enumerate(calls) if c[0]=='DIP']
b2=[c[1:3] for c in calls[dips[0]:dips[1]] if c[0]=='SRS']
ok((56,3) in b2 and (57,5) in b2 and (58,3) in b2 and (23,8) in b2,'ring pass: stencil EQUAL (ref 5, mask 3), ZFUNC ALWAYS')
a2=[c[1:3] for c in calls[dips[1]:dips[2]] if c[0]=='SRS']
ok(a2[0]==(23,4) and (58,0xFF) in a2,'ZFUNC restored to engine value (4) after ring pass, mask back to FF')
ok((56,5) in srs and (57,1) in srs and (168,0) in srs and (14,1) in srs,'copies: GREATER ref 1, colorwrite 0, zwrite 1')
ok(srs[-1]==(52,0),'stencil disabled at end')
vs=[c for c in calls if c[0]=='SetVSConst']
ok(len(vs)==9 and all(c[1]==2 and c[3]==4 for c in vs),'9 VS const uploads to c2..c5')
m=vs[0][4]; ox=2*2/1920; 
exp=[P[i]+ox*P[12+i] for i in range(4)]
print('DBG',m[:4],exp,m[4:8],m[8:]); ok(all(abs(m[i]-exp[i])<1e-6 for i in range(4)) and all(abs(m[4+i]-P[4+i])<1e-6 for i in range(4)) and all(abs(m[8+i]-P[8+i])<1e-6 for i in range(8)),'copy 0: c2 += 2px*ox*c5, c3 unchanged')
m=vs[2][4]; oy=-2*2/1080
ok(all(abs(m[4+i]-(P[4+i]+oy*P[12+i]))<1e-6 for i in range(4)),'copy 2: c3 += oy*c5 (down 2px)')
ok(vs[-1][2]==0xC5F008,'restore from cache')
ok(e.r32(DEV+0x3E70)==0xFFFFFFFF and e.r32(DEV+0x3E74)==0xFFFFFFFF and e.r32(GPU+0xF0)==0xFFFFFFFE and e.r32(GPU+0x100)==0xFFFFFFFE and ST['dirty']==[15,16],'zwrite/colorwrite invalidated')
ok(e.r32(OUT+0x30)==1,'MARKED set')
# 4a) invalid engine ZFUNC shadow -> LESSEQUAL restored
calls.clear(); e.w32(OUT+0x18,1); e.w32(DEV+0x3E60,0); e.w32(DEV+0x3E88,0xFFFFFFFF); e.w32(OUT+0x14C,0)
run(DIP,RET,{},[RET]+args)
dd=[k for k,c in enumerate(calls) if c[0]=='DIP']
ok([c[1:3] for c in calls[dd[1]:dd[2]] if c[0]=='SRS'][0]==(23,4),'invalid ZFUNC shadow: LESSEQUAL (4) restored')
e.w32(DEV+0x3E88,4)
# 4b) occluders after marking: depth-writing draws clear the stencil, others not
SM=OUT+0x14C
calls.clear(); e.w32(OUT+0x18,0); e.w32(OUT+0x30,1); e.w32(SM,0); e.w32(DEV+0x3E70,1)
sp=run(DIP,RET,{UC_X86_REG_EBX:1,UC_X86_REG_ESI:2,UC_X86_REG_EDI:3,UC_X86_REG_EBP:4},[RET]+args)
srs=[c[1:3] for c in calls if c[0]=='SRS']; seq=[c[0] for c in calls]
ok(seq[-1]=='DIP' and seq.count('DIP')==1 and (52,1) in srs and (56,8) in srs and (57,0) in srs and (55,3) in srs,'zwrite draw after marking: stencil ALWAYS/REPLACE 0, one DIP')
ok(e.r32(SM)==1 and mu.reg_read(UC_X86_REG_ESP)==sp+4+28 and [mu.reg_read(r) for r in (UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP)]==[1,2,3,4],'SMODE 1, stack + regs kept')
calls.clear(); run(DIP,RET,{},[RET]+args)
ok([c[0] for c in calls]==['DIP'],'same mode again: no state change')
calls.clear(); e.w32(DEV+0x3E70,0); run(DIP,RET,{},[RET]+args)
ok([c[0] for c in calls]==['SRS','DIP'] and calls[0][1:3]==(52,0) and e.r32(SM)==0,'zwrite off: stencil disabled')
calls.clear(); e.w32(OUT+0x30,0); e.w32(DEV+0x3E70,1); run(DIP,RET,{},[RET]+args)
ok([c[0] for c in calls]==['DIP'],'nothing marked yet: plain DIP')
# target batch while clear mode active: clear mode switched off first
e.w32(OUT+0x30,1); calls.clear(); run(DIP,RET,{},[RET]+args); ok(e.r32(SM)==1,'clear mode on again')
calls.clear(); e.w32(OUT+0x18,1); e.w32(DEV+0x3E60,1)
run(DIP,RET,{},[RET]+args)
ok([c[0] for c in calls]==['SRS','DIP'] and calls[0][1:3]==(52,0) and e.r32(SM)==0,'blended target batch: clear mode off, plain draw')
e.w32(DEV+0x3E60,0); e.w32(DEV+0x3E70,0xFFFFFFFF)
# 5) blended batch: plain
calls.clear(); e.w32(DEV+0x3E60,1)
run(DIP,RET,{},[RET]+args); ok([c[0] for c in calls]==['DIP'],'blended: plain draw only')
e.w32(DEV+0x3E60,0)
# 6) no shaders: real only
calls.clear(); e.w32(0xD43020,0)
run(DIP,RET,{},[RET]+args); ok([c[0] for c in calls].count('DIP')==1,'fixed-function: real draw only')
e.w32(0xD43020,1)
# 7) post
calls.clear(); ST['force']=0; e.w32(OUT+0x30,1); e.w32(OUT+0x2C,1)
regs={UC_X86_REG_EAX:0xA,UC_X86_REG_EBX:0xB,UC_X86_REG_ECX:0xC,UC_X86_REG_EDX:0xD,UC_X86_REG_ESI:0xE,UC_X86_REG_EDI:0xF,UC_X86_REG_EBP:0x10}
sp=run(POST,RET,regs,[RET])
seq=[c[0] for c in calls]
ok('CreatePS' in seq and calls[seq.index('CreatePS')][3]==struct.pack('<5I',0xFFFF0101,1,0x800F0000,0x90E40000,0xFFFF),'pixel shader created')
dp=[c for c in calls if c[0]=='DPUP']
ok(len(dp)==2 and all(c[1:5]==(5,2,dp[0][3],20) for c in dp),'two quads (target, mouseover) as triangle strips')
v=struct.unpack('<4f I 4f I 4f I 4f I',dp[0][5])
ok(v[0]==-0.5 and v[5]==1919.5 and v[11]==1079.5 and v[4]==0xFFFF0000 and v[3]==1.0,'quad covers viewport, target color')
ok(struct.unpack('<I',dp[1][5][16:20])[0]==0xFF00FF00,'mouseover quad color')
srs=[c[1:3] for c in calls if c[0]=='SRS']
i1=seq.index('DPUP')
ok((57,1) in [c[1:3] for c in calls[:i1] if c[0]=='SRS'] and (56,3) in srs and (23,8) in srs,'quad 1 stencil EQUAL 1, ZFUNC ALWAYS')
ok(any(c[0]=='Clear' and c[1:4]==(0,0,4) for c in calls),'stencil cleared')
ok(ST['force']==1 and e.r32(DEV+0x3BC4)==0xFFFFFFFF and e.r32(DEV+0x3E98)==0xFFFFFFFF and e.r32(DEV+0x3E9C)!=0xFFFFFFFF,'engine states forced + shadow block refilled exactly')
ok(e.r32(OUT+0x30)==0 and e.r32(OUT+0x2C)==0 and e.r32(OUT+0x14C)==0,'MARKED/VALID/SMODE reset')
ok(ST.get('circles')==0xC and all(mu.reg_read(r)==v for r,v in regs.items() if r!=UC_X86_REG_EAX),'jumps to circles with registers restored')
# 8) post without marking: only clear
calls.clear(); ST['force']=0
run(POST,RET,regs,[RET]); seq=[c[0] for c in calls]
ok(seq.count('Clear')==1 and 'DPUP' not in seq and ST['force']==0,'unmarked frame: just clear stencil')
# 9) no stencil format -> nothing
calls.clear(); e.w32(DEV+0x1CC,7); e.w32(OUT+0x2C,0)
r,_=batch(TM); ok(r==[0],'no stencil (D32): no marking')
run(POST,RET,regs,[RET]); ok(len(calls)==0,'no stencil: post does nothing')
print('FAILS',fails)

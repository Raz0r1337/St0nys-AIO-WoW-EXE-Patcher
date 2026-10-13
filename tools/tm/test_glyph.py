import sys,os,struct,random
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu2 import *
D=open(sys.argv[1],'rb').read()
fails=0
def ok(c,msg):
    global fails
    print(('OK   ' if c else 'FAIL ')+msg)
    if not c: fails+=1
H=0x30000000
def new():
    e=Emu2(D); e.mu.mem_write(H,b'\0'*0x100000); return e
# ---------- CreateNewDesc: widest free slot ----------
def pywidest(nodes):
    w=0;cur=0
    for s,en in nodes:
        if s>cur and s-cur>w: w=s-cur
        cur=en+1
    if 256>cur and 256-cur>w: w=256-cur
    return w
random.seed(1)
for trial in range(200):
    e=new(); row=H; LO=0x10
    n=random.randint(0,8); pos=0; nodes=[]
    for i in range(n):
        s=pos+random.randint(0,30); en=s+random.randint(0,40)
        if en>255: break
        nodes.append((s,en)); pos=en+1
    e.w32(row,0x55555555); e.w32(row+4,LO); e.w32(row+8,0)
    addrs=[H+0x1000+0x100*i for i in range(len(nodes))]
    term=(row+8)|1
    e.w32(row+0xC,addrs[0] if addrs else term)
    for i,(s,en) in enumerate(nodes):
        a=addrs[i]; e.w32(a+0x30,s); e.w32(a+0x34,en)
        e.w32(a+LO+4,addrs[i+1] if i+1<len(addrs) else term)
    res={}
    def at(em):
        mu=em.mu
        res['esp']=mu.reg_read(UC_X86_REG_ESP); res['ebp']=mu.reg_read(UC_X86_REG_EBP)
        res['regs']=[mu.reg_read(r) for r in (UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_ECX)]
        res['ret']=em.r32(res['ebp']+4); res['a1']=em.r32(res['ebp']+8)
        mu.emu_stop()
    e.watch_at(0x6C5126,at)
    e.mu.reg_write(UC_X86_REG_ESP,0)
    sp=0x200F0000-16
    for k,v in enumerate((0x31000000,0xA1,0xA2,0xA3)): e.w32(sp+4*k,v)
    e.mu.reg_write(UC_X86_REG_ESP,sp); e.mu.reg_write(UC_X86_REG_ECX,row)
    e.mu.reg_write(UC_X86_REG_EBX,0x11111111); e.mu.reg_write(UC_X86_REG_ESI,0x22222222); e.mu.reg_write(UC_X86_REG_EDI,0x33333333); e.mu.reg_write(UC_X86_REG_EBP,0x44444444)
    e.mu.emu_start(0x6C5120,0x31000000,count=100000)
    good=(e.r32(row)==pywidest(nodes) and res['regs']==[0x11111111,0x22222222,0x33333333,row] and res['ret']==0x31000000 and res['a1']==0xA1 and res['esp']==res['ebp']-0xC and e.r32(res['ebp'])==0x44444444)
    if not good: ok(False,'newdesc trial %d %s %s %s'%(trial,nodes,e.r32(row),res)); break
else: ok(True,'CreateNewDesc: 200 Zufalls-Zeilen, breiteste Luecke korrekt, Stack/Register ok')
# ---------- ClearInstanceData ----------
def setup_clear_stubs(e,log):
    e.stub(0x6C65E0,lambda em,a: log.append(('65e0',em.reg(UC_X86_REG_ECX))),1,4)
    e.stub(0x6C6800,lambda em,a: log.append(('6800',em.reg(UC_X86_REG_ECX))),1,4)
    e.stub(0x6C5930,lambda em,a: log.append(('5930',a[0])),1,0)
e=new(); log=[]; setup_clear_stubs(e,log); st=H+0x8000
e.w32(st+0x60,7); e.w32(st+0x64,1); e.w32(st+0xB0,3); e.w32(st+0xB4,0xBEEF); e.w32(st+0xB8,0)
r,dsp=e.call(0x6C6B90,(),regs={UC_X86_REG_ECX:st})
ok(e.r32(st+0x60)==0 and e.r32(st+0x64)==0 and e.r32(st+0xB0)==0 and e.r32(st+0xA4)==0 and e.r32(st+0x68)==0xFFFFFFFF and e.r32(st+0xB4)==0 and dsp==4
   and e.reg(UC_X86_REG_ESI)==0x22222222 and e.reg(UC_X86_REG_EDI)==0x33333333 and ('5930',0xBEEF) in log and ('65e0',st+0x80) in log,
   'ClearInstanceData: +60h/+64h geloescht, Original-Teil laeuft weiter, Stack ok (%s)'%log)
# ---------- CheckGeometry ----------
for ev in (0,1):
    for lines in (0,5):
        e=new(); log=[]; setup_clear_stubs(e,log); st=H+0x8000
        e.w32(st+0x60,9); e.w32(st+0x64,ev); e.w32(st+0xD4,20)
        def cg(em,a,lines=lines):
            log.append(('cg',em.reg(UC_X86_REG_ECX))); em.w32(em.reg(UC_X86_REG_ECX)+0xB0,lines)
        e.stub(0x6C7B10,cg,0,0)
        e.mu.reg_write(UC_X86_REG_EAX,0xFFFFFFFF)
        r,dsp=e.call(0x6C7480,(),regs={UC_X86_REG_ECX:st,UC_X86_REG_EAX:0xFFFFFFFF})
        cleared=any(x[0]=='65e0' for x in log)
        ok(cleared==bool(ev) and ('cg',st) in log and e.r32(st+0x64)==0 and e.r32(st+0xD4)==0 and (r&0xFF)==(1 if lines else 0) and dsp==4 and e.reg(UC_X86_REG_ESI)==0x22222222,
           'CheckGeometry evicted=%d lines=%d -> clear=%s ret=%d esp+%d'%(ev,lines,cleared,r&0xFF,dsp))
# ---------- RenderBatch ----------
def render_case(evict_map,init_ev,maxcalls=100):
    e=new(); log=[]; setup_clear_stubs(e,log)
    b=H+0x10000; LO=0x40; strs=[H+0x20000+0x400*i for i in range(3)]
    e.w32(b+0x1C,LO); e.w32(b+0x24,strs[0])
    for i,s in enumerate(strs):
        e.w32(s+LO+4, strs[i+1] if i+1<len(strs) else (b+0x20)|1); e.w32(s+0x64,init_ev[i])
    calls=[]
    def cg(em,a):
        s=em.reg(UC_X86_REG_ECX); i=strs.index(s); calls.append(i)
        n=len(calls)
        for j in evict_map(n,i): em.w32(strs[j]+0x64,1)
    e.stub(0x6C7B10,cg,0,0)
    e.w32(0xC7D2DC,0)
    r,dsp=e.call(0x6C4AD0,(),regs={UC_X86_REG_ECX:b})
    regs=[e.reg(x) for x in (UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP)]
    return calls,dsp,regs
c,dsp,regs=render_case(lambda n,i: [2] if i==0 and n==1 else [], [1,0,0])
ok(c==[0,1,2] and dsp==4 and regs==[0x11111111,0x22222222,0x33333333,0x44444444],'RenderBatch: Durchgang 1 baut alle, kein weiterer (calls=%s)'%c)
c,dsp,regs=render_case(lambda n,i: [0] if i==2 and n==3 else [], [1,0,0])
ok(c==[0,1,2,0] and dsp==4 and regs==[0x11111111,0x22222222,0x33333333,0x44444444],'RenderBatch: verdraengter String im 2. Durchgang neu (calls=%s)'%c)
c,dsp,regs=render_case(lambda n,i: [(i+1)%3], [1,1,1])
ok(len(c)<=3+3*3 and dsp==4 and regs==[0x11111111,0x22222222,0x33333333,0x44444444],'RenderBatch: Dauer-Verdraengung endet nach 4 Durchgaengen (%d Aufrufe)'%len(c))
c,dsp,regs=render_case(lambda n,i: [], [0,0,0])
ok(c==[0,1,2] and dsp==4,'RenderBatch: nichts verdraengt -> ein Durchgang (calls=%s)'%c)
# ---------- TextureCallback ----------
for cmd in (1,0,2):
    e=new()
    e.mu.mem_write(0xC7D328-4,b'\x77'*4+b'\xAA'*0x20000+b'\x77'*4)
    res={}
    def at(em):
        mu=em.mu; res['ebp']=mu.reg_read(UC_X86_REG_EBP); res['esp']=mu.reg_read(UC_X86_REG_ESP)
        res['regs']=[mu.reg_read(x) for x in (UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDI)]
        res['zf']=(mu.reg_read(UC_X86_REG_EFLAGS)>>6)&1; mu.emu_stop()
    e.watch_at(0x6C9F58,at)
    sp=0x200F0000-36
    vals=[0x31000000,cmd]+[0x100+k for k in range(7)]
    for k,v in enumerate(vals): e.w32(sp+4*k,v)
    e.mu.reg_write(UC_X86_REG_ESP,sp); e.mu.reg_write(UC_X86_REG_EAX,0xAAAA0001); e.mu.reg_write(UC_X86_REG_ECX,0xCCCC0002); e.mu.reg_write(UC_X86_REG_EDI,0xDDDD0003); e.mu.reg_write(UC_X86_REG_EBP,0x44444444)
    e.mu.emu_start(0x6C9F50,0x31000000,count=200000)
    buf=bytes(e.mu.mem_read(0xC7D328-4,0x20008))
    zeroed=buf[4:-4]==b'\0'*0x20000; edges=buf[:4]==b'\x77'*4 and buf[-4:]==b'\x77'*4
    ok((zeroed==(cmd==1)) and edges and (buf[4:-4]==b'\xAA'*0x20000 or cmd==1) and res['regs']==[0xAAAA0001,0xCCCC0002,0xDDDD0003] and res['zf']==(1 if cmd==1 else 0) and res['ebp']==sp-4 and res['esp']==sp-8 and e.r32(sp-4)==0x44444444,
       'TextureCallback Befehl %d: Puffer %s, Register/Flags/Frame ok'%(cmd,'geleert' if zeroed else 'unveraendert'))
# hook bytes
for va,n in ((0x6C5120,6),(0x6C6B90,6),(0x6C4AD0,6),(0x6C9F50,8)):
    b=bytes(e.mu.mem_read(va,n)); ok(b[0]==0xE9 and all(x==0x90 for x in b[5:]),'Hook %X: %s'%(va,b.hex()))
print('FAILS',fails)

from emu import *
import datetime as dtm, itertools, random

def pack(mi,hr,wd,md,mo,yr,fl=0):
    return (mi&63)|((hr&31)<<6)|((wd&7)<<11)|((md&63)<<14)|((mo&15)<<20)|((yr&31)<<24)|((fl&3)<<29)
W=lambda E,a: tuple(E.s32(a+4*i) for i in range(8))
def setw(E,a,v):
    for i,x in enumerate(v): E.w32(a+4*i,x)

def norm(Y,M,D,hh,mm):
    # mktime-artige Normalisierung (Monat/Tag duerfen ausserhalb liegen)
    Y+= M//12; M%=12
    base=dtm.datetime(Y,M+1,1)
    return base+dtm.timedelta(days=D-1,hours=hh,minutes=mm)
def wb(E,this,dt,keep):
    if not (1970<=dt.year<=2037):
        E.w32(this+0x14,-100); E.w32(this+0x10,0); E.w32(this+0xc,-1); E.w32(this+8,0); return
    E.w32(this+0x14,dt.year-2000); E.w32(this+0x10,dt.month-1); E.w32(this+0xc,dt.day-1); E.w32(this+8,(dt.weekday()+1)%7)
    if keep: E.w32(this+4,dt.hour); E.w32(this,dt.minute)
def add_days(E,this,days,keep):
    t=W(E,this)
    if t[5]<0 or t[4]<0 or t[3]<0: return False
    hh=t[1] if keep and t[1]>=0 else 0; mm=t[0] if keep and t[0]>=0 else 0
    dt=norm(2000+t[5],t[4],t[3]+1,hh,mm)+dtm.timedelta(days=days)
    wb(E,this,dt,keep); return True
def s_adddays(E,a):
    this=E.reg(UC_X86_REG_ECX); E.log.append(('AddDays',W(E,this),E.s32v(a[0]),a[1]&0xFF))
    add_days(E,this,E.s32v(a[0]),a[1]&0xFF); return None
def s_addmin(E,a):
    this=E.reg(UC_X86_REG_ECX); m=E.s32v(a[0]); E.log.append(('AddMin',W(E,this),m))
    t=W(E,this)
    if t[5]<0 or t[4]<0 or t[3]<0: return None
    dt=norm(2000+t[5],t[4],t[3]+1,max(t[1],0),max(t[0],0))+dtm.timedelta(minutes=m)
    wb(E,this,dt,True); return None
def s_setmin(E,a):
    this=E.reg(UC_X86_REG_ECX); m=E.s32v(a[0]); E.log.append(('3F0',W(E,this),m))
    t=W(E,this)
    tod=(max(t[1],0)*60+max(t[0],0))+m
    days=tod//1440; tod%=1440
    if days: add_days(E,this,days,False)
    E.w32(this+4,tod//60); E.w32(this,tod%60); return None
def s_tz(E,a):
    this=E.reg(UC_X86_REG_ECX); t=W(E,this); E.log.append(('TZ',t))
    if t[7]==0: return None
    try: dt=norm(2000+t[5],t[4],t[3]+1,t[1],t[0])+dtm.timedelta(hours=t[7]-2)
    except Exception as ex: E.log.append(('TZERR',str(ex))); return None
    wb(E,this,dt,True); E.w32(this+8,-1); return None
def s_lookup(E,a):
    E.log.append(('lookup',a[0])); return 0

def mk(data):
    E=Emu(data)
    E.s32v=lambda v: struct.unpack('<i',struct.pack('<I',v&0xFFFFFFFF))[0]
    E.stub(0x76C280,s_adddays,2,8)
    E.stub(0x76C4C0,s_addmin,1,4)
    E.stub(0x76C3F0,s_setmin,1,4)
    E.stub(0x76CBA0,s_tz,1,4)
    E.stub(0x6F6020,s_lookup,2,8)
    return E

NOW=0x30001000; WS=0x30001100; WE=0x30001200; OUTE=0x30001300; OUTS=0x30001400; REC=0x30002000; FLAG=0x30001500
def run(E,case):
    dates,durs,loop,flags,stage,now,ws,we,view,tz=case
    E.log=[]
    for i in range(0x100//4): E.w32(REC+4*i,0)
    E.w32(REC,301)
    for i,v in enumerate(durs): E.w32(REC+4+4*i,v)
    for i,v in enumerate(dates): E.w32(REC+0x2C+4*i,v)
    E.w32(REC+0x98,loop); E.w32(REC+0xD8,flags)
    setw(E,NOW,now); setw(E,WS,ws); setw(E,WE,we); setw(E,OUTE,[0x55555555]*8); setw(E,OUTS,[0x66666666]*8)
    E.mu.mem_write(FLAG,b'\x77')
    E.w32(0xACFF90,view[0]); E.w32(0xACFF8C,view[1]); E.w32(0xD37FAC,now[5]); E.w32(0xD37FB4,tz)
    r,_=E.call(0x5BFAB0,(NOW,WS,WE,OUTE,REC,stage,FLAG,10080),regs={UC_X86_REG_EBX:OUTS})
    return (r&0xFF, W(E,OUTS), W(E,OUTE), bytes(E.mu.mem_read(FLAG,1)), tuple(E.log))

random.seed(2031)
cases=[]
def now_t(y,mo,md,hh=12,mm=0,wd=None):
    if wd is None: wd=(dtm.date(2000+y,mo+1,md+1).weekday()+1)%7
    return [mm,hh,wd,md,mo,y,0,0]
for y in (8,24,26,30,31):
    for mo in (0,5,11):
        now=now_t(y,mo,14)
        ws=now_t(y,mo,8); we=now_t(y+ (1 if mo==11 else 0),(mo+1)%12,25)
        for view in ((y,mo),(y,(mo+1)%12),(-1,-1)):
            for flags in (0,1):
                for tz in (0,5):
                    for loop in (0,1):
                        datesets=[
                          [pack(0,0,7,20,5,31)],                         # jaehrlich (Jahr-Platzhalter) 21.6.
                          [pack(0,0,7,14,11,31),pack(0,0,7,0,0,31)],      # jaehrlich, mehrere
                          [pack(0,14,0,63,15,31)],                        # woechentlich (So 14:00)
                          [pack(0,14,0,63,15,31,1)],                      # woechentlich mit Flag-Bits
                          [pack(0,0,7,mo*2%28,mo,y)],                     # explizit dieses Jahr
                          [pack(0,0,7,3,2,yy) for yy in (8,9,10,30)]+[pack(0,0,7,3,2,31)], # explizit, inkl. 31
                          [pack(30,6,3,10,4,31)],                         # jaehrlich mit Wochentag
                          [pack(63,31,7,63,15,31)],                       # alles Platzhalter
                        ]
                        for ds in datesets:
                            for stage in (0,1):
                                cases.append((ds,[48,24,0,0],loop,flags,stage,now,ws,we,view,tz))
print('cases',len(cases))
EO=mk(ORIG); EP=mk(PATCHED)
nd=0; first=None
for c in cases:
    a=run(EO,c); b=run(EP,c)
    if a!=b:
        nd+=1
        if first is None: first=(c,a,b)
print('diffs',nd)
if first:
    c,a,b=first; print('case',c); print('orig ',a[:4]); print('patch',b[:4])
    for x,y in zip(a[4],b[4]):
        if x!=y: print(' log orig',x,'\n log patc',y); break
print('HOLIDAY EQUIV OK' if nd==0 else 'HOLIDAY EQUIV FAIL')
# Stichprobe: Ergebnisse zeigen, dass die Faelle wirklich verschiedene Pfade nehmen
seen=set(run(EP,c)[0] for c in cases[:200]); print('ret values seen',seen)

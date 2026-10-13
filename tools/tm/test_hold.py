import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from emu2 import *
D=open(sys.argv[1],'rb').read()
fails=0
def ok(c,msg):
    global fails
    print(('OK   ' if c else 'FAIL ')+msg)
    if not c: fails+=1
H=0x30000000
e=Emu2(D); e.mu.mem_write(H,b'\0'*0x100000)
SEC=e.secs['.hrep']
ST={'now':1000,'cmd':b'ACTIONBUTTON3','entry':1,'cd':(0,0),'uses':[],'origexec':[],'events':[],'origret':0x77}
CMD=H+0x500
def red(em,a):
    # thiscall (keyMode, slot, buf, size) callee pops 16
    ST['red']=a; return 0 if not ST['entry'] else H+0x400
e.stub(0x5622E0,red,4,16)
def getcmd(em,a):
    em.mu.mem_write(CMD,ST['cmd']+b'\0'); return CMD
e.stub(0x55E470,getcmd,2,8)
e.stub(0x86AE20,lambda em,a: ST['now'],0,0)
e.stub(0x47D3C0,lambda em,a: ST['events'].append(a),4,0)
PLAYER=H+0x9000
ST['player']=PLAYER
def actguid(em,a):
    em.mu.reg_write(UC_X86_REG_EDX,0x07000000); return 0x1234
e.stub(0x4D3790,actguid,0,0)
def objptr(em,a):
    ST['objargs']=a
    return ST['player'] if a[0]==0x1234 and a[1]==0x07000000 else 0
e.stub(0x4D4DB0,objptr,5,0)
def gcd(em,a):
    s,d=ST['cd']; em.w32(a[1],s); em.w32(a[2],d); em.w32(a[3],1); ST.setdefault('gcdslots',[]).append(a[0])
e.stub(0x5A8E40,gcd,4,0)
def leave(em,popargs,ret):
    mu=em.mu; ebp=mu.reg_read(UC_X86_REG_EBP)
    r=em.r32(ebp+4); old=em.r32(ebp)
    mu.reg_write(UC_X86_REG_ESP,ebp+8+popargs); mu.reg_write(UC_X86_REG_EBP,old); mu.reg_write(UC_X86_REG_EIP,r)
    if ret is not None: mu.reg_write(UC_X86_REG_EAX,ret)
def origexec(em):
    ebp=em.mu.reg_read(UC_X86_REG_EBP)
    ST['origexec'].append(([em.r32(ebp+8+4*k) for k in range(5)], em.mu.reg_read(UC_X86_REG_ECX), em.r32(SEC+0x100)))
    leave(em,0x14,ST['origret'])
e.watch_at(0x563159,origexec)
def origuse(em):
    ebp=em.mu.reg_read(UC_X86_REG_EBP)
    ST['uses'].append((em.r32(ebp+8),em.r32(ebp+12),em.r32(ebp+16),em.r32(em.r32(ebp+12)),bytes(em.mu.mem_read(em.r32(ebp+16),1))))
    leave(em,0,None)
e.watch_at(0x5ABBC6,origuse)
def origrender(em): ST['rendered']=ST.get('rendered',0)+1; leave(em,0,1)
e.watch_at(0x4F8EA6,origrender)
SELF=H+0x600
def setpage(cur=0,bonus=0,temp=0): e.w32(0xC1E598,cur); e.w32(0xC1E59C,bonus); e.w32(0xC1E5A0,temp)
def execkey(slot,down,keymode=0,mods=0):
    r,dsp=e.call(0x563150,(mods,slot,down,0,keymode),regs={UC_X86_REG_ECX:SELF})
    return r,dsp
def entry(i):
    b=SEC+32*i; return [e.r32(b+4*k) for k in range(7)]
def render():
    r,dsp=e.call(0x4F8EA0,(),regs={UC_X86_REG_ECX:H+0x700}); return r,dsp
setpage(); e.w32(0xD3F4E4,0)
r,dsp=execkey(0x111,1)
ok(r==0x77 and dsp==4+0x14 and len(ST['origexec'])==1 and ST['origexec'][0][0]==[0,0x111,1,0,0] and ST['origexec'][0][1]==SELF,'ExecKey runter: Original laeuft mit allen Argumenten, Rueckgabe/Stack ok (esp+%d)'%dsp)
ok(entry(0)==[0x111,2,1000,1000,0,0,1],'Eintrag: Taste 0x111, Slot 2 (ACTIONBUTTON3, Seite 1), Zeit 1000, aktiv %s'%entry(0))
ok(len(ST['events'])==1 and ST['events'][0][0]==2 and ST['events'][0][1]==SEC+0x2EF and ST['events'][0][2]==0 and ST['events'][0][3]==0,'Fokus-Ereignis angemeldet %s'%ST['events'])
ok(ST['red'][0]==0 and ST['red'][1]==0x111 and ST['red'][3]==0x80,'GetReducedKeyBinding-Argumente %s'%(ST['red'],))
regs=[e.reg(x) for x in (UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP)]
ok(regs==[0x11111111,0x22222222,0x33333333,0x44444444],'ExecKey: ebx/esi/edi/ebp erhalten')
for now,cd,exp,msg in ((1200,(0,0),0,'200 ms: noch nichts'),(1500,(0,0),0,'500 ms: bereit seit jetzt, Wartezeit 100 ms'),(1599,(0,0),0,'599 ms: noch nicht'),
                       (1600,(0,0),1,'600 ms: erste Wiederholung'),(1650,(0,0),0,'Abstand < 100 ms: nichts'),
                       (1700,(1600,1500),0,'globale Abklingzeit: nichts'),(3099,(1600,1500),0,'noch in Abklingzeit'),(3100,(1600,1500),0,'Abklingzeit vorbei: Wartezeit'),(3199,(1600,1500),0,'Wartezeit laeuft'),(3200,(1600,1500),1,'nach Wartezeit: Wiederholung'),(3299,(0,0),0,'Abstand < 100 ms'),(3300,(0,0),1,'Abstand 100 ms: Wiederholung')):
    ST['now']=now; ST['cd']=cd; n=len(ST['uses'])
    r,dsp=render()
    got=len(ST['uses'])-n
    ok(got==exp and r==1 and dsp==4,'Tick %d: %s (UseAction %dx, Rueckgabe %d)'%(now,msg,got,r))
u=ST['uses'][-1]
ok(u[0]==2 and u[3]==0 and u[4]==b'\0','UseAction(Slot 2, GUID 0, leerer Text) %s'%(u,))
ok(entry(0)[3]==3300 and entry(0)[5]==1,'letzte Wiederholung 3300, wiederholt-Merker gesetzt')
e.w32(0xD3F4E4,0x1234); ST['now']=5000; ST['cd']=(0,0); n=len(ST['uses']); render()
ok(len(ST['uses'])==n and entry(0)[4]==0,'laufender Zauber: keine Wiederholung')
e.w32(0xD3F4E4,0)
# key up after a repeat -> suppressed
r,dsp=execkey(0x111,0)
ok(ST['origexec'][-1][2]==1 and e.r32(SEC+0x100)==0 and entry(0)[6]==0 and r==0x77 and dsp==4+0x14,'Loslassen nach Wiederholung: Original laeuft mit Unterdrueckung, danach aufgehoben, Eintrag inaktiv')
# UseAction with suppress flag
e.w32(SEC+0x100,1); n=len(ST['uses']); r,dsp=e.call(0x5ABBC0,(5,H+0x800,H+0x810))
ok(len(ST['uses'])==n and e.r32(SEC+0x100)==0 and dsp==4,'UseAction unterdrueckt einmal und loescht den Merker')
r,dsp=e.call(0x5ABBC0,(5,H+0x800,H+0x810))
ok(len(ST['uses'])==n+1 and ST['uses'][-1][0]==5 and dsp==4,'UseAction danach normal')
# key up without repeat -> no suppression
ST['now']=10000; execkey(0x222,1); ST['now']=10100; execkey(0x222,0)
ok(ST['origexec'][-1][2]==0 and entry(0)[6]==0,'kurzer Druck: normales Ausloesen beim Loslassen (keine Unterdrueckung)')
ok(len(ST['events'])==1,'Fokus-Ereignis nur einmal angemeldet')
# page logic
def slot_for(cmd,cur=0,bonus=0,temp=0):
    ST['cmd']=cmd; setpage(cur,bonus,temp)
    for i in range(8): e.w32(SEC+32*i+24,0)
    execkey(0x333,1); en=entry(0); return en[1] if en[6] else None
for cmd,pg,exp in ((b'ACTIONBUTTON1',(0,0,0),0),(b'actionbutton12',(0,0,0),11),(b'ActionButton1',(0,1,0),72),(b'ACTIONBUTTON2',(0,3,0),97),
                   (b'ACTIONBUTTON1',(2,0,0),24),(b'ACTIONBUTTON1',(2,1,0),24),(b'ACTIONBUTTON4',(3,0,1),3),(b'ACTIONBUTTON4',(3,2,1),87),
                   (b'ACTIONBUTTON13',(0,0,0),None),(b'ACTIONBUTTON0',(0,0,0),None),(b'ACTIONBUTTON',(0,0,0),None),(b'MULTIACTIONBAR1BUTTON1',(0,0,0),None),
                   (b'ACTIONBUTTON1234567890123',(0,0,0),None),(b'JUMP',(0,0,0),None)):
    got=slot_for(cmd,*pg)
    ok(got==exp,'%s Seite/Bonus/Temp %s -> Slot %s'%(cmd.decode(),pg,got))
ST['cmd']=b'ACTIONBUTTON1'; setpage()
ST['entry']=0
for i in range(8): e.w32(SEC+32*i+24,0)
n=len(ST['origexec']); execkey(0x444,1)
ok(entry(0)[6]==0 and len(ST['origexec'])==n+1,'keine Belegung: kein Eintrag, Original laeuft')
ST['entry']=1
# 9 keys
for i in range(8): e.w32(SEC+32*i+24,0)
for k in range(9): execkey(0x1000+k,1)
ok(all(entry(i)[6]==1 for i in range(8)) and [entry(i)[0] for i in range(8)]==[0x1000+i for i in range(8)],'8 Tasten gleichzeitig, die 9. wird ignoriert')
# same key again reuses entry
ST['now']=20000; execkey(0x1003,1)
ok(entry(3)[2]==20000 and sum(1 for i in range(8) if entry(i)[0]==0x1003)==1,'erneutes Druecken derselben Taste nutzt denselben Eintrag')
# focus handler
r,dsp=e.call(SEC+0x2EF,(0,0))
ok(r==1 and dsp==4 and all(entry(i)[6]==0 for i in range(8)),'Fokus-Handler: alle Tasten vergessen, Rueckgabe 1')
ST['now']=30000; n=len(ST['uses']); render()
ok(len(ST['uses'])==n,'nach Fokusverlust keine Wiederholung')
for va,n_ in ((0x563150,9),(0x5ABBC0,6),(0x4F8EA0,6)):
    b=bytes(e.mu.mem_read(va,n_)); ok(b[0]==0xE9 and all(x==0x90 for x in b[5:]),'Hook %X: %s'%(va,b.hex()))
ok(bytes(e.mu.mem_read(SEC+0x114,12))==b'ACTIONBUTTON','Text ACTIONBUTTON in der Sektion')
# ---- cast bar / channel ----
for i in range(8): e.w32(SEC+32*i+24,0)
ST['cmd']=b'ACTIONBUTTON1'; setpage(); e.w32(0xD3F4E4,0); ST['cd']=(0,0)
ST['now']=40000; execkey(0x555,1)
def tick(now):
    ST['now']=now; n=len(ST['uses']); render(); return len(ST['uses'])-n
P=PLAYER
e.w32(P+0xA6C,133); e.w32(P+0xA7C,42500)          # casting until 42500
r1=tick(40600); r2=tick(41500); r3=tick(42499)
ok(r1==0 and r2==0 and r3==0 and entry(0)[4]==0,'Zauberleiste laeuft (GCD laengst vorbei): keine Wiederholung')
ok(ST['objargs'][2]==0x10,'Spieler-Objekt per GUID und Typmaske 0x10 geholt %s'%(ST['objargs'],))
r4=tick(42500); r5=tick(42599); r6=tick(42600)
ok(r4==0 and r5==0 and r6==1,'nach Zauberende (Zauber-ID bleibt stehen): 100 ms Wartezeit, dann Wiederholung (%d,%d,%d)'%(r4,r5,r6))
e.w32(P+0xA6C,0); e.w32(P+0xA80,5143); e.w32(P+0xA88,45000)   # channel until 45000
r=[tick(t) for t in (43000,44000,44999)]
ok(r==[0,0,0],'Kanalisierung laeuft: keine Wiederholung %s'%r)
r=[tick(t) for t in (45000,45100)]
ok(r==[0,1],'nach Kanalisierungsende: Wartezeit, dann Wiederholung %s'%r)
e.w32(P+0xA80,0); ST['player']=0
r=[tick(t) for t in (46000,47000)]
ok(r==[0,0],'kein Spieler-Objekt: keine Wiederholung')
ST['player']=P
r=[tick(t) for t in (47100,47200)]
ok(r==[0,1],'Spieler wieder da, nichts aktiv: Wartezeit, dann Wiederholung %s'%r)
print('FAILS',fails)

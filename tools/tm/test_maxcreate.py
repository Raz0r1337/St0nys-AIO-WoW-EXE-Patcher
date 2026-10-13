from emu import *
W=lambda E,a: tuple(E.s32(a+4*i) for i in range(8))
def mk(data):
    E=Emu(data)
    def s_add(E,a):
        this=E.reg(UC_X86_REG_ECX); E.log.append(('AddDays',W(E,this),a[0],a[1]))
        # Monatsletzter: (Y,M,0) -1 Tag
        t=W(E,this); import calendar
        Y,M=2000+t[5],t[4]
        if t[5]<0 or M<0: return None
        M-=1
        if M<0: M=11; Y-=1
        E.w32(this+0x14,Y-2000); E.w32(this+0x10,M); E.w32(this+0xc,calendar.monthrange(Y,M+1)[1]-1)
        return None
    def s_set(E,a):
        this=E.reg(UC_X86_REG_ECX); E.log.append(('SetTime',a[0],a[1])); E.w32(this+4,a[0]); E.w32(this,a[1]); return 1
    E.stub(0x76C280,s_add,2,8); E.stub(0x76C3C0,s_set,2,8)
    return E
EO=mk(ORIG); EP=mk(PATCHED)
OUT=0x30003000
bad=0; n=0; changed=0
for y in range(-1,33):
    for m in range(-1,12):
        res=[]
        for E in (EO,EP):
            E.log=[]
            for i in range(8): E.w32(OUT+4*i,0x77777777)
            E.w32(0xD37FAC,y); E.w32(0xD37FA8,m)
            r,dsp=E.call(0x5B7A80,(OUT,),regs={UC_X86_REG_ESI:0x22222222,UC_X86_REG_EBP:0x44444444})
            res.append((E.log[0][1][3:6], W(E,OUT), dsp, E.reg(UC_X86_REG_ESI), E.reg(UC_X86_REG_EBP)))
        o,p=res; n+=1
        tot=12*y+m+13
        exp_before = o[0] if tot<=384 else (0,0,32)
        ok = p[0]==exp_before and p[2]==o[2]==4 and p[3]==0x22222222 and p[4]==0x44444444
        if tot<=384: ok = ok and p[1]==o[1]
        else:
            ok = ok and p[1][5]==31 and p[1][4]==11 and p[1][3]==30
            changed+=1
        if not ok:
            bad+=1
            if bad<5: print('BAD',y,m,'orig',o,'patch',p)
print('cases',n,'clamped',changed,'bad',bad)
print('MAXCREATE OK' if bad==0 else 'MAXCREATE FAIL')
# Beispiele
for y,m in ((26,9),(30,2),(30,11),(31,0),(31,5),(31,11)):
    EP.log=[]; EP.w32(0xD37FAC,y); EP.w32(0xD37FA8,m); EP.call(0x5B7A80,(OUT,))
    t=W(EP,OUT); EO.log=[]; EO.w32(0xD37FAC,y); EO.w32(0xD37FA8,m); EO.call(0x5B7A80,(OUT,)); u=W(EO,OUT)
    print('heute %02d/%d -> max orig %d.%d.%d  patched %d.%d.%d'%(m+1,2000+y,u[3]+1,u[4]+1,2000+u[5],t[3]+1,t[4]+1,2000+t[5]))

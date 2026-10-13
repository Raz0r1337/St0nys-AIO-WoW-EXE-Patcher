import sys,struct; sys.path.insert(0,'ml'); from h import *
from unicorn import *; from unicorn.x86_const import *
IMG=0x400000
def run(patched, dpc_ms=0.0, qpc_backwards=False, ncpu=8):
    mu=Uc(UC_ARCH_X86,UC_MODE_32)
    size=0x9DE400-0x401000
    mu.mem_map(0x401000,0x5DE000)
    text=bytearray(d[0x400:0x400+size])
    if patched:
        o=0x86AC8E-0x401000; text[o:o+6]=bytes([0xE9])+struct.pack('<i',0x86AD16-0x86AC93)+b'\x90'
    # interne Helfer stubben: 0x86b280 (cdecl, Sleep-artig) -> ret ; 0x86b240 -> eax=ncpu ; ret
    o=0x86B280-0x401000; text[o:o+1]=b'\xC3'
    o=0x86B240-0x401000; text[o:o+6]=b'\xB8'+struct.pack('<I',ncpu)+b'\xC3'
    mu.mem_write(0x401000,bytes(text))
    mu.mem_map(0x9DF000,0xD7000); mu.mem_write(0x9DF000,d[0x5DD800:0x5DD800+0xD6800])  # .rdata inkl. IAT
    STUB=0x30000000; mu.mem_map(STUB,0x1000)
    apis={0x9df324:('QPF',1),0x9df1c0:('GetCurrentProcess',0),0x9df220:('GetCurrentThread',0),0x9df2a8:('GetPriorityClass',1),
          0x9df2fc:('GetThreadPriority',1),0x9df2ac:('SetPriorityClass',2),0x9df2f8:('SetThreadPriority',2),0x9df174:('GetTickCount',0),
          0x9df178:('QPC',1),0x9df300:('GetProcessAffinityMask',3),0x9df364:('SetThreadAffinityMask',2)}
    addr={}
    for i,(iat,(n,argc)) in enumerate(apis.items()):
        a=STUB+i*16; addr[a]=(n,argc); mu.mem_write(iat,struct.pack('<I',a))
        mu.mem_write(a,b'\xC2'+struct.pack('<H',argc*4) if argc else b'\xC3')
    st={'t':123456.789,'qpc_calls':0,'core':0,'prio':[]}   # t in ms
    def tick(dt): st['t']+=dt
    def hook(uc,a,sz,ud):
        if a not in addr: return
        n,argc=addr[a]; sp=uc.reg_read(UC_X86_REG_ESP)
        args=struct.unpack('<%dI'%argc,bytes(uc.mem_read(sp+4,4*argc))) if argc else ()
        tick(0.0005)
        r=0
        if n=='QPF': uc.mem_write(args[0],struct.pack('<Q',10_000_000)); r=1
        elif n=='GetCurrentProcess': r=0xFFFFFFFF
        elif n=='GetCurrentThread': r=0xFFFFFFFE
        elif n=='GetPriorityClass': r=0x20
        elif n=='GetThreadPriority': r=0
        elif n in ('SetPriorityClass','SetThreadPriority'): st['prio'].append((n,args[1])); r=1
        elif n=='GetTickCount': r=int(int(st['t']/15.625)*15.625)
        elif n=='QPC':
            st['qpc_calls']+=1
            caller=struct.unpack('<I',bytes(uc.mem_read(sp,4)))[0]
            if caller==0x86ACBA and dpc_ms: tick(dpc_ms)      # Verzoegerung vor dem End-QPC
            v=int(st['t']*10_000)
            if qpc_backwards and st['core']%2==1: v-=5000
            uc.mem_write(args[0],struct.pack('<Q',v)); r=1
        elif n=='GetProcessAffinityMask': uc.mem_write(args[1],struct.pack('<I',(1<<ncpu)-1)); uc.mem_write(args[2],struct.pack('<I',(1<<ncpu)-1)); r=1
        elif n=='SetThreadAffinityMask':
            m=args[1]; st['core']=(m.bit_length()-1) if m else 0; tick(0.01); r=1
        uc.reg_write(UC_X86_REG_EAX,r)
    mu.hook_add(UC_HOOK_CODE,hook,begin=STUB,end=STUB+0x1000)
    # this-Objekt + Stack
    mu.mem_map(0x10000000,0x1000); this=0x10000100
    mu.mem_map(0x20000000,0x10000); sp=0x2000F000
    RET=0x31000000; mu.mem_map(RET,0x1000)
    sp-=4; mu.mem_write(sp,struct.pack('<I',RET))
    for r,v in ((UC_X86_REG_ESP,sp),(UC_X86_REG_ECX,this),(UC_X86_REG_EBX,0x11111111),(UC_X86_REG_ESI,0x22222222),(UC_X86_REG_EDI,0x33333333),(UC_X86_REG_EBP,0x44444444)):
        mu.reg_write(r,v)
    mu.emu_start(0x86AB30,RET,count=5_000_000)
    res=mu.reg_read(UC_X86_REG_EAX); err=struct.unpack('<I',bytes(mu.mem_read(this+0xc,4)))[0]
    regs=[hex(mu.reg_read(r)) for r in (UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP)]
    ok_regs=regs==['0x11111111','0x22222222','0x33333333','0x44444444'] and mu.reg_read(UC_X86_REG_ESP)==sp+4
    return res,err,ok_regs,st['prio'],round(st['t']-123456.789,1)
for name,kw in (('normal',{}),('DPC 6ms',{'dpc_ms':6.0}),('QPC rueckwaerts',{'qpc_backwards':True}),('1 Kern',{'ncpu':1}),('1 Kern + DPC',{'ncpu':1,'dpc_ms':6.0})):
    for p in (False,True):
        res,err,okr,prio,dt=run(p,**kw)
        print('%-16s %-9s -> Methode %d (%s), Fehler %d, Register ok: %s, Prioritaet zurueck: %s, Dauer %.1f ms'%(name,'Patch' if p else 'Original',res,'QPC' if res==2 else 'GetTickCount',err,okr,prio[-2:],dt))

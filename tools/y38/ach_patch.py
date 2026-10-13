from common import *
import keystone, unicorn, struct
from unicorn.x86_const import *
ks=keystone.Ks(keystone.KS_ARCH_X86,keystone.KS_MODE_32)
def asm(code,addr):
    b,_=ks.asm(code,addr); return bytes(b)
blocks={
 'GetAchievementInfo':(0x5B4626,0x5B4662,'ebx','ebp-0xc'),
 'GetAchievementComparisonInfo':(0x5B47FD,0x5B4839,'esi','ebp-8'),
}
res={}
for nm,(s,e,L,tmp) in blocks.items():
    code=f'''
    fild dword ptr [edi+0x1c]
    fld1
    faddp st(1), st(0)
    fstp qword ptr [esp]
    push {L}
    call 0x84e2a0
    fild dword ptr [edi+0x18]
    fld1
    faddp st(1), st(0)
    add esp,4
    fstp qword ptr [esp]
    push {L}
    call 0x84e2a0
    mov eax,dword ptr [edi+0x20]
    add eax,0x1c
    mov dword ptr [{tmp}],eax
    fild dword ptr [{tmp}]
    add esp,4
    fstp qword ptr [esp]
    push {L}
    call 0x84e2a0
    '''
    b=asm(code,s)
    n=e-s
    assert len(b)<=n,(nm,len(b),n)
    b=b+b'\x90'*(n-len(b))
    res[nm]=(s,d[va2fo(s):va2fo(s)+n],b)
# tooltip link parser: 62DEE9..62DEF5
s=0x62DEE9; e=0x62DEF5
code='''
inc esi
push esi
call 0x76f0d0
add al,0x1c
mov dword ptr [ebp-0x30],eax
'''
b=asm(code,s); assert len(b)==e-s,(len(b))
res['AchievementLinkParse']=(s,d[va2fo(s):va2fo(s)+(e-s)],b)
import pickle; pickle.dump(res,open('ach_patch.pkl','wb'))
for k,(s,o,n) in res.items():
    print(k,hex(s),'fo',hex(va2fo(s)),len(o))
    print('  orig',o.hex()); print('  new ',n.hex())
    for i in md.disasm(n,s): print('     %08X %-16s %s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str))

# emulate
def emu(code_bytes,s,e,L,tmp,vals):
    mu=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_32)
    base=0x400000; mu.mem_map(base,0x1000000)
    text=d[0x400:0x5DD800]; mu.mem_write(0x401000,text)
    mu.mem_write(s,code_bytes)
    stk=0x2000000; mu.mem_map(stk-0x10000,0x20000)
    st=0x3000000; mu.mem_map(st,0x1000)
    mu.mem_write(st+0x18,struct.pack('<III',*vals))  # day@0x18, month@0x1c, year@0x20
    # vals order day,month,year
    got=[]
    def hook(uc,addr,size,ud):
        if addr==0x84e2a0:
            sp=uc.reg_read(UC_X86_REG_ESP)
            got.append(struct.unpack('<d',uc.mem_read(sp+8,8))[0])
            ret=struct.unpack('<I',uc.mem_read(sp,4))[0]
            uc.reg_write(UC_X86_REG_ESP,sp+4); uc.reg_write(UC_X86_REG_EIP,ret)
    mu.hook_add(unicorn.UC_HOOK_CODE,hook,begin=0x84e2a0,end=0x84e2a0)
    esp0=stk-0x100
    mu.reg_write(UC_X86_REG_ESP,esp0); mu.reg_write(UC_X86_REG_EBP,stk-0x40)
    mu.reg_write(UC_X86_REG_EDI,st)
    mu.reg_write(getattr(unicorn.x86_const,'UC_X86_REG_'+L.upper()),0x1234)
    mu.emu_start(s,e)
    return got, mu.reg_read(UC_X86_REG_ESP)-esp0
for k in ('GetAchievementInfo','GetAchievementComparisonInfo'):
    s,o,n=res[k]; e=s+len(o); L=blocks[k][2]; tmp=blocks[k][3]
    for vals in ((13,9,2),(0,0,30)):
        print(k,vals,'orig',emu(o,s,e,L,tmp,vals),'new',emu(n,s,e,L,tmp,vals))

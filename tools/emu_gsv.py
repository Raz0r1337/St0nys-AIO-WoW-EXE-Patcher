import struct
from unicorn import *
from unicorn.x86_const import *
orig=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
SECS=[(0x1000,0x5dd3b3,0x400,0x5dd400),(0x5df000,0xd6679,0x5dd800,0xd6800),(0x6b6000,0x31a508,0x6b4000,0x78e00)]
FO=0x1F8480
BORED_OLD=bytes.fromhex('558bece828e8ffff8b4508680005000050681844c200e8855c1700e8b0feffffc6051849c200015dc3cccccccc')
BORED_NEW=bytes.fromhex('558bece828e8ffff8b4508680005000068a084a300681844c200e8815c1700e8acfeffffc6051849c200015dc3')
MINE=(0x1F8488, bytes.fromhex('6a7f68a084a3009090'))
assert orig[FO:FO+45]==BORED_OLD
def variant(name):
    d=bytearray(orig)
    if name=='bored': d[FO:FO+45]=BORED_NEW
    if name=='mine': d[MINE[0]:MINE[0]+len(MINE[1])]=MINE[1]
    return bytes(d)
def run(d,arg=b'MYACCOUNT\0',prefill=b''):
    mu=Uc(UC_ARCH_X86,UC_MODE_32)
    for va,vs,ra,rs in SECS:
        base=0x400000+va; size=(max(vs,rs)+0xfff)&~0xfff
        mu.mem_map(base,size); mu.mem_write(base,d[ra:ra+min(rs,vs)])
    STK=0x100000; mu.mem_map(STK,0x10000); ARG=0x200000; mu.mem_map(ARG,0x1000); mu.mem_write(ARG,arg)
    if prefill: mu.mem_write(0xC24418,prefill)
    RET=0x300000; mu.mem_map(RET,0x1000); mu.mem_write(RET,b'\xf4')
    esp0=STK+0x8000
    mu.mem_write(esp0,struct.pack('<II',RET,ARG))   # [esp]=ret addr, [esp+4]=arg
    mu.reg_write(UC_X86_REG_ESP,esp0); mu.reg_write(UC_X86_REG_EBP,0x13579BDF)
    mu.reg_write(UC_X86_REG_EBX,0x11111111); mu.reg_write(UC_X86_REG_ESI,0x22222222); mu.reg_write(UC_X86_REG_EDI,0x33333333)
    stubs={0x5F78B0:0,0x5F8F50:0}
    calls=[]
    def hook(mu,addr,size,u):
        if addr in stubs:
            calls.append(addr)
            r=struct.unpack('<I',mu.mem_read(mu.reg_read(UC_X86_REG_ESP),4))[0]
            mu.reg_write(UC_X86_REG_ESP,mu.reg_read(UC_X86_REG_ESP)+4); mu.reg_write(UC_X86_REG_EIP,r)
        if addr==0x76ED20: calls.append(addr)
    mu.hook_add(UC_HOOK_CODE,hook)
    mu.emu_start(0x5F9080,RET,count=100000)
    buf=bytes(mu.mem_read(0xC24418,0x40)); flag=mu.mem_read(0xC24918,1)[0]
    return dict(buf=buf.split(b'\0')[0], esp_ok=(mu.reg_read(UC_X86_REG_ESP)==esp0+4), ebp=hex(mu.reg_read(UC_X86_REG_EBP)),
                ebx=hex(mu.reg_read(UC_X86_REG_EBX)), esi=hex(mu.reg_read(UC_X86_REG_ESI)), edi=hex(mu.reg_read(UC_X86_REG_EDI)),
                flag=flag, calls=[hex(c) for c in calls], tail=buf[:12].hex())
for n in ['orig','bored','mine']:
    print(n, run(variant(n)))
# leftover from a longer earlier name must not leak through
print('mine prefilled', run(variant('mine'),prefill=b'VERYLONGACCOUNTNAME\0'))
print('bored prefilled', run(variant('bored'),prefill=b'VERYLONGACCOUNTNAME\0'))
# code diff mine vs orig
d=variant('mine'); print('changed bytes mine:', sum(1 for i in range(len(d)) if d[i]!=orig[i]))
d=variant('bored'); print('changed bytes bored:', sum(1 for i in range(len(d)) if d[i]!=orig[i]))

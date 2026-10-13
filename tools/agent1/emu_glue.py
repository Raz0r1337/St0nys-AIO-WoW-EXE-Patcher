from lib import *
import struct
from unicorn import *
from unicorn.x86_const import *
pb=load_patched(14)
mu=Uc(UC_ARCH_X86,UC_MODE_32)
# map image (page aligned) 0x400000..0xA00000 and copy sections
mu.mem_map(0x400000,0xC00000)
for n,f,va,s in SECS: mu.mem_write(va,bytes(pb[f:f+s]))
# bss part of .data up to 0x9D0508 RVA -> VA 0xDD0508? .data virtual size extends; map extra zeros
pass
STACK=0x2000000; mu.mem_map(STACK,0x100000)
SCR=0x3000000; mu.mem_map(SCR,0x10000)
# fake addon record at SCR: [ebx+0x14]=name ptr, [ebx+0xd1]=0, [ebx+0x30]=heap-ish ptr
name=SCR+0x1000; mu.mem_write(name,b'MyAddon\0')
mu.mem_write(SCR+0x14,struct.pack('<I',name)); mu.mem_write(SCR+0x30,struct.pack('<I',0x4444444))
esp=STACK+0x80000; ebp=esp+0x300
mu.reg_write(UC_X86_REG_EBX,SCR); mu.reg_write(UC_X86_REG_ESP,esp); mu.reg_write(UC_X86_REG_EBP,ebp)
mu.reg_write(UC_X86_REG_ESI,name); mu.reg_write(UC_X86_REG_EDI,0x4444444)
log=[]
def hook_code(mu,addr,size,ud):
    if addr==0x76F070:   # SStrPrintf: emulate real one? just return (cdecl) - but it writes buffer; irrelevant
        ret=struct.unpack('<I',mu.mem_read(mu.reg_read(UC_X86_REG_ESP),4))[0]
        mu.reg_write(UC_X86_REG_ESP,mu.reg_read(UC_X86_REG_ESP)+4); mu.reg_write(UC_X86_REG_EIP,ret); log.append('SStrPrintf stub')
    elif addr==0x424E80: # SFileLoadFile: fail -> eax=0, ret 0x1C
        sp=mu.reg_read(UC_X86_REG_ESP); ret=struct.unpack('<I',mu.mem_read(sp,4))[0]
        args=[struct.unpack('<I',mu.mem_read(sp+4+4*i,4))[0] for i in range(7)]
        log.append('SFileLoadFile(%s) -> 0'%(['0x%X'%a for a in args]))
        mu.reg_write(UC_X86_REG_EAX,0); mu.reg_write(UC_X86_REG_ESP,sp+4+0x1C); mu.reg_write(UC_X86_REG_EIP,ret)
    elif addr==0x421CA0: # SFileUnloadFile
        sp=mu.reg_read(UC_X86_REG_ESP); arg=struct.unpack('<I',mu.mem_read(sp+4,4))[0]
        log.append('SFileUnloadFile(0x%X)  <- %s'%(arg, 'ptr to "%s" in .rdata'%cstr(d,arg).decode() if cstr(d,arg) else 'unknown'))
        ebp_=mu.reg_read(UC_X86_REG_EBP)
        log.append('  callee [ebp-4]=0x%X [ebp-8]=0x%X'%(struct.unpack('<I',mu.mem_read(ebp_-4,4))[0],struct.unpack('<I',mu.mem_read(ebp_-8,4))[0]))
        mu.emu_stop()
    elif addr==0x5F7B46: log.append('returned from 0x8165E0 with eax=0x%X'%mu.reg_read(UC_X86_REG_EAX)); mu.emu_stop()
mu.hook_add(UC_HOOK_CODE,hook_code)
try:
    mu.emu_start(0x5F7AE3,0x5F7B90,count=2000)
except UcError as e:
    log.append('emu error: %s at EIP 0x%X'%(e,mu.reg_read(UC_X86_REG_EIP)))
print('\n'.join(log))
# continue from SFileUnloadFile to see return value: resume after hooking unload as no-op
# second run: let SFileUnloadFile be a no-op and see the return value of 0x8165E0
log.clear()
def hook2(mu,addr,size,ud):
    if addr==0x76F070:
        ret=struct.unpack('<I',mu.mem_read(mu.reg_read(UC_X86_REG_ESP),4))[0]
        mu.reg_write(UC_X86_REG_ESP,mu.reg_read(UC_X86_REG_ESP)+4); mu.reg_write(UC_X86_REG_EIP,ret)
    elif addr==0x424E80:
        sp=mu.reg_read(UC_X86_REG_ESP); ret=struct.unpack('<I',mu.mem_read(sp,4))[0]
        mu.reg_write(UC_X86_REG_EAX,0); mu.reg_write(UC_X86_REG_ESP,sp+4+0x1C); mu.reg_write(UC_X86_REG_EIP,ret)
    elif addr==0x421CA0:
        sp=mu.reg_read(UC_X86_REG_ESP); ret=struct.unpack('<I',mu.mem_read(sp,4))[0]
        mu.reg_write(UC_X86_REG_EAX,1); mu.reg_write(UC_X86_REG_ESP,sp+8); mu.reg_write(UC_X86_REG_EIP,ret); log.append('SFileUnloadFile stubbed')
    elif addr==0x5F7B65:
        log.append('addon record [ebx+0x24]=0x%X [ebx+0x2a]=0x%X after sig check'%(struct.unpack('<I',mu.mem_read(SCR+0x24,4))[0], mu.mem_read(SCR+0x2a,1)[0])); mu.emu_stop()
    elif addr==0x5F7B46: log.append('0x8165E0 returned eax=0x%X'%mu.reg_read(UC_X86_REG_EAX))
mu2=Uc(UC_ARCH_X86,UC_MODE_32); mu2.mem_map(0x400000,0xC00000)
for n,f,va,s in SECS: mu2.mem_write(va,bytes(pb[f:f+s]))
mu2.mem_map(STACK,0x100000); mu2.mem_map(SCR,0x10000)
mu2.mem_write(name,b'MyAddon\0'); mu2.mem_write(SCR+0x14,struct.pack('<I',name)); mu2.mem_write(SCR+0x30,struct.pack('<I',0x4444444))
mu2.mem_write(SCR+0x24,struct.pack('<I',1))
mu2.reg_write(UC_X86_REG_EBX,SCR); mu2.reg_write(UC_X86_REG_ESP,esp); mu2.reg_write(UC_X86_REG_EBP,ebp); mu2.reg_write(UC_X86_REG_ESI,name); mu2.reg_write(UC_X86_REG_EDI,0x4444444)
mu2.hook_add(UC_HOOK_CODE,hook2)
try: mu2.emu_start(0x5F7AE3,0x5F7B90,count=3000)
except UcError as e: log.append('emu error: %s at EIP 0x%X'%(e,mu2.reg_read(UC_X86_REG_EIP)))
print('--- run 2'); print('\n'.join(log))

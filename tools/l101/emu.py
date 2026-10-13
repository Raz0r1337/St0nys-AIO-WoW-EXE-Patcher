import struct
from unicorn import *
from unicorn.x86_const import *
orig=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
acc0=open('acc0.bin','rb').read(); twin=open('twin.bin','rb').read()
patched=bytearray(orig); patched[0x3F5DB0:0x3F5DB0+48]=acc0; patched[0x3F5DE0:0x3F5DE0+47]=twin
STRIDE=100; RECS=0x300000
def run(img, fn, row, col, slot):
    mu=Uc(UC_ARCH_X86,UC_MODE_32)
    mu.mem_map(0x7F6000,0x2000); mu.mem_write(0x7F6000,bytes(img[0x3F5400:0x3F7400]))
    mu.mem_map(0x200000,0x10000); mu.mem_map(RECS,0x10000); mu.mem_map(0x100000,0x10000)
    obj=0x200000; meta=0x200100; cont=0x200200; vt=0x200300
    mu.mem_write(obj+8,struct.pack('<I',meta)); mu.mem_write(obj+0xC,struct.pack('<I',cont))
    mu.mem_write(meta+4,struct.pack('<I',STRIDE))
    mu.mem_write(cont+0x18,struct.pack('<I',vt)); mu.mem_write(vt+4,struct.pack('<I',0x7F7000))  # fake accessor
    mu.mem_write(0x7F7000,b'\xf4')
    for i in range(4000): mu.mem_write(RECS+8*i,struct.pack('<ff',float(i),float(i)+0.5))
    calls=[]
    def hook(mu,addr,size,u):
        if addr==0x7F7000:   # accessor(this=ecx, idx): returns &recs[idx], stdcall ret 4
            esp=mu.reg_read(UC_X86_REG_ESP); ret=struct.unpack('<I',mu.mem_read(esp,4))[0]; idx=struct.unpack('<i',mu.mem_read(esp+4,4))[0]
            calls.append(idx); mu.reg_write(UC_X86_REG_EAX,RECS+8*idx); mu.reg_write(UC_X86_REG_ESP,esp+8); mu.reg_write(UC_X86_REG_EIP,ret)
    mu.hook_add(UC_HOOK_CODE,hook)
    esp=0x108000; mu.mem_write(esp,struct.pack('<III',0x7F7800,row&0xffffffff,col)); mu.mem_map(0x7F8000,0x1000) if False else None
    mu.mem_write(0x7F7800,b'\xf4')
    mu.reg_write(UC_X86_REG_ESP,esp); mu.reg_write(UC_X86_REG_ECX,obj); mu.reg_write(UC_X86_REG_EBP,0xBEEF0000)
    mu.emu_start(fn,0x7F7800,count=200)
    # read st0 via FPU? unicorn: read ST0 register
    st0=mu.reg_read(UC_X86_REG_ST0)
    return calls[0] if calls else None, st0, mu.reg_read(UC_X86_REG_ESP)-esp-12, mu.reg_read(UC_X86_REG_EBP)
for slot,fn in ((0,0x7F69B0),(1,0x7F69E0)):
    for row,col in [(0,0),(50,3),(99,31),(100,0),(150,2),(-1,1)]:
        o=run(orig,fn,row,col,slot); p=run(patched,fn,row,col,slot)
        print('slot%d row=%4d col=%2d  orig idx=%5s st0=%s  | patched idx=%5s st0=%s  esp_ok=%s ebp_ok=%s'%(slot,row,col,o[0],o[1],p[0],p[1],p[2]==0,p[3]==0xBEEF0000))

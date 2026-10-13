import struct,sys
import os; _b=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(_b,'..','ml')); sys.path.insert(0,_b)
from unicorn import *; from unicorn.x86_const import *
import h
from patches import *

class Emu:
    def __init__(self, data):
        self.data=bytes(data)
        mu=Uc(UC_ARCH_X86,UC_MODE_32); self.mu=mu
        mu.mem_map(0x400000,0x9DF000-0x400000)                 # header + .text
        mu.mem_write(0x400000,self.data[:0x400]); mu.mem_write(0x401000,self.data[0x400:0x400+0x5DD400])
        mu.mem_map(0x9DF000,0xAB6000-0x9DF000); mu.mem_write(0x9DF000,self.data[0x5DD800:0x5DD800+0xD6800])
        mu.mem_map(0xAB6000,0xDD1000-0xAB6000); mu.mem_write(0xAB6000,self.data[0x6B4000:0x6B4000+0x78E00])
        mu.mem_map(0x20000000,0x100000)                        # stack
        mu.mem_map(0x30000000,0x100000)                        # heap/scratch
        mu.mem_map(0x31000000,0x1000)                          # return sentinel
        self.stubs={}; self.log=[]; self.stubs_pop={}
        self.watch={}
    def _hook(self,uc,addr,size,ud):
        if addr in self.watch: self.watch[addr](self)
        if addr in self.stubs:
            fn,nargs=self.stubs[addr]
            sp=uc.reg_read(UC_X86_REG_ESP)
            ret=struct.unpack('<I',bytes(uc.mem_read(sp,4)))[0]
            args=struct.unpack('<%dI'%nargs,bytes(uc.mem_read(sp+4,4*nargs))) if nargs else ()
            r=fn(self,args)
            if r is not None: uc.reg_write(UC_X86_REG_EAX,r&0xFFFFFFFF)
            pop=self.stubs_pop.get(addr,0)
            uc.reg_write(UC_X86_REG_ESP,sp+4+pop)
            uc.reg_write(UC_X86_REG_EIP,ret)
    def stub(self,addr,fn,nargs=0,callee_pop=0):
        self.stubs[addr]=(fn,nargs); self.stubs_pop[addr]=callee_pop
        self.mu.hook_add(UC_HOOK_CODE,self._hook,begin=addr,end=addr)
    def watch_at(self,addr,fn):
        self.watch[addr]=fn
        self.mu.hook_add(UC_HOOK_CODE,self._hook,begin=addr,end=addr)
    def r32(self,a): return struct.unpack('<I',bytes(self.mu.mem_read(a,4)))[0]
    def s32(self,a): return struct.unpack('<i',bytes(self.mu.mem_read(a,4)))[0]
    def w32(self,a,v): self.mu.mem_write(a,struct.pack('<I',v&0xFFFFFFFF))
    def reg(self,r): return self.mu.reg_read(r)
    def call(self,addr,args=(),regs=None,count=2_000_000):
        mu=self.mu
        sp=0x200F0000
        for a in reversed(args): sp-=4; mu.mem_write(sp,struct.pack('<I',a&0xFFFFFFFF))
        sp-=4; mu.mem_write(sp,struct.pack('<I',0x31000000))
        base={UC_X86_REG_EAX:0x0BADF00D,UC_X86_REG_EBX:0x11111111,UC_X86_REG_ECX:0x0C0C0C0C,UC_X86_REG_EDX:0x0D0D0D0D,
              UC_X86_REG_ESI:0x22222222,UC_X86_REG_EDI:0x33333333,UC_X86_REG_EBP:0x44444444}
        if regs: base.update(regs)
        for r,v in base.items(): mu.reg_write(r,v)
        mu.reg_write(UC_X86_REG_ESP,sp)
        mu.emu_start(addr,0x31000000,count=count)
        return mu.reg_read(UC_X86_REG_EAX), mu.reg_read(UC_X86_REG_ESP)-sp
ORIG=h.d
PATCHED=bytes(apply(ORIG,YEAR2031))

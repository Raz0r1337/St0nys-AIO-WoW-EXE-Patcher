import struct,sys,os
_b=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,_b)
from emu import Emu
from unicorn import *; from unicorn.x86_const import *
def sections(data):
    e=struct.unpack_from('<I',data,0x3C)[0]; n=struct.unpack_from('<H',data,e+6)[0]; opt=struct.unpack_from('<H',data,e+20)[0]
    sb=e+24+opt; out=[]
    for i in range(n):
        so=sb+40*i; nm=data[so:so+8].rstrip(b'\0').decode()
        vs,va,rs,ro,ch=struct.unpack_from('<IIII',data,so+8)+(struct.unpack_from('<I',data,so+36)[0],)
        out.append((nm,0x400000+va,vs,rs,ro,ch))
    return out
class Emu2(Emu):
    def __init__(self,data):
        super().__init__(data)
        self.secs={}
        for nm,va,vs,rs,ro,ch in sections(data):
            if va>=0xDD1000+0x10000 or nm in ('.glyph','.hrep','.djump','.hdp','.cam'):
                size=(vs+0xFFF)&~0xFFF
                try: self.mu.mem_map(va,size)
                except UcError: pass
                self.mu.mem_write(va,data[ro:ro+min(rs,vs)])
                self.secs[nm]=va
        # make sure .data region beyond 0xDD1000 exists (glyph buffer 0xC7D328 is inside mapped range)

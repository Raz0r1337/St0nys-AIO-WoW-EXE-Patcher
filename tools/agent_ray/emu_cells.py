import struct
from unicorn import *
from unicorn.x86_const import *
import wx
D = wx.D
mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(0x400000, 0xA00000)
for nm, va, vs, ro, rs in wx.SECS: mu.mem_write(va, D[ro:ro + min(rs, vs if vs else rs)])
STK = 0x20000000; mu.mem_map(STK, 0x100000)
HEAP = 0x30000000; mu.mem_map(HEAP, 0x100000)
w32 = lambda a, v: mu.mem_write(a, struct.pack('<I', v & 0xffffffff))
r32 = lambda a: struct.unpack('<I', mu.mem_read(a, 4))[0]
wf = lambda a, *v: mu.mem_write(a, struct.pack('<%df' % len(v), *v))
w32(0xCD754C, HEAP + 0x1000); w32(0xCF4930, HEAP + 0x10000)
RET = 0x0DEAD000; mu.mem_map(RET, 0x1000)
p = HEAP + 0x100
for (s, e) in (((1000.0, 2000.0, 10.0), (1000.0, 2000.0, -10.0)), ((1000.0, 2000.0, 10.0), (1009.0, 2000.0, -10.0)), ((1000.0, 2000.0, 10.0), (1000.0, 2009.0, -10.0))):
    wf(p, *s); wf(p + 12, *e); wf(p + 36, 1.0)
    esp = STK + 0x80000 - 24; mu.mem_write(esp, struct.pack('<6I', p, p + 12, p + 24, p + 36, 0x100, 0)); esp -= 4; w32(esp, RET)
    mu.reg_write(UC_X86_REG_ESP, esp); mu.emu_start(0x7A3B70, RET, count=1000000)
    n = r32(0xCE04C8)
    ent = [r32(HEAP + 0x10000 + 4 * i) for i in range(n)]
    print(s, e, 'Eintraege', [hex(x) for x in ent])
x, y = 1000.0, 2000.0
print('(17066.67-x)/4.1667=', (17066.6666 - x) / (100/24.), ' (17066.67-y)/4.1667=', (17066.6666 - y) / (100/24.))

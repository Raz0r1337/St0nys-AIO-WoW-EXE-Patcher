# Kostenmessung (Befehlszahl) des WMO-Pfads: N geladene WMO-Instanzen, deren AABB der Strahl nicht trifft
import struct
from unicorn import *
from unicorn.x86_const import *
import wx
D = wx.D
def run(N, hit_box=False):
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    mu.mem_map(0x400000, 0xA00000)
    for nm, va, vs, ro, rs in wx.SECS: mu.mem_write(va, D[ro:ro + min(rs, vs if vs else rs)])
    STK = 0x20000000; mu.mem_map(STK, 0x100000)
    HEAP = 0x30000000; mu.mem_map(HEAP, 0x1000000)
    w32 = lambda a, v: mu.mem_write(a, struct.pack('<I', v & 0xffffffff))
    wf = lambda a, *v: mu.mem_write(a, struct.pack('<%df' % len(v), *v))
    w32(0xCD754C, HEAP + 0x1000); w32(0xCF4930, HEAP + 0x10000)
    model = HEAP + 0x20000; w32(model + 0x1e0, 1)
    L = 0x200; w32(0xD25438, L)
    nodes = [HEAP + 0x100000 + i * 0x400 for i in range(N)]
    for i, n in enumerate(nodes):
        w32(n + 0xc, 0); w32(n + 0xf4, model)
        x0 = 5000.0 + 50 * i  # weit weg vom Strahl
        wf(n + 0x48, x0, x0, -100.0, x0 + 30, x0 + 30, 100.0)
        w32(n + L + 4, nodes[i + 1] if i + 1 < N else 1)
    w32(0xD25440, nodes[0] if N else 1)
    RET = 0x0DEAD000; mu.mem_map(RET, 0x1000)
    cnt = [0]
    mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: cnt.__setitem__(0, cnt[0] + 1))
    p = HEAP + 0x100
    wf(p, 1000.0, 2000.0, 50.0); wf(p + 12, 1010.0, 2003.0, 48.0); wf(p + 36, 1.0)
    esp = STK + 0x80000
    args = [p, p + 12, p + 24, p + 36, 0x100111, 0]
    esp -= 24; mu.mem_write(esp, struct.pack('<6I', *args)); esp -= 4; w32(esp, RET)
    mu.reg_write(UC_X86_REG_ESP, esp)
    mu.emu_start(0x7A3B70, RET, count=50_000_000)
    return cnt[0]
base = run(0)
for N in (0, 1, 10, 100, 300):
    c = run(N); print('WMO-Instanzen=%4d  Befehle=%7d  (+%.0f je Instanz)' % (N, c, (c - base) / N if N else 0))

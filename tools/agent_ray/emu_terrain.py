# Unicorn-Test mit synthetischem, ebenem Gelaende-Chunk (z=0): prueft frac/hitOut/Rueckgabe von TraceLine
import struct
from unicorn import *
from unicorn.x86_const import *
import wx
D = wx.D
mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(0x400000, 0xA00000)
for nm, va, vs, ro, rs in wx.SECS: mu.mem_write(va, D[ro:ro + min(rs, vs if vs else rs)])
STK = 0x20000000; mu.mem_map(STK, 0x100000)
HEAP = 0x30000000; mu.mem_map(HEAP, 0x400000)
w32 = lambda a, v: mu.mem_write(a, struct.pack('<I', v & 0xffffffff))
r32 = lambda a: struct.unpack('<I', mu.mem_read(a, 4))[0]
wf = lambda a, *v: mu.mem_write(a, struct.pack('<%df' % len(v), *v))
rf = lambda a, n=1: struct.unpack('<%df' % n, mu.mem_read(a, 4 * n))
w32(0xCD754C, HEAP + 0x1000); w32(0xCF4930, HEAP + 0x10000)
RET = 0x0DEAD000; mu.mem_map(RET, 0x1000)
cnt = [0]
mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: cnt.__setitem__(0, cnt[0] + 1))
def call(fn, args):
    esp = STK + 0x80000 - 4 * len(args)
    if args: mu.mem_write(esp, struct.pack('<%dI' % len(args), *args))
    esp -= 4; w32(esp, RET); mu.reg_write(UC_X86_REG_ESP, esp)
    cnt[0] = 0
    mu.emu_start(fn, RET, count=5_000_000)
    return mu.reg_read(UC_X86_REG_EAX)
call(0x7C3C60, [])  # Gitter der Chunk-Vertices (0xD25498) initialisieren, wie beim Weltstart
U = 100.0 / 24.0; C = 100.0 / 3.0; M = 17066.666
def place_chunk(xi, yi, height):
    """xi/yi: Zellindex (8192er-Raster) irgendeiner Zelle im Chunk; legt einen ebenen Chunk an"""
    area_idx = ((xi >> 7) & 63) * 64 + ((yi >> 7) & 63)
    area = HEAP + 0x100000 + area_idx * 0  # ein Area-Objekt reicht
    if r32(0xCE48D0 + area_idx * 4) == 0:
        area = HEAP + 0x100000 + (len(placed) * 0x800)
        w32(0xCE48D0 + area_idx * 4, area); w32(area + 0x70, 0)
    else:
        area = r32(0xCE48D0 + area_idx * 4)
    ch_idx = ((xi >> 3) & 15) * 16 + ((yi >> 3) & 15)
    chunk = HEAP + 0x200000 + len(placed) * 0x1000
    w32(area + 0xBC + ch_idx * 4, chunk)
    ox = M - (xi >> 3) * C; oy = M - (yi >> 3) * C
    wf(chunk + 0x7C, ox, oy, 0.0)
    hdr = chunk + 0x400; w32(chunk + 0x110, hdr); mu.mem_write(hdr + 0x3C, b'\0\0')
    hts = chunk + 0x600; w32(chunk + 0x11C, hts); wf(hts, *([height] * 145))
    w32(chunk + 0x108, 0); w32(chunk + 0xC4 + 8, 0); w32(chunk + 0xDC + 8, 0)
    placed.append((xi >> 3, yi >> 3))
placed = []
def idx(x, y): return int((M - x) / U), int((M - y) / U)
p = HEAP + 0x100
def trace(s, e, flags=0x100, frac=1.0, hit=True):
    wf(p, *s); wf(p + 12, *e); wf(p + 24, -1, -1, -1); wf(p + 36, frac)
    al = call(0x7A3B70, [p, p + 12, p + 24 if hit else 0, p + 36, flags, 0]) & 0xff
    print('  %s -> %s flags=0x%X frac_in=%.2f: AL=%d frac=%.4f hit=%s Befehle=%d' % (s, e, flags, frac, al, rf(p + 36)[0], tuple(round(v, 3) for v in rf(p + 24, 3)), cnt[0]))
# Chunks um den Testbereich anlegen (ebener Boden z=0)
x0, y0 = 1030.0, 1990.0
for dx in range(-2, 3):
    for dy in range(-2, 3):
        xi, yi = idx(x0 + dx * C, y0 + dy * C)
        if ((xi >> 3), (yi >> 3)) not in placed: place_chunk(xi, yi, 0.0)
print('Ebener Boden z=0, Chunks:', len(placed))
trace((x0, y0, 10.0), (x0, y0, -10.0))                     # senkrecht: erwartet frac 0.5, hit z=0
trace((x0, y0, 10.0), (x0 + 5, y0 + 3, -30.0))              # schraeg
trace((x0, y0, 10.0), (x0 + 5, y0 + 3, 2.0))                # endet ueber dem Boden: kein Treffer
trace((x0, y0, 10.0), (x0, y0, -10.0), frac=0.4)            # frac_in 0.4 < Trefferanteil 0.5: kein Treffer
trace((x0, y0, 10.0), (x0, y0, -10.0), hit=False)           # hitOut = NULL erlaubt
trace((x0 - 20, y0 - 10, 30.0), (x0 + 20, y0 + 15, 0.5))    # langer flacher Strahl ueber Boden (~47 m): kein Treffer
trace((x0 - 20, y0 - 10, 30.0), (x0 + 20, y0 + 15, -0.5))   # Ziel 0.5 unter Boden ("Fuss steckt im Boden"): Treffer kurz vor Ende
print('Kosten nach Strahllaenge (ebener Boden, keine WMO/M2 geladen; Befehle):')
import math
for L in (5, 10, 20, 40, 80):
    for fl in (0x100, 0x100111):
        d = (math.cos(0.6), math.sin(0.6))
        s = (x0 - d[0] * L / 2, y0 - d[1] * L / 2, 20.0); e = (x0 + d[0] * L / 2, y0 + d[1] * L / 2, 1.0)
        wf(p, *s); wf(p + 12, *e); wf(p + 36, 1.0)
        al = call(0x7A3B70, [p, p + 12, 0, p + 36, fl, 0]) & 0xff
        print('  L=%3d yd flags=0x%06X: Befehle=%6d, Zellen=%d, AL=%d' % (L, fl, cnt[0], r32(0xCE04C8) // 2, al))

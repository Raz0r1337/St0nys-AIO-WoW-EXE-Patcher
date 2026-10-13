# Unicorn-Test: TraceLine 0x7A3B70 mit leerer Welt (keine ADT/WMO geladen)
import struct, sys
from unicorn import *
from unicorn.x86_const import *
import wx
D = wx.D
mu = Uc(UC_ARCH_X86, UC_MODE_32)
IMG_LO, IMG_HI = 0x400000, 0xE00000
mu.mem_map(IMG_LO, IMG_HI - IMG_LO)
for nm, va, vs, ro, rs in wx.SECS:
    mu.mem_write(va, D[ro:ro + min(rs, vs if vs else rs)])
STK = 0x20000000; mu.mem_map(STK, 0x100000)
HEAP = 0x30000000; mu.mem_map(HEAP, 0x100000)
def w32(a, v): mu.mem_write(a, struct.pack('<I', v & 0xffffffff))
def r32(a): return struct.unpack('<I', mu.mem_read(a, 4))[0]
def wf(a, *v): mu.mem_write(a, struct.pack('<%df' % len(v), *v))
def rf(a, n=1): return struct.unpack('<%df' % n, mu.mem_read(a, 4 * n))
# Minimal-Weltzustand: M2-Szene [0xCD754C] (Nullobjekt), Zellpuffer [0xCF4930]
scene = HEAP + 0x1000; w32(0xCD754C, scene)
cellbuf = HEAP + 0x10000; w32(0xCF4930, cellbuf)
RET = 0x0DEAD000
mu.mem_map(RET & ~0xfff, 0x1000)
calls = []; ninsn = [0]; minesp = [STK + 0x100000]
FUNCS = {0x7A30D0: 'WMO-Pfad (Objektliste 0xD25440)', 0x7A39F0: 'Gitter-Pfad (Terrain/M2/Wasser)',
         0x7A3570: 'Zellen abarbeiten', 0x81CAC0: 'M2-Szene: Trace-Flag setzen', 0x81E110: 'M2-Szene: Kollisionstest (schnell)',
         0x81DF10: 'M2-Szene: Kollisionstest (allgemein)', 0x40CA10: '_alloca_probe', 0x40BE50: 'qsort', 0x7AE140: 'Flags->WMO-Maske',
         0x7A2230: 'Zellen sammeln (diag)', 0x7A23E0: 'Zellen sammeln (diag2)', 0x7A20E0: 'Zellen sammeln (Achse Y)', 0x7A2180: 'Zellen sammeln (Achse X)',
         0x81CF20: 'M2-Szene: Kandidaten', 0x81CAD0: 'M2-Szene: Puffer', 0x4C21B0: 'Vektor*Matrix'}
def hook_code(uc, addr, size, ud):
    ninsn[0] += 1
    esp = uc.reg_read(UC_X86_REG_ESP)
    if esp < minesp[0]: minesp[0] = esp
    if addr in FUNCS: calls.append(addr)
def hook_bad(uc, access, addr, size, value, ud):
    print('  !! ungueltiger Speicherzugriff', hex(addr), 'bei EIP', hex(uc.reg_read(UC_X86_REG_EIP))); return False
mu.hook_add(UC_HOOK_CODE, hook_code)
mu.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, hook_bad)
def trace(start, end, flags, frac_in=1.0):
    p = HEAP + 0x100
    wf(p, *start); wf(p + 12, *end); wf(p + 24, -1.0, -1.0, -1.0); wf(p + 36, frac_in)
    esp = STK + 0x80000
    args = [p, p + 12, p + 24, p + 36, flags, 0]
    esp -= 4 * len(args); mu.mem_write(esp, struct.pack('<6I', *args))
    esp -= 4; w32(esp, RET)
    mu.reg_write(UC_X86_REG_ESP, esp); mu.reg_write(UC_X86_REG_EBP, 0x11111111)
    for r in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI): mu.reg_write(r, 0x22222222)
    calls.clear(); ninsn[0] = 0; minesp[0] = esp
    cnt0 = r32(0xCE04C4)
    mu.emu_start(0x7A3B70, RET, count=2_000_000)
    al = mu.reg_read(UC_X86_REG_EAX) & 0xff
    ok_regs = all(mu.reg_read(r) == 0x22222222 for r in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI)) and mu.reg_read(UC_X86_REG_EBP) == 0x11111111
    print('flags=0x%08X  start=%s end=%s -> AL=%d, frac=%.3f, hit=%s, Befehle=%d, Stack-Bedarf=%d Byte, ebx/esi/edi/ebp erhalten=%s, Zaehler 0xCE04C4 %d->%d, ESP nach ret=+%d'
          % (flags, start, end, al, rf(p + 36)[0], tuple(round(x, 2) for x in rf(p + 24, 3)), ninsn[0], (esp - minesp[0]), ok_regs,
             cnt0, r32(0xCE04C4), mu.reg_read(UC_X86_REG_ESP) - esp))
    seen = []
    for c in calls:
        if not seen or seen[-1] != c: seen.append(c)
    print('   Aufrufkette:', ' -> '.join('%X(%s)' % (c, FUNCS[c]) for c in seen))
    print('   Zellpuffer-Eintraege [0xCE04C8] =', r32(0xCE04C8), ' Szene+0x1C =', hex(r32(scene + 0x1c)))
for fl in (0x100111, 0x100171, 0x110, 0x100, 0x20000, 0x1000124):
    trace((1000.0, 2000.0, 50.0), (1010.0, 2003.0, 48.0), fl)
trace((1000.0, 2000.0, 50.0), (1000.0, 2030.0, 48.0), 0x100111)

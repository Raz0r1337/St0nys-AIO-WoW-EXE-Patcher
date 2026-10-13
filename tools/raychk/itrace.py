# Integrationstest: rayframe der gepatchten Exe gegen die ECHTE TraceLine (0x7A3B70) mit synthetischem Gelaende
# (nach agent_ray/emu_terrain.py). Aufruf: itrace.py <gepatchte Wow.exe>
import sys, struct, math
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/ol2')
from unicorn import *
from unicorn.x86_const import *
import outline10 as o
D = open(sys.argv[1], 'rb').read()
pe = struct.unpack_from('<I', D, 0x3C)[0]; nsec = struct.unpack_from('<H', D, pe + 6)[0]; opt = struct.unpack_from('<H', D, pe + 20)[0]
SECS = []
for i in range(nsec):
    q = pe + 24 + opt + 40 * i
    nm = D[q:q + 8].rstrip(b'\0').decode(); vs, va, rs, ro = struct.unpack_from('<4I', D, q + 8); SECS.append((nm, 0x400000 + va, vs, ro, rs))
mu = Uc(UC_ARCH_X86, UC_MODE_32)
top = max(va + max(vs, rs) for nm, va, vs, ro, rs in SECS)
mu.mem_map(0x400000, ((top - 0x400000) + 0xFFFF) & ~0xFFFF)
for nm, va, vs, ro, rs in SECS: mu.mem_write(va, D[ro:ro + min(rs, vs if vs else rs)])
OUT = [va for nm, va, vs, ro, rs in SECS if nm == '.outl'][0]
DO = {k: OUT + v for k, v in o.DO.items()}; LB = {k: OUT + v for k, v in o.LAB.items()}
STK = 0x20000000; mu.mem_map(STK, 0x100000); HEAP = 0x30000000; mu.mem_map(HEAP, 0x400000)
w32 = lambda a, v: mu.mem_write(a, struct.pack('<I', v & 0xffffffff)); r32 = lambda a: struct.unpack('<I', mu.mem_read(a, 4))[0]
wf = lambda a, *v: mu.mem_write(a, struct.pack('<%df' % len(v), *v)); rf = lambda a, n=1: struct.unpack('<%df' % n, mu.mem_read(a, 4 * n))
w32(0xCD754C, HEAP + 0x1000); w32(0xCF4930, HEAP + 0x10000)
RET = 0x0DEAD000; mu.mem_map(RET, 0x1000)
STUBS = {}
def hook(uc, a, s, u):
    if a in STUBS:
        fn, pop = STUBS[a]; sp = uc.reg_read(UC_X86_REG_ESP); ret = r32(sp)
        r = fn(sp); 
        if r is not None: uc.reg_write(UC_X86_REG_EAX, r)
        uc.reg_write(UC_X86_REG_ESP, sp + 4 + pop); uc.reg_write(UC_X86_REG_EIP, ret)
mu.hook_add(UC_HOOK_CODE, hook)
NTR = [0]
mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: NTR.__setitem__(0, NTR[0] + 1), begin=0x7A3B70, end=0x7A3B70)
def call(fn, args=(), regs=None):
    esp = STK + 0x80000 - 4 * len(args)
    if args: mu.mem_write(esp, struct.pack('<%dI' % len(args), *args))
    esp -= 4; w32(esp, RET); mu.reg_write(UC_X86_REG_ESP, esp)
    for r, v in (regs or {}).items(): mu.reg_write(r, v)
    mu.emu_start(fn, RET, count=20_000_000)
    return mu.reg_read(UC_X86_REG_EAX)
call(0x7C3C60)
U = 100.0 / 24.0; C = 100.0 / 3.0; M = 17066.666
placed = []
def place_chunk(xi, yi, height):
    area_idx = ((xi >> 7) & 63) * 64 + ((yi >> 7) & 63)
    if r32(0xCE48D0 + area_idx * 4) == 0:
        area = HEAP + 0x100000 + (len(placed) * 0x800); w32(0xCE48D0 + area_idx * 4, area); w32(area + 0x70, 0)
    else: area = r32(0xCE48D0 + area_idx * 4)
    ch_idx = ((xi >> 3) & 15) * 16 + ((yi >> 3) & 15)
    chunk = HEAP + 0x200000 + len(placed) * 0x1000
    w32(area + 0xBC + ch_idx * 4, chunk)
    ox = M - (xi >> 3) * C; oy = M - (yi >> 3) * C
    wf(chunk + 0x7C, ox, oy, 0.0)
    hdr = chunk + 0x400; w32(chunk + 0x110, hdr); mu.mem_write(hdr + 0x3C, b'\0\0')
    hts = chunk + 0x600; w32(chunk + 0x11C, hts); wf(hts, *([height] * 145))
    w32(chunk + 0x108, 0); w32(chunk + 0xC4 + 8, 0); w32(chunk + 0xDC + 8, 0)
    placed.append((xi >> 3, yi >> 3))
def idx(x, y): return int((M - x) / U), int((M - y) / U)
x0, y0 = 1030.0, 1990.0
HILLX = x0 - C   # Chunk westlich des Testpunkts (bei Bedarf hoeher)
for dx in range(-2, 3):
    for dy in range(-2, 3):
        xi, yi = idx(x0 + dx * C, y0 + dy * C)
        if ((xi >> 3), (yi >> 3)) not in placed: place_chunk(xi, yi, 0.0)
# Welt, Kamera, Einheit (Objekt mit vtbl+0x2C = GetPosition, Hoehe +0x854), Tabelle wie nach einem Bild
WF = HEAP + 0x300000; CAM = HEAP + 0x310000; OBJ = HEAP + 0x320000; VT = HEAP + 0x321000; GP = HEAP + 0x322000
mu.mem_write(0xBD0792, b'\x01'); mu.mem_write(0xBD0790, b'\x00'); w32(0xB7436C, WF); w32(WF + 0x7E20, CAM)
POS = [x0, y0, 0.0]
def getpos(sp): wf(r32(sp + 4), *POS)
w32(OBJ, VT); w32(VT + 0x2C, GP); STUBS[GP] = (getpos, 4); wf(OBJ + 0x854, 2.0); w32(OBJ + 0x98C, 0)
STUBS[0x4D4DB0] = (lambda sp: OBJ if r32(sp + 4) == 0x333 else 0, 0)
STUBS[0x7E6480] = (lambda sp: None, 0)
w32(DO['UNITS'], 0x333); w32(DO['UNITS'] + 4, 0x0F000000); w32(DO['NUNITS'], 1); mu.mem_write(DO['RAYREQ'] + 1, b'\x01')
fails = 0
def ok(c, m):
    global fails; print(('OK   ' if c else 'FAIL ') + m); fails += 0 if c else 1
def slot():
    b = DO['RT']; st = bytes(mu.mem_read(b + 8, 4)); return st[0], st[2], [rf(b + 12 + 12 * k, 3) for k in range(st[2])]
def frame(cam, regs_check=True):
    wf(CAM + 8, *cam); NTR[0] = 0
    mu.reg_write(UC_X86_REG_ESI, 0x5151); mu.reg_write(UC_X86_REG_EDI, 0x7171); mu.reg_write(UC_X86_REG_EBX, 0x8181); mu.reg_write(UC_X86_REG_EBP, 0x4444)
    esp = STK + 0x80000; w32(esp - 4, RET); mu.reg_write(UC_X86_REG_ESP, esp - 4)
    mu.emu_start(0x4FB036, 0x4FB03B, count=20_000_000)
    regs = [mu.reg_read(r) for r in (UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBX, UC_X86_REG_EBP)] == [0x5151, 0x7171, 0x8181, 0x4444]
    return regs and mu.reg_read(UC_X86_REG_ESP) == esp - 4 and ((mu.reg_read(UC_X86_REG_FPSW) >> 11) & 7) == 0
# 1) Figur steht auf ebenem Boden, Kamera 10 Yards hinter ihr, 5 hoch: alle Strahlen frei
ok(frame((x0 - 10.0, y0, 5.0)) and NTR[0] == 3 and slot()[0] == 0, 'ebener Boden, Kamera schraeg oben: 3 echte TraceLine-Aufrufe, frei, Register/Stack/FPU erhalten')
# 2) Fuesse 0.3 Yards im Boden, flache Kamera (1.5 Yards hoch): Knie-Strahl endet 0.4 vor dem Ziel -> frei
POS[2] = -0.3
for k in range(3): frame((x0 - 10.0, y0, 1.5))
ok(NTR[0] == 3 and slot()[0] == 0, 'Fuesse 0.3 im Boden, flache Kamera: frei (Boden am Fuss zaehlt nicht)')
# 3) Figur 1.5 Yards im Boden: Knie-Ziel unter dem Boden -> Strahl trifft den Boden vor ihr -> blockiert
POS[2] = -1.5; frame((x0 - 10.0, y0, 1.5)); st, n, pts = slot()
ok(st == 1 and n >= 1 and all(abs(p[2]) < 0.2 for p in pts), 'Figur tief im Boden: blockiert, Punkt am Boden (z %s)' % [round(p[2], 3) for p in pts])
# 4) Huegel zwischen Kamera und Figur (Chunk westlich 3 Yards hoch), Kamera weit westlich: blockiert, Treffer auf dem Huegel
POS[2] = 0.0
for k in range(o.RAYFREE): frame((x0 - 10.0, y0, 5.0))
ok(slot()[0] == 0, '(wieder frei)')
xi, yi = idx(x0 - C, y0); ch = [i for i, p in enumerate(placed) if p == (xi >> 3, yi >> 3)][0]
wf(HEAP + 0x200000 + ch * 0x1000 + 0x600, *([3.0] * 145))
frame((x0 - 50.0, y0, 4.0)); st, n, pts = slot()
ok(st == 1 and n >= 1 and all(abs(p[2] - 3.0) < 0.3 for p in pts), 'Huegel (3 Yards) zwischen Kamera und Figur: blockiert, Punkte auf dem Huegel (z %s)' % [round(p[2], 3) for p in pts])
print('FAILS', fails)

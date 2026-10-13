# Boden-Teil von "Mehr Lichter": echte Funktion 0x7D0050 (Original und gepatcht), Lichtliste ueber Stub von 0x81E400
import sys, os, struct
S = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad'
sys.path.insert(0, S + '/gen'); sys.path.insert(0, S + '/lgt'); sys.path.insert(0, S + '/tm')
from emu2 import *
import lights as LG
D = open(sys.argv[1], 'rb').read()
ORIGD = open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe', 'rb').read()
fails = 0
def ok(c, msg):
    global fails
    print(('OK   ' if c else 'FAIL ') + msg)
    if not c: fails += 1
so = [s for s in sections(D) if s[0] == '.lght'][0]; SEC = so[1]
H = 0x30000000; LIGHTS = H + 0x10000; RINGMEM = H + 0x90000; CHUNK = H + 0x20000; DEV = H + 0x40000; VT = H + 0x41000
CAM = (100.0, 200.0, 300.0)
def mk(data, patched):
    e = Emu2(data)
    if patched:
        try: e.mu.mem_map(SEC, 0x1000)
        except UcError: pass
        e.mu.mem_write(SEC, data[so[4]:so[4] + so[3]])
        e.w32(SEC + LG.DO['RING'], RINGMEM)
    e.mu.mem_write(CHUNK, b'\0' * 0x100)
    e.w32(0xC5DF88, DEV); e.w32(DEV, VT); e.w32(VT + 0x118, H + 0x42000); e.w32(DEV + 0x2E0, 256)
    e.mu.mem_write(0xCD8F5C, struct.pack('<3f', *CAM))
    e.ups = []
    def setc(em, a):
        em.ups.append((em.mu.reg_read(UC_X86_REG_ECX), a[0], a[1], a[2], a[3], struct.unpack('<%df' % (4 * a[3]), bytes(em.mu.mem_read(a[2], 16 * a[3])))))
    e.stub(H + 0x42000, setc, 4, 16)
    e.lst = [None]
    def query(em, a):   # 0x81E400(thiscall ecx=Szene, Liste): Lichter wie nach AddLight eintragen
        lst = a[0]; em.lst[0] = lst; inl, ext = em.scene
        for i, p in enumerate(inl): em.w32(lst + 0x84 + 4 * i, p)
        em.w32(lst + 0xA4, len(inl))
        if patched and ext:
            em.mu.mem_write(lst + 0x16, struct.pack('<H', 1)); em.w32(RINGMEM, lst); em.w32(RINGMEM + 4, len(ext))
            for i, p in enumerate(ext): em.w32(RINGMEM + 8 + 4 * i, p)
    e.stub(0x81E400, query, 1, 4)
    e.stub(0x7B7BD0, lambda em, a: None, 1, 4)
    e.stub(0x873FF0, lambda em, a: 0, 0, 0)
    e.stub(0x79E470, lambda em, a: 0x77, 6, 0)
    e.stub(0x685F50, lambda em, a: em.ups.append(('setvs', a[0], a[1])), 2, 8)
    return e
def light(e, i, pos, col, att):
    a = LIGHTS + i * 0x80; e.mu.mem_write(a, b'\0' * 0x80)
    e.mu.mem_write(a + 0xC, struct.pack('<3f', *pos)); e.mu.mem_write(a + 0x3C, struct.pack('<3f', *col)); e.mu.mem_write(a + 0x54, struct.pack('<3f', *att))
    return a
def L(i): return ((110.0 + i, 205.0 - i, 290.0 + 0.5 * i), (0.1 * (i + 1), 0.2, 0.05 * i), (1.0 + i, 0.25 * i, 0.01 * i))
def run(e, n):
    pts = [light(e, i, *L(i)) for i in range(n)]
    e.scene = (pts[:4], pts[4:8]); e.ups.clear()
    t0 = (e.mu.reg_read(UC_X86_REG_FPSW) >> 11) & 7
    r, d = e.call(0x7D0050, (CHUNK, 1, 0), regs={UC_X86_REG_EBX: 0x5151, UC_X86_REG_ESI: 0x6161, UC_X86_REG_EDI: 0x7171})
    good = [e.mu.reg_read(x) for x in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI)] == [0x5151, 0x6161, 0x7171] and d == 4 and ((e.mu.reg_read(UC_X86_REG_FPSW) >> 11) & 7) == t0
    return good, bytes(e.mu.mem_read(0xD250A0, 0x25 * 16))
F = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
def expect(n):   # 15 Vektoren: Licht 4..8
    out = []
    for k in range(3, 8):
        if k < n:
            p, c, a = L(k)
            out += [F(F(p[0]) - CAM[0]), F(F(p[1]) - CAM[1]), F(F(p[2]) - CAM[2]), 1.0, F(c[0]), F(c[1]), F(c[2]), 0.0, F(a[0]), F(a[1]), F(a[2]), 0.0]
        else:
            out += [0.0] * 8 + [1.0, 0.0, 0.0, 0.0]
    return tuple(out)
eo = mk(ORIGD, False); ep = mk(D, True)
for n in (0, 2, 3, 4, 6, 7, 8):
    go, bo = run(eo, n); gp, bp = run(ep, n)
    upo = [u for u in eo.ups if u[0] != 'setvs']; upp = [u for u in ep.ups if u[0] != 'setvs']
    ok(go and gp, '%d Lichter: Register, Stack und FPU erhalten (Original und gepatcht)' % n)
    ok(bo == bp and len(upo) == 1 and upo[0][1:5] == (0, 0, 0xD250A0, 0x25) and upp[-1][:5] == upo[0][:5] and upp[-1][5] == upo[0][5], '%d Lichter: c0-c36 (Licht 1-3 in c28-c36) und ihr Upload wie im Original' % n)
    ext = upp[:-1]
    ok(len(ext) == 1 and ext[0][:5] == (DEV, 0, 0xEC, SEC + LG.DO['TBUF'], 15) and ext[0][5] == expect(n),
       '%d Lichter: vorher c236-c250 (Licht 4-8 im Boden-Format, freie Plaetze 0 / Abschwaechung x=1)' % n)
    ok([u for u in ep.ups if u[0] == 'setvs'] == [u for u in eo.ups if u[0] == 'setvs'] == [('setvs', 0x4D, 0x77)], '%d Lichter: Shader-Wahl unveraendert' % n)
# Karte mit weniger als 251 Konstanten: kein Zusatz-Upload (Modelle brauchen 247)
ep.w32(DEV + 0x2E0, 250); gp, bp = run(ep, 8); upp = [u for u in ep.ups if u[0] != 'setvs']
ok(gp and len(upp) == 1 and upp[0][1:5] == (0, 0, 0xD250A0, 0x25), '250 VS-Konstanten: kein Upload nach c236, Original-Upload bleibt')
ep.w32(DEV + 0x2E0, 256)
ep.w32(0xC5DF88, 0); 
try:
    run(ep, 8); crash = False
except UcError: crash = True
ok(crash, '(ohne Geraet stuerzt schon das Original ab - kein eigener Fall)')
ep.w32(0xC5DF88, DEV)
# Zusatzliste einer anderen Liste (Besitzer passt nicht): nicht verwendet
pts = [light(ep, i, *L(i)) for i in range(8)]
def query_foreign(em, a):
    lst = a[0]
    for i, p in enumerate(pts[:4]): em.w32(lst + 0x84 + 4 * i, p)
    em.w32(lst + 0xA4, 4); em.mu.mem_write(lst + 0x16, struct.pack('<H', 1)); em.w32(RINGMEM, lst + 0x1000); em.w32(RINGMEM + 4, 4)
ep.stubs[0x81E400] = (query_foreign, 1); ep.ups.clear(); ep.call(0x7D0050, (CHUNK, 1, 0))
ext = [u for u in ep.ups if u[0] != 'setvs'][0]
ok(ext[5] == expect(4), 'Zusatzliste mit fremdem Besitzer: nur Licht 4, Rest frei')
# Hook-Stelle
o = 0x7D0292 - 0x400C00
ok(D[o] == 0xE9 and 0x7D0297 + struct.unpack_from('<i', D, o + 1)[0] == SEC + LG.LAB['cave_ter'] and D[o + 5] == 0x90, 'VA 0x7D0292: jmp cave_ter, nop')
print('fails', fails)
sys.exit(1 if fails else 0)

# Funktionstest fuer den WorldFrame-Absturzfix: Funktion 0x81D510 in Unicorn.
# Aufruf: python3 test_wc.py <exe> [label]
import sys, struct
from unicorn import *
from unicorn.x86_const import *
D = open(sys.argv[1], 'rb').read()
label = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
def secs(d):
    e = struct.unpack_from('<I', d, 0x3C)[0]; n = struct.unpack_from('<H', d, e + 6)[0]; o = struct.unpack_from('<H', d, e + 20)[0]
    sb = e + 24 + o
    for i in range(n):
        so = sb + 40 * i; vs, va, rs, ro = struct.unpack_from('<IIII', d, so + 8)
        yield 0x400000 + va, vs, rs, ro
def new_mu():
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    for va, vs, rs, ro in secs(D):
        size = (max(vs, rs) + 0xFFF) & ~0xFFF
        mu.mem_map(va, size); mu.mem_write(va, D[ro:ro + min(rs, vs + 0xFFF)])
    return mu
F = lambda x: struct.pack('<f', x)
def run(tris, winding, best=1.0e9, point=(0.0, 0.0), base=100, trace=False):
    """tris: Liste von (ok, z): ok=False -> ein Index kleiner als Basis.
    Vertexpuffer liegt am Seitenanfang, davor ist nichts gemappt."""
    mu = new_mu()
    STACK = 0x20000000; mu.mem_map(STACK, 0x10000)
    VB = 0x30000000; mu.mem_map(VB, 0x1000)          # Vertexpuffer, davor ungemappt
    DATA = 0x40000000; mu.mem_map(DATA, 0x1000)
    # Vertices: je Dreieck 3 Punkte (x,y,z), 12 Byte
    verts = b''
    for i, (ok, z) in enumerate(tris):
        A, B, C = (-10.0, -10.0), (10.0, -10.0), (0.0, 10.0)
        if winding: B, C = C, B
        for (x, y) in (A, B, C): verts += F(x) + F(y) + F(z)
    mu.mem_write(VB, verts)
    idx = b''
    for i, (ok, z) in enumerate(tris):
        i0 = base + 3 * i
        if ok: idx += struct.pack('<HHH', i0, i0 + 1, i0 + 2)
        else:  idx += struct.pack('<HHH', i0, base - 1, i0 + 2)     # 2. Index zeigt vor den Puffer
    IDX = DATA; mu.mem_write(IDX, idx)
    PT = DATA + 0x100; mu.mem_write(PT, F(point[0]) + F(point[1]))
    OUTZ = DATA + 0x200; mu.mem_write(OUTZ, F(best))
    THIS = DATA + 0x400; mu.mem_write(THIS + 0x124, struct.pack('<I', VB))
    TAG = 0x1234
    RET = 0x50000000; mu.mem_map(RET, 0x1000); mu.mem_write(RET, b'\xf4')  # hlt
    sp = STACK + 0x8000
    args = [IDX, IDX + len(idx), base, PT, 0, TAG, OUTZ, 0]
    for a in reversed(args): sp -= 4; mu.mem_write(sp, struct.pack('<I', a))
    sp -= 4; mu.mem_write(sp, struct.pack('<I', RET))
    mu.reg_write(UC_X86_REG_ESP, sp); mu.reg_write(UC_X86_REG_ECX, THIS)
    mu.reg_write(UC_X86_REG_EBP, 0x44444444)
    err = None
    try:
        mu.emu_start(0x81D510, RET, count=200000)
    except UcError as e:
        err = '%s @ eip=%#x' % (e, mu.reg_read(UC_X86_REG_EIP))
    eax = mu.reg_read(UC_X86_REG_EAX); esp2 = mu.reg_read(UC_X86_REG_ESP)
    z = struct.unpack('<f', bytes(mu.mem_read(OUTZ, 4)))[0]
    return err, eax, z, esp2 - (sp + 4 + 0x20)
# Kalibrierung: welche Windung trifft?
hit_w = None
for w in (0, 1):
    err, eax, z, dsp = run([(True, 5.0)], w)
    if err is None and eax == 0x1234: hit_w = w
print('%s: Windung mit Treffer: %s' % (label, hit_w))
assert hit_w is not None, 'kein Treffer bei einem gueltigen Dreieck - Testaufbau pruefen'
w = hit_w
# Fall A: gueltig(7), ungueltig, gueltig(5) -> Erwartung: kein Fehler, Treffer z=5 (das Dreieck NACH dem ungueltigen)
err, eax, z, dsp = run([(True, 7.0), (False, 6.0), (True, 5.0)], w)
print('%s: A [ok z=7, UNGUELTIG, ok z=5]: err=%s eax=%#x z=%s stack=%+d' % (label, err, eax, z, dsp))
# Fall B: ungueltig als erstes, dann gueltig -> Erwartung: Treffer z=5
err, eax, z, dsp = run([(False, 9.0), (True, 5.0)], w)
print('%s: B [UNGUELTIG, ok z=5]: err=%s eax=%#x z=%s stack=%+d' % (label, err, eax, z, dsp))
# Fall C: nur gueltige -> wie Original: kleinstes z gewinnt
err, eax, z, dsp = run([(True, 7.0), (True, 5.0), (True, 6.0)], w)
print('%s: C [ok 7, ok 5, ok 6]: err=%s eax=%#x z=%s stack=%+d' % (label, err, eax, z, dsp))
# Fall D: leere Liste -> eax=0, z unveraendert (1e9)
err, eax, z, dsp = run([], w)
print('%s: D []: err=%s eax=%#x z=%s stack=%+d' % (label, err, eax, z, dsp))
# Fall E: Punkt ausserhalb aller Dreiecke -> kein Treffer
err, eax, z, dsp = run([(True, 7.0), (True, 5.0)], w, point=(50.0, 50.0))
print('%s: E [ok, ok] Punkt ausserhalb: err=%s eax=%#x z=%s stack=%+d' % (label, err, eax, z, dsp))

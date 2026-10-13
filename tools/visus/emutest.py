# Emulationstest fuer Visus - St0nyCam: Registrierungs-Haken und Kamera-Haken.
# Aufruf: emutest.py <Wow.exe> [<Sektions-VA hex> <Sektionsbytes-Datei>]  (ohne Datei: Referenz aus ref.py)
import sys, struct, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unicorn import *; from unicorn.x86_const import *
import ref
D = open(sys.argv[1], 'rb').read()
if len(sys.argv) > 3:
    V = int(sys.argv[2], 16); SEC = open(sys.argv[3], 'rb').read()
else:
    V = 0x00E1A000; SEC = ref.section(V)[0]
fails = 0
HOOKS = 'hooks' in sys.argv[4:]
print('Start ueber die Haken in der Exe' if HOOKS else 'Start direkt in der Sektion')
def ok(c, m):
    global fails
    print(('OK   ' if c else 'FAIL ') + m); fails += (not c)
def secs(d):
    e = struct.unpack_from('<I', d, 0x3C)[0]; n = struct.unpack_from('<H', d, e + 6)[0]
    sb = e + 24 + struct.unpack_from('<H', d, e + 20)[0]; out = []
    for i in range(n):
        o = sb + 40 * i
        vs, va, rs, ro = struct.unpack_from('<IIII', d, o + 8)
        out.append((d[o:o+8].rstrip(b'\0').decode(), 0x400000 + va, vs, rs, ro))
    return out
def new_mu():
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    mu.mem_map(0x400000, 0x1000); mu.mem_write(0x400000, D[:0x1000])
    for nm, va, vs, rs, ro in secs(D):
        if va >= 0xDD1000 + 0x10000 and nm not in ('.text', '.rdata', '.data'): continue
        size = (max(vs, rs) + 0xFFF) & ~0xFFF
        try: mu.mem_map(va, size)
        except UcError: pass
        mu.mem_write(va, D[ro:ro + min(rs, vs)])
    mu.mem_map(V & ~0xFFF, 0x2000); mu.mem_write(V, SEC)
    mu.mem_map(0x20000000, 0x100000); mu.mem_map(0x30000000, 0x10000)
    return mu
f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
def rf(mu, a): return struct.unpack('<f', bytes(mu.mem_read(a, 4)))[0]
def wf(mu, a, v): mu.mem_write(a, struct.pack('<f', v))
def r32(mu, a): return struct.unpack('<I', bytes(mu.mem_read(a, 4)))[0]
def w32(mu, a, v): mu.mem_write(a, struct.pack('<I', v & 0xFFFFFFFF))
ORIG_C = struct.unpack('<f', D[0x9F1670 - 0x401800: 0x9F1670 - 0x401800 + 4])[0] if False else None

# ---------- Registrierungs-Haken ----------
mu = new_mu(); calls = []
def hook(uc, addr, size, ud):
    if addr == 0x767FC0:
        sp = uc.reg_read(UC_X86_REG_ESP)
        ret = r32(uc, sp); args = struct.unpack('<9I', bytes(uc.mem_read(sp + 4, 36)))
        nm = bytes(uc.mem_read(args[0], 40)).split(b'\0')[0].decode()
        dv = bytes(uc.mem_read(args[3], 8)).split(b'\0')[0].decode()
        calls.append((nm, args[1], args[2], dv, args[4], args[5], args[6:]))
        uc.reg_write(UC_X86_REG_EAX, 0xCAFE0000 + len(calls)); uc.reg_write(UC_X86_REG_ESP, sp + 4); uc.reg_write(UC_X86_REG_EIP, ret)
mu.hook_add(UC_HOOK_CODE, hook, begin=0x767FC0, end=0x767FC0)
sp0 = 0x200F0000
mu.reg_write(UC_X86_REG_ESP, sp0); mu.reg_write(UC_X86_REG_EAX, 0x12345678)
for r, v in ((UC_X86_REG_EBX, 0x11), (UC_X86_REG_ESI, 0x22), (UC_X86_REG_EDI, 0x33), (UC_X86_REG_EBP, 0x44)): mu.reg_write(r, v)
mu.emu_start(0x5FE2AF if HOOKS else V + ref.O_REG, 0x5FE2B4, count=200)
ok(mu.reg_read(UC_X86_REG_EIP) == 0x5FE2B4, 'Registrierung: zurueck bei 0x5FE2B4')
ok(r32(mu, 0xC24970) == 0x12345678, 'Registrierung: ueberschriebener Befehl (mov [0xC24970], eax) ausgefuehrt')
ok([c[0] for c in calls] == ['visusHeight', 'visusShoulder'], 'Registrierung: Namen %s' % [c[0] for c in calls])
ok(all(c[1] == 0 and c[2] == 0x10 and c[3] == '0' and c[4] == 0 and c[5] == 5 and c[6] == (0, 0, 0) for c in calls), 'Registrierung: Argumente wie die Kamera-CVars (Flags 0x10, Vorgabe "0", Kategorie 5)')
ok(r32(mu, V + ref.D_PH) == 0xCAFE0001 and r32(mu, V + ref.D_PS) == 0xCAFE0002, 'Registrierung: CVar-Zeiger gemerkt')
ok(mu.reg_read(UC_X86_REG_ESP) == sp0, 'Registrierung: Stack ausgeglichen')
ok(all(mu.reg_read(r) == v for r, v in ((UC_X86_REG_EBX, 0x11), (UC_X86_REG_ESI, 0x22), (UC_X86_REG_EDI, 0x33), (UC_X86_REG_EBP, 0x44))), 'Registrierung: ebx/esi/edi/ebp unveraendert')

# ---------- Kamera-Haken ----------
CVH, CVS, CAM, CAM2, EBP = 0x30001000, 0x30002000, 0x30000000, 0x30003000, 0x200F0000
def run_cam(mu, focus, cam, h=None, s=None, esi=CAM):
    if h is None: w32(mu, V + ref.D_PH, 0)
    else: w32(mu, V + ref.D_PH, CVH); wf(mu, CVH + 0x2C, h)
    if s is None: w32(mu, V + ref.D_PS, 0)
    else: w32(mu, V + ref.D_PS, CVS); wf(mu, CVS + 0x2C, s)
    for k, v in enumerate(focus): wf(mu, EBP - 0x34 + 4 * k, v)
    for k, v in enumerate(cam): wf(mu, esi + 8 + 4 * k, v)
    mu.reg_write(UC_X86_REG_EBP, EBP); mu.reg_write(UC_X86_REG_ESI, esi); mu.reg_write(UC_X86_REG_ESP, EBP - 0xB0)
    mu.reg_write(UC_X86_REG_EBX, 0x5555); mu.reg_write(UC_X86_REG_EDI, 0x6666)
    mu.emu_start(0x6070CB if HOOKS else V + ref.O_CAM, 0x6070D1, count=500)
    sw = mu.reg_read(UC_X86_REG_FPSW); top = (sw >> 11) & 7
    # st0 ablegen, um den Wert und die Stacktiefe zu pruefen
    mu.mem_write(0x30008000, b'\xD9\x1D' + struct.pack('<I', 0x30008100))   # fstp dword [0x30008100]
    mu.emu_start(0x30008000, 0x30008006, count=2)
    sw2 = mu.reg_read(UC_X86_REG_FPSW); top2 = (sw2 >> 11) & 7
    res = [rf(mu, EBP - 0x34 + 4 * k) for k in range(3)]
    return res, top, top2, rf(mu, 0x30008100), mu.reg_read(UC_X86_REG_EIP)
orig_c = struct.unpack('<f', bytes(new_mu().mem_read(0x9F1670, 4)))[0]
def expect(focus, cam, h, s, ref_pt):
    X, Y, Z = focus
    if h is not None: Z = Z + max(-1.0, min(1.0, h))
    if s is not None:
        s = max(-2.0, min(2.0, s))
        if s != 0:
            dX, dY = cam[0] - ref_pt[0], cam[1] - ref_pt[1]
            ln = math.hypot(dX, dY)
            if ln > 0.01: X, Y = X - s * dY / ln, Y + s * dX / ln
    return [X, Y, Z]
def close(a, b): return all(abs(x - y) < 1e-4 for x, y in zip(a, b))
mu = new_mu()
F = (100.0, 200.0, 50.0)
cases = [
    ('Kamera suedlich, h=0.5, s=1 -> 1 Yard nach Osten (-Y)', F, (90.0, 200.0, 55.0), 0.5, 1.0, None),
    ('zweites Bild, gleiche Kamera, Bezug = letzter verschobener Blickpunkt', F, (90.0, 199.0, 55.0), 0.5, 1.0, 'prev'),
    ('Klammern: h=5 -> 1, s=10 -> 2', F, (90.0, 198.0, 55.0), 5.0, 10.0, 'prev'),
    ('negativ: h=-3 -> -1, s=-1 -> nach Westen', F, (90.0, 198.0, 55.0), -3.0, -1.0, 'prev'),
    ('s=0: kein Seitenversatz', F, (90.0, 201.0, 55.0), 0.25, 0.0, None),
    ('Kamera im Blickpunkt (Ich-Perspektive): kein Seitenversatz', F, (100.0, 200.0, 50.0), 0.0, 1.5, 'prev'),
    ('diagonal (Kamera suedoestlich... d=(-10,-10)), s=1', F, (90.0, 190.0, 55.0), None, 1.0, 'prev'),
    ('keine CVars registriert: nur Originalbefehl', F, (90.0, 190.0, 55.0), None, None, None),
]
prev = None
for name, focus, cam, h, s, refmode in cases:
    ref_pt = prev if (refmode == 'prev' and prev is not None) else focus
    exp = expect(focus, cam, h, s, ref_pt)
    res, top, top2, st0, eip = run_cam(mu, focus, cam, h, s)
    ok(eip == 0x30008006 and close(res, exp) and top == 7 and top2 == 0 and abs(st0 - orig_c) < 1e-9,
       '%s: %s (erwartet %s), FPU-Tiefe 1, st0 = Originalwert' % (name, ['%.4f' % v for v in res], ['%.4f' % v for v in exp]))
    prev = (res[0], res[1])
    ok(close([rf(mu, V + ref.D_PX), rf(mu, V + ref.D_PY)], prev) and r32(mu, V + ref.D_PCAM) == CAM and r32(mu, V + ref.D_PVALID) == 1, '   gemerkter Blickpunkt = verschobener Blickpunkt')
# andere Kamera: Bezug = aktueller Blickpunkt, nicht der gemerkte
res, top, top2, st0, eip = run_cam(mu, F, (90.0, 200.0, 55.0), None, 1.0, esi=CAM2)
ok(close(res, expect(F, (90.0, 200.0, 55.0), None, 1.0, F)), 'andere Kamera (esi): Bezug = aktueller Blickpunkt %s' % ['%.4f' % v for v in res])
print('Originalwert [0x9F1670] =', orig_c)
sys.exit(1 if fails else 0)

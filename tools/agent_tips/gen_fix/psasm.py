# Mini-Assembler/Disassembler fuer die beiden ps_2_0-Shader der Umrandung (Weichzeichner, Einblenden).
import struct
T, V, C, TX, OC, S = 0, 1, 2, 3, 8, 10   # Registertypen: temp, input, const, texture(t), colorout(oC), sampler
def reg(t, n): return 0x80000000 | ((t & 7) << 28) | (((t >> 3) & 3) << 11) | n
def dst(t, n, mask=0xF, sat=False): return reg(t, n) | (mask << 16) | (0x100000 if sat else 0)
SW = {'xyzw': 0xE4, 'x': 0x00, 'y': 0x55, 'z': 0xAA, 'w': 0xFF}
def src(t, n, sw='xyzw'): return reg(t, n) | (SW[sw] << 16)
def ins(op, *toks): return [op | (len(toks) << 24)] + list(toks)
MOV, ADD, MAD, MUL, DCL, TEX, DEF = 1, 2, 4, 5, 0x1F, 0x42, 0x51
def f2i(f): return struct.unpack('<I', struct.pack('<f', f))[0]

def blur_ps(w0, w1, w2):
    t = [0xFFFF0200]
    t += ins(DEF, dst(C, 0), f2i(w0), f2i(w1), f2i(w2), 0)
    for i in range(5): t += ins(DCL, 0x80000000, dst(TX, i, 0x3))
    t += ins(DCL, 0x90000000, dst(S, 0))
    for i in range(5): t += ins(TEX, dst(T, i), src(TX, i), src(S, 0))
    t += ins(MUL, dst(T, 0), src(T, 0), src(C, 0, 'x'))
    t += ins(ADD, dst(T, 1), src(T, 1), src(T, 2))
    t += ins(MAD, dst(T, 0), src(T, 1), src(C, 0, 'y'), src(T, 0))
    t += ins(ADD, dst(T, 3), src(T, 3), src(T, 4))
    t += ins(MAD, dst(T, 0), src(T, 3), src(C, 0, 'z'), src(T, 0))
    t += ins(MOV, dst(OC, 0), src(T, 0))
    t += [0x0000FFFF]
    return struct.pack('<%dI' % len(t), *t)

def comp_ps(k):
    t = [0xFFFF0200]
    t += ins(DEF, dst(C, 0), f2i(k), f2i(k), f2i(k), f2i(k))
    t += ins(DCL, 0x80000000, dst(TX, 0, 0x3))
    t += ins(DCL, 0x90000000, dst(S, 0))
    t += ins(TEX, dst(T, 0), src(TX, 0), src(S, 0))
    t += ins(MUL, dst(T, 0, sat=True), src(T, 0), src(C, 0, 'x'))
    t += ins(MOV, dst(OC, 0), src(T, 0))
    t += [0x0000FFFF]
    return struct.pack('<%dI' % len(t), *t)

# Schein-Fix gegen Flimmern (agent_shimmer):
# tent_ps: Verkleinern mit 4x4-Zelt statt 2x2-Kasten - 4 bilineare Abgriffe bei (+-0.75, +-0.75) Texeln
# (je Achse [1 3 3 1]/8). t1/t2 = (u,v) +/- (a,b) aus mkq (QDU*O1, QDV*O1), die Gegendiagonale per Komponententausch
# (abhaengiges Lesen, Stufe 1).
def tent_ps(k=0.25):
    t = [0xFFFF0200]
    t += ins(DEF, dst(C, 0), f2i(k), f2i(k), f2i(k), f2i(k))
    for i in (1, 2): t += ins(DCL, 0x80000000, dst(TX, i, 0x3))
    t += ins(DCL, 0x90000000, dst(S, 0))
    t += ins(TEX, dst(T, 0), src(TX, 1), src(S, 0))           # (u+a, v+b)
    t += ins(TEX, dst(T, 1), src(TX, 2), src(S, 0))           # (u-a, v-b)
    t += ins(MOV, dst(T, 2, 0x1), src(TX, 1))                 # r2 = (u+a, v-b)
    t += ins(MOV, dst(T, 2, 0x2), src(TX, 2))
    t += ins(MOV, dst(T, 3, 0x1), src(TX, 2))                 # r3 = (u-a, v+b)
    t += ins(MOV, dst(T, 3, 0x2), src(TX, 1))
    t += ins(TEX, dst(T, 2), src(T, 2), src(S, 0))
    t += ins(TEX, dst(T, 3), src(T, 3), src(S, 0))
    t += ins(ADD, dst(T, 0), src(T, 0), src(T, 1))
    t += ins(ADD, dst(T, 0), src(T, 0), src(T, 2))
    t += ins(ADD, dst(T, 0), src(T, 0), src(T, 3))
    t += ins(MUL, dst(T, 0), src(T, 0), src(C, 0, 'x'))
    t += ins(MOV, dst(OC, 0), src(T, 0))
    t += [0x0000FFFF]
    return struct.pack('<%dI' % len(t), *t)

# blur_soft_ps: senkrechter Weichzeichner wie blur_ps, danach die Schein-Kurve 1-(1-y)^2 = y*(2-y), y = sat(k*x),
# je Kanal (vormultipliziert wie bisher). TEX1 haelt damit schon die Deckkraft (volle 8 Bit), Einblenden mit Faktor 1.
def blur_soft_ps(w0, w1, w2, k):
    t = [0xFFFF0200]
    t += ins(DEF, dst(C, 0), f2i(w0), f2i(w1), f2i(w2), 0)
    t += ins(DEF, dst(C, 1), f2i(k), f2i(-1.0), f2i(2.0), 0)
    for i in range(5): t += ins(DCL, 0x80000000, dst(TX, i, 0x3))
    t += ins(DCL, 0x90000000, dst(S, 0))
    for i in range(5): t += ins(TEX, dst(T, i), src(TX, i), src(S, 0))
    t += ins(MUL, dst(T, 0), src(T, 0), src(C, 0, 'x'))
    t += ins(ADD, dst(T, 1), src(T, 1), src(T, 2))
    t += ins(MAD, dst(T, 0), src(T, 1), src(C, 0, 'y'), src(T, 0))
    t += ins(ADD, dst(T, 3), src(T, 3), src(T, 4))
    t += ins(MAD, dst(T, 0), src(T, 3), src(C, 0, 'z'), src(T, 0))
    t += ins(MUL, dst(T, 0, sat=True), src(T, 0), src(C, 1, 'x'))       # y = sat(k*x)
    t += ins(MAD, dst(T, 1), src(T, 0), src(C, 1, 'y'), src(C, 1, 'z'))  # 2 - y
    t += ins(MUL, dst(T, 0), src(T, 0), src(T, 1))                      # y*(2-y)
    t += ins(MOV, dst(OC, 0), src(T, 0))
    t += [0x0000FFFF]
    return struct.pack('<%dI' % len(t), *t)

# Linie an duennen Stellen (agent_tips): Die Kopien liegen nur 1 Pixel neben der Figur (Rand 1 Pixel, auch um
# Punkte und Spitzen geschlossen). line_ps macht daraus die Linie: 3x3-Zelt [1 2 1]x[1 2 1]/16 ueber TEX0
# (4 bilineare Abgriffe bei (+-0.5, +-0.5) Texeln, Gegendiagonale per Komponententausch wie tent_ps), Deckkraft
# a = sat(k * Zelt), Farbe = Mittel der Randfarben: Ausgabe = Summe * min(k/4, 1/Summe.a) (vormultipliziert).
# Bei k = 4 ist die Linie an geraden Kanten genau 2 Pixel breit (geglaettet, Masse unabhaengig von der Lage).
MAX, RCP = 0x0B, 0x06
def line_ps(k=4.0):
    t = [0xFFFF0200]
    t += ins(DEF, dst(C, 0), f2i(4.0 / k), 0, 0, 0)
    for i in (1, 2): t += ins(DCL, 0x80000000, dst(TX, i, 0x3))
    t += ins(DCL, 0x90000000, dst(S, 0))
    t += ins(TEX, dst(T, 0), src(TX, 1), src(S, 0))           # (u+a, v+b)
    t += ins(TEX, dst(T, 1), src(TX, 2), src(S, 0))           # (u-a, v-b)
    t += ins(MOV, dst(T, 2, 0x1), src(TX, 1))                 # r2 = (u+a, v-b)
    t += ins(MOV, dst(T, 2, 0x2), src(TX, 2))
    t += ins(MOV, dst(T, 3, 0x1), src(TX, 2))                 # r3 = (u-a, v+b)
    t += ins(MOV, dst(T, 3, 0x2), src(TX, 1))
    t += ins(TEX, dst(T, 2), src(T, 2), src(S, 0))
    t += ins(TEX, dst(T, 3), src(T, 3), src(S, 0))
    t += ins(ADD, dst(T, 0), src(T, 0), src(T, 1))
    t += ins(ADD, dst(T, 0), src(T, 0), src(T, 2))
    t += ins(ADD, dst(T, 0), src(T, 0), src(T, 3))            # Summe = 4 * Zelt
    t += ins(MAX, dst(T, 1, 0x8), src(T, 0, 'w'), src(C, 0, 'x'))   # max(Summe.a, 4/k)
    t += ins(RCP, dst(T, 1, 0x8), src(T, 1, 'w'))                   # min(k/4, 1/Summe.a)
    t += ins(MUL, dst(T, 0), src(T, 0), src(T, 1, 'w'))
    t += ins(MOV, dst(OC, 0), src(T, 0))
    t += [0x0000FFFF]
    return struct.pack('<%dI' % len(t), *t)

# linecomp_ps: Linie aus TEX3 (vormultipliziert c*a, a) aufgehellt einblenden: Farbe * 5/8 + 0x5E/255 je Kanal
# (wie bisher die Vierecke), also rgb = 0.625 * rgb + 0.3686 * a, Alpha a.
def linecomp_ps(m=0.625, add=94 / 255.0):
    t = [0xFFFF0200]
    t += ins(DEF, dst(C, 0), f2i(m), f2i(m), f2i(m), f2i(1.0))
    t += ins(DEF, dst(C, 1), f2i(add), f2i(add), f2i(add), 0)
    t += ins(DCL, 0x80000000, dst(TX, 0, 0x3))
    t += ins(DCL, 0x90000000, dst(S, 0))
    t += ins(TEX, dst(T, 0), src(TX, 0), src(S, 0))
    t += ins(MUL, dst(T, 1), src(T, 0), src(C, 0))
    t += ins(MAD, dst(T, 1), src(T, 0, 'w'), src(C, 1), src(T, 1))
    t += ins(MOV, dst(OC, 0), src(T, 1))
    t += [0x0000FFFF]
    return struct.pack('<%dI' % len(t), *t)

# --- Gegenprobe: Disassembler ---
NAMES = {1: 'mov', 2: 'add', 4: 'mad', 5: 'mul', 6: 'rcp', 0x0B: 'max', 0x1F: 'dcl', 0x42: 'texld', 0x51: 'def'}
RN = {0: 'r', 1: 'v', 2: 'c', 3: 't', 8: 'oC', 10: 's'}
def rtype(tok): return ((tok >> 28) & 7) | (((tok >> 11) & 3) << 3)
def rd(tok, isdst):
    s = RN.get(rtype(tok), '?%d' % rtype(tok)) + str(tok & 0x7FF)
    if isdst:
        m = (tok >> 16) & 0xF
        if m != 0xF: s += '.' + ''.join(c for i, c in enumerate('xyzw') if m >> i & 1)
        if tok & 0x100000: s = '_sat ' + s
    else:
        sw = (tok >> 16) & 0xFF
        if sw != 0xE4: s += '.' + ''.join('xyzw'[(sw >> (2 * i)) & 3] for i in range(4))
    return s
def disasm(b):
    t = list(struct.unpack('<%dI' % (len(b) // 4), b)); out = ['ps_%d_%d' % ((t[0] >> 8) & 0xFF, t[0] & 0xFF)]; i = 1
    while i < len(t):
        tok = t[i]
        if tok == 0x0000FFFF: out.append('end'); break
        op = tok & 0xFFFF; n = (tok >> 24) & 0xF; a = t[i + 1:i + 1 + n]
        if op == 0x51: out.append('def %s, %s' % (rd(a[0], True), ', '.join('%.7g' % struct.unpack('<f', struct.pack('<I', x))[0] for x in a[1:])))
        elif op == 0x1F: out.append('dcl%s %s' % ('_2d' if a[0] == 0x90000000 else '', rd(a[1], True)))
        else: out.append('%s %s' % (NAMES[op], ', '.join([rd(a[0], True)] + [rd(x, False) for x in a[1:]])))
        i += 1 + n
    return out
if __name__ == '__main__':
    print('\n'.join(disasm(blur_ps(0.2270270, 0.3162162, 0.0702703)))); print(len(blur_ps(0.227, 0.316, 0.07)))
    print('\n'.join(disasm(comp_ps(3.0)))); print(len(comp_ps(3.0)))
    print(blur_ps(1, 2, 3)[:40].hex())
    print('\n'.join(disasm(tent_ps()))); print(len(tent_ps()))
    print('\n'.join(disasm(blur_soft_ps(0.2270270, 0.3162162, 0.0702703, 2.5)))); print(len(blur_soft_ps(0.2270270, 0.3162162, 0.0702703, 2.5)))

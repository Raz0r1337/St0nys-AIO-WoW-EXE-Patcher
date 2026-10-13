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

# --- Gegenprobe: Disassembler ---
NAMES = {1: 'mov', 2: 'add', 4: 'mad', 5: 'mul', 0x1F: 'dcl', 0x42: 'texld', 0x51: 'def'}
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

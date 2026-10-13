# Checks the call log of glowtest.exe (one frame's glow part) against EXP of ol2/test_outline10.py section 20.
# The EXP-building source is taken verbatim from the test file; only sizes, the unit list and (v2) the restored
# TEXTURETRANSFORMFLAGS values (the test's emulated WoW cache holds 0, glowtest's holds TTSAV from its log) are substituted.
# usage: python3 -I exp_check.py <run.log> <W> <H> <ms> <mq> [frame]
import sys, ast, struct, re
S = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad'
log, W, H, MS, MQ = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
FR = sys.argv[6] if len(sys.argv) > 6 else 'f1'
W2, H2 = (W + 1) // 2, (H + 1) // 2
# log -> tuples of the selected frame's glow part
got, verts, ttsav, on = [], [], None, False
for line in open(log):
    if line.startswith('MARK glowpart-begin'): on = 'pending'; continue
    if on == 'pending': on = line.startswith(FR + ' ')
    if line.startswith('MARK glowpart-end'):
        if on is True: break
        on = False; continue
    if on is True:
        m = re.match(r'^\S+\s+T \((.*)\) => (\S+)', line)
        if m:
            got.append(ast.literal_eval('(' + m.group(1) + ',)'))
            if not m.group(2).startswith('refs') and m.group(2) != '0x00000000': print('  non-OK HRESULT:', line.strip())
        elif line.startswith('V '):
            verts.append([struct.unpack('<f', struct.pack('<I', int(x, 16)))[0] for x in line.split()[1:]])
        elif ' TTSAV ' in line:
            ttsav = [int(x, 16) for x in line.split('TTSAV')[1].split()]
t = open(S + '/ol2/test_outline10.py').read()
a = t.index('SRC = []\n'); b = t.index('\n', t.index('EXP += RING +'))
code = t[a:b]
code = code.replace('(4, 3, 2, 1)', '(2, 1)')
code = code.replace("('CreateRT', 1920, 1080, 21, 4, 0, 0, '&MSRT', 0)", "('CreateRT', %d, %d, 21, %d, %d, 0, '&MSRT', 0)" % (W, H, MS, MQ))
code = code.replace("('CreateTex', 1920, 1080,", "('CreateTex', %d, %d," % (W, H)).replace("('CreateTex', 960, 540,", "('CreateTex', %d, %d," % (W2, H2))
TTE = "[('TSS', i, 24, 0) for i in range(5)]"
v2 = TTE in code
if v2 and ttsav is not None:
    code = code.replace(TTE, "[('TSS', i, 24, v) for i, v in enumerate(%r) if v != 0xFFFFFFFF]" % (ttsav,))
ns = {}; exec(code, ns); EXP = ns['EXP']
print('test file EXP is %s; TTSAV from log: %s' % ('v2 (TTFF restore)' if v2 else 'v1', None if ttsav is None else ['0x%X' % x for x in ttsav]))
print('EXP entries %d, logged entries %d, identical: %s' % (len(EXP), len(got), got == EXP))
if got != EXP and got == EXP[2:]: print('  identical to EXP without the two CreatePS calls (pixel shaders kept across Reset, as in test section 24)')
for k, (x, y) in enumerate(zip(got, EXP)):
    if x != y: print('  first difference at %d: got %s expected %s' % (k, x, y)); break
if v2: print('  v2 entries present in log: SRS(168,7) before SetPS(CPS): %s, SRS(168,0xF) in tail: %s, TTFF restore: %s' % (
    ('SRS', 168, 7) in got and got.index(('SRS', 168, 7)) == got.index(('SetPS', 'CPS')) - 1,
    ('SRS', 168, 15) in got and got.index(('SRS', 168, 15)) == got.index(('SetPS', 'PS')) - 1,
    [c for c in got if c[0] == 'TSS' and c[2] == 24][5:]))
# vertex data, same checks as quad_ok() in the test
f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
O1, O2 = f32(1.3846154), f32(3.2307692)
def quad_ok(vs, x0, y0, x1, y1, u0, v0, u1, v1, du, dv):
    want = []
    for k in range(4):
        x, y, u, v = (x1 if k & 1 else x0), (y1 if k & 2 else y0), (u1 if k & 1 else u0), (v1 if k & 2 else v0)
        taps = [u, v]
        for oo, sg in ((O1, 1), (O1, -1), (O2, 1), (O2, -1)): taps += [f32(u + sg * du * oo), f32(v + sg * dv * oo)]
        want.append([f32(x), f32(y), 0.0, 1.0] + [f32(q) for q in taps])
    return vs == want, vs, want
qs = [verts[4 * i:4 * i + 4] for i in range(4)]
du, dv = f32(1 / W2), f32(1 / H2)
checks = [('downsample', qs[0], (-0.5, -0.5, W2 - 0.5, H2 - 0.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0)),
          ('horizontal', qs[1], (-0.5, -0.5, W2 - 0.5, H2 - 0.5, 0.0, 0.0, 1.0, 1.0, du, 0.0)),
          ('vertical', qs[2], (-0.5, -0.5, W2 - 0.5, H2 - 0.5, 0.0, 0.0, 1.0, 1.0, 0.0, dv)),
          ('composite', qs[3], (-0.5, -0.5, W - 0.5, H - 0.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0))]
print('  vertices of the four 56-byte quads exact as quad_ok expects: %s' % [nm for nm, q, args in checks if quad_ok(q, *args)[0]])

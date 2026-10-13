# make_fix.py - derives the shimmer fix from snapshots of ol2/ (outline10_base.py, psasm_base.py, mkoutline10_base.py,
# test_outline10_base.py = ol2 files as of 2026-10-11 15:22-15:27, md5 in README of the report) and writes
# gen_fix/{outline10,psasm,mkoutline10,test_outline10}.py plus *.diff. ol2/ itself is never written.
import os, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
def load(n): return open(os.path.join(HERE, n)).read()
class Ed:
    def __init__(self, s): self.s = s
    def rep(self, old, new, count=1):
        assert self.s.count(old) == count, (self.s.count(old), old[:120]); self.s = self.s.replace(old, new); return self

# ------------------------------------------------------------------ psasm.py: two new shaders
p = Ed(load('psasm_base.py'))
p.rep('''# --- Gegenprobe: Disassembler ---''', '''# Schein-Fix gegen Flimmern (agent_shimmer):
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

# --- Gegenprobe: Disassembler ---''')
p.rep('''    print(blur_ps(1, 2, 3)[:40].hex())''', '''    print(blur_ps(1, 2, 3)[:40].hex())
    print('\\n'.join(disasm(tent_ps()))); print(len(tent_ps()))
    print('\\n'.join(disasm(blur_soft_ps(0.2270270, 0.3162162, 0.0702703, 2.5)))); print(len(blur_soft_ps(0.2270270, 0.3162162, 0.0702703, 2.5)))''')

# ------------------------------------------------------------------ outline10.py
o = Ed(load('outline10_base.py'))
o.rep('''import sys, os, struct, math''', '''# Schein gegen Flimmern (agent_shimmer): Verkleinern mit 4x4-Zelt (tent_ps, Pixelshader TPS) statt 2x2-Kasten,
# die Kurve 1-(1-y)^2, y = sat(2.5*x) (statt mal 4 mit Saettigung) schon im senkrechten Durchgang (blur_soft_ps, VPS):
# TEX1 haelt die Deckkraft mit vollen 8 Bit (vorher wurden 8-Bit-Stufen mal 4 verstaerkt), Einblenden mit Faktor 1.
import sys, os, struct, math''')
o.rep('''DESC=0x6EC, VERTT=0x70C, GPSCODE=0x7EC, CPSCODE=0x908, TTSAV=0x970, PETF=0x990)
CODE_OFF = 0x9D0''', '''DESC=0x6EC, VERTT=0x70C, GPSCODE=0x7EC, CPSCODE=0x908, TTSAV=0x970, PETF=0x990,
          TPS=0x9D0, VPS=0x9D4, TQ=0x9D8, TPSCODE=0x9E0, VPSCODE=0xAE0)
CODE_OFF = 0xC50''')
o.rep('''DESC=32, VERTT=224, GPSCODE=284, CPSCODE=100, TTSAV=20, PETF=64)''',
      '''DESC=32, VERTT=224, GPSCODE=284, CPSCODE=100, TTSAV=20, PETF=64,
             TPS=4, VPS=4, TQ=4, TPSCODE=256, VPSCODE=360)''')
o.rep('''# Schein: Gauss mit 5 bilinearen Abgriffen (9 Texel), Verstaerkung beim Einblenden
BLUR_W = (0.2270270, 0.3162162, 0.0702703)
BLUR_O = (1.3846154, 3.2307692)
GLOW_GAIN = 4.0''', '''# Schein: Verkleinern mit 4x4-Zelt (Abgriffe bei +-TENT Texeln diagonal), Gauss mit 5 bilinearen Abgriffen (9 Texel),
# im senkrechten Durchgang die Kurve 1-(1-y)^2 mit y = sat(GLOW_K * x); Einblenden mit GLOW_GAIN = 1
BLUR_W = (0.2270270, 0.3162162, 0.0702703)
BLUR_O = (1.3846154, 3.2307692)
TENT = 0.75
GLOW_K = 2.5
GLOW_GAIN = 1.0''')
o.rep('''  mov ebx,{CPS}
  call gr_rel
  mov ebx,{PS}
  call gr_rel''', '''  mov ebx,{CPS}
  call gr_rel
  mov ebx,{TPS}
  call gr_rel
  mov ebx,{VPS}
  call gr_rel
  mov ebx,{PS}
  call gr_rel''')
o.rep('''  mov dword ptr [{GPS}],0
  mov dword ptr [{CPS}],0
\'\'\' + DEV(0x1A8, '{GPSCODE}', '{GPS}') + DEV(0x1A8, '{CPSCODE}', '{CPS}') + \'\'\'
g_sh:
  cmp dword ptr [{GPS}],0
  je g_fail
  cmp dword ptr [{CPS}],0
  je g_fail''', '''  mov dword ptr [{GPS}],0
  mov dword ptr [{CPS}],0
  mov dword ptr [{TPS}],0
  mov dword ptr [{VPS}],0
\'\'\' + DEV(0x1A8, '{GPSCODE}', '{GPS}') + DEV(0x1A8, '{CPSCODE}', '{CPS}') + DEV(0x1A8, '{TPSCODE}', '{TPS}') + DEV(0x1A8, '{VPSCODE}', '{VPS}') + \'\'\'
g_sh:
  cmp dword ptr [{GPS}],0
  je g_fail
  cmp dword ptr [{CPS}],0
  je g_fail
  cmp dword ptr [{TPS}],0
  je g_fail
  cmp dword ptr [{VPS}],0
  je g_fail''')
o.rep('''+ SRS(7, 0) + SRS(52, 0) + DEV(0x1AC, 'dword ptr [{GPS}]') + DEV(0x164, 0x504) + \\''',
      '''+ SRS(7, 0) + SRS(52, 0) + DEV(0x1AC, 'dword ptr [{TPS}]') + DEV(0x164, 0x504) + \\''')
o.rep('''  mov dword ptr [{QV1}],0x3F800000
  mov dword ptr [{QDU}],0
  mov dword ptr [{QDV}],0
  mov ebx,dword ptr [{TEX0}]
  mov edi,dword ptr [{TEX1S}]
  call g_pass
  fld1
  fidiv dword ptr [{RTW2}]
  fstp dword ptr [{QDU}]''', '''  mov dword ptr [{QV1}],0x3F800000
  fld dword ptr [{TQ}]
  fidiv dword ptr [{RTW}]
  fstp dword ptr [{QDU}]
  fld dword ptr [{TQ}]
  fidiv dword ptr [{RTH}]
  fstp dword ptr [{QDV}]
  mov ebx,dword ptr [{TEX0}]
  mov edi,dword ptr [{TEX1S}]
  call g_pass
\'\'\' + DEV(0x1AC, 'dword ptr [{GPS}]') + \'\'\'
  mov dword ptr [{QDV}],0
  fld1
  fidiv dword ptr [{RTW2}]
  fstp dword ptr [{QDU}]''')
o.rep('''  mov dword ptr [{QDU}],0
  fld1
  fidiv dword ptr [{RTH2}]
  fstp dword ptr [{QDV}]
  mov ebx,dword ptr [{TEX2}]''', '''\'\'\' + DEV(0x1AC, 'dword ptr [{VPS}]') + \'\'\'
  mov dword ptr [{QDU}],0
  fld1
  fidiv dword ptr [{RTH2}]
  fstp dword ptr [{QDV}]
  mov ebx,dword ptr [{TEX2}]''')
o.rep('''    g = psasm.blur_ps(*BLUR_W); c = psasm.comp_ps(GLOW_GAIN)
    assert len(g) == SIZES['GPSCODE'] and len(c) == SIZES['CPSCODE']
    d[DO['GPSCODE']:DO['GPSCODE'] + len(g)] = g; d[DO['CPSCODE']:DO['CPSCODE'] + len(c)] = c''',
      '''    g = psasm.blur_ps(*BLUR_W); c = psasm.comp_ps(GLOW_GAIN)
    assert len(g) == SIZES['GPSCODE'] and len(c) == SIZES['CPSCODE']
    d[DO['GPSCODE']:DO['GPSCODE'] + len(g)] = g; d[DO['CPSCODE']:DO['CPSCODE'] + len(c)] = c
    tp = psasm.tent_ps(); vp = psasm.blur_soft_ps(*BLUR_W, GLOW_K)
    assert len(tp) == SIZES['TPSCODE'] and len(vp) == SIZES['VPSCODE']
    d[DO['TPSCODE']:DO['TPSCODE'] + len(tp)] = tp; d[DO['VPSCODE']:DO['VPSCODE'] + len(vp)] = vp
    struct.pack_into('<f', d, DO['TQ'], TENT / BLUR_O[0])     # mkq: t1/t2 = (u,v) +- (TQ/RTW, TQ/RTH) * O1 = +-0.75 Texel''')

# ------------------------------------------------------------------ mkoutline10.py: new data blocks in the PowerShell output
m = Ed(load('mkoutline10_base.py'))
m.rep('''          (DO['CPSCODE'], len(psasm.comp_ps(GLOW_GAIN)), 'Schein: Pixelshader ps_2_0 Einblenden (mul_sat mal %g)' % GLOW_GAIN)]''',
      '''          (DO['CPSCODE'], len(psasm.comp_ps(GLOW_GAIN)), 'Schein: Pixelshader ps_2_0 Einblenden (mul_sat mal %g)' % GLOW_GAIN),
          (DO['TQ'], 4, 'Schein: 0.75 / 1.3846 (Zelt-Abgriffe +-0.75 Texel ueber mkq)'),
          (DO['TPSCODE'], len(psasm.tent_ps()), 'Schein: Pixelshader ps_2_0 Verkleinern mit 4x4-Zelt (4 bilineare Abgriffe)'),
          (DO['VPSCODE'], len(psasm.blur_soft_ps(*BLUR_W, GLOW_K)), 'Schein: Pixelshader ps_2_0 senkrecht weichzeichnen + Kurve 1-(1-sat(%g*x))^2' % GLOW_K)]''')
m.rep("""#    ps_2_0-Weichzeichner (5 bilineare Abgriffe, Gauss) verkleinern nach TEX1
#    (halbe Aufloesung), waagrecht nach TEX2, senkrecht zurueck nach TEX1.
#    Dann ueber den Viewport eingeblendet (vormultipliziertes Alpha, mal 4,
#    gesaettigt, nur RGB), nur wo keine Figur ist (Stencil kleiner 0x80). Die""",
      """#    4x4-Zelt verkleinern nach TEX1 (halbe Aufloesung, 4 bilineare Abgriffe
#    bei +-0.75 Texeln), mit einem ps_2_0-Weichzeichner (5 bilineare Abgriffe,
#    Gauss) waagrecht nach TEX2, senkrecht zurueck nach TEX1 - dabei gleich
#    die Kurve 1-(1-y)^2 mit y = 2.5 * Wert (gesaettigt), so bleiben in TEX1
#    volle 8 Bit fuer die Deckkraft (ruhiger bei kleinen Bewegungen).
#    Dann ueber den Viewport eingeblendet (vormultipliziertes Alpha, Faktor 1,
#    nur RGB), nur wo keine Figur ist (Stencil kleiner 0x80). Die""")

for name, ed, base in (('psasm.py', p, 'psasm_base.py'), ('outline10.py', o, 'outline10_base.py'), ('mkoutline10.py', m, 'mkoutline10_base.py')):
    open(os.path.join(HERE, name), 'w').write(ed.s)
    diff = difflib.unified_diff(load(base).splitlines(1), ed.s.splitlines(1), 'ol2/' + name, 'agent_shimmer/gen_fix/' + name)
    open(os.path.join(HERE, name.replace('.py', '.diff')), 'w').writelines(diff)
# ------------------------------------------------------------------ test_outline10.py: expectations of the fixed glow
t = Ed(load('test_outline10_base.py'))
t.rep("sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/ol2')",
      "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # agent_shimmer/gen_fix: outline10/psasm with the fix")
t.rep("""DO['GPS']: '&GPS', DO['CPS']: '&CPS', DO['PS']: '&PS', DO['GPSCODE']: '&GPSCODE', DO['CPSCODE']: '&CPSCODE', DO['PSCODE']: '&PSCODE'}""",
      """DO['GPS']: '&GPS', DO['CPS']: '&CPS', DO['PS']: '&PS', DO['GPSCODE']: '&GPSCODE', DO['CPSCODE']: '&CPSCODE', DO['PSCODE']: '&PSCODE',
         DO['TPS']: '&TPS', DO['VPS']: '&VPS', DO['TPSCODE']: '&TPSCODE', DO['VPSCODE']: '&VPSCODE'}""")
t.rep("""    for nm, k in (('GPS', 'GPS'), ('CPS', 'CPS'), ('PS', 'PS')):""", """    for nm, k in (('GPS', 'GPS'), ('CPS', 'CPS'), ('PS', 'PS'), ('TPS', 'TPS'), ('VPS', 'VPS')):""")
t.rep("""EXP = [('CreatePS', '&GPSCODE', '&GPS'), ('CreatePS', '&CPSCODE', '&CPS'), ('GetRT', 0, '&BBP'), ('GetDesc', 'BB'),""",
      """EXP = [('CreatePS', '&GPSCODE', '&GPS'), ('CreatePS', '&CPSCODE', '&CPS'), ('CreatePS', '&TPSCODE', '&TPS'), ('CreatePS', '&VPSCODE', '&VPS'), ('GetRT', 0, '&BBP'), ('GetDesc', 'BB'),""")
t.rep("""('SRS', 7, 0), ('SRS', 52, 0), ('SetPS', 'GPS'), ('SetFVF', 0x504),""", """('SRS', 7, 0), ('SRS', 52, 0), ('SetPS', 'TPS'), ('SetFVF', 0x504),""")
t.rep("""       ('SetTex', 0, 'TEX0'), ('SetRT', 0, 'TEX1S'), ('DPUP', 5, 2, '&VERTT', 56),
       ('SetTex', 0, 'TEX1'), ('SetRT', 0, 'TEX2S'), ('DPUP', 5, 2, '&VERTT', 56),
       ('SetTex', 0, 'TEX2'), ('SetRT', 0, 'TEX1S'), ('DPUP', 5, 2, '&VERTT', 56),""",
      """       ('SetTex', 0, 'TEX0'), ('SetRT', 0, 'TEX1S'), ('DPUP', 5, 2, '&VERTT', 56), ('SetPS', 'GPS'),
       ('SetTex', 0, 'TEX1'), ('SetRT', 0, 'TEX2S'), ('DPUP', 5, 2, '&VERTT', 56), ('SetPS', 'VPS'),
       ('SetTex', 0, 'TEX2'), ('SetRT', 0, 'TEX1S'), ('DPUP', 5, 2, '&VERTT', 56),""")
t.rep("""ok(cp[0][3] == o.psasm.blur_ps(*o.BLUR_W)[:20] and cp[1][3] == o.psasm.comp_ps(o.GLOW_GAIN)[:20], 'Pixelshader-Code aus dem Datenbereich (Weichzeichner, Einblenden)')""",
      """ok(cp[0][3] == o.psasm.blur_ps(*o.BLUR_W)[:20] and cp[1][3] == o.psasm.comp_ps(o.GLOW_GAIN)[:20] and cp[2][3] == o.psasm.tent_ps()[:20] and cp[3][3] == o.psasm.blur_soft_ps(*o.BLUR_W, o.GLOW_K)[:20], 'Pixelshader-Code aus dem Datenbereich (Weichzeichner, Einblenden, Zelt, senkrecht+Kurve)')
ok(bytes(mu.mem_read(DO['TPSCODE'], o.SIZES['TPSCODE'])) == o.psasm.tent_ps() and bytes(mu.mem_read(DO['VPSCODE'], o.SIZES['VPSCODE'])) == o.psasm.blur_soft_ps(*o.BLUR_W, o.GLOW_K) and o.GLOW_GAIN == 1.0, 'Shader-Bytes Zelt und senkrecht+Kurve wie psasm, Einblenden mit Faktor 1')""")
t.rep("""r1 = quad_ok(pz[0][5], -0.5, -0.5, 959.5, 539.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0)
ok(r1[0], 'Verkleinern: Viereck ueber 960x540, alle Abgriffe in der Mitte %s' % (r1[1][:1] if not r1[0] else ''))""",
      """TQ = f32(o.TENT / o.BLUR_O[0]); du0 = f32(TQ / 1920); dv0 = f32(TQ / 1080)
r1 = quad_ok(pz[0][5], -0.5, -0.5, 959.5, 539.5, 0.0, 0.0, 1.0, 1.0, du0, dv0)
ok(r1[0], 'Verkleinern (Zelt): Viereck ueber 960x540, t1/t2 = (u,v) +/- (TQ/1920, TQ/1080) * O1 %s' % (r1[1][:1] if not r1[0] else ''))
vv = verts(pz[0][5]); ok(all(abs((v[6] - v[4]) * 1920 - 0.75) < 1e-3 and abs((v[4] - v[8]) * 1920 - 0.75) < 1e-3 and abs((v[7] - v[5]) * 1080 - 0.75) < 1e-3 for v in vv[1:]), 'Zelt-Abgriffe +/- 0.75 Texel von TEX0 diagonal %s' % [round((v[6] - v[4]) * 1920, 5) for v in vv])""")
t.rep("""shaders = [e.r32(DO['GPS']), e.r32(DO['CPS']), e.r32(DO['PS'])]; res = [e.r32(DO['GLRES'] + 4 * i) for i in range(7)]""",
      """shaders = [e.r32(DO['GPS']), e.r32(DO['CPS']), e.r32(DO['PS']), e.r32(DO['TPS']), e.r32(DO['VPS'])]; res = [e.r32(DO['GLRES'] + 4 * i) for i in range(7)]""")
t.rep("""e.r32(DO['PS']) == 0, 'Abbau (Argument 1): auch die 3 Pixelshader frei')""",
      """e.r32(DO['PS']) == 0 and e.r32(DO['TPS']) == 0 and e.r32(DO['VPS']) == 0, 'Abbau (Argument 1): auch die 5 Pixelshader frei')""")
t.rep("""cs = post(); ok(sum(1 for c in cs if c[0] == 'CreatePS') == 3 and e.r32(DO['GLOK']) == 1, 'nach dem Abbau: alle 3 Shader neu')""",
      """cs = post(); ok(sum(1 for c in cs if c[0] == 'CreatePS') == 5 and e.r32(DO['GLOK']) == 1, 'nach dem Abbau: alle 5 Shader neu')""")
t.rep("""ok(g[k + 1] == ('SetRT', 0, 'BB') and not any(c[0] == 'DPUP' and c[4] == 56 for c in g[k:]), 'nach dem Fehler kein Zeichnen und kein weiterer Durchgang (keine Rueckkopplung TEX1 -> TEX1S)')""",
      """ok(g[k + 1:k + 3] == [('SetPS', 'VPS'), ('SetRT', 0, 'BB')] and not any(c[0] == 'DPUP' and c[4] == 56 for c in g[k:]), 'nach dem Fehler (nur noch SetPixelShader VPS) kein Zeichnen und kein weiterer Durchgang (keine Rueckkopplung TEX1 -> TEX1S)')""")
t.rep("""ok(sum(1 for c in cs if c[0] == 'CreatePS') == 3 and sum(1 for c in g if c[0] in ('CreateRT', 'CreateTex')) == 4 and all(OBJS[p]['refs'] == 0 for p in old) and e.r32(DO['RTDEV']) == D3D2, 'neues Geraet: Shader und Texturen neu, alte frei')""",
      """ok(sum(1 for c in cs if c[0] == 'CreatePS') == 5 and sum(1 for c in g if c[0] in ('CreateRT', 'CreateTex')) == 4 and all(OBJS[p]['refs'] == 0 for p in old) and e.r32(DO['RTDEV']) == D3D2, 'neues Geraet: 5 Shader und Texturen neu, alte frei')""")
open(os.path.join(HERE, 'test_outline10.py'), 'w').write(t.s)
open(os.path.join(HERE, 'test_outline10.diff'), 'w').writelines(difflib.unified_diff(load('test_outline10_base.py').splitlines(1), t.s.splitlines(1), 'ol2/test_outline10.py', 'agent_shimmer/gen_fix/test_outline10.py'))
print('ok')

import re, sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
a = s.index('# Huellkugel-Vorderseite (agent_feet): zfront setzt')
b = s.index('def src(base, sym=False):')
new = r'''# Quader-Vorderseite (agent_feet, Abstand verkleinert): zfront setzt ZC = kleinste NDC-Tiefe z/w der Vorderseite
# des Huellquaders von gezeichnetem Teil (CURM) und seinen Eltern ([Modell+0x48], bis 3 Stufen), soweit sie Figur oder
# Reittier der Einheit CUR sind (Waffe -> Figur -> Reittier; der Reiter haengt am Reittier, 0x73D793). Gelesen wird
# nur ueber CURM und die Eltern-Kette, die das Spiel gerade selbst benutzt - die Zeiger in der Tabelle werden nur
# verglichen, nie gelesen. 0x7F800000 (+unendlich) = kein Quader. zsph(ecx = Modell oder 0, edi = 1 fuer ein
# Anbauteil, sonst 0): Mitte SC = (min + max) / 2 des Huellquaders im M2-Kopf, SV = SC * [Modell+0xF4]
# (Modell -> Sicht), halbe Kanten h = |max - min| / 2 (danach in SC), ZT = |c5.xyz|, g_i = c5.xyz . Zeile i
# (Aenderung von w je Einheit entlang der Modellachse i, mit Skalierung). Vorderseite E = h0 |g0| + h1 |g1| + h2 g2':
# waagrecht die Ecke zur Kamera; senkrecht (Modell-z = oben) bei Figur und Reittier nur die Unterseite, wenn die
# Kamera von unten schaut (g2' = max(g2, 0) = (g2 + |g2|) / 2: was am Boden steht, liegt dann vorn), von oben zaehlt
# der Kopf nicht (Fuesse und Boden liegen dann tiefer als die Mitte); bei Anbauteilen (Waffe, Stab am Boden) die
# ganze Hoehe (g2' = |g2|). ZR = E / ZT + SPHM (Zuschlag in Yards); w = c5.(SV,1) - ZR * ZT,
# z = c4.(SV,1) - ZR * (c4.c5) / ZT; w <= 0 oder z/w < 0 (Kamera vor der Vorderseite bzw. vor der nahen Ebene) -> 0.
# Vergleiche als Ganzzahl (fuer Werte >= 0 wie die Floats; NaN mit Vorzeichen 0 ist groesser als +unendlich und wird
# nie genommen). Der Radius im M2-Kopf (+0xB8) > 0 dient nur als Pruefung des Kopfes. ebx, esi, edi bleiben.
ZSPH = """zfront:
  mov dword ptr [{ZC}],0x7F800000
  push ebx
  push esi
  push edi
  mov esi,dword ptr [{CUR}]
  lea esi,[esi+esi*2]
  lea esi,[{UNITS}-24+esi*8]
  mov ecx,dword ptr [{CURM}]
  xor edi,edi
  cmp ecx,[esi+8]
  je zf_0
  cmp ecx,[esi+12]
  je zf_0
  inc edi
zf_0:
  call zsph
  xor edi,edi
  mov ebx,3
zf_l:
  test ecx,ecx
  jz zf_r
  mov ecx,[ecx+0x48]
  test ecx,ecx
  jz zf_r
  cmp ecx,[esi+8]
  je zf_s
  cmp ecx,[esi+12]
  jne zf_n
zf_s:
  call zsph
zf_n:
  dec ebx
  jnz zf_l
zf_r:
  pop edi
  pop esi
  pop ebx
  ret
zsph:
  test ecx,ecx
  jz zs_r
  mov edx,[ecx+0x%(SCN)X]
  test edx,edx
  jz zs_r
  mov eax,[edx+0x%(FRM)X]
  cmp eax,[ecx+0x%(STP)X]
  jne zs_r
  mov edx,[ecx+0x%(SHR)X]
  test edx,edx
  jz zs_r
  test byte ptr [edx+8],1
  jz zs_r
  mov edx,[edx+0x%(HDR)X]
  test edx,edx
  jz zs_r
  cmp dword ptr [edx+0x%(RAD)X],0
  jle zs_r
""" % dict(SCN=M2_SCENE, FRM=SC_FRAME, STP=M2_STAMP, SHR=M2_SHARED, HDR=M2_HDR, RAD=M2_RAD) + ''.join("""  fld dword ptr [edx+0x%X]
  fadd dword ptr [edx+0x%X]
  fmul dword ptr [{HALF}]
  fstp dword ptr [{SC}+%d]
""" % (M2_BOX + 4 * j, M2_BOX + 12 + 4 * j, 4 * j) for j in range(3)) + ''.join("""  fld dword ptr [{SC}]
  fmul dword ptr [ecx+0x%X]
  fld dword ptr [{SC}+4]
  fmul dword ptr [ecx+0x%X]
  faddp st(1),st(0)
  fld dword ptr [{SC}+8]
  fmul dword ptr [ecx+0x%X]
  faddp st(1),st(0)
  fadd dword ptr [ecx+0x%X]
  fstp dword ptr [{SV}+%d]
""" % (M2_MV + 4 * j, M2_MV + 16 + 4 * j, M2_MV + 32 + 4 * j, M2_MV + 48 + 4 * j, 4 * j) for j in range(3)) + ''.join("""  fld dword ptr [edx+0x%X]
  fsub dword ptr [edx+0x%X]
  fabs
  fmul dword ptr [{HALF}]
  fstp dword ptr [{SC}+%d]
""" % (M2_BOX + 12 + 4 * j, M2_BOX + 4 * j, 4 * j) for j in range(3)) + """  fld dword ptr [{C5}]
  fmul st(0),st(0)
  fld dword ptr [{C5}+4]
  fmul st(0),st(0)
  faddp st(1),st(0)
  fld dword ptr [{C5}+8]
  fmul st(0),st(0)
  faddp st(1),st(0)
  fsqrt
  fstp dword ptr [{ZT}]
""" + ''.join("""  fld dword ptr [{C5}]
  fmul dword ptr [ecx+0x%X]
  fld dword ptr [{C5}+4]
  fmul dword ptr [ecx+0x%X]
  faddp st(1),st(0)
  fld dword ptr [{C5}+8]
  fmul dword ptr [ecx+0x%X]
  faddp st(1),st(0)
""" % (M2_MV + 16 * i, M2_MV + 16 * i + 4, M2_MV + 16 * i + 8) + ("""  fabs
  fmul dword ptr [{SC}+%d]
""" % (4 * i) if i < 2 else """  fld st(0)
  fabs
  test edi,edi
  jnz zs_full
  faddp st(1),st(0)
  fmul dword ptr [{HALF}]
  jmp zs_h
zs_full:
  fstp st(1)
zs_h:
  fmul dword ptr [{SC}+8]
""") + ("" if i == 0 else """  faddp st(1),st(0)
""") for i in range(3)) + """  fdiv dword ptr [{ZT}]
  fadd dword ptr [{SPM}]
  fstp dword ptr [{ZR}]
""" + ''.join("""  fld dword ptr [{%s}]
  fmul dword ptr [{SV}]
  fld dword ptr [{%s}+4]
  fmul dword ptr [{SV}+4]
  faddp st(1),st(0)
  fld dword ptr [{%s}+8]
  fmul dword ptr [{SV}+8]
  faddp st(1),st(0)
  fadd dword ptr [{%s}+12]
  fstp dword ptr [{%s}]
""" % (c, c, c, c, out) for c, out in (('C5', 'ZW'), ('C4', 'ZZ'))) + """  fld dword ptr [{ZR}]
  fmul dword ptr [{ZT}]
  fstp dword ptr [{ZT2}]
  fld dword ptr [{ZW}]
  fsub dword ptr [{ZT2}]
  fstp dword ptr [{ZW}]
  fld dword ptr [{C4}]
  fmul dword ptr [{C5}]
  fld dword ptr [{C4}+4]
  fmul dword ptr [{C5}+4]
  faddp st(1),st(0)
  fld dword ptr [{C4}+8]
  fmul dword ptr [{C5}+8]
  faddp st(1),st(0)
  fdiv dword ptr [{ZT}]
  fmul dword ptr [{ZR}]
  fstp dword ptr [{ZT2}]
  fld dword ptr [{ZZ}]
  fsub dword ptr [{ZT2}]
  fstp dword ptr [{ZZ}]
  cmp dword ptr [{ZW}],0
  jle zs_zero
  fld dword ptr [{ZZ}]
  fdiv dword ptr [{ZW}]
  fstp dword ptr [{ZZ}]
  cmp dword ptr [{ZZ}],0
  jge zs_min
zs_zero:
  mov dword ptr [{ZZ}],0
zs_min:
  mov eax,dword ptr [{ZZ}]
  cmp eax,dword ptr [{ZC}]
  jge zs_r
  mov dword ptr [{ZC}],eax
zs_r:
  ret
"""

'''
s = s[:a] + new + s[b:]
# Konstanten
s = s.replace("SPHK = 1.0         # mit Huellkugel: Kopien auf der Kugel-Vorderseite, zusaetzlich SPHK * KZ nach vorn (0 = nur die Kugel)",
              "SPHK = 0.1         # mit Huellquader: Kopien auf der Quader-Vorderseite, zusaetzlich SPHK * KZ nach vorn (0 = nur der Quader)\n"
              "SPHM = 0.05        # Zuschlag vor der Quader-Vorderseite in Yards (Animation ragt etwas ueber den Quader im M2-Kopf)")
s = s.replace("SC=0xE90, SV=0xE9C, SPK=0xEA8)", "SC=0xE90, SV=0xE9C, SPK=0xEA8, SPM=0xEAC)")
s = s.replace("SC=12, SV=12, SPK=4)", "SC=12, SV=12, SPK=4, SPM=4)")
s = s.replace("    struct.pack_into('<f', d, DO['SPK'], SPHK)\n", "    struct.pack_into('<f', d, DO['SPK'], SPHK)\n    struct.pack_into('<f', d, DO['SPM'], SPHM)\n")
open(p, 'w', encoding='utf-8').write(s)

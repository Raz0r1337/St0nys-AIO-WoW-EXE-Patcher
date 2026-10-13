import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)
code = r'''
# Kollisionsstrahlen (agent_ray). raystub ersetzt bei VA 0x4FB036 den Aufruf von 0x7E6480 (zwischen OnWorldUpdate mit
# dem Kamera-Update und RenderWorld, einmal pro Bild im Hauptthread): Original, dann rayframe, alle Register erhalten.
# rayframe: nur in der Welt ([0xBD0792] != 0), nicht beim Laden ([0xBD0790] = 0), mit WorldFrame [0xB7436C] und
# Kamera [wf+0x7E20] und endlicher Kameraposition (cam+8, Welt) -> CAMP, RAYSEQ + 1. Dann reihum (RCUR) die
# Kategorien des letzten Bilds, deren Kopien "nur wo verdeckt" gezeichnet wurden (RAYREQ), solange noch 3 Strahlen im
# Budget sind. rayunit: Eintrag der Strahl-Tabelle RT (gleicher Index wie UNITS, per GUID abgeglichen, sonst neu), Objekt
# frisch per GUID (0x4D4DB0, nie alte Zeiger), Fusspunkt ueber [vtbl+0x2C] (mit Transporter), Hoehe [obj+0x854]
# (0.3..40, sonst 2), beritten ([obj+0x98C]) andere Anteile. Je Zielpunkt T: L = |T - Kamera| (1..150 Yards), frac =
# 1 - RAYS / L (TraceLine prueft nur bis dort), TraceLine(Kamera, T, 0, &frac, RAYFLAGS, 0). Treffer: Punkt
# Kamera + (T - Kamera) * (frac + RAYD / L), also RAYD Yards hinter dem Treffer, in die Tabelle. Mit Treffer:
# blockiert (sofort), sonst nach RAYFREE freien Pruefungen frei. Objekt weg: frei.
RAYCODE = """raystub:
  call {ORIGRF}
  pushad
  call rayframe
  popad
  ret
rayframe:
  cmp byte ptr [{INWORLD}],0
  je rf_r
  cmp byte ptr [{LOADING}],0
  jne rf_r
  mov eax,dword ptr [{WFRAME}]
  test eax,eax
  jz rf_r
  mov eax,[eax+0x7E20]
  test eax,eax
  jz rf_r
""" + ''.join("""  mov ecx,[eax+%d]
  mov edx,ecx
  and edx,0x7F800000
  cmp edx,0x7F800000
  je rf_r
  mov dword ptr [{CAMP}+%d],ecx
""" % (8 + 4 * j, 4 * j) for j in range(3)) + """  inc dword ptr [{RAYSEQ}]
  mov dword ptr [{RBUD}],{RAYB}
  mov eax,dword ptr [{NUNITS}]
  cmp eax,48
  ja rf_r
  mov dword ptr [{RCNT}],eax
rf_l:
  cmp dword ptr [{RBUD}],3
  jl rf_r
  dec dword ptr [{RCNT}]
  js rf_r
  mov eax,dword ptr [{RCUR}]
  inc eax
  cmp eax,dword ptr [{NUNITS}]
  jbe rf_c
  mov eax,1
rf_c:
  mov dword ptr [{RCUR}],eax
  cmp byte ptr [{RAYREQ}+eax],0
  je rf_l
  call rayunit
  jmp rf_l
rf_r:
  ret
rayunit:
  lea esi,[eax+eax*2]
  lea esi,[{UNITS}-24+esi*8]
  imul edi,eax,48
  lea edi,[edi+{RT}-48]
  mov eax,[esi]
  cmp eax,[edi]
  jne ru_new
  mov eax,[esi+4]
  cmp eax,[edi+4]
  je ru_have
ru_new:
  mov eax,[esi]
  mov [edi],eax
  mov eax,[esi+4]
  mov [edi+4],eax
  mov dword ptr [edi+8],0
ru_have:
  push 0
  push {FILESTR}
  push 0x18
  push dword ptr [esi+4]
  push dword ptr [esi]
  call {OBJPTR}
  add esp,0x14
  test eax,eax
  jz ru_gone
  mov ebx,eax
  push {RPOS}
  mov ecx,ebx
  mov eax,[ebx]
  call dword ptr [eax+0x2C]
  mov eax,[ebx+0x854]
  cmp eax,{HLO}
  jl ru_hd
  cmp eax,{HHI}
  jle ru_hok
ru_hd:
  mov eax,dword ptr [{HDEF}]
ru_hok:
  mov dword ptr [{RH}],eax
  mov dword ptr [{RK}],{KFR}
  cmp dword ptr [ebx+0x98C],0
  je ru_k
  mov dword ptr [{RK}],{KFRM}
ru_k:
  mov dword ptr [{RNH}],0
  mov dword ptr [{RI}],0
ru_ray:
  mov eax,dword ptr [{RPOS}]
  mov dword ptr [{REND}],eax
  mov eax,dword ptr [{RPOS}+4]
  mov dword ptr [{REND}+4],eax
  mov eax,dword ptr [{RK}]
  mov ecx,dword ptr [{RI}]
  fld dword ptr [eax+ecx*4]
  fmul dword ptr [{RH}]
  fadd dword ptr [{RPOS}+8]
  fstp dword ptr [{REND}+8]
  fld dword ptr [{REND}]
  fsub dword ptr [{CAMP}]
  fmul st(0),st(0)
  fld dword ptr [{REND}+4]
  fsub dword ptr [{CAMP}+4]
  fmul st(0),st(0)
  faddp st(1),st(0)
  fld dword ptr [{REND}+8]
  fsub dword ptr [{CAMP}+8]
  fmul st(0),st(0)
  faddp st(1),st(0)
  fsqrt
  fstp dword ptr [{RL}]
  mov eax,dword ptr [{RL}]
  cmp eax,dword ptr [{LMIN}]
  jl ru_next
  cmp eax,dword ptr [{LMAX}]
  jg ru_next
  fld dword ptr [{ONE}]
  fld dword ptr [{RAYS}]
  fdiv dword ptr [{RL}]
  fsubp st(1),st(0)
  fstp dword ptr [{RFRAC}]
  push 0
  push {RAYFLAGS}
  push {RFRAC}
  push 0
  push {REND}
  push {CAMP}
  call {TRACE}
  add esp,0x18
  dec dword ptr [{RBUD}]
  test al,al
  jz ru_next
  fld dword ptr [{RAYD}]
  fdiv dword ptr [{RL}]
  fadd dword ptr [{RFRAC}]
  mov eax,dword ptr [{RNH}]
  lea eax,[eax+eax*2]
  lea eax,[edi+12+eax*4]
""" + ''.join("""  fld dword ptr [{REND}+%d]
  fsub dword ptr [{CAMP}+%d]
  fmul st(0),st(1)
  fadd dword ptr [{CAMP}+%d]
  fstp dword ptr [eax+%d]
""" % (4 * j, 4 * j, 4 * j, 4 * j) for j in range(3)) + """  fstp st(0)
  inc dword ptr [{RNH}]
ru_next:
  inc dword ptr [{RI}]
  cmp dword ptr [{RI}],3
  jb ru_ray
  mov eax,dword ptr [{RNH}]
  test eax,eax
  jz ru_free
  mov byte ptr [edi+8],1
  mov byte ptr [edi+9],0
  mov byte ptr [edi+10],al
  ret
ru_free:
  cmp byte ptr [edi+8],0
  je ru_r
  inc byte ptr [edi+9]
  cmp byte ptr [edi+9],{RAYFREE}
  jb ru_r
ru_gone:
  mov dword ptr [edi+8],0
ru_r:
  ret
"""
# zhit (nach KZ in d_copies, Kopien "nur wo verdeckt" mit Quader): Ist die Einheit CUR laut Strahl-Tabelle blockiert
# (Strahlen in diesem Bild gelaufen: RAYOK, GUID gleich), wird jeder gemerkte Punkt H (Welt) ueber die erste Figur bzw.
# das erste Reittier der Kette (ZMOD, von zsph geprueft) in Sichtkoordinaten gerechnet: Modell = ((H - t) . Zeile i) /
# |Zeile i|^2 mit der Welt-Matrix [m+0xB4] (Zeilen, Verschiebung +0x30, Zeilen senkrecht zueinander), dann mal
# [m+0xF4]. z/w = (c4.v) / (c5.v), nur w > 0, 0 <= z/w endlich. Die tiefste Stelle ersetzt KZ, wenn sie weiter hinten
# liegt (als Ganzzahl verglichen: z/w >= 0, KZ auch < 0 moeglich). ebx, esi, edi bleiben.
RAYCODE += """zhit:
  cmp dword ptr [{RAYOK}],0
  je zh_r
  mov ecx,dword ptr [{ZMOD}]
  test ecx,ecx
  jz zh_r
  push esi
  push edi
  push ebx
  mov eax,dword ptr [{CUR}]
  lea esi,[eax+eax*2]
  lea esi,[{UNITS}-24+esi*8]
  imul edi,eax,48
  lea edi,[edi+{RT}-48]
  mov eax,[esi]
  cmp eax,[edi]
  jne zh_x
  mov eax,[esi+4]
  cmp eax,[edi+4]
  jne zh_x
  cmp byte ptr [edi+8],1
  jne zh_x
  movzx ebx,byte ptr [edi+10]
  cmp ebx,3
  ja zh_x
  mov dword ptr [{ZH}],0xFFFFFFFF
zh_l:
  test ebx,ebx
  jz zh_done
  dec ebx
  lea eax,[ebx+ebx*2]
  lea eax,[edi+12+eax*4]
""" + ''.join("""  fld dword ptr [eax+%d]
  fsub dword ptr [ecx+0x%X]
  fstp dword ptr [{HD}+%d]
""" % (4 * j, 0xE4 + 4 * j, 4 * j) for j in range(3)) + ''.join("""  fld dword ptr [{HD}]
  fmul dword ptr [ecx+0x%X]
  fld dword ptr [{HD}+4]
  fmul dword ptr [ecx+0x%X]
  faddp st(1),st(0)
  fld dword ptr [{HD}+8]
  fmul dword ptr [ecx+0x%X]
  faddp st(1),st(0)
  fld dword ptr [ecx+0x%X]
  fmul st(0),st(0)
  fld dword ptr [ecx+0x%X]
  fmul st(0),st(0)
  faddp st(1),st(0)
  fld dword ptr [ecx+0x%X]
  fmul st(0),st(0)
  faddp st(1),st(0)
  fdivp st(1),st(0)
  fstp dword ptr [{HV}+%d]
""" % (0xB4 + 16 * i, 0xB8 + 16 * i, 0xBC + 16 * i, 0xB4 + 16 * i, 0xB8 + 16 * i, 0xBC + 16 * i, 4 * i) for i in range(3)) + ''.join("""  fld dword ptr [{HV}]
  fmul dword ptr [ecx+0x%X]
  fld dword ptr [{HV}+4]
  fmul dword ptr [ecx+0x%X]
  faddp st(1),st(0)
  fld dword ptr [{HV}+8]
  fmul dword ptr [ecx+0x%X]
  faddp st(1),st(0)
  fadd dword ptr [ecx+0x%X]
  fstp dword ptr [{HD}+%d]
""" % (0xF4 + 4 * j, 0x104 + 4 * j, 0x114 + 4 * j, 0x124 + 4 * j, 4 * j) for j in range(3)) + ''.join("""  fld dword ptr [{%s}]
  fmul dword ptr [{HD}]
  fld dword ptr [{%s}+4]
  fmul dword ptr [{HD}+4]
  faddp st(1),st(0)
  fld dword ptr [{%s}+8]
  fmul dword ptr [{HD}+8]
  faddp st(1),st(0)
  fadd dword ptr [{%s}+12]
  fstp dword ptr [{%s}]
""" % (c, c, c, c, out) for c, out in (('C5', 'ZW'), ('C4', 'ZZ'))) + """  cmp dword ptr [{ZW}],0
  jle zh_l
  fld dword ptr [{ZZ}]
  fdiv dword ptr [{ZW}]
  fstp dword ptr [{ZZ}]
  mov eax,dword ptr [{ZZ}]
  test eax,eax
  js zh_l
  mov edx,eax
  and edx,0x7F800000
  cmp edx,0x7F800000
  je zh_l
  cmp eax,dword ptr [{ZH}]
  jle zh_l
  mov dword ptr [{ZH}],eax
  jmp zh_l
zh_done:
  mov eax,dword ptr [{ZH}]
  test eax,eax
  js zh_x
  cmp eax,dword ptr [{KZ}]
  jle zh_x
  mov dword ptr [{KZ}],eax
zh_x:
  pop ebx
  pop edi
  pop esi
zh_r:
  ret
"""

'''
rep("def src(base, sym=False):", code + "def src(base, sym=False):")
rep("''' + ZSPH + '''post:", "''' + ZSPH + RAYCODE + '''post:")
rep("'zfront', 'zsph']).items()}", "'zfront', 'zsph', 'raystub', 'rayframe', 'rayunit', 'zhit']).items()}")
# Daten
rep("    struct.pack_into('<f', d, DO['SPM'], SPHM)\n",
"""    struct.pack_into('<f', d, DO['SPM'], SPHM)
    struct.pack_into('<12f', d, DO['RAYS'], RAYS, RAYD, *KFR, *KFRM, RAYLMIN, RAYLMAX, RAYH[2], 1.0)
""")
open(p, 'w', encoding='utf-8').write(s)

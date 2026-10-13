import sys, struct
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)
f2i = lambda x: struct.unpack('<I', struct.pack('<f', x))[0]
# --- Konstanten ---
rep("SPHM = 0.05        # Zuschlag vor der Quader-Vorderseite in Yards (Animation ragt etwas ueber den Quader im M2-Kopf)\n",
"""SPHM = 0.05        # Zuschlag vor der Quader-Vorderseite in Yards (Animation ragt etwas ueber den Quader im M2-Kopf)
# Kollisionsstrahlen (agent_ray): vor RenderWorld (VA 0x4FB036) je Einheit mit "nur wo verdeckt" 3 Strahlen per
# TraceLine (0x7A3B70) von der Kamera zu Knie, Brust und Kopf; blockiert -> Bezugstiefe bis hinter den Treffer
RAYSITE = 0x4FB036  # call 0x7E6480 (E8 45 B4 2E 00) zwischen OnWorldUpdate (Kamera) und RenderWorld
RAYB = 18          # Strahlen pro Bild (reihum, je Einheit 3)
RAYS = 0.4         # Strahl endet so viele Yards vor dem Zielpunkt (Boden direkt am eingesunkenen Fuss zaehlt nicht)
RAYD = 0.1         # Bezugspunkt so viele Yards hinter dem Treffer (Kollision und sichtbare Flaeche weichen etwas ab)
RAYFREE = 3        # blockiert gilt sofort, frei erst nach so vielen freien Pruefungen hintereinander
RAYFLAGS = 0x100111  # Gelaende, WMO-Kollision, M2-Kollisionsnetze, GameObjects (wie Flugbahn/Bodenprobe des Spiels)
KFR = (0.3, 0.6, 0.9)      # Knie, Brust, Kopf (Anteil der Hoehe)
KFRM = (0.55, 0.75, 0.95)  # beritten
RAYLMIN, RAYLMAX = 1.0, 150.0   # kein Strahl unter 1 Yard (Ego-Sicht) oder ueber 150 Yards
RAYH = (0.3, 40.0, 2.0)    # gueltige Hoehe [Objekt+0x854], sonst 2 Yards
RTE = 48           # Eintrag der Strahl-Tabelle: GUID (8), Zustand, Zaehler frei, Treffer, -, 3 Trefferpunkte (Welt, je 12)
""")
rep("SC=0xE90, SV=0xE9C, SPK=0xEA8, SPM=0xEAC)\nCODE_OFF = 0xEB0",
"""SC=0xE90, SV=0xE9C, SPK=0xEA8, SPM=0xEAC,
          RAYREQ=0xEB0, RCUR=0xEF0, RCNT=0xEF4, RBUD=0xEF8, RAYSEQ=0xEFC, RAYLAST=0xF00, RAYOK=0xF04, CAMP=0xF08, RPOS=0xF14,
          REND=0xF20, RFRAC=0xF2C, RL=0xF30, RH=0xF34, RK=0xF38, RI=0xF3C, RNH=0xF40, ZMOD=0xF44, ZH=0xF48, HV=0xF4C, HD=0xF58,
          RTMP=0xF64, RAYS=0xF68, RAYD=0xF6C, KFR=0xF70, KFRM=0xF7C, LMIN=0xF88, LMAX=0xF8C, HDEF=0xF90, ONE=0xF94, RT=0xFA0)
CODE_OFF = 0x18A0""")
rep("SC=12, SV=12, SPK=4, SPM=4)",
"""SC=12, SV=12, SPK=4, SPM=4,
             RAYREQ=64, RCUR=4, RCNT=4, RBUD=4, RAYSEQ=4, RAYLAST=4, RAYOK=4, CAMP=12, RPOS=12, REND=12, RFRAC=4, RL=4, RH=4,
             RK=4, RI=4, RNH=4, ZMOD=4, ZH=4, HV=12, HD=12, RTMP=4, RAYS=4, RAYD=4, KFR=12, KFRM=12, LMIN=4, LMAX=4, HDEF=4,
             ONE=4, RT=MAXU * RTE)""")
rep("         SPHERE=0x983D20, M2UPD=0x823F10, LIGHTCB=0x780CD0, VISLIST=0xCDB098, LISTADD=0x6DED60)",
"""         SPHERE=0x983D20, M2UPD=0x823F10, LIGHTCB=0x780CD0, VISLIST=0xCDB098, LISTADD=0x6DED60,
         ORIGRF=0x7E6480, TRACE=0x7A3B70, INWORLD=0xBD0792, LOADING=0xBD0790, WFRAME=0xB7436C)""")
rep("X.update(PULSE=PULSE_MS, HOSTILE=HOSTILE, MAXPET=45)",
"X.update(PULSE=PULSE_MS, HOSTILE=HOSTILE, MAXPET=45, RAYB=RAYB, RAYFREE=RAYFREE, RAYFLAGS=RAYFLAGS,\n         HLO=%s, HHI=%s)" % ("struct.unpack('<I', struct.pack('<f', RAYH[0]))[0]", "struct.unpack('<I', struct.pack('<f', RAYH[1]))[0]"))
# --- zfront: ZMOD (erste Figur bzw. erstes Reittier der Kette mit gueltigem Kopf) ---
rep("""ZSPH = \"\"\"zfront:
  mov dword ptr [{ZC}],0x7F800000
""", """ZSPH = \"\"\"zfront:
  mov dword ptr [{ZC}],0x7F800000
  mov dword ptr [{ZMOD}],0
""")
rep("""  cmp dword ptr [edx+0x%(RAD)X],0x7F800000
  jge zs_r
""", """  cmp dword ptr [edx+0x%(RAD)X],0x7F800000
  jge zs_r
  test edi,edi
  jnz zs_nm
  cmp dword ptr [{ZMOD}],0
  jne zs_nm
  mov dword ptr [{ZMOD}],ecx
zs_nm:
""")
# --- d_copies: Anforderung merken, nach KZ die Treffer einrechnen ---
rep("""  cmp dword ptr [{MODE}],2
  jne d_kz
  fld dword ptr [{C5}]
  fmul dword ptr [{C5}]
""", """  cmp dword ptr [{MODE}],2
  jne d_kz
  mov eax,dword ptr [{CUR}]
  mov byte ptr [{RAYREQ}+eax],1
  fld dword ptr [{C5}]
  fmul dword ptr [{C5}]
""")
rep("""  fld dword ptr [{KZ}]
  fmul dword ptr [{SPK}]
  fadd dword ptr [{ZC}]
  fstp dword ptr [{KZ}]
  mov dword ptr [{ZA}],0
d_kz:
""", """  fld dword ptr [{KZ}]
  fmul dword ptr [{SPK}]
  fadd dword ptr [{ZC}]
  fstp dword ptr [{KZ}]
  mov dword ptr [{ZA}],0
  call zhit
d_kz:
""")
# --- ensure: neues Bild ---
rep("""ensure:
  cmp dword ptr [{VALID}],0
  jne e_ret
  mov dword ptr [{VALID}],1
""", """ensure:
  cmp dword ptr [{VALID}],0
  jne e_ret
  mov dword ptr [{VALID}],1
  xor eax,eax
  mov ecx,16
e_rq:
  mov dword ptr [{RAYREQ}-4+ecx*4],eax
  dec ecx
  jnz e_rq
  mov ecx,dword ptr [{RAYSEQ}]
  cmp ecx,dword ptr [{RAYLAST}]
  je e_ro
  inc eax
e_ro:
  mov dword ptr [{RAYOK}],eax
  mov dword ptr [{RAYLAST}],ecx
""")
open(p, 'w', encoding='utf-8').write(s)

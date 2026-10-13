# Outline (Nr. 68) mit Optionen: Ziel, Mouseover, eigener Charakter, 5er-Gruppe, Schlachtzug,
# eigener Charakter nur wo verdeckt, durch Waende, Klassen- bzw. Gesinnungsfarbe; feindliche
# Spieler in Klassenfarbe pulsieren sanft rot (WoW 3.3.5a 12340). Weiterentwicklung von outline4.py:
# "nur wo verdeckt" - Kopien mit STENCILZFAIL KEEP und Tiefen-Abstand (KZ aus der Projektion).
# outline7: Durch Waende nur fuer Gruppe/Schlachtzug (GMODE 1); ohne Gruppen-Umrandung werden
# Gruppe/Schlachtzug dann nur wo verdeckt umrandet (GMODE 2). Spaeter Gezeichnetes loescht nur
# Raender ueber WPROT (Gruppen-Raender durch Waende bleiben).
# outline10: weicher Schein wie in Retail fuer dich, Gruppe, Ziel und Mouseover: die duenne Linie wird
# in eine Render-Textur gezeichnet, per ps_2_0 weichgezeichnet (Gauss, halbe Aufloesung) und ausserhalb
# der Figuren eingeblendet; Schlachtzug-Mitglieder ausserhalb der 5er-Gruppe nur duenne Linie (THIN).
# Vor IDirect3DDevice9::Reset bzw. dem Abbau (Aufrufe von 0x690150 bei VA 0x69029D, 0x6A337F, 0x69040B)
# werden die Texturen freigegeben.
# outline8: Sortierung von Pass 0 der Welt-Szene (VA 0x822FDD): Teile umrandeter Einheiten kommen
# ans Ende der undurchsichtigen M2-Teile, untereinander in der Reihenfolge des Spiels. Beim Zeichnen
# von Pass 0 (VA 0x823D1F/0x823D3B) kommen sie erst nach den gebuendelten Doodads (M2BatchDoodads),
# damit Laternen, Briefkaesten usw. schon im Tiefenpuffer liegen ("nur wo verdeckt" erkennt sie).
import sys, os, struct, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ol2'))   # psasm
import psasm
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/gen')
from asmgen import *
PX = 2.0   # Randbreite in Pixeln
OFFS = [(PX, 0), (-PX, 0), (0, PX), (0, -PX), (PX, PX), (PX, -PX), (-PX, PX), (-PX, -PX)]
# Datenlayout (Sektions-Offsets)
MAXU = 48          # umrandete Einheiten pro Bild (Kategorie = Index + 1)
UE = 24            # Eintrag: GUID lo, GUID hi, Modell, Reittier-Modell, Farbe, Pulsfarbe (0 = keine)
PULSE_MS = 1500    # Dauer eines Pulses (Klassenfarbe -> rot -> Klassenfarbe) in ms
KAPPA = 0.001      # "nur wo verdeckt": Abstand in Yards = KAPPA * Entfernung^2 (15 yd -> 0,23 yd)
HOSTILE = 0xFFFF0000   # Farbe des Auswahlkreises fuer feindlich (0xBD0C94/0xBD0C98)
DO = dict(VP=0x00, CUR=0x18, VALID=0x1C, MARKED=0x20, SMODE=0x24, PS=0x28, PSDEV=0x2C,
          FX=0x30, FY=0x34, SX=0x38, SY=0x3C, TWO=0x40, MTWO=0x44, HALF=0x48, MODE=0x4C,
          MAT=0x50, VERTS=0x90, OFFS=0xE0, PSCODE=0x120, PGUID=0x138, NUNITS=0x140, SELFCAT=0x144,
          KAP=0x148, KZ=0x14C, CLS=0x150, K128=0x180, PW=0x184, T8=0x188, TMP=0x18C, UNITS=0x190,
          GRPN=0x610, GMODE=0x614, WPROT=0x618, NMARK=0x61C, MLIST=0x620, MCOUNT=0x624,
          THIN=0x628, GLRES=0x668, RTDEV=0x684, RTW=0x688, RTH=0x68C, RTMS=0x690, RTMQ=0x694, RTW2=0x698, RTH2=0x69C,
          BBP=0x6A0, DSP=0x6A4, GPS=0x6A8, CPS=0x6AC, GPSDEV=0x6B0, GLFAIL=0x6B4, GLOK=0x6B8, O1=0x6BC, O2=0x6C0,
          QX0=0x6C4, QY0=0x6C8, QX1=0x6CC, QY1=0x6D0, QU0=0x6D4, QV0=0x6D8, QU1=0x6DC, QV1=0x6E0, QDU=0x6E4, QDV=0x6E8,
          DESC=0x6EC, VERTT=0x70C, GPSCODE=0x7EC, CPSCODE=0x908, TTSAV=0x970)
CODE_OFF = 0x990
SIZES = dict(VP=24, CUR=4, VALID=4, MARKED=4, SMODE=4, PS=4, PSDEV=4, FX=4, FY=4, SX=4, SY=4, TWO=4, MTWO=4, HALF=4, MODE=4,
             MAT=64, VERTS=80, OFFS=64, PSCODE=20, PGUID=8, NUNITS=4, SELFCAT=4, KAP=4, KZ=4, CLS=48,
             K128=4, PW=4, T8=4, TMP=4, UNITS=MAXU * UE, GRPN=4, GMODE=4, WPROT=4, NMARK=4, MLIST=4, MCOUNT=4,
             THIN=64, GLRES=28, RTDEV=4, RTW=4, RTH=4, RTMS=4, RTMQ=4, RTW2=4, RTH2=4, BBP=4, DSP=4, GPS=4, CPS=4,
             GPSDEV=4, GLFAIL=4, GLOK=4, O1=4, O2=4, QX0=4, QY0=4, QX1=4, QY1=4, QU0=4, QV0=4, QU1=4, QV1=4, QDU=4, QDV=4,
             DESC=32, VERTT=224, GPSCODE=284, CPSCODE=100, TTSAV=20)
# Schein: Gauss mit 5 bilinearen Abgriffen (9 Texel), Verstaerkung beim Einblenden
BLUR_W = (0.2270270, 0.3162162, 0.0702703)
BLUR_O = (1.3846154, 3.2307692)
GLOW_GAIN = 4.0
GLRES_NAMES = ['MSRT', 'TEX0', 'TEX0S', 'TEX1', 'TEX1S', 'TEX2', 'TEX2S']   # Reihenfolge in GLRES
# Eintraege von WoWs Zustands-Cache [Geraet+0x3BC4+4*i], die Post und Schein aendern: SRCBLEND, DESTBLEND,
# Sampler 0 (MAG, MIN, MIP, ADDRESSU, ADDRESSV), TEXCOORDINDEX 0-4, ALPHABLEND, ALPHATEST, FOG, ZWRITE,
# COLORWRITE, CULL, ZFUNC. Nur diese werden ungueltig (0xFFFFFFFF) - fuer D3DRS_AMBIENT (0xA6) ist
# 0xFFFFFFFF ein echter Wert. TEXTURETRANSFORMFLAGS 0-4 (0x52-0x56) setzt der Schein selbst zurueck.
HWCACHE_DIRTY = (0x00, 0x01, 0x02, 0x12, 0x22, 0x32, 0x42, 0x6A, 0x6B, 0x6C, 0x6D, 0x6E, 0xA7, 0xA8, 0xAA, 0xAB, 0xAC, 0xAF, 0xB1)
FIG = 0x80         # Stencil-Wert der Figur; Rand = Kategorie (1..MAXU)
# Klassenfarben (RAID_CLASS_COLORS aus FrameXML 3.3.5), D3DCOLOR 0xAARRGGBB, Index = Klassen-Id
CLASSCOL = {1: 0xFFC79C6E, 2: 0xFFF58CBA, 3: 0xFFABD473, 4: 0xFFFFF569, 5: 0xFFFFFFFF, 6: 0xFFC41F3B,
            7: 0xFF0070DE, 8: 0xFF69CCF0, 9: 0xFF9482C9, 11: 0xFFFF7D0A}
# Schalter der Optionen: je ein CC-Fuellbyte nach einem ret in .text, 1 = an (gesetzt ueber die J/N-Fragen)
FLAGS = dict(FWALLS=0x6AB7DF, FSELF=0x6ABAAF, FPARTY=0x6ABE2F, FRAID=0x6ABE8F, FHIDDEN=0x6ABF3F, FREACT=0x6ABE5F,
             FWALLSGRP=0x6AC02F)
# externe Adressen
X = dict(DEVPTR=0xC5DF88, VT9=0xA2E718, WSCENE=0xCD754C, DRAWBATCH=0x8203B0, AFTERB=0x823AD3, VPRET=0x6A9B16,
         CIRCLES=0x4F6F90, OBJPTR=0x4D4DB0, FILESTR=0xA22CD4, SELCOL=0x521BF0, TGT=0xBD07B0, TGT4=0xBD07B4,
         MOV=0xBD07A0, MOV4=0xBD07A4, GETTICK=0x9DF174, SHADERS=0xD43020, C2=0xC5F008, C3=0xC5F018, C4=0xC5F028, C5=0xC5F038,
         MARKDIRTY=0x685970, FORCEUPD=0x685A70, PLAYERGUID=0x4D3790, PARTY=0xBD1948, RAIDARR=0xBEB568, RAIDCNT=0xBEB608,
         QSORT=0x83DCF0, CMPOPA=0x81EEA0, CMPBATCH=0x81EAD0, DRAWLIST=0x823130, RESETFN=0x690150)
X.update(FLAGS)
X.update(PULSE=PULSE_MS, HOSTILE=HOSTILE)
# Aufrufe von 0x690150 (gibt vor IDirect3DDevice9::Reset bzw. beim Abbau die Geraete-Ressourcen frei):
# Formatwechsel 0x690230 (vtable 0xA2E718 + 0x58), verlorenes Geraet 0x6A3350, Abbau 0x6903B0 (Argument 1)
RESETSITES = (0x69029D, 0x6A337F, 0x69040B)

def SRS(state, val):
    v = val if isinstance(val, str) else '0x%X' % val
    return '''  push %s
  push %d
  push esi
  mov eax,[esi]
  call dword ptr [eax+0xE4]
''' % (v, state)

def _arg(a): return a if isinstance(a, str) else '0x%X' % a
def DEV(off, *args):   # Methode des D3D-Geraets (esi), Argumente von links nach rechts
    return ''.join('  push %s\n' % _arg(a) for a in reversed(args)) + '  push esi\n  mov eax,[esi]\n  call dword ptr [eax+0x%X]\n' % off
def OBJ(ref, off, *args):   # Methode eines COM-Objekts, dessen Zeiger in ref (Speicheroperand) steht
    return ''.join('  push %s\n' % _arg(a) for a in reversed(args)) + '  mov ecx,%s\n  push ecx\n  mov eax,[ecx]\n  call dword ptr [eax+0x%X]\n' % (ref, off)
def SSS(typ, val): return DEV(0x114, 0, typ, val)          # SetSamplerState(0, ...)
def TSS(stage, typ, val): return DEV(0x10C, stage, typ, val)
def REL(ref, lab):   # Release, falls der Zeiger in ref nicht 0 ist
    return '  mov ecx,%s\n  test ecx,ecx\n  jz %s\n  push ecx\n  mov eax,[ecx]\n  call dword ptr [eax+8]\n%s:\n' % (ref, lab, lab)
def MKQ():
    # 4 Ecken (Dreiecksstreifen) aus QX0/QX1, QY0/QY1, QU0/QU1, QV0/QV1; je 5 Abgriffe:
    # t0 = (u,v), t1/t2 = (u,v) +/- (QDU,QDV)*O1, t3/t4 = (u,v) +/- (QDU,QDV)*O2
    s = 'mkq:\n'
    for k in range(4):
        b = '{VERTT}+%d' % (56 * k)
        xs, ys = ('QX1' if k & 1 else 'QX0'), ('QY1' if k & 2 else 'QY0')
        us, vs = ('QU1' if k & 1 else 'QU0'), ('QV1' if k & 2 else 'QV0')
        s += '  mov eax,dword ptr [{%s}]\n  mov dword ptr [%s],eax\n' % (xs, b)
        s += '  mov eax,dword ptr [{%s}]\n  mov dword ptr [%s+4],eax\n' % (ys, b)
        for c, dd, o in ((us, 'QDU', 16), (vs, 'QDV', 20)):
            s += '  mov eax,dword ptr [{%s}]\n  mov dword ptr [%s+%d],eax\n' % (c, b, o)
            for j, (oo, op) in enumerate((('O1', 'fadd'), ('O1', 'fsubr'), ('O2', 'fadd'), ('O2', 'fsubr'))):
                s += '  fld dword ptr [{%s}]\n  fmul dword ptr [{%s}]\n  %s dword ptr [{%s}]\n  fstp dword ptr [%s+%d]\n' % (dd, oo, op, c, b, o + 8 * (j + 1))
    return s + '  ret\n'
DPUPT = DEV(0x14C, 5, 2, '{VERTT}', 56)   # DrawPrimitiveUP(TRIANGLESTRIP, 2, VERTT, 56)

# Weicher Schein (nur Einheiten ohne THIN): Ringfarben ueber den Stencil in eine Render-Textur gleicher
# Groesse und Kantenglaettung (MSRT), aufloesen nach TEX0, verkleinern nach TEX1 (halbe Aufloesung),
# waagrecht nach TEX2, senkrecht zurueck nach TEX1, dann ausserhalb der Figuren (Stencil < 0x80)
# vormultipliziert einblenden. Fehler: GLFAIL = Geraet, dann nur die duennen Linien.
GLOW = '''
ucol:
  lea eax,[ebx+ebx*2]
  mov edx,dword ptr [{UNITS}-8+eax*8]
  mov ecx,dword ptr [{UNITS}-4+eax*8]
  test ecx,ecx
  jz uc_r
  call blend
uc_r:
  ret
glfree:
  push ebx
  mov ebx,6
gf_l:
  mov ecx,dword ptr [{GLRES}+ebx*4]
  mov dword ptr [{GLRES}+ebx*4],0
  test ecx,ecx
  jz gf_n
  push ecx
  mov eax,[ecx]
  call dword ptr [eax+8]
gf_n:
  dec ebx
  jns gf_l
  mov dword ptr [{RTDEV}],0
  pop ebx
  ret
glrel:
  push ecx
  call glfree
  mov dword ptr [{GLFAIL}],0
  cmp dword ptr [esp+8],1
  jne gr_go
  push ebx
  mov ebx,{GPS}
  call gr_rel
  mov ebx,{CPS}
  call gr_rel
  mov ebx,{PS}
  call gr_rel
  mov dword ptr [{GPSDEV}],0
  mov dword ptr [{PSDEV}],0
  pop ebx
gr_go:
  pop ecx
  jmp {RESETFN}
gr_rel:
  mov ecx,[ebx]
  mov dword ptr [ebx],0
  test ecx,ecx
  jz grr_r
  push ecx
  mov eax,[ecx]
  call dword ptr [eax+8]
grr_r:
  ret
''' + MKQ() + '''
g_pass:
  cmp dword ptr [{GLFAIL}],esi
  je gp_r
''' + DEV(0x104, 0, 'ebx') + DEV(0x94, 0, 'edi') + '''
  test eax,eax
  jge gp_ok
  mov dword ptr [{GLFAIL}],esi
gp_r:
  ret
gp_ok:
  call mkq
''' + DPUPT + '''
  ret
glow:
  mov dword ptr [{GLOK}],0
  cmp dword ptr [{GLFAIL}],esi
  je g_ret0
  mov ecx,dword ptr [{NUNITS}]
g_any:
  test ecx,ecx
  jz g_ret0
  cmp byte ptr [{THIN}+ecx],0
  je g_have
  dec ecx
  jmp g_any
g_have:
  push ebx
  push edi
  push ebp
  cmp dword ptr [{GPSDEV}],esi
  je g_sh
  mov dword ptr [{GPSDEV}],esi
  mov dword ptr [{GPS}],0
  mov dword ptr [{CPS}],0
''' + DEV(0x1A8, '{GPSCODE}', '{GPS}') + DEV(0x1A8, '{CPSCODE}', '{CPS}') + '''
g_sh:
  cmp dword ptr [{GPS}],0
  je g_fail
  cmp dword ptr [{CPS}],0
  je g_fail
  mov dword ptr [{BBP}],0
  mov dword ptr [{DSP}],0
''' + DEV(0x98, 0, '{BBP}') + '''
  test eax,eax
  jl g_out
''' + OBJ('dword ptr [{BBP}]', 0x30, '{DESC}') + '''
  test eax,eax
  jl g_relbb
  mov eax,dword ptr [{DESC}+0x18]
  cmp eax,dword ptr [{RTW}]
  jne g_new
  mov eax,dword ptr [{DESC}+0x1C]
  cmp eax,dword ptr [{RTH}]
  jne g_new
  mov eax,dword ptr [{DESC}+0x10]
  cmp eax,dword ptr [{RTMS}]
  jne g_new
  mov eax,dword ptr [{DESC}+0x14]
  cmp eax,dword ptr [{RTMQ}]
  jne g_new
  cmp dword ptr [{RTDEV}],esi
  jne g_new
  cmp dword ptr [{TEX2S}],0
  jne g_go
g_new:
  call glfree
  mov eax,dword ptr [{DESC}+0x18]
  mov dword ptr [{RTW}],eax
  inc eax
  shr eax,1
  mov dword ptr [{RTW2}],eax
  mov eax,dword ptr [{DESC}+0x1C]
  mov dword ptr [{RTH}],eax
  inc eax
  shr eax,1
  mov dword ptr [{RTH2}],eax
  mov eax,dword ptr [{DESC}+0x10]
  mov dword ptr [{RTMS}],eax
  mov eax,dword ptr [{DESC}+0x14]
  mov dword ptr [{RTMQ}],eax
''' + DEV(0x70, 'dword ptr [{RTW}]', 'dword ptr [{RTH}]', 21, 'dword ptr [{RTMS}]', 'dword ptr [{RTMQ}]', 0, '{MSRT}', 0) + '''
  test eax,eax
  jl g_nfail
''' + DEV(0x5C, 'dword ptr [{RTW}]', 'dword ptr [{RTH}]', 1, 1, 21, 0, '{TEX0}', 0) + '''
  test eax,eax
  jl g_nfail
''' + OBJ('dword ptr [{TEX0}]', 0x48, 0, '{TEX0S}') + '''
  test eax,eax
  jl g_nfail
''' + DEV(0x5C, 'dword ptr [{RTW2}]', 'dword ptr [{RTH2}]', 1, 1, 21, 0, '{TEX1}', 0) + '''
  test eax,eax
  jl g_nfail
''' + OBJ('dword ptr [{TEX1}]', 0x48, 0, '{TEX1S}') + '''
  test eax,eax
  jl g_nfail
''' + DEV(0x5C, 'dword ptr [{RTW2}]', 'dword ptr [{RTH2}]', 1, 1, 21, 0, '{TEX2}', 0) + '''
  test eax,eax
  jl g_nfail
''' + OBJ('dword ptr [{TEX2}]', 0x48, 0, '{TEX2S}') + '''
  test eax,eax
  jl g_nfail
  mov dword ptr [{RTDEV}],esi
  jmp g_go
g_nfail:
  call glfree
  mov dword ptr [{GLFAIL}],esi
  jmp g_relbb
g_go:
''' + DEV(0xA0, '{DSP}') + '''
  test eax,eax
  jl g_relbb
  mov ecx,dword ptr [{DEVPTR}]
''' + ''.join('  mov eax,dword ptr [ecx+0x%X]\n  mov dword ptr [{TTSAV}+%d],eax\n' % (0x3BC4 + 4 * (0x52 + i), 4 * i) for i in range(5)) + SRS(174, 0) + DEV(0x94, 0, 'dword ptr [{MSRT}]') + '''
  test eax,eax
  jl g_sfail
''' + DEV(0xAC, 0, 0, 1, 0, 0x3F800000, 0) + '''
  mov ebx,dword ptr [{NUNITS}]
g_src:
  test ebx,ebx
  jz g_srcd
  cmp byte ptr [{THIN}+ebx],0
  jne g_srcn
  call ucol
  or edx,0xFF000000
  call quad
g_srcn:
  dec ebx
  jmp g_src
g_srcd:
''' + DEV(0x88, 'dword ptr [{MSRT}]', 0, 'dword ptr [{TEX0S}]', 0, 0) + '''
  test eax,eax
  jl g_sfail
''' + DEV(0x9C, 0) + SRS(7, 0) + SRS(52, 0) + DEV(0x1AC, 'dword ptr [{GPS}]') + DEV(0x164, 0x504) + \
    SSS(5, 2) + SSS(6, 2) + SSS(7, 0) + SSS(1, 3) + SSS(2, 3) + \
    ''.join(TSS(i, 11, i) + TSS(i, 24, 0) for i in range(5)) + '''
  fild dword ptr [{RTW2}]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QX1}]
  fild dword ptr [{RTH2}]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QY1}]
  mov dword ptr [{QX0}],0xBF000000
  mov dword ptr [{QY0}],0xBF000000
  mov dword ptr [{QU0}],0
  mov dword ptr [{QV0}],0
  mov dword ptr [{QU1}],0x3F800000
  mov dword ptr [{QV1}],0x3F800000
  mov dword ptr [{QDU}],0
  mov dword ptr [{QDV}],0
  mov ebx,dword ptr [{TEX0}]
  mov edi,dword ptr [{TEX1S}]
  call g_pass
  fld1
  fidiv dword ptr [{RTW2}]
  fstp dword ptr [{QDU}]
  mov ebx,dword ptr [{TEX1}]
  mov edi,dword ptr [{TEX2S}]
  call g_pass
  mov dword ptr [{QDU}],0
  fld1
  fidiv dword ptr [{RTH2}]
  fstp dword ptr [{QDV}]
  mov ebx,dword ptr [{TEX2}]
  mov edi,dword ptr [{TEX1S}]
  call g_pass
  cmp dword ptr [{GLFAIL}],esi
  je g_rest
  mov dword ptr [{GLOK}],1
  jmp g_rest
g_sfail:
  mov dword ptr [{GLFAIL}],esi
g_rest:
''' + DEV(0x94, 0, 'dword ptr [{BBP}]') + DEV(0x9C, 'dword ptr [{DSP}]') + DEV(0xBC, '{VP}') + SRS(7, 1) + SRS(52, 1) + '''
  mov ecx,dword ptr [{DEVPTR}]
  mov dword ptr [ecx+0xF6C],1
  mov dword ptr [ecx+0x2534],1
  cmp dword ptr [{GLOK}],0
  je g_tail
''' + SRS(56, 5) + SRS(57, 0x80) + SRS(27, 1) + SRS(19, 2) + SRS(20, 6) + SRS(168, 7) + DEV(0x1AC, 'dword ptr [{CPS}]') + DEV(0x104, 0, 'dword ptr [{TEX1}]') + '''
  fild dword ptr [{VP}]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QX0}]
  fild dword ptr [{VP}]
  fiadd dword ptr [{VP}+8]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QX1}]
  fild dword ptr [{VP}+4]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QY0}]
  fild dword ptr [{VP}+4]
  fiadd dword ptr [{VP}+12]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QY1}]
  fild dword ptr [{VP}]
  fidiv dword ptr [{RTW}]
  fstp dword ptr [{QU0}]
  fild dword ptr [{VP}]
  fiadd dword ptr [{VP}+8]
  fidiv dword ptr [{RTW}]
  fstp dword ptr [{QU1}]
  fild dword ptr [{VP}+4]
  fidiv dword ptr [{RTH}]
  fstp dword ptr [{QV0}]
  fild dword ptr [{VP}+4]
  fiadd dword ptr [{VP}+12]
  fidiv dword ptr [{RTH}]
  fstp dword ptr [{QV1}]
  mov dword ptr [{QDU}],0
  mov dword ptr [{QDV}],0
  call mkq
''' + DPUPT + '''
g_tail:
''' + DEV(0x104, 0, 0) + SRS(27, 0) + SRS(56, 3) + SRS(168, 0xF) + DEV(0x1AC, 'dword ptr [{PS}]') + DEV(0x164, 0x44) + '''
  mov eax,dword ptr [{TTSAV}+0]
  cmp eax,0xFFFFFFFF
  je gt_d0
''' + TSS(0, 24, 'eax') + '''
  jmp gt_n0
gt_d0:
  mov ecx,dword ptr [{DEVPTR}]
  mov byte ptr [ecx+0x100C],1
gt_n0:
  mov eax,dword ptr [{TTSAV}+4]
  cmp eax,0xFFFFFFFF
  je gt_d1
''' + TSS(1, 24, 'eax') + '''
  jmp gt_n1
gt_d1:
  mov ecx,dword ptr [{DEVPTR}]
  mov byte ptr [ecx+0x1124],1
gt_n1:
  mov eax,dword ptr [{TTSAV}+8]
  cmp eax,0xFFFFFFFF
  je gt_d2
''' + TSS(2, 24, 'eax') + '''
  jmp gt_n2
gt_d2:
  mov ecx,dword ptr [{DEVPTR}]
  mov byte ptr [ecx+0x123C],1
gt_n2:
  mov eax,dword ptr [{TTSAV}+12]
  cmp eax,0xFFFFFFFF
  je gt_d3
''' + TSS(3, 24, 'eax') + '''
  jmp gt_n3
gt_d3:
  mov ecx,dword ptr [{DEVPTR}]
  mov byte ptr [ecx+0x1354],1
gt_n3:
  mov eax,dword ptr [{TTSAV}+16]
  cmp eax,0xFFFFFFFF
  je gt_d4
''' + TSS(4, 24, 'eax') + '''
  jmp gt_n4
gt_d4:
  mov ecx,dword ptr [{DEVPTR}]
  mov byte ptr [ecx+0x146C],1
gt_n4:
''' + REL('dword ptr [{DSP}]', 'g_nods') + '''
g_relbb:
''' + REL('dword ptr [{BBP}]', 'g_nobb') + '''
g_out:
  pop ebp
  pop edi
  pop ebx
g_ret0:
  ret
g_fail:
  mov dword ptr [{GLFAIL}],esi
  jmp g_out
'''

def src(base, sym=False):
    base = base or 0
    A = {k: ('0x%X' % (base + v) if not sym else k) for k, v in DO.items()}
    A.update({n: ('0x%X' % (base + DO['GLRES'] + 4 * i) if not sym else n) for i, n in enumerate(GLRES_NAMES)})
    keep = ('DEVPTR', 'WSCENE', 'TGT', 'TGT4', 'MOV', 'MOV4', 'SHADERS', 'C2', 'C3', 'C4', 'C5', 'PARTY', 'RAIDARR', 'RAIDCNT') + tuple(FLAGS)
    A.update({k: ('0x%X' % v if not sym else ('0x%X' % v if k not in keep else k)) for k, v in X.items()})
    if sym: A.update(GETTICK='GetTickCount', PULSE=str(PULSE_MS))   # nur fuer die Kommentare
    def f(s):
        for k, v in sorted(A.items(), key=lambda kv: -len(kv[0])): s = s.replace('{' + k + '}', v)
        return s
    s = '''
vpcap:
  push esi
  push edi
  push ecx
  lea esi,[ebp-0x24]
  mov edi,{VP}
  mov ecx,6
  cld
  .byte 0xF3,0xA5
  pop ecx
  pop edi
  pop esi
  mov eax,[esi+0x397c]
  jmp {VPRET}
batch:
  mov eax,[esi+0x40]
  cmp eax,dword ptr [{WSCENE}]
  jne b_plain
  call ensure
  mov eax,[esi+0x60]
  call classify
  mov dword ptr [{CUR}],eax
  mov ecx,esi
  call {DRAWBATCH}
  mov dword ptr [{CUR}],0
  jmp {AFTERB}
b_plain:
  mov ecx,esi
  call {DRAWBATCH}
  jmp {AFTERB}
okdev:
  mov ecx,dword ptr [{DEVPTR}]
  xor eax,eax
  test ecx,ecx
  jz ok_r
  cmp dword ptr [ecx],{VT9}
  jne ok_r
  mov edx,[ecx+0x1CC]
  cmp edx,5
  jb ok_r
  cmp edx,6
  ja ok_r
  mov eax,[ecx+0x397C]
ok_r:
  ret
ensure:
  cmp dword ptr [{VALID}],0
  jne e_ret
  mov dword ptr [{VALID}],1
  mov dword ptr [{NUNITS}],0
  mov dword ptr [{SELFCAT}],0
  mov dword ptr [{GRPN}],0
  mov dword ptr [{WPROT}],0
  mov dword ptr [{GMODE}],0
  cmp byte ptr [{FWALLSGRP}],1
  jne e_gm
  mov dword ptr [{GMODE}],2
  cmp byte ptr [{FPARTY}],1
  je e_g1
  cmp byte ptr [{FRAID}],1
  jne e_gm
e_g1:
  mov dword ptr [{GMODE}],1
e_gm:
  call okdev
  test eax,eax
  jz e_ret
  push esi
  push edi
  push ebx
  call {PLAYERGUID}
  mov dword ptr [{PGUID}],eax
  mov dword ptr [{PGUID}+4],edx
  cmp byte ptr [{FRAID}],1
  je e_r
  cmp dword ptr [{GMODE}],2
  jne e_party
e_r:
  mov ebx,dword ptr [{RAIDCNT}]
  cmp ebx,40
  jbe e_rok
  mov ebx,40
e_rok:
  xor edi,edi
e_rloop:
  cmp edi,ebx
  jae e_party
  mov esi,dword ptr [{RAIDARR}+edi*4]
  test esi,esi
  jz e_rnext
  call same_tms
  je e_rnext
  call add_unit
  test eax,eax
  jz e_rnext
  call in_party
  je e_rnext
  mov byte ptr [{THIN}+eax],1
e_rnext:
  inc edi
  jmp e_rloop
e_party:
  cmp byte ptr [{FPARTY}],1
  je e_p
  cmp byte ptr [{FRAID}],1
  je e_p
  cmp dword ptr [{GMODE}],2
  jne e_self
e_p:
  mov esi,{PARTY}
  mov edi,4
e_ploop:
  call same_tms
  je e_pnext
  call add_unit
e_pnext:
  add esi,8
  dec edi
  jnz e_ploop
e_self:
  mov eax,dword ptr [{NUNITS}]
  mov dword ptr [{GRPN}],eax
  cmp dword ptr [{GMODE}],1
  jne e_wp
  mov dword ptr [{WPROT}],eax
e_wp:
  cmp byte ptr [{FSELF}],1
  je e_s
  cmp byte ptr [{FHIDDEN}],1
  jne e_tgt
e_s:
  mov esi,{PGUID}
  call same_tm
  je e_tgt
  call add_unit
  mov dword ptr [{SELFCAT}],eax
e_tgt:
  mov esi,{TGT}
  call add_unit
  mov esi,{MOV}
  call same_tgt
  je e_done
  call add_unit
e_done:
  pop ebx
  pop edi
  pop esi
e_ret:
  ret
same_tgt:
  mov eax,[esi]
  cmp eax,dword ptr [{TGT}]
  jne s_r
  mov eax,[esi+4]
  cmp eax,dword ptr [{TGT4}]
s_r:
  ret
same_tm:
  call same_tgt
  je s_r2
  mov eax,[esi]
  cmp eax,dword ptr [{MOV}]
  jne s_r2
  mov eax,[esi+4]
  cmp eax,dword ptr [{MOV4}]
s_r2:
  ret
same_tms:
  call same_tm
  je s_r3
  mov eax,[esi]
  cmp eax,dword ptr [{PGUID}]
  jne s_r3
  mov eax,[esi+4]
  cmp eax,dword ptr [{PGUID}+4]
s_r3:
  ret
add_unit:
  mov eax,[esi]
  or eax,[esi+4]
  jz au_zero
  push edi
  push ebx
  mov ecx,dword ptr [{NUNITS}]
  mov edi,{UNITS}
au_dup:
  test ecx,ecx
  jz au_new
  mov eax,[edi]
  cmp eax,[esi]
  jne au_dn
  mov eax,[edi+4]
  cmp eax,[esi+4]
  je au_none
au_dn:
  add edi,24
  dec ecx
  jmp au_dup
au_new:
  cmp dword ptr [{NUNITS}],48
  jae au_none
  push 0
  push {FILESTR}
  push 0x18
  push dword ptr [esi+4]
  push dword ptr [esi]
  call {OBJPTR}
  add esp,0x14
  test eax,eax
  jz au_none
  mov ebx,eax
  mov eax,[esi]
  mov [edi],eax
  mov eax,[esi+4]
  mov [edi+4],eax
  mov eax,[ebx+0xB4]
  mov [edi+8],eax
  mov eax,[ebx+0x98C]
  mov [edi+12],eax
  mov dword ptr [edi+20],0
  cmp byte ptr [{FREACT}],1
  je au_sel
  push 0
  push {FILESTR}
  push 0x10
  push dword ptr [esi+4]
  push dword ptr [esi]
  call {OBJPTR}
  add esp,0x14
  test eax,eax
  jz au_sel
  mov ecx,[ebx+0xD0]
  test ecx,ecx
  jz au_sel
  movzx ecx,byte ptr [ecx+0x45]
  cmp ecx,11
  ja au_sel
  mov ecx,dword ptr [{CLS}+ecx*4]
  test ecx,ecx
  jz au_sel
  mov [edi+16],ecx
  lea eax,[edi+20]
  push 1
  push eax
  push esi
  call {SELCOL}
  add esp,0xC
  cmp dword ptr [edi+20],{HOSTILE}
  je au_ok
  mov dword ptr [edi+20],0
  jmp au_ok
au_sel:
  lea eax,[edi+16]
  push 1
  push eax
  push esi
  call {SELCOL}
  add esp,0xC
au_ok:
  inc dword ptr [{NUNITS}]
  mov eax,dword ptr [{NUNITS}]
  mov byte ptr [{THIN}+eax],0
  pop ebx
  pop edi
  ret
au_none:
  pop ebx
  pop edi
au_zero:
  xor eax,eax
  ret
in_party:
  push ecx
  push edx
  mov ecx,{PARTY}
  mov edx,4
ip_l:
  push eax
  mov eax,[esi]
  cmp eax,[ecx]
  jne ip_n
  mov eax,[esi+4]
  cmp eax,[ecx+4]
ip_n:
  pop eax
  je ip_r
  add ecx,8
  dec edx
  jnz ip_l
  or edx,1
ip_r:
  pop edx
  pop ecx
  ret
classify:
  test eax,eax
  jz c_none
  push esi
  mov ecx,eax
  mov edx,3
c_loop:
  mov eax,dword ptr [{NUNITS}]
c_u:
  test eax,eax
  jz c_next
  lea esi,[eax+eax*2]
  lea esi,[{UNITS}-24+esi*8]
  cmp ecx,[esi+8]
  je c_hit
  cmp ecx,[esi+12]
  je c_hit
  dec eax
  jmp c_u
c_next:
  mov ecx,[ecx+0x48]
  test ecx,ecx
  jz c_out
  dec edx
  jnz c_loop
c_out:
  pop esi
c_none:
  xor eax,eax
  ret
c_hit:
  pop esi
  ret
dip:
  mov eax,dword ptr [{CUR}]
  test eax,eax
  jnz d_mark
  call smode
  test eax,eax
  jnz d_two
  mov eax,[esp+4]
  mov eax,[eax]
  jmp dword ptr [eax+0x148]
d_two:
  push ebp
  mov ebp,esp
  push ebx
  push esi
  push edi
  mov esi,[ebp+8]
  call do_dip
  mov ebx,eax
  call two_on
  call do_dip
  call two_off
  mov eax,ebx
  pop edi
  pop esi
  pop ebx
  pop ebp
  ret 0x1C
dp:
  cmp dword ptr [{CUR}],0
  jne dp_cur
  call smode
  test eax,eax
  jnz dp_two
dp_go:
  mov eax,[esp+4]
  mov eax,[eax]
  jmp dword ptr [eax+0x144]
dp_cur:
  cmp dword ptr [{SMODE}],0
  je dp_go
  mov dword ptr [{SMODE}],0
  push esi
  mov esi,[esp+8]
''' + SRS(52, 0) + '''
  pop esi
  jmp dp_go
dp_two:
  push ebp
  mov ebp,esp
  push ebx
  push esi
  push edi
  mov esi,[ebp+8]
  call do_dp
  mov ebx,eax
  call two_on
  call do_dp
  call two_off
  mov eax,ebx
  pop edi
  pop esi
  pop ebx
  pop ebp
  ret 0x10
do_dp:
  push dword ptr [ebp+0x14]
  push dword ptr [ebp+0x10]
  push dword ptr [ebp+0xC]
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x144]
  ret
smode:
  cmp dword ptr [{MARKED}],0
  je sm_0
  cmp byte ptr [{FWALLS}],1
  je sm_0
  mov ecx,dword ptr [{DEVPTR}]
  xor eax,eax
  cmp dword ptr [ecx+0x3E70],0
  setne al
  cmp dword ptr [{WPROT}],0
  jne sm_r
  cmp eax,dword ptr [{SMODE}]
  je sm_0
  mov dword ptr [{SMODE}],eax
  push esi
  mov esi,[esp+0xC]
  test eax,eax
  jz sm_off
''' + SRS(52, 1) + SRS(56, 8) + SRS(55, 2) + SRS(53, 1) + SRS(54, 1) + SRS(59, 0xFF) + '''
  jmp sm_done
sm_off:
''' + SRS(52, 0) + '''
sm_done:
  pop esi
sm_0:
  xor eax,eax
sm_r:
  ret
two_on:
''' + SRS(168, 0) + SRS(14, 0) + SRS(23, 3) + SRS(52, 1) + SRS(56, 2) + SRS(57, 'dword ptr [{WPROT}]') + SRS(55, 2) + SRS(53, 1) + SRS(54, 1) + SRS(58, 0xFF) + SRS(59, 0xFF) + '''
  ret
two_off:
''' + SRS(52, 0) + '''
  mov ecx,dword ptr [{DEVPTR}]
  mov eax,dword ptr [ecx+0x3E88]
  lea edx,[eax-1]
  cmp edx,7
  jbe t_zf
  mov eax,4
t_zf:
''' + SRS(23, 'eax') + '''
  mov ecx,dword ptr [{DEVPTR}]
  mov dword ptr [ecx+0x3E70],0xFFFFFFFF
  mov dword ptr [ecx+0x3E74],0xFFFFFFFF
  mov eax,[ecx+0x2900]
  mov dword ptr [eax+0xF0],0xFFFFFFFE
  mov dword ptr [eax+0x100],0xFFFFFFFE
  push 15
  call {MARKDIRTY}
  mov ecx,dword ptr [{DEVPTR}]
  push 16
  call {MARKDIRTY}
  ret
d_mark:
  push ebp
  mov ebp,esp
  push ebx
  push esi
  push edi
  mov esi,[ebp+8]
  cmp dword ptr [{SMODE}],0
  je d_nosm
  mov dword ptr [{SMODE}],0
''' + SRS(52, 0) + '''
d_nosm:
  mov ecx,dword ptr [{DEVPTR}]
  cmp dword ptr [ecx+0x3E60],0
  jne d_plain
  xor edi,edi
  mov eax,dword ptr [{CUR}]
  cmp byte ptr [{FHIDDEN}],1
  jne d_mg
  cmp eax,dword ptr [{SELFCAT}]
  jne d_mg
  mov edi,2
  jmp d_m2
d_mg:
  cmp eax,dword ptr [{GRPN}]
  ja d_m1
  mov edi,dword ptr [{GMODE}]
  test edi,edi
  jnz d_m2
d_m1:
  cmp byte ptr [{FWALLS}],1
  jne d_m2
  mov edi,1
d_m2:
  mov dword ptr [{MODE}],edi
  mov edi,1
  test dword ptr [{MODE}],0xFF
  jz d_zk
  mov edi,3
d_zk:
''' + SRS(52, 1) + SRS(56, 8) + SRS(57, FIG) + SRS(55, 3) + SRS(53, 1) + SRS(54, 'edi') + SRS(58, 0xFF) + SRS(59, 0xFF) + '''
  call do_dip
  mov dword ptr [{MARKED}],1
  cmp dword ptr [{SHADERS}],0
  je d_end
  mov ecx,dword ptr [{DEVPTR}]
  mov ebx,dword ptr [ecx+0x3E88]
  lea eax,[ebx-1]
  cmp eax,7
  jbe d_zf
  mov ebx,4
d_zf:
  cmp dword ptr [{MODE}],0
  jne d_cw
''' + SRS(56, 3) + '''
  mov eax,dword ptr [{CUR}]
  or eax,0x80
''' + SRS(57, 'eax') + SRS(58, 0x7F) + SRS(23, 8) + '''
  call do_dip
''' + SRS(23, 'ebx') + SRS(58, 0xFF) + SRS(56, 5) + '''
  mov eax,dword ptr [{CUR}]
''' + SRS(57, 'eax') + SRS(168, 0) + SRS(14, 1) + '''
  jmp d_copies
d_cw:
''' + SRS(56, 5) + SRS(54, 1) + '''
  mov eax,dword ptr [{CUR}]
''' + SRS(57, 'eax') + SRS(168, 0) + SRS(14, 0) + '''
  mov eax,8
  cmp dword ptr [{MODE}],2
  jne d_zw
  mov eax,5
d_zw:
''' + SRS(23, 'eax') + '''
d_copies:
  fild dword ptr [{VP}+8]
  fdivr dword ptr [{TWO}]
  fstp dword ptr [{SX}]
  fild dword ptr [{VP}+12]
  fdivr dword ptr [{MTWO}]
  fstp dword ptr [{SY}]
  mov dword ptr [{KZ}],0
  cmp dword ptr [{MODE}],2
  jne d_kz
  fld dword ptr [{C5}]
  fmul dword ptr [{C5}]
  fld dword ptr [{C5}+4]
  fmul dword ptr [{C5}+4]
  faddp st(1),st(0)
  fld dword ptr [{C5}+8]
  fmul dword ptr [{C5}+8]
  faddp st(1),st(0)
  fstp dword ptr [{FX}]
  cmp dword ptr [{FX}],0
  je d_kz
  fld dword ptr [{C4}]
  fmul dword ptr [{C5}]
  fld dword ptr [{C4}+4]
  fmul dword ptr [{C5}+4]
  faddp st(1),st(0)
  fld dword ptr [{C4}+8]
  fmul dword ptr [{C5}+8]
  faddp st(1),st(0)
  fdiv dword ptr [{FX}]
  fstp dword ptr [{FY}]
  fld dword ptr [{C4}+12]
  fdiv dword ptr [{FY}]
  fsub dword ptr [{C5}+12]
  fmul dword ptr [{KAP}]
  fstp dword ptr [{KZ}]
d_kz:
  xor edi,edi
d_loop:
  fld dword ptr [{OFFS}+edi*8]
  fmul dword ptr [{SX}]
  fstp dword ptr [{FX}]
  fld dword ptr [{OFFS}+edi*8+4]
  fmul dword ptr [{SY}]
  fstp dword ptr [{FY}]
''' + ''.join('''  fld dword ptr [{C5}+%d]
  fmul dword ptr [{FX}]
  fadd dword ptr [{C2}+%d]
  fstp dword ptr [{MAT}+%d]
  fld dword ptr [{C5}+%d]
  fmul dword ptr [{FY}]
  fadd dword ptr [{C3}+%d]
  fstp dword ptr [{MAT}+%d]
''' % (4 * k, 4 * k, 4 * k, 4 * k, 4 * k, 16 + 4 * k) for k in range(4)) + ''.join('''  fld dword ptr [{C5}+%d]
  fmul dword ptr [{KZ}]
  fadd dword ptr [{C4}+%d]
  fstp dword ptr [{MAT}+%d]
''' % (4 * k, 4 * k, 32 + 4 * k) for k in range(4)) + ''.join('''  mov eax,dword ptr [{C5}+%d]
  mov dword ptr [{MAT}+%d],eax
''' % (4 * k, 48 + 4 * k) for k in range(4)) + '''
  push 4
  push {MAT}
  push 2
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x178]
  call do_dip
  inc edi
  cmp edi,8
  jb d_loop
  push 4
  push {C2}
  push 2
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x178]
  mov ecx,dword ptr [{DEVPTR}]
  mov dword ptr [ecx+0x3E70],0xFFFFFFFF
  mov dword ptr [ecx+0x3E74],0xFFFFFFFF
  mov eax,[ecx+0x2900]
  mov dword ptr [eax+0xF0],0xFFFFFFFE
  mov dword ptr [eax+0x100],0xFFFFFFFE
  push 15
  call {MARKDIRTY}
  mov ecx,dword ptr [{DEVPTR}]
  push 16
  call {MARKDIRTY}
  cmp dword ptr [{MODE}],0
  je d_end
''' + SRS(23, 'ebx') + '''
d_end:
  cmp dword ptr [{MODE}],0
  je d_off
''' + SRS(54, 1) + '''
d_off:
''' + SRS(52, 0) + '''
  jmp d_ret
d_plain:
  call do_dip
d_ret:
  xor eax,eax
  pop edi
  pop esi
  pop ebx
  pop ebp
  ret 0x1C
do_dip:
  push dword ptr [ebp+0x20]
  push dword ptr [ebp+0x1C]
  push dword ptr [ebp+0x18]
  push dword ptr [ebp+0x14]
  push dword ptr [ebp+0x10]
  push dword ptr [ebp+0xC]
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x148]
  ret
post:
  pushad
  cmp dword ptr [{MARKED}],0
  je p_clear
  call okdev
  test eax,eax
  jz p_reset
  mov esi,eax
  cmp dword ptr [{PSDEV}],esi
  je p_ps
  mov dword ptr [{PS}],0
  mov dword ptr [{PSDEV}],esi
  push {PS}
  push {PSCODE}
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x1A8]
p_ps:
  cmp dword ptr [{PS}],0
  je p_clear
''' + SRS(52, 1) + SRS(56, 3) + SRS(55, 1) + SRS(53, 1) + SRS(54, 1) + SRS(58, 0xFF) + SRS(23, 8) + SRS(14, 0) + SRS(27, 0) + SRS(15, 0) + SRS(22, 1) + SRS(168, 0xF) + SRS(28, 0) + '''
  push 0
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x170]
  push dword ptr [{PS}]
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x1AC]
  push 0x44
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x164]
  fild dword ptr [{VP}]
  fsub dword ptr [{HALF}]
  fst dword ptr [{VERTS}]
  fstp dword ptr [{VERTS}+40]
  fild dword ptr [{VP}]
  fiadd dword ptr [{VP}+8]
  fsub dword ptr [{HALF}]
  fst dword ptr [{VERTS}+20]
  fstp dword ptr [{VERTS}+60]
  fild dword ptr [{VP}+4]
  fsub dword ptr [{HALF}]
  fst dword ptr [{VERTS}+4]
  fstp dword ptr [{VERTS}+24]
  fild dword ptr [{VP}+4]
  fiadd dword ptr [{VP}+12]
  fsub dword ptr [{HALF}]
  fst dword ptr [{VERTS}+44]
  fstp dword ptr [{VERTS}+64]
  call dword ptr [{GETTICK}]
  xor edx,edx
  mov ecx,{PULSE}
  div ecx
  mov dword ptr [{TMP}],edx
  fild dword ptr [{TMP}]
  fmul dword ptr [{PW}]
  fcos
  fchs
  fld1
  faddp st(1),st(0)
  fmul dword ptr [{K128}]
  fistp dword ptr [{T8}]
  call glow
  mov ebx,dword ptr [{NUNITS}]
p_loop:
  test ebx,ebx
  jz p_done
  call ucol
  cmp dword ptr [{GLOK}],0
  je p_q
  cmp byte ptr [{THIN}+ebx],0
  jne p_q
  mov eax,edx
  shr eax,2
  and eax,0x3F3F3F
  mov ecx,edx
  shr ecx,3
  and ecx,0x1F1F1F
  and edx,0xFFFFFF
  sub edx,eax
  sub edx,ecx
  add edx,0xFF5E5E5E
p_q:
  call quad
  dec ebx
  jmp p_loop
p_done:
  mov ecx,dword ptr [{DEVPTR}]
  call {FORCEUPD}
  mov edx,dword ptr [{DEVPTR}]
''' + ''.join('  mov dword ptr [edx+0x%X],0xFFFFFFFF\n' % (0x3BC4 + 4 * i) for i in HWCACHE_DIRTY) + '''  mov dword ptr [edx+0x3B5C],0
  mov dword ptr [edx+0x3B64],0
  mov dword ptr [edx+0x3B84],0xFFFFFFFF
  mov dword ptr [edx+0x3BA4],0xFFFFFFFF
p_clear:
  call okdev
  test eax,eax
  jz p_reset
  mov esi,eax
  push 0
  push 0x3F800000
  push 0
  push 4
  push 0
  push 0
  push esi
  mov eax,[esi]
  call dword ptr [eax+0xAC]
''' + SRS(52, 0) + '''
p_reset:
  mov dword ptr [{SMODE}],0
  mov dword ptr [{MARKED}],0
  mov dword ptr [{VALID}],0
  popad
  jmp {CIRCLES}
quad:
  mov dword ptr [{VERTS}+16],edx
  mov dword ptr [{VERTS}+36],edx
  mov dword ptr [{VERTS}+56],edx
  mov dword ptr [{VERTS}+76],edx
''' + SRS(57, 'ebx') + '''
  push 20
  push {VERTS}
  push 2
  push 5
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x14C]
  ret
blend:
  push esi
  push edi
  mov esi,dword ptr [{T8}]
  mov edi,256
  sub edi,esi
  mov eax,edx
  and eax,0xFF00FF
  imul eax,edi
  push ecx
  and ecx,0xFF00FF
  imul ecx,esi
  add eax,ecx
  shr eax,8
  and eax,0xFF00FF
  pop ecx
  and edx,0xFF00
  imul edx,edi
  and ecx,0xFF00
  imul ecx,esi
  add edx,ecx
  shr edx,8
  and edx,0xFF00
  or edx,eax
  or edx,0xFF000000
  pop edi
  pop esi
  ret
sortp:
  mov eax,[esp+0x10]
  cmp eax,dword ptr [{WSCENE}]
  jne sp_jmp
  push esi
  push edi
  push ebx
  mov edi,[esp+0x14]
  mov ebx,[esp+0x18]
  mov dword ptr [{NMARK}],0
  mov dword ptr [{MLIST}],edi
  mov dword ptr [{MCOUNT}],ebx
  call ensure
  cmp dword ptr [{NUNITS}],0
  je sp_none
  mov esi,[esp+0x1C]
sp_m:
  test ebx,ebx
  jz sp_sort
  dec ebx
  mov eax,[edi+ebx*4]
  call item
  cmp dword ptr [eax],0
  jne sp_m
  push eax
  mov eax,[eax+4]
  call classify
  pop ecx
  test eax,eax
  jz sp_m
  mov dword ptr [ecx],0x10
  inc dword ptr [{NMARK}]
  jmp sp_m
sp_sort:
  cmp dword ptr [{NMARK}],0
  je sp_none
  push esi
  push dword ptr [esp+0x1C]
  push edi
  call sp_go
sp_cw:
  jmp cmpw
sp_go:
  call {QSORT}
  add esp,0x10
  mov ebx,[esp+0x18]
sp_r:
  test ebx,ebx
  jz sp_done
  dec ebx
  mov eax,[edi+ebx*4]
  call item
  cmp dword ptr [eax],0x10
  jne sp_r
  mov dword ptr [eax],0
  jmp sp_r
sp_done:
  pop ebx
  pop edi
  pop esi
  ret
sp_none:
  pop ebx
  pop edi
  pop esi
sp_jmp:
  jmp {QSORT}
item:
  mov ecx,eax
  shl ecx,4
  add ecx,eax
  mov eax,[esi+0x3C]
  lea eax,[eax+ecx*4]
  ret
cmpw:
  push ebp
  mov ebp,esp
  push esi
  push edi
  mov esi,[ebp+0x10]
  mov eax,[ebp+8]
  call item
  mov edi,eax
  mov eax,[ebp+0xC]
  call item
  cmp dword ptr [edi],0x10
  jne cw_orig
  cmp dword ptr [eax],0x10
  jne cw_orig
  mov dword ptr [edi],0
  mov dword ptr [eax],0
  push eax
  push eax
  push edi
  call {CMPBATCH}
  add esp,8
  pop ecx
  mov dword ptr [edi],0x10
  mov dword ptr [ecx],0x10
  jmp cw_ret
cw_orig:
  push dword ptr [ebp+0x10]
  push dword ptr [ebp+0xC]
  push dword ptr [ebp+8]
  call {CMPOPA}
  add esp,0xC
cw_ret:
  pop edi
  pop esi
  pop ebp
  ret
draw1:
  cmp dword ptr [esp+4],0
  jne dr_go
  mov eax,[ecx+0x40]
  cmp eax,dword ptr [{WSCENE}]
  jne dr_go
  mov eax,dword ptr [{NMARK}]
  test eax,eax
  jz dr_go
  mov edx,[esp+0xC]
  cmp edx,dword ptr [{MLIST}]
  jne dr_go
  mov edx,[esp+0x10]
  cmp edx,dword ptr [{MCOUNT}]
  jne dr_go
  sub [esp+0x10],eax
dr_go:
  jmp {DRAWLIST}
draw2:
  mov eax,[ecx+0x40]
  cmp eax,dword ptr [{WSCENE}]
  jne dr_go
  cmp dword ptr [{NMARK}],0
  je dr_go
  mov edx,[eax+0x5C]
  cmp edx,dword ptr [{MLIST}]
  jne dr_go
  mov edx,[eax+0x58]
  cmp edx,dword ptr [{MCOUNT}]
  jne dr_go
  push esi
  mov esi,ecx
  push dword ptr [esp+0x14]
  push dword ptr [esp+0x14]
  push dword ptr [esp+0x14]
  push dword ptr [esp+0x14]
  call {DRAWLIST}
  mov eax,dword ptr [{MCOUNT}]
  sub eax,dword ptr [{NMARK}]
  mov edx,dword ptr [{MLIST}]
  lea edx,[edx+eax*4]
  push dword ptr [{NMARK}]
  push edx
  push dword ptr [esp+0x14]
  push 0
  mov ecx,esi
  call {DRAWLIST}
  pop esi
  ret 0x10
''' + GLOW
    return f(s)

def data():
    # Datenlayout pruefen: keine Ueberlappung, alles vor CODE_OFF
    iv = sorted((DO[k], DO[k] + SIZES[k], k) for k in DO)
    for (a, b, k), (c, _, k2) in zip(iv, iv[1:]): assert b <= c, (k, k2)
    assert iv[-1][1] <= CODE_OFF
    d = bytearray(CODE_OFF)
    for i in range(4): struct.pack_into('<ff', d, DO['VERTS'] + i * 20 + 8, 0.0, 1.0)
    for i, (x, y) in enumerate(OFFS): struct.pack_into('<ff', d, DO['OFFS'] + i * 8, x, y)
    struct.pack_into('<f', d, DO['TWO'], 2.0); struct.pack_into('<f', d, DO['MTWO'], -2.0); struct.pack_into('<f', d, DO['HALF'], 0.5)
    struct.pack_into('<5I', d, DO['PSCODE'], 0xFFFF0101, 0x00000001, 0x800F0000, 0x90E40000, 0x0000FFFF)
    for k, v in CLASSCOL.items(): struct.pack_into('<I', d, DO['CLS'] + 4 * k, v)
    struct.pack_into('<ff', d, DO['K128'], 128.0, 2 * math.pi / PULSE_MS)
    struct.pack_into('<f', d, DO['KAP'], KAPPA)
    struct.pack_into('<ff', d, DO['O1'], *BLUR_O)
    for k in range(4): struct.pack_into('<ff', d, DO['VERTT'] + 56 * k + 8, 0.0, 1.0)
    g = psasm.blur_ps(*BLUR_W); c = psasm.comp_ps(GLOW_GAIN)
    assert len(g) == SIZES['GPSCODE'] and len(c) == SIZES['CPSCODE']
    d[DO['GPSCODE']:DO['GPSCODE'] + len(g)] = g; d[DO['CPSCODE']:DO['CPSCODE'] + len(c)] = c
    return d

def reloc2():
    a = asm(src(B1), B1 + CODE_OFF); b = asm(src(B2), B2 + CODE_OFF)
    assert len(a) == len(b)
    delta = B2 - B1; absf = []; relf = []; done = set()
    for k in [k for k in range(len(a)) if a[k] != b[k]]:
        if k in done: continue
        for s in range(k - 3, k + 1):
            if s < 0 or s + 4 > len(a): continue
            va = struct.unpack_from('<I', a, s)[0]; vb = struct.unpack_from('<I', b, s)[0]
            if (vb - va) & 0xFFFFFFFF == delta: absf.append(s + CODE_OFF); done.update(range(s, s + 4)); break
            if (va - vb) & 0xFFFFFFFF == delta: relf.append(s + CODE_OFF); done.update(range(s, s + 4)); break
        else: raise Exception(hex(k))
    return a, absf, relf

code, absf, relf = reloc2()
TPL = bytes(data()) + code
LAB = {k: CODE_OFF + v for k, v in label_offsets(src(B1), B1 + CODE_OFF,
       ['vpcap', 'batch', 'dip', 'dp', 'smode', 'two_on', 'two_off', 'post', 'okdev', 'ensure', 'add_unit', 'classify', 'quad', 'blend', 'same_tgt', 'same_tm', 'same_tms', 'sortp', 'item', 'cmpw', 'sp_cw', 'draw1', 'draw2',
        'in_party', 'ucol', 'glfree', 'glrel', 'mkq', 'g_pass', 'glow']).items()}
if __name__ == '__main__':
    print('size', hex(len(TPL)), 'code', hex(len(code)), 'abs', len(absf), 'rel', len(relf), {k: hex(v) for k, v in LAB.items()})

# Outline (Nr. 68) mit Optionen: Ziel, Mouseover, eigener Charakter, 5er-Gruppe, Schlachtzug,
# eigener Charakter nur wo verdeckt, durch Waende, Klassen- bzw. Gesinnungsfarbe; feindliche
# Spieler in Klassenfarbe pulsieren sanft rot (WoW 3.3.5a 12340). Weiterentwicklung von outline4.py:
# "nur wo verdeckt" - Kopien mit STENCILZFAIL KEEP und Tiefen-Abstand (KZ aus der Projektion).
# outline7: Durch Waende nur fuer Gruppe/Schlachtzug (GMODE 1); ohne Gruppen-Umrandung werden
# Gruppe/Schlachtzug dann nur wo verdeckt umrandet (GMODE 2). Spaeter Gezeichnetes loescht nur
# Raender ueber WPROT (Gruppen-Raender durch Waende bleiben).
# outline10: weicher Schein wie in Retail fuer dich, Gruppe, Ziel und Mouseover: die duenne Linie wird
# in eine Render-Textur gezeichnet, per ps_2_0 weichgezeichnet (Gauss, halbe Aufloesung) und ausserhalb
# der Figuren eingeblendet. Alle umrandeten Einheiten bekommen den Schein; THIN (nur duenne Linie) haben nur noch
# die Begleiter, die bloss zum Sortieren in der Tabelle stehen (PETF 2).
# Vor IDirect3DDevice9::Reset bzw. dem Abbau (Aufrufe von 0x690150 bei VA 0x69029D, 0x6A337F, 0x69040B)
# werden die Texturen freigegeben.
# outline8: Sortierung von Pass 0 der Welt-Szene (VA 0x822FDD): Teile umrandeter Einheiten kommen
# ans Ende der undurchsichtigen M2-Teile, untereinander in der Reihenfolge des Spiels. Beim Zeichnen
# von Pass 0 (VA 0x823D1F/0x823D3B) kommen sie erst nach den gebuendelten Doodads (M2BatchDoodads),
# damit Laternen, Briefkaesten usw. schon im Tiefenpuffer liegen ("nur wo verdeckt" erkennt sie).
# Stencil: Figur 0xC0 (0x80 Figur, 0x40 sichtbar), Rand 0x40 | Kategorie. Spaeter Gezeichnetes mit Tiefe
# (DrawIndexedPrimitive VA 0x6A36C8 und DrawPrimitive VA 0x6A3706): STENCILFUNC ALWAYS, PASS ZERO, Schreibmaske 0xC0 -
# es wird immer gezeichnet (vorher LESS gegen WPROT: alles auf Stencil 0 fiel weg, z.B. die Namen ueber den Koepfen)
# und loescht dort, wo es vorne liegt, Figur- und Sichtbar-Bit. Geschuetzte Gruppen-Raender (Kategorie bis WPROT)
# faerbt Post mit Maske 0x3F, also auch dort.
# Begleiter: Pets/Begleiter (CHARMEDBY/SUMMONEDBY/CREATEDBY) der Gruppen-Eintraege kommen mit der Farbe ihres
# Besitzers in die Tabelle (PETF 1); bei "nur wo verdeckt" (ich oder GMODE 2) die eigenen (und die der Gruppe, wenn
# sie nicht in der Tabelle ist) nur zum Sortieren (PETF 2, keine Umrandung). Pass 0: Begleiter (Markierung 0x11) nach allen umrandeten Teilen (0x10) -
# so loesen sie "nur wo verdeckt" nicht aus. Culling (VA 0x7934C6): Gruppen-Eintraege (bei "durch Waende alle" alle)
# werden auch dann gezeichnet, wenn das Spiel sie in einem anderen Gebaeude/hinter dem Horizont aussortiert.
# Schein gegen Flimmern (agent_shimmer): Verkleinern mit 4x4-Zelt (tent_ps, Pixelshader TPS) statt 2x2-Kasten,
# die Kurve 1-(1-y)^2, y = sat(2.5*x) (statt mal 4 mit Saettigung) schon im senkrechten Durchgang (blur_soft_ps, VPS):
# TEX1 haelt die Deckkraft mit vollen 8 Bit (vorher wurden 8-Bit-Stufen mal 4 verstaerkt), Einblenden mit Faktor 1.
# Duenne Stellen (agent_tips): Ohrspitzen, Stacheln usw. sind duenner als ein Pixel und werden nur als Punkte gerastert.
# Die Kopien um 2 Pixel machten daraus einzelne Punkte im Abstand 2 mit Luecken direkt an der Figur, die von Bild zu
# Bild wechselten. Jetzt liegen 4 Kopien diagonal 1 Pixel neben der Figur (+-1, +-1) und 4 einen halben Pixel daneben
# (+-0.5, 0), (0, +-0.5): Der Rand ist 1 Pixel breit und auch um einzelne Punkte geschlossen; die halben Pixel tasten
# duenne Stellen an weiteren Stellen ab (wie zusaetzliche Abtastpunkte), liegen aber innerhalb des Quadrats der
# ganzzahligen Kopien und aendern an geraden Kanten nichts (kein Pumpen). Die Linie entsteht im Schein: line_ps (LPS)
# macht aus TEX0 per 3x3-Zelt und Saettigung (k = 4) die 2 Pixel breite,
# geglaettete Linie in TEX3 (volle Aufloesung, vormultipliziert), daraus kommt auch der Schein (Zelt nach TEX1 ...,
# GLOW_K 2.0); eingeblendet wird sie nach dem Schein aufgehellt (linecomp_ps, LCPS). Die Vierecke je Einheit gibt es
# nur noch ohne Schein (GLOK 0); ist der Schein auf dem Geraet fehlgeschlagen (GLFAIL), liegen die Kopien wie bisher
# 2 Pixel weit (OFFS2), damit die duennen Linien 2 Pixel breit bleiben.
# Fuesse im Boden (agent_feet): "nur wo verdeckt" markierte den Rand auch dort, wo die Figur nur IN etwas steckt
# (Fuesse leicht im Boden, Figur halb in einer Wand) - der Boden vor dem eingesunkenen Fuss liegt bei flachem Blick
# um s / sin(Winkel) vor ihm, mehr als KZ (0,001 * d^2). Jetzt liegen alle Kopien eines Teils auf EINER Tiefe:
# der Vorderseite der Huellkugel (naechster Punkt zur Kamera) - c4' = (ZC + KZ) * c5, also z/w = ZC + KZ fuer jeden
# Punkt. Kugeln (Mitte des M2-Huellquaders, Radius aus dem M2-Kopf: [[Modell+0x2C]+0x150] +0xA0/+0xAC/+0xB8) in
# Sichtkoordinaten ueber die Modell-Sicht-Matrix [Modell+0xF4] (Welt [Modell+0xB4] mal Sicht der Szene, 0x82F2F5;
# c2-c5 sind nur die Projektion, 0x872C10), genommen wird die vorderste von gezeichnetem Teil (CURM) und seinen
# Eltern, soweit sie Figur oder Reittier der Einheit sind. Nur Modelle, die in diesem Bild bewegt wurden ([Modell+0x3C] = [[Modell+0x28]+0x14],
# 0x830961), geladen ([[Modell+0x2C]+8] Bit 0) und mit Radius > 0; sonst wie bisher c4 + KZ * c5. Rand also nur,
# wo etwas vor der ganzen Einheit liegt (hinter Wand, Huegel, Laterne); was die Kugel schneidet (Boden unter den
# Fuessen, Wand, in der sie steht), zaehlt nicht. Kamera in der Kugel: kein Rand (ZC 0).
import sys, os, struct, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psasm
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/gen')
from asmgen import *
PX = 2.0   # Randbreite in Pixeln (Linie)
# Kopien: diagonal 1 Pixel (ganzzahlig: der Rand ist an jeder geraden Kante unabhaengig von der Lage genau 1 Pixel bzw.
# 1.41 Pixel bei 45 Grad breit) und 4 innere um einen halben Pixel (zusaetzliche Abtastphasen fuer duenne Stellen, ohne
# Einfluss auf gerade Kanten); die 2 Pixel breite Linie macht LPS daraus
OFFS = [(1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0), (0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5)]
# ohne Schein (GLFAIL = Geraet): wie bisher 2 Pixel weit, die Vierecke zeichnen dann direkt die Linie
OFFS2 = [(PX, 0), (-PX, 0), (0, PX), (0, -PX), (PX, PX), (PX, -PX), (-PX, PX), (-PX, -PX)]
# Datenlayout (Sektions-Offsets)
MAXU = 48          # umrandete Einheiten pro Bild (Kategorie = Index + 1)
UE = 24            # Eintrag: GUID lo, GUID hi, Modell, Reittier-Modell, Farbe, Pulsfarbe (0 = keine)
PULSE_MS = 1500    # Dauer eines Pulses (Klassenfarbe -> rot -> Klassenfarbe) in ms
KAPPA = 0.001      # "nur wo verdeckt": Abstand in Yards = KAPPA * Entfernung^2 (15 yd -> 0,23 yd)
SPHK = 0.1         # mit Huellquader: Kopien auf der Quader-Vorderseite, zusaetzlich SPHK * KZ nach vorn (0 = nur der Quader)
SPHM = 0.05        # Zuschlag vor der Quader-Vorderseite in Yards (Animation ragt etwas ueber den Quader im M2-Kopf)
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
M2_SHARED, M2_HDR, M2_BOX, M2_RAD, M2_MV, M2_SCENE, M2_STAMP, SC_FRAME = 0x2C, 0x150, 0xA0, 0xB8, 0xF4, 0x28, 0x3C, 0x14
HOSTILE = 0xFFFF0000   # Farbe des Auswahlkreises fuer feindlich (0xBD0C94/0xBD0C98)
DO = dict(VP=0x00, CUR=0x18, VALID=0x1C, MARKED=0x20, SMODE=0x24, PS=0x28, PSDEV=0x2C,
          FX=0x30, FY=0x34, SX=0x38, SY=0x3C, TWO=0x40, MTWO=0x44, HALF=0x48, MODE=0x4C,
          MAT=0x50, VERTS=0x90, OFFS=0xE0, PSCODE=0x120, PGUID=0x138, NUNITS=0x140, SELFCAT=0x144,
          KAP=0x148, KZ=0x14C, CLS=0x150, K128=0x180, PW=0x184, T8=0x188, TMP=0x18C, UNITS=0x190,
          GRPN=0x610, GMODE=0x614, WPROT=0x618, NMARK=0x61C, MLIST=0x620, MCOUNT=0x624,
          THIN=0x628, LPS=0x668, LCPS=0x66C, TL=0x670, OFP=0x674, RTDEV=0x684, RTW=0x688, RTH=0x68C, RTMS=0x690, RTMQ=0x694, RTW2=0x698, RTH2=0x69C,
          BBP=0x6A0, DSP=0x6A4, GPS=0x6A8, CPS=0x6AC, GPSDEV=0x6B0, GLFAIL=0x6B4, GLOK=0x6B8, O1=0x6BC, O2=0x6C0,
          QX0=0x6C4, QY0=0x6C8, QX1=0x6CC, QY1=0x6D0, QU0=0x6D4, QV0=0x6D8, QU1=0x6DC, QV1=0x6E0, QDU=0x6E4, QDV=0x6E8,
          DESC=0x6EC, VERTT=0x70C, GPSCODE=0x7EC, CPSCODE=0x908, TTSAV=0x970, PETF=0x990,
          TPS=0x9D0, VPS=0x9D4, TQ=0x9D8, TPSCODE=0x9E0, VPSCODE=0xAE0,
          GLRES=0xC50, OFFS2=0xC80, LPSCODE=0xCC0, LCPSCODE=0xDE0,
          ZA=0xE70, ZC=0xE74, CURM=0xE78, ZR=0xE7C, ZT=0xE80, ZT2=0xE84, ZW=0xE88, ZZ=0xE8C, SC=0xE90, SV=0xE9C, SPK=0xEA8, SPM=0xEAC,
          RAYREQ=0xEB0, RCUR=0xEF0, RCNT=0xEF4, RBUD=0xEF8, RAYSEQ=0xEFC, RAYLAST=0xF00, RAYOK=0xF04, CAMP=0xF08, RPOS=0xF14,
          REND=0xF20, RFRAC=0xF2C, RL=0xF30, RH=0xF34, RK=0xF38, RI=0xF3C, RNH=0xF40, ZMOD=0xF44, ZH=0xF48, HV=0xF4C, HD=0xF58,
          RTMP=0xF64, RAYS=0xF68, RAYD=0xF6C, KFR=0xF70, KFRM=0xF7C, LMIN=0xF88, LMAX=0xF8C, HDEF=0xF90, ONE=0xF94, RLM=0xF98, RLIM=0xF9C, RT=0xFA0)
CODE_OFF = 0x18A0
SIZES = dict(VP=24, CUR=4, VALID=4, MARKED=4, SMODE=4, PS=4, PSDEV=4, FX=4, FY=4, SX=4, SY=4, TWO=4, MTWO=4, HALF=4, MODE=4,
             MAT=64, VERTS=80, OFFS=64, PSCODE=20, PGUID=8, NUNITS=4, SELFCAT=4, KAP=4, KZ=4, CLS=48,
             K128=4, PW=4, T8=4, TMP=4, UNITS=MAXU * UE, GRPN=4, GMODE=4, WPROT=4, NMARK=4, MLIST=4, MCOUNT=4,
             THIN=64, LPS=4, LCPS=4, TL=4, OFP=4, GLRES=36, OFFS2=64, LPSCODE=284, LCPSCODE=144, RTDEV=4, RTW=4, RTH=4, RTMS=4, RTMQ=4, RTW2=4, RTH2=4, BBP=4, DSP=4, GPS=4, CPS=4,
             GPSDEV=4, GLFAIL=4, GLOK=4, O1=4, O2=4, QX0=4, QY0=4, QX1=4, QY1=4, QU0=4, QV0=4, QU1=4, QV1=4, QDU=4, QDV=4,
             DESC=32, VERTT=224, GPSCODE=284, CPSCODE=100, TTSAV=20, PETF=64,
             TPS=4, VPS=4, TQ=4, TPSCODE=256, VPSCODE=360,
             ZA=4, ZC=4, CURM=4, ZR=4, ZT=4, ZT2=4, ZW=4, ZZ=4, SC=12, SV=12, SPK=4, SPM=4,
             RAYREQ=64, RCUR=4, RCNT=4, RBUD=4, RAYSEQ=4, RAYLAST=4, RAYOK=4, CAMP=12, RPOS=12, REND=12, RFRAC=4, RL=4, RH=4,
             RK=4, RI=4, RNH=4, ZMOD=4, ZH=4, HV=12, HD=12, RTMP=4, RAYS=4, RAYD=4, KFR=12, KFRM=12, LMIN=4, LMAX=4, HDEF=4,
             ONE=4, RLM=4, RLIM=4, RT=MAXU * RTE)
# Schein: Verkleinern mit 4x4-Zelt (Abgriffe bei +-TENT Texeln diagonal), Gauss mit 5 bilinearen Abgriffen (9 Texel),
# im senkrechten Durchgang die Kurve 1-(1-y)^2 mit y = sat(GLOW_K * x); Einblenden mit GLOW_GAIN = 1
BLUR_W = (0.2270270, 0.3162162, 0.0702703)
BLUR_O = (1.3846154, 3.2307692)
TENT = 0.75
GLOW_K = 2.0      # Quelle ist jetzt die 2 Pixel breite Linie aus TEX3 (auch 1 Pixel unter der Figur): 2.0 statt 2.5
GLOW_GAIN = 1.0
LINE_K = 4.0      # Linie: a = sat(LINE_K * 3x3-Zelt(TEX0)), 4 = an geraden Kanten genau 2 Pixel
LINE_T = 0.5      # Abgriffe der Linie bei +-0.5 Texeln (ueber mkq: TL = LINE_T / O1)
GLRES_NAMES = ['MSRT', 'TEX0', 'TEX0S', 'TEX1', 'TEX1S', 'TEX2', 'TEX2S', 'TEX3', 'TEX3S']   # Reihenfolge in GLRES
# Eintraege von WoWs Zustands-Cache [Geraet+0x3BC4+4*i], die Post und Schein aendern: SRCBLEND, DESTBLEND,
# Sampler 0 (MAG, MIN, MIP, ADDRESSU, ADDRESSV), TEXCOORDINDEX 0-4, ALPHABLEND, ALPHATEST, FOG, ZWRITE,
# COLORWRITE, CULL, ZFUNC. Nur diese werden ungueltig (0xFFFFFFFF) - fuer D3DRS_AMBIENT (0xA6) ist
# 0xFFFFFFFF ein echter Wert. TEXTURETRANSFORMFLAGS 0-4 (0x52-0x56) setzt der Schein selbst zurueck.
HWCACHE_DIRTY = (0x00, 0x01, 0x02, 0x12, 0x22, 0x32, 0x42, 0x6A, 0x6B, 0x6C, 0x6D, 0x6E, 0xA7, 0xA8, 0xAA, 0xAB, 0xAC, 0xAF, 0xB1)
FIG = 0xC0         # Stencil-Wert der Figur (0x80 Figur | 0x40 sichtbar); Rand = 0x40 | Kategorie (1..MAXU)
UBIT = 0x40        # "sichtbar": spaeter davor Gezeichnetes loescht es (mit dem Figur-Bit), Kategorie-Bits bleiben
assert MAXU < UBIT # Kategorien passen in die Bits 0..5
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
         QSORT=0x83DCF0, CMPOPA=0x81EEA0, CMPBATCH=0x81EAD0, DRAWLIST=0x823130, RESETFN=0x690150,
         OBJMGR=0x4D3730, CULLCB=0x4F9F70, CULLCONT=0x7934CB, CULLNEXT=0x79358F, FRUST=0xCD8798, FRUSTB=0xCDB168,
         SPHERE=0x983D20, M2UPD=0x823F10, LIGHTCB=0x780CD0, VISLIST=0xCDB098, LISTADD=0x6DED60,
         ORIGRF=0x7E6480, TRACE=0x7A3B70, INWORLD=0xBD0792, LOADING=0xBD0790, WFRAME=0xB7436C)
X.update(FLAGS)
X.update(PULSE=PULSE_MS, HOSTILE=HOSTILE, MAXPET=45, RAYB=RAYB, RAYFREE=RAYFREE, RAYFLAGS=RAYFLAGS,
         HLO=struct.unpack('<I', struct.pack('<f', RAYH[0]))[0], HHI=struct.unpack('<I', struct.pack('<f', RAYH[1]))[0])
# Aufrufe von 0x690150 (gibt vor IDirect3DDevice9::Reset bzw. beim Abbau die Geraete-Ressourcen frei):
# Formatwechsel 0x690230 (vtable 0xA2E718 + 0x58), verlorenes Geraet 0x6A3350, Abbau 0x6903B0 (Argument 1)
RESETSITES = (0x69029D, 0x6A337F, 0x69040B)
# Aussortierte Karten-Objekte (0x793450): bei 0x7934C6 (mov ecx,[ebx+0x34]; xor edx,edx) ist ebx das Objekt
CULLSITE = 0x7934C6
MAXPET = 45       # Begleiter nur bis hier - Platz fuer ich, Ziel, Mouseover

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
  mov ebx,8
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
  mov ebx,{TPS}
  call gr_rel
  mov ebx,{VPS}
  call gr_rel
  mov ebx,{LPS}
  call gr_rel
  mov ebx,{LCPS}
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
  mov dword ptr [{TPS}],0
  mov dword ptr [{VPS}],0
  mov dword ptr [{LPS}],0
  mov dword ptr [{LCPS}],0
''' + DEV(0x1A8, '{GPSCODE}', '{GPS}') + DEV(0x1A8, '{CPSCODE}', '{CPS}') + DEV(0x1A8, '{TPSCODE}', '{TPS}') + DEV(0x1A8, '{VPSCODE}', '{VPS}') + \
    DEV(0x1A8, '{LPSCODE}', '{LPS}') + DEV(0x1A8, '{LCPSCODE}', '{LCPS}') + '''
g_sh:
  cmp dword ptr [{GPS}],0
  je g_fail
  cmp dword ptr [{CPS}],0
  je g_fail
  cmp dword ptr [{TPS}],0
  je g_fail
  cmp dword ptr [{VPS}],0
  je g_fail
  cmp dword ptr [{LPS}],0
  je g_fail
  cmp dword ptr [{LCPS}],0
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
  cmp dword ptr [{TEX3S}],0
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
''' + DEV(0x5C, 'dword ptr [{RTW}]', 'dword ptr [{RTH}]', 1, 1, 21, 0, '{TEX3}', 0) + '''
  test eax,eax
  jl g_nfail
''' + OBJ('dword ptr [{TEX3}]', 0x48, 0, '{TEX3S}') + '''
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
''' + DEV(0x9C, 0) + SRS(7, 0) + SRS(52, 0) + DEV(0x1AC, 'dword ptr [{LPS}]') + DEV(0x164, 0x504) + \
    SSS(5, 2) + SSS(6, 2) + SSS(7, 0) + SSS(1, 3) + SSS(2, 3) + \
    ''.join(TSS(i, 11, i) + TSS(i, 24, 0) for i in range(5)) + '''
  fild dword ptr [{RTW}]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QX1}]
  fild dword ptr [{RTH}]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QY1}]
  mov dword ptr [{QX0}],0xBF000000
  mov dword ptr [{QY0}],0xBF000000
  mov dword ptr [{QU0}],0
  mov dword ptr [{QV0}],0
  mov dword ptr [{QU1}],0x3F800000
  mov dword ptr [{QV1}],0x3F800000
  fld dword ptr [{TL}]
  fidiv dword ptr [{RTW}]
  fstp dword ptr [{QDU}]
  fld dword ptr [{TL}]
  fidiv dword ptr [{RTH}]
  fstp dword ptr [{QDV}]
  mov ebx,dword ptr [{TEX0}]
  mov edi,dword ptr [{TEX3S}]
  call g_pass
''' + DEV(0x1AC, 'dword ptr [{TPS}]') + '''
  fild dword ptr [{RTW2}]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QX1}]
  fild dword ptr [{RTH2}]
  fsub dword ptr [{HALF}]
  fstp dword ptr [{QY1}]
  fld dword ptr [{TQ}]
  fidiv dword ptr [{RTW}]
  fstp dword ptr [{QDU}]
  fld dword ptr [{TQ}]
  fidiv dword ptr [{RTH}]
  fstp dword ptr [{QDV}]
  mov ebx,dword ptr [{TEX3}]
  mov edi,dword ptr [{TEX1S}]
  call g_pass
''' + DEV(0x1AC, 'dword ptr [{GPS}]') + '''
  mov dword ptr [{QDV}],0
  fld1
  fidiv dword ptr [{RTW2}]
  fstp dword ptr [{QDU}]
  mov ebx,dword ptr [{TEX1}]
  mov edi,dword ptr [{TEX2S}]
  call g_pass
''' + DEV(0x1AC, 'dword ptr [{VPS}]') + '''
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
''' + SRS(56, 5) + SRS(57, 0x80) + SRS(58, 0xFF) + SRS(27, 1) + SRS(19, 2) + SRS(20, 6) + SRS(168, 7) + DEV(0x1AC, 'dword ptr [{CPS}]') + DEV(0x104, 0, 'dword ptr [{TEX1}]') + '''
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
''' + DPUPT + DEV(0x1AC, 'dword ptr [{LCPS}]') + DEV(0x104, 0, 'dword ptr [{TEX3}]') + DPUPT + '''
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

# Quader-Vorderseite (agent_feet, Abstand verkleinert): zfront setzt ZC = kleinste NDC-Tiefe z/w der Vorderseite
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
# nie genommen). Der Radius im M2-Kopf (+0xB8) dient nur als Pruefung des Kopfes (endlich und > 0). ebx, esi, edi bleiben.
ZSPH = """zfront:
  mov dword ptr [{ZC}],0x7F800000
  mov dword ptr [{ZMOD}],0
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
  cmp dword ptr [edx+0x%(RAD)X],0x7F800000
  jge zs_r
  test edi,edi
  jnz zs_nm
  cmp dword ptr [{ZMOD}],0
  jne zs_nm
  mov dword ptr [{ZMOD}],ecx
zs_nm:
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
# blockiert (sofort), sonst nach RAYFREE freien Pruefungen frei; bis dahin fallen gemerkte Punkte weg, die weiter als
# max(L) - RAYS + RAYD von der Kamera liegen (Figur ist vor die Mauer getreten). Objekt weg: frei.
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
  mov eax,{KFR}
  cmp dword ptr [ebx+0x98C],0
  je ru_k
  mov eax,{KFRM}
ru_k:
  mov dword ptr [{RK}],eax
  mov dword ptr [{RNH}],0
  mov dword ptr [{RI}],0
  mov dword ptr [{RLM}],0
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
  cmp eax,dword ptr [{RLM}]
  jle ru_lm
  mov dword ptr [{RLM}],eax
ru_lm:
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
  fld dword ptr [{RLM}]
  fsub dword ptr [{RAYS}]
  fadd dword ptr [{RAYD}]
  fstp dword ptr [{RLIM}]
  movzx ecx,byte ptr [edi+10]
  xor edx,edx
  xor esi,esi
ru_fl:
  cmp esi,ecx
  jae ru_fd
  lea eax,[esi+esi*2]
  lea eax,[edi+12+eax*4]
  fld dword ptr [eax]
  fsub dword ptr [{CAMP}]
  fmul st(0),st(0)
  fld dword ptr [eax+4]
  fsub dword ptr [{CAMP}+4]
  fmul st(0),st(0)
  faddp st(1),st(0)
  fld dword ptr [eax+8]
  fsub dword ptr [{CAMP}+8]
  fmul st(0),st(0)
  faddp st(1),st(0)
  fsqrt
  fstp dword ptr [{RTMP}]
  mov ebx,dword ptr [{RTMP}]
  cmp ebx,dword ptr [{RLIM}]
  jg ru_fx
  lea ebx,[edx+edx*2]
  lea ebx,[edi+12+ebx*4]
  push dword ptr [eax]
  pop dword ptr [ebx]
  push dword ptr [eax+4]
  pop dword ptr [ebx+4]
  push dword ptr [eax+8]
  pop dword ptr [ebx+8]
  inc edx
ru_fx:
  inc esi
  jmp ru_fl
ru_fd:
  mov byte ptr [edi+10],dl
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
  mov dword ptr [{CURM}],eax
  call classify
  test eax,eax
  jz b_set
  cmp byte ptr [{PETF}+eax],2
  jne b_set
  xor eax,eax
b_set:
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
  mov ebx,1
  call addpets
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
  cmp dword ptr [{GMODE}],2
  je e_pet2
  cmp dword ptr [{SELFCAT}],0
  je e_nopet
  cmp byte ptr [{FHIDDEN}],1
  jne e_nopet
e_pet2:
  mov ebx,2
  call addpets
e_nopet:
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
  mov byte ptr [{PETF}+eax],0
  pop ebx
  pop edi
  ret
au_none:
  pop ebx
  pop edi
au_zero:
  xor eax,eax
  ret
addpets:
  push esi
  push edi
  push ebp
  push ebx
  mov ebp,dword ptr [{NUNITS}]
  call {OBJMGR}
  test eax,eax
  jz ap_r
  push eax
  mov edi,[eax+0xAC]
ap_l:
  test edi,edi
  jz ap_x
  test edi,1
  jnz ap_x
  cmp dword ptr [{NUNITS}],{MAXPET}
  jae ap_x
  mov esi,[edi+8]
  mov eax,[esi+8]
  and eax,0x18
  cmp eax,8
  jne ap_n
  mov ecx,0x30
ap_o:
  lea edx,[esi+ecx]
  call ap_own
  test eax,eax
  jnz ap_hit
  add ecx,8
  cmp ecx,0x48
  jb ap_o
  jmp ap_n
ap_hit:
  push eax
  call same_tm
  je ap_skip
  call add_unit
  test eax,eax
  jz ap_skip
  pop ecx
  cmp ebx,1
  jne ap_m2
  mov byte ptr [{PETF}+eax],1
  lea ecx,[ecx+ecx*2]
  mov edx,dword ptr [{UNITS}-8+ecx*8]
  lea ecx,[eax+eax*2]
  mov dword ptr [{UNITS}-8+ecx*8],edx
  mov dword ptr [{UNITS}-4+ecx*8],0
  jmp ap_n
ap_m2:
  mov byte ptr [{PETF}+eax],2
  mov byte ptr [{THIN}+eax],1
  jmp ap_n
ap_skip:
  pop eax
ap_n:
  mov eax,[esp]
  mov eax,[eax+0xA4]
  mov edi,[edi+eax+4]
  jmp ap_l
ap_x:
  pop eax
ap_r:
  pop ebx
  pop ebp
  pop edi
  pop esi
  ret
ap_own:
  mov eax,[edx]
  or eax,[edx+4]
  jz ao_none
  push ecx
  push esi
  cmp ebx,1
  jne ao_m2
  mov ecx,ebp
ao_l:
  test ecx,ecx
  jz ao_nf
  lea esi,[ecx+ecx*2]
  lea esi,[{UNITS}-24+esi*8]
  call ao_eq
  je ao_f
  dec ecx
  jmp ao_l
ao_m2:
  mov esi,{PGUID}
  call ao_eq
  je ao_y
  mov esi,{PARTY}
  mov ecx,4
ao_p:
  call ao_eq
  je ao_y
  add esi,8
  dec ecx
  jnz ao_p
  mov ecx,dword ptr [{RAIDCNT}]
  cmp ecx,40
  jbe ao_rl
  mov ecx,40
ao_rl:
  test ecx,ecx
  jz ao_nf
  dec ecx
  mov esi,dword ptr [{RAIDARR}+ecx*4]
  test esi,esi
  jz ao_rl
  call ao_eq
  jne ao_rl
ao_y:
  mov ecx,1
ao_f:
  mov eax,ecx
  pop esi
  pop ecx
  ret
ao_nf:
  pop esi
  pop ecx
ao_none:
  xor eax,eax
  ret
ao_eq:
  mov eax,[esi]
  cmp eax,[edx]
  jne ao_e
  mov eax,[esi+4]
  cmp eax,[edx+4]
ao_e:
  ret
cull:
  cmp dword ptr [ebx+0x90],{CULLCB}
  jne cu_orig
  test byte ptr [ebx+0x7C],4
  jnz cu_orig
  cmp dword ptr [ebx+0x34],0
  je cu_orig
  call ensure
  mov ecx,dword ptr [{NUNITS}]
  cmp byte ptr [{FWALLS}],1
  je cu_cnt
  mov ecx,dword ptr [{GRPN}]
  cmp dword ptr [{GMODE}],0
  je cu_orig
cu_cnt:
  test ecx,ecx
  jz cu_orig
cu_l:
  lea edx,[ecx+ecx*2]
  lea edx,[{UNITS}-24+edx*8]
  mov eax,[edx]
  cmp eax,[ebx+0x98]
  jne cu_n
  mov eax,[edx+4]
  cmp eax,[ebx+0x9C]
  jne cu_n
  cmp byte ptr [{PETF}+ecx],2
  jne cu_hit
cu_n:
  dec ecx
  jnz cu_l
cu_orig:
  mov ecx,[ebx+0x34]
  xor edx,edx
  jmp {CULLCONT}
cu_hit:
  mov ecx,dword ptr [{FRUST}]
  imul ecx,ecx,0xFC
  add ecx,{FRUSTB}
  lea eax,[ebx+0x38]
  push eax
  call {SPHERE}
  test eax,eax
  jz cu_orig
  mov ecx,[ebx+0x34]
  push 1
  call {M2UPD}
  mov ecx,[ebx+0x34]
  mov eax,0x10008
  cmp dword ptr [ecx+0x48],0
  je cu_f
  mov eax,0x20080
cu_f:
  or dword ptr [ecx+0x10],eax
  mov dword ptr [ecx+0x2AC],{LIGHTCB}
  mov dword ptr [ecx+0x2B0],ebx
  push dword ptr [ebx+0xA0]
  push dword ptr [ebx+0x9C]
  push dword ptr [ebx+0x98]
  push 5
  push dword ptr [ebx+0x94]
  call dword ptr [ebx+0x90]
  add esp,0x14
  test eax,eax
  jz cu_done
  push ebx
  mov ecx,{VISLIST}
  call {LISTADD}
cu_done:
  jmp {CULLNEXT}
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
  mov eax,[esp+4]
  mov eax,[eax]
  jmp dword ptr [eax+0x148]
dp:
  cmp dword ptr [{CUR}],0
  jne dp_cur
  call smode
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
smode:
  cmp dword ptr [{MARKED}],0
  je sm_r
  cmp byte ptr [{FWALLS}],1
  je sm_r
  push esi
  mov esi,[esp+0xC]
  mov ecx,dword ptr [{DEVPTR}]
  xor eax,eax
  cmp dword ptr [ecx+0x3E70],0
  setne al
  cmp eax,dword ptr [{SMODE}]
  je sm_done
  mov dword ptr [{SMODE}],eax
  test eax,eax
  jz sm_off
''' + SRS(52, 1) + SRS(56, 8) + SRS(55, 2) + SRS(53, 1) + SRS(54, 1) + SRS(59, 0xC0) + '''
  jmp sm_done
sm_off:
''' + SRS(52, 0) + '''
sm_done:
  pop esi
sm_r:
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
  or eax,0xC0
''' + SRS(57, 'eax') + SRS(58, 0x7F) + SRS(23, 8) + '''
  call do_dip
''' + SRS(23, 'ebx') + SRS(58, 0xFF) + SRS(56, 5) + '''
  mov eax,dword ptr [{CUR}]
  or eax,0x40
''' + SRS(57, 'eax') + SRS(168, 0) + SRS(14, 1) + '''
  jmp d_copies
d_cw:
''' + SRS(56, 5) + SRS(54, 1) + '''
  mov eax,dword ptr [{CUR}]
  or eax,0x40
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
  mov dword ptr [{ZA}],0x3F800000
  cmp dword ptr [{MODE}],2
  jne d_kz
  mov eax,dword ptr [{CUR}]
  mov byte ptr [{RAYREQ}+eax],1
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
  call zfront
  cmp dword ptr [{ZC}],0x7F800000
  je d_kz
  fld dword ptr [{KZ}]
  fmul dword ptr [{SPK}]
  fadd dword ptr [{ZC}]
  fstp dword ptr [{KZ}]
  mov dword ptr [{ZA}],0
  call zhit
d_kz:
  mov eax,{OFFS}
  cmp dword ptr [{GLFAIL}],esi
  jne d_of
  mov eax,{OFFS2}
d_of:
  mov dword ptr [{OFP}],eax
  xor edi,edi
d_loop:
  mov eax,dword ptr [{OFP}]
  fld dword ptr [eax+edi*8]
  fmul dword ptr [{SX}]
  fstp dword ptr [{FX}]
  fld dword ptr [eax+edi*8+4]
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
''' % (4 * k, 4 * k, 4 * k, 4 * k, 4 * k, 16 + 4 * k) for k in range(4)) + ''.join('''  fld dword ptr [{C4}+%d]
  fmul dword ptr [{ZA}]
  fld dword ptr [{C5}+%d]
  fmul dword ptr [{KZ}]
  faddp st(1),st(0)
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
''' + ZSPH + RAYCODE + '''post:
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
  cmp byte ptr [{PETF}+ebx],2
  je p_nx
  cmp dword ptr [{GLOK}],0
  je p_q
  cmp byte ptr [{THIN}+ebx],0
  je p_nx
p_q:
  call ucol
  call quad
p_nx:
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
''' + SRS(59, 0xFF) + '''  push 0
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
  lea eax,[ebx+0x40]
''' + SRS(57, 'eax') + '''
  mov eax,0xFF
  cmp ebx,dword ptr [{WPROT}]
  ja q_m
  mov eax,0x3F
q_m:
''' + SRS(58, 'eax') + '''
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
  mov edx,0x10
  cmp byte ptr [{PETF}+eax],0
  je sp_k
  mov edx,0x11
sp_k:
  mov dword ptr [ecx],edx
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
  jb sp_r
  cmp dword ptr [eax],0x11
  ja sp_r
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
  mov ecx,[edi]
  cmp ecx,0x10
  jb cw_orig
  cmp ecx,[eax]
  jne cw_orig
  push ecx
  mov dword ptr [edi],0
  mov dword ptr [eax],0
  push eax
  push eax
  push edi
  call {CMPBATCH}
  add esp,8
  pop ecx
  pop edx
  mov dword ptr [edi],edx
  mov dword ptr [ecx],edx
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
    for i, (x, y) in enumerate(OFFS2): struct.pack_into('<ff', d, DO['OFFS2'] + i * 8, x, y)
    struct.pack_into('<f', d, DO['TWO'], 2.0); struct.pack_into('<f', d, DO['MTWO'], -2.0); struct.pack_into('<f', d, DO['HALF'], 0.5)
    struct.pack_into('<5I', d, DO['PSCODE'], 0xFFFF0101, 0x00000001, 0x800F0000, 0x90E40000, 0x0000FFFF)
    for k, v in CLASSCOL.items(): struct.pack_into('<I', d, DO['CLS'] + 4 * k, v)
    struct.pack_into('<ff', d, DO['K128'], 128.0, 2 * math.pi / PULSE_MS)
    struct.pack_into('<f', d, DO['KAP'], KAPPA)
    struct.pack_into('<f', d, DO['SPK'], SPHK)
    struct.pack_into('<f', d, DO['SPM'], SPHM)
    struct.pack_into('<12f', d, DO['RAYS'], RAYS, RAYD, *KFR, *KFRM, RAYLMIN, RAYLMAX, RAYH[2], 1.0)
    struct.pack_into('<ff', d, DO['O1'], *BLUR_O)
    for k in range(4): struct.pack_into('<ff', d, DO['VERTT'] + 56 * k + 8, 0.0, 1.0)
    g = psasm.blur_ps(*BLUR_W); c = psasm.comp_ps(GLOW_GAIN)
    assert len(g) == SIZES['GPSCODE'] and len(c) == SIZES['CPSCODE']
    d[DO['GPSCODE']:DO['GPSCODE'] + len(g)] = g; d[DO['CPSCODE']:DO['CPSCODE'] + len(c)] = c
    tp = psasm.tent_ps(); vp = psasm.blur_soft_ps(*BLUR_W, GLOW_K)
    assert len(tp) == SIZES['TPSCODE'] and len(vp) == SIZES['VPSCODE']
    d[DO['TPSCODE']:DO['TPSCODE'] + len(tp)] = tp; d[DO['VPSCODE']:DO['VPSCODE'] + len(vp)] = vp
    struct.pack_into('<f', d, DO['TQ'], TENT / BLUR_O[0])     # mkq: t1/t2 = (u,v) +- (TQ/RTW, TQ/RTH) * O1 = +-0.75 Texel
    lp = psasm.line_ps(LINE_K); lc = psasm.linecomp_ps()
    assert len(lp) == SIZES['LPSCODE'] and len(lc) == SIZES['LCPSCODE']
    d[DO['LPSCODE']:DO['LPSCODE'] + len(lp)] = lp; d[DO['LCPSCODE']:DO['LCPSCODE'] + len(lc)] = lc
    struct.pack_into('<f', d, DO['TL'], LINE_T / BLUR_O[0])   # mkq: t1/t2 = (u,v) +- (TL/RTW, TL/RTH) * O1 = +-0.5 Texel
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
def one_fix_per_insn():
    # emitps.emit (Add-Outline) setzt je Befehl nur EINE Adresse um - kein Befehl darf zwei haben (z.B. mov [abs],abs)
    from asmgen import md
    fx = sorted(absf + relf)
    for i in md.disasm(code, B1 + CODE_OFF):
        a = i.address - B1; n = sum(1 for f in fx if a <= f < a + i.size)
        assert n <= 1, 'zwei Umsetzungen in einem Befehl bei 0x%X: %s %s' % (a, i.mnemonic, i.op_str)
one_fix_per_insn()
TPL = bytes(data()) + code
LAB = {k: CODE_OFF + v for k, v in label_offsets(src(B1), B1 + CODE_OFF,
       ['vpcap', 'batch', 'dip', 'dp', 'smode', 'post', 'addpets', 'cull', 'okdev', 'ensure', 'add_unit', 'classify', 'quad', 'blend', 'same_tgt', 'same_tm', 'same_tms', 'sortp', 'item', 'cmpw', 'sp_cw', 'draw1', 'draw2',
        'ucol', 'glfree', 'glrel', 'mkq', 'g_pass', 'glow', 'zfront', 'zsph', 'raystub', 'rayframe', 'rayunit', 'zhit']).items()}
if __name__ == '__main__':
    print('size', hex(len(TPL)), 'code', hex(len(code)), 'abs', len(absf), 'rel', len(relf), {k: hex(v) for k, v in LAB.items()})

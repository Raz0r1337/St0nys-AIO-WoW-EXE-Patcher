# Outline (Nr. 68) mit Optionen: Ziel, Mouseover, eigener Charakter, 5er-Gruppe, Schlachtzug,
# eigener Charakter nur wo verdeckt, durch Waende, Klassen- bzw. Gesinnungsfarbe; feindliche
# Spieler in Klassenfarbe pulsieren sanft rot (WoW 3.3.5a 12340). Weiterentwicklung von outline4.py:
# "nur wo verdeckt" - Kopien mit STENCILZFAIL KEEP und Tiefen-Abstand (KZ aus der Projektion).
import sys, os, struct, math
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
          KAP=0x148, KZ=0x14C, CLS=0x150, K128=0x180, PW=0x184, T8=0x188, TMP=0x18C, UNITS=0x190)
CODE_OFF = DO['UNITS'] + MAXU * UE
SIZES = dict(VP=24, CUR=4, VALID=4, MARKED=4, SMODE=4, PS=4, PSDEV=4, FX=4, FY=4, SX=4, SY=4, TWO=4, MTWO=4, HALF=4, MODE=4,
             MAT=64, VERTS=80, OFFS=64, PSCODE=20, PGUID=8, NUNITS=4, SELFCAT=4, KAP=4, KZ=4, CLS=48,
             K128=4, PW=4, T8=4, TMP=4, UNITS=MAXU * UE)
FIG = 0x80         # Stencil-Wert der Figur; Rand = Kategorie (1..MAXU)
# Klassenfarben (RAID_CLASS_COLORS aus FrameXML 3.3.5), D3DCOLOR 0xAARRGGBB, Index = Klassen-Id
CLASSCOL = {1: 0xFFC79C6E, 2: 0xFFF58CBA, 3: 0xFFABD473, 4: 0xFFFFF569, 5: 0xFFFFFFFF, 6: 0xFFC41F3B,
            7: 0xFF0070DE, 8: 0xFF69CCF0, 9: 0xFF9482C9, 11: 0xFFFF7D0A}
# Schalter der Optionen: je ein CC-Fuellbyte nach einem ret in .text, 1 = an (gesetzt ueber die J/N-Fragen)
FLAGS = dict(FWALLS=0x6AB7DF, FSELF=0x6ABAAF, FPARTY=0x6ABE2F, FRAID=0x6ABE8F, FHIDDEN=0x6ABF3F, FREACT=0x6ABE5F)
# externe Adressen
X = dict(DEVPTR=0xC5DF88, VT9=0xA2E718, WSCENE=0xCD754C, DRAWBATCH=0x8203B0, AFTERB=0x823AD3, VPRET=0x6A9B16,
         CIRCLES=0x4F6F90, OBJPTR=0x4D4DB0, FILESTR=0xA22CD4, SELCOL=0x521BF0, TGT=0xBD07B0, TGT4=0xBD07B4,
         MOV=0xBD07A0, MOV4=0xBD07A4, GETTICK=0x9DF174, SHADERS=0xD43020, C2=0xC5F008, C3=0xC5F018, C4=0xC5F028, C5=0xC5F038,
         MARKDIRTY=0x685970, FORCEUPD=0x685A70, PLAYERGUID=0x4D3790, PARTY=0xBD1948, RAIDARR=0xBEB568, RAIDCNT=0xBEB608)
X.update(FLAGS)
X.update(PULSE=PULSE_MS, HOSTILE=HOSTILE)

def SRS(state, val):
    v = val if isinstance(val, str) else '0x%X' % val
    return '''  push %s
  push %d
  push esi
  mov eax,[esi]
  call dword ptr [eax+0xE4]
''' % (v, state)

def src(base, sym=False):
    base = base or 0
    A = {k: ('0x%X' % (base + v) if not sym else k) for k, v in DO.items()}
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
  jne e_party
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
  pop ebx
  pop edi
  ret
au_none:
  pop ebx
  pop edi
au_zero:
  xor eax,eax
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
  cmp dword ptr [{MARKED}],0
  je d_fast
  cmp byte ptr [{FWALLS}],1
  je d_fast
  push esi
  mov esi,[esp+8]
  mov ecx,dword ptr [{DEVPTR}]
  xor eax,eax
  cmp dword ptr [ecx+0x3E70],0
  setne al
  cmp eax,dword ptr [{SMODE}]
  je d_cl_done
  mov dword ptr [{SMODE}],eax
  test eax,eax
  jz d_cl_off
''' + SRS(52, 1) + SRS(56, 8) + SRS(57, 0) + SRS(55, 3) + SRS(53, 1) + SRS(54, 1) + SRS(58, 0xFF) + SRS(59, 0xFF) + '''
  jmp d_cl_done
d_cl_off:
''' + SRS(52, 0) + '''
d_cl_done:
  pop esi
d_fast:
  mov eax,[esp+4]
  mov eax,[eax]
  jmp dword ptr [eax+0x148]
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
  cmp byte ptr [{FHIDDEN}],1
  jne d_m1
  mov eax,dword ptr [{CUR}]
  cmp eax,dword ptr [{SELFCAT}]
  jne d_m1
  mov edi,2
  jmp d_m2
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
  mov ebx,dword ptr [{NUNITS}]
p_loop:
  test ebx,ebx
  jz p_done
  lea eax,[ebx+ebx*2]
  mov edx,dword ptr [{UNITS}-8+eax*8]
  mov ecx,dword ptr [{UNITS}-4+eax*8]
  test ecx,ecx
  jz p_q
  call blend
p_q:
  call quad
  dec ebx
  jmp p_loop
p_done:
  mov ecx,dword ptr [{DEVPTR}]
  call {FORCEUPD}
  mov edx,dword ptr [{DEVPTR}]
  lea edi,[edx+0x3BC4]
  mov ecx,0xB6
  mov eax,0xFFFFFFFF
  cld
  .byte 0xF3,0xAB
  mov dword ptr [edx+0x3B5C],0
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
'''
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
       ['vpcap', 'batch', 'dip', 'post', 'okdev', 'ensure', 'add_unit', 'classify', 'quad', 'blend', 'same_tgt', 'same_tm', 'same_tms']).items()}
if __name__ == '__main__':
    print('size', hex(len(TPL)), 'code', hex(len(code)), 'abs', len(absf), 'rel', len(relf), {k: hex(v) for k, v in LAB.items()})

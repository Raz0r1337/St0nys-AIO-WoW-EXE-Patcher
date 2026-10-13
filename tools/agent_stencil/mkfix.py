# Derives outline10_fix.py (this directory) from ol2/outline10.py with the proposed stencil fix ("U bit"):
#  - every mark carries bit 0x40: figure 0xC0, ring 0x40|cat, second pass 0xC0|cat
#  - later depth-writing geometry (SMODE): STENCILFUNC ALWAYS, PASS ZERO, FAIL/ZFAIL KEEP, write mask 0xC0
#    -> never discards a pixel; clears figure+U bits where the draw passes depth/alpha test
#  - post: ring quad REF 0x40|cat, MASK 0x3F for protected categories (<= WPROT), 0xFF otherwise;
#    glow composite sets MASK 0xFF; write mask 0xFF before the final stencil Clear
#  - the SMODE check moves into a subroutine smode, used by dip (VA 0x6A36C8) and the new dp (VA 0x6A3706)
# ol2/outline10.py is only read. usage: python3 -B mkfix.py
import os, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'ol2', 'outline10.py')
s = open(SRC).read()
orig = s
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)

rep('''# Outline (Nr. 68) mit Optionen''', '''# stencilfix (agent_stencil, Vorschlag): Stencil-Werte mit "U-Bit" 0x40 (sichtbar): Figur 0xC0, Rand 0x40 | Kategorie,
# zweiter Durchgang 0xC0 | Kategorie. Spaeter Gezeichnetes mit Tiefe (SMODE): STENCILFUNC ALWAYS, PASS ZERO,
# Schreibmaske 0xC0 - verwirft nie ein Pixel (vorher LESS gegen WPROT: alles auf Stencil <= WPROT fiel weg) und loescht
# dort, wo es vorne liegt, Figur- und U-Bit. Post: Rand-Viereck Ref 0x40 | Kategorie, Maske 0x3F fuer geschuetzte
# Gruppen-Raender (Kategorie <= WPROT, auch verdeckt), sonst 0xFF. Der DrawPrimitive-Zweig (VA 0x6A3706) laeuft
# durch dieselbe Pruefung (dp -> smode) wie DrawIndexedPrimitive (dip -> smode).
# Outline (Nr. 68) mit Optionen''')
rep('''sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psasm''', '''sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ol2'))   # psasm
import psasm''')
rep('''FIG = 0x80         # Stencil-Wert der Figur; Rand = Kategorie (1..MAXU)''',
    '''FIG = 0xC0         # Stencil-Wert der Figur (0x80 Figur | 0x40 sichtbar); Rand = 0x40 | Kategorie (1..MAXU)
UBIT = 0x40        # "sichtbar": spaeter davor Gezeichnetes loescht es (mit dem Figur-Bit), Kategorie-Bits bleiben
assert MAXU < UBIT # Kategorien passen in die Bits 0..5''')
# dip / dp / smode
rep('''dip:
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
\'\'\' + SRS(52, 1) + SRS(56, 2) + SRS(57, 'dword ptr [{WPROT}]') + SRS(55, 2) + SRS(53, 1) + SRS(54, 1) + SRS(58, 0xFF) + SRS(59, 0xFF) + \'\'\'
  jmp d_cl_done
d_cl_off:
\'\'\' + SRS(52, 0) + \'\'\'
d_cl_done:
  pop esi
d_fast:
  mov eax,[esp+4]
  mov eax,[eax]
  jmp dword ptr [eax+0x148]
d_mark:''', '''dip:
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
\'\'\' + SRS(52, 0) + \'\'\'
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
\'\'\' + SRS(52, 1) + SRS(56, 8) + SRS(55, 2) + SRS(53, 1) + SRS(54, 1) + SRS(59, 0xC0) + \'\'\'
  jmp sm_done
sm_off:
\'\'\' + SRS(52, 0) + \'\'\'
sm_done:
  pop esi
sm_r:
  ret
d_mark:''')
# d_mark: second pass ref CUR|0xC0, copies ref CUR|0x40
rep('''  mov eax,dword ptr [{CUR}]
  or eax,0x80
''', '''  mov eax,dword ptr [{CUR}]
  or eax,0xC0
''')
rep('''  mov eax,dword ptr [{CUR}]
\'\'\' + SRS(57, 'eax') + SRS(168, 0) + SRS(14, 1) + \'\'\'''', '''  mov eax,dword ptr [{CUR}]
  or eax,0x40
\'\'\' + SRS(57, 'eax') + SRS(168, 0) + SRS(14, 1) + \'\'\'''')
rep('''  mov eax,dword ptr [{CUR}]
\'\'\' + SRS(57, 'eax') + SRS(168, 0) + SRS(14, 0) + \'\'\'''', '''  mov eax,dword ptr [{CUR}]
  or eax,0x40
\'\'\' + SRS(57, 'eax') + SRS(168, 0) + SRS(14, 0) + \'\'\'''')
# quad: REF 0x40|cat, MASK 0x3F (protected) / 0xFF
rep('''  mov dword ptr [{VERTS}+76],edx
\'\'\' + SRS(57, 'ebx') + \'\'\'''', '''  mov dword ptr [{VERTS}+76],edx
  lea eax,[ebx+0x40]
\'\'\' + SRS(57, 'eax') + \'\'\'
  mov eax,0xFF
  cmp ebx,dword ptr [{WPROT}]
  ja q_m
  mov eax,0x3F
q_m:
\'\'\' + SRS(58, 'eax') + \'\'\'''')
# glow composite: GREATER 0x80 needs MASK 0xFF (the last ring quad may have left 0x3F)
rep('''SRS(56, 5) + SRS(57, 0x80) + SRS(27, 1)''', '''SRS(56, 5) + SRS(57, 0x80) + SRS(58, 0xFF) + SRS(27, 1)''')
# final stencil clear: write mask 0xFF first (SMODE leaves 0xC0; Wine's Clear ignores it, but be explicit)
rep('''p_clear:
  call okdev
  test eax,eax
  jz p_reset
  mov esi,eax
''', '''p_clear:
  call okdev
  test eax,eax
  jz p_reset
  mov esi,eax
\'\'\' + SRS(59, 0xFF) + \'\'\'''')
rep(''''vpcap', 'batch', 'dip', 'post',''', ''''vpcap', 'batch', 'dip', 'dp', 'smode', 'post',''')
open(os.path.join(HERE, 'outline10_fix.py'), 'w').write(s)
open(os.path.join(HERE, 'outline10_fix.diff'), 'w').writelines(difflib.unified_diff(orig.splitlines(True), s.splitlines(True), 'ol2/outline10.py', 'agent_stencil/outline10_fix.py'))
print('wrote outline10_fix.py and outline10_fix.diff')

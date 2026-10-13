# Alternative fix (two passes, no change to the stencil encoding): derives outline10_fix_r1.py from ol2/outline10.py.
#  - WPROT 0: later depth-writing draw with STENCILFUNC ALWAYS, PASS ZERO, FAIL/ZFAIL KEEP, write mask 0xFF (single pass,
#    state toggled like before)
#  - WPROT > 0: pass 1 = the draw exactly as unpatched (stencil off); pass 2 = same draw with COLORWRITE 0, ZWRITE 0,
#    ZFUNC EQUAL, STENCILFUNC LESS ref WPROT, PASS ZERO; then stencil off, ZFUNC from WoW's cache, ZWRITE/COLORWRITE
#    invalidated + marked dirty (WoW re-sends them before its next draw, as after d_mark)
#  - same for DrawPrimitive (VA 0x6A3706, routine dp)
# usage: python3 -B mkfix_r1.py
import os, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'ol2', 'outline10.py')
s = open(SRC).read(); orig = s
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep('''sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psasm''', '''sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ol2'))   # psasm
import psasm''')
DIRTY = '''  mov ecx,dword ptr [{DEVPTR}]
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
'''
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
\'\'\' + SRS(52, 0) + \'\'\'
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
\'\'\' + SRS(52, 1) + SRS(56, 8) + SRS(55, 2) + SRS(53, 1) + SRS(54, 1) + SRS(59, 0xFF) + \'\'\'
  jmp sm_done
sm_off:
\'\'\' + SRS(52, 0) + \'\'\'
sm_done:
  pop esi
sm_0:
  xor eax,eax
sm_r:
  ret
two_on:
\'\'\' + SRS(168, 0) + SRS(14, 0) + SRS(23, 3) + SRS(52, 1) + SRS(56, 2) + SRS(57, 'dword ptr [{WPROT}]') + SRS(55, 2) + SRS(53, 1) + SRS(54, 1) + SRS(58, 0xFF) + SRS(59, 0xFF) + \'\'\'
  ret
two_off:
\'\'\' + SRS(52, 0) + \'\'\'
  mov ecx,dword ptr [{DEVPTR}]
  mov eax,dword ptr [ecx+0x3E88]
  lea edx,[eax-1]
  cmp edx,7
  jbe t_zf
  mov eax,4
t_zf:
\'\'\' + SRS(23, 'eax') + \'\'\'
''' + DIRTY + '''  ret
d_mark:''')
rep(''''vpcap', 'batch', 'dip', 'post',''', ''''vpcap', 'batch', 'dip', 'dp', 'smode', 'two_on', 'two_off', 'post',''')
open(os.path.join(HERE, 'outline10_fix_r1.py'), 'w').write(s)
open(os.path.join(HERE, 'outline10_fix_r1.diff'), 'w').writelines(difflib.unified_diff(orig.splitlines(True), s.splitlines(True), 'ol2/outline10.py', 'agent_stencil/outline10_fix_r1.py'))
print('wrote outline10_fix_r1.py')

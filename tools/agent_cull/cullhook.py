# Proposed "keep group members drawn" hook for outline10 (WoW 3.3.5a 12340).
#
# Site: inside 0x793450 (CWorldScene "process culled map entities", called once per frame from
# 0x79AB2F in 0x79A870 = world cull/render prep, before the M2 scene build 0x821A20 at 0x79AC13).
# At 0x7934C6 the entity (ebx) has just been unlinked from the "not visible" list 0xCDB0A4.
#   007934C6  8B 4B 34        mov ecx,[ebx+0x34]      ; E->model
#   007934C9  33 D2           xor edx,edx
#   007934CB  33 F6           xor esi,esi             ; <- continue here (original path)
# Patch: 0x7934C6: E9 rel32 -> cull  (exactly 5 bytes, 2 whole instructions; only branch into the
# range is "je 0x7934C6" at 0x79349D, i.e. to the start of the jmp).
# Register state at the site: ebx = entity, edi = 0 (set at loop top 0x793479), [ebp-4] = next entity.
# The original path needs edi = 0, ecx = model, edx = 0. ensure preserves ebx/esi/edi.
#
# Forced path = copy of the visible branch of 0x793060 (0x793145..0x7931FD) minus "E+0x25 = 0"
# (E+0x25 stays "culled", so CWorld intersect queries with flag 0x1000000 and anything else that
# asks "was this entity visible" behave like in the unmodified game).
SITE = 0x7934C6
ORIG = bytes.fromhex('8b4b3433d2')
CONT = 0x7934CB          # original path continues here
NEXT = 0x79358F          # "mov ebx,[ebp-4]; jmp 0x793470" = next entity

CULL = '''
cull:
  cmp dword ptr [ebx+0x90],0x4F9F70
  jne cu_orig
  test byte ptr [ebx+0x7C],4
  jnz cu_orig
  cmp dword ptr [ebx+0x34],0
  je cu_orig
  call ensure
  cmp dword ptr [{GMODE}],0
  je cu_orig
  mov ecx,dword ptr [{GRPN}]
  test ecx,ecx
  jz cu_orig
  mov edx,{UNITS}
cu_l:
  mov eax,[edx]
  cmp eax,[ebx+0x98]
  jne cu_n
  mov eax,[edx+4]
  cmp eax,[ebx+0x9C]
  je cu_hit
cu_n:
  add edx,24
  dec ecx
  jnz cu_l
cu_orig:
  mov ecx,[ebx+0x34]
  xor edx,edx
  jmp 0x7934CB
cu_hit:
  mov ecx,dword ptr [0xCD8798]
  imul ecx,ecx,0xFC
  add ecx,0xCDB168
  lea eax,[ebx+0x38]
  push eax
  call 0x983D20
  test eax,eax
  jz cu_orig
  mov ecx,[ebx+0x34]
  push 1
  call 0x823F10
  mov ecx,[ebx+0x34]
  mov eax,0x10008
  cmp dword ptr [ecx+0x48],0
  je cu_f
  mov eax,0x20080
cu_f:
  or dword ptr [ecx+0x10],eax
  mov dword ptr [ecx+0x2AC],0x780CD0
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
  mov ecx,0xCDB098
  call 0x6DED60
cu_done:
  jmp 0x79358F
'''

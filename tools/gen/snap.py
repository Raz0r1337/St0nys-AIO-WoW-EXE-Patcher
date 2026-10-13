from asmgen import *
def rnd(off,clamp):
    s='''  fld dword ptr [esi+%s]
  fadd dword ptr [esp+4]
  frndint
'''%off
    if clamp: s+='''  fld1
  fcomi st(0),st(1)
  fcmovbe st(0),st(1)
  fstp dword ptr [esi+%s]
  fstp st(0)
'''%off
    else: s+='  fstp dword ptr [esi+%s]\n'%off
    return s
SRC='''snap:
  push esi
  push dword ptr [esp+0x18]
  push dword ptr [esp+0x18]
  push dword ptr [esp+0x18]
  push dword ptr [esp+0x18]
  push dword ptr [esp+0x18]
  call tramp
  add esp,0x14
  test al,al
  jz out
  push eax
  fld dword ptr [esp+0x14]
  fcomp dword ptr [esp+0x1C]
  fnstsw ax
  and ah,0x45
  cmp ah,0x40
  je out_pop
  mov esi,[esp+0x10]
  sub esp,8
  fnstcw word ptr [esp]
  mov ax,word ptr [esp]
  and ax,0xF3FF
  or ax,0x400
  mov word ptr [esp+2],ax
  mov dword ptr [esp+4],0x3F000000
  fldcw word ptr [esp+2]
'''+rnd('0x18',1)+rnd('0x1C',1)+rnd('0x20',0)+rnd('0x24',0)+'''  fldcw word ptr [esp]
  add esp,8
out_pop:
  pop eax
out:
  pop esi
  ret
tramp:
  push ebp
  mov ebp,esp
  sub esp,0x44
  jmp 0x6C0E86
'''
tpl,absf,relf=reloc(SRC)
LAB=label_offsets(SRC,B1,['snap','tramp'])
if __name__=='__main__':
    print(len(tpl),absf,relf,LAB); dis(tpl,B1)

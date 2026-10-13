# Outline PoC generator: target + mouseover outline via stencil (WoW 3.3.5a 12340)
from asmgen import *
import struct
CODE_OFF=0x150
PX=2.0   # outline thickness in pixels
OFFS=[(PX,0),(-PX,0),(0,PX),(0,-PX),(PX,PX),(PX,-PX),(-PX,PX),(-PX,-PX)]
# data layout (section offsets)
DO=dict(VP=0x00,CUR=0x18,T=0x1C,T2=0x20,M=0x24,M2=0x28,VALID=0x2C,MARKED=0x30,COLT=0x34,COLM=0x38,
        PS=0x44,PSDEV=0x48,MAT=0x4C,VERTS=0x8C,FX=0xDC,FY=0xE0,OFFS=0xE4,PSCODE=0x124,SX=0x138,SY=0x13C,TWO=0x140,MTWO=0x144,HALF=0x148,SMODE=0x14C)
# external addresses
X=dict(DEVPTR=0xC5DF88,VT9=0xA2E718,WSCENE=0xCD754C,DRAWBATCH=0x8203B0,AFTERB=0x823AD3,VPRET=0x6A9B16,
       CIRCLES=0x4F6F90,OBJPTR=0x4D4DB0,FILESTR=0xA22CD4,SELCOL=0x521BF0,TGT=0xBD07B0,TGT4=0xBD07B4,
       MOV=0xBD07A0,MOV4=0xBD07A4,SHADERS=0xD43020,C2=0xC5F008,C3=0xC5F018,C4=0xC5F028,C5=0xC5F038,
       MARKDIRTY=0x685970,FORCEUPD=0x685A70)
def SRS(state,val):
    v=val if isinstance(val,str) else '0x%X'%val
    return '''  push %s
  push %d
  push esi
  mov eax,[esi]
  call dword ptr [eax+0xE4]
'''%(v,state)
def src(base,sym=False):
    base=base or 0
    A={k:('0x%X'%(base+v) if not sym else k) for k,v in DO.items()}
    A.update({k:('0x%X'%v if not sym else ('0x%X'%v if k not in ('DEVPTR','WSCENE','TGT','TGT4','MOV','MOV4','SHADERS','C2','C3','C4','C5') else k)) for k,v in X.items()})
    def f(s):
        for k,v in sorted(A.items(),key=lambda kv:-len(kv[0])): s=s.replace('{'+k+'}',v)
        return s
    s='''
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
  xor eax,eax
  mov dword ptr [{T}],eax
  mov dword ptr [{T2}],eax
  mov dword ptr [{M}],eax
  mov dword ptr [{M2}],eax
  call okdev
  test eax,eax
  jz e_ret
  push esi
  push edi
  mov esi,{TGT}
  mov edi,{T}
  push {COLT}
  call lookup
  mov eax,dword ptr [{MOV}]
  cmp eax,dword ptr [{TGT}]
  jne e_m
  mov eax,dword ptr [{MOV4}]
  cmp eax,dword ptr [{TGT4}]
  je e_done
e_m:
  mov esi,{MOV}
  mov edi,{M}
  push {COLM}
  call lookup
e_done:
  pop edi
  pop esi
e_ret:
  ret
lookup:
  mov eax,[esi]
  or eax,[esi+4]
  jz l_ret
  push 0
  push {FILESTR}
  push 0x18
  push dword ptr [esi+4]
  push dword ptr [esi]
  call {OBJPTR}
  add esp,0x14
  test eax,eax
  jz l_ret
  mov ecx,[eax+0xB4]
  mov [edi],ecx
  mov ecx,[eax+0x98C]
  mov [edi+4],ecx
  push 1
  push dword ptr [esp+8]
  push esi
  call {SELCOL}
  add esp,0xC
l_ret:
  ret 4
classify:
  test eax,eax
  jz c_none
  mov ecx,eax
  mov edx,3
c_loop:
  cmp ecx,dword ptr [{T}]
  je c_t
  cmp ecx,dword ptr [{T2}]
  je c_t
  cmp ecx,dword ptr [{M}]
  je c_m
  cmp ecx,dword ptr [{M2}]
  je c_m
  mov ecx,[ecx+0x48]
  test ecx,ecx
  jz c_none
  dec edx
  jnz c_loop
c_none:
  xor eax,eax
  ret
c_t:
  mov eax,1
  ret
c_m:
  mov eax,2
  ret
dip:
  mov eax,dword ptr [{CUR}]
  test eax,eax
  jnz d_mark
  cmp dword ptr [{MARKED}],0
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
'''+SRS(52,1)+SRS(56,8)+SRS(57,0)+SRS(55,3)+SRS(53,1)+SRS(54,1)+SRS(58,0xFF)+SRS(59,0xFF)+'''
  jmp d_cl_done
d_cl_off:
'''+SRS(52,0)+'''
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
'''+SRS(52,0)+'''
d_nosm:
  mov ecx,dword ptr [{DEVPTR}]
  cmp dword ptr [ecx+0x3E60],0
  jne d_plain
'''+SRS(52,1)+SRS(56,8)+SRS(57,4)+SRS(55,3)+SRS(53,1)+SRS(54,1)+SRS(58,0xFF)+SRS(59,0xFF)+'''
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
'''+SRS(56,3)+'''
  mov eax,dword ptr [{CUR}]
  or eax,4
'''+SRS(57,'eax')+SRS(58,3)+SRS(23,8)+'''
  call do_dip
'''+SRS(23,'ebx')+SRS(58,0xFF)+SRS(56,5)+'''
  mov eax,dword ptr [{CUR}]
'''+SRS(57,'eax')+SRS(168,0)+SRS(14,1)+'''
  fild dword ptr [{VP}+8]
  fdivr dword ptr [{TWO}]
  fstp dword ptr [{SX}]
  fild dword ptr [{VP}+12]
  fdivr dword ptr [{MTWO}]
  fstp dword ptr [{SY}]
  xor edi,edi
d_loop:
  fld dword ptr [{OFFS}+edi*8]
  fmul dword ptr [{SX}]
  fstp dword ptr [{FX}]
  fld dword ptr [{OFFS}+edi*8+4]
  fmul dword ptr [{SY}]
  fstp dword ptr [{FY}]
'''+''.join('''  fld dword ptr [{C5}+%d]
  fmul dword ptr [{FX}]
  fadd dword ptr [{C2}+%d]
  fstp dword ptr [{MAT}+%d]
  fld dword ptr [{C5}+%d]
  fmul dword ptr [{FY}]
  fadd dword ptr [{C3}+%d]
  fstp dword ptr [{MAT}+%d]
'''%(4*k,4*k,4*k,4*k,4*k,16+4*k) for k in range(4))+''.join('''  mov eax,dword ptr [{C4}+%d]
  mov dword ptr [{MAT}+%d],eax
'''%(4*k,32+4*k) for k in range(8))+'''
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
d_end:
'''+SRS(52,0)+'''
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
'''+SRS(52,1)+SRS(56,3)+SRS(55,1)+SRS(53,1)+SRS(54,1)+SRS(58,0xFF)+SRS(23,8)+SRS(14,0)+SRS(27,0)+SRS(15,0)+SRS(22,1)+SRS(168,0xF)+SRS(28,0)+'''
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
  mov eax,dword ptr [{T}]
  or eax,dword ptr [{T2}]
  jz p_m
  mov ebx,1
  mov edx,dword ptr [{COLT}]
  call quad
p_m:
  mov eax,dword ptr [{M}]
  or eax,dword ptr [{M2}]
  jz p_inv
  mov ebx,2
  mov edx,dword ptr [{COLM}]
  call quad
p_inv:
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
'''+SRS(52,0)+'''
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
'''+SRS(57,'ebx')+'''
  push 20
  push {VERTS}
  push 2
  push 5
  push esi
  mov eax,[esi]
  call dword ptr [eax+0x14C]
  ret
'''
    return f(s)
# data template
def data():
    d=bytearray(CODE_OFF)
    # vertices: z=0, rhw=1 for all 4
    for i in range(4):
        struct.pack_into('<ff',d,DO['VERTS']+i*20+8,0.0,1.0)
    for i,(x,y) in enumerate(OFFS): struct.pack_into('<ff',d,DO['OFFS']+i*8,x,y)
    struct.pack_into('<3f',d,DO['TWO'],2.0,-2.0,0.5)
    struct.pack_into('<5I',d,DO['PSCODE'],0xFFFF0101,0x00000001,0x800F0000,0x90E40000,0x0000FFFF)
    return d
def reloc2():
    a=asm(src(B1),B1+CODE_OFF); b=asm(src(B2),B2+CODE_OFF)
    assert len(a)==len(b)
    delta=B2-B1; absf=[]; relf=[]; done=set()
    for k in [k for k in range(len(a)) if a[k]!=b[k]]:
        if k in done: continue
        for s in range(k-3,k+1):
            if s<0 or s+4>len(a): continue
            va=struct.unpack_from('<I',a,s)[0]; vb=struct.unpack_from('<I',b,s)[0]
            if (vb-va)&0xFFFFFFFF==delta: absf.append(s+CODE_OFF); done.update(range(s,s+4)); break
            if (va-vb)&0xFFFFFFFF==delta: relf.append(s+CODE_OFF); done.update(range(s,s+4)); break
        else: raise Exception(hex(k))
    return a,absf,relf
code,absf,relf=reloc2()
TPL=bytes(data())+code
LAB={k:CODE_OFF+v for k,v in label_offsets(src(B1),B1+CODE_OFF,['vpcap','batch','dip','post','okdev','ensure','lookup','classify','quad']).items()}
if __name__=='__main__':
    print('size',hex(len(TPL)),'abs',len(absf),'rel',len(relf),{k:hex(v) for k,v in LAB.items()})

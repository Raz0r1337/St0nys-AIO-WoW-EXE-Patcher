from asmgen import *
CODE_OFF=0x120
def src(base,focusoff=0x12345678):
    base0=base; base=base or 0
    D=dict(focusabs=(base+focusoff) if focusoff!=0x12345678 else focusoff, held=base, suppress=base+0x100, evreg=base+0x104, guid=base+0x108, btn=base+0x110, strab=base+0x114)
    s='''
exec:
  push ebp
  mov ebp,esp
  sub esp,0x104
  push ebx
  push esi
  push edi
  mov [ebp-0x104],ecx
  mov byte ptr [ebp-0x100],0
  push 0x80
  lea eax,[ebp-0x100]
  push eax
  push dword ptr [ebp+0xC]
  push dword ptr [ebp+0x18]
  call 0x5622E0
  test eax,eax
  jz ex_orig
  push dword ptr [ebp+0x18]
  push eax
  mov ecx,[ebp-0x104]
  call 0x55E470
  test eax,eax
  jz ex_orig
  mov esi,eax
  mov edi,{strab}
  mov ecx,12
ex_cmp:
  mov al,[esi]
  cmp al,0x61
  jb ex_c1
  cmp al,0x7A
  ja ex_c1
  sub al,0x20
ex_c1:
  cmp al,[edi]
  jne ex_orig
  inc esi
  inc edi
  dec ecx
  jnz ex_cmp
  xor eax,eax
ex_dig:
  movzx edx,byte ptr [esi]
  sub edx,0x30
  cmp edx,9
  ja ex_num
  imul eax,eax,10
  add eax,edx
  cmp eax,12
  ja ex_orig
  inc esi
  jmp ex_dig
ex_num:
  test eax,eax
  jz ex_orig
  lea ebx,[eax-1]
  cmp dword ptr [0xC1E5A0],0
  je ex_p1
  mov edx,1
  jmp ex_p2
ex_p1:
  mov edx,dword ptr [0xC1E598]
  inc edx
ex_p2:
  cmp edx,1
  jne ex_p3
  mov ecx,dword ptr [0xC1E59C]
  test ecx,ecx
  jz ex_p3
  lea edx,[ecx+6]
ex_p3:
  dec edx
  imul edx,edx,12
  add ebx,edx
  mov edx,[ebp+0xC]
  call find
  cmp dword ptr [ebp+0x10],0
  je ex_up
  test eax,eax
  jnz ex_init
  call findfree
  test eax,eax
  jz ex_orig
ex_init:
  mov esi,eax
  mov [esi+4],ebx
  call 0x86AE20
  mov [esi+8],eax
  mov [esi+12],eax
  xor eax,eax
  mov [esi+16],eax
  mov [esi+20],eax
  mov edx,[ebp+0xC]
  mov [esi],edx
  mov dword ptr [esi+24],1
  cmp dword ptr [{evreg}],0
  jne ex_orig
  mov dword ptr [{evreg}],1
  push 0
  push 0
  push {focusabs}
  push 2
  call 0x47D3C0
  add esp,16
  jmp ex_orig
ex_up:
  test eax,eax
  jz ex_orig
  mov dword ptr [eax+24],0
  cmp dword ptr [eax+20],0
  je ex_orig
  mov dword ptr [{suppress}],1
  push dword ptr [ebp+0x18]
  push dword ptr [ebp+0x14]
  push dword ptr [ebp+0x10]
  push dword ptr [ebp+0xC]
  push dword ptr [ebp+8]
  mov ecx,[ebp-0x104]
  call exec_tramp
  mov dword ptr [{suppress}],0
  pop edi
  pop esi
  pop ebx
  mov esp,ebp
  pop ebp
  ret 0x14
ex_orig:
  mov ecx,[ebp-0x104]
  pop edi
  pop esi
  pop ebx
  mov esp,ebp
  pop ebp
exec_tramp:
  push ebp
  mov ebp,esp
  sub esp,0xC4
  jmp 0x563159
find:
  mov eax,{held}
  mov ecx,8
f_l:
  cmp dword ptr [eax+24],0
  je f_n
  cmp [eax],edx
  je f_r
f_n:
  add eax,32
  dec ecx
  jnz f_l
  xor eax,eax
f_r:
  ret
findfree:
  mov eax,{held}
  mov ecx,8
ff_l:
  cmp dword ptr [eax+24],0
  je ff_r
  add eax,32
  dec ecx
  jnz ff_l
  xor eax,eax
ff_r:
  ret
focus:
  mov eax,{held}
  mov ecx,8
fo_l:
  mov dword ptr [eax+24],0
  add eax,32
  dec ecx
  jnz fo_l
  mov eax,1
  ret
use:
  cmp dword ptr [{suppress}],0
  je use_tramp
  mov dword ptr [{suppress}],0
  ret
use_tramp:
  push ebp
  mov ebp,esp
  sub esp,0xC
  jmp 0x5ABBC6
render:
  call render_tramp
  push eax
  call update
  pop eax
  ret
render_tramp:
  push ebp
  mov ebp,esp
  sub esp,0x34
  jmp 0x4F8EA6
update:
  push ebx
  push esi
  push edi
  push ebp
  sub esp,16
  mov ebx,esp
  call 0x86AE20
  mov ebp,eax
  call 0x4D3790
  push 0
  push 0xA22CD4
  push 0x10
  push edx
  push eax
  call 0x4D4DB0
  add esp,0x14
  mov ecx,1
  test eax,eax
  jz cast_done
  cmp dword ptr [eax+0xA6C],0
  je cast_chan
  mov edx,ebp
  sub edx,[eax+0xA7C]
  js cast_done
cast_chan:
  cmp dword ptr [eax+0xA80],0
  je cast_no
  mov edx,ebp
  sub edx,[eax+0xA88]
  js cast_done
cast_no:
  xor ecx,ecx
cast_done:
  mov [ebx+12],ecx
  mov esi,{held}
  mov edi,8
up_l:
  cmp dword ptr [esi+24],0
  je up_n
  mov eax,ebp
  sub eax,[esi+8]
  cmp eax,500
  jb up_n
  cmp dword ptr [0xD3F4E4],0
  jne up_busy
  cmp dword ptr [ebx+12],0
  je up_nc
up_busy:
  mov dword ptr [esi+16],0
  jmp up_n
up_nc:
  xor eax,eax
  mov [ebx],eax
  mov [ebx+4],eax
  mov [ebx+8],eax
  lea eax,[ebx+8]
  push eax
  lea eax,[ebx+4]
  push eax
  push ebx
  push dword ptr [esi+4]
  call 0x5A8E40
  add esp,16
  mov eax,[ebx+4]
  test eax,eax
  jle up_ready
  mov ecx,ebp
  sub ecx,[ebx]
  cmp ecx,eax
  jae up_ready
  mov dword ptr [esi+16],0
  jmp up_n
up_ready:
  cmp dword ptr [esi+16],0
  jne up_r2
  mov [esi+16],ebp
up_r2:
  mov eax,ebp
  sub eax,[esi+16]
  cmp eax,100
  jb up_n
  mov eax,ebp
  sub eax,[esi+12]
  cmp eax,100
  jb up_n
  xor eax,eax
  mov dword ptr [{guid}],eax
  mov dword ptr [{guid4}],eax
  mov dword ptr [{btn}],eax
  push {btn}
  push {guid}
  push dword ptr [esi+4]
  call use_tramp
  add esp,12
  mov [esi+12],ebp
  mov dword ptr [esi+20],1
up_n:
  add esi,32
  dec edi
  jnz up_l
  add esp,16
  pop ebp
  pop edi
  pop esi
  pop ebx
  ret
'''
    D['guid4']=D['guid']+4
    if base0 is None:
        for k in D: s=s.replace('{%s}'%k, {'focusabs':'focus','guid4':'guid+4'}.get(k,k))
        return s
    for k,v in D.items(): s=s.replace('{%s}'%k,'0x%X'%v)
    return s
def reloc2(fn):
    a=asm(fn(B1),B1+CODE_OFF); b=asm(fn(B2),B2+CODE_OFF)
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
FOCUS_OFF=CODE_OFF+label_offsets(src(B1),B1+CODE_OFF,['focus'])['focus']
src0=src
src=lambda base: src0(base,FOCUS_OFF)
code,absf,relf=reloc2(src)
DATA=bytearray(CODE_OFF); DATA[0x114:0x120]=b'ACTIONBUTTON'
TPL=bytes(DATA)+code
LAB={k:CODE_OFF+v for k,v in label_offsets(src(B1),B1+CODE_OFF,['exec','use','render','focus','update','exec_tramp','use_tramp','render_tramp']).items()}
if __name__=='__main__':
    print('size',hex(len(TPL)),'abs',absf,'rel',relf,{k:hex(v) for k,v in LAB.items()})
    dis(code,B1+CODE_OFF)

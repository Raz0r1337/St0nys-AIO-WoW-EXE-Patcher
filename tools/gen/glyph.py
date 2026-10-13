from asmgen import *
# Section code: labels are offsets from section start
SRC='''
newdesc:
  push esi
  push edi
  push ebx
  xor eax,eax
  xor edx,edx
  mov esi,[ecx+0xC]
  mov edi,[ecx+4]
nd_loop:
  test esi,esi
  jz nd_end
  test esi,1
  jnz nd_end
  mov ebx,[esi+0x30]
  cmp ebx,edx
  jbe nd_skip
  sub ebx,edx
  cmp ebx,eax
  jbe nd_skip
  mov eax,ebx
nd_skip:
  mov edx,[esi+0x34]
  inc edx
  mov esi,[esi+edi+4]
  jmp nd_loop
nd_end:
  mov ebx,0x100
  cmp ebx,edx
  jbe nd_store
  sub ebx,edx
  cmp ebx,eax
  jbe nd_store
  mov eax,ebx
nd_store:
  mov [ecx],eax
  pop ebx
  pop edi
  pop esi
  push ebp
  mov ebp,esp
  sub esp,0xC
  jmp 0x6C5126
clear:
  and dword ptr [ecx+0x60],0
  and dword ptr [ecx+0x64],0
  push esi
  push edi
  mov esi,ecx
  push 0
  jmp 0x6C6B96
render:
  push ebx
  push esi
  push edi
  push ebp
  mov ebx,ecx
  xor ebp,ebp
rb_pass:
  xor edi,edi
  mov esi,[ebx+0x24]
rb_str:
  test esi,esi
  jz rb_end
  test esi,1
  jnz rb_end
  mov eax,[esi+0x64]
  test ebp,ebp
  jz rb_do
  test eax,eax
  jz rb_next
rb_do:
  or edi,eax
  mov ecx,esi
  call 0x6C7480
rb_next:
  mov eax,[ebx+0x1C]
  mov esi,[esi+eax+4]
  jmp rb_str
rb_end:
  test edi,edi
  jz rb_out
  inc ebp
  cmp ebp,4
  jb rb_pass
rb_out:
  mov ecx,ebx
  pop ebp
  pop edi
  pop esi
  pop ebx
  push ebp
  mov ebp,esp
  sub esp,0x20
  jmp 0x6C4AD6
tex:
  cmp dword ptr [esp+4],1
  jne tx_go
  push edi
  push ecx
  push eax
  mov edi,0xC7D328
  mov ecx,0x8000
  xor eax,eax
  rep stosd
  pop eax
  pop ecx
  pop edi
tx_go:
  push ebp
  mov ebp,esp
  push ecx
  cmp dword ptr [ebp+8],1
  jmp 0x6C9F58
'''
CHECK='''
  push esi
  mov esi,ecx
  cmp dword ptr [esi+0x64],0
  je L
  mov ecx,esi
  call 0x6C6B90
L:
  mov ecx,esi
  call 0x6C7B10
  xor eax,eax
  mov [esi+0x64],eax
  mov [esi+0xD4],eax
  cmp [esi+0xB0],eax
  setne al
  pop esi
  ret
'''
def labels(src):
    # find offsets of labels by assembling prefix up to label
    out={}; lines=src.strip('\n').split('\n')
    for idx,l in enumerate(lines):
        if l.strip().endswith(':') :
            name=l.strip()[:-1]
            pre='\n'.join(lines[:idx])+'\n'+'\n'.join(lines[idx:])  # not used
    return out
tpl,absf,relf=reloc(SRC)
# label offsets: assemble with a marker trick: keystone symbol resolution via 'resolver' not avail; compute by assembling prefixes
LAB=label_offsets(SRC,B1,['newdesc','clear','render','tex'])
chk=asm(CHECK,0x6C7480)
if __name__=='__main__':
    print('section size',len(tpl),'abs',absf,'rel',relf,LAB)
    dis(tpl,B1)
    print('check',len(chk)); dis(chk,0x6C7480)

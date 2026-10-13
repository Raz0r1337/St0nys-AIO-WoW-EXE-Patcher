# More lights generator (WoW 3.3.5a 12340): 8 point lights instead of 4
#  - CM2Lighting keeps the nearest 4 inline (unchanged), lights 5..8 go to a side ring
#  - shader path: lights 5..8 uploaded to VS c236..c246 (same 11-register layout as c17..c27)
#  - fixed-function path: Gx light slots moved to an 8-slot array, SetupGxLights takes the
#    7 nearest (also fixes the original "nearest light dropped" bug)
#  - terrain (0x7D0050, shader path): the chunk shader gets lights 1-3 in c28-c36 as before;
#    lights 4-8 (inline #4 + side list) go to VS c236-c250 in the terrain format
#    (position world minus camera w=1, colour w=0, attenuation w=0; empty: 0 / att x=1)
from asmgen import *
import struct
RINGN=8192; ESZ=0x28; RINGBYTES=RINGN*ESZ
DO=dict(RING=0x00,NEXT=0x04,FAIL=0x08,TMP=0x0C,GXLIST=0x10,EXTBUF=0x40,GX=0x100,TBUF=0x340)
CODE_OFF=0x430
X=dict(DEVPTR=0xC5DF88,VALLOC=0x9DF238,CLL=0x872900,XFORM=0x4C21B0,REJ_RET=0x83508E,TL_RET=0x835114,TER_RET=0x7D0298,CAMX=0xCD8F5C)
SITES=dict(REJ=0x834FC7,EVICT=0x834FCD,TL=0x83510E,UPM2=0x873E85,UPWMO=0x7A91A9,FFCNT=0x835483,FFLEA=0x8354CB,TER=0x7D0292)
def src(base,sym=False):
    A={k:('0x%X'%(base+v) if not sym else k) for k,v in DO.items()}
    A.update({k:('0x%X'%v if not sym else k) for k,v in X.items()})
    A.update(dict(RINGN1='0x%X'%(RINGN-1),RINGBYTES='0x%X'%RINGBYTES))
    def f(s):
        for k,v in sorted(A.items(),key=lambda kv:-len(kv[0])): s=s.replace('{'+k+'}',v)
        return s
    s='''
get_entry:
  movzx eax,word ptr [ecx+0x16]
  test eax,eax
  jz ge_ret
  mov edx,dword ptr [{RING}]
  test edx,edx
  jz ge_none
  dec eax
  imul eax,eax,0x28
  add eax,edx
  cmp dword ptr [eax],ecx
  jne ge_none
ge_ret:
  ret
ge_none:
  xor eax,eax
  ret
alloc_entry:
  call get_entry
  test eax,eax
  jnz ae_ret
  mov eax,dword ptr [{RING}]
  test eax,eax
  jnz ae_have
  cmp dword ptr [{FAIL}],0
  jne ae_none
  push ecx
  push 4
  push 0x3000
  push {RINGBYTES}
  push 0
  call dword ptr [{VALLOC}]
  pop ecx
  test eax,eax
  jnz ae_ok
  mov dword ptr [{FAIL}],1
  jmp ae_none
ae_ok:
  mov dword ptr [{RING}],eax
ae_have:
  mov edx,dword ptr [{NEXT}]
  lea eax,[edx+1]
  mov word ptr [ecx+0x16],ax
  and eax,{RINGN1}
  mov dword ptr [{NEXT}],eax
  imul edx,edx,0x28
  add edx,dword ptr [{RING}]
  mov dword ptr [edx],ecx
  mov dword ptr [edx+4],0
  mov eax,edx
ae_ret:
  ret
ae_none:
  xor eax,eax
  ret
ins_extra:
  push ebx
  push esi
  push edi
  mov ebx,edx
  mov edi,eax
  cmp edi,0x7F800000
  jae ie_done
  call alloc_entry
  test eax,eax
  jz ie_done
  mov esi,dword ptr [eax+4]
  cmp esi,4
  jb ie_room
  cmp edi,dword ptr [eax+0x24]
  jae ie_done
  mov esi,3
  jmp ie_loop
ie_room:
  inc dword ptr [eax+4]
ie_loop:
  test esi,esi
  jz ie_store
  cmp edi,dword ptr [eax+esi*4+0x14]
  ja ie_store
  mov edx,dword ptr [eax+esi*4+4]
  mov dword ptr [eax+esi*4+8],edx
  mov edx,dword ptr [eax+esi*4+0x14]
  mov dword ptr [eax+esi*4+0x18],edx
  dec esi
  jmp ie_loop
ie_store:
  mov dword ptr [eax+esi*4+8],ebx
  mov dword ptr [eax+esi*4+0x18],edi
ie_done:
  pop edi
  pop esi
  pop ebx
  ret
cave_reject:
  fstp dword ptr [{TMP}]
  mov eax,dword ptr [{TMP}]
  mov edx,ebx
  call ins_extra
  jmp {REJ_RET}
cave_evict:
  fstp dword ptr [{TMP}]
  mov edx,dword ptr [ecx+0x90]
  mov eax,dword ptr [ecx+0xA0]
  call ins_extra
  fld dword ptr [{TMP}]
  mov esi,3
  ret
cave_tl:
  push edi
  push ebx
  mov ecx,esi
  call get_entry
  test eax,eax
  jz tl_done
  mov edi,eax
  xor ebx,ebx
tl_loop:
  cmp ebx,dword ptr [edi+4]
  jae tl_done
  mov eax,dword ptr [esi]
  add eax,0x84
  push eax
  mov ecx,dword ptr [edi+ebx*4+8]
  add ecx,0xC
  push ecx
  lea edx,[ebp-0x18]
  push edx
  call {XFORM}
  add esp,0xC
  mov ecx,dword ptr [edi+ebx*4+8]
  mov edx,dword ptr [eax]
  mov dword ptr [ecx+0x18],edx
  mov edx,dword ptr [eax+4]
  mov dword ptr [ecx+0x1C],edx
  mov edx,dword ptr [eax+8]
  mov dword ptr [ecx+0x20],edx
  inc ebx
  jmp tl_loop
tl_done:
  pop ebx
  pop edi
  mov ecx,dword ptr [esi+0x14]
  and ecx,0x60
  jmp {TL_RET}
cll_ex:
  push ebp
  mov ebp,esp
  push dword ptr [ebp+0x14]
  push dword ptr [ebp+0x10]
  push dword ptr [ebp+0xC]
  push dword ptr [ebp+8]
  call {CLL}
  add esp,0x10
  mov ecx,dword ptr [{DEVPTR}]
  test ecx,ecx
  jz cx_done
  cmp dword ptr [ecx+0x2E0],0xF7
  jl cx_done
  mov ecx,dword ptr [ebp+0x10]
  sub ecx,0x84
  call get_entry
  xor edx,edx
  test eax,eax
  jz cx_n
  mov edx,dword ptr [eax+4]
  add eax,8
cx_n:
  push dword ptr [ebp+0x14]
  push eax
  push edx
  push {EXTBUF}
  call {CLL}
  add esp,0x10
  mov ecx,dword ptr [{DEVPTR}]
  mov eax,dword ptr [ecx]
  push 0xB
  push {EXTBUF}
  push 0xEC
  push 0
  call dword ptr [eax+0x118]
cx_done:
  pop ebp
  ret
cave_ff:
  push eax
  push ecx
  push edx
  push edi
  push esi
  mov ecx,esi
  call get_entry
  mov edx,dword ptr [esi+0xA4]
  xor ecx,ecx
  test eax,eax
  jz ff_1
  mov ecx,dword ptr [eax+4]
ff_1:
  lea ebx,[edx+ecx]
  lea edi,[ebx-1]
  mov esi,dword ptr [esp]
  add esi,0x84
ff_in:
  test edx,edx
  jz ff_ex
  push dword ptr [esi]
  pop dword ptr [edi*4+{GXLIST}]
  add esi,4
  dec edi
  dec edx
  jmp ff_in
ff_ex:
  test ecx,ecx
  jz ff_done
  lea esi,[eax+8]
ff_ex2:
  push dword ptr [esi]
  pop dword ptr [edi*4+{GXLIST}]
  add esi,4
  dec edi
  dec ecx
  jnz ff_ex2
ff_done:
  pop esi
  pop edi
  pop edx
  pop ecx
  pop eax
  ret
cave_ter:
  pushad
  mov ecx,dword ptr [{DEVPTR}]
  test ecx,ecx
  jz ct_done
  cmp dword ptr [ecx+0x2E0],0xFB
  jl ct_done
  mov edi,{TBUF}
  mov ecx,5
ct_clr:
  xor eax,eax
  mov dword ptr [edi+0],eax
  mov dword ptr [edi+4],eax
  mov dword ptr [edi+8],eax
  mov dword ptr [edi+12],eax
  mov dword ptr [edi+16],eax
  mov dword ptr [edi+20],eax
  mov dword ptr [edi+24],eax
  mov dword ptr [edi+28],eax
  mov dword ptr [edi+32],eax
  mov dword ptr [edi+36],eax
  mov dword ptr [edi+40],eax
  mov dword ptr [edi+44],eax
  mov dword ptr [edi+0x20],0x3F800000
  add edi,0x30
  dec ecx
  jnz ct_clr
  lea ecx,[ebp-0x104]
  cmp dword ptr [ecx+0xA4],3
  jbe ct_ex
  mov eax,dword ptr [ecx+0x90]
  mov edi,{TBUF}
  call ct_put
ct_ex:
  lea ecx,[ebp-0x104]
  call get_entry
  test eax,eax
  jz ct_up
  mov esi,eax
  xor ebx,ebx
ct_l:
  cmp ebx,dword ptr [esi+4]
  jae ct_up
  cmp ebx,4
  jae ct_up
  mov eax,dword ptr [esi+ebx*4+8]
  lea edi,[ebx+ebx*2]
  shl edi,4
  add edi,{TBUF}+0x30
  call ct_put
  inc ebx
  jmp ct_l
ct_up:
  mov ecx,dword ptr [{DEVPTR}]
  mov eax,dword ptr [ecx]
  push 0xF
  push {TBUF}
  push 0xEC
  push 0
  call dword ptr [eax+0x118]
ct_done:
  popad
  mov ecx,dword ptr [{DEVPTR}]
  jmp {TER_RET}
ct_put:
  fld dword ptr [eax+0xC]
  fsub dword ptr [{CAMX}+0]
  fstp dword ptr [edi+0]
  fld dword ptr [eax+0x10]
  fsub dword ptr [{CAMX}+4]
  fstp dword ptr [edi+4]
  fld dword ptr [eax+0x14]
  fsub dword ptr [{CAMX}+8]
  fstp dword ptr [edi+8]
  mov dword ptr [edi+0xC],0x3F800000
  mov ecx,dword ptr [eax+0x3C]
  mov dword ptr [edi+0x10],ecx
  mov ecx,dword ptr [eax+0x40]
  mov dword ptr [edi+0x14],ecx
  mov ecx,dword ptr [eax+0x44]
  mov dword ptr [edi+0x18],ecx
  mov ecx,dword ptr [eax+0x54]
  mov dword ptr [edi+0x20],ecx
  mov ecx,dword ptr [eax+0x58]
  mov dword ptr [edi+0x24],ecx
  mov ecx,dword ptr [eax+0x5C]
  mov dword ptr [edi+0x28],ecx
  mov dword ptr [edi+0x1C],0
  mov dword ptr [edi+0x2C],0
  ret
'''
    return f(s)
LABELS=['get_entry','alloc_entry','ins_extra','cave_reject','cave_evict','cave_tl','cll_ex','cave_ff','cave_ter']
def data():
    d=bytearray(CODE_OFF)
    struct.pack_into('<4f',d,DO['EXTBUF']+8*16,1.0,1.0,1.0,1.0)   # c244 (attenuation 0) = 1.0 before first use
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
LAB={k:CODE_OFF+v for k,v in label_offsets(src(B1),B1+CODE_OFF,LABELS).items()}
GX=DO['GX']
# same-length rewrites of the Gx light slot users (offset = from GX base; None = plain bytes)
FF=[
 (0x682FD9,'8D94C148250000','8D14C5',0x00,'LightGet: Slot im neuen 8er-Feld'),
 (0x683089,'8D84C148250000','8D04C5',0x00,'LightEnable: Slot im neuen 8er-Feld'),
 (0x6847DD,'8D8CC148250000','8D0CC5',0x00,'LightSet: Slot im neuen 8er-Feld'),
 (0x6A4414,'8DB78C250000','BE',0x44,'D3D9: Licht-aus-Schleife, Basis'),
 (0x6A444B,'83FB04','83FB08',None,'D3D9: Licht-aus-Schleife, 8 Slots'),
 (0x6A456E,'8DB788250000','BE',0x40,'D3D9: SetLight-Schleife, Basis'),
 (0x6A46EC,'83FB04','83FB08',None,'D3D9: SetLight-Schleife, 8 Slots'),
 (0x6A8384,'8DB78C250000','BE',0x44,'D3D9Ex: Licht-aus-Schleife, Basis'),
 (0x6A83BB,'83FB04','83FB08',None,'D3D9Ex: Licht-aus-Schleife, 8 Slots'),
 (0x6A84DE,'8DB788250000','BE',0x40,'D3D9Ex: SetLight-Schleife, Basis'),
 (0x6A865C,'83FB04','83FB08',None,'D3D9Ex: SetLight-Schleife, 8 Slots'),
 (0x695689,'81C68C250000','BE',0x44,'OpenGL: Licht-aus-Schleife, Basis'),
 (0x6956B0,'83FF04','83FF08',None,'OpenGL: Licht-aus-Schleife, 8 Slots'),
 (0x6957A2,'81C688250000','BE',0x40,'OpenGL: Licht-Schleife, Basis'),
 (0x6957A8,'C745F004000000','C745F008000000',None,'OpenGL: Licht-Schleife, 8 Slots'),
 (0x8354E2,'83FF04','83FF08',None,'SetupGxLights: bis Slot 7'),
 (0x835593,'83FF04','83FF08',None,'SetupGxLights: bis Slot 7'),
 (0x8355B3,'83FF04','83FF08',None,'SetupGxLights: Rest bis Slot 7 aus'),
 (0x7A8901,'83FE04','83FE08',None,'Standardlicht (WMO): Slots 1-7 aus'),
 (0x6BC0C9,'83FE04','83FE08',None,'Lichtraster: Rest bis Slot 7 aus'),
 (0x6BC0E1,'83FE04','83FE08',None,'Lichtraster: Rest bis Slot 7 aus'),
]
RESET_VA=0x682C50
RESET_ORIG='B8FF0000006689818C2500006689818E25000033D28991882500008991'
def reset_code(gxva):
    return asm('''mov eax,%#x
L: mov dword ptr [eax],0
mov dword ptr [eax+4],0x00ff00ff
add eax,0x48
cmp eax,%#x
jb L
ret'''%(gxva+0x40,gxva+0x40+8*0x48),RESET_VA)
if __name__=='__main__':
    print('size',hex(len(TPL)),'abs',len(absf),'rel',len(relf),{k:hex(v) for k,v in LAB.items()})
    d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
    for va,orig,new,gxo,c in FF:
        o=va-0x400C00; ob=bytes.fromhex(orig); assert d[o:o+len(ob)]==ob,(hex(va),d[o:o+len(ob)].hex())
        n=bytes.fromhex(new)+(b'' if gxo is None else b'\0'*4)
        if gxo is not None and len(n)<len(ob): n+=b'\x90'*(len(ob)-len(n))
        assert len(n)==len(ob),hex(va)
    print('FF sites ok', len(reset_code(0x1000000)))

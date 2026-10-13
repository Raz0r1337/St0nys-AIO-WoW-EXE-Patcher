# Fixed-function (non-shader) M2 lighting path — WoW 3.3.5a (12340) Wow.exe

Agent "ff". All VAs are image VAs (base 0x400000). "VERIFIED" = read from disassembly; "GUESS" = inference.
Helper files in this folder: `setupgxlights.asm` (annotated listing), `sites.py` (patch-site table, asserts byte lengths with keystone), `disp.py` (displacement scan over the full .text listing).

## TL;DR
* `[0xD43020]` = "M2 uses vertex shaders" flag. 0 = fixed-function (FF) M2 path. Written ONCE at startup (0x872CEA), value = `M2Cache.flags & 8`, and that bit is set only if the Gx caps report VS target > 0 AND PS target > 0 (0x81C164..0x81C193).
* CVar **`fixedFunction`** ("Force fixed function rendering", default "0", registered 0x76AA8B) is the switch: when 1, ConsoleDeviceInitialize (0x76AD3B) sets CGxFormat.maxVSTarget(+0x38) = maxPSTarget(+0x48) = 0, which clamps the device caps VS/PS target to 0 (D3D9 0x68F02E..0x68F050, GL 0x68AD36..0x68AD44) -> M2Cache bit 8 not set -> `[0xD43020]=0`. Works on any modern GPU with gxApi d3d9/d3d9ex/opengl. **Needs a client restart** (not per-frame switchable; no runtime writer of `[0xD43020]`). Note: hwDetect/hwChange path resets the CVar to "0" (0x76A15A, 0x76AD85).
* FF M2 lighting: per M2 **batch** `DrawBatch 0x8203B0 -> 0x81FB10 -> SetLocalLighting 0x873CA0 -> SetupGxLights 0x8353D0(lighting=[CM2Model+0x2A8], offset=NULL)`. Sets GxRs 11 (Lighting) = batch-lit, slot 0 = sun (directional), slots 1..3 = point lights, rest disabled.
* **Bug (VERIFIED)**: SetupGxLights walks CM2Lighting.lights[] from the end (farthest first, AddLight keeps them sorted nearest-first) and stops at slot 4, so with 4 lights the **nearest** light (lights[0]) is dropped in FF mode.
* Gx light slots: 4 x 0x48 bytes at dev+0x2548. Directly behind them (dev+0x2668) is an unrelated array (6 x 0x28 shader hash tables, then master-enable mask dev+0x2758), so the array cannot grow in place, **but** it is addressed in only a handful of places, so redirecting it to an external 8-slot array is a ~22-site patch of same-length instruction rewrites + one 29-byte in-place routine (no code cave needed). D3D9, D3D9Ex and OpenGL can all go to 8 (GL_MAX_LIGHTS >= 8 by spec, DXVK MaxActiveLights = 8).
* D3D9 conversion: per draw, `0x6A43D0` (D3D9) / `0x6A8340` (D3D9Ex) / `0x695640` (GL), only when no vertex shader is bound. D3DLIGHT9 built in a static buffer 0xC606F8 (Ex: 0xC607C0): type POINT(1) if slot.w==1 else DIRECTIONAL(3), Range=10000.0, Falloff=1, Att0/1/2 = slot+0x34/38/3C, Theta=Phi=0; IDirect3DDevice9::LightEnable (vt+0xD4) and SetLight (vt+0xCC).


## 1. When is the FF path used? CVars, `[0xD43020]`

### Flag globals (VERIFIED)
| global | meaning | writer |
|---|---|---|
| `[0xD43020]` | M2 vertex-shader mode (0 = fixed function) | only `0x872CEA` in `M2SetShaderMode 0x872CE0(useVS, usePS)` |
| `[0xD43014]` | M2 pixel-shader mode (= useVS && usePS) | 0x872CF3/0x872CFF, also `0x872AD0(ps)` (hwPCF toggle 0x78E0EE) |
| `[0xD3FCF4]` | CM2Cache (0xD3FCF0)+4 flags; bit 8 = shaders | 0x81C193 `or [esi+4],8` (init), setters 0x81C0C0 (M2 batching console cmds), 0x81C060 (bits 0xE000 only) |

Chain (all VERIFIED):
1. `ClientInitialize 0x4047E0`: `0x4048B8 call 0x402760` builds M2 flags from CVars M2UseZFill(1)/M2UseClipPlanes(2)/M2UseThreads(4)/M2BatchDoodads(0x20)/M2BatchParticles(0x80)/M2ForceAdditiveParticleSort(0x100) and **always** `or eax,8` (0x402904).
2. `0x4048EB call 0x81C6E0 -> 0x81C0D0 CM2Cache::Init(flags)`: guarded by `cmp [esi],0` (runs once). `0x81C164 test bl,8` -> `caps=[dev+0x214]`; `edi=[caps+0xB4]` (vertexShaderTarget, dev+0x2C8), `eax=[caps+0xC4]` (pixelShaderTarget, dev+0x2D8); only if both > 0: `0x81C193 or dword [esi+4],8`.
3. `0x404916 -> 0x404130 -> 0x4041C7 call 0x780F50` (CWorld init): `0x781176 call 0x81C0B0` (returns [0xD3FCF4]); `and eax,8`; `ecx=[0xCD7750]&2` (hwPCF); `0x781189 call 0x872CE0` -> `mov [0xD43020],eax` (0 or 8).

`0x780F50` and `0x81C0D0` run once per process -> **not switchable at runtime**; a gxRestart does not re-run them.

### What drives caps VS/PS target to 0: CVar `fixedFunction`
* Registered `0x76AA75..0x76AA95`: name "fixedFunction", help "Force fixed function rendering", default "0" (0x9E14A0), CVar* stored in `[0xCABBA8]`.
* `ConsoleDeviceInitialize 0x76AB80`, at `0x76AD3B`: `mov edx,[0xCABBA8]; cmp [edx+0x30],ebx(0); je; mov [0xCABD20],0; mov [0xCABD10],0`. 0xCABCD8 is the global CGxFormat; +0x38 = max VS target, +0x48 = max PS target (CGxFormat ctor 0x681950 sets +0x38..+0x4C = -1 = "no clamp").
* D3D9 caps (CGxDeviceD3d, in the device-create function, `ecx`=CGxFormat*): PS target from D3DCAPS9.PixelShaderVersion (0x68EF94..), VS target from VertexShaderVersion (0x68EFE6..), then `0x68F02E mov eax,[ecx+48h]; cmp eax,-1; je; cmp eax,edx; jg; mov [esi+2D8h],eax` and `0x68F040 mov eax,[ecx+38h] ... 0x68F050 mov [esi+2C8h],eax`. With 0 -> both targets 0.
* OpenGL caps: same clamp `0x68ACD0` (+0x48) and `0x68AD36..0x68AD44` (+0x38).
* hwDetect / hwChange path (0x76AD52..0x76AD85, and 0x76A144..0x76A15A) resets `fixedFunction` to "0" and copies the detected format over 0xCABCD8.

So: **`SET fixedFunction "1"` in Config.wtf (or `/console fixedFunction 1` + full client restart) selects the FF M2 path on any GPU, with gxApi d3d9/d3d9ex/opengl.** Side effects (VERIFIED by the same flag): `[0xD43014]=0` -> no pixel shaders anywhere (specular "Requires pixel shaders" 0x78DEA2, hwPCF shadows off, terrain/WMO/particles also take their FF branches: many `cmp [0xD43020],0` sites at 0x7A832E..0x7ACEB1 (WMO), 0x7CBCE2/0x7D7741 (terrain), 0x81F497..0x823902 (M2), 0x836333, 0x872AD9..0x873C20 (M2 shader mgr)).

Readers of `[0xD43020]` (complete list, VERIFIED by grep of the full .text listing): 0x7A832E 0x7A84D0 0x7A8959 0x7A8CE4 0x7A9169 0x7A93BC 0x7A9625 0x7A9917 0x7ACD3D 0x7ACEB1 0x7CBCE2 0x7D7741 0x81F497 0x81F703 0x81FD9D 0x820071 0x820420 0x8205C2 0x820B81 0x823902 0x836333 0x872AD9 0x872B09 0x872C19 0x872D7E 0x872EC4 0x872F96 0x873066 0x873163 0x8731C3 0x873216 0x8733AD 0x8733F9 0x87348C 0x87355C 0x87362C 0x873739 0x873906 0x873A56 0x873C20 0x873CAC 0x873CF9. Single writer 0x872CEA.

Per-frame switching (GUESS): all readers are draw-time checks, so writing `[0xD43020]=0` at runtime (shader -> FF) might work, but the reverse fails when started in FF (vertex shaders are only loaded when the flag is set, e.g. 0x872D7E `cmp [0xD43020],eax; je` skips "Shaders\Vertex" loading). FF skinning/bone path and VS unbinding were not verified -> treat runtime switching as untested.

## 2. SetupGxLights 0x8353D0 (thiscall ecx=CM2Lighting*, arg = C3Vector* offset or NULL; ret 4)

### CGxLight (input struct, 0x40 bytes, ctor 0x683FB0)
| off | field | ctor default |
|---|---|---|
| +00 | flags: bit0 enabled, bit1 point (else directional) | bits 0,1 cleared |
| +04 | vec3 direction / position | (0,0,1) |
| +10 | vec3 ambient | 0 |
| +1C | vec3 diffuse | (1,1,1) |
| +28 | vec3 specular | 0 |
| +34/+38/+3C | attenuation 0/1/2 | 0 / 0.7 (0x9E2EC0) / 0.03 (0x9F23C8) |

### Gx device light slot (dev+0x2548 + i*0x48, i=0..3) — VERIFIED from LightSet 0x6847D0/0x684620, LightEnable 0x683080, LightGet 0x682FD0, reset 0x682C50, D3D/GL consumers
| off | field | dirty bit (word +0x44) |
|---|---|---|
| +00..+0C | vec4 pos/dir; **w = 1.0 point, 0.0 directional** (type is encoded only in w) | 0x02 |
| +10 | vec3 ambient | 0x04 |
| +1C | vec3 diffuse | 0x08 |
| +28 | vec3 specular | 0x10 |
| +34 | attenuation0 | 0x20 |
| +38 | attenuation1 | 0x40 |
| +3C | attenuation2 | 0x80 |
| +40 | dword enabled | 0x01 |
| +44 | word dirty mask | |
| +46 | word "relevant bits" mask: point -> `or 0xE0` (attenuation matters), directional -> `and 0xFF1F` (used by GL only, 0x6957B4) | |

* `CGxDevice::LightSet 0x6847D0 (idx, CGxLight*, C3Vector* offs)`: `lea eax,[idx*9]; lea ecx,[ecx+eax*8+2548h]`; field-wise compare/copy 0x684620 sets dirty bits; if point and offs != 0, pos -= offs (another dirty 2).
* `CGxDevice::LightEnable 0x683080 (idx, bool)`: if changed, `or word [slot+44h],1; mov [slot+40h],en`.
* `CGxDevice::LightGet 0x682FD0 (idx, CGxLight* out)` (only user 0x8A2240).
* `CGxDevice::ResetLights 0x682C50`: 4x unrolled: enable=0, dirty=0xFF, mask=0xFF. Called at device init 0x688EA2, GL 0x695F02, D3D9 reset 0x6A3BFD, D3D9Ex 0x6A7B9D.

### Annotated listing
```
008353D0  55                     push ebp                               ; SetupGxLights(this=CM2Lighting* esi, arg0=C3Vector* offset or NULL)
008353D1  8bec                   mov ebp, esp                           
008353D3  83ec64                 sub esp, 0x64                          
008353D6  53                     push ebx                               
008353D7  56                     push esi                               
008353D8  8bf1                   mov esi, ecx                           
008353DA  57                     push edi                               
008353DB  8d4d9c                 lea ecx, [ebp - 0x64]                  ; L = CGxLight on stack at [ebp-64h] (0x40 bytes) ...
008353DE  e8cdebe4ff             call 0x683fb0                          ; CGxLight::CGxLight 0x683FB0: dir(0,0,1) amb 0 diff 1 spec 0 att(0,0.7,0.03), flags&=~3
008353E3  bf01000000             mov edi, 1                             ; edi = 1 (also next slot index)
008353E8  097d9c                 or dword ptr [ebp - 0x64], edi         ; L.flags |= 1 (enabled)
008353EB  8bce                   mov ecx, esi                           
008353ED  e88efeffff             call 0x835280                          ; CM2Lighting::UpdateSun 0x835280 (once; sets +0x14 bit2): dir->+78h, diffuse->+60h, ambient +54h adjust
008353F2  d9ee                   fldz                                   
008353F4  8b4678                 mov eax, dword ptr [esi + 0x78]        
008353F7  d955f4                 fst dword ptr [ebp - 0xc]              
008353FA  8b4e7c                 mov ecx, dword ptr [esi + 0x7c]        
008353FD  d955f8                 fst dword ptr [ebp - 8]                
00835400  8b9680000000           mov edx, dword ptr [esi + 0x80]        
00835406  d95dfc                 fstp dword ptr [ebp - 4]               
00835409  83659cfd               and dword ptr [ebp - 0x64], 0xfffffffd ; L.flags &= ~2  -> DIRECTIONAL
0083540D  8945a0                 mov dword ptr [ebp - 0x60], eax        ; L.dir = lighting+78h..80h (sun direction)
00835410  8b4654                 mov eax, dword ptr [esi + 0x54]        
00835413  894da4                 mov dword ptr [ebp - 0x5c], ecx        
00835416  8b4e58                 mov ecx, dword ptr [esi + 0x58]        
00835419  8945ac                 mov dword ptr [ebp - 0x54], eax        ; L.ambient(+10h) = lighting+54h..5Ch
0083541C  8b4660                 mov eax, dword ptr [esi + 0x60]        
0083541F  894db0                 mov dword ptr [ebp - 0x50], ecx        
00835422  8b4e64                 mov ecx, dword ptr [esi + 0x64]        
00835425  8945b8                 mov dword ptr [ebp - 0x48], eax        ; L.diffuse(+1Ch) = lighting+60h..68h
00835428  8b466c                 mov eax, dword ptr [esi + 0x6c]        
0083542B  8955a8                 mov dword ptr [ebp - 0x58], edx        
0083542E  8b565c                 mov edx, dword ptr [esi + 0x5c]        
00835431  894dbc                 mov dword ptr [ebp - 0x44], ecx        
00835434  8b4e70                 mov ecx, dword ptr [esi + 0x70]        
00835437  8945c4                 mov dword ptr [ebp - 0x3c], eax        ; L.specular(+28h) = lighting+6Ch..74h
0083543A  8b45f4                 mov eax, dword ptr [ebp - 0xc]         
0083543D  8955b4                 mov dword ptr [ebp - 0x4c], edx        
00835440  8b5668                 mov edx, dword ptr [esi + 0x68]        
00835443  894dc8                 mov dword ptr [ebp - 0x38], ecx        
00835446  8b4df8                 mov ecx, dword ptr [ebp - 8]           
00835449  8945e8                 mov dword ptr [ebp - 0x18], eax        ; zero vector V at [ebp-18h] (3rd arg)
0083544C  8955c0                 mov dword ptr [ebp - 0x40], edx        
0083544F  8b5674                 mov edx, dword ptr [esi + 0x74]        
00835452  894dec                 mov dword ptr [ebp - 0x14], ecx        
00835455  8d45e8                 lea eax, [ebp - 0x18]                  
00835458  50                     push eax                               
00835459  8d4d9c                 lea ecx, [ebp - 0x64]                  
0083545C  51                     push ecx                               
0083545D  8b0d88dfc500           mov ecx, dword ptr [0xc5df88]          
00835463  8955cc                 mov dword ptr [ebp - 0x34], edx        
00835466  8b55fc                 mov edx, dword ptr [ebp - 4]           
00835469  6a00                   push 0                                 
0083546B  8955f0                 mov dword ptr [ebp - 0x10], edx        
0083546E  e85df3e4ff             call 0x6847d0                          ; CGxDevice::LightSet(0, &L, &V)   -> slot 0 (dev+2548h)
00835473  8b0d88dfc500           mov ecx, dword ptr [0xc5df88]          
00835479  57                     push edi                               
0083547A  6a00                   push 0                                 
0083547C  e8ffdbe4ff             call 0x683080                          ; CGxDevice::LightEnable(0, 1)
00835481  d9ee                   fldz                                   
00835483  8b9ea4000000           mov ebx, dword ptr [esi + 0xa4]        ; ebx = lighting->count (+A4h, 0..4)
00835489  d955f4                 fst dword ptr [ebp - 0xc]              
0083548C  8b55f4                 mov edx, dword ptr [ebp - 0xc]         
0083548F  d955f8                 fst dword ptr [ebp - 8]                
00835492  8b45f8                 mov eax, dword ptr [ebp - 8]           
00835495  d955fc                 fst dword ptr [ebp - 4]                
00835498  8b4dfc                 mov ecx, dword ptr [ebp - 4]           
0083549B  d955f4                 fst dword ptr [ebp - 0xc]              
0083549E  834d9c02               or dword ptr [ebp - 0x64], 2           ; L.flags |= 2 -> POINT
008354A2  d955f8                 fst dword ptr [ebp - 8]                
008354A5  85db                   test ebx, ebx                          
008354A7  d955fc                 fst dword ptr [ebp - 4]                
008354AA  8955ac                 mov dword ptr [ebp - 0x54], edx        ; L.ambient = 0
008354AD  8b55f4                 mov edx, dword ptr [ebp - 0xc]         
008354B0  8945b0                 mov dword ptr [ebp - 0x50], eax        
008354B3  8b45f8                 mov eax, dword ptr [ebp - 8]           
008354B6  894db4                 mov dword ptr [ebp - 0x4c], ecx        
008354B9  8b4dfc                 mov ecx, dword ptr [ebp - 4]           
008354BC  8955c4                 mov dword ptr [ebp - 0x3c], edx        ; L.specular = 0
008354BF  8945c8                 mov dword ptr [ebp - 0x38], eax        
008354C2  894dcc                 mov dword ptr [ebp - 0x34], ecx        
008354C5  0f84d5000000           je 0x8355a0                            ; no point lights -> disable slots edi..3
008354CB  8d849e84000000         lea eax, [esi + ebx*4 + 0x84]          ; eax = &lights[count]  (iterate BACKWARDS: farthest first)
008354D2  8b7508                 mov esi, dword ptr [ebp + 8]           ; esi = offset arg
008354D5  eb05                   jmp 0x8354dc                           
008354D7  d9ee                   fldz                                   
008354D9  8b4508                 mov eax, dword ptr [ebp + 8]           
008354DC  83e804                 sub eax, 4                             ; eax -> &lights[ebx-1]
008354DF  83eb01                 sub ebx, 1                             
008354E2  83ff04                 cmp edi, 4                             ; *** slot cap: if edi>=4 stop (with 4 lights lights[0] = NEAREST is dropped)
008354E5  894508                 mov dword ptr [ebp + 8], eax           
008354E8  0f83d3000000           jae 0x8355c1                           
008354EE  85f6                   test esi, esi                          
008354F0  8b00                   mov eax, dword ptr [eax]               ; eax = CM2Light*
008354F2  741f                   je 0x835513                            
008354F4  d9400c                 fld dword ptr [eax + 0xc]              ; pos = light+0Ch - offset (world pos relative)
008354F7  8d4de8                 lea ecx, [ebp - 0x18]                  
008354FA  d826                   fsub dword ptr [esi]                   
008354FC  d95de8                 fstp dword ptr [ebp - 0x18]            
008354FF  d94010                 fld dword ptr [eax + 0x10]             
00835502  d86604                 fsub dword ptr [esi + 4]               
00835505  d95dec                 fstp dword ptr [ebp - 0x14]            
00835508  d94014                 fld dword ptr [eax + 0x14]             
0083550B  d86608                 fsub dword ptr [esi + 8]               
0083550E  d95df0                 fstp dword ptr [ebp - 0x10]            
00835511  eb03                   jmp 0x835516                           
00835513  8d4818                 lea ecx, [eax + 0x18]                  ; offset==NULL: pos = light+18h
00835516  8b11                   mov edx, dword ptr [ecx]               ; L.pos(+4) = pos
00835518  8955a0                 mov dword ptr [ebp - 0x60], edx        
0083551B  8b5104                 mov edx, dword ptr [ecx + 4]           
0083551E  8955a4                 mov dword ptr [ebp - 0x5c], edx        
00835521  8b4908                 mov ecx, dword ptr [ecx + 8]           
00835524  894da8                 mov dword ptr [ebp - 0x58], ecx        
00835527  8b503c                 mov edx, dword ptr [eax + 0x3c]        ; L.diffuse(+1Ch) = light+3Ch..44h
0083552A  8955b8                 mov dword ptr [ebp - 0x48], edx        
0083552D  8b4840                 mov ecx, dword ptr [eax + 0x40]        
00835530  894dbc                 mov dword ptr [ebp - 0x44], ecx        
00835533  8b5044                 mov edx, dword ptr [eax + 0x44]        
00835536  8955c0                 mov dword ptr [ebp - 0x40], edx        
00835539  d94054                 fld dword ptr [eax + 0x54]             ; L.att0/1/2 (+34h/+38h/+3Ch) = light+54h/58h/5Ch
0083553C  d95dd0                 fstp dword ptr [ebp - 0x30]            
0083553F  d94058                 fld dword ptr [eax + 0x58]             
00835542  d95dd4                 fstp dword ptr [ebp - 0x2c]            
00835545  d9405c                 fld dword ptr [eax + 0x5c]             
00835548  d95dd8                 fstp dword ptr [ebp - 0x28]            
0083554B  d955f4                 fst dword ptr [ebp - 0xc]              ; zero vector V2 at [ebp-24h]
0083554E  8b45f4                 mov eax, dword ptr [ebp - 0xc]         
00835551  d955f8                 fst dword ptr [ebp - 8]                
00835554  8b4df8                 mov ecx, dword ptr [ebp - 8]           
00835557  8945dc                 mov dword ptr [ebp - 0x24], eax        
0083555A  d95dfc                 fstp dword ptr [ebp - 4]               
0083555D  8b55fc                 mov edx, dword ptr [ebp - 4]           
00835560  894de0                 mov dword ptr [ebp - 0x20], ecx        
00835563  8d45dc                 lea eax, [ebp - 0x24]                  
00835566  50                     push eax                               
00835567  8d4d9c                 lea ecx, [ebp - 0x64]                  
0083556A  51                     push ecx                               
0083556B  8b0d88dfc500           mov ecx, dword ptr [0xc5df88]          
00835571  57                     push edi                               
00835572  8955e4                 mov dword ptr [ebp - 0x1c], edx        
00835575  e856f2e4ff             call 0x6847d0                          ; CGxDevice::LightSet(edi, &L, &V2)
0083557A  8b0d88dfc500           mov ecx, dword ptr [0xc5df88]          
00835580  6a01                   push 1                                 
00835582  57                     push edi                               
00835583  e8f8dae4ff             call 0x683080                          ; CGxDevice::LightEnable(edi, 1)
00835588  83c701                 add edi, 1                             ; edi++
0083558B  85db                   test ebx, ebx                          
0083558D  0f8544ffffff           jne 0x8354d7                           
00835593  83ff04                 cmp edi, 4                             ; *** if edi>=4 return
00835596  732b                   jae 0x8355c3                           
00835598  eb08                   jmp 0x8355a2                           
0083559A  8d9b00000000           lea ebx, [ebx]                         
008355A0  ddd8                   fstp st(0)                             
008355A2  8b0d88dfc500           mov ecx, dword ptr [0xc5df88]          ; disable loop: LightEnable(edi,0) for edi..3
008355A8  6a00                   push 0                                 
008355AA  57                     push edi                               
008355AB  e8d0dae4ff             call 0x683080                          
008355B0  83c701                 add edi, 1                             
008355B3  83ff04                 cmp edi, 4                             ; *** cmp edi,4
008355B6  72ea                   jb 0x8355a2                            
008355B8  5f                     pop edi                                
008355B9  5e                     pop esi                                
008355BA  5b                     pop ebx                                
008355BB  8be5                   mov esp, ebp                           
008355BD  5d                     pop ebp                                
008355BE  c20400                 ret 4                                  
008355C1  ddd8                   fstp st(0)                             
008355C3  5f                     pop edi                                
008355C4  5e                     pop esi                                
008355C5  5b                     pop ebx                                
008355C6  8be5                   mov esp, ebp                           
008355C8  5d                     pop ebp                                
008355C9  c20400                 ret 4                                  
```

CM2Light fields used (VERIFIED from this function, AddLight 0x834F60 and 0x834B50): +08 type (1 = point; AddLight only keeps type 1, other types are accumulated into the sun/ambient), +0C world position, +18 alternate position (used when offset==NULL — this is the M2 batch case), +3C diffuse colour, +54/+58/+5C attenuation triple (copied verbatim to D3D Attenuation0/1/2; GUESS: precomputed FF coefficients), +60 enabled.
CM2Lighting fields: +54 ambient, +60 sun diffuse, +6C sun specular(?), +78 sun direction, +84 lights[4], +94 dist2[4] (sorted ascending, nearest first — AddLight 0x834F60 insertion sort, `cmp esi,4` 0x834FA9/0x834FCD, `cmp eax,4` 0x83502C), +A0 = dist2[3], +A4 count.

Result: slot0 = sun (directional, ambient+diffuse+specular), slots 1..min(count,3) = point lights (diffuse only, ambient/spec 0) in order farthest..nearest, remaining slots up to 3 disabled. With count==4, lights[0] (nearest) is never set — FF shows only the 3 farthest of the 4 (VERIFIED by tracing the loop: ebx=4 -> idx3,2,1 then `cmp edi,4; jae 0x8355C1` before idx0).

## 3. Gx -> API

Called per draw in the pre-draw state flush (D3D9 `0x6A5940`: `0x6A5973 call 0x6A43D0` — skipped when a vertex shader is bound (rs 77 test at 0x6A595E..0x6A596F)); D3D9Ex flush `0x6A9893 call 0x6A8340`; GL `0x69D57B call 0x695640`.

### D3D9 `CGxDeviceD3d::ISyncLights 0x6A43D0` (edi = dev)
* `rs = [dev+0x28F4]`; `[rs+0x108]` = GxRs 11 **Lighting** (stride 0x18).
* Lighting == 0:
  * if `!(dev+0x28A8 & 0x10)` and `[rs+0x18] != -1`: once (`[dev+0x3B2C]` latch) loop `0x6A4414 lea esi,[edi+258Ch]` ... `LightEnable(i,0)` (vt+0xD4), re-mark bit0 dirty for enabled slots, `0x6A444B cmp ebx,4`; then D3DRS_LIGHTING(0x89)=1 and D3DRS_AMBIENT(0x8B)=0xFFFFFFFF (unlit-but-material trick).
  * else D3DRS_LIGHTING=0, AMBIENT=0.
* Lighting != 0 (`0x6A451B`): D3DRS_LIGHTING = `[dev+0x2758] & 1` (master-enable mask, default 0x1FF at 0x688EAC, query 0x683100); AMBIENT=0; then loop `0x6A456E lea esi,[edi+2588h]` (esi -> slot+0x40):
  * `dirty = word [esi+4]`; 0 -> skip.
  * dirty&1: enabled -> `LightEnable(i,1)` then SetLight; disabled -> clear bit0, `LightEnable(i,0)`, skip.
  * else if enabled -> SetLight.
  * SetLight: `fld1; fcom [esi-34h]` (w): ==1 -> `Type=1 POINT`, Position = slot+0..8 (0xC6072C); else `Type=3 DIRECTIONAL`, Direction = slot+0..8 (0xC60738). Diffuse.rgb = slot+1C, a=1 (0xC606FC); Specular.rgb = slot+28, a=0 (0xC6070C); Ambient.rgb = slot+10, a=0 (0xC6071C); **Range = 10000.0** ([0xA2F95C]) -> 0xC60744; **Falloff = 1.0** -> 0xC60748; **Attenuation0/1/2 = slot+34/38/3C** -> 0xC6074C/50/54; Theta/Phi never written (0). `IDirect3DDevice9::SetLight(i, &0xC606F8)` (vt+0xCC, 0x6A46CF). Then dirty word = 0.
  * `0x6A46EC cmp ebx,4; jb`.
* Material colours are taken via D3DRS_*MATERIALSOURCE (0x93/0x91/0x92/0x94 at 0x6A4700..) and SetMaterial (vt+0xC4 at 0x6A438E).

### D3D9Ex `0x6A8340` (vtable 0xA2F500 device class)
Instruction-for-instruction identical to 0x6A43D0 (39 differing operands only: shadow RS cache +0x3EFC/+0x3EE0 instead of +0x3E78/+0x3E5C, D3DLIGHT9 buffer 0xC607C0, Range const 0xA2FB60 = 10000.0). Same slot base: `0x6A8384 lea esi,[edi+258Ch]`, `0x6A83BB cmp ebx,4`, `0x6A84DE lea esi,[edi+2588h]`, `0x6A865C cmp ebx,4`.

### OpenGL `CGxDeviceOpenGl::ISyncLights 0x695640`
Same logic with glEnable/glDisable(GL_LIGHTING 0xB50), glLightModelfv(GL_LIGHT_MODEL_AMBIENT 0xB53), glEnable/glDisable(GL_LIGHT0+i = 0x4000+i), glLightfv/glLightf (GL_POSITION 0x1203 with w, directional = negated, GL_*_ATTENUATION 0x1207..0x1209, GL_AMBIENT/DIFFUSE/SPECULAR 0x1200..0x1202). Dirty = `word[+44] & word[+46] & specMask | (2 if view matrix changed)`. Loops: `0x695689 add esi,258Ch` + `0x6956B0 cmp edi,4`; `0x6957A2 add esi,2588h` + `0x6957A8 mov [ebp-10h],4` (dev kept in [ebp-14h]). GL guarantees >= 8 lights, so GL can go to 8 as easily as D3D.

## 4. What follows the slots, all accesses, redirect plan

* dev+0x2668: array of 6 x 0x28 (`lea edi,[ecx+eax*8+2668h]` with eax=type*5 at 0x68783D/0x6897E4/0x68988C; init loop 0x688B45) = per-shader-type CGxShader hash tables; dev+0x2758 = master-enable mask; dev+0x2788.. stream objects. -> no room to grow in place.
* **Every access to dev+0x2548..dev+0x2667 in .text** (scan of all displacements 0x2548..0x2677 over the whole .text listing, `disp.py`; non-device hits filtered: 0x4B368F/0x4B3815 imul imm, 0x8992E6/0x8992F7/0x899814 stack, 0x8E88A4, 0x8F45FF.., 0x9293AF other objects):
  * 0x682C55..0x682CA0 ResetLights (12 stores, unrolled 4 slots)
  * 0x682FD9 LightGet, 0x683089 LightEnable, 0x6847DD LightSet (indexed `lea r,[ecx+eax*8+2548h]`)
  * 0x688B21..0x688CAE CGxDevice ctor zero-fills the slot floats (writes only)
  * GL 0x695689, 0x6957A2; D3D9 0x6A4414, 0x6A456E; D3D9Ex 0x6A8384, 0x6A84DE (loop base pointers, stride `add esi,48h`)
  * (0x2668..0x2677 hits 0x68783D/0x688B45/0x6897E4/0x68988C/0x69FA0E/0x69FA68/0x6A5E99/0x6A5ECE belong to the shader tables.)
* Users of slot indices with a hard-coded 4 (outside Gx): SetupGxLights 0x8354E2/0x835593/0x8355B3; default-light setup 0x7A8800 (slot 0 + disable 1..3, `0x7A8901 cmp esi,4`, used by WMO code 0x7AA3DA..0x7AB500); light grid 0x6BBF40 (disables rest, `0x6BC0C9`/`0x6BC0E1 cmp esi,4`); save/restore 0x8A2240 (4 slots on stack, `0x8A228A`/`0x8A2369 cmp esi,4`, 0x100-byte stack array); 0x834B50 CM2Light::SetGxLight(idx) only called with idx 0 (0x7A8E61).

### Redirect to an external 8-slot array (1 sun + 7 points) — all same-length rewrites (bytes generated & length-checked by `sites.py`, EXT = example 0x00E00000, a zero-initialised 8*0x48 = 0x240-byte block in a new section)
| site | VA | file off | original bytes | original | new bytes | new |
|---|---|---|---|---|---|---|
| LightGet 0x682FD0 | 00682FD9 | 2823D9 | 8D 94 C1 48 25 00 00 | `lea edx, [ecx + eax*8 + 0x2548]` | 8D 14 C5 00 00 E0 00 | `lea edx,[eax*8+0xe00000]` |
| LightEnable 0x683080 | 00683089 | 282489 | 8D 84 C1 48 25 00 00 | `lea eax, [ecx + eax*8 + 0x2548]` | 8D 04 C5 00 00 E0 00 | `lea eax,[eax*8+0xe00000]` |
| LightSet 0x6847D0 | 006847DD | 283BDD | 8D 8C C1 48 25 00 00 | `lea ecx, [ecx + eax*8 + 0x2548]` | 8D 0C C5 00 00 E0 00 | `lea ecx,[eax*8+0xe00000]` |
| D3D9 disable loop ptr | 006A4414 | 2A3814 | 8D B7 8C 25 00 00 | `lea esi, [edi + 0x258c]` | BE 44 00 E0 00 90 | `mov esi,0xe00044; nop` |
| D3D9 disable loop cnt | 006A444B | 2A384B | 83 FB 04 | `cmp ebx, 4` | 83 FB 08 | `cmp ebx,8` |
| D3D9 SetLight loop ptr | 006A456E | 2A396E | 8D B7 88 25 00 00 | `lea esi, [edi + 0x2588]` | BE 40 00 E0 00 90 | `mov esi,0xe00040; nop` |
| D3D9 SetLight loop cnt | 006A46EC | 2A3AEC | 83 FB 04 | `cmp ebx, 4` | 83 FB 08 | `cmp ebx,8` |
| D3D9Ex disable loop ptr | 006A8384 | 2A7784 | 8D B7 8C 25 00 00 | `lea esi, [edi + 0x258c]` | BE 44 00 E0 00 90 | `mov esi,0xe00044; nop` |
| D3D9Ex disable loop cnt | 006A83BB | 2A77BB | 83 FB 04 | `cmp ebx, 4` | 83 FB 08 | `cmp ebx,8` |
| D3D9Ex SetLight loop ptr | 006A84DE | 2A78DE | 8D B7 88 25 00 00 | `lea esi, [edi + 0x2588]` | BE 40 00 E0 00 90 | `mov esi,0xe00040; nop` |
| D3D9Ex SetLight loop cnt | 006A865C | 2A7A5C | 83 FB 04 | `cmp ebx, 4` | 83 FB 08 | `cmp ebx,8` |
| GL disable loop ptr | 00695689 | 294A89 | 81 C6 8C 25 00 00 | `add esi, 0x258c` | BE 44 00 E0 00 90 | `mov esi,0xe00044; nop` |
| GL disable loop cnt | 006956B0 | 294AB0 | 83 FF 04 | `cmp edi, 4` | 83 FF 08 | `cmp edi,8` |
| GL light loop ptr | 006957A2 | 294BA2 | 81 C6 88 25 00 00 | `add esi, 0x2588` | BE 40 00 E0 00 90 | `mov esi,0xe00040; nop` |
| GL light loop cnt | 006957A8 | 294BA8 | C7 45 F0 04 00 00 00 | `mov dword ptr [ebp - 0x10], 4` | C7 45 F0 08 00 00 00 | `mov dword ptr [ebp-0x10],8` |
| SetupGxLights cap | 008354E2 | 4348E2 | 83 FF 04 | `cmp edi, 4` | 83 FF 08 | `cmp edi,8` |
| SetupGxLights cap2 | 00835593 | 434993 | 83 FF 04 | `cmp edi, 4` | 83 FF 08 | `cmp edi,8` |
| SetupGxLights disable rest | 008355B3 | 4349B3 | 83 FF 04 | `cmp edi, 4` | 83 FF 08 | `cmp edi,8` |
| DefaultLight 0x7A8800 disable 1..3 | 007A8901 | 3A7D01 | 83 FE 04 | `cmp esi, 4` | 83 FE 08 | `cmp esi,8` |
| LightGrid 0x6BBF40 disable rest a | 006BC0C9 | 2BB4C9 | 83 FE 04 | `cmp esi, 4` | 83 FE 08 | `cmp esi,8` |
| LightGrid 0x6BBF40 disable rest b | 006BC0E1 | 2BB4E1 | 83 FE 04 | `cmp esi, 4` | 83 FE 08 | `cmp esi,8` |

Reset 0x682C50 replacement (29 bytes, original body 0x58 bytes up to ret at 0x682CA7): B8 40 00 E0 00 C7 00 00 00 00 00 C7 40 04 FF 00 FF 00 83 C0 48 3D 80 02 E0 00 72 E9 C3
  00682C50 mov eax, 0xe00040
  00682C55 mov dword ptr [eax], 0
  00682C5B mov dword ptr [eax + 4], 0xff00ff
  00682C62 add eax, 0x48
  00682C65 cmp eax, 0xe00280
  00682C6A jb 0x682c55
  00682C6C ret 

Notes on the plan:
* The three Gx accessors already compute `eax = idx*9`, so `lea r,[eax*8+EXT]` (7 bytes, same as original) gives EXT + idx*0x48 — no cave needed.
* ResetLights 0x682C50 is rewritten in place (29 bytes < original 0x58): loop over 8 slots writing enable=0 and dword 0x00FF00FF to +0x44 (dirty=0xFF, mask=0xFF). Only eax clobbered (original clobbers eax/edx).
* Device ctor zero-fill (0x688B21..) can stay (it writes the now-unused device slots); EXT is .bss-zero and ResetLights runs at every device init/reset, so a recreated device fully re-sends all lights.
* D3D/GL loops: `lea/add esi,...` -> `mov esi,EXT+0x44 / EXT+0x40; nop`; after those loops the code only uses edi (D3D) or [ebp-14h] (GL) as the device pointer (VERIFIED: 0x6A4455.., 0x6A4549.., 0x69580A, 0x69594D).
* SetupGxLights `cmp edi,4` x3 -> 8: with the unchanged 4-light CM2Lighting this alone renders **all 4** point lights in FF (fixes the nearest-light drop) and disables slots 5..7.
* For 7 point lights, CM2Lighting must hold 7 (it has fixed arrays +0x84[4] / +0x94[4] / count +0xA4 and AddLight caps at 4 — other agents' scope). SetupGxLights reads only `0x835483 mov ebx,[esi+0A4h]` (8B 9E A4 00 00 00) and `0x8354CB lea eax,[esi+ebx*4+84h]` (8D 84 9E 84 00 00 00); these two would follow a relocated light list.
* Must also widen the "disable remaining" loops of other light users (0x7A8901, 0x6BC0C9, 0x6BC0E1), otherwise slots 4..7 left on by an M2 batch leak into WMO/other FF draws. 0x8A2240 save/restore can stay at 4 (its restore only re-enables, never disables; slots 4..7 are rewritten by the next SetupGxLights anyway) — optional: grow its 0x100-byte stack array.
* D3D9 limit: LightEnable on index >= D3DCAPS9.MaxActiveLights fails; 8 is the common value (DXVK = 8). The engine does not appear to query MaxActiveLights (GUESS, not exhaustively checked) — keep total at 8.
* OpenGL: included above (4 sites); trivial.

## 5. Is lighting really on for M2 in FF mode, and is it per model?

* `SetLocalLighting 0x873CA0(CM2Lighting* L, int lit, C3Vector* offs)`:
  * FF (`[0xD43020]==0`): `0x873CC0..0x873CE0` inline GxRsSet(11 = Lighting, lit) (`[rs+0x108]`, dirty via 0x685970), then `0x873EBD test edi,edi; je; 0x873EC7 call SetupGxLights(offs)`.
  * VS mode: uploads c10/c11/c12 (sun dir/ambient/diffuse at 0xD43028..0xD43048) + c17..c27 local lights (0x872900) instead.
* `lit` comes from `0x81FB10` (called from `DrawBatch 0x8203B0` at 0x82040D, and the other batch types 0x820720/0x820AE0/0x820F40/0x821040/0x8214E0/0x823070): `lit = !(renderFlags.flags & 1 /*unlit*/) && table0xA45374[renderFlags.blend]`; `L = [ctx+0x70]` = `[CM2Model+0x2A8]` (set at 0x823A26/0x823A51 per scene element), offs = NULL.
* So yes: in FF mode D3DRS_LIGHTING is enabled (GxRs 11 = 1 -> 0x6A451B: D3DRS_LIGHTING = master bit0 = 1), and the light list is rebuilt **per batch** (per draw call) from the model's own CM2Lighting; redundant calls are cheap because LightSet only marks changed fields dirty and the API sync only sends dirty slots.
* Other SetupGxLights callers (all with a stack CM2Lighting filled from the world scene 0x81E400 and offset 0xCD8F5C): 0x798606 (in 0x7984A0), 0x7A91E4 (0x7A9160, WMO), 0x7D0590 (0x7D04A0, terrain/map), 0x8A532C/0x8A5E2A/0x8A644D (callback table 0xA594C0..). 

## Verified vs. guessed summary
VERIFIED: flag chain & writers/readers of 0xD43020, fixedFunction -> format clamp -> caps -> M2Cache bit 8; SetupGxLights logic incl. dropped nearest light; slot layout & dirty bits; D3D9/D3D9Ex/GL sync code & D3DLIGHT9 fields; full access list of dev+0x2548..0x2667; patch-site bytes (assembled + length-checked); per-batch call chain.
GUESS: semantic of CM2Light +0x54..+0x5C as FF attenuation coefficients; runtime switching shader->FF; no MaxActiveLights query; names of 0x7984A0/0x8A5170 subsystems. Not run in-game.

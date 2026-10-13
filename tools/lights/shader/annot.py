import capstone,sys
from ex import *
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
C={
0x873CA0:'SetLocalLighting(CM2Lighting* L, int lit, C3Vector* origin)  cdecl',
0x873CAC:'[0xD43020] = M2 vertex-shader path enabled (set by 0x872CE0)',
0x873CB8:'g_curLit [0xD4301C] = lit  (VS index bit 0)',
0x873CBE:'shader path -> skip FF renderstate',
0x873CC0:'FF only: GxRs LIGHTING (rs index 0x108/4) = lit',
0x873CEF:'count = L->count(+0xA4)  (0 if L==NULL)  ** patch site: clamp to 4 **',
0x873D00:'g_curLightCount [0xD43018] = count (used by VS index 0x873160 and below)',
0x873D05:'FF path -> 0x873EBD (SetupGxLights 0x8353D0)',
0x873D0B:'unlit -> return (no constants)',
0x873D13:'sun dir = L+0x78/+0x7C/+0x80 -> 0xD43040.. (c12)',
0x873D50:'if dir != (0,0,0): normalize (0x873DB0..0x873DE2)',
0x873D6E:'c11 = L+0x54/58/5C (sun diffuse colour; FF path uses it as light-0 colour at 0x835410)',
0x873D88:'ambient = L+0x60/64/68 -> each min(x,1.0) -> c10 (0xD43028..30)',
0x873E1A:'GxShaderConstantsSet(VS, c10, 0xD43028, 1)  (w = c11.x, buffers overlap)',
0x873E43:'GxShaderConstantsSet(VS, c11, 0xD43034, 1)  (w = c12.x)',
0x873E5E:'GxShaderConstantsSet(VS, c12, 0xD43040, 1)  (w = [0xD4304C], stale)',
0x873E6B:'if count==0 skip point lights (c17..c27 NOT re-uploaded)',
0x873E74:'ComputeLocalLights(0xD43098, count, &L->lights[0] (+0x84), origin)',
0x873E85:'** patch site A: call 0x872900 (E8 76 EA FF FF) **',
0x873E9B:'GxShaderConstantsSet(VS, c17, 0xD43098, 11)',
0x873EA8:'shadow PS consts: 0x8745D0(L->flags(+0x14) & 8)',
0x873EBD:'FF path: if lit -> CM2Lighting::SetupGxLights(ecx=L, origin) 0x8353D0',
0x872900:'ComputeLocalLights(float out[44], uint n, CM2Light** lights, C3Vector* origin) cdecl',
0x87291A:'identity 4x4 at [ebp-0x80]',
0x872951:'if origin: M = device xform stack top  dev+0x1B00+[dev+0x1AF8]*64 (copy 0x407F80)',
0x872979:'st0=0.0, st1=1.0',
0x872982:'edi = out+0x48 (+16/light) , ecx=[ebp-4] = out+0x90 (+4/light)',
0x872991:'loop i: esi = lights[i]',
0x872997:'light->type(+8) != 1 (not point) -> colour = 0, pos/att NOT written',
0x8729AE:'out[4i+0..2] = light+0x3C/40/44 (colour)  -> c17+i',
0x8729D9:'out[4i+3] = 1.0  (colour.w)',
0x8729DE:'origin != 0: pos = (light+0x0C..0x14 - origin) * M  (0x4C21B0)',
0x872A3C:'origin == 0 (M2 path): pos = light+0x18..0x20',
0x872A4E:'out[16+4i+0..2] = pos, out[16+4i+3] = 1.0  -> c21+i',
0x872A62:'out[32+i] = light+0x54 (c25.comp i), out[36+i]=+0x58 (c26.i), out[40+i]=+0x5C (c27.i)',
0x872A75:'i++ ; while i < n   (NO upper bound: n>4 overflows the 44-float buffer)',
0x872A8A:'if i<4: zero colour regs c17+i..c20 (pos/att of unused slots left stale)',
0x6833E0:'CGxDevice::ShaderConstantsSet(target, reg, const float* v4, count)  vtbl+0x118, thiscall, ret 0x10',
0x6833F0:'target==0 -> VS cache 0xC5EFE8+reg*16 ; else PS cache 0xC5DFE0+reg*16',
0x683410:'per register: compare 4 floats with cache; copy changed ones',
0x68346F:'changed -> VS dirty min [0xC5FFEC] = min(.., reg); dirty max [0xC5FFE8] = max(.., reg)',
0x6834A4:'PS: dirty min [0xC5EFE4], max [0xC5EFE0]',
0x6A9FE0:'CGxDeviceD3d flush of shader constants (called from 0x6A5940 before every DIP)',
0x6A9FF3:'if min<=max: IDirect3DDevice9::SetVertexShaderConstantF(min, &cacheVS[min], max-min+1) [vt+0x178]',
0x6AA016:'reset VS dirty: min=0xFF, max=0',
0x6AA037:'PS: SetPixelShaderConstantF(min, &cachePS[min], max-min+1) [vt+0x1B4]; reset',
}
def dis(va,end):
    o=off(va)
    for i in md.disasm(d[o:o+(end-va)],va):
        c=C.get(i.address,'')
        print('%08X  %-22s %-38s %s'%(i.address,i.bytes.hex(' '),(i.mnemonic+' '+i.op_str)[:38],('; '+c) if c else ''))
for a,b in ((0x873CA0,0x873ED2),(0x872900,0x872AC5),(0x6833E0,0x6834A4),(0x6A9FE0,0x6AA06D)):
    dis(a,b); print()

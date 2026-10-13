import capstone
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
C={
0x8353D0:'SetupGxLights(this=CM2Lighting* esi, arg0=C3Vector* offset or NULL)',
0x8353DB:'L = CGxLight on stack at [ebp-64h] (0x40 bytes) ...',
0x8353DE:'CGxLight::CGxLight 0x683FB0: dir(0,0,1) amb 0 diff 1 spec 0 att(0,0.7,0.03), flags&=~3',
0x8353E3:'edi = 1 (also next slot index)',
0x8353E8:'L.flags |= 1 (enabled)',
0x8353ED:'CM2Lighting::UpdateSun 0x835280 (once; sets +0x14 bit2): dir->+78h, diffuse->+60h, ambient +54h adjust',
0x835409:'L.flags &= ~2  -> DIRECTIONAL',
0x83540D:'L.dir = lighting+78h..80h (sun direction)',
0x835419:'L.ambient(+10h) = lighting+54h..5Ch',
0x835425:'L.diffuse(+1Ch) = lighting+60h..68h',
0x835437:'L.specular(+28h) = lighting+6Ch..74h',
0x835449:'zero vector V at [ebp-18h] (3rd arg)',
0x83546E:'CGxDevice::LightSet(0, &L, &V)   -> slot 0 (dev+2548h)',
0x83547C:'CGxDevice::LightEnable(0, 1)',
0x835483:'ebx = lighting->count (+A4h, 0..4)',
0x83549E:'L.flags |= 2 -> POINT',
0x8354AA:'L.ambient = 0',
0x8354BC:'L.specular = 0',
0x8354C5:'no point lights -> disable slots edi..3',
0x8354CB:'eax = &lights[count]  (iterate BACKWARDS: farthest first)',
0x8354D2:'esi = offset arg',
0x8354DC:'eax -> &lights[ebx-1]',
0x8354E2:'*** slot cap: if edi>=4 stop (with 4 lights lights[0] = NEAREST is dropped)',
0x8354F0:'eax = CM2Light*',
0x8354F4:'pos = light+0Ch - offset (world pos relative)',
0x835513:'offset==NULL: pos = light+18h',
0x835516:'L.pos(+4) = pos',
0x835527:'L.diffuse(+1Ch) = light+3Ch..44h',
0x835539:'L.att0/1/2 (+34h/+38h/+3Ch) = light+54h/58h/5Ch',
0x83554B:'zero vector V2 at [ebp-24h]',
0x835575:'CGxDevice::LightSet(edi, &L, &V2)',
0x835583:'CGxDevice::LightEnable(edi, 1)',
0x835588:'edi++',
0x835593:'*** if edi>=4 return',
0x8355A2:'disable loop: LightEnable(edi,0) for edi..3',
0x8355B3:'*** cmp edi,4',
}
o=0x8353D0-0x400C00
for i in md.disasm(d[o:o+0x1FC],0x8353D0):
    c=C.get(i.address,'')
    print('%08X  %-22s %-38s %s'%(i.address,i.bytes.hex(),i.mnemonic+' '+i.op_str,('; '+c) if c else ''))

import struct,re,bisect
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
t=lambda va: va-0x400C00
L=[l.rstrip('\n').split(' ',2) for l in open('text.asm')]
addrs=[int(x[0],16) for x in L]
idx=d[t(0x6a5444):t(0x6a5444)+0x55]
ncase=max(idx)+1
tbl=[struct.unpack_from('<I',d,t(0x6a53c8)+4*i)[0] for i in range(ncase)]
names={0xe4:'SetRenderState',0x10c:'SetTextureStageState',0x114:'SetSamplerState',0x104:'SetTexture',0xc4:'SetMaterial',0xdc:'SetClipPlane',0x170:'SetVertexShader',0x1ac:'SetPixelShader',0xb0:'SetTransform',0x15c:'SetVertexDeclaration',0x164:'SetFVF',0x12c:'SetScissorRect',0xd4:'LightEnable',0xcc:'SetLight'}
starts=sorted(set(tbl))
def summarize(a):
    i=bisect.bisect_left(addrs,a); out=[]; pushes=[]
    n=0
    while n<120:
        x=L[i]; mn=x[1]; ops=x[2] if len(x)>2 else ''
        if mn=='push': pushes.append(ops)
        m=re.search(r'\+ (0x[0-9a-f]+)\]',ops)
        if mn=='mov' and m and int(m.group(1),16) in names and ops.split(',')[0].strip() in ('eax','ebx','ecx','edx','esi','edi'):
            out.append(names[int(m.group(1),16)])
        if mn=='call' and not ops.startswith('0x'):
            out.append('  args(rev)='+','.join(pushes[-4:]))
            pushes=[]
        elif mn=='call':
            out.append('call '+ops); pushes=[]
        if mn=='jmp' and ops=='0x6a53bf': break
        if mn in('ret',): break
        if mn=='jmp': out.append('jmp '+ops); break
        i+=1; n+=1
    return ' '.join(out)
for s in range(0x55):
    c=idx[s]; a=tbl[c]
    print('rs %2d (0x%02X) case %2d -> %08X : %s'%(s,s,c,a,summarize(a) if a!=0x6a53bf else 'default/no-op'))

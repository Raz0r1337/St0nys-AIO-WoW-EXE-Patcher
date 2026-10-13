# crude register-tracking scan for IDirect3DDevice9 method calls via [X+0x397c]
import re,sys,collections
REGS=['eax','ebx','ecx','edx','esi','edi','ebp']
names={0x0:'QueryInterface',0x4:'AddRef',0x8:'Release',0xC:'TestCooperativeLevel',0x10:'GetAvailableTextureMem',0x14:'EvictManagedResources',0x18:'GetDirect3D',0x1C:'GetDeviceCaps',0x20:'GetDisplayMode',0x24:'GetCreationParameters',0x28:'SetCursorProperties',0x2C:'SetCursorPosition',0x30:'ShowCursor',0x34:'CreateAdditionalSwapChain',0x38:'GetSwapChain',0x3C:'GetNumberOfSwapChains',0x40:'Reset',0x44:'Present',0x48:'GetBackBuffer',0x4C:'GetRasterStatus',0x50:'SetDialogBoxMode',0x54:'SetGammaRamp',0x58:'GetGammaRamp',0x5C:'CreateTexture',0x60:'CreateVolumeTexture',0x64:'CreateCubeTexture',0x68:'CreateVertexBuffer',0x6C:'CreateIndexBuffer',0x70:'CreateRenderTarget',0x74:'CreateDepthStencilSurface',0x78:'UpdateSurface',0x7C:'UpdateTexture',0x80:'GetRenderTargetData',0x84:'GetFrontBufferData',0x88:'StretchRect',0x8C:'ColorFill',0x90:'CreateOffscreenPlainSurface',0x94:'SetRenderTarget',0x98:'GetRenderTarget',0x9C:'SetDepthStencilSurface',0xA0:'GetDepthStencilSurface',0xA4:'BeginScene',0xA8:'EndScene',0xAC:'Clear',0xB0:'SetTransform',0xB4:'GetTransform',0xB8:'MultiplyTransform',0xBC:'SetViewport',0xC0:'GetViewport',0xC4:'SetMaterial',0xC8:'GetMaterial',0xCC:'SetLight',0xD0:'GetLight',0xD4:'LightEnable',0xD8:'GetLightEnable',0xDC:'SetClipPlane',0xE0:'GetClipPlane',0xE4:'SetRenderState',0xE8:'GetRenderState',0xEC:'CreateStateBlock',0xF0:'BeginStateBlock',0xF4:'EndStateBlock',0xF8:'SetClipStatus',0xFC:'GetClipStatus',0x100:'GetTexture',0x104:'SetTexture',0x108:'GetTextureStageState',0x10C:'SetTextureStageState',0x110:'GetSamplerState',0x114:'SetSamplerState',0x118:'ValidateDevice',0x11C:'SetPaletteEntries',0x120:'GetPaletteEntries',0x124:'SetCurrentTexturePalette',0x128:'GetCurrentTexturePalette',0x12C:'SetScissorRect',0x130:'GetScissorRect',0x134:'SetSoftwareVertexProcessing',0x138:'GetSoftwareVertexProcessing',0x13C:'SetNPatchMode',0x140:'GetNPatchMode',0x144:'DrawPrimitive',0x148:'DrawIndexedPrimitive',0x14C:'DrawPrimitiveUP',0x150:'DrawIndexedPrimitiveUP',0x154:'ProcessVertices',0x158:'CreateVertexDeclaration',0x15C:'SetVertexDeclaration',0x160:'GetVertexDeclaration',0x164:'SetFVF',0x168:'GetFVF',0x16C:'CreateVertexShader',0x170:'SetVertexShader',0x174:'GetVertexShader',0x178:'SetVertexShaderConstantF',0x17C:'GetVertexShaderConstantF',0x180:'SetVertexShaderConstantI',0x184:'GetVertexShaderConstantI',0x188:'SetVertexShaderConstantB',0x18C:'GetVertexShaderConstantB',0x190:'SetStreamSource',0x194:'GetStreamSource',0x198:'SetStreamSourceFreq',0x19C:'GetStreamSourceFreq',0x1A0:'SetIndices',0x1A4:'GetIndices',0x1A8:'CreatePixelShader',0x1AC:'SetPixelShader',0x1B0:'GetPixelShader',0x1B4:'SetPixelShaderConstantF',0x1B8:'GetPixelShaderConstantF',0x1BC:'SetPixelShaderConstantI',0x1C0:'GetPixelShaderConstantI',0x1C4:'SetPixelShaderConstantB',0x1C8:'GetPixelShaderConstantB',0x1CC:'DrawRectPatch',0x1D0:'DrawTriPatch',0x1D4:'DeletePatch',0x1D8:'CreateQuery'}
lines=[l.rstrip('\n').split(' ',2) for l in open('text.asm')]
st={}
hits=[]
lastpush=collections.deque(maxlen=8)
def parse_mem(s):
    m=re.match(r'dword ptr \[(\w+)(?: \+ (0x[0-9a-f]+|\d+))?\]$',s.strip())
    if m: return m.group(1), int(m.group(2),0) if m.group(2) else 0
    return None
for parts in lines:
    if len(parts)<2: continue
    a=parts[0]; mn=parts[1]; ops=parts[2] if len(parts)>2 else ''
    if mn in ('ret','jmp','int3'):
        st={}; lastpush.clear(); continue
    if mn=='push':
        lastpush.appendleft(ops); continue
    if mn=='call':
        r=None
        if ops in REGS and st.get(ops,('',))[0]=='fn': r=st[ops][1]
        m=parse_mem(ops)
        if m and st.get(m[0],('',))[0]=='vt': r=m[1]
        if r is not None:
            hits.append((a,r,list(lastpush)))
        for k in ('eax','ecx','edx'): st.pop(k,None)
        lastpush.clear()
        continue
    if mn in ('mov','lea') and ',' in ops:
        dst,src=[x.strip() for x in ops.split(',',1)]
        if dst in REGS:
            m=parse_mem(src)
            newst=None
            if mn=='mov' and m:
                base,off=m
                if off==0x3978 and base!='ebp': newst=('dev',)
                elif off==0 and st.get(base,('',))[0]=='dev': newst=('vt',)
                elif st.get(base,('',))[0]=='vt': newst=('fn',off)
            elif mn=='mov' and src in REGS and src in st:
                newst=st[src]
            if newst: st[dst]=newst
            else: st.pop(dst,None)
            continue
    # any other instr writing a reg: crude - if first operand is reg, drop
    if ',' in ops:
        dst=ops.split(',')[0].strip()
        if dst in REGS and mn not in ('cmp','test','push'): st.pop(dst,None)
    elif ops in REGS and mn in ('pop','inc','dec','neg','not'):
        st.pop(ops,None)
cnt=collections.Counter(h[1] for h in hits)
with open('d3dcalls.txt','w') as f:
    for a,r,p in hits:
        f.write('%s %s(0x%X) pushes=%s\n'%(a,{0x10:'GetAdapterCount',0x14:'GetAdapterIdentifier',0x18:'GetAdapterModeCount',0x1C:'EnumAdapterModes',0x20:'GetAdapterDisplayMode',0x24:'CheckDeviceType',0x28:'CheckDeviceFormat',0x2C:'CheckDeviceMultiSampleType',0x30:'CheckDepthStencilMatch',0x34:'CheckDeviceFormatConversion',0x38:'GetDeviceCaps',0x3C:'GetAdapterMonitor',0x40:'CreateDevice',0x8:'Release'}.get(r,'?'),r,p[:6]))
for r,c in sorted(cnt.items()):
    print('0x%03X %-26s %d'%(r,{0x10:'GetAdapterCount',0x14:'GetAdapterIdentifier',0x18:'GetAdapterModeCount',0x1C:'EnumAdapterModes',0x20:'GetAdapterDisplayMode',0x24:'CheckDeviceType',0x28:'CheckDeviceFormat',0x2C:'CheckDeviceMultiSampleType',0x30:'CheckDepthStencilMatch',0x34:'CheckDeviceFormatConversion',0x38:'GetDeviceCaps',0x3C:'GetAdapterMonitor',0x40:'CreateDevice',0x8:'Release'}.get(r,'?'),c))

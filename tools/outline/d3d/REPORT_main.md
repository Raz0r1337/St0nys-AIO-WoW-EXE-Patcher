D3D agent summary (saved by main):
- g_theGxDevicePtr [0xC5DF88]; vtable D3D9 0xA2E718, D3D9Ex 0xA2F500 (check before using; GL has no member).
- +0x3978 IDirect3D9*, +0x397C IDirect3DDevice9*, +0x3B3C backbuffer surf, +0x3B40 auto depth surface, +0x3B28 inScene flag.
- AutoDepthStencilFormat = table 0xA2E4A8[depthFormat]; idx5=D24X8 (default 24bit). PATCH: VA 0xA2E4BC (file 0x62CCBC) 0x4D->0x4B (D24S8). D3D9Ex copy VA 0xA2F3FC (file 0x62DBFC).
- PURE DEVICE: no GetRenderState. Engine never uses stencil. Only Clear at 0x6A752F (SceneClear 0x6A74B0, never STENCIL). Per-frame world clear 0x4F8F7E (GxSceneClear 0x6813B0 mask 3).
- Engine RS cache: GxRsSet 0x408BF0; dev+0x28F4 requested, dev+0x2900 gpu; IRsSync 0x685B50; IRsForceUpdate 0x685A70 (thiscall, marks all dirty).
- D3D shadow block +0x3BC4..: SRC/DEST blend +0x3BC4/+0x3BC8, ALPHABLEND +0x3E60, ALPHATEST +0x3E64, ALPHAREF +0x3E68, FOG +0x3E6C, ZWRITE +0x3E70, colorwrite +0x3E74, LIGHTING +0x3E78, CULL +0x3E80, ZFUNC +0x3E88.
- Object caches: +0x3B5C vdecl, +0x3B60 ib, +0x3B64[8] vb, +0x3B84 offsets, +0x3BA4 strides.
- vtable: Present 0x44, BeginScene 0xA4, EndScene 0xA8, Clear 0xAC, SetRenderState 0xE4, SetTexture 0x104, SetTSS 0x10C, SetSampler 0x114, DrawPrimitiveUP 0x14C (unused by engine), SetFVF 0x164 (unused), SetVS 0x170, SetPS 0x1AC, CreateTexture 0x5C, SetRT 0x94, GetRT 0x98, SetDepthStencilSurface 0x9C, GetDSS 0xA0, StretchRect 0x88.

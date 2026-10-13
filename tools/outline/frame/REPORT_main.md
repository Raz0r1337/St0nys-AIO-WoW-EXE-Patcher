Frame agent summary (saved by main):
- RenderWorld cb 0x4FAF90 -> OnWorldRender 0x4F8EA0 @0x4FB03D -> names 0x7E5140 @0x4FB042 -> restore proj/view.
- OnWorldRender: RsPush 0x4F8F2A; FFX begin 0x8C1770; clear 0x4F8F7E; world viewport set 0x4F905A; M2 pass0 0x4F911D; terrain/WMO 0x7984A0; passes 2/1; weather; spells 0x7FCA30; missiles 0x6FDFB0; 0x4F6F90 circles @0x4F91E5; RsPop 0x4F923B; bubbles 0x56C7A0; restore vp 0x4F9279; FFX apply 0x8C1010.
- Gx 2D API: RsPush 0x409670 (thiscall dev), RsPop 0x685FB0, GxRsSet 0x408BF0 cdecl(state,val): Lighting 0xB, Fog 0xC, DepthTest 0xD, DepthWrite 0xF, Cull 0x11, Blend 6, AlphaRef 7, ColorWrite 0x10; RsSet(ptr) 0x685F50 thiscall ret 8 (Texture0 0x15, VS 0x4D, PS 0x4E).
  GxuXformCreateOrtho 0x6BF4C0 (6 floats + C44Matrix* out); XformSetProjection vt+0xA0, SetView vt+0xA4; GxXformSetViewport 0x681F60; GxXformViewport get 0x408070.
  GxPrimLockVertexPtrs 0x6828C0 (13 args); GxDrawLockedElements 0x682340 (prim 4=strip,count,u16*); example DrawBackground 0x763DF0.
- Screen size floats dev+0x174 {minY,minX,maxY,maxX}. depthFormat dev+0x1CC (6 = D24S8).
- Viewport D3D applied lazily by 0x6A99E0 when dev+0xF6C set (checked in IStateSync 0x6A59E1).
- Portraits 0x619580, UI models 0x95FC30 use M2 after/aside world; restrict to [0xCD754C].

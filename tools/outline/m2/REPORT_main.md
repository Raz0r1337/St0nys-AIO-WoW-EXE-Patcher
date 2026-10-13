M2 agent summary (saved by main):
- CM2Scene::Draw(pass) 0x823CB0; CM2SceneRender::Draw 0x823130; element 0x44 bytes (+0 type,+4 model,+8 flags).
- Loop sets [esi+0x60]=current CM2Model*, [esi+0x40]=CM2Scene*. Jump table 0x823A7A -> 0x823C90.
- DrawBatch 0x8203B0 (type 0) via device vtable +0xA8 -> CGxDeviceD3d::Draw 0x6A3620 -> flush 0x6A5940 -> DrawIndexedPrimitive [vt+0x148] at 0x6A36CF.
- D3D9 device = [[0xC5DF88]+0x397C]. Api [dev+0x1B4]: 0 GL,1 D3D9,2 D3D9Ex.
- Engine never sets stencil states. D24X8 (0x4D) used for RT depth (0x6A0EF3, 0x6A2D15). D3D9Ex tries D24S8,D24X8,D32 at 0x6A7985. Backbuffer depth fmt unverified.
- Passes: 0 opaque, 1/2 transparent. World order in 0x4F8EA0: Draw(0) 0x4F911D, Draw(2/1) ... 0x4F91B9; 0x4F91BE first instr after M2 passes (83 3D A4 79 AC 00 02).
- Hook: 0x823A81 '8B CE E8 28 C9 FF FF' (mov ecx,esi; call DrawBatch) then 'EB 49' jmp 0x823AD3. eax/ecx/edx free. Compare [esi+0x40]==[0xCD754C] for world scene.
  Alt: 0x823A7A 'FF 24 85 90 3C 82 00' (jmp table) and 0x823AD3 '8B 46 50 8B 4E 58' after.
- Model match: model==T || [model+0x48]==T (attachments); T=[target+0xB4]; mount [target+0x98C].
- CM2Model +0x10 flags (0x2000 hidden), +0x24 owner obj ptr (load cb arg), +0x48 attach parent.
- Other scenes: sky 0x7F08C0, UI model frames 0x619580, preview 0x95FC30.

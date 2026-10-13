Target agent summary (saved by main):
- Target GUID 0xBD07B0/0xBD07B4; mouseover 0xBD07A0; focus 0xBD07D0.
- [obj+0xB4] = CM2Model*; vtable+0xD4 GetActiveModel (units: [this+0x98C] (mount?) else +0xB4). Model pool size 0x2F0.
- World M2 scene [0xCD754C]; CM2Scene::Draw(pass) 0x823CB0.
- Color: void cdecl 0x521BF0(const uint64* guid, uint32* outARGB, int forCircle) -> 0xAARRGGBB. Only in-world.
- CGUnit_C::GetSelectionColor 0x718AC0 (vt+0x78). RenderTargetSelectionCircle 0x725980 (vt+0x6C).
- RenderWorld 0x4F8EA0 (ecx=CGWorldFrame, global [0xB7436C]); M2 passes 0x4F911D..0x4F91B9; then call 0x4F6F90 at 0x4F91E5 (RenderSelectionCircles, uses [wf+0x380] target guid set at 0x743F02 if visible & ObjectSelectionCircle CVar).
- Highlight: SetHighlight 0x743C70 / Clear 0x743BC0; obj+0xBC bits; model+0x18C..0x194 RGB float additive tint, model+0x1B8=1.0. Target already highlighted (0x524D37).

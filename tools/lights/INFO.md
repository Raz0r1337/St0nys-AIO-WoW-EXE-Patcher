# Shared info for the "more lights" research (WoW 3.3.5a build 12340 Wow.exe)

Goal of the project: raise the number of dynamic point lights the client renders (today 1 sun + 3 point lights
per M2 model; terrain also 3). Work must be done as exe binary patches (new code appended in a new PE section is fine).
Shaders live in the MPQs (we do NOT have the MPQ files here); a modder team can supply new shaders, but we want to
know exactly what the exe must do and whether a proof of concept is possible without new MPQ shaders.

Original exe (read-only, never modify): /root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
Image base 0x400000. Sections (file offset -> VA):
- .text : VA = fileoff + 0x400C00   (fileoff 0x400 .. 0x5DD800)
- .rdata: VA = fileoff - 0x5DD800 + 0x9DF000  (VA 0x9DF000 .. 0xAB5679)
- .data : VA = fileoff - 0x6B4000 + 0xAB6000  (raw 0x78E00 bytes, virtual size 0x31A508; bss beyond raw)
Python: capstone, keystone, unicorn installed (python3).
Disassembler helper: python3 SCRATCH/dis2.py - <VAhex>:<nbytes> [...]   (annotates .rdata strings)
String xref helper:   python3 SCRATCH/wc/refs.py "<exact string>"  -> VA of string and code pushing it.
SCRATCH = /tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad
Earlier outline research reports with lots of D3D/Gx facts: SCRATCH/outline/{d3d,m2,frame,target}/REPORT_main.md
(e.g. g_theGxDevicePtr [0xC5DF88], IDirect3DDevice9* at dev+0x397C, D3D9 vtable 0xA2E718, VS-constant cache
0xC5EFE8 + reg*16, DIP call site 0x6A36C8 in CGxDeviceD3d::Draw 0x6A3620, M2 batch loop 0x823A81 -> DrawBatch 0x8203B0).

Known facts about lights (verified earlier, re-check what you rely on):
- CVar MaxLights: registered 0x78E480 default "4", validator 0x78D6B0 clamps 1..4 and writes 0xCD7660 which nobody reads (dead).
- CM2Lighting struct, size 0xD4: 4 light pointers at +0x84, 4 distances at +0x94, count at +0xA4, [+0xA0] = farthest dist?
  Embedded in the M2 model (CM2Model) at +0x1D4 (and maybe elsewhere / on stack).
- CM2Lighting::AddLight 0x834F60 (thiscall ecx=lighting, arg=light ptr): keeps the 4 nearest (cmp esi,4). ~12 callers.
- SetLocalLighting 0x873CA0: uploads 11 VS constants starting c17 (c17..c27) at 0x873E9B.
- ComputeLocalLights 0x872900 fills buffer 0xD43098 (44 floats): colours c17-c20, positions c21-c24, attenuation c25-c27.
- Vertex shader index 0x873160: lit + 2*(lightcount + 5*...), 90 variants, lightcount 0..4.
- SetupGxLights 0x8353D0 (non-shader path): slot 0 sun, slots 1..3 point lights (cmp edi,4).
- Gx device: 4 light slots at dev+0x2548 (0x48 bytes each); loops 'cmp ..,4' in D3D9 0x6A43A0 and OpenGL 0x695640.
- Terrain chunks 0x7D0050: loop with fixed 3 lights ([ebp-1Ch]=3), 37 VS constants uploaded; const buffer ends 0xD252F0.
- Shader path flag [0xD43020] (meaning to be confirmed).
- VS registers in use (rough): c0..c48 and c224..c235.

Rules: Do NOT modify anything under /home/user/St0nys-WoW-EXE-Patcher. Work only in SCRATCH/lights/<yourname>/.
Write your final findings to SCRATCH/lights/<yourname>/REPORT.md (English, concise, with VAs and instruction evidence),
and return the same summary as your final answer. Mark clearly what is verified vs. guessed.

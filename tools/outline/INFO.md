# Shared info for the outline research (WoW 3.3.5a build 12340 Wow.exe)

Original exe (read-only, never modify): /root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
Image base 0x400000. Sections (file offset -> VA):
- .text : VA = fileoff + 0x400C00   (fileoff 0x400 .. 0x5DD800)
- .rdata: VA = fileoff - 0x5DD800 + 0x9DF000  (VA 0x9DF000 .. 0xAB5679)
- .data : VA = fileoff - 0x6B4000 + 0xAB6000  (raw 0x78E00 bytes, virtual size 0x31A508; bss beyond raw)
Python: capstone, keystone, unicorn are installed (python3).
Disassembler helper: python3 /tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/dis2.py - <VAhex>:<nbytes> [...]
  (prints .rdata string annotations). Example: python3 .../dis2.py - 720010:300
String xref helper: python3 .../scratchpad/wc/refs.py "<exact string>"  -> prints VA of string and code addresses pushing it.

Known facts (verified earlier):
- ClntObjMgrObjectPtr-like lookup: call 0x4D4DB0 with args (guidLo, guidHi, typeMask, file, line) -> object ptr (cdecl, add esp,0x14). typeMask 0x10 = player.
- 0x4D3790 returns active player GUID in eax:edx. 0x4038F0 returns active player object ptr.
- Chat bubble code: 0x720010 (CGUnit_C method, ecx=unit) computes positions via vtable [unit]+0x2C (GetPosition).
- Typical OS/CRT: cdecl/thiscall MSVC 2005.
Do NOT modify anything under /home/user/St0nys-WoW-EXE-Patcher. Work only in your own folder under scratchpad/outline/<yourname>/.

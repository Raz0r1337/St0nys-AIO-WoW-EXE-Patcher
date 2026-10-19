#!/usr/bin/env python3
"""
make_debug_exe.py - add asset load / render logging to a WoW 3.3.5a (build 12340) client.

Works on the unmodified client (wow.exe.ORI) as well as on a client patched with
St0nys-AIO-WoW-EXE-Patcher: nothing about the PE layout is hard-coded, and every
hook site is checked against the original 3.3.5a bytes before it is touched.
The input file is never modified; the result is written to a separate exe.

    uv run --with keystone-engine --with pefile --with capstone \\
        tools/make_debug_exe.py [wow.exe] [-o wow_debug.exe] [--ods]

Run the St0ny patcher (if wanted) BEFORE this script, never on its output.

What the patched client does (new PE section ".alog"):

  * Every file opened from the MPQs (SFileOpenFileEx, 0x424B50) is written to
    Logs\\AssetDebug.log (fallback: AssetDebug.log next to the exe):
        0000123456 [0A1C] OPEN      Creature\\Foo\\Foo.m2 (flags=0)
        0000123460 [0A1C] OPEN-FAIL Creature\\Foo\\Foo01.skin (flags=0)
    The last 16 opened names are also kept in a ring buffer.
  * CM2Scene::CreateModel (0x81F8F0) and CMapObj::Create (0x7B0CC0) log the
    model path and the object they returned:
        M2-CREATE  Creature\\Foo\\Foo.m2 -> model=1A2B3C40
        WMO-CREATE World\\wmo\\Bar\\Bar.wmo -> mapobj=1A2B3C40
  * TextureCreate (0x4B9760) logs every BLP that is really loaded (texture
    cache misses only, hooked at 0x4B9853), before the load starts:
        TEX-LOAD   Textures\\Foo\\Bar.blp (gxflags=... createflags=...)
  * Rendering: the M2 batch loop (0x823A20), both WMO group render calls
    (0x7ABFF0 / 0x7AC011) and the terrain chunk loop (0x798A6C) remember which
    model / WMO group / ADT chunk is being drawn (memory only, no per-frame I/O).
  * Crash: WoW's top-level exception filter (installed at 0x772B20) is wrapped.
    On a crash the log gets the exception, registers, the M2, WMO and terrain
    chunk being drawn (with paths; the ADT path is rebuilt from the chunk's
    coordinates and the current map), and the last 16 opened files; then WoW's
    own crash handler runs as usual.
"""

import argparse
import hashlib
import os
import struct
import sys

try:
    import keystone
    import pefile
except ImportError:
    sys.exit("needs keystone-engine and pefile:\n"
             "  uv run --with keystone-engine --with pefile --with capstone tools/make_debug_exe.py")

SECTION_NAME = b".alog"
ORI_SHA256 = "aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8"

# Hook sites: VA -> original 3.3.5a bytes (identical in wow.exe.ORI and St0ny-patched exes).
SITES = {
    "SFileOpenFileEx":         (0x424B50, "558bec64a100000000"),  # push ebp; mov ebp,esp; mov eax,fs:[0]
    "CM2Scene::CreateModel":   (0x81F8F0, "558bec8b4508"),        # push ebp; mov ebp,esp; mov eax,[ebp+8]
    "CMapObj::Create":         (0x7B0CC0, "558bec538b5d08"),      # push ebp; mov ebp,esp; push ebx; mov ebx,[ebp+8]
    "CM2Scene batch loop":     (0x823A20, "8b502c895668"),        # mov edx,[eax+2Ch]; mov [esi+68h],edx
    "WMO group render A":      (0x7ABFF0, "ff15ccbecf00"),        # call [0CFBECCh]
    "WMO group render B":      (0x7AC011, "ff15c4becf00"),        # call [0CFBEC4h]
    "SetUnhandledExceptionFilter(WoW filter)": (0x772B20, "6860277700ff15"),  # push 772760h; call [SetUnhandledExceptionFilter]
    "TextureCreate cache miss": (0x4B9853, "3945fc8945f8"),        # cmp [ebp-4],eax; mov [ebp-8],eax  (then jle)
    "Terrain chunk loop":      (0x798A6C, "6a018bcb8945f0"),      # push 1; mov ecx,ebx; mov [ebp-10h],eax  (then call CMapChunk prep)
}
WOW_FILTER = 0x772760
MAP_DIR = 0xCE07D0     # char[] "World\\Maps\\<map>" used by CMapArea's "%s\\%s_%d_%d.adt"
MAP_NAME = 0xCE06D0    # char[] "<map>"

IMPORTS = ["CreateFileA", "WriteFile", "SetFilePointer", "FlushFileBuffers", "GetTickCount",
           "GetCurrentThreadId", "Sleep", "IsBadReadPtr", "OutputDebugStringA", "wsprintfA"]

RING_SLOTS = 16        # must be a power of two
RING_SLOT_SIZE = 260

STRINGS = {
    "S_PATH1": "Logs\\AssetDebug.log",
    "S_PATH2": "AssetDebug.log",
    "S_SESSION": "==== AssetDebug session start ====\r\n",
    "S_PREFIX": "%010u [%04X] ",
    "S_OPEN_OK": "OPEN      %s (flags=%X)\r\n",
    "S_OPEN_FAIL": "OPEN-FAIL %s (flags=%X)\r\n",
    "S_M2": "M2-CREATE  %s -> model=%08X\r\n",
    "S_WMO": "WMO-CREATE %s -> mapobj=%08X\r\n",
    "S_CRASH": "!!!! CRASH: exception %08X at EIP %08X (info0=%X info1=%08X)\r\n",
    "S_REGS": "!!!! EAX=%08X EBX=%08X ECX=%08X EDX=%08X ESI=%08X EDI=%08X\r\n",
    "S_REGS2": "!!!! EBP=%08X ESP=%08X\r\n",
    "S_CM2": "!!!! last M2 drawn        (seq %u): %s  [model=%08X shared=%08X]\r\n",
    "S_CWMO": "!!!! last WMO group drawn (seq %u): %s  [group=%08X mapobj=%08X]\r\n",
    "S_CLAST": "!!!! recent open #%u: %s\r\n",
    "S_TEX": "TEX-LOAD   %s (gxflags=%X createflags=%X)\r\n",
    "S_CTER": "!!!! last terrain chunk drawn (seq %u): %s\\%s_%d_%d.adt chunk (%d,%d)  [chunk=%08X]\r\n",
    "S_CTER0": "!!!! last terrain chunk drawn (seq %u): %s  [chunk=%08X]\r\n",
    "S_NULL": "(null)",
    "S_NONE": "(none)",
    "S_UNREADABLE": "(unreadable)",
}

# Fixed-size variables at the start of the data block.
VARS = ["HFILE", "LOCK", "M2_MODEL", "M2_SHARED", "M2_SEQ", "WMO_GROUP", "WMO_SEQ", "SEQ",
        "RING_IDX", "WRITTEN", "ODS", "TER_CHUNK", "TER_SEQ"]

CODE = r"""
; ---------------------------------------------------------------- log_line(fmt, a1..a9), cdecl
log_line:
    push ebp
    mov ebp, esp
    sub esp, 0x610
    push ebx
    push esi
    push edi
log_spin:
    mov eax, 1
    xchg dword ptr [{LOCK}], eax
    test eax, eax
    jz log_locked
    push 0
    call dword ptr [{Sleep}]
    jmp log_spin
log_locked:
    cmp dword ptr [{HFILE}], 0
    jne log_opened
    call open_log
log_opened:
    call dword ptr [{GetCurrentThreadId}]
    push eax
    call dword ptr [{GetTickCount}]
    push eax
    push {S_PREFIX}
    lea eax, [ebp-0x600]
    push eax
    call dword ptr [{wsprintfA}]
    add esp, 16
    mov ebx, eax
    push dword ptr [ebp+0x2c]
    push dword ptr [ebp+0x28]
    push dword ptr [ebp+0x24]
    push dword ptr [ebp+0x20]
    push dword ptr [ebp+0x1c]
    push dword ptr [ebp+0x18]
    push dword ptr [ebp+0x14]
    push dword ptr [ebp+0x10]
    push dword ptr [ebp+0x0c]
    push dword ptr [ebp+0x08]
    lea eax, [ebp+ebx-0x600]
    push eax
    call dword ptr [{wsprintfA}]
    add esp, 44
    add ebx, eax
    mov eax, dword ptr [{HFILE}]
    cmp eax, -1
    je log_nofile
    push 0
    lea ecx, [ebp-0x604]
    push ecx
    push ebx
    lea ecx, [ebp-0x600]
    push ecx
    push eax
    call dword ptr [{WriteFile}]
log_nofile:
    cmp dword ptr [{ODS}], 0
    je log_unlock
    lea eax, [ebp-0x600]
    push eax
    call dword ptr [{OutputDebugStringA}]
log_unlock:
    mov dword ptr [{LOCK}], 0
    pop edi
    pop esi
    pop ebx
    mov esp, ebp
    pop ebp
    ret

; ---------------------------------------------------------------- open_log (lock held)
open_log:
    push 0
    push 0x80
    push 4
    push 0
    push 3
    push 0x40000000
    push {S_PATH1}
    call dword ptr [{CreateFileA}]
    cmp eax, -1
    jne open_ok
    push 0
    push 0x80
    push 4
    push 0
    push 3
    push 0x40000000
    push {S_PATH2}
    call dword ptr [{CreateFileA}]
open_ok:
    mov dword ptr [{HFILE}], eax
    cmp eax, -1
    je open_ret
    push 2
    push 0
    push 0
    push eax
    call dword ptr [{SetFilePointer}]
    push 0
    push {WRITTEN}
    push {S_SESSION_LEN}
    push {S_SESSION}
    push dword ptr [{HFILE}]
    call dword ptr [{WriteFile}]
open_ret:
    ret

; ---------------------------------------------------------------- SFileOpenFileEx(mpq, name, flags, out), stdcall
hk_open:
    pushfd
    pushad
    mov esi, dword ptr [esp+0x2c]
    test esi, esi
    jz open_skipcopy
    mov eax, 1
    lock xadd dword ptr [{RING_IDX}], eax
    and eax, {RING_MASK}
    imul eax, eax, {RING_SLOT_SIZE}
    lea edi, [eax+{RING}]
    mov ecx, {RING_SLOT_SIZE_M1}
open_cp:
    mov al, byte ptr [esi]
    mov byte ptr [edi], al
    test al, al
    jz open_skipcopy
    inc esi
    inc edi
    dec ecx
    jnz open_cp
    mov byte ptr [edi], 0
open_skipcopy:
    popad
    popfd
    push dword ptr [esp+0x10]
    push dword ptr [esp+0x10]
    push dword ptr [esp+0x10]
    push dword ptr [esp+0x10]
    call tramp_open
    pushfd
    pushad
    mov esi, dword ptr [esp+0x2c]
    test esi, esi
    jnz open_nn
    mov esi, {S_NULL}
open_nn:
    mov edx, dword ptr [esp+0x30]
    mov ecx, {S_OPEN_OK}
    cmp dword ptr [esp+0x1c], 0
    jne open_res
    mov ecx, {S_OPEN_FAIL}
open_res:
    push edx
    push esi
    push ecx
    call log_line
    add esp, 12
    popad
    popfd
    ret 0x10
tramp_open:
    {SFileOpenFileEx_ORIG}
    jmp {SFileOpenFileEx_RESUME}

; ---------------------------------------------------------------- CM2Scene::CreateModel(name, flags), thiscall
hk_m2create:
    push dword ptr [esp+8]
    push dword ptr [esp+8]
    call tramp_m2create
    pushfd
    pushad
    mov esi, dword ptr [esp+0x28]
    test esi, esi
    jnz m2c_nn
    mov esi, {S_NULL}
m2c_nn:
    push dword ptr [esp+0x1c]
    push esi
    push {S_M2}
    call log_line
    add esp, 12
    popad
    popfd
    ret 8
tramp_m2create:
    {CM2Scene_CreateModel_ORIG}
    jmp {CM2Scene_CreateModel_RESUME}

; ---------------------------------------------------------------- CMapObj::Create(name), cdecl
hk_wmocreate:
    push dword ptr [esp+4]
    call tramp_wmocreate
    add esp, 4
    pushfd
    pushad
    mov esi, dword ptr [esp+0x28]
    test esi, esi
    jnz wmoc_nn
    mov esi, {S_NULL}
wmoc_nn:
    push dword ptr [esp+0x1c]
    push esi
    push {S_WMO}
    call log_line
    add esp, 12
    popad
    popfd
    ret
tramp_wmocreate:
    {CMapObj_Create_ORIG}
    jmp {CMapObj_Create_RESUME}

; ---------------------------------------------------------------- M2 batch loop: eax = CM2Model*, ecx is dead here
hk_m2draw:
    mov edx, dword ptr [eax+0x2c]
    mov dword ptr [esi+0x68], edx
    mov dword ptr [{M2_MODEL}], eax
    mov dword ptr [{M2_SHARED}], edx
    mov ecx, dword ptr [{SEQ}]
    lea ecx, [ecx+1]
    mov dword ptr [{SEQ}], ecx
    mov dword ptr [{M2_SEQ}], ecx
    jmp {M2_DRAW_RESUME}

; ---------------------------------------------------------------- WMO group render calls: esi = CMapObjGroup*
hk_wmodraw_a:
    mov dword ptr [{WMO_GROUP}], esi
    push eax
    mov eax, dword ptr [{SEQ}]
    lea eax, [eax+1]
    mov dword ptr [{SEQ}], eax
    mov dword ptr [{WMO_SEQ}], eax
    pop eax
    jmp dword ptr [0xcfbecc]
hk_wmodraw_b:
    mov dword ptr [{WMO_GROUP}], esi
    push eax
    mov eax, dword ptr [{SEQ}]
    lea eax, [eax+1]
    mov dword ptr [{SEQ}], eax
    mov dword ptr [{WMO_SEQ}], eax
    pop eax
    jmp dword ptr [0xcfbec4]

; ---------------------------------------------------------------- TextureCreate(name, gxflags, status, createflags) cache miss
hk_texload:
    pushfd
    pushad
    mov esi, dword ptr [ebp+8]
    test esi, esi
    jnz tex_nn
    mov esi, {S_NULL}
tex_nn:
    push dword ptr [ebp+0x14]
    push dword ptr [ebp+0x0c]
    push esi
    push {S_TEX}
    call log_line
    add esp, 16
    popad
    popfd
    {TEX_ORIG}
    jmp {TEX_RESUME}

; ---------------------------------------------------------------- terrain chunk loop: ebx = CMapChunk*
hk_terrain:
    {TERRAIN_ORIG}
    mov dword ptr [{TER_CHUNK}], ebx
    push eax
    mov eax, dword ptr [{SEQ}]
    lea eax, [eax+1]
    mov dword ptr [{SEQ}], eax
    mov dword ptr [{TER_SEQ}], eax
    pop eax
    jmp {TERRAIN_RESUME}

; ---------------------------------------------------------------- top-level exception filter(EXCEPTION_POINTERS*)
hk_filter:
    push ebp
    mov ebp, esp
    sub esp, 0x10
    pushad
    mov dword ptr [{LOCK}], 0
    mov esi, dword ptr [ebp+8]
    mov ebx, dword ptr [esi]
    push dword ptr [ebx+0x18]
    push dword ptr [ebx+0x14]
    push dword ptr [ebx+0x0c]
    push dword ptr [ebx]
    push {S_CRASH}
    call log_line
    add esp, 20
    mov edi, dword ptr [esi+4]
    push dword ptr [edi+0x9c]
    push dword ptr [edi+0xa0]
    push dword ptr [edi+0xa8]
    push dword ptr [edi+0xac]
    push dword ptr [edi+0xa4]
    push dword ptr [edi+0xb0]
    push {S_REGS}
    call log_line
    add esp, 28
    push dword ptr [edi+0xc4]
    push dword ptr [edi+0xb4]
    push {S_REGS2}
    call log_line
    add esp, 12

    mov eax, {S_NONE}
    mov ebx, dword ptr [{M2_SHARED}]
    test ebx, ebx
    jz flt_m2
    lea ebx, [ebx+0x3c]
    push 260
    push ebx
    call dword ptr [{IsBadReadPtr}]
    test eax, eax
    mov eax, {S_UNREADABLE}
    jnz flt_m2
    mov eax, ebx
flt_m2:
    push dword ptr [{M2_SHARED}]
    push dword ptr [{M2_MODEL}]
    push eax
    push dword ptr [{M2_SEQ}]
    push {S_CM2}
    call log_line
    add esp, 20

    mov dword ptr [ebp-4], 0
    mov eax, {S_NONE}
    mov ebx, dword ptr [{WMO_GROUP}]
    test ebx, ebx
    jz flt_wmo
    lea ecx, [ebx+0x18c]
    push 4
    push ecx
    call dword ptr [{IsBadReadPtr}]
    test eax, eax
    mov eax, {S_UNREADABLE}
    jnz flt_wmo
    mov ecx, dword ptr [ebx+0x18c]
    mov dword ptr [ebp-4], ecx
    test ecx, ecx
    jz flt_wmo
    lea ecx, [ecx+0x1c]
    mov dword ptr [ebp-8], ecx
    push 260
    push ecx
    call dword ptr [{IsBadReadPtr}]
    test eax, eax
    mov eax, {S_UNREADABLE}
    jnz flt_wmo
    mov eax, dword ptr [ebp-8]
flt_wmo:
    push dword ptr [ebp-4]
    push dword ptr [{WMO_GROUP}]
    push eax
    push dword ptr [{WMO_SEQ}]
    push {S_CWMO}
    call log_line
    add esp, 20

    mov eax, {S_NONE}
    mov ebx, dword ptr [{TER_CHUNK}]
    test ebx, ebx
    jz flt_ter_simple
    lea ecx, [ebx+0x24]
    push 0x18
    push ecx
    call dword ptr [{IsBadReadPtr}]
    test eax, eax
    mov eax, {S_UNREADABLE}
    jnz flt_ter_simple
    mov eax, dword ptr [ebx+0x34]
    mov edx, dword ptr [ebx+0x38]
    push ebx
    mov ecx, edx
    and ecx, 15
    push ecx
    mov ecx, eax
    and ecx, 15
    push ecx
    sar edx, 4
    push edx
    sar eax, 4
    push eax
    push {MAP_NAME}
    push {MAP_DIR}
    push dword ptr [{TER_SEQ}]
    push {S_CTER}
    call log_line
    add esp, 36
    jmp flt_ter_done
flt_ter_simple:
    push ebx
    push eax
    push dword ptr [{TER_SEQ}]
    push {S_CTER0}
    call log_line
    add esp, 16
flt_ter_done:

    mov esi, dword ptr [{RING_IDX}]
    mov edi, esi
    sub edi, {RING_SLOTS}
    jns flt_loop
    xor edi, edi
flt_loop:
    cmp edi, esi
    jae flt_done
    mov eax, edi
    and eax, {RING_MASK}
    imul eax, eax, {RING_SLOT_SIZE}
    add eax, {RING}
    push eax
    push edi
    push {S_CLAST}
    call log_line
    add esp, 12
    inc edi
    jmp flt_loop
flt_done:
    mov eax, dword ptr [{HFILE}]
    test eax, eax
    jz flt_out
    cmp eax, -1
    je flt_out
    push eax
    call dword ptr [{FlushFileBuffers}]
flt_out:
    popad
    mov esp, ebp
    pop ebp
    jmp {WOW_FILTER}
"""

# Labels in CODE that must be resolved to absolute addresses for the hook sites.
ENTRY_LABELS = ["hk_open", "hk_m2create", "hk_wmocreate", "hk_m2draw",
                "hk_wmodraw_a", "hk_wmodraw_b", "hk_texload", "hk_terrain", "hk_filter", "tramp_open"]


def align(x, a):
    return (x + a - 1) & ~(a - 1)


def die(msg):
    sys.exit("error: " + msg)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", nargs="?", default="wow.exe", help="input exe (default: wow.exe)")
    ap.add_argument("-o", "--output", help="output exe (default: <input>_debug.exe)")
    ap.add_argument("--ods", action="store_true",
                    help="also send every line to OutputDebugStringA (slower; for DebugView / WINEDEBUG=+debugstr)")
    args = ap.parse_args()

    out_path = args.output or os.path.splitext(args.input)[0] + "_debug.exe"
    if os.path.abspath(out_path) == os.path.abspath(args.input):
        die("output must differ from input")

    raw = open(args.input, "rb").read()
    buf = bytearray(raw)
    sha = hashlib.sha256(raw).hexdigest()
    pe = pefile.PE(data=raw, fast_load=False)

    # ---- sanity checks -------------------------------------------------------------
    if pe.FILE_HEADER.Machine != 0x14C:
        die("not a 32-bit x86 exe")
    if pe.OPTIONAL_HEADER.DllCharacteristics & 0x40:
        die("exe has DYNAMIC_BASE set; absolute addresses would not hold")
    names = [s.Name.rstrip(b"\0") for s in pe.sections]
    if SECTION_NAME in names:
        die("input already contains a %s section (already patched?)" % SECTION_NAME.decode())
    ib = pe.OPTIONAL_HEADER.ImageBase
    if ib != 0x400000:
        die("unexpected ImageBase %#x" % ib)

    def va2off(va):
        return pe.get_offset_from_rva(va - ib)

    for name, (va, orig) in SITES.items():
        o = va2off(va)
        have = bytes(buf[o:o + len(orig) // 2]).hex()
        if have != orig:
            die("hook site %s at %#x does not have the original 3.3.5a bytes\n"
                "  expected %s\n  found    %s\n"
                "  (another patch changed this spot - not a 3.3.5a 12340 client, or a conflicting patch)"
                % (name, va, orig, have))

    iat = {}
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        for imp in entry.imports:
            if imp.name and imp.name.decode() in IMPORTS:
                iat[imp.name.decode()] = imp.address
    missing = [n for n in IMPORTS if n not in iat]
    if missing:
        die("missing imports: " + ", ".join(missing))

    # ---- placement -----------------------------------------------------------------
    sa = pe.OPTIONAL_HEADER.SectionAlignment
    fa = pe.OPTIONAL_HEADER.FileAlignment
    last = max(pe.sections, key=lambda s: s.VirtualAddress)
    sec_rva = align(last.VirtualAddress + max(last.Misc_VirtualSize, last.SizeOfRawData), sa)
    sec_va = ib + sec_rva
    raw_off = align(len(buf), fa)

    hdr_off = (pe.DOS_HEADER.e_lfanew + 4 + 20 + pe.FILE_HEADER.SizeOfOptionalHeader
               + 40 * pe.FILE_HEADER.NumberOfSections)
    first_raw = min(s.PointerToRawData for s in pe.sections if s.PointerToRawData)
    if hdr_off + 40 > min(pe.OPTIONAL_HEADER.SizeOfHeaders, first_raw):
        die("no room for another section header")
    if any(buf[hdr_off:hdr_off + 40]):
        die("section header slot at %#x is not empty" % hdr_off)

    # ---- data block ------------------------------------------------------------------
    code_va = sec_va
    data_va = sec_va + 0x1000
    sym = {}
    data = bytearray()
    for v in VARS:
        sym[v] = data_va + len(data)
        data += b"\0" * 4
    data += b"\0" * (align(len(data), 16) - len(data))
    for k, s in STRINGS.items():
        sym[k] = data_va + len(data)
        data += s.encode("ascii") + b"\0"
    sym["S_SESSION_LEN"] = len(STRINGS["S_SESSION"])
    data += b"\0" * (align(len(data), 16) - len(data))
    sym["RING"] = data_va + len(data)
    data += b"\0" * (RING_SLOTS * RING_SLOT_SIZE)
    if args.ods:
        struct.pack_into("<I", data, sym["ODS"] - data_va, 1)

    sym.update(iat)
    sym["RING_MASK"] = RING_SLOTS - 1
    sym["RING_SLOTS"] = RING_SLOTS
    sym["RING_SLOT_SIZE"] = RING_SLOT_SIZE
    sym["RING_SLOT_SIZE_M1"] = RING_SLOT_SIZE - 1
    sym["WOW_FILTER"] = WOW_FILTER
    sym["SFileOpenFileEx_RESUME"] = SITES["SFileOpenFileEx"][0] + 9
    sym["CM2Scene_CreateModel_RESUME"] = SITES["CM2Scene::CreateModel"][0] + 6
    sym["CMapObj_Create_RESUME"] = SITES["CMapObj::Create"][0] + 7
    sym["M2_DRAW_RESUME"] = SITES["CM2Scene batch loop"][0] + 6
    sym["TEX_RESUME"] = SITES["TextureCreate cache miss"][0] + 6
    sym["TERRAIN_RESUME"] = SITES["Terrain chunk loop"][0] + 7
    sym["MAP_DIR"] = MAP_DIR
    sym["MAP_NAME"] = MAP_NAME

    fmt = {k: "%#x" % v for k, v in sym.items()}
    # trampolines re-run the overwritten prologue bytes verbatim
    for key, site in (("SFileOpenFileEx_ORIG", "SFileOpenFileEx"),
                      ("CM2Scene_CreateModel_ORIG", "CM2Scene::CreateModel"),
                      ("CMapObj_Create_ORIG", "CMapObj::Create"),
                      ("TEX_ORIG", "TextureCreate cache miss"),
                      ("TERRAIN_ORIG", "Terrain chunk loop")):
        fmt[key] = ".byte " + ", ".join("%#x" % b for b in bytes.fromhex(SITES[site][1]))
    src = CODE.format(**fmt)
    # keystone does not understand ';' comments in multi-line input reliably - strip them
    src = "\n".join(l.split(";")[0].rstrip() for l in src.splitlines() if l.split(";")[0].strip())

    # A table of the entry label addresses is appended to the code, read back, then dropped.
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    table = "\n".join(".long " + lab for lab in ENTRY_LABELS)
    enc, _ = ks.asm(src + "\n" + table, code_va)
    code = bytes(enc[:-4 * len(ENTRY_LABELS)])
    labels = dict(zip(ENTRY_LABELS, struct.unpack_from("<%dI" % len(ENTRY_LABELS), bytes(enc), len(code))))
    if len(code) > 0x1000:
        die("cave code too large")

    # check that the trampoline really re-creates the original prologue bytes
    t = labels["tramp_open"] - code_va
    if code[t:t + 9].hex() != SITES["SFileOpenFileEx"][1]:
        die("internal: trampoline bytes mismatch (%s)" % code[t:t + 9].hex())

    section = bytearray(0x1000)
    section[:len(code)] = code
    section += data
    vsize = len(section)
    rsize = align(vsize, fa)
    section += b"\0" * (rsize - vsize)

    # ---- hook writes ---------------------------------------------------------------
    def put(va, b):
        o = va2off(va)
        buf[o:o + len(b)] = b

    def jmp(src_va, dst_va, length):
        put(src_va, b"\xE9" + struct.pack("<i", dst_va - (src_va + 5)) + b"\x90" * (length - 5))

    def call(src_va, dst_va, length):
        put(src_va, b"\xE8" + struct.pack("<i", dst_va - (src_va + 5)) + b"\x90" * (length - 5))

    jmp(SITES["SFileOpenFileEx"][0], labels["hk_open"], 9)
    jmp(SITES["CM2Scene::CreateModel"][0], labels["hk_m2create"], 6)
    jmp(SITES["CMapObj::Create"][0], labels["hk_wmocreate"], 7)
    jmp(SITES["CM2Scene batch loop"][0], labels["hk_m2draw"], 6)
    call(SITES["WMO group render A"][0], labels["hk_wmodraw_a"], 6)
    call(SITES["WMO group render B"][0], labels["hk_wmodraw_b"], 6)
    jmp(SITES["TextureCreate cache miss"][0], labels["hk_texload"], 6)
    jmp(SITES["Terrain chunk loop"][0], labels["hk_terrain"], 7)
    put(SITES["SetUnhandledExceptionFilter(WoW filter)"][0] + 1, struct.pack("<I", labels["hk_filter"]))

    # ---- PE header -------------------------------------------------------------------
    hdr = struct.pack("<8sIIIIIIHHI", SECTION_NAME.ljust(8, b"\0"), vsize, sec_rva, rsize, raw_off,
                      0, 0, 0, 0, 0xE0000020)  # code | execute | read | write
    buf[hdr_off:hdr_off + 40] = hdr
    fh = pe.DOS_HEADER.e_lfanew + 4
    oh = fh + 20
    struct.pack_into("<H", buf, fh + 2, pe.FILE_HEADER.NumberOfSections + 1)
    struct.pack_into("<I", buf, oh + 0x38, align(sec_rva + vsize, sa))  # SizeOfImage
    # The Authenticode signature (only present on the untouched client) is void after patching.
    sec_dir = oh + 0x60 + 4 * 8
    sig_note = ""
    if any(buf[sec_dir:sec_dir + 8]):
        buf[sec_dir:sec_dir + 8] = b"\0" * 8
        sig_note = " (cleared the now-invalid signature directory)"

    buf += b"\0" * (raw_off - len(buf))
    buf += section

    # ---- verify ----------------------------------------------------------------------
    chk = pefile.PE(data=bytes(buf))
    s = chk.sections[-1]
    assert s.Name.rstrip(b"\0") == SECTION_NAME
    assert chk.OPTIONAL_HEADER.SizeOfImage == align(s.VirtualAddress + s.Misc_VirtualSize, sa)
    assert s.PointerToRawData % fa == 0 and s.VirtualAddress % sa == 0

    open(out_path, "wb").write(buf)

    kind = "unmodified 3.3.5a client" if sha == ORI_SHA256 else "modified client (sha256 %s...)" % sha[:16]
    print("input : %s - %s" % (args.input, kind))
    print("output: %s (%d bytes)%s" % (out_path, len(buf), sig_note))
    print("section %s at VA %#x (raw %#x, %#x bytes), header at file offset %#x"
          % (SECTION_NAME.decode(), sec_va, raw_off, rsize, hdr_off))
    for lab in ENTRY_LABELS:
        print("  %-14s %#x" % (lab, labels[lab]))
    print("log file: Logs\\AssetDebug.log (fallback AssetDebug.log) in the WoW folder%s"
          % (", plus OutputDebugString" if args.ods else ""))

    try:
        import capstone
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        print("hook sites:")
        for name, (va, orig) in SITES.items():
            o = chk.get_offset_from_rva(va - ib)
            ins = next(md.disasm(bytes(buf[o:o + 16]), va))
            print("  %#x %-40s %s %s" % (va, name, ins.mnemonic, ins.op_str))
    except ImportError:
        pass


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Emuliert die Startkette einer gepatchten Wow.exe ab dem Einstiegspunkt (VA 0x401000) mit unicorn bis
# __tmainCRTStartup (VA 0x40BA9B) und schreibt mit, welche DLLs in welcher Reihenfolge per LoadLibraryA geladen
# werden (und ob der wow_optimize-Lader seinen Thread anlegt). __security_init_cookie (VA 0x7755F0) ist ein Stub.
# Aufruf: emu_entry.py <Wow.exe> <erwartete Folge, z.B. "Luxvelum.dll,Lexara.dll,THREAD,LuxShoulderCam.dll"> [fehlt]
#         "fehlt": LoadLibraryA liefert NULL (DLL nicht da) - die Kette muss trotzdem durchlaufen.
import sys, struct
from unicorn import *
from unicorn.x86_const import *
import pefile
d = open(sys.argv[1], 'rb').read(); pe = pefile.PE(data=d); IB = pe.OPTIONAL_HEADER.ImageBase
want = [x for x in sys.argv[2].split(',') if x]; missing = len(sys.argv) > 3 and sys.argv[3] == 'fehlt'
mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(IB, (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF)
mu.mem_write(IB, d[:0x1000])
for s in pe.sections:
    mu.mem_write(IB + s.VirtualAddress, d[s.PointerToRawData:s.PointerToRawData + min(s.SizeOfRawData, s.Misc_VirtualSize or s.SizeOfRawData)])
STK = 0x100000; mu.mem_map(STK, 0x100000)
STUB = 0x2000000; mu.mem_map(STUB, 0x10000); mu.mem_write(STUB, b'\xF4' * 0x10000)
def r32(a): return struct.unpack('<I', mu.mem_read(a, 4))[0]
def w32(a, v): mu.mem_write(a, struct.pack('<I', v & 0xFFFFFFFF))
def rstr(a): return bytes(mu.mem_read(a, 64)).split(b'\0')[0].decode('latin-1')
seen = []
API = {'LoadLibraryA': 1, 'CreateThread': 6, 'CloseHandle': 1}
stubs = {}
for e in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in e.imports:
        if imp.name and imp.name.decode() in API:
            sa = STUB + 0x10 * len(stubs); stubs[sa] = imp.name.decode(); w32(imp.address, sa)
assert len(stubs) == len(API), stubs
CRT = 0x40BA9B
def hook(uc, addr, size, ud):
    if addr in stubs:
        name = stubs[addr]; esp = uc.reg_read(UC_X86_REG_ESP); ret = r32(esp)
        if name == 'LoadLibraryA': seen.append(rstr(r32(esp + 4))); eax = 0 if missing else 0x10000000
        elif name == 'CreateThread': seen.append('THREAD'); eax = 0x44
        else: eax = 1
        for r in (UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EDX): uc.reg_write(r, 0xDEAD0000)   # fluechtige Register zerstoeren
        uc.reg_write(UC_X86_REG_EAX, eax); uc.reg_write(UC_X86_REG_ESP, esp + 4 + 4 * API[name]); uc.reg_write(UC_X86_REG_EIP, ret)
    elif addr == 0x7755F0:                                    # __security_init_cookie: Stub
        esp = uc.reg_read(UC_X86_REG_ESP); uc.reg_write(UC_X86_REG_ESP, esp + 4); uc.reg_write(UC_X86_REG_EIP, r32(esp))
mu.hook_add(UC_HOOK_CODE, hook)
esp0 = STK + 0xF0000; mu.reg_write(UC_X86_REG_ESP, esp0)
for k, r in enumerate((UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP)): mu.reg_write(r, 0x7E570000 + k)
mu.emu_start(0x401000, CRT, count=100000)
ok = (mu.reg_read(UC_X86_REG_EIP) == CRT and mu.reg_read(UC_X86_REG_ESP) == esp0 and seen == want and
      all(mu.reg_read(r) == 0x7E570000 + k for k, r in enumerate((UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP))))
print('  Startkette: %s -> %s%s' % (', '.join(seen) or '(keine DLL)', 'bei __tmainCRTStartup, Stack und Register sauber' if ok else 'FALSCH (erwartet: %s)' % ', '.join(want),
      ' (DLLs fehlen)' if missing else ''))
sys.exit(0 if ok else 1)

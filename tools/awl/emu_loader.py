#!/usr/bin/env python3
# Emuliert den awesome-Lader (VA 0x4E5CB0) bis hinter den Ladeaufruf und meldet, ob LoadLibraryA gerufen wurde.
import sys, struct
from unicorn import *
from unicorn.x86_const import *
d = open(sys.argv[1], 'rb').read()
e = struct.unpack_from('<I', d, 0x3C)[0]; n = struct.unpack_from('<H', d, e + 6)[0]
base = e + 24 + struct.unpack_from('<H', d, e + 20)[0]
mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(0x400000, 0x1000000)
mu.mem_write(0x400000, d[:0x1000])
for i in range(n):
    o = base + 40 * i
    vs, va, rs, ra = struct.unpack_from('<IIII', d, o + 8)
    mu.mem_write(0x400000 + va, d[ra:ra + min(rs, vs if vs else rs)])
STUB = 0x2000000; mu.mem_map(STUB, 0x1000); mu.mem_write(STUB, b'\xC2\x04\x00')   # ret 4
mu.mem_map(0x3000000, 0x100000); esp = 0x30F0000; mu.reg_write(UC_X86_REG_ESP, esp)
IAT_LLA = 0x9DF248
mu.mem_write(IAT_LLA, struct.pack('<I', STUB))
calls = []
def hook(uc, addr, size, ud):
    if addr == STUB:
        p = struct.unpack('<I', uc.mem_read(uc.reg_read(UC_X86_REG_ESP) + 4, 4))[0]
        s = bytes(uc.mem_read(p, 64)).split(b'\0')[0].decode('latin1'); calls.append(s)
        uc.reg_write(UC_X86_REG_EAX, 0x10000000)
mu.hook_add(UC_HOOK_CODE, hook)
END = 0x4E5CC7   # push ebp hinter "call + add esp,4"
try:
    mu.emu_start(0x4E5CB0, END, count=20000)
    eip = mu.reg_read(UC_X86_REG_EIP)
except UcError as ex:
    eip = mu.reg_read(UC_X86_REG_EIP); print('Emulationsfehler bei %X: %s' % (eip, ex))
print('Ende bei %X, LoadLibraryA-Aufrufe: %s, eax=%X, Stack %s' % (eip, calls or 'keine', mu.reg_read(UC_X86_REG_EAX), 'ok' if mu.reg_read(UC_X86_REG_ESP) == esp else 'VERSCHOBEN'))

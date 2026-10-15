#!/usr/bin/env python3
# Emuliert alle DLL-Lader einer gepatchten Wow.exe und meldet die LoadLibraryA-Aufrufe.
# Je Lader ein Abschnitt vom Einsprung bis zur Fortsetzung im Original-Code:
#  Lexara 0x401000 -> 0x76E490, wow_optimize 0x76E490 -> 0x7755F0 (+ dessen Thread),
#  Lux 0x76E495 -> Ruecksprung, voice.dll 0x401005 -> 0x40BA9B,
#  awesome 0x40B7D0 -> 0x406D70, WotLKExtensions 0x406D70 -> 0x406D75
# Aufruf: emu_loaders.py <Wow.exe>
import sys, struct
from unicorn import *
from unicorn.x86_const import *
d = open(sys.argv[1], 'rb').read()
e = struct.unpack_from('<I', d, 0x3C)[0]; n = struct.unpack_from('<H', d, e + 6)[0]
opt = e + 24; base = opt + struct.unpack_from('<H', d, e + 20)[0]
secs = [struct.unpack_from('<IIII', d, base + 40 * i + 8) for i in range(n)]   # vs, va, rs, ra
def rva2off(r):
    for vs, va, rs, ra in secs:
        if va <= r < va + max(vs, rs): return ra + r - va
mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(0x400000, 0x1400000)
mu.mem_write(0x400000, d[:0x1000])
for vs, va, rs, ra in secs: mu.mem_write(0x400000 + va, d[ra:ra + min(rs, vs or rs)])
# Importe: jeder IAT-Eintrag bekommt eine eigene Stub-Adresse
imp_rva = struct.unpack_from('<I', d, opt + 96 + 8)[0]
STUB = 0x2000000; mu.mem_map(STUB, 0x10000); mu.mem_write(STUB, b'\xCC' * 0x10000)
names = {}; k = 0; o = rva2off(imp_rva)
while True:
    ilt, _, _, name_rva, iat = struct.unpack_from('<IIIII', d, o)
    if not iat: break
    i = 0
    while True:
        th = struct.unpack_from('<I', d, rva2off(ilt or iat) + 4 * i)[0]
        if not th: break
        nm = d[rva2off(th) + 2:rva2off(th) + 80].split(b'\0')[0].decode() if not th & 0x80000000 else '#%d' % (th & 0xFFFF)
        addr = STUB + 4 * k; names[addr] = nm; k += 1
        mu.mem_write(0x400000 + iat + 4 * i, struct.pack('<I', addr)); i += 1
    o += 20
ARGS = {'LoadLibraryA': 1, 'Sleep': 1, 'CreateThread': 6, 'CloseHandle': 1, 'GetSystemTimeAsFileTime': 1,
        'GetCurrentProcessId': 0, 'GetCurrentThreadId': 0, 'GetTickCount': 0, 'QueryPerformanceCounter': 1}
log = []; threads = []
def rd32(a): return struct.unpack('<I', mu.mem_read(a, 4))[0]
def cstr(a): return bytes(mu.mem_read(a, 64)).split(b'\0')[0].decode('latin1')
END = [None]; REACHED = [False]
def hook(uc, addr, size, ud):
    if addr == END[0]:
        REACHED[0] = True; uc.emu_stop(); return
    if addr in names:
        nm = names[addr]; esp = uc.reg_read(UC_X86_REG_ESP); ret = rd32(esp)
        if nm not in ARGS: log.append('?' + nm); uc.emu_stop(); return
        eax = 0
        if nm == 'LoadLibraryA': log.append('LoadLibraryA("%s")' % cstr(rd32(esp + 4))); eax = 0x10000000
        elif nm == 'CreateThread': threads.append(rd32(esp + 12)); eax = 0x44
        elif nm == 'QueryPerformanceCounter': uc.mem_write(rd32(esp + 4), b'\1' * 8); eax = 1
        uc.reg_write(UC_X86_REG_EAX, eax)
        uc.reg_write(UC_X86_REG_ESP, esp + 4 + 4 * ARGS[nm]); uc.reg_write(UC_X86_REG_EIP, ret)
mu.hook_add(UC_HOOK_CODE, hook)
mu.mem_map(0x3000000, 0x100000)
SENT = 0x5000000
def run(start, end, label):
    esp = 0x30F0000; mu.reg_write(UC_X86_REG_ESP, esp - 4); mu.mem_write(esp - 4, struct.pack('<I', SENT))
    mu.reg_write(UC_X86_REG_EBP, 0); before = len(log); END[0] = end; REACHED[0] = False
    try:
        mu.emu_start(start, SENT + 0x800, count=200000)
    except UcError as ex:
        pass
    ok = 'ok' if REACHED[0] else 'ENDE %X' % mu.reg_read(UC_X86_REG_EIP)
    print('%-16s %s  %s' % (label, ok, ', '.join(log[before:]) or 'kein LoadLibraryA'))
mu.mem_map(SENT, 0x1000); mu.mem_write(SENT, b'\x90' * 0x1000)
run(0x401000, 0x76E490, 'Lexara')
run(0x76E490, 0x7755F0, 'wow_optimize')
for t in list(threads): run(t, SENT, '  Thread %X' % t)
run(0x76E495, SENT, 'Lux')
run(0x401005, 0x40BA9B, 'voice.dll')
run(0x40B7D0, 0x406D70, 'awesome')
run(0x406D70, 0x406D75, 'WotLKExtensions')

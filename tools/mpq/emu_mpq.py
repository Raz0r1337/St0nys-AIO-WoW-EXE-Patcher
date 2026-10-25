#!/usr/bin/env python3
# MPQ-Limit-Fix: den Block hinter dem Aufruf der Patch-Pfad-Suche (VA 0x405E2E bis 0x405E79) im Original und in einer
# gepatchten Exe emulieren und vergleichen. Die Vergroesserung (VA 0x4037F0) ist ein Stub, der Aufrufe mitschreibt und
# die Kapazitaet setzt; 0x5D0040 (Schrittweite) laeuft echt. Geprueft: ebx = 64, edi = 0, Stapel ausgeglichen,
# Schrittweite wie im Original, Kapazitaet danach >= 2*N+64 (gepatcht) bzw. wie im Original (64).
# Aufruf: emu_mpq.py <Original-Wow.exe> <gepatchte Wow.exe>
import sys, struct, pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import *
def load(p):
    pe = pefile.PE(p); img = pe.get_memory_mapped_image(); ib = pe.OPTIONAL_HEADER.ImageBase
    uc = Uc(UC_ARCH_X86, UC_MODE_32); size = (len(img) + 0xFFFF) & ~0xFFFF
    uc.mem_map(ib, max(size, 0xB40000 - ib)); uc.mem_write(ib, bytes(img))
    uc.mem_map(0x100000, 0x10000)                      # Stapel
    return uc
CAP, CNT, DAT, GRAN = 0xB2FA38, 0xB2FA3C, 0xB2FA40, 0xB2FA44
def run(path, n, cap, cnt, gran):
    uc = load(path); calls = []
    r32 = lambda a: struct.unpack('<I', uc.mem_read(a, 4))[0]
    w32 = lambda a, v: uc.mem_write(a, struct.pack('<I', v & 0xFFFFFFFF))
    ebp = 0x10F000; esp = ebp - 0x460
    w32(ebp - 0x24, n); w32(CAP, cap); w32(CNT, cnt); w32(DAT, 0); w32(GRAN, gran)
    for r, v in ((UC_X86_REG_EBP, ebp), (UC_X86_REG_ESP, esp), (UC_X86_REG_EBX, 0x11111111), (UC_X86_REG_EDI, 0x22222222),
                 (UC_X86_REG_ESI, 0x33333333), (UC_X86_REG_EAX, 0x44444444), (UC_X86_REG_ECX, 0x55555555), (UC_X86_REG_EDX, 0x66666666)):
        uc.reg_write(r, v)
    def hook(uc, addr, size, _):
        if addr == 0x4037F0:
            sp = uc.reg_read(UC_X86_REG_ESP); ret = r32(sp); arg = r32(sp + 4); ecx = uc.reg_read(UC_X86_REG_ECX)
            calls.append((ecx, arg)); w32(ecx, arg)                          # Kapazitaet = arg
            uc.reg_write(UC_X86_REG_ESP, sp + 8); uc.reg_write(UC_X86_REG_EIP, ret)
            uc.reg_write(UC_X86_REG_EAX, 0x77777777); uc.reg_write(UC_X86_REG_ECX, 0x88888888); uc.reg_write(UC_X86_REG_EDX, 0x99999999)
    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(0x405E2E, 0x405E79, count=5000)
    return dict(ebx=uc.reg_read(UC_X86_REG_EBX), edi=uc.reg_read(UC_X86_REG_EDI), esp_ok=uc.reg_read(UC_X86_REG_ESP) == esp,
                eip=uc.reg_read(UC_X86_REG_EIP), cap=r32(CAP), cnt=r32(CNT), gran=r32(GRAN), calls=calls)
ORI, NEW = sys.argv[1:3]; bad = 0
for n, cap, cnt, gran in ((0, 0, 0, 0), (6, 0, 0, 0), (36, 0, 0, 0), (37, 0, 0, 0), (120, 0, 0, 0), (40, 200, 0, 64), (10, 64, 64, 64), (50, 64, 64, 64)):
    o, p = run(ORI, n, cap, cnt, gran), run(NEW, n, cap, cnt, gran)
    need = 2 * n + 64
    ok = (p['ebx'] == 64 and p['edi'] == 0 and p['esp_ok'] and p['eip'] == 0x405E79 and p['cap'] >= need and p['cnt'] == cnt
          and p['gran'] == (o['gran'] if o['calls'] else (gran or 64)) and all(c[0] == CAP for c in p['calls'])
          and (len(p['calls']) == (1 if cap < need else 0)))
    bad += not ok
    print('%s N=%-3d cap=%-3d cnt=%-2d | Original: Kap. %-3d Schrittw. %-2d Aufrufe %s | gepatcht: Kap. %-3d Schrittw. %-2d Aufrufe %s ebx=%d edi=%d' % (
        'OK  ' if ok else 'FAIL', n, cap, cnt, o['cap'], o['gran'], [c[1] for c in o['calls']], p['cap'], p['gran'], [c[1] for c in p['calls']], p['ebx'], p['edi']))
print('fails=%d' % bad); sys.exit(1 if bad else 0)

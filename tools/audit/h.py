# Analyse-Harness: PE-Karte, Disassembler, Import-Namen, Funktionsgrenzen.
import struct, re, sys, os
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_OP_IMM, X86_OP_MEM

ORI = '/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
F = open(ORI, 'rb').read()
BASE = 0x400000
SECS = []  # (name, va, vsize, raw, rsize)
pe = struct.unpack_from('<I', F, 0x3c)[0]
nsec = struct.unpack_from('<H', F, pe + 6)[0]
optsz = struct.unpack_from('<H', F, pe + 20)[0]
opt = pe + 24
sec = opt + optsz
for i in range(nsec):
    o = sec + i * 40
    name = F[o:o + 8].rstrip(b'\0').decode()
    vs, va, rs, ro = struct.unpack_from('<IIII', F, o + 8)
    SECS.append((name, BASE + va, vs, ro, rs))
TEXT = SECS[0]
TEXT_LO, TEXT_HI = TEXT[1], TEXT[1] + TEXT[2]

def off2va(off):
    for n, va, vs, ro, rs in SECS:
        if ro <= off < ro + rs:
            return va + (off - ro)
    return None

def va2off(va):
    for n, va0, vs, ro, rs in SECS:
        if va0 <= va < va0 + max(vs, rs):
            return ro + (va - va0)
    return None

def secname(va):
    for n, va0, vs, ro, rs in SECS:
        if va0 <= va < va0 + max(vs, rs):
            return n
    return None

# Importe: IAT-Slot -> Name
IMPORTS = {}
imp_rva, imp_sz = struct.unpack_from('<II', F, opt + 96 + 1 * 8)
d = va2off(BASE + imp_rva)
while True:
    ilt, ts, fc, name_rva, iat_rva = struct.unpack_from('<IIIII', F, d)
    if name_rva == 0:
        break
    dll = F[va2off(BASE + name_rva):].split(b'\0')[0].decode()
    src = ilt or iat_rva
    so = va2off(BASE + src)
    i = 0
    while True:
        e = struct.unpack_from('<I', F, so + i * 4)[0]
        if e == 0:
            break
        if e & 0x80000000:
            nm = '#%d' % (e & 0xffff)
        else:
            nm = F[va2off(BASE + e) + 2:].split(b'\0')[0].decode()
        IMPORTS[BASE + iat_rva + i * 4] = dll + '!' + nm
        i += 1
    d += 20

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

def dis(data, va, count=None):
    out = []
    for ins in md.disasm(data, va):
        out.append(ins)
        if count and len(out) >= count:
            break
    return out

def fmt(ins):
    s = '%08X  %-24s %s %s' % (ins.address, ins.bytes.hex(' '), ins.mnemonic, ins.op_str)
    # Importe benennen
    m = re.search(r'\[(0x[0-9a-f]+)\]', ins.op_str)
    if m:
        a = int(m.group(1), 16)
        if a in IMPORTS:
            s += '   ; ' + IMPORTS[a]
    return s

def func_start(va, limit=0x4000):
    """Sucht rueckwaerts den Funktionsanfang: hinter int3/ret-Padding, oder
    typischer Prolog. Liefert VA oder None."""
    off = va2off(va)
    o = off
    while off - o < limit and o > 0:
        # Padding davor (CC CC) oder nach ret
        if F[o - 1] == 0xCC and F[o] != 0xCC:
            return off2va(o)
        if F[o - 1] in (0xC3,) and F[o] in (0x55, 0x8B, 0x53, 0x56, 0x57, 0x6A, 0x68, 0x81, 0x83, 0xA1, 0xE8, 0xE9, 0xB8, 0x33):
            # ret davor und plausibler Anfang
            return off2va(o)
        if F[o - 3] == 0xC2 and F[o] in (0x55, 0x8B, 0x53, 0x56, 0x57, 0x6A, 0x68, 0x81, 0x83, 0xA1, 0xE8, 0xE9, 0xB8, 0x33):
            return off2va(o)
        o -= 1
    return None

def linear_boundaries(start_va, end_va):
    """Instruktionsgrenzen zwischen start und end per linearer Disassemblierung."""
    o = va2off(start_va)
    bounds = set()
    for ins in md.disasm(F[o:o + (end_va - start_va) + 32], start_va):
        bounds.add(ins.address)
        if ins.address + ins.size >= end_va:
            bounds.add(ins.address + ins.size)
            break
    return bounds

def show(va, n=12, data=None, before=0):
    """Disassemblierung ab va (Original oder data) ausgeben."""
    src = F if data is None else data
    o = va2off(va)
    for ins in dis(src[o:o + 256], va, n):
        print(fmt(ins))

if __name__ == '__main__':
    print('sections', SECS)
    print('imports', len(IMPORTS))
    for k in sorted(IMPORTS)[:5]:
        print(hex(k), IMPORTS[k])

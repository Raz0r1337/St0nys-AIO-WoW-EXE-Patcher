# Erzeugt die PowerShell-Zeilen fuer Code der Visus-Sektion aus ref.py (Adressen relativ zu $V).
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keystone import Ks, KS_ARCH_X86, KS_MODE_32
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import ref
B1, B2 = 0x10000000, 0x20000000
ks = Ks(KS_ARCH_X86, KS_MODE_32); md = Cs(CS_ARCH_X86, CS_MODE_32)
def gen(fn, base_off):
    a1 = bytes(ks.asm(fn(B1), B1 + base_off)[0]); a2 = bytes(ks.asm(fn(B2), B2 + base_off)[0])
    assert len(a1) == len(a2)
    lines = []
    for ins in md.disasm(a1, B1 + base_off):
        o = ins.address - B1 - base_off
        b1, b2 = a1[o:o + ins.size], a2[o:o + ins.size]
        txt = (ins.mnemonic + ' ' + ins.op_str).strip()
        if b1 == b2:
            lines.append(('AddRaw $c @(%s)' % ', '.join('0x%02X' % x for x in b1), txt)); continue
        diff = [k for k in range(ins.size) if b1[k] != b2[k]]
        k0 = diff[-1] - 3; assert diff[0] >= k0 and k0 >= 1
        v1 = struct.unpack_from('<I', b1, k0)[0]; v2 = struct.unpack_from('<I', b2, k0)[0]
        head = b1[:k0]; tail = b1[k0 + 4:]
        if (v2 - v1) & 0xFFFFFFFF == B2 - B1:
            expr = '($V + 0x%03X)' % (v1 - B1)                       # absolut in der Sektion
            txt = txt.replace('0x%x' % v1, '[V+0x%03X]' % (v1 - B1))
        elif (v1 - v2) & 0xFFFFFFFF == B2 - B1:
            nxt = base_off + o + k0 + 4                              # relativ zu fester Adresse
            tgt = (v1 + B1 + nxt) & 0xFFFFFFFF
            expr = '(0x%X - ($V + 0x%03X))' % (tgt, nxt)
        else: raise SystemExit('unbekannt: ' + txt)
        s = ''
        if head: s += 'AddRaw $c @(%s); ' % ', '.join('0x%02X' % x for x in head)
        s += 'AddLE32 $c %s' % expr
        if tail: s += '; AddRaw $c @(%s)' % ', '.join('0x%02X' % x for x in tail)
        lines.append((s, txt))
    names = {0x180: 'CVar visusHeight', 0x184: 'CVar visusShoulder', 0x188: 'letztes X', 0x18C: 'letztes Y', 0x190: 'letzte Kamera',
             0x194: 'gemerkt', 0x1A0: '1.0', 0x1A4: '-1.0', 0x1A8: '2.0', 0x1AC: '-2.0', 0x1B0: '0.01', 0x1B4: '100.0',
             0x1C0: '"0"', 0x1C4: '"20"', 0x1C8: '"visusHeight"', 0x1D8: '"visusShoulder"'}
    import re as _re
    out = []
    for l, t in lines:
        t = t.replace('[[V+', '[V+').replace(']]', ']')
        t = _re.sub(r'0x1[0-9a-f]{7}', lambda m: 'V+0x%03X' % (int(m.group(0), 16) - B1), t)
        m = _re.search(r'V\+0x([0-9A-F]{3})', t)
        if m and int(m.group(1), 16) in names and not _re.match(r'(je|jne|jmp|jp|jae)\b', t): t += '  (%s)' % names[int(m.group(1), 16)]
        out.append((l, t))
    lines = out
    w = max(len(l) for l, _ in lines)
    return ['    %s   # %s' % (l.ljust(w), t) for l, t in lines], len(a1)
reg, lr = gen(ref.reg_asm, ref.O_REG)
cam, lc = gen(ref.cam_asm, ref.O_CAM)
print('    # --- Registrierung (Sektion +0x000, %d Byte) ---' % lr)
print('\n'.join(reg))
print('    # --- Kamera-Haken (Sektion +0x060, %d Byte) ---' % lc)
print('\n'.join(cam))

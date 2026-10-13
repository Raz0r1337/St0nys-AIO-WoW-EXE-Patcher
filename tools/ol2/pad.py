# Einzelne CC-Fuellbytes zwischen Funktionen in .text finden (Lauf genau 1 Byte, davor ret).
import struct, re, sys
d = open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe', 'rb').read()
scr = open(sys.argv[1], encoding='ascii').read()
tab = scr[scr.index("$ORIGINAL_TABLE = @'"):]
used = []
for m in re.finditer(r'(?m)^([a-z0-9]+);([0-9A-F]+);([0-9A-F]+);[01]\r?$', tab):
    o = int(m.group(2), 16); used.append((o, o + len(m.group(3)) // 2))
def free(o): return all(not (a - 64 <= o < b + 64) for a, b in used)
c = []
for o in range(0x1000, 0x5DD7B0):
    if d[o] != 0xCC or d[o - 1] == 0xCC or d[o + 1] == 0xCC: continue
    if d[o - 1] != 0xC3: continue
    if (o + 1 + 0x400C00) % 16 != 0: continue          # danach beginnt eine 16-Byte-ausgerichtete Funktion
    if d[o + 1] not in (0x55, 0x56, 0x53, 0x57, 0x8B, 0x83, 0x6A, 0x51, 0xA1): continue
    if not free(o): continue
    c.append(o)
print(len(c), 'Kandidaten')
for o in c[:8]: print('file %06X  VA %08X  bytes %s' % (o, o + 0x400C00, d[o - 4:o + 4].hex()))
# Kandidaten nahe den Outline-Haken (0x6A3xxx .. 0x6AAxxx)
near = [o for o in c if 0x6A0000 <= o + 0x400C00 <= 0x6B0000]
for o in near[:12]: print('nahe: file %06X  VA %08X  bytes %s' % (o, o + 0x400C00, d[o - 4:o + 4].hex()))

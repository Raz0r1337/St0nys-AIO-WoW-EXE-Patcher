#!/usr/bin/env python3
# Vergleicht eine gepatchte Wow.exe mit dem Original an den Stellen, die Luxveil prueft oder umschreibt
# (luxveil_sites.txt im selben Ordner). Gibt jede abweichende Stelle aus.
# Aufruf: check_sites.py <Original-Wow.exe> <gepatchte Wow.exe> [erlaubte VAs, z.B. 0x81E548]
import sys, os, pefile
orig, new = sys.argv[1], sys.argv[2]
allowed = {int(x, 16) for x in sys.argv[3].split(',')} if len(sys.argv) > 3 and sys.argv[3] else set()
pe = pefile.PE(orig, fast_load=True); IB = pe.OPTIONAL_HEADER.ImageBase
a = open(orig, 'rb').read(); b = open(new, 'rb').read()
bad = []; mem = 0; n = 0
for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'luxveil_sites.txt')):
    if l.startswith('#') or not l.strip(): continue
    va, ln, what = l.split(None, 2); va = int(va, 16); ln = int(ln); n += 1
    off = None
    for s in pe.sections:
        if s.VirtualAddress <= va - IB < s.VirtualAddress + s.SizeOfRawData: off = s.PointerToRawData + va - IB - s.VirtualAddress
    if off is None: mem += 1; continue           # liegt nur im Speicher (nicht in der Datei)
    if a[off:off + ln] != b[off:off + ln]:
        bad.append((va, ln, what.strip(), a[off:off + ln].hex(), b[off:off + ln].hex()))
other = [x for x in bad if x[0] not in allowed]
for va, ln, what, o, p in bad:
    print('  %s 0x%08X %2d %s: %s -> %s' % ('erlaubt' if va in allowed else 'ANDERS ', va, ln, what, o, p))
print('  %d Stellen geprueft (%d nur im Speicher), %d abweichend, davon %d nicht erlaubt' % (n, mem, len(bad), len(other)))
sys.exit(1 if other else 0)

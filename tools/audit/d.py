# python3 dis.py VA LEN [exe]  - Original (oder exe) ab VA disassemblieren
import sys, h
from diffrep import target_info
va = int(sys.argv[1], 16); ln = int(sys.argv[2], 16) if sys.argv[2].startswith('0x') else int(sys.argv[2])
data = open(sys.argv[3], 'rb').read() if len(sys.argv) > 3 else h.F
o = h.va2off(va)
print('== %#x (%s) off %#x' % (va, h.secname(va), o))
for ins in h.dis(data[o:o + ln + 16], va):
    if ins.address >= va + ln:
        break
    ti = target_info(ins, data)
    print('  ' + h.fmt(ins) + ('   ; ' + ' | '.join(ti) if ti else ''))

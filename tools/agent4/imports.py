from lib import *
import struct
# parse import directory of original
e = struct.unpack('<I', d[0x3C:0x40])[0]
opt = e + 24
dd_import = opt + 96 + 8*1
rva, sz = struct.unpack('<II', d[dd_import:dd_import+8])
iat = {}
o = v2f(IB+rva)
while True:
    oft, ts, fc, name_rva, first_thunk = struct.unpack('<IIIII', d[o:o+20])
    if first_thunk == 0: break
    dll = cstr(d, IB+name_rva).decode()
    t = v2f(IB+(oft or first_thunk)); ft_va = IB+first_thunk
    while True:
        v = struct.unpack('<I', d[t:t+4])[0]
        if v == 0: break
        if v & 0x80000000: nm = 'ord%d' % (v & 0xffff)
        else: nm = cstr(d, IB+v+2).decode()
        iat[ft_va] = (dll, nm)
        t += 4; ft_va += 4
    o += 20
import sys
for a in sys.argv[1:]:
    v = int(a, 16); print('%08X -> %s' % (v, iat.get(v)))

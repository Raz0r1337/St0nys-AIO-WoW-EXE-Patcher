from lib import *
import struct, sys
def hdr(data, label):
    e = struct.unpack('<I', data[0x3C:0x40])[0]
    nsec = struct.unpack('<H', data[e+6:e+8])[0]
    opt = struct.unpack('<H', data[e+20:e+22])[0]
    SA, FA = struct.unpack('<II', data[e+24+32:e+24+40])
    soi = struct.unpack('<I', data[e+24+56:e+24+60])[0]
    soh = struct.unpack('<I', data[e+24+60:e+24+64])[0]
    print('%s: e=%X nsec=%d SA=%X FA=%X SizeOfImage=%X SizeOfHeaders=%X filelen=%X' % (label, e, nsec, SA, FA, soi, soh, len(data)))
    sb = e + 24 + opt
    secs = []
    for i in range(nsec):
        so = sb + 40*i
        nm = data[so:so+8].rstrip(b'\0').decode('latin1')
        vs, va, rs, ro = struct.unpack('<IIII', data[so+8:so+24])
        ch = struct.unpack('<I', data[so+36:so+40])[0]
        print('  %-8s VA=%08X vsize=%08X raw=%08X rawsize=%08X chars=%08X  (hdr at file %X)' % (nm, va, vs, ro, rs, ch, so))
        secs.append((nm, va, vs, ro, rs, ch))
    return e, sb, secs, soi
if __name__ == '__main__':
    hdr(d, 'ORIGINAL')
    for n in sys.argv[1:]:
        hdr(load(n), 'out/%s' % n)

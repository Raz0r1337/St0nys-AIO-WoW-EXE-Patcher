from lib import *
import struct, sys
RSRC_VA = 0x9D3000; RSRC_RAW = 0x72E000
def parse_dir(data, off, level=0, path=()):
    """returns list of (path, data_rva, size)"""
    base = RSRC_RAW
    nnamed, nid = struct.unpack('<HH', data[base+off+12:base+off+16])
    res = []
    for i in range(nnamed+nid):
        eo = base+off+16+8*i
        name, doff = struct.unpack('<II', data[eo:eo+8])
        if name & 0x80000000:
            so = base + (name & 0x7fffffff); ln = struct.unpack('<H', data[so:so+2])[0]
            nm = data[so+2:so+2+2*ln].decode('utf-16le')
        else:
            nm = name
        if doff & 0x80000000:
            res += parse_dir(data, doff & 0x7fffffff, level+1, path+(nm,))
        else:
            de = base+doff
            rva, size, cp, _ = struct.unpack('<IIII', data[de:de+16])
            res.append((path+(nm,), rva, size))
    return res
def entries(data):
    return parse_dir(data, 0)
def rva2file(rva): return RSRC_RAW + (rva - RSRC_VA)
def parse_versioninfo(data, off, size):
    """walk VS_VERSIONINFO tree; yields (depth, key, wLength, wValueLength, wType, value, node_off)"""
    out = []
    def node(o, end, depth):
        wLength, wValueLength, wType = struct.unpack('<HHH', data[o:o+6])
        # key: utf16 string
        k = o+6; e = data.find(b'\0\0', k)
        while (e - k) % 2: e = data.find(b'\0\0', e+1)
        key = data[k:e].decode('utf-16le')
        vo = (e+2 + 3) & ~3
        if wType == 1 and wValueLength:
            val = data[vo:vo+wValueLength*2]
            # check terminator
            term_ok = val[-2:] == b'\0\0'
            txt = val.decode('utf-16le', 'replace')
            out.append((depth, key, wLength, wValueLength, wType, txt, o, vo, term_ok))
            co = (vo + wValueLength*2 + 3) & ~3
        elif wValueLength:
            val = data[vo:vo+wValueLength]
            out.append((depth, key, wLength, wValueLength, wType, val.hex(), o, vo, None))
            co = (vo + wValueLength + 3) & ~3
        else:
            out.append((depth, key, wLength, wValueLength, wType, '', o, vo, None))
            co = vo
        # String nodes (depth 3) and Var nodes are leaves; guard zero-length children
        if depth >= 3 or key in ('Translation',):
            return o + wLength
        while co < o + wLength:
            if struct.unpack('<H', data[co:co+2])[0] == 0:
                out.append((depth+1, '<zero-length child!>', 0, 0, 0, '', co, co, None)); break
            co = node(co, o+wLength, depth+1)
            co = (co + 3) & ~3
        return o + wLength
    node(off, off+size, 0)
    return out
if __name__ == '__main__':
    import sys
    which = sys.argv[1:] or ['ORI']
    for w in which:
        data = d if w == 'ORI' else load(w)
        print('==== %s' % w)
        ents = entries(data)
        for path, rva, size in ents:
            fo = rva2file(rva)
            print('  %-28s rva=%08X file=%06X size=%d' % (str(path), rva, fo, size))
        for path, rva, size in ents:
            if path[0] == 16:
                fo = rva2file(rva)
                print('  --- VS_VERSIONINFO at file %X size %d' % (fo, size))
                for depth, key, wl, wvl, wt, txt, o, vo, term in parse_versioninfo(data, fo, size):
                    extra = ''
                    if wt == 1 and wvl:
                        nchars = len(txt.rstrip('\0'))
                        extra = ' chars=%d(+nul) %s' % (nchars, 'TERM_OK' if term else 'NO_TERMINATOR!')
                        if wvl != nchars+1: extra += ' wValueLength MISMATCH (field says %d)' % wvl
                        # also check padding bytes after value up to next node are zero
                        pad = data[vo+wvl*2:(vo+wvl*2+3)&~3]
                        if any(pad): extra += ' PAD_NONZERO'
                    print('    %s%-18s off=%X wLen=%d wValLen=%d type=%d %r%s' % ('  '*depth, key, o, wl, wvl, wt, txt, extra))
                    if key == 'VS_VERSION_INFO':
                        ff = data[vo:vo+52]
                        sig, sver, fvms, fvls, pvms, pvls, fflm, ffl, fos, ft, fst, dms, dls = struct.unpack('<13I', ff)
                        print('      FIXEDFILEINFO sig=%08X FileVersion=%d.%d.%d.%d ProductVersion=%d.%d.%d.%d' % (sig, fvms>>16, fvms&0xffff, fvls>>16, fvls&0xffff, pvms>>16, pvms&0xffff, pvls>>16, pvls&0xffff))

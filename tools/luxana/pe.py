# Minimal PE32 parser + capstone disassembler with import/string annotation (static only)
import struct, sys, re
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
class PE:
    def __init__(self, path):
        self.d = open(path, 'rb').read()
        d = self.d
        e = struct.unpack_from('<I', d, 0x3C)[0]
        self.nsec = struct.unpack_from('<H', d, e + 6)[0]
        opt = e + 24
        self.ib = struct.unpack_from('<I', d, opt + 28)[0]
        self.ep = struct.unpack_from('<I', d, opt + 16)[0] + self.ib
        sh = opt + struct.unpack_from('<H', d, e + 20)[0]
        self.secs = []
        for i in range(self.nsec):
            o = sh + 40 * i
            name = d[o:o+8].rstrip(b'\0').decode()
            vs, va, rs, ro = struct.unpack_from('<IIII', d, o + 8)
            self.secs.append((name, va + self.ib, vs, ro, rs))
        self.imports = {}
        imp_rva = struct.unpack_from('<I', d, opt + 96 + 8)[0]
        if imp_rva:
            o = self.off(imp_rva + self.ib)
            while True:
                oft, ts, fc, nm, ft = struct.unpack_from('<IIIII', d, o)
                if nm == 0: break
                dll = self.cstr(nm + self.ib)
                t = oft or ft; k = 0
                while True:
                    v = struct.unpack_from('<I', d, self.off(t + self.ib) + 4 * k)[0]
                    if v == 0: break
                    fn = ('#%d' % (v & 0xFFFF)) if v & 0x80000000 else self.cstr(v + self.ib + 2)
                    self.imports[ft + self.ib + 4 * k] = dll + '!' + fn
                    k += 1
                o += 20
    def off(self, va):
        for name, sva, vs, ro, rs in self.secs:
            if sva <= va < sva + max(vs, rs): return va - sva + ro
        raise ValueError(hex(va))
    def cstr(self, va):
        o = self.off(va); return self.d[o:self.d.index(b'\0', o)].decode('latin1')
    def dis(self, va, n=60, stop_ret=False):
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        o = self.off(va)
        out = []
        for ins in md.disasm(self.d[o:o + 0x2000], va):
            ann = ''
            for m in re.findall(r'0x[0-9a-f]+', ins.op_str):
                v = int(m, 16)
                if v in self.imports: ann += ' ; ' + self.imports[v]
                else:
                    try:
                        oo = self.off(v)
                        s = self.d[oo:oo + 80].split(b'\0')[0]
                        if len(s) >= 4 and all(32 <= c < 127 for c in s): ann += ' ; "%s"' % s.decode()[:70]
                    except Exception: pass
            out.append('%08X  %-28s %s %s%s' % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str, ann))
            n -= 1
            if n <= 0 or (stop_ret and ins.mnemonic in ('ret', 'retn')): break
        return '\n'.join(out)
if __name__ == '__main__':
    p = PE(sys.argv[1])
    va = int(sys.argv[2], 16) if len(sys.argv) > 2 else p.ep
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    print(p.dis(va, n, stop_ret=len(sys.argv) > 4))

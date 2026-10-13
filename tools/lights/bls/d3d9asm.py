# Minimal D3D9 shader-model 2/3 bytecode (token stream) assembler + dumper.
# Encoding follows the public D3D9 "Shader Code Format" docs (version/instruction/
# parameter tokens).  Not validated against the D3D9 runtime here (no Windows):
# validate on Windows with D3DXDisassembleShader / fxc /dumpbin, or vkd3d-compiler.
import struct

OP = dict(nop=0, mov=1, add=2, sub=3, mad=4, mul=5, rcp=6, rsq=7, dp3=8, dp4=9, min=10, max=11,
          slt=12, sge=13, exp=14, log=15, lit=16, dst=17, lrp=18, frc=19, m4x4=20, m4x3=21,
          m3x4=22, m3x3=23, m3x2=24, loop=27, endloop=29, dcl=31, pow=32, nrm=36, rep=38,
          endrep=39, mova=46, defi=48)
OP["def"] = 81
RT = dict(r=0, v=1, c=2, a=3, oPos_raster=4, oD=5, oT=6, i=7, o=6, aL=15)
USAGE = dict(position=0, blendweight=1, blendindices=2, normal=3, psize=4, texcoord=5,
             tangent=6, binormal=7, color=10, fog=11)
SW = {'x': 0, 'y': 1, 'z': 2, 'w': 3}

def _reg(rtype, num):
    return (num & 0x7FF) | ((rtype & 7) << 28) | (((rtype >> 3) & 3) << 11)

def dst(rtype, num, mask='xyzw', sat=False):
    m = sum(1 << SW[ch] for ch in mask)
    return 0x80000000 | _reg(RT[rtype], num) | (m << 16) | ((1 << 20) if sat else 0)

def src(rtype, num, swz='xyzw', neg=False, rel=None):
    swz = (swz + swz[-1] * 4)[:4]
    s = sum(SW[ch] << (2 * k) for k, ch in enumerate(swz))
    t = [0x80000000 | _reg(RT[rtype], num) | (s << 16) | ((1 << 24) if neg else 0)]
    if rel is not None:                       # relative addressing: c[a0.x + num] / c[aL + num]
        t[0] |= 1 << 13
        rr, rn, rc = rel
        t.append(0x80000000 | _reg(RT[rr], rn) | ((SW[rc] * 0x55) << 16))
    return t

class Asm:
    def __init__(self, major=3, minor=0, vs=True):
        self.t = [(0xFFFE0000 if vs else 0xFFFF0000) | (major << 8) | minor]
    def ins(self, name, *params, ctrl=0):
        body = []
        for p in params:
            body += p if isinstance(p, list) else [p]
        self.t.append(OP[name] | (ctrl << 16) | (len(body) << 24))
        self.t += body
    def dcl(self, usage, idx, d):
        self.t.append(OP['dcl'] | (2 << 24))
        self.t += [0x80000000 | USAGE[usage] | (idx << 16), d]
    def defc(self, n, *f):
        self.t.append(OP['def'] | (5 << 24)); self.t.append(dst('c', n)); self.t += [struct.unpack('<I', struct.pack('<f', x))[0] for x in f]
    def defi(self, n, *v):
        self.t.append(OP['defi'] | (5 << 24)); self.t.append(dst('i', n)); self.t += [x & 0xFFFFFFFF for x in v]
    def end(self):
        self.t.append(0x0000FFFF); return struct.pack('<%dI' % len(self.t), *self.t)

def dump(b):
    t = struct.unpack('<%dI' % (len(b) // 4), b); i = 1
    out = ['version %08X' % t[0]]
    while i < len(t):
        tok = t[i]
        if tok == 0xFFFF: out.append('end'); break
        if (tok & 0xFFFF) == 0xFFFE: i += 1 + ((tok >> 16) & 0x7FFF); out.append('comment'); continue
        n = (tok >> 24) & 0xF; op = tok & 0xFFFF
        name = {v: k for k, v in OP.items()}.get(op, 'op%d' % op)
        out.append('%-6s ' % name + ' '.join('%08X' % x for x in t[i + 1:i + 1 + n])); i += 1 + n
    return '\n'.join(out)

if __name__ == '__main__':
    # Demo: vs_3_0, position transform + pass-through texcoord + an 8-light loop skeleton
    # c0..c3 = WVP (hypothetical), lights at c[17+aL] colours, c[25+aL] positions (hypothetical layout)
    a = Asm(3, 0)
    a.dcl('position', 0, dst('v', 0)); a.dcl('normal', 0, dst('v', 1)); a.dcl('texcoord', 0, dst('v', 2))
    a.dcl('position', 0, dst('o', 0)); a.dcl('color', 0, dst('o', 1)); a.dcl('texcoord', 0, dst('o', 2))
    a.defi(0, 8, 0, 1, 0)                                  # loop count 8, start 0, step 1
    a.defc(100, 0, 0, 0, 1)
    a.ins('m4x4', dst('o', 0), src('v', 0), src('c', 0))
    a.ins('mov', dst('r', 0), src('c', 100))               # accum = 0
    a.ins('loop', src('aL', 0), src('i', 0))
    a.ins('add', dst('r', 1, 'xyz'), src('c', 25, rel=('aL', 0, 'x')), src('v', 0, neg=True))  # L = lightpos - P
    a.ins('dp3', dst('r', 2, 'w'), src('r', 1), src('r', 1))
    a.ins('rsq', dst('r', 2, 'w'), src('r', 2, 'w'))
    a.ins('mul', dst('r', 1, 'xyz'), src('r', 1), src('r', 2, 'w'))
    a.ins('dp3', dst('r', 2, 'x', sat=True), src('r', 1), src('v', 1))           # N.L
    a.ins('mad', dst('r', 0, 'xyz'), src('c', 17, rel=('aL', 0, 'x')), src('r', 2, 'x'), src('r', 0))
    a.ins('endloop')
    a.ins('mov', dst('o', 1), src('r', 0)); a.ins('mov', dst('o', 2, 'xy'), src('v', 2))
    b = a.end()
    print(len(b), 'bytes'); print(b.hex()); print(dump(b))

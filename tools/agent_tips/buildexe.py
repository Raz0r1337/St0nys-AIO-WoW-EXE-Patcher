# buildexe.py - builds a Wow.exe with the outline patch like Add-Outline (mkoutline10.py) for the emulation test:
# new writable section .outl with the relocated template, jumps/calls at the patch sites, D24S8. Option flags stay CC.
# (copy of agent_shimmer/gen_fix/buildexe.py with ORI = ol2/exe14/Wow.exe.ORI; quick builds for iterating - the real build uses apply_patches.ps1)
# usage: python3 -B buildexe.py <dir with outline10.py: base snapshot dir or this dir> <out.exe>
import sys, os, struct, importlib
S = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad'
sys.path.insert(0, os.path.join(S, 'gen')); sys.path.insert(0, os.path.abspath(sys.argv[1]))
import outline10 as o
from asmgen import relocate
ORI = os.path.join(S, 'ol2/exe14/Wow.exe.ORI')   # read only
d = bytearray(open(ORI, 'rb').read())
al = lambda v, a: (v + a - 1) // a * a
e = struct.unpack_from('<I', d, 0x3C)[0]; nsec = struct.unpack_from('<H', d, e + 6)[0]; optsz = struct.unpack_from('<H', d, e + 20)[0]
opt = e + 24; salign, falign = struct.unpack_from('<II', d, opt + 32); sizehdr = struct.unpack_from('<I', d, opt + 60)[0]
st = opt + optsz; last = st + 40 * (nsec - 1)
lvs, lva, lrs, lro = struct.unpack_from('<IIII', d, last + 8)
new = st + 40 * nsec
assert new + 40 <= sizehdr and all(b == 0 for b in d[new:new + 40]), 'no room for a section header'
va = al(lva + max(lvs, lrs), salign); raw = al(len(d), falign)
tpl = relocate(o.TPL, o.absf, o.relf, 0x400000 + va); rs = al(len(tpl), falign)
d += b'\0' * (raw - len(d)) + tpl + b'\0' * (rs - len(tpl))
struct.pack_into('<8sIIIIIIHHI', d, new, b'.outl', len(tpl), va, rs, raw, 0, 0, 0, 0, 0xE0000020)
struct.pack_into('<H', d, e + 6, nsec + 1); struct.pack_into('<I', d, opt + 56, al(va + len(tpl), salign))
CAVE = 0x400000 + va; L = o.LAB
def off(v): return v - 0x400C00
def rel32(op, site, target): return bytes([op]) + struct.pack('<i', target - (site + 5))
def patch(site, expect, data):
    f = off(site); assert bytes(d[f:f + len(expect)]) == bytes(expect), hex(site); d[f:f + len(data)] = data
patch(0x6A9B10, [0x8B, 0x86, 0x7C, 0x39, 0x00, 0x00], rel32(0xE9, 0x6A9B10, CAVE + L['vpcap']) + b'\x90')
patch(0x823A81, [0x8B, 0xCE, 0xE8, 0x28, 0xC9, 0xFF, 0xFF], rel32(0xE9, 0x823A81, CAVE + L['batch']) + b'\x90\x90')
patch(0x6A36C8, [0x8B, 0x88, 0x48, 0x01, 0x00, 0x00, 0x52, 0xFF, 0xD1], b'\x52' + rel32(0xE8, 0x6A36C9, CAVE + L['dip']) + b'\x90\x90\x90')
patch(0x6A3706, [0x8B, 0x88, 0x44, 0x01, 0x00, 0x00, 0x52, 0xFF, 0xD1], b'\x52' + rel32(0xE8, 0x6A3707, CAVE + L['dp']) + b'\x90\x90\x90')
patch(0x4F91E5, [0xE8, 0xA6, 0xDD, 0xFF, 0xFF], rel32(0xE8, 0x4F91E5, CAVE + L['post']))
patch(0x822FDD, [0xE8, 0x0E, 0xAD, 0x01, 0x00], rel32(0xE8, 0x822FDD, CAVE + L['sortp']))
patch(0x823D1F, [0xE8, 0x0C, 0xF4, 0xFF, 0xFF], rel32(0xE8, 0x823D1F, CAVE + L['draw1']))
patch(0x823D3B, [0xE8, 0xF0, 0xF3, 0xFF, 0xFF], rel32(0xE8, 0x823D3B, CAVE + L['draw2']))
patch(o.CULLSITE, [0x8B, 0x4B, 0x34, 0x33, 0xD2], rel32(0xE9, o.CULLSITE, CAVE + L['cull']))
for site in o.RESETSITES: patch(site, rel32(0xE8, site, o.X['RESETFN']), rel32(0xE8, site, CAVE + L['glrel']))
assert d[0x62CCBC] == 0x4D; d[0x62CCBC] = 0x4B
open(sys.argv[2], 'wb').write(d)
print('wrote %s: .outl at VA 0x%X, %d bytes (CODE_OFF 0x%X)' % (sys.argv[2], CAVE, len(tpl), o.CODE_OFF))

import sys, struct, capstone
ORI = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/ol2/exe14/Wow.exe.ORI'
D = open(ORI, 'rb').read()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
pe = struct.unpack_from('<I', D, 0x3C)[0]
nsec = struct.unpack_from('<H', D, pe + 6)[0]; opt = struct.unpack_from('<H', D, pe + 20)[0]
IB = struct.unpack_from('<I', D, pe + 24 + 28)[0]
SECS = []
for i in range(nsec):
    o = pe + 24 + opt + 40 * i
    nm = D[o:o + 8].rstrip(b'\0').decode(); vs, va, rs, ro = struct.unpack_from('<4I', D, o + 8)
    SECS.append((nm, IB + va, vs, ro, rs))
def off(va):
    for nm, v, vs, ro, rs in SECS:
        if v <= va < v + max(vs, rs): return va - v + ro
def dis(va, n=40):
    o = off(va); out = []
    for i in md.disasm(D[o:o + n * 15], va):
        out.append('%08X  %-22s %s %s' % (i.address, i.bytes.hex(), i.mnemonic, i.op_str)); n -= 1
        if n <= 0: break
    return out
def f32(va, n=1): return struct.unpack_from('<%df' % n, D, off(va))
def u32(va, n=1): return struct.unpack_from('<%dI' % n, D, off(va))
if __name__ == '__main__':
    for a in sys.argv[1:]:
        va, n = (a.split(':') + ['30'])[:2]
        print('=== %s' % va); print('\n'.join(dis(int(va, 16), int(n))))

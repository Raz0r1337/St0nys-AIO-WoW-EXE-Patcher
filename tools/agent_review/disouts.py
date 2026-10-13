import sys, struct, capstone
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/tm')
from emu2 import sections
D = open(sys.argv[1], 'rb').read()
so = [s for s in sections(D) if s[0] == '.outl'][0]
print(so)
OUT = so[1]; raw = D[so[4]:so[4] + so[2]]
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
start = int(sys.argv[2], 16); end = int(sys.argv[3], 16)
for i in md.disasm(raw[start:end], OUT + start):
    print('%08X +%04X %-26s %s %s' % (i.address, i.address - OUT, i.bytes.hex(), i.mnemonic, i.op_str))

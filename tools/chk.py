import pefile,capstone,sys
pe=pefile.PE(sys.argv[1]); d=open(sys.argv[1],'rb').read()
print([ (s.Name.rstrip(b'\0').decode(), hex(s.Misc_VirtualSize)) for s in pe.sections])
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def dis(va,n):
    o=pe.get_offset_from_rva(va-0x400000)
    for i in list(md.disasm(d[o:o+64],va))[:n]: print('   ',hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
for va,n in [(0x81D51B,2),(0x743DA3,2)]:
    print(hex(va)); dis(va,n)
    o=pe.get_offset_from_rva(va-0x400000); import struct
    tgt=va+5+struct.unpack_from('<i',d,o+1)[0]; print(' cave',hex(tgt)); dis(tgt,13)

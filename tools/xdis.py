import sys, capstone
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def va2off(va): return va-0x400C00  # .text only
def dis(off, n, va=None, data=d):
    if va is None: va=off+0x400C00
    for i in md.disasm(data[off:off+n], va):
        print(f'  {i.address:08X}  {i.bytes.hex():24} {i.mnemonic} {i.op_str}')
if __name__=='__main__':
    for a in sys.argv[1:]:
        va,n=a.split(':'); va=int(va,16); n=int(n)
        print(f'--- VA {va:X}'); dis(va2off(va), n, va)

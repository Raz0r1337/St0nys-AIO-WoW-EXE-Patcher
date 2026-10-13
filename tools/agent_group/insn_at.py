import sys,capstone,struct
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
# given ref addresses (address of imm32 inside insn), find the insn containing it by trying start offsets back 1..7
for a in sys.argv[1:]:
    r=int(a,16)
    best=None
    for back in range(1,8):
        s=r-back
        o=s-0x400C00
        ins=list(md.disasm(D[o:o+16],s))
        if ins and ins[0].address+ins[0].size>r+3 and ins[0].address<=r:
            best=ins[0]
            # prefer the one where the disp ends right at insn end or imm
            break
    if best: print('%08X  %s %s'%(best.address,best.mnemonic,best.op_str))

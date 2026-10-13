# linear-sweep disassembly of a VA range with function grouping; grep-able output
import capstone,sys,re,pickle,os
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
md.skipdata=True
cache='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/frame/text.lst'
if not os.path.exists(cache):
    with open(cache,'w') as f:
        for i in md.disasm(d[0x400:0x5DD800],0x401000):
            f.write('%08X %s %s\n'%(i.address,i.mnemonic,i.op_str))

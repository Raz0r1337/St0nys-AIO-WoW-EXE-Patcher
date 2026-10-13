from lib import *
import sys,re
# for each site that loads reg <- [x+0x2a8], show next 14 instrs, flag uses of reg with disp 0x84..0xa7 and calls
def show(s,n=16):
    f=fstart(s)
    ins=dis(s,0x60,out=False)
    m=re.match(r'(\w+), dword ptr',ins[0].op_str)
    reg=m.group(1) if m else None
    print('== %x (func %x) reg=%s : %s %s'%(s,f,reg,ins[0].mnemonic,ins[0].op_str))
    for i in ins[1:n]:
        mark=''
        if reg and reg in i.op_str: mark='<'
        print('    %08X %s %s %s'%(i.address,i.mnemonic,i.op_str,mark))
for a in sys.argv[1:]: show(int(a,16))

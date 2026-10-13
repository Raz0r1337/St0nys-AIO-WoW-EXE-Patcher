from lib import *
import re
exec(open('stack.py').read().split('for s,ct in sites')[0])
for s,ct in sites:
    f=fstart(s); e=fend(f); ins=dis(f,e-f,out=False)
    X=None
    for i in ins:
        if i.address<s and i.mnemonic=='lea' and i.op_str.startswith('ecx, [ebp -'):
            X=int(i.op_str.split('- ')[1].rstrip(']'),16)
    out=[]
    for k,i in enumerate(ins):
        if i.mnemonic=='lea' and ('[ebp - %#x]'%X) in i.op_str:
            for j in ins[k+1:k+12]:
                if j.mnemonic=='call':
                    out.append('%x->%s'%(i.address,j.op_str)); break
    print('%x ebp-%#x:'%(f,X),' '.join(out))

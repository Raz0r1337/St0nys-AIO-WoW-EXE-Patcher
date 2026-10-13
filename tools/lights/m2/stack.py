from lib import *
import re
sites=[(s,0x790440) for s in calls[0x790440]]+[(s,0x7b0f10) for s in calls[0x7b0f10]]
def fend(f):
    # next function start after f: scan for int3 padding followed by code
    a=f+1
    while True:
        o=off(a)
        if d[o-1]==0xcc and d[o]!=0xcc and d[o-2]==0xcc: return a
        a+=1
for s,ct in sites:
    f=fstart(s); e=fend(f)
    # get X from 'lea ecx, [ebp - X]' right before call
    ins=dis(f,e-f,out=False)
    X=None
    for i in ins:
        if i.address<s and i.mnemonic=='lea' and i.op_str.startswith('ecx, [ebp -'):
            X=int(i.op_str.split('- ')[1].rstrip(']'),16)
    print('== func %x..%x ctor %x at %x, CM2Lighting at ebp-%#x  callers=%s'%(f,e,ct,s,X,[hex(c) for c in calls.get(f,[])][:6]))
    lo=X-0xD4; 
    for i in ins:
        for m in re.finditer(r'\[ebp - 0x([0-9a-f]+)\]',i.op_str):
            y=int(m.group(1),16)
            if X>=y>X-0xD4:
                fo=X-y
                tag='LIST' if 0x84<=fo<0xA8 else ''
                if i.mnemonic in('lea',) or tag:
                    print('   %08X %-6s %-40s field+%#x %s'%(i.address,i.mnemonic,i.op_str,fo,tag))
        if i.mnemonic=='call' and i.address!=s:
            pass

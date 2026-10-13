from lib import *
import sys
def fend(f):
    a=f+1
    while True:
        o=off(a)
        if d[o-1]==0xcc and d[o]!=0xcc and d[o-2]==0xcc: return a
        a+=1
for x in sys.argv[1:]:
    f=fstart(int(x,16)); e=fend(f)
    with open('f_%x.txt'%f,'w') as fh:
        for i in dis(f,e-f,out=False):
            fh.write('%08X %s %s\n'%(i.address,i.mnemonic,i.op_str))
    print('f_%x.txt'%f, hex(e-f))

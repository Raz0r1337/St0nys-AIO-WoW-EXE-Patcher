import sys; sys.path.insert(0,'ml')
from h import *
def funcs_in(a,b):
    fa=v2f(a); fb=v2f(b); res=[]
    o=fa
    while o<fb:
        if d[o:o+3]==b'\x55\x8b\xec' and d[o-1] in (0xCC,0xC3,0x90,0xC2) : res.append(o+0x400C00)
        o+=1
    return res
def sweep(fs, fe):
    out=[]
    o=v2f(fs)
    for i in md.disasm(d[o:v2f(fe)],fs):
        out.append(i)
    return out
if __name__=='__main__':
    rng=[(0x5B0000,0x5C4000),(0x5F0000,0x5F4000),(0x76C000,0x76E800),(0x7E2000,0x7E3000),(0x4C9000,0x4CA000)]
    for a,b in rng:
        fl=funcs_in(a,b)+[b]
        for k in range(len(fl)-1):
            ins=sweep(fl[k],fl[k+1])
            for j,i in enumerate(ins):
                if i.mnemonic=='cmp' and any(i.op_str.endswith(s) for s in (', 0x1f',', 0x1e',', 0x20',', 0x7d0',', 0x7ce',', 0x7cf')):
                    nxt=ins[j+1] if j+1<len(ins) else None
                    print('fn %08X  %08X %-16s %s %s   | next: %s %s'%(fl[k],i.address,i.bytes.hex(),i.mnemonic,i.op_str, nxt.mnemonic if nxt else '', nxt.op_str if nxt else ''))

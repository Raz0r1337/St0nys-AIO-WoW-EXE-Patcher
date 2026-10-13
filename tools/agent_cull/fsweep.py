# function-wise sweep: function starts = 16-aligned addresses preceded by CC (or call targets)
import sys,capstone,re,struct,pickle,os
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
CACHE=os.path.join(os.path.dirname(__file__),'insns.pkl')
def build():
    lo,hi=0x401000,0x9DE000
    starts=set()
    for va in range(lo,hi,16):
        o=va-0x400C00
        if D[o-1]==0xCC and D[o]!=0xCC: starts.add(va)
    # also E8 call targets
    for o in range(0x400,hi-0x400C00-5):
        if D[o]==0xE8:
            t=o+0x400C00+5+struct.unpack_from('<i',D,o+1)[0]
            if lo<=t<hi: starts.add(t)
    starts=sorted(starts)
    out=[]
    for k,s in enumerate(starts):
        e=starts[k+1] if k+1<len(starts) else hi
        o=s-0x400C00
        for i in md.disasm(D[o:e-0x400C00],s):
            out.append((i.address,i.mnemonic+' '+i.op_str,s))
    return out
if os.path.exists(CACHE): I=pickle.load(open(CACHE,'rb'))
else:
    I=build(); pickle.dump(I,open(CACHE,'wb'))
if __name__=='__main__':
    pat=re.compile(sys.argv[1])
    lo=int(sys.argv[2],16) if len(sys.argv)>2 else 0
    hi=int(sys.argv[3],16) if len(sys.argv)>3 else 1<<32
    seen=set()
    for a,s,f in I:
        if lo<=a<hi and pat.search(s) and a not in seen:
            seen.add(a); print('%08X  %-40s fn %08X'%(a,s,f))

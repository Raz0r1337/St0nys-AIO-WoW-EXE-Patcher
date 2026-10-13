import capstone,struct,sys
D=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def calls_of(fn, maxlen=0x3000):
    o=fn-0x400C00; out=set()
    for i in md.disasm(D[o:o+maxlen],fn):
        if i.mnemonic=='call' and i.op_str.startswith('0x'): out.add(int(i.op_str,16))
        if i.mnemonic=='ret' : 
            # stop at first ret followed by int3 padding
            nxt=i.address+i.size-0x400C00
            if D[nxt]==0xCC: break
        if i.mnemonic=='jmp' and i.op_str.startswith('0x'):
            t=int(i.op_str,16)
            if t<fn or t>fn+maxlen: 
                nxt=i.address+i.size-0x400C00
                if D[nxt]==0xCC: out.add(t); break
    return out
targets={int(x,16) for x in sys.argv[2].split(',')}
roots=[int(x,16) for x in sys.argv[1].split(',')]
seen={}; frontier=[(r,[r]) for r in roots]; depth=int(sys.argv[3]) if len(sys.argv)>3 else 4
for d in range(depth):
    nf=[]
    for fn,path in frontier:
        if fn in seen: continue
        seen[fn]=path
        if fn in targets: print('REACH %08X via %s'%(fn,' -> '.join('%08X'%p for p in path)))
        if not (0x401000<=fn<0x9DE000): continue
        for c in calls_of(fn): nf.append((c,path+[c]))
    frontier=nf
for fn,path in frontier:
    if fn in targets and fn not in seen: print('REACH %08X via %s'%(fn,' -> '.join('%08X'%p for p in path)))
print('visited',len(seen))

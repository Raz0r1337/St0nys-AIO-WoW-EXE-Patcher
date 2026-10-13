import re,struct,capstone,os
exec(open('global.py').read().split("# 3) branch-into-range")[0].replace("print(","(lambda *a,**k:None)("))
T0,T1=0x400,0x400+0x5dd3b3
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
# menu order ids
pat_ids=re.findall(r"(?m)^    @\{ Id = '([a-z0-9]+)'",s)
ranges_by_id={}
for idn,off,n,own in ents: ranges_by_id.setdefault(idn,[]).append((off,off+n))
print('== new-code branch targets landing in ANOTHER patch\'s range ==')
issues=0
for N,idn in enumerate(pat_ids,1):
    p=open('out/%d.exe'%N,'rb').read()
    for off,end in ranges_by_id.get(idn,[]):
        if not (T0<=off<T1): continue
        # decode new bytes in this range (plus up to 16 following bytes for context? no - only the range)
        for ins in md.disasm(p[off:end],off+0x400C00):
            if ins.mnemonic.startswith('j') or ins.mnemonic=='call':
                try: tv=int(ins.op_str,16)
                except: continue
                tf=tv-0x400C00
                for idn2,rr in ranges_by_id.items():
                    if idn2==idn or idn2 in ('pe','watermark'): continue
                    for o2,e2 in rr:
                        if o2<=tf<e2:
                            issues+=1; print('  %2d %-13s %08X %s %s -> inside %s 0x%X..0x%X'%(N,idn,ins.address,ins.mnemonic,ins.op_str,idn2,o2,e2))
print('  issues:',issues)
# all.exe sanity: diff vs original must be subset of union of ranges (+ watermark) within original size
print('\n== all.exe diff check ==')
p=open('out/all.exe','rb').read()
print('  size all.exe',len(p),'orig',len(d))
union=set()
for idn,off,n,own in ents:
    for i in range(off,off+n): union.add(i)
bad=[i for i in range(len(d)) if p[i]!=d[i] and i not in union]
print('  bytes changed outside table union:',len(bad), [hex(x) for x in bad[:10]])
# which table ranges unchanged in all.exe (expected: pe slot bytes beyond used, parts of value patches equal to original e.g. date month?)
for idn,off,n,own in ents:
    if idn in ('pe',): continue
    if p[off:off+n]==d[off:off+n]: print('  range unchanged in all.exe: %s 0x%X+%d'%(idn,off,n))

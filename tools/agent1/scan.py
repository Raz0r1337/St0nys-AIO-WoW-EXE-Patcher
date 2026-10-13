from lib import *
print('== branches into worldcrash cave VA 0x9DE3B3..0x9DE3D9 (original .text linear sweep)')
r=branch_targets_into(d,0x9DE3B3,0x9DE3D9)
print(len(r), [('src 0x%X'%va,'len%d'%ln,'tgt 0x%X'%t) for va,o,ln,t in r][:20])
print('== branches into afk cave VA 0x94B902..0x94B91A')
r=branch_targets_into(d,0x94B902,0x94B91A)
print(len(r), [('src 0x%X'%va,'len%d'%ln,'tgt 0x%X'%t) for va,o,ln,t in r][:20])
print('orig cave bytes afk:', d[0x54AD02:0x54AD1A].hex(), ' neighbours:', d[0x54ACF0:0x54AD02].hex(), '|', d[0x54AD1A:0x54AD30].hex())
print('orig cave bytes worldcrash:', d[0x5DD7B3:0x5DD7D9].hex(), ' before:', d[0x5DD7A0:0x5DD7B3].hex(), ' after to .text raw end:', d[0x5DD7D9:0x5DD800].hex())
print('== strict-inside branch targets for all multi-byte replaced code ranges of patches 1-18 (linear sweep, may contain false positives from data/misaligned decode)')
rows=table()
IDS=['worldcrash','rce','wardenoff','noserverpatch','nosurvey','nohttp','afk','glue','mpqsig','localdata','luaunlock','itemcache']
for pid,off,ob,ex in rows:
    if pid not in IDS or len(ob)<2: continue
    if off<TEXT_F or off>=TEXT_F+TEXT_RAW: continue
    lo=f2v(off); hi=lo+len(ob)
    r=branch_targets_into(d,lo,hi,strict_inside=True)
    print('%-14s range VA 0x%X..0x%X  strict-inside hits: %d'%(pid,lo,hi,len(r)), [('src 0x%X'%va,'tgt 0x%X'%t) for va,o,ln,t in r][:12])

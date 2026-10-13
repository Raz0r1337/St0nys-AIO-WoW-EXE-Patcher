from lib import *
rows=table()
IDS=['laa','cache','itemcache','worldcrash','rce','wardenoff','scandll','noserverpatch','nosurvey','skipbnet','skiprdp','nohttp','afk','glue','mpqsig','mpqnames','localdata','luaunlock']
def func_bounds(off):
    """for a .text file offset: start = after preceding int3 run; end = start of next int3 run (>=1 CC following a ret/jmp) -- approximate"""
    s=find_func_start(d,off,0x4000)
    # end: scan forward for first 0xCC byte at/after off that is preceded by a ret (C3/C2xx) or jmp
    o=off
    while o<TEXT_F+TEXT_RAW:
        if d[o]==0xCC and d[o+1]==0xCC: break
        o+=1
    return s,o
print('== same-function / overlapping-range conflicts with OTHER patches')
for pid,off,ob,ex in rows:
    if pid not in IDS: continue
    if TEXT_F<=off<TEXT_F+TEXT_RAW:
        s,e=func_bounds(off)
        kind='func VA 0x%X..0x%X'%(f2v(s),f2v(e))
    else:
        s,e=off-0x40,off+len(ob)+0x40; kind='data +-0x40'
    hits=[]
    for pid2,off2,ob2,ex2 in rows:
        if pid2==pid: continue
        if off2<e and off2+len(ob2)>s: hits.append('%s@0x%X(len %d)'%(pid2,off2,len(ob2)))
    if hits: print('%-14s 0x%X %-28s <- %s'%(pid,off,kind,', '.join(hits)))
print('== done')
# also: all rows of other patches, with VA, for reference
print('== header/data rows of other patches that touch PE header (<0x400)')
for pid,off,ob,ex in rows:
    if off<0x400: print(pid,'0x%X'%off,ob.hex(),ex)

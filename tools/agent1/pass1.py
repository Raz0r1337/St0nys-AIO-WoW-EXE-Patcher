from lib import *
IDS=['laa','cache','itemcache','worldcrash','rce','wardenoff','scandll','noserverpatch','nosurvey','skipbnet','skiprdp','nohttp','afk','glue','mpqsig','mpqnames','localdata','luaunlock']
rows=table()
for n,pid in enumerate(IDS,1):
    print('='*100); print('%d %s'%(n,pid))
    mine=[r for r in rows if r[0]==pid]
    pb=load_patched(n)
    # (a) table original bytes vs exe
    for _,off,ob,excl in mine:
        ok = d[off:off+len(ob)]==ob
        print('  table range 0x%X len %d excl=%d  orig-match=%s'%(off,len(ob),excl,ok))
    # (b) diff set
    diffs=[i for i in range(len(d)) if d[i]!=pb[i]] if len(d)==len(pb) else None
    if diffs is None: print('  SIZE DIFFERS', len(d), len(pb))
    else:
        # group
        groups=[]
        for i in diffs:
            if groups and i==groups[-1][1]: groups[-1][1]=i+1
            else: groups.append([i,i+1])
        print('  diff groups:', ['0x%X..0x%X'%(a,b) for a,b in groups])
        covered=set()
        for _,off,ob,_ in mine: covered.update(range(off,off+len(ob)))
        outside=[i for i in diffs if i not in covered]
        print('  diffs outside table ranges:', ['0x%X'%i for i in outside][:20])
    # (c) ini undo lines
    ini=open(os.path.join(OUT,'%d.ini'%n)).read().splitlines()
    undo=[l for l in ini if l.startswith('undo=')]
    print('  ini undo:', undo)
    # new bytes
    for _,off,ob,_ in mine:
        print('  0x%X old=%s new=%s'%(off,ob.hex(),pb[off:off+len(ob)].hex()))

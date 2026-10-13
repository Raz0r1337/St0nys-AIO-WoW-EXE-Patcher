# usage: q.py VA:len [VA:len ...]  -> xrefs to any address in [VA,VA+len), raw-pattern hits strictly inside, and insn boundary info
from lib import *
import pickle,sys
xrefs,insn_starts,raw=pickle.load(open('xref.pkl','rb'))
for a in sys.argv[1:]:
    v,n=a.split(':'); v=int(v,16); n=int(n,16)
    print(f'=== VA 0x{v:X}..0x{v+n-1:X} (file 0x{va2off(v):X}) start_is_insn_boundary={v in insn_starts}')
    inside=[x for x in range(v,v+n) if x in insn_starts]
    print('  insn starts inside (sweep):',' '.join('%X'%x for x in inside))
    for t in range(v,v+n):
        if t in xrefs:
            for s,m in xrefs[t]: print(f'  SWEEP xref -> 0x{t:X} from 0x{s:X} {m}')
    for t in range(v,v+n):
        if t in raw:
            for s,k in raw[t]:
                tag='' if s in insn_starts else ' (src not an insn start in sweep)'
                print(f'  RAW   hit  -> 0x{t:X} from 0x{s:X} {k}{tag}')

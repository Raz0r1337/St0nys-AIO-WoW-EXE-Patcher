import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/frame')
from fsum import summ
import re
def tgt(c):
    m=re.match(r'^0x([0-9a-f]+)$',c)
    return int(m.group(1),16) if m else None
def follow(va):
    # follow jmp thunk
    import bisect
    from fsum import lines,addrs
    i=bisect.bisect_left(addrs,va)
    p=lines[i].split(None,2)
    if p[1]=='jmp' and p[2].startswith('0x'): return int(p[2],16)
    return va
def strs(va,depth,seen):
    va=follow(va)
    if va in seen: return set()
    seen.add(va)
    end,calls,s,g=summ(va,3000)
    r=set(s)
    if depth>0:
        for c in calls:
            t=tgt(c)
            if t: r|=strs(t,depth-1,seen)
    return r
dep=int(sys.argv[1])
for a in sys.argv[2:]:
    s=strs(int(a,16),dep,set())
    s=[x for x in s if not x.startswith('d:\\Build')]
    print(a,sorted(s)[:25])

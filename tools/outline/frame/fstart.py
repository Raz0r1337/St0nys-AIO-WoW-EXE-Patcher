import sys
lines=open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/frame/text.lst').read().split('\n')
import bisect
addrs=[int(l.split()[0],16) for l in lines if l]
def fstart(va):
    i=bisect.bisect_right(addrs,va)-1
    while i>0:
        if lines[i-1].split()[1]=='int3' and lines[i].split()[1]!='int3': return addrs[i]
        if lines[i-1].split()[1]=='ret' and lines[i].split()[1:3]==['push','ebp']: return addrs[i]
        i-=1
for a in sys.argv[1:]:
    print(a,hex(fstart(int(a,16))))

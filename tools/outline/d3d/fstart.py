import sys,bisect
L=[l.split(' ',2) for l in open('text.asm')]
addrs=[int(x[0],16) for x in L]
def fstart(va):
    i=bisect.bisect_left(addrs,va)
    while i>0:
        if L[i-1][1]=='int3' and L[i][1]!='int3': return addrs[i]
        # also ret followed by aligned push ebp
        i-=1
    return None
for a in sys.argv[1:]:
    va=int(a,16); s=fstart(va); print(a, hex(s))

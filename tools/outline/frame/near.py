import sys,re,bisect
sys.path.insert(0,'/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/frame')
from fsum import lines,addrs,cstr
for a in sys.argv[1:]:
    va=int(a,16); i=bisect.bisect_left(addrs,va); out=[]
    for j in range(max(0,i-3000),min(len(lines),i+3000)):
        for tok in re.findall(r'0x[0-9a-f]+',lines[j]):
            v=int(tok,16)
            if v>=0x9DF000:
                c=cstr(v)
                if c and '.cpp' in c: out.append((abs(addrs[j]-va),hex(addrs[j]),c))
    out.sort(); print(a,[(o[1],o[2]) for o in out[:4]])

import pickle,re,bisect
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
L=pickle.load(open('lin.pkl','rb')); A=[x[0] for x in L]
def cs(v):
    if 0x9DF000<=v<0xAB6000: o=v-0x9DF000+0x5DD800
    elif 0xAB6000<=v<0xB2EE00: o=v-0xAB6000+0x6B4000
    else: return None
    e=d.find(b'\0',o); s=d[o:e]
    return s.decode('latin1') if 1<len(s)<80 and all(32<=c<127 for c in s) else None
def ann(op):
    r=''
    for t in re.findall(r'0x[0-9a-f]+',op):
        s=cs(int(t,16))
        if s: r+=' "%s"'%s
    return r
import sys
targets=[int(x,16) for x in sys.argv[1:]]
for tg in targets:
    i=bisect.bisect_left(A,tg)
    lo=i-14; hi=i
    while hi<len(L) and not L[hi][2].startswith('call'): hi+=1
    hi=min(hi+1,i+25)
    print('=== xref',hex(tg))
    for a,s,m,o in L[lo:hi]:
        print('  %08X %s %s%s'%(a,m,o,ann(o)))

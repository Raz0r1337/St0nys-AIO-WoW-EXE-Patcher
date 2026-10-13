import pickle,sys
L=pickle.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/lights/shader/lines.pkl','rb'))
idx={}
import bisect
addrs=[int(l.split()[0],16) if l[:1].strip() else 0 for l in L]
for a in sys.argv[1:]:
    a,b,c=(a.split(':')+['20','5'])[:3] if ':' in a else (a,'20','5')
    va=int(a,16); i=bisect.bisect_left(addrs,va)
    print('=====',a)
    print('\n'.join(L[i-int(b):i+int(c)]))

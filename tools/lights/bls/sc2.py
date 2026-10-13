import pickle,re
from scan import L,cs,ann
res=[]
for k,(a,s,m,o) in enumerate(L):
    if m=='mov' and o.endswith('+ 0x110]'):
        # need gx device load within 6 before
        if not any('0xc5df88' in L[j][3] for j in range(k-8,k)): continue
        pushes=[];j=k+1
        while j<len(L) and not L[j][2].startswith('call') and j<k+60:
            if L[j][2]=='push': pushes.append((L[j][0],L[j][3]))
            j+=1
        args=[p[1]+ann(p[1]) for p in reversed(pushes[-5:])]
        res.append((a,L[j][0],args,pushes))
for a,c,args,p in res:
    print(hex(a),hex(c),' | '.join(args))

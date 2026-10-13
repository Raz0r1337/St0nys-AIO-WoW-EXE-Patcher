import pickle,re
from scan import L,ann
from fstart import fstart
for k,(a,s,m,o) in enumerate(L):
    if m=='mov' and o.endswith('+ 0x118]') and any('0xc5df88' in L[j][3] for j in range(k-8,k)):
        pushes=[];j=k+1
        # also collect pushes before k back to the device load
        jj=k-1
        while jj>k-8 and '0xc5df88' not in L[jj][3]:
            jj-=1
        for t in range(jj,k):
            if L[t][2]=='push': pushes.append(L[t][3])
        while j<len(L) and not L[j][2].startswith('call') and j<k+40:
            if L[j][2]=='push': pushes.append(L[j][3])
            j+=1
        p=list(reversed(pushes[-4:]))
        if len(p)==4: print(hex(fstart(a) or 0), hex(L[j][0]), 'type=%s reg=%s ptr=%s n=%s'%tuple(p))

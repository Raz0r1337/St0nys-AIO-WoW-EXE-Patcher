import pickle,re,sys
ins=pickle.load(open('sweep.pkl','rb'))
disp=sys.argv[1]; lo=int(sys.argv[2],16); hi=int(sys.argv[3],16)
clo=int(sys.argv[4],16); chi=int(sys.argv[5],16)
pat=re.compile(r'^(e[a-ds][xip]|e[sd]i), dword ptr \[(e..) \+ %s\]$'%disp)
from collections import Counter
cnt=Counter()
for k,(a,s,m,o) in enumerate(ins):
    if not (lo<=a<hi): continue
    if m=='mov' and pat.match(o):
        for j in range(k+1,min(k+8,len(ins))):
            a2,s2,m2,o2=ins[j]
            if m2=='call' and o2.startswith('0x'):
                t=int(o2,16)
                if clo<=t<chi:
                    print(hex(a),o,'->',hex(a2),hex(t)); cnt[t]+=1
                break
print(cnt.most_common(20))

import re,sys,pickle
T='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/d3d/text.asm'
L=open(T).read().split('\n')
pickle.dump(L,open('lines.pkl','wb'))
res=[]
for i,l in enumerate(L):
    if '+ 0x118]' not in l: continue
    # find the call that uses it
    m=re.match(r'(\w+) (\w+) (.*)',l)
    win=L[max(0,i-40):i+12]
    hasdev=any('0xc5df88' in w for w in L[max(0,i-40):i+1])
    # find call after (if mov reg,[x+0x118])
    j=i
    if l.split()[1]!='call':
        reg=re.search(r'mov (\w+), dword ptr \[\w+ \+ 0x118\]',l)
        if not reg: continue
        reg=reg.group(1)
        for j in range(i+1,i+15):
            if re.search(r' call %s$'%reg,L[j]): break
        else: continue
    # collect pushes backwards from j
    pushes=[]
    k=j-1
    while k>j-40 and len(pushes)<4:
        p=L[k].split(' ',2)
        if len(p)>1 and p[1]=='push': pushes.append(p[2])
        if len(p)>1 and p[1] in('call','ret','jmp'): break
        k-=1
    res.append((L[j].split()[0],hasdev,pushes))
for r in res: print(r[0],'DEV' if r[1] else '---',r[2])

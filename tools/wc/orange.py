import re
from codes import C1,C2,C3,C4
sh=lambda n: n+1 if 75<=n<=85 else n
C1={sh(n) for n in C1}; C2={sh(n) for n in C2}; C3={sh(n) for n in C3}|{75}; C4={sh(n) for n in C4}|{75}
G={9,50,63,64,74,80}
assert C1|C2|C3|C4==set(range(1,87))
R='/home/user/St0nys-WoW-EXE-Patcher/'
T={'de':('Bann-Gefahr','auf öffentlichen Servern ungetestet','im Spiel ungetestet','auf öffentlichen Servern und im Spiel ungetestet','Exe wird größer','sicher'),
   'en':('ban risk','untested on public servers','untested in game','untested on public servers and in game','exe grows','safe')}
def badges(n,t):
    b=[]
    if n in C2: b.append('🔴 **[%s]**'%t[0])
    if n in C3 and n in C4: b.append('🟡 **[%s]**'%t[3])
    elif n in C3: b.append('🟡 **[%s]**'%t[1])
    elif n in C4: b.append('🟡 **[%s]**'%t[2])
    if n in G: b.append('🟠 **[%s]**'%t[4])
    if not b: b.append('🟢 **[%s]**'%t[5])
    return ' '.join(b)
BADGE=re.compile(r' (?:🔴|🟡|🟢|🟠) \*\*\[[^\]]*\]\*\*')
for fn,lang,kind in (('README.md','en','r'),('README.de.md','de','r'),('PATCHES.md','de','p'),('PATCHES.en.md','en','p')):
    L=open(R+fn,encoding='utf-8').read().split('\n'); cnt=0
    for i,l in enumerate(L):
        n=None
        if kind=='r':
            m=re.match(r'\| \[(\d+)\]\(PATCHES',l)
            if m:
                n=int(m.group(1)); cells=l.split(' | '); c=cells[1]
                c2=BADGE.sub('',c); assert c2!=c,(fn,n)
                cells[1]=c2+' '+badges(n,T[lang]); L[i]=' | '.join(cells); cnt+=1
        else:
            if i>0 and L[i-1].startswith('<a id="patch-'):
                n=int(re.search(r'\*\((?:Nr\.|No\.) (\d+)[,)]',l).group(1))
                l2=BADGE.sub('',l); assert l2!=l,(fn,n)
                L[i]=l2+' '+badges(n,T[lang]); cnt+=1
    assert cnt==86,(fn,cnt)
    open(R+fn,'w',encoding='utf-8').write('\n'.join(L))

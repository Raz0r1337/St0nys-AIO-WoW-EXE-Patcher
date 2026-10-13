import re
from codes import C2,C3,C4
sh=lambda n: n+1 if 75<=n<=85 else n
SAFE={7,8,9,63,64,70,75}
C2={sh(n) for n in C2}; C3=({sh(n) for n in C3}|{75})-SAFE; C4=({sh(n) for n in C4}|{75})-SAFE
G={9,50,63,64,74,80}
REF={1,3,5,7,8,9,12,13,14,15,16,17,19,20,21,22,27,30,31,32,33,34,35,36,37,38,40,52,53,54,55,56,57,59,60,61,63,64,65,66,67,70,75,76,77,78,79,81}
assert len(REF)==48
R='/home/user/St0nys-WoW-EXE-Patcher/'
T={'de':('Bann-Gefahr','auf öffentlichen Servern ungetestet','im Spiel ungetestet','auf öffentlichen Servern und im Spiel ungetestet','Exe wird größer','sicher'),
   'en':('ban risk','untested on public servers','untested in game','untested on public servers and in game','exe grows','safe')}
def badges(n,t):
    b=[]
    if n in C2: b.append('🔴 **[%s]**'%t[0])
    if n in C3 and n in C4: b.append('🟠 **[%s]**'%t[3])
    elif n in C3: b.append('🟠 **[%s]**'%t[1])
    elif n in C4: b.append('🟠 **[%s]**'%t[2])
    if not b: b.append('🟢 **[%s]**'%t[5])
    if n in G: b.append('🟡 **[%s]**'%t[4])
    return ' '.join(b)
BADGE=re.compile(r' (?:🔴|🟡|🟢|🟠) \*\*\[[^\]]*\]\*\*')
WARNBOX=re.compile(r'\n> \[!WARNING\]\n> \*\*(?:Auf öffentlichen Servern ungetestet|Im Spiel ungetestet|Untested on public servers|Untested in game)\*\*[^\n]*\n(?:>\n> \*\*(?:Im Spiel ungetestet|Untested in game)\*\*[^\n]*\n)?')
for fn,lang,kind in (('README.md','en','r'),('README.de.md','de','r'),('PATCHES.md','de','p'),('PATCHES.en.md','en','p')):
    L=open(R+fn,encoding='utf-8').read().split('\n'); cnt=0
    for i,l in enumerate(L):
        if kind=='r':
            m=re.match(r'\| \[(\d+)\]\(PATCHES',l)
            if m:
                n=int(m.group(1)); cells=l.split(' | ')
                cells[1]=BADGE.sub('',cells[1])+' '+badges(n,T[lang])
                assert len(cells)==6,(fn,n,len(cells))
                cells[3]='✅' if n in REF else '–'
                L[i]=' | '.join(cells); cnt+=1
        else:
            if i>0 and L[i-1].startswith('<a id="patch-'):
                n=int(re.search(r'\*\((?:Nr\.|No\.) (\d+)[,)]',l).group(1))
                L[i]=BADGE.sub('',l)+' '+badges(n,T[lang]); cnt+=1
                if n in SAFE: L[i]+='\x00'
    assert cnt==86,(fn,cnt)
    s='\n'.join(L)
    if kind=='p':
        # remove the standard warning box right after headers of now-safe patches
        def rm(m): return m.group(1)+'\n'
        s,k=re.subn('\x00\n'+WARNBOX.pattern, lambda m:'\n', s)
        assert k==7,(fn,k); assert '\x00' not in s
    open(R+fn,'w',encoding='utf-8').write(s)

import re
from codes import *
G={9,50,63,64,74,79}
R='/home/user/St0nys-WoW-EXE-Patcher/'
cfg={
 'README.md':dict(lang='en',
   strip={"detectable through Warden on public servers – ban risk":None,
     "may get you kicked if Warden is active, ban risk on public servers":None,
     "may be treated as botting – ban risk":None,
     "asks for the value, may be detected as cheating by the server, exe grows – ban risk":"asks for the value",
     "asks for the value, may be detected as cheating by the server – ban risk":"asks for the value",
     "may be detected as cheating by the server – ban risk":None,
     "may be treated as automation (botting) by the server, exe grows – ban risk":None,
     "shoulder offset has no effect yet; exe grows – ban risk":"shoulder offset has no effect yet",
     "exe grows – ban risk":None},
   unt=" – untested", tags=('ban risk','untested on public servers','untested in game','untested on public servers and in game','exe grows')),
 'README.de.md':dict(lang='de',
   strip={"auf öffentlichen Servern über Warden erkennbar – Bann-Gefahr":None,
     "Kick-Gefahr bei aktivem Warden, auf öffentlichen Servern Bann-Gefahr":None,
     "kann als Botting gewertet werden – Bann-Gefahr":None,
     "fragt den Wert ab, kann vom Server als Cheat erkannt werden, Exe wird größer – Bann-Gefahr":"fragt den Wert ab",
     "fragt den Wert ab, kann vom Server als Cheat erkannt werden – Bann-Gefahr":"fragt den Wert ab",
     "kann vom Server als Cheat erkannt werden – Bann-Gefahr":None,
     "kann vom Server als Automatisierung (Bot) gewertet werden, Exe wird größer – Bann-Gefahr":None,
     "Schulterversatz noch ohne Wirkung; Exe wird größer – Bann-Gefahr":"Schulterversatz noch ohne Wirkung",
     "Exe wird größer – Bann-Gefahr":None},
   unt=" – ungetestet", tags=('Bann-Gefahr','auf öffentlichen Servern ungetestet','im Spiel ungetestet','auf öffentlichen Servern und im Spiel ungetestet','Exe wird größer')),
}
for fn,c in cfg.items():
    L=open(R+fn,encoding='utf-8').read().split('\n')
    seen=set()
    for i,l in enumerate(L):
        m=re.match(r"\| \[(\d+)\]\(PATCHES(?:\.en)?\.md#patch-[a-z0-9]+\) \| (.*?) \| ",l)
        if not m: continue
        n=int(m.group(1)); cell=m.group(2); seen.add(n)
        new=cell.replace(c['unt'],'')
        for a,b in c['strip'].items():
            if f"*({a})*" in new:
                new=new.replace(f"*({a})*", f"*({b})*" if b else '').rstrip()
        assert 'ban' not in new.lower() and 'ungetestet' not in new and 'untested' not in new, (fn,n,new)
        t=c['tags']; tags=[]
        if n in C2: tags.append(t[0])
        if n in C3 and n in C4: tags.append(t[3])
        elif n in C3: tags.append(t[1])
        elif n in C4: tags.append(t[2])
        if n in G: tags.append(t[4])
        if tags:
            emo='🔴' if n in C2 else '🟡'
            new=f"{new} {emo} **[{', '.join(tags)}]**"
        L[i]=l.replace(f"| {cell} | ",f"| {new} | ",1)
    assert seen==set(range(1,86)),(fn,set(range(1,86))-seen)
    open(R+fn,'w',encoding='utf-8').write('\n'.join(L))

import re
from codes import *
G={9,50,63,64,74,79}
R='/home/user/St0nys-WoW-EXE-Patcher/'
cfg={
 'PATCHES.md':dict(unt=" – ungetestet",nr="Nr.",
   tags=('Bann-Gefahr','auf öffentlichen Servern ungetestet','im Spiel ungetestet','auf öffentlichen Servern und im Spiel ungetestet','Exe wird größer'),
   box={2:"**Bann-Gefahr** – kann auf vielen Servern zu einem Bann führen. Nur auf Servern nutzen, die das erlauben.",
        3:"**Auf öffentlichen Servern ungetestet** – mögliche Bann-Gefahr. Vorsicht, kann zu Kick/Bann führen.",
        4:"**Im Spiel ungetestet** – die Funktion ist im Spiel noch nicht geprüft, möglicherweise verbuggt."},
   fix=[("> Patch standardmäßig abgewählt. Der Patch selbst ist im Spiel getestet.\n","> Patch standardmäßig abgewählt.\n"),
        ("> v2 ist im Spiel getestet. Die Patch-Liste von v1, aus der dieser Patch\n> übernommen wurde,","> Die Patch-Liste von v1, aus der dieser Patch übernommen wurde,")]),
 'PATCHES.en.md':dict(unt=" – untested",nr="No.",
   tags=('ban risk','untested on public servers','untested in game','untested on public servers and in game','exe grows'),
   box={2:"**Ban risk** – can lead to a ban on many servers. Only use it on servers that allow it.",
        3:"**Untested on public servers** – possible ban risk. Careful, it may get you kicked or banned.",
        4:"**Untested in game** – the function has not been checked in game yet, possibly buggy."},
   fix=[]),
}
for fn,c in cfg.items():
    s=open(R+fn,encoding='utf-8').read()
    for a,b in c['fix']:
        assert s.count(a)==1,(fn,a); s=s.replace(a,b)
    L=s.split('\n'); out=[]; seen=set()
    i=0
    while i<len(L):
        l=L[i]; out.append(l)
        if l.startswith('<a id="patch-'):
            h=L[i+1]
            m=re.search(r"\*\("+re.escape(c['nr'])+r" (\d+)[,)]",h); n=int(m.group(1)); seen.add(n)
            h=h.replace(c['unt']+"**","**")
            t=c['tags']; tags=[]
            if n in C2: tags.append(t[0])
            if n in C3 and n in C4: tags.append(t[3])
            elif n in C3: tags.append(t[1])
            elif n in C4: tags.append(t[2])
            if n in G: tags.append(t[4])
            if tags: h=f"{h} {'🔴' if n in C2 else '🟡'} **[{', '.join(tags)}]**"
            out.append(h); i+=2
            box=[c['box'][k] for k in (2,3,4) if n in {2:C2,3:C3,4:C4}[k]]
            if box:
                assert L[i]=='',(fn,n)
                out.append('')
                out.append('> [!CAUTION]' if n in C2 else '> [!WARNING]')
                out.append('> '+'\n>\n> '.join(box))
            continue
        i+=1
    assert seen==set(range(1,86)),(fn,set(range(1,86))-seen)
    open(R+fn,'w',encoding='utf-8').write('\n'.join(out))

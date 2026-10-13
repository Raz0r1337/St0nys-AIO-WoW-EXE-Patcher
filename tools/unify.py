import re,sys
d=sys.argv[1]; NBOX=int(sys.argv[2])
RANK={'🔴':4,'🟠':3,'🟡':2,'🟢':1}
DOT='(?:🔴|🟠|🟡|🟢)'
def rd(fn):
    raw=open(d+'/'+fn,'rb').read(); assert b'\r\n' not in raw,fn
    return raw.decode('utf-8')
def wr(fn,t): open(d+'/'+fn,'w',encoding='utf-8',newline='\n').write(t)
def once(t,a,b,fn):
    assert t.count(a)==1,(fn,a[:70],t.count(a)); return t.replace(a,b)

# --- README: Uebersicht ---
def cell(m):
    d1,a,d2,b=m.group(1),m.group(2),m.group(3),m.group(4)
    dot=max([d1]+([d2] if d2 else []),key=lambda x:RANK[x])
    return '%s **[%s - %s]**'%(dot,a,b)
SENT={'README.de.md':('''Ein Patch kann mehrere Kennzeichnungen tragen, z. B. **[sicher]** und
**[Exe wird größer]**. In der Übersicht hat jeder Patch nur einen Punkt: Bei
sicheren Patches, die die Exe vergrößern, wird der grüne Punkt gelb
(🟡 **[sicher]** **[Exe wird größer]**), rote und orange Punkte bleiben.
''','''Ein Patch kann mehrere Kennzeichnungen tragen. Sie stehen dann zusammen in
einer Klammer, und davor steht nur ein Punkt: Der strengere gewinnt (Rot vor
Orange vor Gelb), ein grüner Punkt wird gelb, wenn die Exe größer wird. Zum
Beispiel 🟡 **[sicher - Exe wird größer]**, 🔴 **[unsicher - Exe wird größer]**,
🟠 **[ungetestet - Exe wird größer]** oder 🔴 **[unsicher - ingame ungetestet]**.
'''),'README.md':('''A patch can carry several ratings, e.g. **[safe]** and **[exe grows]**.
In the overview each patch has only one dot: for safe patches that grow
the exe the green dot turns yellow (🟡 **[safe]** **[exe grows]**); red
and orange dots stay.
''','''A patch can carry several ratings. They then share one pair of brackets
with a single dot in front: the stricter one wins (red before orange before
yellow), and a green dot turns yellow when the exe grows. For example
🟡 **[safe - exe grows]**, 🔴 **[unsafe - exe grows]**,
🟠 **[untested - exe grows]** or 🔴 **[unsafe - untested ingame]**.
''')}
for fn in ('README.de.md','README.md'):
    t=rd(fn)
    t,n=re.subn(r'(%s) \*\*\[([^\]]+)\]\*\*<br>(?:(%s) )?\*\*\[([^\]]+)\]\*\*'%(DOT,DOT),cell,t)
    assert '<br>' not in ''.join(l for l in t.splitlines() if l.startswith('| [')),fn
    t=once(t,*SENT[fn],fn)
    wr(fn,t); print(fn,'cells',n)

# --- PATCHES ---
STD={'de':r'> \*\*(?:Unsicher|Online ungetestet|Ingame ungetestet)\*\* – [^\n]*\n',
     'en':r'> \*\*(?:Unsafe|Untested online|Untested ingame)\*\* – [^\n]*\n'}
def head(m):
    tags=re.findall(r'(%s) \*\*\[([^\]]+)\]\*\*'%DOT,m.group(2))
    if len(tags)<2: return m.group(0)
    dot=max((x for x,_ in tags),key=lambda x:RANK[x])
    return '%s %s **[%s]**'%(m.group(1),dot,' - '.join(y for _,y in tags))
GROW={'de':[
 ('''> [!WARNING]
> Der Patch hängt eine Sektion an – die `Wow.exe` wird größer. Das ist keine
> sichere Bann-Gefahr, aber ein Risiko: Manche Server prüfen die Dateigröße.

''',''),
 ('''> Bann führen.
>
> Dieser Patch hängt eine eigene Sektion an, die `Wow.exe` wird dadurch größer.
> Das ist keine sichere Bann-Gefahr, aber ein Risiko: Manche Server prüfen die
> Dateigröße der `Wow.exe`.
''','''> Bann führen.
'''),
 ('''> [!WARNING]
> Dieser Patch hängt eine neue PE-Sektion `.hdp` an die `Wow.exe` an (generierte
> 256er-Alphamaske + Code-Höhlen + Detour des Masken-Builders), die Datei wächst
> dadurch um ca. 69 KB. Das ist keine sichere Bann-Gefahr, aber ein Risiko:
> Manche Server prüfen die Dateigröße der `Wow.exe`.
''','''Der Patch hängt eine neue PE-Sektion `.hdp` an die `Wow.exe` an (generierte
256er-Alphamaske + Code-Höhlen + Detour des Masken-Builders), die Datei wächst
dadurch um ca. 69 KB.
'''),
 ('''> [!WARNING]
> Der Patch hängt eine kleine Sektion an (`.isnap`, 179 Byte) – die `Wow.exe`
> wird größer. Das ist keine sichere Bann-Gefahr, aber ein Risiko: Manche
> Server prüfen die Dateigröße.
''','''Der Code liegt in einer eigenen kleinen Sektion (`.isnap`, 179 Byte).
'''),
 ('''> Server verbieten „ein Tastendruck = mehrere Aktionen“. Außerdem hängt der
> Patch eine Sektion an – die `Wow.exe` wird größer (Bann-Gefahr).
''','''> Server verbieten „ein Tastendruck = mehrere Aktionen“.
'''),
 ('''> [!WARNING]
> Dieser Patch hängt wie die HD-Portraits eine eigene Sektion an (etwa +1 KB),
> die `Wow.exe` wird dadurch größer. Das ist keine sichere Bann-Gefahr, aber
> ein Risiko: Manche Server prüfen die Dateigröße der `Wow.exe`.

''',''),
 ('''Preset-Zuordnung steht in der [README](README.de.md#patch-übersicht).
''','''Preset-Zuordnung steht in der [README](README.de.md#patch-übersicht). Dort
steht auch, was die Kennzeichnungen hinter den Namen bedeuten, z. B.
🔴 **[unsicher]** oder 🟡 **[sicher - Exe wird größer]**.
''')],
'en':[
 ('''> [!WARNING]
> The patch appends a section – `Wow.exe` gets larger. This does not mean a certain
> ban, but it is a risk: some servers check the file size.

''',''),
 ('''> Servers with anti-cheat may detect jumps in the air – this can lead to a ban.
>
> This patch appends a section of its own, which makes `Wow.exe` larger.
> This does not mean a certain ban, but it is a risk: some servers check the file size
> of `Wow.exe`.
''','''> Servers with anti-cheat may detect jumps in the air – this can lead to a ban.
'''),
 ('''> [!WARNING]
> This patch appends a new PE section `.hdp` to `Wow.exe` (generated 256px alpha
> mask + code caves + detour of the mask builder), the file grows by about
> 69 KB. This does not mean a certain ban, but it is a risk: some servers check the
> file size of `Wow.exe`.
''','''The patch appends a new PE section `.hdp` to `Wow.exe` (generated 256px alpha
mask + code caves + detour of the mask builder), the file grows by about
69 KB.
'''),
 ('''> [!WARNING]
> The patch appends a small section (`.isnap`, 179 bytes) – `Wow.exe` gets
> larger. This does not mean a certain ban, but it is a risk: some servers check the
> file size.
''','''The code lives in a small section of its own (`.isnap`, 179 bytes).
'''),
 ('''> servers forbid "one key press = several actions". In addition, the patch
> appends a section – `Wow.exe` gets larger (ban risk).
''','''> servers forbid "one key press = several actions".
'''),
 ('''> [!WARNING]
> Like the HD portraits, this patch appends a section of its own (about +1 KB),
> which makes `Wow.exe` larger. This does not mean a certain ban, but it is a risk: some
> servers check the file size of `Wow.exe`.

''',''),
 ('''preset assignment is in the [README](README.md#patch-overview).
''','''preset assignment is in the [README](README.md#patch-overview). It also
explains what the ratings after the names mean, e.g. 🔴 **[unsafe]** or
🟡 **[safe - exe grows]**.
''')]}
for fn,lang in (('PATCHES.de.md','de'),('PATCHES.en.md','en')):
    t=rd(fn)
    # Kaesten, die nur die Legende wiederholen
    box=r'(?m)^> \[!(?:CAUTION|WARNING)\]\n(?:%s(?:>\n%s)*)\n'%(STD[lang],STD[lang])
    t,nb=re.subn(box,'',t)
    assert nb==NBOX,(fn,nb)
    assert not re.search(r'(?m)^'+STD[lang],t),fn
    for a,b in GROW[lang]: t=once(t,a,b,fn)
    t,nh=re.subn(r'(?m)^(\*\*.+?\*\* \*\((?:Nr\.|No\.) \d+[^\n]*?\)\*)((?: %s \*\*\[[^\]]+\]\*\*)+)$'%DOT,head,t)
    t=re.sub(r'\n{3,}','\n\n',t)
    wr(fn,t); print(fn,'boxes',nb,'headings',nh)

# --- Patcher ---
p=d+'/apply_patches.ps1'; raw=open(p,'rb').read()
a=b"    if ($tags.Count -gt 0) { $n = \"$n [$($tags -join ', ')]\" }"
assert raw.count(a)==1
raw=raw.replace(a,a.replace(b"', '",b"' - '"))
open(p,'wb').write(raw); print('ps1 ok')

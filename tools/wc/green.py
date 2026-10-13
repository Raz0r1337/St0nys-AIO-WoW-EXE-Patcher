import re
from codes import *
R='/home/user/St0nys-WoW-EXE-Patcher/'
def edit(fn,pairs):
    s=open(R+fn,encoding='utf-8').read()
    for a,b in pairs:
        assert s.count(a)==1,(fn,a[:70],s.count(a)); s=s.replace(a,b)
    open(R+fn,'w',encoding='utf-8').write(s)
def move_box(fn,click,summary):
    s=open(R+fn,encoding='utf-8').read()
    i=s.index('> [!IMPORTANT]\n> **W', s.index('## Patch'))
    j=s.index(click)
    box=s[i:j]  # box + blank line
    s=s[:i]+s[j:]
    k=s.index(summary)+len(summary)
    assert s[k:k+2]=='\n\n'
    s=s[:k+2]+box+s[k+2:]
    open(R+fn,'w',encoding='utf-8').write(s)
def green(fn,tag,anchor_re,nr_re):
    L=open(R+fn,encoding='utf-8').read().split('\n'); cnt=0
    for i,l in enumerate(L):
        m=re.match(anchor_re,l)
        if m:
            n=int(m.group(1))
            if n in C1:
                if fn.startswith('README'):
                    cell=l.split(' | ')[1]
                    L[i]=l.replace(' | '+cell+' | ',' | '+cell+' '+tag+' | ',1)
                else:
                    L[i]=l+' '+tag
                cnt+=1
    assert cnt==len(C1),(fn,cnt)
    open(R+fn,'w',encoding='utf-8').write('\n'.join(L))
# --- DE ---
edit('README.de.md',[
("""> **Was die Warnungen bedeuten** – sie stehen hinter dem Namen eines Patches,
> im Patcher in eckigen Klammern:
>
> - **ohne Warnung** – **sicher**: im Spiel getestet, keine Warnung und kein
>   Hinweis.""","""> **Was die Einstufungen bedeuten** – sie stehen hinter dem Namen eines
> Patches. Der Patcher zeigt die Warnungen in eckigen Klammern, sichere Patches
> stehen dort ohne Zusatz:
>
> - 🟢 **[sicher]** – **sicher**: im Spiel getestet, keine Warnung und kein
>   Hinweis."""),
("""> **Benutzung auf eigene Gefahr.** Patches ohne Warnung sind im Spiel getestet
> und sollten auch auf öffentlichen Servern unbedenklich sein – eine""","""> **Benutzung auf eigene Gefahr.** Als sicher (🟢) eingestufte Patches sind im
> Spiel getestet und sollten auch auf öffentlichen Servern unbedenklich sein – eine"""),
("""Patches ohne Warnung, die die `Wow.exe` nicht vergrößern – **das Preset ist""","""sichere Patches (🟢), die die `Wow.exe` nicht vergrößern – **das Preset ist"""),
("""  - **ohne Warnung** – sicher, im Spiel getestet.""","""  - 🟢 **sicher** – im Spiel getestet, im Patcher ohne Warnung."""),
])
edit('README.md',[
("""> **What the warnings mean** – they are shown after the name of a patch, in
> the patcher in square brackets:
>
> - **no warning** – **safe**: tested in game, no warning and no note.""","""> **What the ratings mean** – they are shown after the name of a patch. The
> patcher shows the warnings in square brackets, safe patches have no addition
> there:
>
> - 🟢 **[safe]** – **safe**: tested in game, no warning and no note."""),
("""> **Use at your own risk.** Patches without a warning have been tested in game
> and should be harmless on public servers as well – but there is no 100 %""","""> **Use at your own risk.** Patches rated safe (🟢) have been tested in game and
> should be harmless on public servers as well – but there is no 100 %"""),
("""without a warning that do not make `Wow.exe` larger – **the preset is safe** and""","""rated safe (🟢) that do not make `Wow.exe` larger – **the preset is safe** and"""),
("""  - **no warning** – safe, tested in game.""","""  - 🟢 **safe** – tested in game, no warning in the patcher."""),
])
move_box('README.de.md',"Ein Klick auf die Nummer eines Patches springt zu seiner Beschreibung.\n",
         "<summary><b>Übersicht aller Patches mit Autor und Preset-Zuordnung anzeigen</b></summary>\n")
move_box('README.md',"Click the number of a patch to jump to its description.\n",
         "<summary><b>Show all patches with author and preset assignment</b></summary>\n")
green('README.de.md','🟢 **[sicher]**',r"\| \[(\d+)\]\(PATCHES\.md#",None)
green('README.md','🟢 **[safe]**',r"\| \[(\d+)\]\(PATCHES\.en\.md#",None)
# PATCHES headers: line after anchor
for fn,tag,nr in [('PATCHES.md','🟢 **[sicher]**','Nr.'),('PATCHES.en.md','🟢 **[safe]**','No.')]:
    L=open(R+fn,encoding='utf-8').read().split('\n'); cnt=0
    for i,l in enumerate(L):
        if L[i-1].startswith('<a id="patch-'):
            n=int(re.search(r"\*\("+re.escape(nr)+r" (\d+)[,)]",l).group(1))
            if n in C1: L[i]=l+' '+tag; cnt+=1
    assert cnt==len(C1); open(R+fn,'w',encoding='utf-8').write('\n'.join(L))

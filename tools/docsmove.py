import sys,re
d=sys.argv[1]
def fix(fn,rows):
    p=d+'/docs/'+fn; t=open(p,encoding='utf-8').read()
    assert '\r\n' not in t
    for a,b in rows:
        assert t.count(a)==1,(fn,a); t=t.replace(a,b)
    assert t.count('](LICENSE)')==1; t=t.replace('](LICENSE)','](../LICENSE)')
    open(p,'w',encoding='utf-8',newline='\n').write(t); print(fn,'ok')
fix('README.md',[
 ("| `README.md`         | This file |","| `docs/README.md`    | This file |"),
 ("| `README.de.md`      | German documentation |","| `docs/README.de.md` | German documentation |"),
 ("| `PATCHES.de.md`     | Detailed patch descriptions in German |","| `docs/PATCHES.de.md` | Detailed patch descriptions in German |"),
 ("| `PATCHES.en.md`     | Detailed descriptions of all patches |","| `docs/PATCHES.en.md` | Detailed descriptions of all patches |")])
fix('README.de.md',[
 ("| `README.md`         | Englische Anleitung |","| `docs/README.md`    | Englische Anleitung |"),
 ("| `README.de.md`      | Diese Datei |","| `docs/README.de.md` | Diese Datei |"),
 ("| `PATCHES.de.md`     | Ausführliche Beschreibungen aller Patches |","| `docs/PATCHES.de.md` | Ausführliche Beschreibungen aller Patches |"),
 ("| `PATCHES.en.md`     | Patch-Beschreibungen auf Englisch |","| `docs/PATCHES.en.md` | Patch-Beschreibungen auf Englisch |")])

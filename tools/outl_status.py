import sys
d=sys.argv[1]
def edit(fn,pairs,binary_crlf=False):
    p=d+'/'+fn
    raw=open(p,'rb').read(); crlf=b'\r\n' in raw
    t=raw.decode('utf-8')
    if crlf: t=t.replace('\r\n','\n')
    for a,b in pairs:
        assert t.count(a)==1,(fn,a[:80],t.count(a)); t=t.replace(a,b)
    if crlf: t=t.replace('\n','\r\n')
    open(p,'wb').write(t.encode('utf-8'))
    print(fn,'crlf' if crlf else 'lf')
WD_DE=">\n> **Ingame ungetestet** – die Funktion ist im Spiel noch nicht geprüft, möglicherweise verbuggt.\n\nWie in Retail"
WD_EN=">\n> **Untested ingame** – the function has not been checked in game yet, possibly buggy.\n\nLike retail"
edit('apply_patches.ps1',[
 ("#  Umrandung fuer Ziel und Mouseover (Proof of Concept, St0ny)","#  Umrandung fuer Ziel und Mouseover (St0ny)"),
 ("@{ Id = 'outline'; Cat = 'graphics'; On = $false; GrowsExe = $true; PublicUntested = $true; GameUntested = $true",
  "@{ Id = 'outline'; Cat = 'graphics'; On = $false; GrowsExe = $true; PublicUntested = $true"),
 ("De = 'Umrandung fuer Ziel und Mouseover (Proof of Concept)'","De = 'Umrandung fuer Ziel und Mouseover'"),
 ("En = 'Outline for target and mouseover (proof of concept)'","En = 'Outline for target and mouseover'"),
])
edit('README.de.md',[
 ("Umrandung für Ziel und Mouseover (Proof of Concept) *(nur gxApi d3d9)* | 🟠 **[ungetestet]**","Umrandung für Ziel und Mouseover *(nur gxApi d3d9)* | 🟠 **[online ungetestet]**"),
 ("möglicherweise verbuggt: Nr. 25, 26, 29, 44, 51, 62 und 65 (rote Warnung).","möglicherweise verbuggt: Nr. 25, 26, 29, 44, 51 und 62 (rote Warnung)."),
])
edit('README.md',[
 ("Outline for target and mouseover (proof of concept) *(gxApi d3d9 only)* | 🟠 **[untested]**","Outline for target and mouseover *(gxApi d3d9 only)* | 🟠 **[untested online]**"),
 ("possibly buggy: No. 25, 26, 29, 44, 51, 62 and 65 (red warning).","possibly buggy: No. 25, 26, 29, 44, 51 and 62 (red warning)."),
])
edit('PATCHES.de.md',[
 ("**Umrandung für Ziel und Mouseover (Proof of Concept)** *(Nr. 65, Autor: St0ny)* 🟠 **[ungetestet]**","**Umrandung für Ziel und Mouseover** *(Nr. 65, Autor: St0ny)* 🟠 **[online ungetestet]**"),
 (WD_DE,"\nWie in Retail"),
 ("Mit\n> DXVK sollte er funktionieren, weil WoW auch dort Direct3D 9 nutzt.","Mit\n> DXVK funktioniert er ebenfalls (im Spiel getestet), weil WoW auch dort\n> Direct3D 9 nutzt."),
])
edit('PATCHES.en.md',[
 ("**Outline for target and mouseover (proof of concept)** *(No. 65, Author: St0ny)* 🟠 **[untested]**","**Outline for target and mouseover** *(No. 65, Author: St0ny)* 🟠 **[untested online]**"),
 (WD_EN,"\nLike retail"),
 ("It\n> should work with DXVK, because WoW uses Direct3D 9 there as well.","It\n> works with DXVK as well (tested in game), because WoW uses Direct3D 9 there\n> as well."),
])

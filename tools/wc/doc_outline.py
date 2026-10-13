import re,os
os.chdir('/home/user/St0nys-WoW-EXE-Patcher')
sh=lambda n: str(int(n)+1 if int(n)>=65 else int(n))
def refs(s):
    pat=re.compile(r'(Nr\.|No\.) (\d+)((?:, \d+)*)((?: (?:und|and) (?:Nr\. |No\. )?)(\d+))?')
    def f(m):
        out=m.group(1)+' '+sh(m.group(2))
        if m.group(3): out+=re.sub(r'\d+',lambda x: sh(x.group(0)),m.group(3))
        if m.group(4): out+=m.group(4)[:-len(m.group(5))]+sh(m.group(5))
        return out
    return pat.sub(f,s)
def table(s,md): return re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(sh(m.group(1)),md), s)
def once(s,a,b):
    assert s.count(a)==1,(a[:80],s.count(a)); return s.replace(a,b)
LISTS={'README.de.md':[
 ("11, 23–25, 41, 42, 45–50, 74 und 82–86 (rote Warnung).","11, 23–25, 41, 42, 45–50, 75 und 83–87 (rote Warnung)."),
 ("Nr. 4, 26, 29, 39, 44, 51, 62, 68, 71–73 und 80 (rote\n    Warnung).","Nr. 4, 26, 29, 39, 44, 51, 62, 65, 69, 72–74 und 81\n    (rote Warnung)."),
 ("Nr. 25, 26, 29, 44, 51 und 62 (rote Warnung).","Nr. 25, 26, 29, 44, 51, 62 und 65 (rote Warnung)."),
 ("Nr. 9, 50, 63, 64, 74 und 80. Das ist","Nr. 9, 50, 63–65, 75 und 81. Das ist"),
 ("(Nr. 9, 50, 63, 64, 74 und 80), entfernen","(Nr. 9, 50, 63–65, 75 und 81), entfernen")],
 'README.md':[
 ("41, 42, 45–50, 74 and 82–86 (red warning).","41, 42, 45–50, 75 and 83–87 (red warning)."),
 ("No. 4, 26, 29, 39, 44, 51, 62, 68, 71–73 and 80 (red\n    warning).","No. 4, 26, 29, 39, 44, 51, 62, 65, 69, 72–74 and 81\n    (red warning)."),
 ("No. 25, 26, 29, 44, 51 and 62 (red warning).","No. 25, 26, 29, 44, 51, 62 and 65 (red warning)."),
 ("No. 9, 50,\n    63, 64, 74 and 80. This","No. 9, 50,\n    63–65, 75 and 81. This"),
 ("(No. 9, 50, 63, 64, 74 and 80) also remove","(No. 9, 50, 63–65, 75 and 81) also remove")]}
ROW={'de':'| [65](PATCHES.de.md#patch-outline) | Umrandung für Ziel und Mouseover (Proof of Concept) *(nur gxApi d3d9)* | 🟠 **[ungetestet]**<br>🟡 **[Exe wird größer]** | St0ny | – | – | – |\n',
     'en':'| [65](PATCHES.en.md#patch-outline) | Outline for target and mouseover (proof of concept) *(gxApi d3d9 only)* | 🟠 **[untested]**<br>🟡 **[exe grows]** | St0ny | – | – | – |\n'}
SEC={'de':'''<a id="patch-outline"></a>
**Umrandung für Ziel und Mouseover (Proof of Concept)** *(Nr. 65, Autor: St0ny)* 🟠 **[ungetestet]** 🟡 **[Exe wird größer]**

> [!WARNING]
> **Online ungetestet** – nicht auf öffentlichen Servern getestet, mögliche Bann-Gefahr. Vorsicht, kann zu Kick/Bann führen.
>
> **Ingame ungetestet** – die Funktion ist im Spiel noch nicht geprüft, möglicherweise verbuggt.

Wie in Retail bekommt die 3D-Figur des markierten Ziels und die Figur unter
dem Mauszeiger eine dünne Umrandung (etwa 2 Pixel) in ihrer Gesinnungsfarbe –
dieselbe Farbe wie der Auswahlkreis: rot feindlich, gelb neutral, grün
freundlich. Der Rand erscheint nur dort, wo die Figur sichtbar ist; steht eine
Wand davor, bekommt sie dort keinen Rand. Waffen, Helm und Reittier gehören
mit zur Figur.

So funktioniert es:
- Der Tiefenpuffer bekommt einen Stencil-Anteil (D24S8 statt D24X8). Das Spiel
  selbst nutzt Stencil nirgends.
- Beim Zeichnen der Figur werden ihre sichtbaren Pixel im Stencil markiert.
  Danach wird sie noch achtmal unsichtbar gezeichnet, je um 2 Pixel in alle
  Richtungen verschoben (über die Projektionsmatrix des Shaders), mit
  Tiefentest – diese Kopien markieren den Rand.
- Nach den Modellen und vor dem Interface färbt eine bildschirmfüllende Fläche
  nur die Rand-Pixel ein; danach wird der Stencil geleert und das Spiel setzt
  alle Grafik-Einstellungen neu.
- Code und Daten liegen in einer eigenen Sektion (`.outl`, 0x880 Byte).

> [!NOTE]
> Nur mit `gxApi d3d9` (Standard) und 24-Bit-Tiefenpuffer (Standard). Mit
> D3D9Ex, OpenGL oder `gxDepthBits` 16/32 schaltet sich der Patch ab. Mit
> DXVK sollte er funktionieren, weil WoW auch dort Direct3D 9 nutzt.

> [!NOTE]
> Sind alle Patches mit eigener Sektion gleichzeitig aktiv, ist im PE-Header
> kein Platz mehr für einen weiteren Sektionseintrag. Dann verlängert der
> Patcher die zuletzt angehängte Sektion, statt eine neue anzulegen.

''','en':'''<a id="patch-outline"></a>
**Outline for target and mouseover (proof of concept)** *(No. 65, Author: St0ny)* 🟠 **[untested]** 🟡 **[exe grows]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

Like in retail, the 3D figure of your target and the figure under the mouse
cursor get a thin outline (about 2 pixels) in their reaction color – the same
color as the selection circle: red hostile, yellow neutral, green friendly. The
outline only appears where the figure is visible; where a wall stands in front
of it, there is no outline. Weapons, helmet and mount belong to the figure.

How it works:
- The depth buffer gets a stencil part (D24S8 instead of D24X8). The game
  itself never uses stencil.
- While the figure is drawn, its visible pixels are marked in the stencil.
  Then it is drawn eight more times invisibly, each shifted by 2 pixels in
  every direction (via the shader's projection matrix), with depth test –
  these copies mark the outline.
- After the models and before the interface, a full-screen quad colors only
  the outline pixels; then the stencil is cleared and the game sends all its
  graphics states again.
- Code and data live in a section of their own (`.outl`, 0x880 bytes).

> [!NOTE]
> Only with `gxApi d3d9` (default) and a 24-bit depth buffer (default). With
> D3D9Ex, OpenGL or `gxDepthBits` 16/32 the patch switches itself off. It
> should work with DXVK, because WoW uses Direct3D 9 there as well.

> [!NOTE]
> If all patches with a section of their own are active at the same time,
> there is no room left in the PE header for another section entry. Then the
> patcher extends the last appended section instead of adding a new one.

'''}
for fn,md,lang in (('README.de.md','PATCHES.de.md','de'),('README.md','PATCHES.en.md','en')):
    s=open(fn,encoding='utf-8').read()
    PH={}
    for k,(a,b) in enumerate(LISTS[fn]):
        s=once(s,a,'@@L%d@@'%k); PH['@@L%d@@'%k]=b
    s=table(s,md); s=refs(s)
    for k,v in PH.items(): s=s.replace(k,v)
    i=s.index('](%s#patch-iconsnap)'%md); j=s.index('\n',i)+1; s=s[:j]+ROW[lang]+s[j:]
    open(fn,'w',encoding='utf-8',newline='\n').write(s)
for fn,lang,head in (('PATCHES.de.md','de','## Interface & Komfort'),('PATCHES.en.md','en','## Interface & comfort')):
    s=open(fn,encoding='utf-8').read()
    s=refs(s)
    s=once(s,'\n'+head+'\n','\n'+SEC[lang]+head+'\n')
    open(fn,'w',encoding='utf-8',newline='\n').write(s)

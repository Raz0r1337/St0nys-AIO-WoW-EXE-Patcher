import re,sys
d=sys.argv[1]
sh=lambda n: str(int(n)+1 if 66<=int(n)<=87 else int(n))
def once(s,a,b):
    assert s.count(a)==1,(a[:90],s.count(a)); return s.replace(a,b)
def table(s,md): return re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(sh(m.group(1)),md), s)
def refs(s):
    # one pass: "Nr. N", "No. N" plus a bare second number after "und"/"and"
    def f(m):
        out='%s %s'%(m.group(1),sh(m.group(2)))
        if m.group(3): out+=m.group(3)+sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?![\d.])(?:( (?:und|and) )(\d+)(?!\d))?',f,s)
def rowrefs(s):
    return re.sub(r'(?m)^\| \[\d+\]\(.*$',lambda m: refs(m.group(0)),s)
ROW={'de':'| [66](PATCHES.de.md#patch-lightstay) | Lichter bleiben an, wenn ihre Quelle außerhalb des Bildes ist | 🟠 **[ungetestet]** | St0ny | – | – | – |\n',
     'en':'| [66](PATCHES.en.md#patch-lightstay) | Lights stay on when their source is off-screen | 🟠 **[untested]** | St0ny | – | – | – |\n'}
SEC={'de':"""<a id="patch-lightstay"></a>
**Lichter bleiben an, wenn ihre Quelle außerhalb des Bildes ist** *(Nr. 66, Autor: St0ny)* 🟠 **[ungetestet]**

> [!WARNING]
> **Online ungetestet** – nicht auf öffentlichen Servern getestet, mögliche Bann-Gefahr. Vorsicht, kann zu Kick/Bann führen.
>
> **Ingame ungetestet** – die Funktion ist im Spiel noch nicht geprüft, möglicherweise verbuggt.

Behebt einen Fehler des Original-Clients: Dreht man die Kamera so, dass eine
Lichtquelle (z. B. eine Fackel) aus dem Bild rutscht, verschwindet ihr Licht
auch auf allem, was noch zu sehen ist – etwa auf der eigenen Figur direkt
daneben. Das passiert mit und ohne Shader.

Ursache: Punktlichter hängen an Modellen. Ihr Zeitstempel wird nur gesetzt,
wenn das Modell im aktuellen Bild gezeichnet wird (VA `0x828B9C`); Modelle
außerhalb des Blickfelds werden nicht gezeichnet. Beim Sammeln der Lichter
(VA `0x81E400`) schaltet der Client jedes Licht mit veraltetem Zeitstempel ab.
Der Patch ändert dort ein Byte (VA `0x81E548`, `je` → `jmp`): Das Licht bleibt
aktiv.

- Beim Entfernen eines Modells (Fackel abgebaut, Einheit verschwunden) meldet
  es seine Lichter weiterhin selbst ab (VA `0x824D30`) – es bleiben keine
  verwaisten Lichter zurück.
- Bewegt sich eine Lichtquelle außerhalb des Bildes, bleibt ihr Licht an der
  zuletzt gesehenen Stelle; Flackern oder Ein-/Ausschalten wird erst
  weiterberechnet, wenn die Quelle wieder im Bild ist.

""",'en':"""<a id="patch-lightstay"></a>
**Lights stay on when their source is off-screen** *(No. 66, Author: St0ny)* 🟠 **[untested]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

Fixes a bug of the original client: if you turn the camera so that a light
source (e.g. a torch) leaves the screen, its light also disappears from
everything that is still visible – for example from your own character right
next to it. This happens with and without shaders.

Cause: point lights belong to models. Their time stamp is only set when the
model is drawn in the current frame (VA `0x828B9C`); models outside the view
are not drawn. When collecting lights (VA `0x81E400`), the client switches off
every light with an outdated time stamp. The patch changes one byte there
(VA `0x81E548`, `je` → `jmp`): the light stays active.

- When a model is removed (torch gone, unit despawned), it still unregisters
  its lights itself (VA `0x824D30`) – no orphaned lights are left behind.
- If a light source moves while off-screen, its light stays at the last seen
  position; flickering or switching on/off continues once the source is back
  on screen.

"""}
LEG={'de':[("Nr. 4, 10,\n    11, 23–25, 41, 42, 45–50, 75 und 83–87 (rote Warnung).","Nr. 4, 10,\n    11, 23–25, 41, 42, 45–50, 76 und 84–88 (rote Warnung)."),
           ("Nr. 26, 29, 39, 44, 51, 62, 65, 69, 72–74 und 81\n    (rote Warnung).","Nr. 26, 29, 39, 44, 51, 62, 65, 66, 70, 73–75\n    und 82 (rote Warnung)."),
           ("Nr. 25, 26, 29, 44, 51, 62 und 65 (rote Warnung).","Nr. 25, 26, 29, 44, 51, 62, 65 und 66 (rote Warnung)."),
           ("Nr. 9, 50, 63–65, 75 und 81. Das ist","Nr. 9, 50, 63–65, 76 und 82. Das ist"),
           ("(Nr. 9, 50, 63–65, 75 und 81), entfernen","(Nr. 9, 50, 63–65, 76 und 82), entfernen")],
     'en':[("No. 4, 10, 11, 23–25,\n    41, 42, 45–50, 75 and 83–87 (red warning).","No. 4, 10, 11, 23–25,\n    41, 42, 45–50, 76 and 84–88 (red warning)."),
           ("No. 26, 29, 39, 44, 51, 62, 65, 69, 72–74 and 81\n    (red warning).","No. 26, 29, 39, 44, 51, 62, 65, 66, 70, 73–75\n    and 82 (red warning)."),
           ("No. 25, 26, 29, 44, 51, 62 and 65 (red warning).","No. 25, 26, 29, 44, 51, 62, 65 and 66 (red warning)."),
           ("63–65, 75 and 81. This does not","63–65, 76 and 82. This does not"),
           ("(No. 9, 50, 63–65, 75 and 81) also remove","(No. 9, 50, 63–65, 76 and 82) also remove")]}
for fn,md,lang in (('README.de.md','PATCHES.de.md','de'),('README.md','PATCHES.en.md','en')):
    p=d+'/'+fn; s=open(p,encoding='utf-8').read()
    for a,b in LEG[lang]: s=once(s,a,b)
    s=table(s,md); s=rowrefs(s)
    m=re.search(r'(?m)^\| \[65\]\(%s#patch-lights\).*\n'%re.escape(md),s); assert m
    s=s[:m.end()]+ROW[lang]+s[m.end():]
    open(p,'w',encoding='utf-8').write(s)
for fn,lang,head in (('PATCHES.de.md','de','## Interface & Komfort'),('PATCHES.en.md','en','## Interface & comfort')):
    p=d+'/'+fn; s=open(p,encoding='utf-8').read()
    s=refs(s)
    a=s.index('<a id="patch-lights"></a>'); b=s.index(head,a)
    s=s[:b]+SEC[lang]+s[b:]
    open(p,'w',encoding='utf-8').write(s)
print('ok')

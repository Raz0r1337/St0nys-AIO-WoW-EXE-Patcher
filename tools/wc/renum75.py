import re,os
os.chdir('/home/user/St0nys-WoW-EXE-Patcher')
sh=lambda n: str(int(n)+1 if 75<=int(n)<=85 else int(n))
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
WARN={'de':"""> [!WARNING]
> **Auf öffentlichen Servern ungetestet** – mögliche Bann-Gefahr. Vorsicht, kann zu Kick/Bann führen.
>
> **Im Spiel ungetestet** – die Funktion ist im Spiel noch nicht geprüft, möglicherweise verbuggt.""",
'en':"""> [!WARNING]
> **Untested on public servers** – possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested in game** – the function has not been checked in game yet, possibly buggy."""}
ROW={'de':'| [75](PATCHES.md#patch-bubblerange) | Sprechblasen-Reichweite erhöhen (Original 25 Meter) *(fragt den Wert ab)* 🟡 **[auf öffentlichen Servern und im Spiel ungetestet]** | St0ny | – | – | – |\n',
     'en':'| [75](PATCHES.en.md#patch-bubblerange) | Increase the chat bubble range (original 25 yards) *(asks for the value)* 🟡 **[untested on public servers and in game]** | St0ny | – | – | – |\n'}
SEC={'de':"""<a id="patch-bubblerange"></a>
**Sprechblasen-Reichweite erhöhen (Original 25 Meter)** *(Nr. 75, Autor: St0ny)* 🟡 **[auf öffentlichen Servern und im Spiel ungetestet]**

"""+WARN['de']+"""

Der Client zeigt Sprechblasen (Sagen, Gruppe, Schreien, NPC-Sagen und
NPC-Schreien) nur für Sprecher bis 25 Meter Entfernung. Schickt der Server
zum Beispiel ein Schreien aus 100 Metern, steht es nur im Chat. Der Patch
erhöht diese Grenze; der Patcher fragt die Reichweite ab: 50, 100, 150, 200
(Vorschlag) oder 0 = unbegrenzt.

Der Client vergleicht das Quadrat des Abstands an zwei Stellen mit der
Konstante 625.0 (= 25²): beim Eintreffen der Nachricht (VA `0x7200CE`, sonst
entsteht keine Blase) und beim Aktualisieren der Blase (VA `0x56C5E9`, sonst
wird sie ausgeblendet). Dieselbe Konstante nutzen auch die Fußspuren, deshalb
bleibt sie unverändert: Der Patch lässt nur die beiden Sprechblasen-Stellen auf
eine andere, schon vorhandene Konstante zeigen (2500, 10000, 22500, 40000 oder
den größten float-Wert). Daher gibt es nur diese festen Stufen; Dateigröße und
PE-Header bleiben unverändert.

> [!NOTE]
> Eine Blase erscheint nur, wenn der Server die Nachricht schickt und der
> Sprecher für dich sichtbar ist – die Sichtweite legt der Server fest (oft um
> die 100 Meter). Sagen begrenzt der Server ohnehin auf 25 Meter, dort ändert
> sich nichts. Gruppen-Blasen erscheinen dagegen auch über weiter entfernten
> Gruppenmitgliedern.

""",'en':"""<a id="patch-bubblerange"></a>
**Increase the chat bubble range (original 25 yards)** *(No. 75, Author: St0ny)* 🟡 **[untested on public servers and in game]**

"""+WARN['en']+"""

The client shows chat bubbles (say, party, yell, NPC say and NPC yell) only for
speakers up to 25 yards away. If the server sends a yell from 100 yards, for
example, it only appears in the chat. The patch raises this limit; the patcher
asks for the range: 50, 100, 150, 200 (suggestion) or 0 = unlimited.

The client compares the squared distance with the constant 625.0 (= 25²) in
two places: when the message arrives (VA `0x7200CE`, otherwise no bubble is
created) and when the bubble is updated (VA `0x56C5E9`, otherwise it is
hidden). The footprints use the same constant, so it stays unchanged: the patch
only points the two chat bubble places to another constant that already exists
in the exe (2500, 10000, 22500, 40000 or the largest float value). That is why
there are only these fixed steps; the file size and the PE header stay
unchanged.

> [!NOTE]
> A bubble only appears if the server sends the message and the speaker is
> visible to you – the view distance is set by the server (often around 100
> yards). The server limits say to 25 yards anyway, nothing changes there.
> Party bubbles, however, also appear above party members further away.

"""}
for fn,md,lang in (('README.de.md','PATCHES.md','de'),('README.md','PATCHES.en.md','en')):
    s=open(fn,encoding='utf-8').read()
    s=table(s,md); s=refs(s)
    i=s.index('](%s#patch-holdrepeat)'%md); j=s.index('\n',i)+1; s=s[:j]+ROW[lang]+s[j:]
    if lang=='de':
        s=once(s,"11, 23–25, 41, 42, 45–50, 74 und 81–85 (rote Warnung)","11, 23–25, 41, 42, 45–50, 74 und 82–86 (rote Warnung)")
        s=once(s,"Nr. 4, 7–9, 26, 29, 44, 51, 62–64, 68, 70–73 und\n    79 (gelber Hinweis).","Nr. 4, 7–9, 26, 29, 44, 51, 62–64, 68, 70–73, 75 und\n    80 (gelber Hinweis).")
        s=once(s,"Nr. 4, 7–9, 25, 26, 29, 44, 51, 62–64, 68 und 70","Nr. 4, 7–9, 25, 26, 29, 44, 51, 62–64, 68, 70 und 75")
    else:
        s=once(s,"41, 42, 45–50, 74 and 81–85 (red warning)","41, 42, 45–50, 74 and 82–86 (red warning)")
        s=once(s,"No. 4, 7–9, 26, 29, 44, 51, 62–64, 68, 70–73 and\n    79 (yellow note).","No. 4, 7–9, 26, 29, 44, 51, 62–64, 68, 70–73, 75 and\n    80 (yellow note).")
        s=once(s,"No. 4, 7–9, 25, 26, 29, 44, 51, 62–64, 68 and 70 (yellow\n    note).","No. 4, 7–9, 25, 26, 29, 44, 51, 62–64, 68, 70 and 75\n    (yellow note).")
    open(fn,'w',encoding='utf-8',newline='\n').write(s)
for fn,lang,head in (('PATCHES.md','de','## Fenster, Maus & Kamera'),('PATCHES.en.md','en',None)):
    s=open(fn,encoding='utf-8').read()
    s=refs(s)
    if head is None:
        head=[l for l in s.split('\n') if l.startswith('## ') and 'indow' in l][0]
    s=once(s,'\n'+head+'\n','\n'+SEC[lang]+head+'\n')
    open(fn,'w',encoding='utf-8',newline='\n').write(s)

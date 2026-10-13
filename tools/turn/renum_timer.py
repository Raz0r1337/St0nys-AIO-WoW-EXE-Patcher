import re
INS=5
def sh(n): n=int(n); return str(n+1) if n>=INS else str(n)
def refs(s):
    # "Nr. 44, 56 und 67", "Nr. 4 und Nr. 55", "Nr. 72 und 73", "Patch Nr. 50" ...
    pat=re.compile(r'(Nr\.|No\.) (\d+)((?:, \d+)*)((?: (?:und|and) (?:Nr\. |No\. )?)(\d+))?')
    def f(m):
        out=m.group(1)+' '+sh(m.group(2))
        if m.group(3): out+=re.sub(r'\d+',lambda x: sh(x.group(0)),m.group(3))
        if m.group(4):
            out+=m.group(4)[:-len(m.group(5))]+sh(m.group(5))
        return out
    return pat.sub(f,s)
def table(s, md):
    return re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m: '| [%s](%s#'%(sh(m.group(1)),md), s)
def once(s,old,new):
    assert s.count(old)==1,(old[:60],s.count(old)); return s.replace(old,new)

# ---------- README.md ----------
for p,md,lang in (('README.md','PATCHES.md','de'),('README.en.md','PATCHES.en.md','en')):
    s=open(p,encoding='utf-8').read()
    s=table(s,md); s=refs(s)
    if lang=='de':
        s=once(s,'Steigwinkel (39), Sprunghöhe\n  (40), die Sprungsteuerung (41–43) und der Doppelsprung (44).',
                 'Steigwinkel (40), Sprunghöhe\n  (41), die Sprungsteuerung (42–44) und der Doppelsprung (45).')
        s=once(s,'[#21](PATCHES.md#patch-globalsv)','[#22](PATCHES.md#patch-globalsv)')
        row4='| [4](PATCHES.md#patch-worldcrash) | WorldFrame-Absturzfix (ungültige Dreiecks-Indizes) – ungetestet | Alyst3r (0x539wowmod) (fixed by St0ny) | – | ✅ |\n'
        s=once(s,row4,row4+'| [5](PATCHES.md#patch-timer) | Genauen Timer immer nutzen (Ruckeln beim Drehen behoben) | St0ny | – | ✅ |\n')
    else:
        s=once(s,'climb angle (39), jump height (40), the air steering\n  (41–43) and the double jump (44).',
                 'climb angle (40), jump height (41), the air steering\n  (42–44) and the double jump (45).')
        s=once(s,'[#21](PATCHES.en.md#patch-globalsv)','[#22](PATCHES.en.md#patch-globalsv)')
        row4='| [4](PATCHES.en.md#patch-worldcrash) | WorldFrame crash fix (invalid triangle indices) – untested | Alyst3r (0x539wowmod) (fixed by St0ny) | – | ✅ |\n'
        s=once(s,row4,row4+'| [5](PATCHES.en.md#patch-timer) | Always use the precise timer (fixes turning stutter) | St0ny | – | ✅ |\n')
    open(p,'w',encoding='utf-8',newline='\n').write(s)

DE='''<a id="patch-timer"></a>
**Genauen Timer immer nutzen (Ruckeln beim Drehen behoben)** *(Nr. 5, standardmäßig aus, Autor: St0ny)*

Behebt einen alten Blizzard-Fehler: Dreht man den Charakter, ruckelt sich der
Unterkörper in die neue Richtung, statt flüssig nachzudrehen – mal direkt nach
dem Start, mal gar nicht.

Beim Start wählt der Client seine Zeitquelle. Dazu vergleicht er 250 ms lang
den genauen Timer (QueryPerformanceCounter) mit dem groben Windows-Timer
(GetTickCount). Weichen beide um 5 ms oder mehr voneinander ab – das reicht
schon, wenn ein Treiber den Thread einmal kurz aufhält –, nutzt der Client für
die ganze Sitzung GetTickCount. Der zählt nur in Schritten von etwa 16 ms.

Beim Drehen verdreht der Client zuerst Oberkörper und Kopf und zieht den
Unterkörper dann nach. Wie weit, hängt von der Zeit seit der letzten
Richtungsänderung ab – meist nur wenige Millisekunden. Mit dem groben Timer ist
diese Zeit fast immer 0 und springt dann auf 16 ms: Der Unterkörper bleibt
stehen und springt dann ein großes Stück weiter.

Der Patch lässt den 250-ms-Vergleich weg (bedingter Sprung → fester Sprung bei
VA `0x86AC8E`). Ist der genaue Timer vorhanden, nutzt der Client ihn damit
immer. Erhalten bleiben die Prüfung, ob der genaue Timer auf allen CPU-Kernen
vorwärts läuft, und die CVar `timingMethod`: Wer `SET timingMethod "1"` in der
`Config.wtf` stehen hat, bekommt weiterhin GetTickCount. Nebenbei startet der
Client etwa eine Viertelsekunde schneller.

> [!TIP]
> Ob der grobe Timer gerade aktiv ist, zeigt im Spiel
> `/run print(GetCVar("timingTestError"))`: `3` heißt, der Test ist beim Start
> gescheitert. Ohne Patch hilft auch `SET timingMethod "2"` in der `Config.wtf`.
'''
EN='''<a id="patch-timer"></a>
**Always use the precise timer (fixes turning stutter)** *(No. 5, off by default, Author: St0ny)*

Fixes an old Blizzard bug: when you turn your character, the lower body jerks
into the new direction instead of following smoothly – sometimes right after
starting the game, sometimes not at all.

At startup the client picks its time source. To do so, it compares the precise
timer (QueryPerformanceCounter) with the coarse Windows timer (GetTickCount) for
250 ms. If the two differ by 5 ms or more – a driver briefly holding up the
thread is enough – the client uses GetTickCount for the whole session, which
only counts in steps of about 16 ms.

When turning, the client first twists the upper body and the head and then
pulls the lower body along. How far depends on the time since the last change
of direction – usually only a few milliseconds. With the coarse timer this time
is almost always 0 and then jumps to 16 ms: the lower body stands still and
then jumps a large step ahead.

The patch drops the 250 ms comparison (conditional jump → fixed jump at VA
`0x86AC8E`), so the client always uses the precise timer when it is available.
The check whether the precise timer runs forward on all CPU cores and the CVar
`timingMethod` are kept: with `SET timingMethod "1"` in `Config.wtf` you still
get GetTickCount. As a side effect the client starts about a quarter of a second
faster.

> [!TIP]
> In game, `/run print(GetCVar("timingTestError"))` shows whether the coarse
> timer is active: `3` means the test failed at startup. Without the patch,
> `SET timingMethod "2"` in `Config.wtf` helps as well.
'''
for p,desc,nextanchor in (('PATCHES.md',DE,'## Sicherheit & Datenschutz'),('PATCHES.en.md',EN,'## Security & privacy')):
    s=open(p,encoding='utf-8').read()
    s=refs(s)
    s=once(s,'\n'+nextanchor+'\n','\n'+desc+'\n'+nextanchor+'\n')
    open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

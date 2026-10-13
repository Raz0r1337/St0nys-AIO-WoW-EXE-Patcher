import re,os
os.chdir('/home/user/St0nys-WoW-EXE-Patcher')
def sh(n):
    n=int(n)
    if n<=5: return str(n)
    if n<=24: return str(n+1)
    return str(n+2)
def refs(s):
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
    assert s.count(old)==1,(old[:70],s.count(old)); return s.replace(old,new)

ROW6={'de':'| [6](PATCHES.md#patch-year2031) | Jahr-2031-Fix (Datum und Kalender bis Ende 2031) | St0ny (original by Alyst3r) | – | – | – |\n',
      'en':'| [6](PATCHES.en.md#patch-year2031) | Year 2031 fix (date and calendar until the end of 2031) | St0ny (original by Alyst3r) | – | – | – |\n'}
ROW26={'de':'| [26](PATCHES.md#patch-wotlkext) | WotLKExtensions.dll Unterstützung aktivieren *(benötigt [WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions))* | St0ny (original by Alyst3r) | – | – | – |\n',
       'en':'| [26](PATCHES.en.md#patch-wotlkext) | Enable WotLKExtensions.dll support *(requires [WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions))* | St0ny (original by Alyst3r) | – | – | – |\n'}

for p,md,lang in (('README.md','PATCHES.md','de'),('README.en.md','PATCHES.en.md','en')):
    s=open(p,encoding='utf-8').read()
    s=table(s,md); s=refs(s)
    if lang=='de':
        s=once(s,'Steigwinkel (40), Sprunghöhe\n  (41), die Sprungsteuerung (42–44) und der Doppelsprung (45).',
                 'Steigwinkel (42), Sprunghöhe\n  (43), die Sprungsteuerung (44–46) und der Doppelsprung (47).')
        s=once(s,'[#22](PATCHES.md#patch-globalsv)','[#23](PATCHES.md#patch-globalsv)')
        r5='| [5](PATCHES.md#patch-timer) | Genauen Timer immer nutzen (Ruckeln beim Drehen behoben) | St0ny | – | – | ✅ |\n'
        s=once(s,r5,r5+ROW6['de'])
        r25='| [25](PATCHES.md#patch-voicedll) |'
    else:
        s=once(s,'climb angle (40), jump height (41), the air steering\n  (42–44) and the double jump (45).',
                 'climb angle (42), jump height (43), the air steering\n  (44–46) and the double jump (47).')
        s=once(s,'[#22](PATCHES.en.md#patch-globalsv)','[#23](PATCHES.en.md#patch-globalsv)')
        r5='| [5](PATCHES.en.md#patch-timer) | Always use the precise timer (fixes turning stutter) | St0ny | – | – | ✅ |\n'
        s=once(s,r5,r5+ROW6['en'])
        r25='| [25](PATCHES.en.md#patch-voicedll) |'
    i=s.index(r25); j=s.index('\n',i)+1
    s=s[:j]+ROW26[lang]+s[j:]
    open(p,'w',encoding='utf-8',newline='\n').write(s)

DE_Y='''<a id="patch-year2031"></a>
**Jahr-2031-Fix (Datum und Kalender bis Ende 2031)** *(Nr. 6, Autor: St0ny (original by Alyst3r))*

Der 3.3.5a-Client kommt mit dem Jahr 2031 nicht zurecht. Datumsangaben packt
WoW in 32 Bit, für das Jahr bleiben davon 5 Bit – also 2000 bis 2031. Den Wert
31 benutzt der Client aber auch für „nicht gesetzt“. Ab dem 1. Januar 2031
schickt der Server genau diesen Wert: Der Client hält dann schon das aktuelle
Datum für ungesetzt, der Kalender springt auf falsche Jahre, Termine und
Feiertage stimmen nicht mehr (laut WotLK-Extensions bis hin zu Abstürzen).

Die Idee stammt aus [WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions)
von Alyst3r, wo der Fix fest in der DLL steckt. Dieser Patch setzt ihn direkt
in der `Wow.exe` um – ohne DLL und ohne die Datei zu vergrößern:

- Jahr 31 gilt als 2031 und nicht mehr als „nicht gesetzt“.
- Alle Kalendergrenzen, die bisher bei Ende 2030 lagen, liegen jetzt bei Ende
  2031: das späteste Kalenderdatum, das Blättern zwischen den Monaten und die
  Berechnung von Monaten und Feiertagen.
- Das späteste Datum für neue Termine (Monatsende in 12 Monaten) endet
  höchstens am 31.12.2031. Das Original würde 2031 nur noch Termine im
  laufenden Monat zulassen.
- In den Feiertagsdaten (`Holidays.dbc` und die Feiertage vom Server) bleibt
  Jahr 31 ein Platzhalter für „jedes Jahr“.

Gegenüber WotLK-Extensions behebt der Patch zwei Fehler: Dort gilt Jahr 31
auch in den Feiertagsdaten als 2031 – jährliche Feiertage mit festem Datum und
wöchentliche Feiertage fehlen dadurch im Kalender, und zwar schon vor 2031.
Außerdem endet dort die Schleife für die wöchentlichen Feiertage weiterhin
Ende 2030.

> [!NOTE]
> **Ab 2032** reicht das Datumsformat nicht mehr aus. Das lässt sich in der
> `Wow.exe` allein nicht lösen – Client und Server müssten ein anderes Format
> benutzen. Der Kalender reicht deshalb bis zum 31.12.2031.

> [!TIP]
> Lädt der Client zusätzlich die WotLKExtensions.dll (Nr. 26), spielt sie beim
> Start ihren eigenen Zeit-Fix ein. Die Feiertags-Korrektur dieses Patches
> bleibt dabei wirksam.
'''
EN_Y='''<a id="patch-year2031"></a>
**Year 2031 fix (date and calendar until the end of 2031)** *(No. 6, Author: St0ny (original by Alyst3r))*

The 3.3.5a client cannot handle the year 2031. WoW packs dates into 32 bits,
which leaves 5 bits for the year – 2000 to 2031. But the client also uses the
value 31 for "not set". From 1 January 2031 on, the server sends exactly this
value: the client then considers even the current date unset, the calendar
jumps to wrong years, events and holidays are no longer correct (according to
WotLK-Extensions even crashes).

The idea comes from [WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions)
by Alyst3r, where the fix is built into the DLL. This patch applies it directly
to `Wow.exe` – without a DLL and without making the file larger:

- Year 31 counts as 2031 and no longer as "not set".
- All calendar limits that used to be at the end of 2030 are now at the end of
  2031: the latest calendar date, browsing between months and the calculation
  of months and holidays.
- The latest date for new events (end of the month 12 months ahead) ends on
  31 December 2031 at the latest. In 2031 the original would only allow events
  in the current month.
- In the holiday data (`Holidays.dbc` and the holidays sent by the server),
  year 31 stays a placeholder for "every year".

Compared to WotLK-Extensions, the patch fixes two bugs: there, year 31 also
counts as 2031 in the holiday data – yearly holidays with a fixed date and
weekly holidays are therefore missing from the calendar, even before 2031. And
the loop for the weekly holidays still ends at the end of 2030 there.

> [!NOTE]
> **From 2032 on** the date format is no longer sufficient. This cannot be
> solved in `Wow.exe` alone – client and server would have to use a different
> format. The calendar therefore goes up to 31 December 2031.

> [!TIP]
> If the client also loads WotLKExtensions.dll (No. 26), the DLL applies its
> own time fix at startup. The holiday correction of this patch stays in
> effect.
'''
DE_W='''<a id="patch-wotlkext"></a>
**WotLKExtensions.dll Unterstützung aktivieren** *(Nr. 26, Autor: St0ny (original by Alyst3r))*

Lädt beim Client-Start die `WotLKExtensions.dll` aus dem WoW-Ordner. Die DLL aus
[WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions) von Alyst3r
erweitert den Client für eigene Server-Projekte, u. a. um eigene DBC-Dateien,
eigene Pakete und neue Lua-Funktionen.
**Benötigt** die `WotLKExtensions.dll` aus WotLK-Extensions. Gehört zusammen
mit dem 4GB-Patch (Nr. 1); fehlt der in der Auswahl, weist der Patcher darauf
hin.

Der Original-Patcher von WotLK-Extensions setzt seinen Lader an dieselbe Stelle
wie Nr. 24 – beide zusammen gingen nicht. Dieser Lader hängt sich stattdessen
an die erste Funktion, die der Client von dort aus aufruft, und liegt im
ungenutzten Teil der Scan.dll-Startfunktion hinter dem Lader von Nr. 24. So
lassen sich Nr. 24 und Nr. 26 einzeln oder zusammen einspielen; zusammen lädt
der Client beide DLLs. Wie bei Nr. 24 wird die Lua-Funktion `ScanDLLStart` zum
Leerlauf und das Scan.dll-Flag auf „bestanden“ gesetzt – der Scan.dll-Mechanismus
ist damit abgeschaltet (wie Nr. 9). Fehlt die DLL, startet WoW normal weiter.
Die Dateigröße ändert sich nicht.

> [!NOTE]
> Der Patch selbst ist unkritisch, er lädt nur eine DLL, die hier nicht
> enthalten ist. WotLK-Extensions ist für eigene Server-Projekte gedacht; laut
> dem Projekt können manche Server Aufrufe seiner Lua-Funktionen erkennen. Nur
> dort einsetzen, wo WotLK-Extensions erlaubt ist – der Patcher zeigt dazu
> einen gelben Hinweis.

> [!NOTE]
> Die DLL spielt beim Start selbst einige Patches im Speicher ein, darunter
> immer ihren eigenen Jahr-2031-Fix. Keiner davon kollidiert mit den Patches
> dieses Patchers: Wo die DLL dieselben Stellen ändert (ihr LUA-Unlock wie
> Nr. 21, ihr GlueXML-Unlock wie Nr. 16, ihr Zeit-Fix wie Nr. 6), passen die
> Bytes zusammen, und mit DLL gilt deren Fassung. Zusammen mit Nr. 6 bleiben
> die Feiertage im Kalender erhalten, die der Zeit-Fix der DLL allein
> verlieren würde.
'''
EN_W='''<a id="patch-wotlkext"></a>
**Enable WotLKExtensions.dll support** *(No. 26, Author: St0ny (original by Alyst3r))*

Loads `WotLKExtensions.dll` from the WoW folder when the client starts. The DLL
from [WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions) by Alyst3r
extends the client for your own server projects, e.g. with custom DBC files,
custom packets and new Lua functions.
**Requires** `WotLKExtensions.dll` from WotLK-Extensions. Belongs together with
the 4GB patch (No. 1): if that one is not selected, the patcher points it out.

The original patcher of WotLK-Extensions puts its loader at the same place as
No. 24 – the two could not be combined. Instead, this loader hooks the first
function the client calls from there, and it sits in the unused part of the
Scan.dll start function behind the loader of No. 24. This way No. 24 and No. 26
can be applied alone or together; together, the client loads both DLLs. As with
No. 24, the Lua function `ScanDLLStart` becomes a no-op and the Scan.dll flag is
set to "passed" – which also disables the Scan.dll mechanism (like No. 9). If
the DLL is missing, WoW simply starts as usual. The file size does not change.

> [!NOTE]
> The patch itself is harmless, it only loads a DLL that is not included here.
> WotLK-Extensions is meant for your own server projects; according to the
> project, some servers can detect calls to its Lua functions. Only use it
> where WotLK-Extensions is allowed – the patcher shows a yellow note about it.

> [!NOTE]
> At startup the DLL applies some patches in memory itself, always including
> its own year 2031 fix. None of them collides with the patches of this
> patcher: where the DLL changes the same places (its LUA unlock like No. 21,
> its GlueXML unlock like No. 16, its time fix like No. 6), the bytes fit
> together, and with the DLL its version applies. Together with No. 6 the
> calendar keeps the holidays that the DLL's time fix alone would lose.
'''
for p,Y,Wt,sec_next_sys,sec_next_dll in (('PATCHES.md',DE_Y,DE_W,'## Sicherheit & Datenschutz','## Gameplay-Fixes'),('PATCHES.en.md',EN_Y,EN_W,'## Security & privacy','## Gameplay fixes')):
    s=open(p,encoding='utf-8').read()
    s=refs(s)
    s=once(s,'\n'+sec_next_sys+'\n','\n'+Y+'\n'+sec_next_sys+'\n')
    s=once(s,'\n'+sec_next_dll+'\n','\n'+Wt+'\n'+sec_next_dll+'\n')
    open(p,'w',encoding='utf-8',newline='\n').write(s)
print('docs ok')

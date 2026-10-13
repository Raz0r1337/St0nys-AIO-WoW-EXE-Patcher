import os
os.chdir('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/wt-y38')
def once(s,a,b):
    assert s.count(a)==1,(a[:80],s.count(a)); return s.replace(a,b)
ROW={'de':'| [87](PATCHES.de.md#patch-y38fix) | Jahr-2038-Fix: Daten um N Jahre verschoben anzeigen *(fragt den Wert ab; nur zusammen mit dem passenden Servermodul)* | 🟠 **[ungetestet]** | St0ny | – | – | – |\n',
     'en':'| [87](PATCHES.en.md#patch-y38fix) | Year 2038 fix: show dates shifted by N years *(asks for the value; only together with the matching server module)* | 🟠 **[untested]** | St0ny | – | – | – |\n'}
SEC={'de':'''
<a id="patch-y38fix"></a>
**Jahr-2038-Fix: Daten um N Jahre verschoben anzeigen** *(Nr. 87, Autor: St0ny)* 🟠 **[ungetestet]**

> [!WARNING]
> **Online ungetestet** – nicht auf öffentlichen Servern getestet, mögliche Bann-Gefahr. Vorsicht, kann zu Kick/Bann führen.
>
> **Ingame ungetestet** – die Funktion ist im Spiel noch nicht geprüft, möglicherweise verbuggt.

Der 3.3.5-Client speichert Daten gepackt mit einem 5-Bit-Jahr ab 2000 – das
reicht nur bis 2031 – und rechnet mit 32-Bit-Unix-Zeiten (bis 2038). Die Idee:
Ein Servermodul schickt alle Daten um N Jahre in die Vergangenheit, dieser
Patch zählt sie für die Anzeige wieder dazu. N ist ein Vielfaches von 28, dann
stimmen Wochentage und Schaltjahre genau. Intern bleibt alles im Bereich
2000–2030, angezeigt wird 2000+N bis 2030+N – mit N = 28 also 2028 bis 2058.
Der Patcher fragt N ab: 28 (Vorschlag), 56 oder 84. So lässt sich der Zyklus
später erneut starten.

Was der Patch ändert:
- Jahresbasis 2000 → 2000+N an allen Lua-Schnittstellen des Kalenders
  (Datum, Grenzen, Monate, Termine, Antwortzeit, Sperren), in der
  Kalender-Post, beim Gründungsdatum der Gilde (`/ginfo`) und bei
  Statistik-Daten. Bei Eingaben (Termin anlegen, Monat wählen) wird N wieder
  abgezogen.
- Kalender-Untergrenze 24.11.2004 → 1.1.2000 (vier Stellen), damit
  verschobene Daten vor 2004 gültig sind.
- Erfolgsdaten rechnen mit zweistelligem Jahr: `GetAchievementInfo`,
  `GetAchievementComparisonInfo` und der Erfolgs-Link (Tooltip) bekommen +N.
- Dateigröße und PE-Header bleiben unverändert.

> [!IMPORTANT]
> **Nur zusammen mit dem passenden Servermodul verwenden** (gleiches N). Ohne
> das Modul zeigt der Client alle Daten N Jahre zu spät an. Die PC-Uhr
> (Chat-Zeitstempel, `date()`/`time()` in Addons) bleibt unverändert, weil
> der Client sie nie mit Server-Daten vergleicht.

> [!NOTE]
> WotLK-Extensions hat einen eigenen Zeit-Fix. Den dort nicht zusätzlich
> einschalten.
''','en':'''
<a id="patch-y38fix"></a>
**Year 2038 fix: show dates shifted by N years** *(No. 87, Author: St0ny)* 🟠 **[untested]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

The 3.3.5 client stores dates packed with a 5-bit year from 2000 – which only
reaches 2031 – and uses 32-bit Unix times (until 2038). The idea: a server
module sends all dates N years into the past, and this patch adds them back
for display. N is a multiple of 28, so weekdays and leap years match exactly.
Internally everything stays within 2000–2030, shown are 2000+N to 2030+N – with
N = 28 that is 2028 to 2058. The patcher asks for N: 28 (suggestion), 56 or
84, so the cycle can be restarted later.

What the patch changes:
- Year base 2000 → 2000+N at all Lua interfaces of the calendar (date,
  limits, months, events, response time, lockouts), in the calendar mail, the
  guild founding date (`/ginfo`) and statistic dates. For input (creating an
  event, choosing a month) N is subtracted again.
- Calendar lower limit 24 Nov 2004 → 1 Jan 2000 (four places), so shifted
  dates before 2004 are valid.
- Achievement dates use a two-digit year: `GetAchievementInfo`,
  `GetAchievementComparisonInfo` and the achievement link (tooltip) get +N.
- File size and PE header stay unchanged.

> [!IMPORTANT]
> **Only use it together with the matching server module** (same N). Without
> the module the client shows all dates N years too late. The PC clock (chat
> timestamps, `date()`/`time()` in addons) stays unchanged, because the client
> never compares it with server dates.

> [!NOTE]
> WotLK-Extensions has its own time fix. Do not switch it on there as well.
'''}
for fn,md,lang in (('README.de.md','PATCHES.de.md','de'),('README.md','PATCHES.en.md','en')):
    s=open(fn,encoding='utf-8').read()
    i=s.index('](%s#patch-clienticon)'%md); j=s.index('\n',i)+1; s=s[:j]+ROW[lang]+s[j:]
    if lang=='de':
        s=once(s,"Nr. 4, 26, 29, 39, 44, 51, 62, 68, 71–73 und 80 (rote\n    Warnung).","Nr. 4, 26, 29, 39, 44, 51, 62, 68, 71–73, 80 und 87\n    (rote Warnung).")
        s=once(s,"Nr. 25, 26, 29, 44, 51 und 62 (rote Warnung).","Nr. 25, 26, 29, 44, 51, 62 und 87 (rote Warnung).")
    else:
        s=once(s,"No. 4, 26, 29, 39, 44, 51, 62, 68, 71–73 and 80 (red\n    warning).","No. 4, 26, 29, 39, 44, 51, 62, 68, 71–73, 80 and 87\n    (red warning).")
        s=once(s,"No. 25, 26, 29, 44, 51 and 62 (red warning).","No. 25, 26, 29, 44, 51, 62 and 87 (red warning).")
    open(fn,'w',encoding='utf-8',newline='\n').write(s)
    p=open(md,encoding='utf-8').read()
    p=p.rstrip('\n')+'\n'+SEC[lang]
    open(md,'w',encoding='utf-8',newline='\n').write(p)

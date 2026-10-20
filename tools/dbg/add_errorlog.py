#!/usr/bin/env python3
# Nr. 93 (assetdebug) um das Fehler-Log erweitern (FineWolf, modified by St0ny). Teil "code": Kopfkommentar
# und Add-AssetDebugLog (von gen_alog.py aus make_debug_exe_st0ny.py erzeugt) ersetzen, Autor, Name und Hinweis
# im Patch-Eintrag. Teil "docs": README/PATCHES DE/EN (Zeile, Abschnitt).
# Aufruf: add_errorlog.py <dev-Ordner> code <Ausgabe von gen_alog.py>  |  add_errorlog.py <dev-Ordner> docs
import sys, os, re
D, MODE = sys.argv[1], sys.argv[2]
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
def once(s, a, b, tag=''):
    assert s.count(a) == 1, (tag, a[:80], s.count(a)); return s.replace(a, b)
if MODE == 'code':
    gen = open(sys.argv[3], encoding='ascii').read().rstrip('\n') + '\n'
    p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
    head = r'''# ============================================================
#  Asset-Debug-Log (FineWolf, modified by St0ny; make_debug_exe_st0ny.py, BETA)
#  Eigene Sektion .alog: Code ab $CAVE, Daten ab $CAVE + 0x1000 (14 Variablen,
#  die Texte und ein Ringpuffer mit den letzten 16 geoeffneten Dateinamen).
#  Neun Stellen im Client springen dorthin (FineWolf):
#   - SFileOpenFileEx (VA 0x424B50): jede Datei, die der Client oeffnet
#     (MPQs oder Data-Ordner) -> "OPEN" bzw. "OPEN-FAIL" ins Log, der Name
#     kommt zusaetzlich in den Ringpuffer.
#   - CM2Scene::CreateModel (0x81F8F0) und CMapObj::Create (0x7B0CC0): Pfad
#     und erzeugtes Objekt ("M2-CREATE", "WMO-CREATE").
#   - TextureCreate, Zweig "nicht im Cache" (0x4B9853): "TEX-LOAD" mit Pfad.
#   - M2-Zeichenschleife (0x823A20), WMO-Gruppen-Aufrufe (0x7ABFF0, 0x7AC011)
#     und Gelaendeschleife (0x798A6C): merken sich nur im Speicher, was gerade
#     gezeichnet wird (keine Schreibzugriffe pro Bild).
#   - Oberster Ausnahme-Filter (Push bei 0x772B20): schreibt bei einem Absturz
#     Ausnahme, Register, das zuletzt gezeichnete M2, die WMO-Gruppe und den
#     Gelaendeabschnitt (ADT-Pfad und Chunk) sowie die letzten 16 Dateien ins
#     Log und springt dann in WoWs eigenen Filter (0x772760).
#  Dazu (St0ny) 52 Aufrufe von WoWs printf-Funktion fuer Fehlermeldungen
#  (VA 0x5EEB70, im fertigen Client leer, z.B. "Corrupt model data: %s"):
#  Sie gehen nach hk_wowerr und landen als "WOW-ERROR <Meldung>" im Log.
#  Die ersetzten Befehle laufen in der Sektion unveraendert weiter; mehrere
#  Threads teilen sich das Log ueber eine Sperre. Log: Logs\AssetDebug.log im
#  WoW-Ordner (sonst AssetDebug.log), es wird immer angehaengt. Zeilen:
#  "<GetTickCount> [<Thread>] <Text>".
#  Fehler-Log (St0ny): Logs\AssetErrors.log (sonst AssetErrors.log) bekommt
#  nur die Fehler - OPEN-FAIL, den ganzen Absturzbericht und WOW-ERROR - mit
#  derselben Zeit und Thread-Nummer wie das grosse Log. Es wird erst beim
#  ersten Fehler einer Sitzung geoeffnet. Den Code erzeugt tools/dbg/gen_alog.py
#  aus make_debug_exe_st0ny.py (FineWolfs make_debug_exe.py plus Fehler-Log).
# ============================================================
'''
    a = s.index('# ============================================================\n#  Asset-Debug-Log (FineWolf, make_debug_exe.py, BETA)\n')
    z = s.index('\n# ============================================================\n#  Wasserzeichen\n', a)
    assert s[a:z].count('function Add-AssetDebugLog {') == 1
    s = s[:a] + head + gen + s[z:]
    old = '''       Author = 'FineWolf'
       De = 'Debug-Log fuer geladene Dateien, Modelle, Texturen und Abstuerze [BETA]'
       En = 'Debug log for loaded files, models, textures and crashes [BETA]'
       NoteDe = 'schreibt Logs\\AssetDebug.log im WoW-Ordner - die Datei waechst mit jedem Start'
       NoteEn = 'writes Logs\\AssetDebug.log in the WoW folder - the file grows with every start'
'''
    new = '''       Author = 'FineWolf (modified by St0ny)'
       De = 'Debug- und Fehler-Log fuer geladene Dateien, Modelle, Texturen und Abstuerze [BETA]'
       En = 'Debug and error log for loaded files, models, textures and crashes [BETA]'
       NoteDe = 'schreibt Logs\\AssetDebug.log (alles) und Logs\\AssetErrors.log (nur Fehler) - beide Dateien wachsen immer weiter'
       NoteEn = 'writes Logs\\AssetDebug.log (everything) and Logs\\AssetErrors.log (errors only) - both files keep growing'
'''
    s = once(s, old, new, 'Eintrag')
    wr(p, s, True)
    print('code ok')
if MODE == 'docs':
    N = 93
    # ---------------- README: Zeile in der Uebersicht ----------------
    for f, old, new in (
        ('README.de.md',
         '| [%d](PATCHES.de.md#patch-assetdebug) | Debug-Log für geladene Dateien, Modelle, Texturen und Abstürze [BETA] *(schreibt `Logs\\AssetDebug.log` im WoW-Ordner – die Datei wächst mit jedem Start)* | 🟠 **[ungetestet - Exe wird größer]** | FineWolf |' % N,
         '| [%d](PATCHES.de.md#patch-assetdebug) | Debug- und Fehler-Log für geladene Dateien, Modelle, Texturen und Abstürze [BETA] *(schreibt `Logs\\AssetDebug.log` (alles) und `Logs\\AssetErrors.log` (nur Fehler) – beide Dateien wachsen immer weiter)* | 🟠 **[ungetestet - Exe wird größer]** | FineWolf (modified by St0ny) |' % N),
        ('README.md',
         '| [%d](PATCHES.en.md#patch-assetdebug) | Debug log for loaded files, models, textures and crashes [BETA] *(writes `Logs\\AssetDebug.log` in the WoW folder – the file grows with every start)* | 🟠 **[untested - exe grows]** | FineWolf |' % N,
         '| [%d](PATCHES.en.md#patch-assetdebug) | Debug and error log for loaded files, models, textures and crashes [BETA] *(writes `Logs\\AssetDebug.log` (everything) and `Logs\\AssetErrors.log` (errors only) – both files keep growing)* | 🟠 **[untested - exe grows]** | FineWolf (modified by St0ny) |' % N)):
        p = os.path.join(D, 'docs', f); s = rd(p)
        s = once(s, old, new, f); wr(p, s)
    # ---------------- PATCHES: Abschnitt (letzter der Datei) ersetzen ----------------
    DE = """<a id="patch-assetdebug"></a>
**Debug- und Fehler-Log für geladene Dateien, Modelle, Texturen und Abstürze [BETA]** *(Nr. %d, Autor: FineWolf (modified by St0ny))* 🟠 **[ungetestet - Exe wird größer]**

Für die Fehlersuche, z. B. wenn eigene Modelle, Texturen oder Karten den Client
abstürzen lassen. Der Patch schreibt zwei Protokolle in den Ordner `Logs` im
WoW-Ordner (geht das nicht, direkt neben die `Wow.exe`):

- `AssetDebug.log` – **alles**, was unten steht.
- `AssetErrors.log` – **nur die Fehler**: `OPEN-FAIL`, `WOW-ERROR` und der
  Absturzbericht.

Ins große Log kommt:

- **Jede Datei, die der Client öffnet** – aus den MPQs oder dem `Data`-Ordner –,
  in der Reihenfolge, in der er sie lädt: `OPEN`, oder `OPEN-FAIL`, wenn er sie
  nicht findet.
- **Modelle und WMOs**, die der Client anlegt: `M2-CREATE` bzw. `WMO-CREATE` mit
  Pfad und Speicheradresse.
- **Texturen**, die wirklich neu geladen werden (nicht schon im Cache):
  `TEX-LOAD` mit Pfad.
- **WoWs eigene Fehlermeldungen** (`WOW-ERROR`): Der Client hat viele
  Fehlermeldungen eingebaut, im fertigen Spiel verschwinden sie aber ungelesen.
  Der Patch fängt 52 davon ab – zu Dateien, Modellen, Texturen, Karten und
  DBC-Daten, z. B. `Model2: File not found`, `Corrupt model data`,
  `Failed to load skin profile`, `Unable to Load Texture`,
  `CMap::SafeOpen() failed` oder `Bad zone ID` (Karte fehlt in der `Map.dbc`).
  Sie zeigen auch Dateien, die zwar da, aber kaputt sind. Ein fehlendes Modell
  ersetzt WoW übrigens ohne Meldung durch einen Platzhalter
  (`Spells\\ErrorCube.mdx`) – im Log steht dann trotzdem ein normales
  `M2-CREATE`, erst die `WOW-ERROR`-Zeile davor verrät den Fehler.
- **Bei einem Absturz:** Fehlercode und Adresse, die Register, das zuletzt
  gezeichnete Modell, die zuletzt gezeichnete WMO-Gruppe, der zuletzt
  gezeichnete Geländeabschnitt (ADT-Datei und Chunk) und die letzten 16
  geöffneten Dateien. Danach meldet der Client den Absturz wie gewohnt.

Jede Zeile beginnt mit der Zeit in Millisekunden seit dem Windows-Start und der
Thread-Nummer – in beiden Logs gleich, so findest du zu jedem Fehler die Stelle
im großen Log. Zum Beispiel:

```
0001234567 [0A1C] OPEN      Creature\\Foo\\Foo.m2 (flags=0)
0001234567 [0A1C] OPEN-FAIL Creature\\Foo\\Foo01.skin (flags=0)
0001234568 [0A1C] WOW-ERROR Failed to load skin profile: Creature\\Foo\\Foo.m2
0001234570 [0A1C] M2-CREATE  Creature\\Foo\\Foo.m2 -> model=1A2B3C40
```

Beim Zeichnen merkt sich der Patch nur im Speicher, was gerade dran ist – pro
Bild wird nichts geschrieben.

> [!WARNING]
> **BETA** – noch ungetestet, online wie im Spiel. Deshalb ist der Patch
> standardmäßig abgewählt und vorerst nur in den dev-Zweigen, nicht in
> `st0ny-main`. Für öffentliche Server ist er nicht gedacht.

> [!NOTE]
> Nicht jedes `OPEN-FAIL` ist ein echter Fehler: Manche Dateien probiert WoW nur
> aus, z. B. eine Textur erst als `.tga` und dann als `.blp`. Das erste
> Fehlschlagen ist dann harmlos. Andere Dateien versucht WoW mehrmals zu öffnen
> (Kartendateien wie WMOs bis zu zehnmal) – dann steht derselbe Fehler mehrfach
> im Log.

> [!NOTE]
> Das Log nennt die einzelnen Dateien, nicht die MPQ-Archive: Es zeigt, in
> welcher Reihenfolge der Client Dateien lädt und ob er sie findet, aber nicht,
> aus welchem MPQ eine Datei stammt.

> [!IMPORTANT]
> Beide Dateien werden fortgesetzt und nie gekürzt – sie wachsen immer weiter.
> Im großen Log beginnt jeder Start mit `==== AssetDebug session start ====`.
> Das Fehler-Log wird erst beim ersten Fehler geöffnet und bekommt dann die
> Zeile `==== AssetErrors session start ====` – eine Sitzung ohne Fehler
> hinterlässt dort nichts. Am besten ab und zu löschen. Weil jede geöffnete
> Datei sofort geschrieben wird, lädt der Client etwas langsamer.

Technik: Der Patch hängt eine eigene Sektion `.alog` an (Code und Daten, rund
9 KB) und leitet neun Stellen im Client dorthin um: `SFileOpenFileEx`
(VA `0x424B50`), `CM2Scene::CreateModel` (`0x81F8F0`), `CMapObj::Create`
(`0x7B0CC0`), den Cache-Fehlschlag in `TextureCreate` (`0x4B9853`), die
M2-Zeichenschleife (`0x823A20`), die beiden WMO-Gruppen-Aufrufe (`0x7ABFF0`,
`0x7AC011`), die Geländeschleife (`0x798A6C`) und den obersten
Ausnahme-Filter (`0x772B20`). Die überschriebenen Befehle laufen in der Sektion
unverändert weiter. Dazu kommen 52 Aufrufe von WoWs Ausgabe-Funktion für
Fehlermeldungen (`0x5EEB70`, im fertigen Client leer): Sie führen jetzt in den
Patch, der die Meldung formatiert und ins Log schreibt – alle Register bleiben
dabei unverändert. Grundlage ist FineWolfs Skript `make_debug_exe.py`, das
Fehler-Log hat St0ny ergänzt. Zusammen mit DLLs, die dieselben Funktionen
umleiten, ist der Patch ungetestet.
""" % N
    EN = """<a id="patch-assetdebug"></a>
**Debug and error log for loaded files, models, textures and crashes [BETA]** *(No. %d, Author: FineWolf (modified by St0ny))* 🟠 **[untested - exe grows]**

For troubleshooting, e.g. when custom models, textures or maps crash the client.
The patch writes two logs to the `Logs` folder in the WoW folder (if that fails,
right next to `Wow.exe`):

- `AssetDebug.log` – **everything** listed below.
- `AssetErrors.log` – **only the errors**: `OPEN-FAIL`, `WOW-ERROR` and the
  crash report.

The big log gets:

- **Every file the client opens** – from the MPQs or the `Data` folder – in the
  order it loads them: `OPEN`, or `OPEN-FAIL` if it cannot find the file.
- **Models and WMOs** the client creates: `M2-CREATE` or `WMO-CREATE` with path
  and memory address.
- **Textures** that are really loaded (not already in the cache): `TEX-LOAD`
  with path.
- **WoW's own error messages** (`WOW-ERROR`): the client has many error
  messages built in, but in the release game they vanish unread. The patch
  catches 52 of them – about files, models, textures, maps and DBC data, e.g.
  `Model2: File not found`, `Corrupt model data`, `Failed to load skin profile`,
  `Unable to Load Texture`, `CMap::SafeOpen() failed` or `Bad zone ID` (map
  missing from `Map.dbc`). They also reveal files that exist but are broken.
  By the way, WoW silently replaces a missing model with a placeholder
  (`Spells\\ErrorCube.mdx`) – the log still shows a normal `M2-CREATE`, only
  the `WOW-ERROR` line before it gives the error away.
- **On a crash:** exception code and address, the registers, the model, WMO
  group and terrain chunk (ADT file and chunk) drawn last and the last 16
  opened files. After that the client reports the crash as usual.

Every line starts with the time in milliseconds since Windows started and the
thread number – the same in both logs, so for every error you find the spot in
the big log. For example:

```
0001234567 [0A1C] OPEN      Creature\\Foo\\Foo.m2 (flags=0)
0001234567 [0A1C] OPEN-FAIL Creature\\Foo\\Foo01.skin (flags=0)
0001234568 [0A1C] WOW-ERROR Failed to load skin profile: Creature\\Foo\\Foo.m2
0001234570 [0A1C] M2-CREATE  Creature\\Foo\\Foo.m2 -> model=1A2B3C40
```

While drawing, the patch only remembers in memory what is being drawn – nothing
is written per frame.

> [!WARNING]
> **BETA** – still untested, online and in game. That is why the patch is
> deselected by default and only in the dev branches for now, not in
> `st0ny-main`. It is not meant for public servers.

> [!NOTE]
> Not every `OPEN-FAIL` is a real error: WoW only tries some files, e.g. a
> texture first as `.tga` and then as `.blp`. The first failure is harmless
> then. Other files WoW tries to open several times (map files such as WMOs up
> to ten times) – then the same error shows up several times in the log.

> [!NOTE]
> The log names the individual files, not the MPQ archives: it shows in which
> order the client loads files and whether it finds them, but not which MPQ a
> file came from.

> [!IMPORTANT]
> Both files are continued and never truncated – they keep growing. In the big
> log every start begins with `==== AssetDebug session start ====`. The error
> log is only opened at the first error and then gets the line
> `==== AssetErrors session start ====` – a session without errors leaves
> nothing there. Best delete them from time to time. Because every opened file
> is written right away, the client loads a bit slower.

Technical details: the patch appends its own section `.alog` (code and data,
about 9 KB) and redirects nine spots in the client to it:
`SFileOpenFileEx` (VA `0x424B50`), `CM2Scene::CreateModel` (`0x81F8F0`),
`CMapObj::Create` (`0x7B0CC0`), the cache miss in `TextureCreate`
(`0x4B9853`), the M2 draw loop (`0x823A20`), both WMO group calls
(`0x7ABFF0`, `0x7AC011`), the terrain loop (`0x798A6C`) and the top-level
exception filter (`0x772B20`). The overwritten instructions keep running
unchanged in the section. On top of that, 52 calls of WoW's output function
for error messages (`0x5EEB70`, empty in the release client) now lead into the
patch, which formats the message and writes it to the log – all registers stay
unchanged. Based on FineWolf's script `make_debug_exe.py`; St0ny added the
error log. Together with DLLs that redirect the same functions, the patch is
untested.
""" % N
    for f, txt in (('PATCHES.de.md', DE), ('PATCHES.en.md', EN)):
        p = os.path.join(D, 'docs', f); s = rd(p)
        a = s.index('<a id="patch-assetdebug"></a>\n')
        assert s.count('<a id="patch-assetdebug"></a>') == 1 and s.endswith('\n') and not s.endswith('\n\n')
        assert s.find('<a id="patch-', a + 10) < 0          # letzter Abschnitt der Datei
        wr(p, s[:a] + txt)
    print('docs ok')

#!/usr/bin/env python3
# Baut FineWolfs Asset-Debug-Log als Patch "assetdebug" in st0ny-dev ein: letzter Patch (Nr. 93), neue Kategorie
# "debug" hinter den Client-Infos. Teil "code": Helfer AddAsciiZ, Add-AssetDebugLog (von gen_alog.py erzeugt),
# Kategorie, Patch-Eintrag. Teil "docs": README/PATCHES DE/EN (Abschnitt, Zeile, Warnlisten, Danksagung).
# Aufruf: add_assetdebug.py <dev-Ordner> code <Ausgabe von gen_alog.py>  |  add_assetdebug.py <dev-Ordner> docs
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
    a = "function AddLE32($list, [int64]$v) { $b = [BitConverter]::GetBytes([int32]$v); for ($i = 0; $i -lt 4; $i++) { [void]$list.Add($b[$i]) } }\n"
    s = once(s, a, a + "function AddAsciiZ($list, [string]$s, [switch]$CrLf) { AddRaw $list ([System.Text.Encoding]::ASCII.GetBytes($s)); if ($CrLf) { AddRaw $list @(0x0D, 0x0A) }; [void]$list.Add([byte]0) }\n", 'AddAsciiZ')
    head = '''# ============================================================
#  Asset-Debug-Log (FineWolf, make_debug_exe.py, BETA)
#  Eigene Sektion .alog: Code (0x511 Byte) ab $CAVE, Daten ab $CAVE + 0x1000
#  (13 Variablen, die Texte und ein Ringpuffer mit den letzten 16 geoeffneten
#  Dateinamen). Neun Stellen im Client springen dorthin:
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
#  Die ersetzten Befehle laufen in der Sektion unveraendert weiter; mehrere
#  Threads teilen sich das Log ueber eine Sperre. Log: Logs\\AssetDebug.log im
#  WoW-Ordner (sonst AssetDebug.log), es wird immer angehaengt. Zeilen:
#  "<GetTickCount> [<Thread>] <Text>". Den Code erzeugt tools/dbg/gen_alog.py
#  aus FineWolfs Skript - Code, Daten und Hook-Bytes sind dieselben.
# ============================================================
'''.replace('\\\\', '\\')
    s = once(s, "# ============================================================\n#  Wasserzeichen\n",
             head + gen + "\n# ============================================================\n#  Wasserzeichen\n", 'Funktion')
    a = "    client   = @{ De = 'Client-Infos: Version, Build, Titel, Datum, Icon'; En = 'Client info: version, build, title, date, icon' }\n"
    s = once(s, a, a + "    debug    = @{ De = 'Debugging & Testen';                En = 'Debugging & testing' }\n", 'Kategorie')
    entry = '''

    # --- Debugging & Testen ---

    @{ Id = 'assetdebug'; Cat = 'debug'; On = $false; GrowsExe = $true; PublicUntested = $true; GameUntested = $true
       Author = 'FineWolf'
       De = 'Debug-Log fuer geladene Dateien, Modelle, Texturen und Abstuerze [BETA]'
       En = 'Debug log for loaded files, models, textures and crashes [BETA]'
       NoteDe = 'schreibt Logs\\AssetDebug.log im WoW-Ordner - die Datei waechst mit jedem Start'
       NoteEn = 'writes Logs\\AssetDebug.log in the WoW folder - the file grows with every start'
       Code = {
        # Eigene Sektion (.alog), siehe Add-AssetDebugLog.
        Add-AssetDebugLog
    }}
'''.replace('\\\\', '\\')
    i = s.index("    @{ Id = 'clienticon'"); k = s.index("\n    }}\n", i) + len("\n    }}\n")
    assert s[k:k + 2] == ')\n', repr(s[k:k + 20])      # Ende der Patch-Liste
    s = s[:k] + '\n\n' + entry.lstrip('\n') + s[k:]
    wr(p, s, True)
    print('code ok')
if MODE == 'docs':
    N = 93
    # ---------------- README ----------------
    for f, tag, cat_new, row, pairs, thanks_anchor, thanks in (
        ('README.de.md', 'PATCHES.de.md', '#### Debugging & Testen',
         '| [%d](PATCHES.de.md#patch-assetdebug) | Debug-Log für geladene Dateien, Modelle, Texturen und Abstürze [BETA] *(schreibt `Logs\\AssetDebug.log` im WoW-Ordner – die Datei wächst mit jedem Start)* | 🟠 **[ungetestet - Exe wird größer]** | FineWolf | – | – | – |' % N,
         [("    kann zu Kick/Bann führen: Nr. 10, 26, 32, 42, 47, 54, 65, 68, 74, 77–79 und 86\n    (orange Warnung).\n",
           "    kann zu Kick/Bann führen: Nr. 10, 26, 32, 42, 47, 54, 65, 68, 74, 77–79, 86\n    und %d (orange Warnung).\n" % N),
          ("    möglicherweise verbuggt: Nr. 25, 26, 32, 47, 54, 65, 68 und 86 (orange Warnung).\n",
           "    möglicherweise verbuggt: Nr. 25, 26, 32, 47, 54, 65, 68, 86 und %d (orange\n    Warnung).\n" % N),
          ("    Nr. 9, 53, 66–69, 80 und 86. Das ist keine sichere Bann-Gefahr,\n",
           "    Nr. 9, 53, 66–69, 80, 86 und %d. Das ist keine sichere Bann-Gefahr,\n" % N)],
         "- Und natürlich danke an alle Autoren der Patches, die in der\n",
         "- Danke an **FineWolf** für den Debug-Patch\n  [#%d](PATCHES.de.md#patch-assetdebug) (Asset-Debug-Log).\n" % N),
        ('README.md', 'PATCHES.en.md', '#### Debugging & testing',
         '| [%d](PATCHES.en.md#patch-assetdebug) | Debug log for loaded files, models, textures and crashes [BETA] *(writes `Logs\\AssetDebug.log` in the WoW folder – the file grows with every start)* | 🟠 **[untested - exe grows]** | FineWolf | – | – | – |' % N,
         [("    you kicked or banned: No. 10, 26, 32, 42, 47, 54, 65, 68, 74, 77–79 and 86\n    (orange warning).\n",
           "    you kicked or banned: No. 10, 26, 32, 42, 47, 54, 65, 68, 74, 77–79, 86\n    and %d (orange warning).\n" % N),
          ("    possibly buggy: No. 25, 26, 32, 47, 54, 65, 68 and 86 (orange warning).\n",
           "    possibly buggy: No. 25, 26, 32, 47, 54, 65, 68, 86 and %d (orange warning).\n" % N),
          ("    66–69, 80 and 86. This does not mean a certain ban, but it is a risk: some\n",
           "    66–69, 80, 86 and %d. This does not mean a certain ban, but it is a risk: some\n" % N)],
         "- And of course thanks to all patch authors named in the\n",
         "- Thanks to **FineWolf** for the debug patch\n  [#%d](PATCHES.en.md#patch-assetdebug) (asset debug log).\n" % N)):
        p = os.path.join(D, 'docs', f); s = rd(p)
        thead = re.search(r'(?m)^\| (Nr\.|No\.) \|[^\n]*\n\|[-:| ]+\|\n', s).group(0)
        m = re.search(r'(?m)^\| \[92\]\(%s#patch-clienticon\) \|[^\n]*\n' % re.escape(tag), s)
        assert m and s[m.end():m.end() + 12] == '\n</details>\n', repr(s[m.end():m.end() + 20])
        s = s[:m.end()] + '\n%s\n\n%s%s\n' % (cat_new, thead, row) + s[m.end():]
        for a, b in pairs: s = once(s, a, b, f + 'Liste')
        s = once(s, thanks_anchor, thanks + thanks_anchor, f + 'Dank')
        wr(p, s)
    # ---------------- PATCHES: Abschnitt ans Ende ----------------
    DE = """## Debugging & Testen

<a id="patch-assetdebug"></a>
**Debug-Log für geladene Dateien, Modelle, Texturen und Abstürze [BETA]** *(Nr. %d, Autor: FineWolf)* 🟠 **[ungetestet - Exe wird größer]**

Für die Fehlersuche, z. B. wenn eigene Modelle, Texturen oder Karten den Client
abstürzen lassen. Der Patch schreibt ein Protokoll nach `Logs\AssetDebug.log` im
WoW-Ordner (geht das nicht, nach `AssetDebug.log` neben der `Wow.exe`):

- **Jede Datei, die der Client öffnet** – aus den MPQs oder dem `Data`-Ordner –,
  in der Reihenfolge, in der er sie lädt: `OPEN`, oder `OPEN-FAIL`, wenn er sie
  nicht findet.
- **Modelle und WMOs**, die der Client anlegt: `M2-CREATE` bzw. `WMO-CREATE` mit
  Pfad und Speicheradresse.
- **Texturen**, die wirklich neu geladen werden (nicht schon im Cache):
  `TEX-LOAD` mit Pfad.
- **Bei einem Absturz:** Fehlercode und Adresse, die Register, das zuletzt
  gezeichnete Modell, die zuletzt gezeichnete WMO-Gruppe, der zuletzt
  gezeichnete Geländeabschnitt (ADT-Datei und Chunk) und die letzten 16
  geöffneten Dateien. Danach meldet der Client den Absturz wie gewohnt.

Jede Zeile beginnt mit der Zeit in Millisekunden seit dem Windows-Start und der
Thread-Nummer, z. B.:

```
0001234567 [0A1C] OPEN      Creature\Foo\Foo.m2 (flags=0)
0001234567 [0A1C] OPEN-FAIL Creature\Foo\Foo01.skin (flags=0)
0001234570 [0A1C] M2-CREATE  Creature\Foo\Foo.m2 -> model=1A2B3C40
```

Beim Zeichnen merkt sich der Patch nur im Speicher, was gerade dran ist – pro
Bild wird nichts geschrieben.

> [!WARNING]
> **BETA** – noch ungetestet, online wie im Spiel. Deshalb ist der Patch
> standardmäßig abgewählt und vorerst nur in den dev-Zweigen, nicht in
> `st0ny-main`. Für öffentliche Server ist er nicht gedacht.

> [!NOTE]
> Das Log nennt die einzelnen Dateien, nicht die MPQ-Archive: Es zeigt, in
> welcher Reihenfolge der Client Dateien lädt und ob er sie findet, aber nicht,
> aus welchem MPQ eine Datei stammt.

> [!IMPORTANT]
> Die Datei wird bei jedem Start fortgesetzt (Zeile
> `==== AssetDebug session start ====`) und nie gekürzt – sie wächst mit jeder
> Sitzung. Am besten ab und zu löschen. Weil jede geöffnete Datei sofort
> geschrieben wird, lädt der Client etwas langsamer.

Technik: Der Patch hängt eine eigene Sektion `.alog` an (Code und Daten, gut
9 KB) und leitet neun Stellen im Client dorthin um: `SFileOpenFileEx`
(VA `0x424B50`), `CM2Scene::CreateModel` (`0x81F8F0`), `CMapObj::Create`
(`0x7B0CC0`), den Cache-Fehlschlag in `TextureCreate` (`0x4B9853`), die
M2-Zeichenschleife (`0x823A20`), die beiden WMO-Gruppen-Aufrufe (`0x7ABFF0`,
`0x7AC011`), die Geländeschleife (`0x798A6C`) und den obersten
Ausnahme-Filter (`0x772B20`). Die überschriebenen Befehle laufen in der Sektion
unverändert weiter. Portiert aus FineWolfs Skript `make_debug_exe.py`: Code,
Daten und Hook-Stellen sind byte-gleich. Zusammen mit DLLs, die dieselben
Funktionen umleiten, ist der Patch ungetestet.
""" % N
    EN = """## Debugging & testing

<a id="patch-assetdebug"></a>
**Debug log for loaded files, models, textures and crashes [BETA]** *(No. %d, Author: FineWolf)* 🟠 **[untested - exe grows]**

For troubleshooting, e.g. when custom models, textures or maps crash the client.
The patch writes a log to `Logs\AssetDebug.log` in the WoW folder (if that
fails, to `AssetDebug.log` next to `Wow.exe`):

- **Every file the client opens** – from the MPQs or the `Data` folder – in the
  order it loads them: `OPEN`, or `OPEN-FAIL` if it cannot find the file.
- **Models and WMOs** the client creates: `M2-CREATE` or `WMO-CREATE` with path
  and memory address.
- **Textures** that are really loaded (not already in the cache): `TEX-LOAD`
  with path.
- **On a crash:** exception code and address, the registers, the model, WMO
  group and terrain chunk (ADT file and chunk) drawn last and the last 16
  opened files. After that the client reports the crash as usual.

Every line starts with the time in milliseconds since Windows started and the
thread number, e.g.:

```
0001234567 [0A1C] OPEN      Creature\Foo\Foo.m2 (flags=0)
0001234567 [0A1C] OPEN-FAIL Creature\Foo\Foo01.skin (flags=0)
0001234570 [0A1C] M2-CREATE  Creature\Foo\Foo.m2 -> model=1A2B3C40
```

While drawing, the patch only remembers in memory what is being drawn – nothing
is written per frame.

> [!WARNING]
> **BETA** – still untested, online and in game. That is why the patch is
> deselected by default and only in the dev branches for now, not in
> `st0ny-main`. It is not meant for public servers.

> [!NOTE]
> The log names the individual files, not the MPQ archives: it shows in which
> order the client loads files and whether it finds them, but not which MPQ a
> file came from.

> [!IMPORTANT]
> The file is continued at every start (line
> `==== AssetDebug session start ====`) and never truncated – it grows with
> every session. Best delete it from time to time. Because every opened file is
> written right away, the client loads a bit slower.

Technical details: the patch appends its own section `.alog` (code and data,
a little over 9 KB) and redirects nine spots in the client to it:
`SFileOpenFileEx` (VA `0x424B50`), `CM2Scene::CreateModel` (`0x81F8F0`),
`CMapObj::Create` (`0x7B0CC0`), the cache miss in `TextureCreate`
(`0x4B9853`), the M2 draw loop (`0x823A20`), both WMO group calls
(`0x7ABFF0`, `0x7AC011`), the terrain loop (`0x798A6C`) and the top-level
exception filter (`0x772B20`). The overwritten instructions keep running
unchanged in the section. Ported from FineWolf's script `make_debug_exe.py`:
code, data and hook sites are byte-identical. Together with DLLs that redirect
the same functions, the patch is untested.
""" % N
    for f, txt in (('PATCHES.de.md', DE), ('PATCHES.en.md', EN)):
        p = os.path.join(D, 'docs', f); s = rd(p)
        assert s.endswith('\n') and not s.endswith('\n\n') and s.count('patch-clienticon') == 1
        wr(p, s + '\n' + txt)
    print('docs ok')

# Doku fuer Visus - St0nyCam (Nr. 83): Zeile, Abschnitt, Nummern ab 83 (+1), Listen,
# Hinweis bei Lux (Nr. 31), Danksagung. Aufruf: docs_edit.py <worktree> <altes Skript>
import re, sys
wt = sys.argv[1]; d = wt + '/docs/'
old_src = open(sys.argv[2], encoding='ascii').read().replace('\r\n', '\n')
new_src = open(wt + '/apply_patches.ps1', encoding='ascii').read().replace('\r\n', '\n')
oh = re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$", old_src); nh = re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$", new_src)
C = [i for i, _ in nh].index('visus') + 1
assert C == 83 and [i for i, _ in oh][C - 1] == 'sound'
FLAGS = ('BanRisk', 'PublicUntested', 'GameUntested', 'GrowsExe', 'DllRisky')
fl = lambda hs: {k: [i + 1 for i, (_, h) in enumerate(hs) if k + ' = $true' in h] for k in FLAGS}
OF, NF = fl(oh), fl(nh)
def rng(L):
    out = []; i = 0
    while i < len(L):
        j = i
        while j + 1 < len(L) and L[j + 1] == L[j] + 1: j += 1
        out += ([str(L[i])] if j == i else ([str(L[i]), str(L[j])] if j == i + 1 else ['%d–%d' % (L[i], L[j])])); i = j + 1
    return out
def txt(L, und):
    r = rng(L); return r[0] if len(r) == 1 else ', '.join(r[:-1]) + ' ' + und + ' ' + r[-1]
def relist(s, old, new):
    pat = re.escape(old).replace('\\ ', r'\s+')
    def f(m):
        span = m.group(0)
        if '\n' not in span: return new
        k = span.index('\n'); before = re.sub(r'\s+', ' ', span[:k]); ind = re.match(r'\n(\s*)', span[k:]).group(1)
        cut = new.rfind(' ', 0, len(before) + 1)
        return new if cut <= 0 else new[:cut] + '\n' + ind + new[cut + 1:]
    return re.subn(pat, f, s)
def sh(n):
    n = int(n); return str(n + 1 if n >= C else n)
def refs(s):
    def f(m):
        out = '%s %s' % (m.group(1), sh(m.group(2)))
        if m.group(3): out += m.group(3) + sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?', f, s)
def once(s, a, b):
    n = s.count(a); assert n == 1, (a[:90], n); return s.replace(a, b)
LUX = 'https://github.com/Stormhand-dev/Lux-Shoulder-Cam'
ROW = {'de': '| [83](PATCHES.de.md#patch-visus) | Visus - St0nyCam [BETA]: Schulterkamera und Zoom *(Schulterkamera per `/console visusHeight` und `visusShoulder`, Zoom bis 100 Yards)* | 🟠 **[ungetestet - Exe wird größer]** | St0ny | – | – | – |\n',
       'en': '| [83](PATCHES.en.md#patch-visus) | Visus - St0nyCam [BETA]: shoulder camera and zoom *(shoulder camera via `/console visusHeight` and `visusShoulder`, zoom up to 100 yards)* | 🟠 **[untested - exe grows]** | St0ny | – | – | – |\n'}
SEC = {'de': '''<a id="patch-visus"></a>
**Visus - St0nyCam [BETA]: Schulterkamera und Zoom** *(Nr. 83, Autor: St0ny)* 🟠 **[ungetestet - Exe wird größer]**

Eine eigene Schulterkamera und mehr Zoom direkt in der `Wow.exe`, ohne DLL.
Vorlage für die Schulterkamera ist [LuxShoulderCam](%s) von
Stormhand – mit seiner Erlaubnis. Der Code ist neu und aus eigener Analyse der
Exe entstanden.

> [!WARNING]
> **BETA** – noch ungetestet, online wie im Spiel. Deshalb ist der Patch
> standardmäßig abgewählt und vorerst nur in den dev-Zweigen, nicht in
> `st0ny-main`.

**Schulterkamera** – zwei neue Konsolen-Variablen:

| CVar            | Vorgabe | Bereich      | Wirkung |
|-----------------|---------|--------------|---------|
| `visusHeight`   | 0       | -1.0 bis 1.0 | hebt oder senkt den Punkt, um den die Kamera kreist (in Yards) |
| `visusShoulder` | 0       | -2.0 bis 2.0 | verschiebt ihn quer zur Blickrichtung: positiv nach rechts (Blick über die rechte Schulter, die Figur steht links im Bild), negativ nach links |

Der Versatz dreht mit der Kamera mit, in der Ich-Perspektive gibt es keinen.
Werte außerhalb der Bereiche werden auf die Grenze gesetzt. Beide Werte wirken
sofort und werden wie die anderen Kamera-Einstellungen in der `Config.wtf`
gespeichert. Beispiele für den Chat oder ein Makro:

```
/console visusShoulder 1
/console visusHeight 0.5
/run SetCVar("visusShoulder", GetCVar("visusShoulder") == "0" and 1 or 0)
```

Die letzte Zeile schaltet die Schulterkamera ein und aus – als Makro auf eine
Taste gelegt.

**Zoom** – WoW begrenzt die Kamera-Entfernung fest auf 50 Yards, Visus hebt die
Grenze auf 100 Yards. Eingestellt wird wie gewohnt: maximale Entfernung =
`cameraDistanceMax` (Vorgabe 15, jetzt bis 100 erlaubt) ×
`cameraDistanceMaxFactor` (den setzt auch der Regler für die Kamera-Entfernung
in den Interface-Optionen), z. B. `/console cameraDistanceMaxFactor 4` für 60
Yards. Das Zoom-Tempo `cameraDistanceMoveSpeed` hat jetzt die Vorgabe 20 statt
8.33 und lässt sich weiter bis 50 einstellen. Wer schon eigene Werte in der
`Config.wtf` hat, behält sie.

> [!NOTE]
> Nicht zusammen mit LuxShoulderCam verwenden (Lux-Lader Nr. 31 oder über
> Lexara): Beide setzen an derselben Stelle der Kamera an. Mit Visus hängt sich
> Lux dort nicht ein, Höhe und Versatz von Lux bleiben dann ohne Wirkung.

<details>
<summary><b>Hintergrund: Wie der Patch eingebaut ist</b></summary>

Visus hängt eine eigene Sektion `.visus` an die Exe an (512 Byte, ausführbar
und beschreibbar) und hängt sich an drei Stellen ein:

- **Neue Variablen:** Die Funktion, die alle Kamera-Variablen anlegt (VA
  `0x5FD910`), springt an ihrem Ende (VA `0x5FE2AF`) in die Sektion. Dort
  werden `visusHeight` und `visusShoulder` mit denselben Einstellungen wie die
  Kamera-Variablen des Clients angelegt.
- **Kamera:** Bei VA `0x6070CB` hat die Kamera-Funktion gerade den Blickpunkt
  berechnet. Visus addiert die Höhe und verschiebt den Punkt quer zur
  Blickrichtung. Die Richtung kommt aus der Kameraposition und dem im letzten
  Bild verschobenen Blickpunkt – so steht der Versatz immer genau quer zur
  Kamera.
- **Zoom:** Acht Stellen der Kamera lesen die feste Grenze von 50 Yards, sie
  zeigen jetzt auf 100 in der Sektion. Die Grenze des Zoom-Tempos (ebenfalls
  50) bleibt unverändert, die Vorgabe des Tempos steht in der Sektion.

</details>

''' % LUX, 'en': '''<a id="patch-visus"></a>
**Visus - St0nyCam [BETA]: shoulder camera and zoom** *(No. 83, Author: St0ny)* 🟠 **[untested - exe grows]**

A shoulder camera of its own and more zoom directly in `Wow.exe`, without a
DLL. The template for the shoulder camera is [LuxShoulderCam](%s)
by Stormhand – with his permission. The code is new and based on our own
analysis of the exe.

> [!WARNING]
> **BETA** – still untested, online and in game. That is why the patch is
> deselected by default and only in the dev branches for now, not in
> `st0ny-main`.

**Shoulder camera** – two new console variables:

| CVar            | Default | Range        | Effect |
|-----------------|---------|--------------|--------|
| `visusHeight`   | 0       | -1.0 to 1.0  | raises or lowers the point the camera orbits around (in yards) |
| `visusShoulder` | 0       | -2.0 to 2.0  | shifts it sideways to the view direction: positive to the right (look over the right shoulder, the character stands on the left of the screen), negative to the left |

The offset turns with the camera; in first person there is none. Values
outside the ranges are set to the limit. Both values take effect at once and
are saved in `Config.wtf` like the other camera settings. Examples for the
chat or a macro:

```
/console visusShoulder 1
/console visusHeight 0.5
/run SetCVar("visusShoulder", GetCVar("visusShoulder") == "0" and 1 or 0)
```

The last line switches the shoulder camera on and off – put it on a key as a
macro.

**Zoom** – WoW limits the camera distance to a fixed 50 yards, Visus raises the
limit to 100 yards. It is set as usual: maximum distance = `cameraDistanceMax`
(default 15, now allowed up to 100) × `cameraDistanceMaxFactor` (also set by
the camera distance slider in the interface options), e.g.
`/console cameraDistanceMaxFactor 4` for 60 yards. The zoom speed
`cameraDistanceMoveSpeed` now defaults to 20 instead of 8.33 and can still be
set up to 50. Values you already have in `Config.wtf` are kept.

> [!NOTE]
> Do not use it together with LuxShoulderCam (Lux loader No. 31 or via Lexara):
> both hook the same spot of the camera. With Visus, Lux does not hook in
> there, and Lux's height and offset have no effect.

<details>
<summary><b>Background: how the patch is built in</b></summary>

Visus appends a section `.visus` of its own to the exe (512 bytes, executable
and writable) and hooks in at three places:

- **New variables:** The function that creates all camera variables (VA
  `0x5FD910`) jumps into the section at its end (VA `0x5FE2AF`). There
  `visusHeight` and `visusShoulder` are created with the same settings as the
  client's camera variables.
- **Camera:** At VA `0x6070CB` the camera function has just computed the
  focus point. Visus adds the height and shifts the point sideways to the view
  direction. The direction comes from the camera position and the focus point
  shifted in the last frame – so the offset always stays exactly sideways to
  the camera.
- **Zoom:** Eight places of the camera read the fixed limit of 50 yards; they
  now point to 100 in the section. The limit of the zoom speed (also 50) stays
  unchanged, the default of the speed is in the section.

</details>

''' % LUX}
LUXNOTE = {'de': ('> geladene DLL zurück, ihr Startcode läuft kein zweites Mal.\n\n',
                  '> geladene DLL zurück, ihr Startcode läuft kein zweites Mal.\n\n'
                  'Nicht zusammen mit Visus - St0nyCam (Nr. 83) verwenden: Beide setzen an\n'
                  'derselben Stelle der Kamera an (VA `0x6070CB`). Ist Visus eingespielt, hängt\n'
                  'sich Lux dort nicht ein, Höhe und Versatz von Lux bleiben dann ohne Wirkung.\n\n'),
           'en': ('> its startup code does not run a second time.\n\n',
                  '> its startup code does not run a second time.\n\n'
                  'Do not use it together with Visus - St0nyCam (No. 83): both hook the same spot\n'
                  'of the camera (VA `0x6070CB`). If Visus is applied, Lux does not hook in there,\n'
                  "and Lux's height and offset have no effect.\n\n")}
THANKS = {'de': ('- Danke auch an **Stormhand** für die Erlaubnis, seine LuxShoulderCam\n  einzubauen. Das offizielle Preset seines Projekts\n  [Project Reforged](https://projectreforged.github.io/wotlk/) steckt als Preset\n  „Reforged“ in diesem Patcher und ist die Standard-Auswahl.\n',
                 '- Danke auch an **Stormhand** für die Erlaubnis, seine LuxShoulderCam\n  einzubinden und als Vorlage für Visus – St0nyCam zu nutzen. Das offizielle\n  Preset seines Projekts [Project Reforged](https://projectreforged.github.io/wotlk/)\n  steckt als Preset „Reforged“ in diesem Patcher und ist die Standard-Auswahl.\n'),
          'en': ('- Thanks also to **Stormhand** for the permission to include his\n  LuxShoulderCam. The official preset of his project\n  [Project Reforged](https://projectreforged.github.io/wotlk/) is included as\n  the preset "Reforged" and is the default selection.\n',
                 '- Thanks also to **Stormhand** for the permission to include his\n  LuxShoulderCam and to use it as the template for Visus – St0nyCam. The\n  official preset of his project\n  [Project Reforged](https://projectreforged.github.io/wotlk/) is included as\n  the preset "Reforged" and is the default selection.\n')}
for lang, rd, pd, nr, und in (('de', 'README.de.md', 'PATCHES.de.md', 'Nr.', 'und'), ('en', 'README.md', 'PATCHES.en.md', 'No.', 'and')):
    s = open(d + rd, encoding='utf-8').read()
    for k in FLAGS:
        o, nw = nr + ' ' + txt(OF[k], und), nr + ' ' + txt(NF[k], und)
        if o == nw: continue
        s, n = relist(s, o, nw); assert n >= 1, (rd, k, o); print(rd, k, n, 'x:', o, '->', nw)
    s = re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(pd), lambda m: '| [%s](%s#' % (sh(m.group(1)), pd), s)
    s = re.sub(r'(?m)^\| \[\d+\]\(.*$', lambda m: refs(m.group(0)), s)
    m = re.search(r'(?m)^\| \[82\]\(%s#patch-mouse\).*\n' % re.escape(pd), s); assert m
    s = s[:m.end()] + ROW[lang] + s[m.end():]
    s = once(s, *THANKS[lang])
    open(d + rd, 'w', encoding='utf-8', newline='\n').write(s)
    s = open(d + pd, encoding='utf-8').read()
    s = refs(s)
    s = once(s, *LUXNOTE[lang])
    a = s.index('<a id="patch-mouse"></a>'); z = s.index('\n## ', a) + 1
    s = s[:z] + SEC[lang] + s[z:]
    open(d + pd, 'w', encoding='utf-8', newline='\n').write(s)
print('Doku angepasst')

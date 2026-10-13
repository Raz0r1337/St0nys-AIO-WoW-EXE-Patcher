# Doku fuer den Lux-Lader (Nr. 31): Zeilen, Abschnitte, Nummern ab 31 (+1),
# Listen, Danksagung, CameraReforged-Zuordnung. md bleibt UTF-8 + LF.
import re, sys
d = sys.argv[1] + '/docs/'
URL = 'https://github.com/Stormhand-dev/Lux-Shoulder-Cam'
def sh(n):
    n = int(n); return str(n + 1 if n >= 31 else n)
def refs(s):
    def f(m):
        out = '%s %s' % (m.group(1), sh(m.group(2)))
        if m.group(3): out += m.group(3) + sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?', f, s)
def once(s, a, b):
    n = s.count(a)
    assert n == 1, (a[:100], n)
    return s.replace(a, b)

SEC = {'de': """<a id="patch-lux"></a>
**LuxShoulderCam.dll beim Start laden (Schulterkamera von Stormhand) [BETA]** *(Nr. 31, Autor: St0ny)* 🟠 **[ungetestet]**

Lädt beim Start die `LuxShoulderCam.dll` aus dem WoW-Ordner –
[LuxShoulderCam](%s) von Stormhand ist eine
Schulterkamera: Höhe und seitlicher Versatz der Kamera lassen sich im Spiel über
ein Fenster (`/lsc`) und eigene Tastenbelegungen einstellen. Dazu gehört das
Addon `LuxShoulderCam`, das in `Interface\\AddOns` liegen muss. Fehlt die DLL,
startet WoW ganz normal.

> [!WARNING]
> **BETA** – dieser Lader ist noch ungetestet, online wie im Spiel. Deshalb ist
> er standardmäßig abgewählt und vorerst nur in den dev-Zweigen, nicht in
> `st0ny-main`.

> [!NOTE]
> **Man braucht nur einen von beiden:** Lexara lädt die `LuxShoulderCam.dll`
> selbst mit, wenn sie im WoW-Ordner liegt – egal, ob Lexara über den
> Lexara-Lader (Nr. 30) oder als `dinput8.dll` geladen wird. Wer Lexara nutzt,
> braucht diesen Patch also nicht. Sind trotzdem beide aktiv, schadet das
> nicht: Windows lädt eine DLL mit demselben Namen pro Prozess nur einmal. Der
> zweite Aufruf von `LoadLibraryA("LuxShoulderCam.dll")` bekommt nur die schon
> geladene DLL zurück, ihr Startcode läuft kein zweites Mal.

Nicht zusammen mit CameraReforged (Nr. 83) verwenden: Beide setzen an derselben
Stelle der Kamera an (VA `0x6070CB`). Ist CameraReforged eingespielt, hängt sich
Lux dort nicht ein, Höhe und Versatz von Lux bleiben dann ohne Wirkung.

Dateigröße und PE-Header bleiben unverändert: Beim Start läuft einmalig der
Sprung bei VA `0x76E495` (zu einem bloßen `ret`) – nach dem Lexara- und dem
wow_optimize-Lader, vor dem voice.dll-Lader. Er führt jetzt durch drei freie
16-Byte-Lücken (VA `0x6B68A0`, `0x6B69C0`, `0x6B6AE0`), die den Namen
`LuxShoulderCam.dll` auf dem Stack ablegen, `LoadLibraryA` aufrufen und dann
zurückkehren. Wie bei Lexara wird die DLL also noch vor dem Spielcode geladen.
Lux selbst legt zur Laufzeit einen kleinen Sprung in die erste freie Lücke ab
24 Byte im Code der Exe; die drei Lücken des Laders sind kleiner, Lux wählt
also dieselbe Stelle wie beim Laden über Lexara. Der Patch verträgt sich mit
dem wow_optimize-Lader (Nr. 27), dem Lexara-Lader (Nr. 30) und dem
voice.dll-Lader (Nr. 32).

""" % URL, 'en': """<a id="patch-lux"></a>
**Load LuxShoulderCam.dll at startup (shoulder camera by Stormhand) [BETA]** *(No. 31, Author: St0ny)* 🟠 **[untested]**

Loads `LuxShoulderCam.dll` from the WoW folder at startup –
[LuxShoulderCam](%s) by Stormhand is an
over-the-shoulder camera: the height and sideways offset of the camera can be
set in game in a panel (`/lsc`) and with its own key bindings. It comes with
the addon `LuxShoulderCam`, which has to be in `Interface\\AddOns`. If the DLL is
missing, WoW starts normally.

> [!WARNING]
> **BETA** – this loader is still untested, online and in game. That is why it
> is deselected by default and only in the dev branches for now, not in
> `st0ny-main`.

> [!NOTE]
> **You only need one of the two:** Lexara loads `LuxShoulderCam.dll` by itself
> if it is in the WoW folder – no matter whether Lexara is loaded by the Lexara
> loader (No. 30) or as `dinput8.dll`. If you use Lexara, you do not need this
> patch. If both are active anyway, no harm is done: Windows loads a DLL with
> the same name only once per process. The second call of
> `LoadLibraryA("LuxShoulderCam.dll")` just gets the already loaded DLL back,
> its startup code does not run a second time.

Do not use it together with CameraReforged (No. 83): both hook the same spot of
the camera (VA `0x6070CB`). If CameraReforged is applied, Lux does not hook in
there, and Lux's height and offset have no effect.

File size and PE header stay unchanged: at startup the jump at VA `0x76E495`
(to a plain `ret`) runs once – after the Lexara and wow_optimize loaders,
before the voice.dll loader. It now leads through three free 16-byte gaps (VA
`0x6B68A0`, `0x6B69C0`, `0x6B6AE0`) that put the name `LuxShoulderCam.dll` on
the stack, call `LoadLibraryA` and return. Like with Lexara, the DLL is loaded
before any game code runs. Lux itself places a small jump into the first free
gap of 24 bytes or more in the exe's code at runtime; the loader's three gaps
are smaller, so Lux picks the same spot as when it is loaded by Lexara. The
patch works together with the wow_optimize loader (No. 27), the Lexara loader
(No. 30) and the voice.dll loader (No. 32).

""" % URL}

PAT = {'de': [
    ("Keine zusätzliche `dinput8.dll` von Lexara liegen lassen, sonst wird Lexara\ndoppelt geladen.\n",
     "Keine zusätzliche `dinput8.dll` von Lexara liegen lassen, sonst wird Lexara\ndoppelt geladen.\n\n"
     "Lexara lädt außerdem die `LuxShoulderCam.dll` (Schulterkamera von Stormhand)\n"
     "mit, wenn sie im WoW-Ordner liegt. Mit Lexara braucht man den Lux-Lader\n(Nr. 31) also nicht.\n"),
    ("Der Patch verträgt sich mit\ndem voice.dll-Lader (Nr. 32), der nur den Sprung direkt danach ändert.\n",
     "Der Patch verträgt sich mit\ndem Lux-Lader (Nr. 31) und dem voice.dll-Lader (Nr. 32), die nur spätere\nSprünge im Startcode ändern.\n"),
    ("Der Patch verträgt sich mit dem\nLexara-Lader (Nr. 30) und dem voice.dll-Lader (Nr. 32).\n",
     "Der Patch verträgt sich mit dem\nLexara-Lader (Nr. 30), dem Lux-Lader (Nr. 31) und dem voice.dll-Lader (Nr. 32).\n"),
    ("*(Nr. 83, Autor: Stormhand (fixed by St0ny))*", "*(Nr. 83, Autor: Zendevve (fixed by St0ny))*"),
    ("Portierung von [CameraReforged](https://github.com/Zendevve/CameraReforged)\nvon **Stormhand** in diesen Patcher, damit\n"
     "alles in einem Durchgang läuft – eingebaut mit seiner ausdrücklichen Erlaubnis\n"
     "(„Of course! Take whatever you need. I appreciate your work.“). Die Portierung\n"
     "und ihre Anpassungen stammen von St0ny. Der Client bekommt zwei komplett neue\n"
     "CVars eingebaut, zwei vorhandene bekommen neue Startwerte.\n",
     "Portierung von [CameraReforged](https://github.com/Zendevve/CameraReforged)\nvon **Zendevve** in diesen Patcher, damit alles in einem Durchgang läuft. Die\n"
     "Portierung und ihre Anpassungen stammen von St0ny. Der Client bekommt zwei\n"
     "komplett neue CVars eingebaut, zwei vorhandene bekommen neue Startwerte.\n"),
    ("> Chat-Fenster (Anzeigedauer der Nachrichten). Sie bleiben hier unangetastet.\n",
     "> Chat-Fenster (Anzeigedauer der Nachrichten). Sie bleiben hier unangetastet.\n\n"
     "> [!NOTE]\n> Nicht zusammen mit LuxShoulderCam verwenden (Lux-Lader Nr. 31 oder über\n"
     "> Lexara): Beide setzen an derselben Stelle der Kamera an (VA `0x6070CB`). Ist\n"
     "> dieser Patch eingespielt, hängt sich Lux dort nicht ein und bleibt ohne\n> Wirkung.\n"),
], 'en': [
    ("Do not leave an additional Lexara\n`dinput8.dll` there, otherwise Lexara is loaded twice.\n",
     "Do not leave an additional Lexara\n`dinput8.dll` there, otherwise Lexara is loaded twice.\n\n"
     "Lexara also loads `LuxShoulderCam.dll` (shoulder camera by Stormhand) if it\n"
     "is in the WoW folder. With Lexara you do not need the Lux loader (No. 31).\n"),
    ("The\npatch works together with the voice.dll loader (No. 32), which only changes\nthe jump right after it.\n",
     "The\npatch works together with the Lux loader (No. 31) and the voice.dll loader\n(No. 32), which only change later jumps in the startup code.\n"),
    ("The patch works together with the Lexara loader (No. 30) and the\nvoice.dll loader (No. 32).\n",
     "The patch works together with the Lexara loader (No. 30), the\nLux loader (No. 31) and the voice.dll loader (No. 32).\n"),
    ("*(No. 83, Author: Stormhand (fixed by St0ny))*", "*(No. 83, Author: Zendevve (fixed by St0ny))*"),
    ("Port of [CameraReforged](https://github.com/Zendevve/CameraReforged) by\n**Stormhand** into this patcher, so everything\n"
     "runs in one pass – included with his explicit permission (\"Of course! Take\n"
     "whatever you need. I appreciate your work.\"). The port and its adjustments were\n"
     "made by St0ny. The client gets two brand-new CVars and new default values for\n"
     "two existing ones.\n",
     "Port of [CameraReforged](https://github.com/Zendevve/CameraReforged) by\n**Zendevve** into this patcher, so everything runs in one pass. The port and\n"
     "its adjustments were made by St0ny. The client gets two brand-new CVars and\n"
     "new default values for two existing ones.\n"),
    ("> (display time of messages). They are left untouched here.\n",
     "> (display time of messages). They are left untouched here.\n\n"
     "> [!NOTE]\n> Do not use it together with LuxShoulderCam (Lux loader No. 31 or via Lexara):\n"
     "> both hook the same spot of the camera (VA `0x6070CB`). If this patch is\n"
     "> applied, Lux does not hook in there and has no effect.\n"),
]}

ROW = {'de': '| [31](PATCHES.de.md#patch-lux) | LuxShoulderCam.dll beim Start laden (Schulterkamera von Stormhand) [BETA] *(benötigt [LuxShoulderCam](%s) – mit Lexara (Nr. 30) nicht nötig)* | 🟠 **[ungetestet]** | St0ny | – | – | – |\n' % URL,
       'en': '| [31](PATCHES.en.md#patch-lux) | Load LuxShoulderCam.dll at startup (shoulder camera by Stormhand) [BETA] *(requires [LuxShoulderCam](%s) – not needed with Lexara (No. 30))* | 🟠 **[untested]** | St0ny | – | – | – |\n' % URL}

LEG = {'de': [
    ("Nr. 4, 10,\n    11, 23–25, 43, 44, 47–52, 76 und 84–88 (rote Warnung).",
     "Nr. 4, 10,\n    11, 23–25, 44, 45, 48–53, 77 und 85–89 (rote Warnung)."),
    ("kann zu Kick/Bann führen: Nr. 26, 31, 41, 46, 53, 64, 70, 73–75 und 82\n",
     "kann zu Kick/Bann führen: Nr. 26, 31, 32, 42, 47, 54, 65, 71, 74–76 und 83\n"),
    ("möglicherweise verbuggt: Nr. 25, 26, 31, 46, 53 und 64 (orange Warnung).",
     "möglicherweise verbuggt: Nr. 25, 26, 31, 32, 47, 54 und 65 (orange Warnung)."),
    ("    Nr. 9, 52, 65, 66, 76 und 82. Das ist keine sichere Bann-Gefahr,",
     "    Nr. 9, 53, 66, 67, 77 und 83. Das ist keine sichere Bann-Gefahr,"),
    ("(Nr. 9, 52, 65, 66, 76 und 82), entfernen", "(Nr. 9, 53, 66, 67, 77 und 83), entfernen"),
    ("Drei davon (Nr. 9, 65 und 66) vergrößern", "Drei davon (Nr. 9, 66 und 67) vergrößern"),
    ("- Danke auch an **Stormhand** für die Erlaubnis, seinen CameraReforged-Patch\n  einzubauen.",
     "- Danke auch an **Stormhand** für die Erlaubnis, seine LuxShoulderCam\n  einzubauen."),
], 'en': [
    ("No. 4, 10, 11, 23–25,\n    43, 44, 47–52, 76 and 84–88 (red warning).",
     "No. 4, 10, 11, 23–25,\n    44, 45, 48–53, 77 and 85–89 (red warning)."),
    ("you kicked or banned: No. 26, 31, 41, 46, 53, 64, 70, 73–75 and 82\n",
     "you kicked or banned: No. 26, 31, 32, 42, 47, 54, 65, 71, 74–76 and 83\n"),
    ("possibly buggy: No. 25, 26, 31, 46, 53 and 64 (orange warning).",
     "possibly buggy: No. 25, 26, 31, 32, 47, 54 and 65 (orange warning)."),
    ("`Wow.exe`: No. 9, 52,\n    65, 66, 76 and 82. This does not",
     "`Wow.exe`: No. 9, 53,\n    66, 67, 77 and 83. This does not"),
    ("(No. 9, 52, 65, 66, 76 and 82) also remove", "(No. 9, 53, 66, 67, 77 and 83) also remove"),
    ("(No. 9, 65 and 66) make `Wow.exe` larger", "(No. 9, 66 and 67) make `Wow.exe` larger"),
    ("- Thanks also to **Stormhand** for the permission to include his\n  CameraReforged patch.",
     "- Thanks also to **Stormhand** for the permission to include his\n  LuxShoulderCam."),
]}

for lang, rd, pd in (('de', 'README.de.md', 'PATCHES.de.md'), ('en', 'README.md', 'PATCHES.en.md')):
    # PATCHES: Nummern verschieben, dann Texte mit den neuen Nummern
    s = open(d + pd, encoding='utf-8').read()
    s = refs(s)
    for a, b in PAT[lang]: s = once(s, a, b)
    s = once(s, '<a id="patch-voicedll"></a>', SEC[lang] + '<a id="patch-voicedll"></a>')
    open(d + pd, 'w', encoding='utf-8', newline='\n').write(s)
    # README
    s = open(d + rd, encoding='utf-8').read()
    for a, b in LEG[lang]: s = once(s, a, b)
    s = re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(pd), lambda m: '| [%s](%s#' % (sh(m.group(1)), pd), s)
    s = re.sub(r'(?m)^\| \[\d+\]\(.*$', lambda m: refs(m.group(0)), s)
    m = re.search(r'(?m)^\| \[30\]\(%s#patch-lexara\).*\n' % re.escape(pd), s)
    assert m
    s = s[:m.end()] + ROW[lang] + s[m.end():]
    m = re.search(r'(?m)^\| \[83\]\(%s#patch-camera\).*$' % re.escape(pd), s)
    assert m and m.group(0).count('| Stormhand (fixed by St0ny) |') == 1
    s = s[:m.start()] + m.group(0).replace('| Stormhand (fixed by St0ny) |', '| Zendevve (fixed by St0ny) |') + s[m.end():]
    open(d + rd, 'w', encoding='utf-8', newline='\n').write(s)
print('Doku angepasst')

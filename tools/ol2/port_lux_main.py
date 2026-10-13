# Lux-Lader (LuxShoulderCam.dll) aus st0ny-dev nach st0ny-main: als Nr. 31 hinter Lexara,
# "ungetestet - DLL riskant", ohne [BETA] und ohne Bezuege auf Visus und den voice.dll-Lader.
# Nummern ab 31 ruecken um 1. Aufruf: port_lux_main.py <main-Worktree>  (Quelle: origin/st0ny-dev)
import sys, re, subprocess
w = sys.argv[1]
INS = 31

def dev(path):
    return subprocess.run(['git', '-C', w, 'show', 'origin/st0ny-dev:' + path], capture_output=True, text=True, check=True).stdout.replace('\r\n', '\n')

def rd(p, crlf=False):
    raw = open(w + '/' + p, 'rb').read()
    if crlf: assert raw.count(b'\r\n') == raw.count(b'\n')
    return raw.decode('ascii' if crlf else 'utf-8').replace('\r\n', '\n')

def wr(p, s, crlf=False):
    if crlf: open(w + '/' + p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
    else: open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

def once(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a))
    return s.replace(a, b)

def shift(s):
    # Nummernlisten hinter "Nr."/"No." (auch ueber Zeilenumbrueche, mit Bereichen): jede Zahl >= 31 um 1 erhoehen
    def fix(m):
        return m.group(1) + re.sub(r'\d+', lambda n: str(int(n.group(0)) + 1) if int(n.group(0)) >= INS else n.group(0), m.group(2))
    s = re.sub(r'((?:Nr\.|No\.) )(\d+(?:(?:–|-|,\s+|\s+und\s+|\s+and\s+)\d+)*)', fix, s)
    # Tabellenzeilen der Patch-Uebersicht
    s = re.sub(r'(?m)^\| \[(\d+)\]\(PATCHES', lambda m: '| [%d](PATCHES' % (int(m.group(1)) + (1 if int(m.group(1)) >= INS else 0)), s)
    return s

def fmt(nums, und):
    nums = sorted(nums); parts = []; i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1: j += 1
        if j - i >= 2: parts.append('%d–%d' % (nums[i], nums[j]))
        else: parts += [str(n) for n in nums[i:j + 1]]
        i = j + 1
    return parts[0] if len(parts) == 1 else ', '.join(parts[:-1]) + ' ' + und + ' ' + parts[-1]

# ---------- Skript ----------
s = rd('apply_patches.ps1', crlf=True)
s = shift(s)
d = dev('apply_patches.ps1')
a = d.index("    @{ Id = 'lux'"); z = d.index('\n    }}\n', a) + 8
lux = d[a:z]
lux = once(lux, "@{ Id = 'lux'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true\n",
           "@{ Id = 'lux'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true; DllRisky = $true\n")
lux = once(lux, "(Schulterkamera von Stormhand) [BETA]'", "(Schulterkamera von Stormhand)'")
lux = once(lux, "(shoulder camera by Stormhand) [BETA]'", "(shoulder camera by Stormhand)'")
lux = once(lux, "        # BETA - noch ungetestet. Laedt beim Start LuxShoulderCam.dll\n",
                "        # Noch ungetestet. Laedt beim Start LuxShoulderCam.dll\n")
lux = once(lux, """        # steht nur ein ret). Ihn erreicht nur der Einstiegspunkt, einmalig nach
        # dem Lexara- und dem wow_optimize-Lader, vor dem voice.dll-Lader. Der
        # Code steht in drei freien 16-Byte-Luecken hinter Aufrufen, die nie
        # zurueckkehren (wie beim Lexara-Lader), den DLL-Namen legt er auf den
        # Stack. Dateigroesse und PE-Header bleiben unveraendert.
""", """        # steht nur ein ret). Ihn erreicht nur der Einstiegspunkt, einmalig nach
        # dem Lexara- und dem wow_optimize-Lader. Der Code steht in drei freien
        # 16-Byte-Luecken hinter Aufrufen, die nie zurueckkehren (wie beim
        # Lexara-Lader), den DLL-Namen legt er auf den Stack. Dateigroesse und
        # PE-Header bleiben unveraendert.
""")
lux = once(lux, """        # dieselbe Stelle wie beim Laden ueber Lexara. Nicht zusammen mit Visus
        # (ShoulderCam): beide setzen an derselben Stelle der Kamera an.
""", """        # dieselbe Stelle wie beim Laden ueber Lexara.
""")
assert 'voice' not in lux and 'Visus' not in lux and 'BETA' not in lux
s = once(s, "\n    # --- Gameplay-Fixes ---\n", "\n" + lux + "\n    # --- Gameplay-Fixes ---\n")
s = once(s, "        # 0x76E490, den nur der Einstiegspunkt erreicht (nach dem Lexara-Lader).\n",
            "        # 0x76E490, den nur der Einstiegspunkt erreicht (nach dem Lexara-Lader,\n        # vor dem Lux-Lader).\n")
s = once(s, "        # Fehlt die DLL, startet WoW ganz normal.\n        Assert-Bytes 0x400 ",
            "        # Fehlt die DLL, startet WoW ganz normal. Lexara laedt selbst die\n"
            "        # LuxShoulderCam.dll mit, wenn sie im WoW-Ordner liegt (siehe Lux-Lader).\n        Assert-Bytes 0x400 ")
ids = re.findall(r"(?m)^    @\{ Id = '([^']+)'", s)
assert len(ids) == 87 and ids[INS - 1] == 'lux' and ids[INS - 2] == 'lexara', (len(ids), ids[28:33])
assert not re.search(r'[^\x00-\x7F]', s)
wr('apply_patches.ps1', s, crlf=True)

# Flags fuer die Listen der README
flags = {}
for n, b in enumerate(re.split(r"(?m)^(?=    @\{ Id = ')", s[s.index('$patches = @('):])[1:], 1):
    head = b.split('\n')[0]
    flags[n] = {f for f in ('BanRisk', 'PublicUntested', 'GameUntested', 'GrowsExe', 'DllRisky') if (f + ' = $true') in head}
lst = lambda f: [n for n in flags if f in flags[n]]

# ---------- README ----------
for fn, md, und, lang in (('docs/README.de.md', 'PATCHES.de.md', 'und', 'de'), ('docs/README.md', 'PATCHES.en.md', 'and', 'en')):
    s = shift(rd(fn))
    row = [l for l in dev(fn).split('\n') if l.startswith('| [31](%s#patch-lux)' % md)][0]
    if lang == 'de':
        row = once(row, ' [BETA] *(', ' *(')
        row = once(row, '🟠 **[ungetestet]**', '🟠 **[ungetestet - DLL riskant]**')
    else:
        row = once(row, ' [BETA] *(', ' *(')
        row = once(row, '🟠 **[untested]**', '🟠 **[untested - DLL risky]**')
    prev = [l for l in s.split('\n') if l.startswith('| [30](%s#patch-lexara)' % md)][0]
    s = once(s, prev + '\n', prev + '\n' + row + '\n')
    # Listen der Kennzeichnungen neu aus den Flags
    if lang == 'de':
        pats = [(r'(kann zu Kick/Bann führen: Nr\. )([^(]*?)( \(orange Warnung\))', 'PublicUntested'),
                (r'(möglicherweise verbuggt: Nr\. )([^(]*?)( \(orange Warnung\))', 'GameUntested'),
                (r'(erkannt oder blockiert werden kann: Nr\. )([^(]*?)(\n    \(gelber Hinweis\))', 'DllRisky')]
        s = once(s, "- Danke auch an **MacWarrior**, der ebenfalls beim Zusammentragen der Patches\n  geholfen und einige eigene Patches beigesteuert hat.\n",
                 "- Danke auch an **MacWarrior**, der ebenfalls beim Zusammentragen der Patches\n  geholfen und einige eigene Patches beigesteuert hat.\n"
                 "- Danke auch an **Stormhand** für die Erlaubnis, seine LuxShoulderCam\n  einzubinden.\n")
    else:
        pats = [(r'(you kicked or banned: No\. )([^(]*?)(\s+\(orange warning\))', 'PublicUntested'),
                (r'(possibly buggy: No\. )([^(]*?)( \(orange warning\))', 'GameUntested'),
                (r'(detected or blocked on public servers: No\. )([^(]*?)(\s+\(yellow note\))', 'DllRisky')]
        s = once(s, "- Thanks also to **MacWarrior**, who also helped collect the patches and\n  contributed some of his own.\n",
                 "- Thanks also to **MacWarrior**, who also helped collect the patches and\n  contributed some of his own.\n"
                 "- Thanks also to **Stormhand** for the permission to include his\n  LuxShoulderCam.\n")
    for p, f in pats:
        m = list(re.finditer(p, s))
        assert len(m) == 1, (fn, f, len(m))
        s = s[:m[0].start(2)] + fmt(lst(f), und) + s[m[0].end(2):]
    wr(fn, s)

# ---------- PATCHES ----------
for fn, lang in (('docs/PATCHES.de.md', 'de'), ('docs/PATCHES.en.md', 'en')):
    s = shift(rd(fn))
    dd = dev(fn)
    a = dd.index('<a id="patch-lux"></a>'); z = dd.index('<a id="patch-voicedll"></a>', a)
    sec = dd[a:z]
    if lang == 'de':
        sec = once(sec, '**LuxShoulderCam.dll beim Start laden (Schulterkamera von Stormhand) [BETA]** *(Nr. 31, Autor: St0ny)* 🟠 **[ungetestet]**',
                        '**LuxShoulderCam.dll beim Start laden (Schulterkamera von Stormhand)** *(Nr. 31, Autor: St0ny)* 🟠 **[ungetestet - DLL riskant]**')
        sec = once(sec, """> [!WARNING]
> **BETA** – dieser Lader ist noch ungetestet, online wie im Spiel. Deshalb ist
> er standardmäßig abgewählt und vorerst nur in den dev-Zweigen, nicht in
> `st0ny-main`.
""", """> [!WARNING]
> Noch ungetestet, online wie im Spiel – deshalb ist der Lader standardmäßig
> abgewählt. Er lädt nur eine DLL, die hier nicht enthalten ist. Die geladene
> `LuxShoulderCam.dll` kann aber auf öffentlichen Servern erkannt oder
> blockiert werden – also nur dort einsetzen, wo LuxShoulderCam erlaubt ist.
""")
        sec = once(sec, """Nicht zusammen mit Visus - ShoulderCam (Nr. 84) verwenden: Beide setzen an
derselben Stelle der Kamera an (VA `0x6070CB`). Ist Visus eingespielt, hängt
sich Lux dort nicht ein, Höhe und Versatz von Lux bleiben dann ohne Wirkung.

""", "")
        sec = once(sec, """Sprung bei VA `0x76E495` (zu einem bloßen `ret`) – nach dem Lexara- und dem
wow_optimize-Lader, vor dem voice.dll-Lader. Er führt jetzt durch drei freie
""", """Sprung bei VA `0x76E495` (zu einem bloßen `ret`) – nach dem Lexara- und dem
wow_optimize-Lader. Er führt jetzt durch drei freie
""")
        sec = once(sec, """also dieselbe Stelle wie beim Laden über Lexara. Der Patch verträgt sich mit
dem wow_optimize-Lader (Nr. 27), dem Lexara-Lader (Nr. 30) und dem
voice.dll-Lader (Nr. 32).
""", """also dieselbe Stelle wie beim Laden über Lexara. Der Patch verträgt sich mit
dem wow_optimize-Lader (Nr. 27) und dem Lexara-Lader (Nr. 30).
""")
        s = once(s, "den DLL-Namen legt der Thread auf dem Stack ab. Der Patch verträgt sich mit dem\nLexara-Lader (Nr. 30).\n",
                    "den DLL-Namen legt der Thread auf dem Stack ab. Der Patch verträgt sich mit dem\nLexara-Lader (Nr. 30) und dem Lux-Lader (Nr. 31).\n")
        s = once(s, "Keine zusätzliche `dinput8.dll` von Lexara liegen lassen, sonst wird Lexara\ndoppelt geladen.\n\n",
                    "Keine zusätzliche `dinput8.dll` von Lexara liegen lassen, sonst wird Lexara\ndoppelt geladen.\n\n"
                    "Lexara lädt außerdem die `LuxShoulderCam.dll` (Schulterkamera von Stormhand)\nmit, wenn sie im WoW-Ordner liegt. Mit Lexara braucht man den Lux-Lader\n(Nr. 31) also nicht.\n\n")
        s = once(s, "Einstiegspunkt geladen, der Zeitpunkt passt also.\n\n## Gameplay-Fixes",
                    "Einstiegspunkt geladen, der Zeitpunkt passt also. Der Patch verträgt sich mit\ndem Lux-Lader (Nr. 31), der nur einen späteren Sprung im Startcode ändert.\n\n"
                    + sec + "## Gameplay-Fixes")
    else:
        sec = once(sec, '**Load LuxShoulderCam.dll at startup (shoulder camera by Stormhand) [BETA]** *(No. 31, Author: St0ny)* 🟠 **[untested]**',
                        '**Load LuxShoulderCam.dll at startup (shoulder camera by Stormhand)** *(No. 31, Author: St0ny)* 🟠 **[untested - DLL risky]**')
        sec = once(sec, """> [!WARNING]
> **BETA** – this loader is still untested, online and in game. That is why it
> is deselected by default and only in the dev branches for now, not in
> `st0ny-main`.
""", """> [!WARNING]
> Still untested, online and in game – that is why the loader is deselected by
> default. It only loads a DLL that is not included here. The loaded
> `LuxShoulderCam.dll`, however, may be detected or blocked on public servers –
> so use it only where LuxShoulderCam is allowed.
""")
        sec = once(sec, """Do not use it together with Visus - ShoulderCam (No. 84): both hook the same spot
of the camera (VA `0x6070CB`). If Visus is applied, Lux does not hook in there,
and Lux's height and offset have no effect.

""", "")
        sec = once(sec, """(to a plain `ret`) runs once – after the Lexara and wow_optimize loaders,
before the voice.dll loader. It now leads through three free 16-byte gaps (VA
""", """(to a plain `ret`) runs once – after the Lexara and wow_optimize loaders. It
now leads through three free 16-byte gaps (VA
""")
        sec = once(sec, """are smaller, so Lux picks the same spot as when it is loaded by Lexara. The
patch works together with the wow_optimize loader (No. 27), the Lexara loader
(No. 30) and the voice.dll loader (No. 32).
""", """are smaller, so Lux picks the same spot as when it is loaded by Lexara. The
patch works together with the wow_optimize loader (No. 27) and the Lexara
loader (No. 30).
""")
        s = once(s, "the stack. The patch works together with the Lexara loader (No. 30).\n",
                    "the stack. The patch works together with the Lexara loader (No. 30) and the\nLux loader (No. 31).\n")
        s = once(s, "`dinput8.dll` there, otherwise Lexara is loaded twice.\n\n",
                    "`dinput8.dll` there, otherwise Lexara is loaded twice.\n\n"
                    "Lexara also loads `LuxShoulderCam.dll` (shoulder camera by Stormhand) if it\nis in the WoW folder. With Lexara you do not need the Lux loader (No. 31).\n\n")
        s = once(s, "proxy DLL is loaded before the entry point as well, so the timing matches.\n\n## Gameplay fixes",
                    "proxy DLL is loaded before the entry point as well, so the timing matches. The\npatch works together with the Lux loader (No. 31), which only changes a later\njump in the startup code.\n\n"
                    + sec + "## Gameplay fixes")
    assert 'voice' not in sec and 'Visus' not in sec and 'BETA' not in sec, fn
    wr(fn, s)
print('ok')

# st0ny-dev an st0ny-main angleichen: Lux-Lader (Nr. 31) ohne [BETA], "ungetestet - DLL riskant",
# Warnung wie in main. Aufruf: align_lux_dev.py <dev-Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs, crlf=False):
    raw = open(w + '/' + p, 'rb').read()
    s = raw.decode('ascii' if crlf else 'utf-8').replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:80], s.count(a))
        s = s.replace(a, b)
    if crlf: open(w + '/' + p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
    else: open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)
edit('apply_patches.ps1', [
    ("@{ Id = 'lux'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true\n",
     "@{ Id = 'lux'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true; DllRisky = $true\n"),
    ("(Schulterkamera von Stormhand) [BETA]'", "(Schulterkamera von Stormhand)'"),
    ("(shoulder camera by Stormhand) [BETA]'", "(shoulder camera by Stormhand)'"),
    ("        # BETA - noch ungetestet. Laedt beim Start LuxShoulderCam.dll\n", "        # Noch ungetestet. Laedt beim Start LuxShoulderCam.dll\n"),
], crlf=True)
edit('docs/README.de.md', [
    ("LuxShoulderCam.dll beim Start laden (Schulterkamera von Stormhand) [BETA] *(", "LuxShoulderCam.dll beim Start laden (Schulterkamera von Stormhand) *("),
    ("nicht nötig)* | 🟠 **[ungetestet]** | St0ny |", "nicht nötig)* | 🟠 **[ungetestet - DLL riskant]** | St0ny |"),
    ("erkannt oder blockiert werden kann: Nr. 27–30\n", "erkannt oder blockiert werden kann: Nr. 27–31\n"),
])
edit('docs/README.md', [
    ("Load LuxShoulderCam.dll at startup (shoulder camera by Stormhand) [BETA] *(", "Load LuxShoulderCam.dll at startup (shoulder camera by Stormhand) *("),
    ("(No. 30))* | 🟠 **[untested]** | St0ny |", "(No. 30))* | 🟠 **[untested - DLL risky]** | St0ny |"),
    ("detected or blocked on public servers: No. 27–30 (yellow note)", "detected or blocked on public servers: No. 27–31 (yellow note)"),
])
edit('docs/PATCHES.de.md', [
    ("**LuxShoulderCam.dll beim Start laden (Schulterkamera von Stormhand) [BETA]** *(Nr. 31, Autor: St0ny)* 🟠 **[ungetestet]**",
     "**LuxShoulderCam.dll beim Start laden (Schulterkamera von Stormhand)** *(Nr. 31, Autor: St0ny)* 🟠 **[ungetestet - DLL riskant]**"),
    ("""> [!WARNING]
> **BETA** – dieser Lader ist noch ungetestet, online wie im Spiel. Deshalb ist
> er standardmäßig abgewählt und vorerst nur in den dev-Zweigen, nicht in
> `st0ny-main`.
""", """> [!WARNING]
> Noch ungetestet, online wie im Spiel – deshalb ist der Lader standardmäßig
> abgewählt. Er lädt nur eine DLL, die hier nicht enthalten ist. Die geladene
> `LuxShoulderCam.dll` kann aber auf öffentlichen Servern erkannt oder
> blockiert werden – also nur dort einsetzen, wo LuxShoulderCam erlaubt ist.
"""),
])
edit('docs/PATCHES.en.md', [
    ("**Load LuxShoulderCam.dll at startup (shoulder camera by Stormhand) [BETA]** *(No. 31, Author: St0ny)* 🟠 **[untested]**",
     "**Load LuxShoulderCam.dll at startup (shoulder camera by Stormhand)** *(No. 31, Author: St0ny)* 🟠 **[untested - DLL risky]**"),
    ("""> [!WARNING]
> **BETA** – this loader is still untested, online and in game. That is why it
> is deselected by default and only in the dev branches for now, not in
> `st0ny-main`.
""", """> [!WARNING]
> Still untested, online and in game – that is why the loader is deselected by
> default. It only loads a DLL that is not included here. The loaded
> `LuxShoulderCam.dll`, however, may be detected or blocked on public servers –
> so use it only where LuxShoulderCam is allowed.
"""),
])
print('ok')

# Lux-Lader (Nr. 31): im Spiel getestet -> [sicher - DLL riskant] wie Lexara. Aufruf: lux_safe.py <Worktree> [dev]
import sys
w = sys.argv[1]
def edit(p, pairs, crlf=False):
    raw = open(w + '/' + p, 'rb').read()
    if crlf: assert raw.count(b'\r\n') == raw.count(b'\n')
    s = raw.decode('ascii' if crlf else 'utf-8').replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    if crlf: open(w + '/' + p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
    else: open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)
edit('apply_patches.ps1', [
    ("@{ Id = 'lux'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true; DllRisky = $true\n",
     "@{ Id = 'lux'; Cat = 'dll'; On = $false; DllRisky = $true\n"),
    ("        # Noch ungetestet. Laedt beim Start LuxShoulderCam.dll\n", "        # Laedt beim Start LuxShoulderCam.dll\n"),
], crlf=True)
edit('docs/README.de.md', [
    ("mit Lexara (Nr. 30) nicht nötig)* | 🟠 **[ungetestet - DLL riskant]** |", "mit Lexara (Nr. 30) nicht nötig)* | 🟡 **[sicher - DLL riskant]** |"),
])
edit('docs/README.md', [
    ("not needed with Lexara (No. 30))* | 🟠 **[untested - DLL risky]** |", "not needed with Lexara (No. 30))* | 🟡 **[safe - DLL risky]** |"),
])
edit('docs/PATCHES.de.md', [
    ("*(Nr. 31, Autor: St0ny)* 🟠 **[ungetestet - DLL riskant]**", "*(Nr. 31, Autor: St0ny)* 🟡 **[sicher - DLL riskant]**"),
    ("""> [!WARNING]
> Noch ungetestet, online wie im Spiel – deshalb ist der Lader standardmäßig
> abgewählt. Er lädt nur eine DLL, die hier nicht enthalten ist. Die geladene
> `LuxShoulderCam.dll` kann aber auf öffentlichen Servern erkannt oder
> blockiert werden – also nur dort einsetzen, wo LuxShoulderCam erlaubt ist.
""", """> [!WARNING]
> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten
> ist. Die geladene `LuxShoulderCam.dll` kann aber auf öffentlichen Servern
> erkannt oder blockiert werden – also nur dort einsetzen, wo LuxShoulderCam
> erlaubt ist.
"""),
])
edit('docs/PATCHES.en.md', [
    ("*(No. 31, Author: St0ny)* 🟠 **[untested - DLL risky]**", "*(No. 31, Author: St0ny)* 🟡 **[safe - DLL risky]**"),
    ("""> [!WARNING]
> Still untested, online and in game – that is why the loader is deselected by
> default. It only loads a DLL that is not included here. The loaded
> `LuxShoulderCam.dll`, however, may be detected or blocked on public servers –
> so use it only where LuxShoulderCam is allowed.
""", """> [!WARNING]
> The patch itself is safe, it only loads a DLL that is not included here.
> The loaded `LuxShoulderCam.dll`, however, may be detected or blocked on
> public servers – so use it only where LuxShoulderCam is allowed.
"""),
])
print('ok')

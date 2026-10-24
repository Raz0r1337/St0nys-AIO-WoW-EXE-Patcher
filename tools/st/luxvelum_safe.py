#!/usr/bin/env python3
# Luxvelum-Lader als sicher markieren (ohne PublicUntested/GameUntested, bleibt "DLL riskant") und ins Preset
# "Reforged" aufnehmen. Patcher: Flags, $PRESET_REFORGED, Kommentar dazu; README DE/EN: Zeile (Status, Spalte
# "Reforged"), Listen unter "Hinweise", Absatz zum Preset; PATCHES DE/EN: Status in der Ueberschrift, Warnkasten.
# Nummern werden aus der Patch-Liste bestimmt (gleiches Skript fuer st0ny-dev und st0ny-main).
# Aufruf: luxvelum_safe.py <Ordner des Zweigs>
import sys, os, re
D = sys.argv[1]
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
def once(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:80], s.count(a)); return s.replace(a, b)
# ---------------- Patcher ----------------
p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
ids = re.findall(r"(?m)^    @\{ Id = '(\w+)'", s[s.index('\n$patches = @(\n'):])
N = {i: k + 1 for k, i in enumerate(ids)}
nl, nx, nu, nv, nw = N['luxvelum'], N['lexara'], N['lux'], N['awesome'], N['lights']
assert nl == nu + 1
s = once(s, "    @{ Id = 'luxvelum'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true; DllRisky = $true\n",
            "    @{ Id = 'luxvelum'; Cat = 'dll'; On = $false; DllRisky = $true\n", 'Flags')
s = once(s, "    'glue', 'awesome', 'lexara', 'lux',\n", "    'glue', 'awesome', 'lexara', 'lux', 'luxvelum',\n", 'Preset')
s = once(s, """# Lader fuer awesome_wotlk, Lexara und Lux (Nr. %d, %d und %d, Patch sicher,
# DLL riskant; Lexara laedt Lux ohnehin mit, der Lux-Lader auch ohne Lexara)
""" % (nv, nx, nu), """# Lader fuer awesome_wotlk, Lexara, Lux und Luxvelum (Nr. %d, %d, %d und %d,
# Patch sicher, DLL riskant; Lexara laedt Lux ohnehin mit, der Lux-Lader auch
# ohne Lexara)
""" % (nv, nx, nu, nl), 'Kommentar')
wr(p, s, True)
# ---------------- Doku ----------------
def drop(m):
    """Nr. nl aus einer Liste wie "Nr. 10, 26, 32, 33, ..." nehmen (steht nie am Anfang oder Ende)."""
    return m.group(0).replace(', %d,' % nl, ',', 1)
for lang, rdm, pdm in (('de', 'README.de.md', 'PATCHES.de.md'), ('en', 'README.md', 'PATCHES.en.md')):
    old, new = (('🟠 **[ungetestet - DLL riskant]**', '🟡 **[sicher - DLL riskant]**') if lang == 'de' else
                ('🟠 **[untested - DLL risky]**', '🟡 **[safe - DLL risky]**'))
    # README: Zeile, Listen, Absatz
    q = os.path.join(D, 'docs', rdm); t = rd(q)
    m = re.search(r'(?m)^\| \[%d\]\(%s#patch-luxvelum\) \|.*\n' % (nl, re.escape(pdm)), t); assert m
    row = m.group(0); c = row.rstrip('\n').split('|')
    assert c[-6].strip() == old and c[-4].strip() == '–', row
    c[-6] = ' %s ' % new; c[-4] = ' ✅ '
    t = t[:m.start()] + '|'.join(c) + '\n' + t[m.end():]
    if lang == 'de':
        heads = ('    kann zu Kick/Bann führen: Nr.', '    möglicherweise verbuggt: Nr.')
    else:
        heads = ('    you kicked or banned: No.', '    possibly buggy: No.')
    for h in heads:
        m = re.search(re.escape(h) + r'[^(]*\(', t); assert m and ', %d,' % nl in m.group(0), h
        t = t[:m.start()] + drop(m) + t[m.end():]
    if lang == 'de':
        t = once(t, """Lux-Lader (Nr. %d) für die Schulterkamera LuxShoulderCam und der
Licht-Patch Nr. %d. Bei den drei Ladern ist der Patch selbst sicher, die
""" % (nu, nw), """Lux-Lader (Nr. %d) für die Schulterkamera LuxShoulderCam, der Luxvelum-Lader
(Nr. %d) für volumetrischen Nebel, Licht und Wasser und der Licht-Patch
Nr. %d. Bei den vier Ladern ist der Patch selbst sicher, die
""" % (nu, nl, nw), rdm)
    else:
        t = once(t, """(No. %d) for Stormhand's HD fonts, the Lux loader (No. %d) for the
LuxShoulderCam shoulder camera and the light patch No. %d. For the three
loaders the patch itself is safe,""" % (nx, nu, nw), """(No. %d) for Stormhand's HD fonts, the Lux loader (No. %d) for the
LuxShoulderCam shoulder camera, the Luxvelum loader (No. %d) for volumetric
fog, light and water and the light patch No. %d. For the four
loaders the patch itself is safe,""" % (nx, nu, nl, nw), rdm)
    wr(q, t)
    # PATCHES: Ueberschrift, Warnkasten
    q = os.path.join(D, 'docs', pdm); t = rd(q)
    if lang == 'de':
        h = '**Luxvelum.dll beim Start laden (Nebel, Licht und Wasser - Atmospheric Immersion for Project Reforged)** *(Nr. %d, Autor: St0ny)* ' % nl
        t = once(t, """> [!WARNING]
> Noch ungetestet, online wie im Spiel. Deshalb ist der Patch standardmäßig
> abgewählt und vorerst nur im Zweig `st0ny-dev`. Der Patch selbst lädt nur
> eine DLL, die hier nicht enthalten ist – die `Luxvelum.dll` kann aber auf
> öffentlichen Servern erkannt oder blockiert werden.
""", """> [!WARNING]
> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten
> ist. Die geladene `Luxvelum.dll` kann aber auf öffentlichen Servern erkannt
> oder blockiert werden – also nur dort einsetzen, wo Luxvelum erlaubt ist.
""", pdm)
    else:
        h = '**Load Luxvelum.dll at startup (fog, light and water - Atmospheric Immersion for Project Reforged)** *(No. %d, Author: St0ny)* ' % nl
        t = once(t, """> [!WARNING]
> Still untested, online and in game. That is why the patch is deselected by
> default and only in the `st0ny-dev` branch for now. The patch itself only
> loads a DLL that is not included here – but `Luxvelum.dll` may be detected or
> blocked on public servers.
""", """> [!WARNING]
> The patch itself is safe, it only loads a DLL that is not included here.
> The loaded `Luxvelum.dll`, however, may be detected or blocked on public
> servers – so use it only where Luxvelum is allowed.
""", pdm)
    t = once(t, h + old + '\n', h + new + '\n', pdm)
    wr(q, t)
print('Luxvelum (Nr. %d) sicher, im Preset Reforged' % nl)

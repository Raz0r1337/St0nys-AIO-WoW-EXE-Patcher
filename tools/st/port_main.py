#!/usr/bin/env python3
# st0ny-main bekommt aus st0ny-dev: RCE-Fix v2 (Nr. 10, "riskant - online ungetestet", mit Blocked-Kennzeichnung,
# Nr. 11 ohne Obsoletes, awesome-Lader mit direktem LoadLibraryA, Danksagung Brady Russell / Pogzur) und die
# Licht-Patches (Nr. 67 "Mehr Lichter", Nr. 68 "Lichter bleiben an" - online getestet, sicher, im Reforged-Preset).
# Die bisherigen Nr. 67-87 werden zu 69-89. Ueber Anker statt Nummern; dev muss vorher status_dev.py haben.
# Aufruf: port_main.py <dev-Ordner (Quelle)> <main-Ordner (Ziel, wird geaendert)>
import sys, os, re
DEV, DST = sys.argv[1], sys.argv[2]
FIRST, LAST, SHIFT = 67, 87, 2                      # main: 67 tracker ... 87 clienticon -> 69 ... 89
DEVMAP = {69: 67, 70: 68}                           # dev-Nummern der Licht-Patches -> main
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
def once(s, a, b, tag=''):
    assert s.count(a) == 1, (tag, a[:90], s.count(a)); return s.replace(a, b)
def section(s, start, end):
    i = s.index(start); j = s.index(end, i + len(start)); return s[i:j]
def sh(n): n = int(n); return str(n + SHIFT if FIRST <= n <= LAST else n)
def refs(s):
    # "Nr. 74", "Nr. 73–75", "Nr. 78 und 79" - Listen mit Kommas werden einzeln ersetzt (siehe unten)
    def f(m):
        out = '%s %s' % (m.group(1), sh(m.group(2)))
        if m.group(3): out += m.group(3) + sh(m.group(4))
        if m.group(5): out += m.group(5) + sh(m.group(6))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?:(–)(\d+))?(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?', f, s)
def table(s, md):
    return re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(md), lambda m: '| [%s](%s#' % (sh(m.group(1)), md), s)
def devnum(s, nr):
    # Verweise in den uebernommenen dev-Texten: nur Nr. 69/70 erlaubt -> 67/68
    found = set(int(x) for x in re.findall(r'%s (\d+)' % re.escape(nr), s))
    assert found <= set(DEVMAP), found
    return re.sub(r'(%s )(\d+)' % re.escape(nr), lambda m: m.group(1) + str(DEVMAP[int(m.group(2))]), s)
def entry(src, id_):
    m = re.search(r"^    @\{ Id = '%s';.*?\n    \}\}\n" % id_, src, re.M | re.S); return m.group(0)

# ================= apply_patches.ps1 =================
dev = rd(os.path.join(DEV, 'apply_patches.ps1'), True); s = rd(os.path.join(DST, 'apply_patches.ps1'), True)
# --- RCE v2 ---
for id_ in ('rce', 'wardenoff'):
    s = once(s, entry(s, id_), entry(dev, id_), id_)
a = entry(s, 'awesome'); d = entry(dev, 'awesome')
a2 = once(a, "       Author = 'FrostAtom'\n", "       Author = 'FrostAtom (fixed by St0ny)'\n", 'awesome author')
cm = section(d, '        # Angepasst (St0ny)', '        Patch 0xABD0')
a2 = once(a2, '        Patch 0xABD0', cm + '        Patch 0xABD0', 'awesome comment')
a2 = once(a2, '0x68, 0xE0, 0x5C, 0x4E, 0x00, 0xE8, 0x1C, 0x68, 0x38, 0x00, 0x83, 0xC4, 0x04,', '0x68, 0xE0, 0x5C, 0x4E, 0x00, 0xFF, 0x15, 0x48, 0xF2, 0x9D, 0x00, 0x90, 0x90,', 'awesome bytes')
s = once(s, a, a2, 'awesome')
assert entry(s, 'awesome') == entry(dev, 'awesome'), 'awesome != dev'
for a_, b_ in [
("        CheatBan      = 'Das kann zu einem Bann fuehren - nur auf Servern nutzen, die das erlauben!'\n",
 "        CheatBan      = 'Das kann zu einem Bann fuehren - nur auf Servern nutzen, die das erlauben!'\n        BlockedHead   = 'VORSICHT - riskant: Diese Patches werden auf manchen Servern geblockt:'\n        BlockedWarn   = 'Im Zweifel die Regeln deines Servers pruefen.'\n"),
("        CheatBan      = 'This can lead to a ban - only use them on servers that allow it!'\n",
 "        CheatBan      = 'This can lead to a ban - only use them on servers that allow it!'\n        BlockedHead   = 'CAUTION - risky: these patches get blocked on some servers:'\n        BlockedWarn   = 'If in doubt, check the rules of your server.'\n"),
("        TagBan        = 'unsicher'\n", "        TagBan        = 'unsicher'\n        TagBlocked    = 'riskant'\n"),
("        TagBan        = 'unsafe'\n", "        TagBan        = 'unsafe'\n        TagBlocked    = 'risky'\n"),
("# GameUntested = Funktion im Spiel ungetestet (4), dazu GrowsExe und DllRisky.\n",
 "# GameUntested = Funktion im Spiel ungetestet (4), Blocked = riskant, wird auf\n# manchen Servern geblockt (5), dazu GrowsExe und DllRisky.\n"),
("    if ($p.BanRisk) { $tags += T 'TagBan' }\n", "    if ($p.BanRisk) { $tags += T 'TagBan' }\n    if ($p.Blocked) { $tags += T 'TagBlocked' }\n"),
("#    Warn-Codes - Patches ohne die drei folgenden Flags sind sicher (Code 1,\n", "#    Warn-Codes - Patches ohne die vier folgenden Flags sind sicher (Code 1,\n"),
("#    GameUntested - optional: $true, wenn die Funktion im Spiel ungetestet\n#            ist - moeglicherweise verbuggt (Code 4, oranger Hinweis)\n",
 "#    GameUntested - optional: $true, wenn die Funktion im Spiel ungetestet\n#            ist - moeglicherweise verbuggt (Code 4, oranger Hinweis)\n#    Blocked - optional: $true, wenn der Patch auf manchen Servern geblockt\n#            wird - riskant (Code 5, oranger Hinweis)\n"),
("    Say (T 'CheatBan') 'Red'\n}\n",
 "    Say (T 'CheatBan') 'Red'\n}\n$blocked = @()\nforeach ($p in $chosen) { if ($p.Blocked) { $blocked += PatchRef $p } }\nif ($blocked.Count -gt 0) {\n    Write-Host ''\n    Say (T 'BlockedHead') 'DarkYellow'\n    foreach ($m in $blocked) { Say \"  - $m\" 'DarkYellow' }\n    Say (T 'BlockedWarn') 'DarkYellow'\n}\n"),
]: s = once(s, a_, b_, 'blocked')
# --- Licht-Patches ---
s = refs(s)
k = dev.index('function Add-MoreLights {')
a = dev.rindex('# ============================================================\n', 0, dev.rindex('# ============================================================\n', 0, k))
b = dev.index('\n}\n', k) + 3
func = dev[a:b]
assert func.count('function ') == 1 and 'Mehr Lichter' in func and not re.search(r'Nr\. \d', func)
s = once(s, '# ============================================================\n#  Wasserzeichen\n', func + '\n# ============================================================\n#  Wasserzeichen\n', 'func')
s = once(s, entry(s, 'iconsnap'), entry(s, 'iconsnap') + '\n' + entry(dev, 'lights') + '\n' + entry(dev, 'lightstay'), 'entries')   # Ende von Grafik & Sichtweite
s = once(s, "    'occluder', 'bluemoon', 'notransparency', 'hdportraits', 'iconsnap',\n    'tracker',",
         "    'occluder', 'bluemoon', 'notransparency', 'hdportraits', 'iconsnap',\n    'lights', 'lightstay',\n    'tracker',", 'preset')
s = once(s, "# Lexara-Lader (Nr. 30, Patch sicher, DLL riskant). Im Menue mit R, ueber\n# -Select reforged; gilt beim ersten Start und fuer neue Patches.\n",
         "# Lexara-Lader (Nr. 30, Patch sicher, DLL riskant) und die Licht-Patches\n# Nr. 67 und 68 (im Spiel und online getestet, sicher; Nr. 67 vergroessert\n# die Wow.exe ebenfalls). Im Menue mit R, ueber -Select reforged; gilt beim\n# ersten Start und fuer neue Patches.\n", 'preset comment')
assert all(ord(c) < 128 for c in s), 'Skript nicht ASCII'
wr(os.path.join(DST, 'apply_patches.ps1'), s, True)

# ================= PATCHES =================
PE_DE = "> [!NOTE]\n> Sind alle Patches mit eigener Sektion gleichzeitig aktiv, ist im PE-Header\n> kein Platz mehr für einen weiteren Sektionseintrag. Dann verlängert der\n> Patcher die zuletzt angehängte Sektion, statt eine neue anzulegen.\n\n"
PE_EN = "> [!NOTE]\n> If all patches with a section of their own are active at the same time,\n> there is no room left in the PE header for another section entry. Then the\n> patcher extends the last appended section instead of adding a new one.\n\n"
for f, nr, fixed, pe, ui in (('PATCHES.de.md', 'Nr.', 'Autor: FrostAtom)', PE_DE, '## Interface & Komfort\n\n<a id="patch-tracker"></a>'),
                             ('PATCHES.en.md', 'No.', 'Author: FrostAtom)', PE_EN, '## Interface & comfort\n\n<a id="patch-tracker"></a>')):
    dev = rd(os.path.join(DEV, 'docs', f)); s = rd(os.path.join(DST, 'docs', f))
    # RCE v2 (Nr. 10/11 bleiben gleich)
    s = once(s, section(s, '<a id="patch-rce"></a>', '<a id="patch-wardenoff"></a>'), section(dev, '<a id="patch-rce"></a>', '<a id="patch-wardenoff"></a>'), 'rce section')
    s = once(s, section(s, '<a id="patch-wardenoff"></a>', '<a id="patch-scandll"></a>'), section(dev, '<a id="patch-wardenoff"></a>', '<a id="patch-scandll"></a>'), 'wardenoff section')
    aw = section(s, '<a id="patch-awesome"></a>', '> [!WARNING]'); aw2 = once(aw, fixed, fixed[:-1] + ' (fixed by St0ny))', 'awesome author')
    da = section(dev, '<a id="patch-awesome"></a>', '> [!WARNING]')
    add = da[da.index('\n\n', da.index('normal weiter.\n' if nr == 'Nr.' else 'starts normally.\n')):]   # Absatz "Anders als im Original ..."
    aw2 = aw2.rstrip('\n') + add
    s = once(s, aw, aw2, 'awesome section')
    hdp = ('Nr. 66 (HD-Portraits)', 'Nr. 65 (HD-Portraits)') if nr == 'Nr.' else ('No. 66 (HD portraits)', 'No. 65 (HD portraits)')   # dev hat Nr. 32 voice.dll
    assert section(s, '<a id="patch-awesome"></a>', '<a id="patch-wotlkext"></a>') == section(dev, '<a id="patch-awesome"></a>', '<a id="patch-wotlkext"></a>').replace(*hdp), 'awesome doc != dev'
    # Licht-Patches nach "Icons pixelgenau", ohne den PE-Header-Hinweis (in main passen alle Sektionen)
    s = refs(s)
    sec = section(dev, '<a id="patch-lights"></a>', ui)   # bis vor die Ueberschrift "Interface & Komfort"
    assert sec.count(pe) == 1; sec = sec.replace(pe, '')
    sec = devnum(sec, nr)
    s = once(s, ui, sec + ui, 'lights sections')
    wr(os.path.join(DST, 'docs', f), s)

# ================= README =================
for f, md in (('README.de.md', 'PATCHES.de.md'), ('README.md', 'PATCHES.en.md')):
    dev = rd(os.path.join(DEV, 'docs', f)); s = rd(os.path.join(DST, 'docs', f)); de = f.endswith('de.md')
    # --- RCE v2 ---
    if de:
        s = once(s, '(Warden komplett abschalten ersetzt den RCE-Fix) und wenn gewählte Patches eine\n', '(der vollständige LUA-Unlock ersetzt den einfachen) und wenn gewählte Patches eine\n', 'hint')
        s = once(s, '| 🔴 **[unsicher]** | Bestätigte Bann-Gefahr: kann auf vielen Servern zu einem Bann führen. Nur auf Servern nutzen, die das erlauben. | rote Warnung |\n',
                 '| 🔴 **[unsicher]** | Bestätigte Bann-Gefahr: kann auf vielen Servern zu einem Bann führen. Nur auf Servern nutzen, die das erlauben. | rote Warnung |\n| 🟠 **[riskant]** | Wird auf manchen Servern geblockt. Im Zweifel die Regeln deines Servers prüfen. | orange Warnung |\n', 'legend')
        brady = section(dev, '- Danke an **Brady Russell**', '- Ein großes Dankeschön'); pog = section(dev, '- Danke an **Pogzur**', '- Und natürlich')
        s = once(s, '- Ein großes Dankeschön an **Stormhand**', brady + '- Ein großes Dankeschön an **Stormhand**', 'brady')
        s = once(s, '- Und natürlich danke an alle Autoren', pog + '- Und natürlich danke an alle Autoren', 'pogzur')
        s = once(s, "Warnung tragen – rot bei Bann-Gefahr, orange bei Patches, die auf öffentlichen\nServern oder im Spiel noch ungetestet sind, und gelb bei vergrößerter\n`Wow.exe` (siehe [Hinweise](#hinweise)).",
                 "Warnung tragen – rot bei Bann-Gefahr, orange bei Patches, die auf manchen\nServern geblockt werden oder auf öffentlichen Servern oder im Spiel noch\nungetestet sind, und gelb bei vergrößerter `Wow.exe` (siehe\n[Hinweise](#hinweise)).", 'orange')
    else:
        s = once(s, 'when a companion patch is missing (e.g. the extended slider maximums need the\nCVar unlocks), when one patch makes another unnecessary (disabling Warden\ncompletely replaces the RCE fix) and when selected patches carry a warning –\n',
                 'when a companion patch is missing (e.g. the extended slider maximums need the\nCVar unlocks), when one patch makes another unnecessary (the complete LUA\nunlock replaces the basic one) and when selected patches carry a warning –\n', 'hint')
        s = once(s, '| 🔴 **[unsafe]** | Confirmed ban risk: can lead to a ban on many servers. Only use it on servers that allow it. | red warning |\n',
                 '| 🔴 **[unsafe]** | Confirmed ban risk: can lead to a ban on many servers. Only use it on servers that allow it. | red warning |\n| 🟠 **[risky]** | Gets blocked on some servers. If in doubt, check the rules of your server. | orange warning |\n', 'legend')
        brady = section(dev, '- Thanks to **Brady Russell**', '- A big thank you'); pog = section(dev, '- Thanks to **Pogzur**', '- And of course')
        s = once(s, '- A big thank you to **Stormhand**', brady + '- A big thank you to **Stormhand**', 'brady')
        s = once(s, '- And of course thanks to all patch authors', pog + '- And of course thanks to all patch authors', 'pogzur')
        s = once(s, "red for ban risk, orange for patches that are still untested on public\nservers or in game, and yellow for a larger `Wow.exe` (see [Notes](#notes)).",
                 "red for ban risk, orange for patches that get blocked on some servers or are\nstill untested on public servers or in game, and yellow for a larger\n`Wow.exe` (see [Notes](#notes)).", 'orange')
    row = [l for l in dev.split('\n') if l.startswith('| [10](%s#patch-rce)' % md)][0]
    s, n = re.subn(r'(?m)^\| \[10\]\(%s#patch-rce\).*$' % re.escape(md), lambda m: row, s); assert n == 1, 'rce row'
    s, n = re.subn(r'(?m)^(\| \[\d+\]\(%s#patch-awesome\).*)\| FrostAtom \|' % re.escape(md), r'\1| FrostAtom (fixed by St0ny) |', s); assert n == 1, 'awesome row'
    # --- Licht-Patches: Nummern 67-87 -> 69-89, dann die Zeilen 67/68 nach "Icons pixelgenau" ---
    s = table(refs(s), md)
    rows = []
    for dn, anchor in ((69, 'lights'), (70, 'lightstay')):
        r = [l for l in dev.split('\n') if l.startswith('| [%d](%s#patch-%s)' % (dn, md, anchor))]
        assert len(r) == 1, r
        rows.append(r[0].replace('| [%d](' % dn, '| [%d](' % DEVMAP[dn], 1))
    k = s.index('| [66](%s#patch-iconsnap)' % md); k = s.index('\n', k) + 1   # Ende der Tabelle Grafik & Sichtweite
    s = s[:k] + '\n'.join(rows) + '\n' + s[k:]
    # --- Listen unter "Hinweise": refs() verschiebt nur die erste Nummer nach "Nr.", der Rest steht hier
    # noch mit alten Nummern und wird von Hand gesetzt; Nr. 31 (Lux, sicher - DLL riskant) raus ---
    if de:
        for a_, b_ in [
            ('Nr. 4, 10,\n    11, 23–25, 43, 44, 47–52, 76 und 83–87 (rote Warnung).\n',
             'Nr. 4,\n    11, 23–25, 43, 44, 47–52, 78 und 85–89 (rote Warnung).\n  - 🟠 **riskant** – wird auf manchen Servern geblockt: Nr. 10 (orange Warnung).\n'),
            ('kann zu Kick/Bann führen: Nr. 26, 31, 41, 46, 53, 64, 70 und 73–75 (orange Warnung).',
             'kann zu Kick/Bann führen: Nr. 10, 26, 41, 46, 53, 64, 72 und 75–77 (orange Warnung).'),
            ('möglicherweise verbuggt: Nr. 25, 26, 31, 46, 53 und 64 (orange Warnung).',
             'möglicherweise verbuggt: Nr. 25, 26, 46, 53 und 64 (orange Warnung).'),
            ('    Nr. 9, 52, 65, 66 und 76. Das ist keine sichere Bann-Gefahr,', '    Nr. 9, 52, 65–67 und 78. Das ist keine sichere Bann-Gefahr,'),
            ('(Nr. 9, 52, 65, 66 und 76), entfernen', '(Nr. 9, 52, 65–67 und 78), entfernen'),
            ('Dazu kommt der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften. Der Patch\nselbst ist sicher, die `Lexara.dll` kann auf öffentlichen Servern aber erkannt\noder blockiert werden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts.\n',
             'Dazu kommen der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften und die\nLicht-Patches Nr. 67 und 68. Beim Lexara-Lader ist der Patch selbst sicher,\ndie `Lexara.dll` kann auf öffentlichen Servern aber erkannt oder blockiert\nwerden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts. Die Licht-Patches\nsind im Spiel und online getestet und sicher. Nr. 67 vergrößert die\n`Wow.exe` ebenfalls und wirkt erst mit den Shadern aus\n[WoW-lights-patch-shader](https://github.com/Raz0r1337/WoW-lights-patch-shader/releases).\n'),
        ]: s = once(s, a_, b_, 'lists de')
    else:
        for a_, b_ in [
            ('No. 4, 10, 11, 23–25,\n    43, 44, 47–52, 76 and 83–87 (red warning).\n',
             'No. 4, 11, 23–25,\n    43, 44, 47–52, 78 and 85–89 (red warning).\n  - 🟠 **risky** – gets blocked on some servers: No. 10 (orange warning).\n'),
            ('you kicked or banned: No. 26, 31, 41, 46, 53, 64, 70 and 73–75 (orange warning).',
             'you kicked or banned: No. 10, 26, 41, 46, 53, 64, 72 and 75–77 (orange warning).'),
            ('possibly buggy: No. 25, 26, 31, 46, 53 and 64 (orange warning).', 'possibly buggy: No. 25, 26, 46, 53 and 64 (orange warning).'),
            ('No. 9, 52,\n    65, 66 and 76.', 'No. 9, 52,\n    65–67 and 78.'),
            ('(No. 9, 52, 65, 66 and 76) also remove', '(No. 9, 52, 65–67 and 78) also remove'),
            ("On top of that comes the Lexara loader\n(No. 30) for Stormhand's HD fonts. The patch itself is safe, but `Lexara.dll`\nmay be detected or blocked on public servers; without `Lexara.dll` in the WoW\nfolder it does nothing. The \"Reforged\" column in the\n",
             "On top of that come the Lexara loader\n(No. 30) for Stormhand's HD fonts and the light patches No. 67 and 68. For the\nLexara loader the patch itself is safe, but `Lexara.dll` may be detected or\nblocked on public servers; without `Lexara.dll` in the WoW folder it does\nnothing. The light patches are tested in game and online and are safe.\nNo. 67 makes `Wow.exe` larger as well and only takes effect with the shaders\nfrom [WoW-lights-patch-shader](https://github.com/Raz0r1337/WoW-lights-patch-shader/releases). The \"Reforged\" column in the\n"),
        ]: s = once(s, a_, b_, 'lists en')
    wr(os.path.join(DST, 'docs', f), s)
print('port ok')

#!/usr/bin/env python3
# Uebertraegt die RCE-v2-Aenderungen aus st0ny-dev in einen anderen Zweig (Skript + Doku), ueber Anker statt Nummern:
# Nr. 10 v2 (orange "riskant"), Nr. 11 ohne Obsoletes, awesome-Lader mit direktem LoadLibraryA, Blocked-Kennzeichnung, Danksagung.
# Aufruf: port_rce_v2.py <dev-Ordner (Quelle)> <Zweig-Ordner (Ziel, wird geaendert)>
import sys, os, re
DEV, DST = sys.argv[1], sys.argv[2]
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
def section(s, start, end):
    i = s.index(start); j = s.index(end, i + len(start)); return s[i:j]
# ---------------- apply_patches.ps1 ----------------
dev = rd(os.path.join(DEV, 'apply_patches.ps1'), True); s = rd(os.path.join(DST, 'apply_patches.ps1'), True)
def entry(src, id_):
    m = re.search(r"^    @\{ Id = '%s';.*?\n    \}\}\n" % id_, src, re.M | re.S); return m.group(0)
for id_ in ('rce', 'wardenoff'):
    s = once(s, entry(s, id_), entry(dev, id_), id_)
# awesome: nur Autor, Kommentar und Bytes (Name und Hinweis des Zweigs bleiben)
a = entry(s, 'awesome'); d = entry(dev, 'awesome')
a2 = once(a, "       Author = 'FrostAtom'\n", "       Author = 'FrostAtom (fixed by St0ny)'\n", 'awesome author')
a2 = once(a2, section(d, '        # Angepasst (St0ny)', '        Patch 0xABD0').replace('        # Angepasst (St0ny)', '') and '        Patch 0xABD0', section(d, '        # Angepasst (St0ny)', '        Patch 0xABD0') + '        Patch 0xABD0', 'awesome comment')
a2 = once(a2, '0x68, 0xE0, 0x5C, 0x4E, 0x00, 0xE8, 0x1C, 0x68, 0x38, 0x00, 0x83, 0xC4, 0x04,', '0x68, 0xE0, 0x5C, 0x4E, 0x00, 0xFF, 0x15, 0x48, 0xF2, 0x9D, 0x00, 0x90, 0x90,', 'awesome bytes')
s = once(s, a, a2, 'awesome')
# Blocked-Kennzeichnung (Texte, Tag, Doku-Kommentar, Hinweisblock)
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
wr(os.path.join(DST, 'apply_patches.ps1'), s, True)
# ---------------- PATCHES ----------------
for f, nr, fixed in (('PATCHES.de.md', 'Nr.', 'Autor: FrostAtom)'), ('PATCHES.en.md', 'No.', 'Author: FrostAtom)')):
    dev = rd(os.path.join(DEV, 'docs', f)); s = rd(os.path.join(DST, 'docs', f))
    s = once(s, section(s, '<a id="patch-rce"></a>', '<a id="patch-wardenoff"></a>'), section(dev, '<a id="patch-rce"></a>', '<a id="patch-wardenoff"></a>'), 'rce section')
    s = once(s, section(s, '<a id="patch-wardenoff"></a>', '<a id="patch-scandll"></a>'), section(dev, '<a id="patch-wardenoff"></a>', '<a id="patch-scandll"></a>'), 'wardenoff section')
    aw = section(s, '<a id="patch-awesome"></a>', '> [!WARNING]'); aw2 = once(aw, fixed, fixed[:-1] + ' (fixed by St0ny))', 'awesome author')
    da = section(dev, '<a id="patch-awesome"></a>', '> [!WARNING]')
    add = da[da.index('\n\n', da.index('normal weiter.\n' if nr == 'Nr.' else 'starts normally.\n')) :]   # Absatz "Anders als im Original ..."
    aw2 = aw2.rstrip('\n') + add
    s = once(s, aw, aw2, 'awesome section')
    wr(os.path.join(DST, 'docs', f), s)
# ---------------- README ----------------
for f, md in (('README.de.md', 'PATCHES.de.md'), ('README.md', 'PATCHES.en.md')):
    dev = rd(os.path.join(DEV, 'docs', f)); s = rd(os.path.join(DST, 'docs', f)); de = f.endswith('de.md')
    if de:
        s = once(s, '(Warden komplett abschalten ersetzt den RCE-Fix) und wenn gewählte Patches eine\n', '(der vollständige LUA-Unlock ersetzt den einfachen) und wenn gewählte Patches eine\n', 'hint')
        s = once(s, '| 🔴 **[unsicher]** | Bestätigte Bann-Gefahr: kann auf vielen Servern zu einem Bann führen. Nur auf Servern nutzen, die das erlauben. | rote Warnung |\n',
                 '| 🔴 **[unsicher]** | Bestätigte Bann-Gefahr: kann auf vielen Servern zu einem Bann führen. Nur auf Servern nutzen, die das erlauben. | rote Warnung |\n| 🟠 **[riskant]** | Wird auf manchen Servern geblockt. Im Zweifel die Regeln deines Servers prüfen. | orange Warnung |\n', 'legend')
        s, n = re.subn(r'(  - 🔴 \*\*unsicher\*\* – Bann-Gefahr[^\n]*Nr\. 4), 10,(\s+)11', r'\1,\g<2>11', s); assert n == 1, 'rote Liste'
        s, n = re.subn(r'(  - 🔴 \*\*unsicher\*\* – .*?\(rote Warnung\)\.\n)', r'\1  - 🟠 **riskant** – wird auf manchen Servern geblockt: Nr. 10 (orange Warnung).\n', s, flags=re.S); assert n == 1, 'riskant-Zeile'
        s, n = re.subn(r'(möglicherweise verbuggt: Nr\. )', r'\g<1>10, ', s); assert n == 1, 'ingame-Liste'
        brady = section(dev, '- Danke an **Brady Russell**', '- Ein großes Dankeschön'); pog = section(dev, '- Danke an **Pogzur**', '- Und natürlich')
        s = once(s, '- Ein großes Dankeschön an **Stormhand**', brady + '- Ein großes Dankeschön an **Stormhand**', 'brady')
        s = once(s, '- Und natürlich danke an alle Autoren', pog + '- Und natürlich danke an alle Autoren', 'pogzur')
    else:
        s = once(s, 'when a companion patch is missing (e.g. the extended slider maximums need the\nCVar unlocks), when one patch makes another unnecessary (disabling Warden\ncompletely replaces the RCE fix) and when selected patches carry a warning –\n',
                 'when a companion patch is missing (e.g. the extended slider maximums need the\nCVar unlocks), when one patch makes another unnecessary (the complete LUA\nunlock replaces the basic one) and when selected patches carry a warning –\n', 'hint')
        s = once(s, '| 🔴 **[unsafe]** | Confirmed ban risk: can lead to a ban on many servers. Only use it on servers that allow it. | red warning |\n',
                 '| 🔴 **[unsafe]** | Confirmed ban risk: can lead to a ban on many servers. Only use it on servers that allow it. | red warning |\n| 🟠 **[risky]** | Gets blocked on some servers. If in doubt, check the rules of your server. | orange warning |\n', 'legend')
        s, n = re.subn(r'(  - 🔴 \*\*unsafe\*\* – ban risk[^\n]*No\. 4), 10,(\s+)11', r'\1,\g<2>11', s); assert n == 1, 'red list'
        s, n = re.subn(r'(  - 🔴 \*\*unsafe\*\* – .*?\(red warning\)\.\n)', r'\1  - 🟠 **risky** – gets blocked on some servers: No. 10 (orange warning).\n', s, flags=re.S); assert n == 1, 'risky line'
        s, n = re.subn(r'(possibly buggy: No\. )', r'\g<1>10, ', s); assert n == 1, 'ingame list'
        brady = section(dev, '- Thanks to **Brady Russell**', '- A big thank you'); pog = section(dev, '- Thanks to **Pogzur**', '- And of course')
        s = once(s, '- A big thank you to **Stormhand**', brady + '- A big thank you to **Stormhand**', 'brady')
        s = once(s, '- And of course thanks to all patch authors', pog + '- And of course thanks to all patch authors', 'pogzur')
    # Tabellenzeilen: Nr. 10 aus dev (gleiche Nummer), awesome nur Autor
    row = [l for l in dev.split('\n') if l.startswith('| [10](%s#patch-rce)' % md)][0]
    s, n = re.subn(r'(?m)^\| \[10\]\(%s#patch-rce\).*$' % re.escape(md), lambda m: row, s); assert n == 1, 'rce row'
    s, n = re.subn(r'(?m)^(\| \[\d+\]\(%s#patch-awesome\).*)\| FrostAtom \|' % re.escape(md), r'\1| FrostAtom (fixed by St0ny) |', s); assert n == 1, 'awesome row'
    wr(os.path.join(DST, 'docs', f), s)
print('port ok')

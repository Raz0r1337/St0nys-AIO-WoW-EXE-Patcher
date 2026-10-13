#!/usr/bin/env python3
# Nr. 28: awesome-Lader ruft LoadLibraryA direkt (call [0x9DF248]) statt ueber die Ladefunktion des Clients.
# Aufruf: edit_awesome.py <Ordner mit apply_patches.ps1 und docs/>
import sys, os
root = sys.argv[1]
def edit_ps1(p, pairs):
    s = open(p, 'rb').read().decode('ascii').replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70], s.count(a)); s = s.replace(a, b)
    s.encode('ascii'); open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
def edit_md(p, pairs):
    s = open(p, encoding='utf-8').read(); assert '\r' not in s
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70], s.count(a)); s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
edit_ps1(os.path.join(root, 'apply_patches.ps1'), [
("""    @{ Id = 'awesome'; Cat = 'dll'; On = $true; Needs = @('laa'); DllRisky = $true
       Author = 'FrostAtom'
""", """    @{ Id = 'awesome'; Cat = 'dll'; On = $true; Needs = @('laa'); DllRisky = $true
       Author = 'FrostAtom (fixed by St0ny)'
"""),
("""        # deaktivieren"). Fehlt die DLL, startet WoW normal weiter.
        Patch 0xABD0""", """        # deaktivieren"). Fehlt die DLL, startet WoW normal weiter.
        # Angepasst (St0ny): Der Lader ruft LoadLibraryA direkt ueber die
        # Importtabelle (call [0x9DF248]) statt ueber eine Ladefunktion des
        # Clients (call 0x86C4E0 / add esp,4) - gleich lang, so laedt er die
        # DLL auch zusammen mit dem RCE-Fix v2 (rce).
        Patch 0xABD0"""),
("0x68, 0xE0, 0x5C, 0x4E, 0x00, 0xE8, 0x1C, 0x68, 0x38, 0x00, 0x83, 0xC4, 0x04,",
 "0x68, 0xE0, 0x5C, 0x4E, 0x00, 0xFF, 0x15, 0x48, 0xF2, 0x9D, 0x00, 0x90, 0x90,"),
])
edit_md(os.path.join(root, 'docs', 'PATCHES.de.md'), [
("*(Nr. 28, Autor: FrostAtom)*", "*(Nr. 28, Autor: FrostAtom (fixed by St0ny))*"),
("""Der Patch schaltet damit nebenbei den Scan.dll-Mechanismus ab (wie Nr. 12).
Fehlt die DLL, startet WoW normal weiter.
""", """Der Patch schaltet damit nebenbei den Scan.dll-Mechanismus ab (wie Nr. 12).
Fehlt die DLL, startet WoW normal weiter.

Anders als im Original von FrostAtom ruft der Lader `LoadLibraryA` direkt auf.
So funktioniert er auch zusammen mit dem RCE-Fix v2 (Nr. 10).
"""),
])
edit_md(os.path.join(root, 'docs', 'PATCHES.en.md'), [
("*(No. 28, Author: FrostAtom)*", "*(No. 28, Author: FrostAtom (fixed by St0ny))*"),
("""(like No. 12). If the DLL is missing, WoW simply starts normally.
""", """(like No. 12). If the DLL is missing, WoW simply starts normally.

Unlike FrostAtom's original, the loader calls `LoadLibraryA` directly. This
way it also works together with the RCE fix v2 (No. 10).
"""),
])
for f, a in (('README.de.md', '| 🟡 **[sicher - DLL riskant]** | FrostAtom | – | ✅ | ✅ |'), ('README.md', '| 🟡 **[safe - DLL risky]** | FrostAtom | – | ✅ | ✅ |')):
    edit_md(os.path.join(root, 'docs', f), [(a, a.replace('| FrostAtom |', '| FrostAtom (fixed by St0ny) |'))])
print('edits ok')

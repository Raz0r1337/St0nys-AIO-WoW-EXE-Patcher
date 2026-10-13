import sys
d=sys.argv[1]
REL='https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/releases/latest'
ISS='https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/issues'
def edit(fn,pairs,crlf=False):
    p=d+'/'+fn; raw=open(p,'rb').read()
    assert (b'\r\n' in raw)==crlf,fn
    t=raw.decode('utf-8')
    if crlf: t=t.replace('\r\n','\n')
    for a,b in pairs:
        assert t.count(a)==1,(fn,a[:70],t.count(a)); t=t.replace(a,b)
    if crlf: t=t.replace('\n','\r\n')
    open(p,'wb').write(t.encode('utf-8')); print(fn,'ok')
edit('docs/README.md',[
("""1. Copy `patcher.bat` and `apply_patches.ps1` into your WoW folder
   (next to `Wow.exe`).
2. Close WoW if it is still running.
3. Double-click `patcher.bat`.
4. Choose the language (first start only), select patches, confirm – done.

To **change or remove** patches just run `patcher.bat` again, see
[Changing or removing patches](#changing-or-removing-patches).""",
"""1. Download the ZIP from the [latest release](%s) and unpack it. It
   contains the folder `St0nys-AIO-WoW-EXE-Patcher`.
2. Copy your original `Wow.exe` from your WoW folder into that folder.
3. Double-click `patcher.bat`.
4. Choose the language (first start only), select patches, confirm.
5. Close WoW and copy the patched `Wow.exe` back into your WoW folder,
   replacing the old one.

To **change or remove** patches just run `patcher.bat` in the patcher folder
again and copy `Wow.exe` back into your WoW folder afterwards, see
[Changing or removing patches](#changing-or-removing-patches).""" % REL),
("""`Wow.exe` is **byte-for-byte the original** again.

How it works:""","""`Wow.exe` is **byte-for-byte the original** again. Afterwards copy `Wow.exe`
back into your WoW folder.

How it works:"""),
])
edit('docs/README.de.md',[
("""1. `patcher.bat` und `apply_patches.ps1` in den WoW-Ordner kopieren
   (dorthin, wo die `Wow.exe` liegt).
2. WoW beenden, falls es noch läuft.
3. `patcher.bat` per Doppelklick starten.
4. Sprache wählen (nur beim ersten Start), Patches auswählen, bestätigen – fertig.

Patches **ändern oder zurücknehmen:** `patcher.bat` einfach erneut starten,
siehe [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen).""",
"""1. Das ZIP vom [neuesten Release](%s) herunterladen und entpacken.
   Darin liegt der Ordner `St0nys-AIO-WoW-EXE-Patcher`.
2. Die originale `Wow.exe` aus dem WoW-Ordner in diesen Ordner kopieren.
3. `patcher.bat` per Doppelklick starten.
4. Sprache wählen (nur beim ersten Start), Patches auswählen, bestätigen.
5. WoW beenden und die gepatchte `Wow.exe` zurück in den WoW-Ordner kopieren,
   dort ersetzt sie die alte.

Patches **ändern oder zurücknehmen:** `patcher.bat` im Patcher-Ordner einfach
erneut starten und die `Wow.exe` danach wieder in den WoW-Ordner kopieren,
siehe [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen).""" % REL),
("""nimmst du alle Patches zurück – danach ist die `Wow.exe` wieder **byte-genau
das Original**.

So funktioniert es:""","""nimmst du alle Patches zurück – danach ist die `Wow.exe` wieder **byte-genau
das Original**. Danach kopierst du die `Wow.exe` wieder in deinen WoW-Ordner.

So funktioniert es:"""),
])
edit('docs/PATCHES.de.md',[("oder `.png`-Datei, absolut oder relativ zum WoW-Ordner. Aus der Datei baut er",
                            "oder `.png`-Datei, absolut oder relativ zum Ordner der `Wow.exe`. Aus der Datei baut er")])
edit('docs/PATCHES.en.md',[("relative to the WoW folder. From that file it builds the four sizes stored in",
                            "relative to the folder of `Wow.exe`. From that file it builds the four sizes stored in")])
edit('apply_patches.ps1',[("PromptDe = 'Icon-Datei (.ico oder .png), Pfad absolut oder relativ zum WoW-Ordner'",
                           "PromptDe = 'Icon-Datei (.ico oder .png), Pfad absolut oder relativ zum Ordner der Wow.exe'"),
                          ("PromptEn = 'Icon file (.ico or .png), path absolute or relative to the WoW folder'",
                           "PromptEn = 'Icon file (.ico or .png), path absolute or relative to the folder of Wow.exe'")],crlf=True)

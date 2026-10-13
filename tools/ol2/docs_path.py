# Doku: Pfad zur Wow.exe (Startmenue P), -Path mit Sicherungen im Patcher-Ordner. Aufruf: docs_path.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)
edit('docs/README.de.md', [
("""siehe [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen).

> [!NOTE]
> Windows warnt""", """siehe [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen).

> [!TIP]
> **Ohne Kopieren:** Statt die `Wow.exe` hin und her zu kopieren, kannst du im
> [Startmenü](#startmenü) mit `P` den Pfad zur `Wow.exe` in deinem WoW-Ordner
> angeben. Der Patcher merkt sich den Pfad und patcht die Exe dann direkt dort;
> die Sicherungen bleiben im Patcher-Ordner. WoW muss dabei beendet sein.

> [!NOTE]
> Windows warnt"""),
("""| `M`     | Patch-Menü öffnen und das Startmenü künftig überspringen (wird gemerkt) |
| `Q`     | abbrechen, nichts ändern |
""", """| `M`     | Patch-Menü öffnen und das Startmenü künftig überspringen (wird gemerkt) |
| `P`     | Pfad zur `Wow.exe` festlegen (wird gemerkt, siehe unten) |
| `Q`     | abbrechen, nichts ändern |
"""),
("""**Startmenü abschalten:** Mit `M` geht es ab dem nächsten Start direkt ins""",
 """**Pfad zur Wow.exe:** Mit `P` gibst du an, welche `Wow.exe` der Patcher
nimmt – die Exe selbst oder den Ordner, in dem sie liegt, z. B. deinen
WoW-Ordner. Du kannst die Datei oder den Ordner auch einfach ins Fenster
ziehen. ENTER ohne Eingabe stellt wieder die `Wow.exe` im Patcher-Ordner ein.
Der Pfad wird in `patcher_selection.ini` gemerkt (`wowpath=`), danach prüft der
Patcher gleich die neue Exe und zeigt das Startmenü neu; beim Start steht der
Pfad grau über der Prüfung. `Wow.exe.ORI`, `Wow.exe.BAK` und
`patcher_state.ini` bleiben im Patcher-Ordner, `2` und `3` stellen direkt am
Pfad wieder her.

**Startmenü abschalten:** Mit `M` geht es ab dem nächsten Start direkt ins"""),
("""**Wenn die Wow.exe fehlt oder nicht verwendbar ist:** Liegt im Patcher-Ordner
keine `Wow.exe` mehr – etwa weil du die gepatchte Exe in den WoW-Ordner
verschoben statt kopiert hast – oder ist sie weder original noch mit diesem""",
 """**Wenn die Wow.exe fehlt oder nicht verwendbar ist:** Liegt im Patcher-Ordner
(bzw. am gemerkten Pfad) keine `Wow.exe` mehr – etwa weil du die gepatchte Exe
in den WoW-Ordner verschoben statt kopiert hast – oder ist sie weder original noch mit diesem"""),
("""`Wow.exe` wird dabei ersetzt. Gibt es keine Sicherungen, bricht der Patcher ab.""",
 """`Wow.exe` wird dabei ersetzt. Gibt es keine Sicherungen, bietet das Startmenü
nur `P` und `Q` an."""),
("""| `-Path <Datei>`        | eine andere `Wow.exe` als die im Skriptordner patchen                        |""",
 """| `-Path <Datei>`        | eine andere `Wow.exe` als die im Skriptordner patchen – nur für diesen Lauf, geht dem gemerkten Pfad vor; die Sicherungen bleiben im Patcher-Ordner |"""),
("""sowie die Einstellung für das Startmenü |""", """sowie die Einstellung für das Startmenü und den Pfad zur `Wow.exe` |"""),
("""| `Wow.exe.ORI`       | Sicherung der originalen `Wow.exe`, angelegt beim ersten Start |""",
 """| `Wow.exe.ORI`       | Sicherung der originalen `Wow.exe`, angelegt beim ersten Start – immer im Patcher-Ordner, auch mit Pfad |"""),
])
edit('docs/README.md', [
("""[Changing or removing patches](#changing-or-removing-patches).

> [!NOTE]
> Windows will""", """[Changing or removing patches](#changing-or-removing-patches).

> [!TIP]
> **Without copying:** instead of copying `Wow.exe` back and forth, you can set
> the path to the `Wow.exe` in your WoW folder with `P` in the
> [start menu](#start-menu). The patcher remembers the path and then patches the
> exe right there; the backups stay in the patcher folder. WoW has to be closed.

> [!NOTE]
> Windows will"""),
("""| `M`   | open the patch menu and skip the start menu from now on (remembered) |
| `Q`   | cancel, change nothing |
""", """| `M`   | open the patch menu and skip the start menu from now on (remembered) |
| `P`   | set the path to `Wow.exe` (remembered, see below) |
| `Q`   | cancel, change nothing |
"""),
("""**Turning the start menu off:** with `M` the patch menu opens directly from""",
 """**Path to Wow.exe:** with `P` you set which `Wow.exe` the patcher uses – the
exe itself or the folder it is in, e.g. your WoW folder. You can also just drag
the file or folder into the window. ENTER without input switches back to the
`Wow.exe` in the patcher folder. The path is remembered in
`patcher_selection.ini` (`wowpath=`); the patcher then checks the new exe right
away and shows the start menu again, and at startup the path is shown in grey
above the check. `Wow.exe.ORI`, `Wow.exe.BAK` and `patcher_state.ini` stay in
the patcher folder, `2` and `3` restore directly at the path.

**Turning the start menu off:** with `M` the patch menu opens directly from"""),
("""**If Wow.exe is missing or cannot be used:** if there is no `Wow.exe` in the
patcher folder any more – e.g. because you moved the patched exe into your""",
 """**If Wow.exe is missing or cannot be used:** if there is no `Wow.exe` in the
patcher folder (or at the remembered path) any more – e.g. because you moved the patched exe into your"""),
("""`Wow.exe` again; a `Wow.exe` that cannot be used is replaced. Without backups
the patcher aborts.""", """`Wow.exe` again; a `Wow.exe` that cannot be used is replaced. Without backups
the start menu only offers `P` and `Q`."""),
("""| `-Path <file>`         | patch a `Wow.exe` other than the one next to the script                    |""",
 """| `-Path <file>`         | patch a `Wow.exe` other than the one next to the script – for this run only, takes precedence over the remembered path; the backups stay in the patcher folder |"""),
("""the entered values and the start menu setting |""", """the entered values, the start menu setting and the path to `Wow.exe` |"""),
("""| `Wow.exe.ORI`       | Backup of the original `Wow.exe`, created on the first start |""",
 """| `Wow.exe.ORI`       | Backup of the original `Wow.exe`, created on the first start – always in the patcher folder, also with a path |"""),
])
print('ok')

# Doku zum Startmenue (README.de.md / README.md). Aufruf: docs_sm.py <worktree>
import sys, re
wt = sys.argv[1]
BAT = sys.argv[2] if len(sys.argv) > 2 else 'patcher-win.bat'

def edit(fn, pairs, cut):
    p = wt + '/docs/' + fn
    raw = open(p, 'rb').read(); assert b'\r' not in raw
    s = raw.decode('utf-8')
    for a, b in pairs:
        a = a.replace('patcher-win.bat', BAT); b = b.replace('patcher-win.bat', BAT)
        n = s.count(a); assert n == 1, (fn, a[:90], n)
        s = s.replace(a, b)
    # alten Abschnitt entfernen (bis zur naechsten ##-Ueberschrift)
    a = s.index(cut); z = s.index('\n## ', a) + 1
    s = s[:a] + s[z:]
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print(fn, 'ok')

DE_SECTION = '''## Startmenü

Nach der Prüfung der `Wow.exe` zeigt der Patcher bei jedem Start ein kleines
Menü. Darüber stehen die Sicherungen, die im Ordner liegen.

| Eingabe | Wirkung |
|---------|---------|
| `1`     | Patch-Menü öffnen (siehe [Patch-Auswahl](#patch-auswahl)) |
| `2`     | vorherige `Wow.exe` wiederherstellen: Der Patcher kopiert `Wow.exe.BAK` zurück, also den Stand vor dem letzten Patchen |
| `3`     | Original wiederherstellen: Der Patcher kopiert `Wow.exe.ORI` zurück |
| `M`     | Patch-Menü öffnen und das Startmenü künftig überspringen (wird gemerkt) |
| `Q`     | abbrechen, nichts ändern |

Ersetzt `2` oder `3` eine vorhandene `Wow.exe`, fragt der Patcher vorher nach
(J/N). Die Sicherungen bleiben in jedem Fall erhalten. Angeboten wird nur, was
sich verwenden lässt: Das Original muss laut SHA256 wirklich das Original sein,
das Backup original oder mit diesem Patcher gepatcht.

**Startmenü abschalten:** Mit `M` geht es ab dem nächsten Start direkt ins
Patch-Menü. Wie die Sprache wird das in `patcher_selection.ini` gemerkt
(`startmenu=off`), beim Start erinnert eine graue Zeile daran. Im Patch-Menü
schaltet `M` das Startmenü wieder ein und auch wieder aus.

**Wenn die Wow.exe fehlt oder nicht verwendbar ist:** Liegt im Patcher-Ordner
keine `Wow.exe` mehr – etwa weil du die gepatchte Exe in den WoW-Ordner
verschoben statt kopiert hast – oder ist sie weder original noch mit diesem
Patcher gepatcht, erscheint das Startmenü auch dann, wenn es abgeschaltet ist.
`1` baut dann eine neue `Wow.exe` aus dem Original: Das Patch-Menü startet mit
den Patches und Werten, die zuletzt eingespielt waren. Du kannst sie
übernehmen, ändern oder mit `R`, `B` oder `S` ein Preset laden. Ohne Änderung
entsteht genau die zuletzt gepatchte `Wow.exe` neu; eine nicht verwendbare
`Wow.exe` wird dabei ersetzt. Gibt es keine Sicherungen, bricht der Patcher ab.

Mit `-Select` (bei verwendbarer `Wow.exe`) und mit `-Unattended` gibt es kein
Startmenü. Fehlt die `Wow.exe` bei `-Unattended` oder ist sie nicht
verwendbar, bricht der Patcher ab und weist auf die Sicherungen hin.

'''

EN_SECTION = '''## Start menu

After checking `Wow.exe` the patcher shows a small menu on every start. Above
it, it lists the backups in the folder.

| Input | Effect |
|-------|--------|
| `1`   | open the patch menu (see [Patch selection](#patch-selection)) |
| `2`   | restore the previous `Wow.exe`: the patcher copies `Wow.exe.BAK` back, i.e. the state before the last patching |
| `3`   | restore the original: the patcher copies `Wow.exe.ORI` back |
| `M`   | open the patch menu and skip the start menu from now on (remembered) |
| `Q`   | cancel, change nothing |

If `2` or `3` replaces an existing `Wow.exe`, the patcher asks first (Y/N).
The backups are kept in every case. Only usable options are offered: the
original must really be the original according to SHA256, the backup original
or patched with this patcher.

**Turning the start menu off:** with `M` the patch menu opens directly from
the next start on. Like the language, this is remembered in
`patcher_selection.ini` (`startmenu=off`), and a grey line points it out at
startup. In the patch menu `M` turns the start menu back on and off again.

**If Wow.exe is missing or cannot be used:** if there is no `Wow.exe` in the
patcher folder any more – e.g. because you moved the patched exe into your
WoW folder instead of copying it – or if it is neither original nor patched
with this patcher, the start menu appears even when it is turned off. `1` then
builds a new `Wow.exe` from the original: the patch menu starts with the
patches and values applied last time. You can keep them, change them or load
a preset with `R`, `B` or `S`. Without changes you get exactly the last patched
`Wow.exe` again; a `Wow.exe` that cannot be used is replaced. Without backups
the patcher aborts.

With `-Select` (if `Wow.exe` can be used) and with `-Unattended` there is no
start menu. If `Wow.exe` is missing or cannot be used with `-Unattended`, the
patcher aborts and points to the backups.

'''

edit('README.de.md', [
    ('- [Ablauf](#ablauf)\n', '- [Ablauf](#ablauf)\n- [Startmenü](#startmenü)\n'),
    ('''4. Prüfung, ob eine `Wow.exe` im Ordner vorhanden ist. Fehlt sie, liegen aber
   noch Sicherungen im Ordner, bietet der Patcher an, sie neu zu bauen oder
   wiederherzustellen (siehe [Wenn die Wow.exe fehlt](#wenn-die-wowexe-fehlt)).
5. Prüfung der `Wow.exe`: Beim ersten Start muss sie original und unmodifiziert
   sein (SHA256). Danach erkennt der Patcher eine von ihm gepatchte `Wow.exe` am
   Wasserzeichen und ermittelt, welche Patches darin stecken. Alles andere führt
   zum Abbruch.
''', '''4. Prüfung der `Wow.exe`: Beim ersten Start muss sie original und unmodifiziert
   sein (SHA256). Danach erkennt der Patcher eine von ihm gepatchte `Wow.exe` am
   Wasserzeichen und ermittelt, welche Patches darin stecken.
5. **Startmenü:** Patch-Menü öffnen oder die `Wow.exe` aus einer Sicherung
   wiederherstellen (siehe [Startmenü](#startmenü)). Fehlt die `Wow.exe` oder
   ist sie nicht verwendbar, kann es sie auch neu aus dem Original bauen; ohne
   Sicherungen bricht der Patcher dann ab.
'''),
    ('\n## Patch-Auswahl\n', '\n' + DE_SECTION + '## Patch-Auswahl\n'),
    ('''| `L`                | Sprache umschalten (Deutsch ↔ English)      |
''', '''| `L`                | Sprache umschalten (Deutsch ↔ English)      |
| `M`                | Startmenü ein- bzw. ausschalten (gemerkt, siehe [Startmenü](#startmenü)) |
'''),
    ('- Auch die Sprache wird dort gemerkt (`language=de` bzw. `en`).\n',
     '- Auch die Sprache wird dort gemerkt (`language=de` bzw. `en`), ebenso, ob\n  das Startmenü erscheint (`startmenu=on` bzw. `off`).\n'),
    ('''  dann gilt wieder das Preset „Reforged“ (beim Löschen der Datei werden
  auch Sprache und gemerkte Werte wieder abgefragt).''', '''  dann gilt wieder das Preset „Reforged“ (beim Löschen der Datei werden
  auch Sprache und gemerkte Werte wieder abgefragt, und das Startmenü ist
  wieder an).'''),
    ('''Eingespielte Patches sind nicht endgültig. Starte `patcher-win.bat` einfach erneut:
Im Menü sind dann genau die Patches angehakt''', '''Eingespielte Patches sind nicht endgültig. Starte `patcher-win.bat` einfach erneut:
Im Patch-Menü (Startmenü `1`) sind dann genau die Patches angehakt'''),
    ('''  erkennt er am Wasserzeichen. Fehlt es (und ist die Datei nicht original),
  bricht er ab – etwa bei einer Exe, die mit einem anderen Tool gepatcht wurde.''',
     '''  erkennt er am Wasserzeichen. Fehlt es (und ist die Datei nicht original), ist
  die `Wow.exe` nicht verwendbar – etwa bei einer Exe, die mit einem anderen
  Tool gepatcht wurde. Dann bietet das [Startmenü](#startmenü) an, sie aus einer
  Sicherung wiederherzustellen oder neu aus dem Original zu bauen; ohne
  Sicherungen bricht der Patcher ab.'''),
    ('''  neue Auswahl ein. Klappt das nicht exakt – etwa weil die Exe nach dem
  Patchen noch anderweitig verändert wurde –, bricht er ab.''', '''  neue Auswahl ein. Klappt das nicht exakt – etwa weil die Exe nach dem
  Patchen noch anderweitig verändert wurde –, ist sie nicht verwendbar (siehe
  oben).'''),
    ('''| `-Select <Auswahl>`    | Auswahlmenü überspringen: ''', '''| `-Select <Auswahl>`    | Auswahlmenü überspringen, bei verwendbarer `Wow.exe` auch das Startmenü: '''),
    ('''| `-Unattended`          | keine Rückfragen und keine Pausen. ''', '''| `-Unattended`          | keine Rückfragen, keine Pausen und kein Startmenü. '''),
    ('''| `patcher_selection.ini` | Wird beim ersten Start angelegt (gemerkte Sprache) und speichert die übernommene Auswahl samt eingegebenen Werten |''',
     '''| `patcher_selection.ini` | Wird beim ersten Start angelegt (gemerkte Sprache) und speichert die übernommene Auswahl samt eingegebenen Werten sowie die Einstellung für das Startmenü |'''),
    ('''- **Original wiederherstellen:** Patcher starten, `N` und ENTER drücken – mit
  oder ohne `patcher_state.ini`. Alternativ die gepatchte `Wow.exe` löschen und
  den Patcher starten: Er bietet dann an, das Original wiederherzustellen
  (siehe [Wenn die Wow.exe fehlt](#wenn-die-wowexe-fehlt)). `Wow.exe.BAK` ist
  dagegen die `Wow.exe` von vor dem letzten Lauf.''', '''- **Original wiederherstellen:** Patcher starten und im
  [Startmenü](#startmenü) `3` wählen – der Patcher kopiert `Wow.exe.ORI` zurück.
  Oder im Patch-Menü `N` und ENTER drücken – mit oder ohne
  `patcher_state.ini`. `Wow.exe.BAK` ist dagegen die `Wow.exe` von vor dem
  letzten Lauf (im Startmenü `2`).'''),
], '### Wenn die Wow.exe fehlt\n')

edit('README.md', [
    ('- [Workflow](#workflow)\n', '- [Workflow](#workflow)\n- [Start menu](#start-menu)\n'),
    ('''4. Check that a `Wow.exe` exists in the folder. If it is missing but backups
   are still there, the patcher offers to rebuild or restore it (see
   [If Wow.exe is missing](#if-wowexe-is-missing)).
5. Checking `Wow.exe`: on the first start it must be original and unmodified
   (SHA256). After that the patcher recognizes a `Wow.exe` it patched itself
   by the watermark and determines which patches are in it. Anything else
   aborts.
''', '''4. Checking `Wow.exe`: on the first start it must be original and unmodified
   (SHA256). After that the patcher recognizes a `Wow.exe` it patched itself
   by the watermark and determines which patches are in it.
5. **Start menu:** open the patch menu or restore `Wow.exe` from a backup (see
   [Start menu](#start-menu)). If `Wow.exe` is missing or cannot be used, it
   can also build it anew from the original; without backups the patcher
   aborts.
'''),
    ('\n## Patch selection\n', '\n' + EN_SECTION + '## Patch selection\n'),
    ('''| `L`                | switch language (Deutsch ↔ English)        |
''', '''| `L`                | switch language (Deutsch ↔ English)        |
| `M`                | turn the start menu on or off (remembered, see [Start menu](#start-menu)) |
'''),
    ('- The language is remembered there as well (`language=de` or `en`).\n',
     '- The language is remembered there as well (`language=de` or `en`), and so\n  is whether the start menu appears (`startmenu=on` or `off`).\n'),
    ('''  the preset "Reforged" applies again (deleting the file also forgets the
  language and the remembered values, they are asked for again).''', '''  the preset "Reforged" applies again (deleting the file also forgets the
  language and the remembered values, they are asked for again, and the start
  menu is on again).'''),
    ('''Applied patches are not final. Just run `patcher-win.bat` again: the menu then has
exactly the patches checked''', '''Applied patches are not final. Just run `patcher-win.bat` again: the patch menu
(start menu `1`) then has exactly the patches checked'''),
    ('''  by the watermark. If it is missing (and the file is not original), it aborts
  – e.g. for an exe patched with another tool.''', '''  by the watermark. If it is missing (and the file is not original), the
  `Wow.exe` cannot be used – e.g. for an exe patched with another tool. The
  [start menu](#start-menu) then offers to restore it from a backup or to build
  it anew from the original; without backups the patcher aborts.'''),
    ('''  top. If that does not work exactly – e.g. because the exe was changed in
  some other way after patching – it aborts.''', '''  top. If that does not work exactly – e.g. because the exe was changed in
  some other way after patching – it cannot be used (see above).'''),
    ('''| `-Select <selection>`  | skip the selection menu: ''', '''| `-Select <selection>`  | skip the selection menu and, if `Wow.exe` can be used, the start menu: '''),
    ('''| `-Unattended`          | no prompts and no pauses. ''', '''| `-Unattended`          | no prompts, no pauses and no start menu. '''),
    ('''| `patcher_selection.ini` | Created on the first start (remembered language), stores the accepted selection and the entered values |''',
     '''| `patcher_selection.ini` | Created on the first start (remembered language), stores the accepted selection, the entered values and the start menu setting |'''),
    ('''- **Restoring the original:** run the patcher, press `N` and ENTER – with or
  without `patcher_state.ini`. Alternatively delete the patched `Wow.exe` and
  start the patcher: it then offers to restore the original (see
  [If Wow.exe is missing](#if-wowexe-is-missing)). `Wow.exe.BAK`, on the other
  hand, is the `Wow.exe` from before the last run.''', '''- **Restoring the original:** run the patcher and choose `3` in the
  [start menu](#start-menu) – the patcher copies `Wow.exe.ORI` back. Or press
  `N` and ENTER in the patch menu – with or without `patcher_state.ini`.
  `Wow.exe.BAK`, on the other hand, is the `Wow.exe` from before the last run
  (start menu `2`).'''),
], '### If Wow.exe is missing\n')

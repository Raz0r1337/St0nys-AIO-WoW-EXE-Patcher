import sys
def edit(p, pairs):
    s=open(p,encoding='utf-8',newline='').read()
    crlf='\r\n' in s
    s=s.replace('\r\n','\n')
    for old,new in pairs:
        c=s.count(old)
        if c!=1: sys.exit(f"{p}: count {c} for {old[:70]!r}")
        s=s.replace(old,new)
    if crlf: s=s.replace('\n','\r\n')
    open(p,'w',encoding='utf-8',newline='').write(s)

edit('README.md', [
("""Beim Start wählst du die **Sprache** (Deutsch / English) und danach in einem
Menü, **welche Patches** eingespielt werden sollen.
""", """Beim Start wählst du die **Sprache** (Deutsch / English) und danach in einem
Menü, **welche Patches** eingespielt werden sollen. Eingespielte Patches lassen
sich später jederzeit wieder **abwählen oder ergänzen** – bis zurück zur
originalen `Wow.exe`.
"""),
("""- [Patch-Auswahl](#patch-auswahl)
""", """- [Patch-Auswahl](#patch-auswahl)
- [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen)
"""),
("""- Eine **originale, unmodifizierte** `Wow.exe` 3.3.5a, Build 12340 mit
  SHA256 `AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8`
""", """- Eine **originale, unmodifizierte** `Wow.exe` 3.3.5a, Build 12340 mit
  SHA256 `AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8`
  (beim ersten Start; danach die zuletzt vom Patcher erzeugte `Wow.exe`)
"""),
("""Zum **Wiederherstellen** einfach `Wow.exe` löschen und `Wow.exe.BAK` in
`Wow.exe` umbenennen.
""", """Patches **ändern oder zurücknehmen:** `patcher.bat` einfach erneut starten,
siehe [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen).
"""),
("""5. SHA256-Integritätsprüfung, ob die `Wow.exe` original/unmodifiziert ist.
6. **Patch-Auswahl** im Menü (siehe unten). Die Auswahl vom letzten Mal ist
   bereits vorausgewählt.
7. Zusammenfassung der gewählten Patches, Hinweise auf fehlende oder
   überflüssige Ergänzungs-Patches und Sicherheitsabfrage (J/N).
8. Automatisches Backup als `Wow.exe.BAK`.
9. Alle gewählten Patches werden im Speicher eingespielt (mit Fortschrittsanzeige)
   und die `Wow.exe` danach **einmal** zurückgeschrieben. Tritt dabei ein Fehler
   auf, bleibt die `Wow.exe` unverändert.
10. Abschlussmeldung mit der Anzahl der eingespielten Patches.
""", """5. SHA256-Integritätsprüfung: Beim ersten Start muss die `Wow.exe` original und
   unmodifiziert sein, danach exakt die Datei, die der Patcher zuletzt erzeugt
   hat. Alles andere führt zum Abbruch.
6. **Patch-Auswahl** im Menü (siehe unten). Vorausgewählt ist die Auswahl vom
   letzten Mal bzw. bei einer gepatchten `Wow.exe` die Patches, die gerade
   darin stecken.
7. Zusammenfassung der gewählten Patches (bei einer gepatchten `Wow.exe`: was
   neu dazukommt, was zurückgenommen wird), Hinweise auf fehlende oder
   überflüssige Ergänzungs-Patches und Sicherheitsabfrage (J/N).
8. Automatisches Backup als `Wow.exe.BAK` – nur vom Original, also beim ersten
   Patchen.
9. Alle gewählten Patches werden im Speicher eingespielt (mit Fortschrittsanzeige)
   und die `Wow.exe` danach **einmal** zurückgeschrieben. Tritt dabei ein Fehler
   auf, bleibt die `Wow.exe` unverändert.
10. Der Patcher merkt sich den Hash der neuen `Wow.exe` samt Original-Bytes in
    `patcher_state.ini` und zeigt eine Abschlussmeldung.
"""),
("""| `B`                | Preset „Billy's_Wow.exe“ laden (= Standard) |
| `Q`                | abbrechen, die `Wow.exe` bleibt unverändert |
""", """| `B`                | Preset „Billy's_Wow.exe“ laden (= Standard) |
| `O`                | Original wiederherstellen, alle Patches zurücknehmen (nur bei gepatchter `Wow.exe`) |
| `Q`                | abbrechen, die `Wow.exe` bleibt unverändert |
"""),
("""Das Preset „Billy's_Wow.exe“ ist das Patch-Set von Billy Hoyle und zugleich die
Standard-Auswahl. Es ist in `apply_patches.ps1` festgelegt: Jeder Patch hat dort
einen Eintrag `On = $true` (im Preset) bzw. `On = $false` (nicht im Preset).
""", """Das Preset „Billy's_Wow.exe“ ist das Patch-Set von Billy Hoyle und zugleich die
Standard-Auswahl. Es ist in `apply_patches.ps1` festgelegt: Jeder Patch hat dort
einen Eintrag `On = $true` (im Preset) bzw. `On = $false` (nicht im Preset).

## Patches ändern oder zurücknehmen

Eingespielte Patches sind nicht endgültig. Starte `patcher.bat` einfach erneut:
Im Menü sind dann genau die Patches angehakt, die gerade in der `Wow.exe`
stecken. Neu angehakte Patches sind mit **(neu)** markiert, abgewählte mit
**(wird zurückgenommen)**. So kannst du beliebig Patches dazunehmen, abwählen
oder bei den Client-Info-Patches die Werte ändern. Mit `O` (oder allen Patches
abgewählt und ENTER) nimmst du alle Patches zurück – danach ist die `Wow.exe`
wieder **byte-genau das Original**.

So funktioniert es:

- **Erster Start:** Die `Wow.exe` muss original sein (SHA256-Prüfung), sonst
  bricht der Patcher ab. Beim Patchen wird `Wow.exe.BAK` angelegt.
- **Nach dem Patchen** merkt sich der Patcher in `patcher_state.ini` den
  SHA256 der erzeugten `Wow.exe`, die eingespielten Patches mit ihren Werten
  und die Original-Bytes an allen Stellen, die die Patches verändert haben.
- **Jeder weitere Start:** Die `Wow.exe` muss exakt die zuletzt erzeugte Datei
  sein (gleicher Hash), sonst bricht der Patcher ab – etwa wenn sie inzwischen
  von einem anderen Tool verändert wurde. Passt der Hash, baut der Patcher
  daraus im Speicher das Original wieder auf, prüft es noch einmal per SHA256
  gegen das Original und spielt darauf die neue Auswahl ein.
- Vor dem Schreiben prüft der Patcher außerdem, dass sich das neue Ergebnis
  wieder sauber zum Original zurücknehmen lässt.
- Ein vorhandenes `Wow.exe.BAK` wird bei weiteren Läufen nicht angefasst und
  bleibt das Original.

> [!WARNING]
> `patcher_state.ini` nicht löschen oder von Hand ändern, solange die `Wow.exe`
> gepatcht ist – ohne diese Datei lassen sich die Patches nicht mehr
> zurücknehmen. Dann hilft nur noch das Backup: `Wow.exe` löschen und
> `Wow.exe.BAK` in `Wow.exe` umbenennen. Liegt ein originales `Wow.exe.BAK`
> im Ordner, weist der Patcher bei einem Abbruch selbst darauf hin.
"""),
("""| `-Select <Auswahl>`    | Auswahlmenü überspringen: `saved` (gespeicherte Auswahl), `billy` (Preset „Billy's_Wow.exe“, auch `default`), `all` oder Nummern/Bereiche wie `"1,3,5-8"`. Mit `-Select` wird die gespeicherte Auswahl nicht verändert. |""",
"""| `-Select <Auswahl>`    | Auswahlmenü überspringen: `saved` (gespeicherte Auswahl), `billy` (Preset „Billy's_Wow.exe“, auch `default`), `all`, `none` (alle Patches zurücknehmen, Original wiederherstellen) oder Nummern/Bereiche wie `"1,3,5-8"`. Die Auswahl ersetzt die Patches in der `Wow.exe` komplett. Mit `-Select` wird die gespeicherte Auswahl nicht verändert. |"""),
("""Exit-Codes: `0` = erfolgreich, `1` = Fehler, `2` = abgebrochen (vom Benutzer oder weil keine Eingabe mehr möglich ist).""",
"""Exit-Codes: `0` = erfolgreich (oder nichts zu tun), `1` = Fehler, `2` = abgebrochen (vom Benutzer oder weil keine Eingabe mehr möglich ist)."""),
("""| `patcher_selection.ini` | Wird angelegt, sobald du eine Auswahl übernimmst, und speichert sie |
""", """| `patcher_selection.ini` | Wird angelegt, sobald du eine Auswahl übernimmst, und speichert sie |
| `patcher_state.ini` | Wird beim Patchen angelegt: Hash der gepatchten `Wow.exe`, eingespielte Patches und Original-Bytes zum Zurücknehmen |
"""),
("""Die Werte merkt sich der Patcher in `patcher_selection.ini` (`value.<Id>=…`);
mit `-Unattended` werden die gemerkten Werte bzw. die Originalwerte genommen.
""", """Die Werte merkt sich der Patcher in `patcher_selection.ini` (`value.<Id>=…`);
mit `-Unattended` werden die gemerkten Werte bzw. die Originalwerte genommen.
Steckt ein Patch schon in der `Wow.exe`, ist sein aktueller Wert der Vorschlag.
"""),
("""Als Vorschlag steht immer das **heutige Datum** in den Klammern (mit `FR`, wenn
du das zuletzt gewählt hast); mit `-Unattended` gilt der gemerkte Wert.
""", """Als Vorschlag steht das **heutige Datum** in den Klammern (mit `FR`, wenn du das
zuletzt gewählt hast); mit `-Unattended` gilt der gemerkte Wert. Ist der Patch
schon eingespielt, steht dort das aktuelle Datum der `Wow.exe`.
"""),
("""- Vor dem Patchen wird die `Wow.exe` per SHA256-Hash geprüft. Nur eine
  originale, unmodifizierte `Wow.exe` wird akzeptiert – eine bereits gepatchte
  Datei wird abgelehnt.
- Das Backup `Wow.exe.BAK` wird erst erstellt, wenn die Integritätsprüfung
  bestanden und die Auswahl bestätigt ist. Ein vorhandenes Backup wird dabei
  überschrieben (es ist ja nachweislich wieder das Original).
- Falls keine `Wow.exe` im Ordner liegt, bricht der Patcher ab.
- Zum Wiederherstellen die gepatchte `Wow.exe` löschen und `Wow.exe.BAK` in
  `Wow.exe` umbenennen.
- Um eine andere Auswahl einzuspielen, zuerst das Original wiederherstellen und
  den Patcher erneut starten.
""", """- Vor dem Patchen wird die `Wow.exe` per SHA256-Hash geprüft. Akzeptiert wird
  nur die originale, unmodifizierte `Wow.exe` oder die Datei, die der Patcher
  zuletzt selbst erzeugt hat. Eine mit anderen Tools oder älteren
  Patcher-Versionen gepatchte Datei wird abgelehnt.
- Das Backup `Wow.exe.BAK` wird nur vom Original erstellt, also beim ersten
  Patchen, und erst wenn die Auswahl bestätigt ist. Ein vorhandenes Backup wird
  dabei überschrieben (es ist ja nachweislich wieder das Original).
- Falls keine `Wow.exe` im Ordner liegt, bricht der Patcher ab.
- Zum Wiederherstellen des Originals den Patcher starten und `O` drücken. Ohne
  `patcher_state.ini` geht es nur über das Backup: gepatchte `Wow.exe` löschen
  und `Wow.exe.BAK` in `Wow.exe` umbenennen.
"""),
])

edit('README.en.md', [
("""On start you choose the **language** (Deutsch / English) and then pick
**which patches** to apply from a menu.
""", """On start you choose the **language** (Deutsch / English) and then pick
**which patches** to apply from a menu. Applied patches can be **deselected or
extended** at any time later – all the way back to the original `Wow.exe`.
"""),
("""- [Patch selection](#patch-selection)
""", """- [Patch selection](#patch-selection)
- [Changing or removing patches](#changing-or-removing-patches)
"""),
("""- An **original, unmodified** `Wow.exe` 3.3.5a, build 12340 with
  SHA256 `AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8`
""", """- An **original, unmodified** `Wow.exe` 3.3.5a, build 12340 with
  SHA256 `AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8`
  (on the first start; after that the `Wow.exe` last produced by the patcher)
"""),
("""To **restore** the original, delete `Wow.exe` and rename `Wow.exe.BAK` to
`Wow.exe`.
""", """To **change or remove** patches just run `patcher.bat` again, see
[Changing or removing patches](#changing-or-removing-patches).
"""),
("""5. SHA256 integrity check that the `Wow.exe` is original/unmodified.
6. **Patch selection** menu (see below). Your selection from last time is
   already preselected.
7. Summary of the selected patches, notes about missing or redundant companion
   patches and a confirmation prompt (Y/N).
8. Automatic backup as `Wow.exe.BAK`.
9. All selected patches are applied in memory (with progress output) and
   `Wow.exe` is written back **once**. If anything fails, `Wow.exe` stays
   untouched.
10. Final message with the number of applied patches.
""", """5. SHA256 integrity check: on the first start `Wow.exe` must be original and
   unmodified, after that exactly the file the patcher produced last time.
   Anything else aborts.
6. **Patch selection** menu (see below). Your selection from last time is
   preselected, or for a patched `Wow.exe` the patches currently in it.
7. Summary of the selected patches (for a patched `Wow.exe`: what is added and
   what is removed), notes about missing or redundant companion patches and a
   confirmation prompt (Y/N).
8. Automatic backup as `Wow.exe.BAK` – of the original only, i.e. on the first
   patch run.
9. All selected patches are applied in memory (with progress output) and
   `Wow.exe` is written back **once**. If anything fails, `Wow.exe` stays
   untouched.
10. The patcher remembers the hash of the new `Wow.exe` together with the
    original bytes in `patcher_state.ini` and shows a final message.
"""),
("""| `B`                | load preset "Billy's_Wow.exe" (= default)  |
| `Q`                | quit, `Wow.exe` stays unmodified           |
""", """| `B`                | load preset "Billy's_Wow.exe" (= default)  |
| `O`                | restore original, remove all patches (patched `Wow.exe` only) |
| `Q`                | quit, `Wow.exe` stays unmodified           |
"""),
("""The preset "Billy's_Wow.exe" is Billy Hoyle's patch set and also the default
selection. It is defined in `apply_patches.ps1`: every patch has an entry
`On = $true` (in the preset) or `On = $false` (not in the preset).
""", """The preset "Billy's_Wow.exe" is Billy Hoyle's patch set and also the default
selection. It is defined in `apply_patches.ps1`: every patch has an entry
`On = $true` (in the preset) or `On = $false` (not in the preset).

## Changing or removing patches

Applied patches are not final. Just run `patcher.bat` again: the menu then has
exactly the patches checked that are currently in `Wow.exe`. Newly checked
patches are marked **(new)**, deselected ones **(will be removed)**. This way
you can add patches, deselect them or change the values of the client info
patches as you like. `O` (or all patches deselected and ENTER) removes every
patch – afterwards `Wow.exe` is **byte-for-byte the original** again.

How it works:

- **First start:** `Wow.exe` must be original (SHA256 check), otherwise the
  patcher aborts. Patching creates `Wow.exe.BAK`.
- **After patching** the patcher stores in `patcher_state.ini` the SHA256 of
  the produced `Wow.exe`, the applied patches with their values and the
  original bytes at every location the patches changed.
- **Every later start:** `Wow.exe` must be exactly the file produced last time
  (same hash), otherwise the patcher aborts – e.g. when another tool has
  modified it in the meantime. If the hash matches, the patcher rebuilds the
  original from it in memory, verifies it once more against the original's
  SHA256 and applies the new selection on top.
- Before writing, the patcher also checks that the new result can be reverted
  cleanly to the original.
- An existing `Wow.exe.BAK` is not touched on later runs and stays the
  original.

> [!WARNING]
> Do not delete or edit `patcher_state.ini` while `Wow.exe` is patched –
> without this file the patches can no longer be removed. Then only the backup
> helps: delete `Wow.exe` and rename `Wow.exe.BAK` to `Wow.exe`. If an original
> `Wow.exe.BAK` is in the folder, the patcher points this out itself when it
> aborts.
"""),
("""| `-Select <selection>`  | skip the selection menu: `saved` (saved selection), `billy` (preset "Billy's_Wow.exe", also `default`), `all` or numbers/ranges like `"1,3,5-8"`. Using `-Select` does not change the saved selection. |""",
"""| `-Select <selection>`  | skip the selection menu: `saved` (saved selection), `billy` (preset "Billy's_Wow.exe", also `default`), `all`, `none` (remove all patches, restore the original) or numbers/ranges like `"1,3,5-8"`. The selection completely replaces the patches in `Wow.exe`. Using `-Select` does not change the saved selection. |"""),
("""Exit codes: `0` = success, `1` = error, `2` = cancelled (by the user or because no more input is possible).""",
"""Exit codes: `0` = success (or nothing to do), `1` = error, `2` = cancelled (by the user or because no more input is possible)."""),
("""| `patcher_selection.ini` | Created when you accept a selection, stores your patch selection |
""", """| `patcher_selection.ini` | Created when you accept a selection, stores your patch selection |
| `patcher_state.ini` | Created when patching: hash of the patched `Wow.exe`, applied patches and original bytes for removing them |
"""),
("""the year in the copyright notice. Input as `YYYY-MM-DD`, optionally followed by
`FR` for French month names (e.g. `2026-09-28 FR` → `Sep 28 2026`). The
suggestion in brackets is always **today's date** (with `FR` if you chose it
last time); with `-Unattended` the remembered value is used.
""", """the year in the copyright notice. Input as `YYYY-MM-DD`, optionally followed by
`FR` for French month names (e.g. `2026-09-28 FR` → `Sep 28 2026`). The
suggestion in brackets is **today's date** (with `FR` if you chose it last
time); with `-Unattended` the remembered value is used. If the patch is already
applied, the current date of `Wow.exe` is suggested.
"""),
("""- Before patching, `Wow.exe` is verified by its SHA256 hash. Only an original,
  unmodified `Wow.exe` is accepted – an already patched file is rejected.
- The backup `Wow.exe.BAK` is only created after the integrity check has passed
  and the selection has been confirmed. An existing backup is overwritten (the
  input has just been verified to be the original).
- If there is no `Wow.exe` in the folder, the patcher aborts.
- To restore, delete the patched `Wow.exe` and rename `Wow.exe.BAK` to
  `Wow.exe`.
- To apply a different selection, restore the original first and run the
  patcher again.
""", """- Before patching, `Wow.exe` is verified by its SHA256 hash. Only the original,
  unmodified `Wow.exe` or the file the patcher produced itself last time is
  accepted. A file patched with other tools or older patcher versions is
  rejected.
- The backup `Wow.exe.BAK` is only created from the original, i.e. on the first
  patch run, and only after the selection has been confirmed. An existing
  backup is overwritten (the input has just been verified to be the original).
- If there is no `Wow.exe` in the folder, the patcher aborts.
- To restore the original, run the patcher and press `O`. Without
  `patcher_state.ini` only the backup helps: delete the patched `Wow.exe` and
  rename `Wow.exe.BAK` to `Wow.exe`.
"""),
])

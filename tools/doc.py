import sys
def ed(p,pairs,crlf=False):
    s=open(p,encoding='utf-8',newline='').read()
    if crlf: s=s.replace('\r\n','\n')
    for o,n in pairs:
        if s.count(o)!=1: sys.exit(p+': '+o[:80])
        s=s.replace(o,n)
    if crlf: s=s.replace('\n','\r\n')
    open(p,'w',encoding='utf-8',newline='').write(s)

ed('apply_patches.ps1',[
("#    2. Pruefen: Wow.exe vorhanden und original (SHA256)\n",
 "#    2. Pruefen: Wow.exe vorhanden und original (SHA256) bzw. mit diesem\n#       Patcher gepatcht (Wasserzeichen) - dann Patchstand ermitteln\n"),
("        StateWarn2    = 'Ohne diese Datei lassen sich die Patches nicht mehr zuruecknehmen - dafuer Wow.exe.BAK verwenden.'\n",
 "        StateWarn2    = 'Kein Problem: Beim naechsten Start ermittelt der Patcher den Patchstand ueber das Wasserzeichen (dauert nur etwas laenger).'\n"),
("        StateWarn2    = 'Without this file the patches cannot be removed anymore - use Wow.exe.BAK for that.'\n",
 "        StateWarn2    = 'No problem: next time the patcher determines the patch state via the watermark (just takes a bit longer).'\n"),
("    $lines.Add('# Nicht von Hand aendern! Ohne diese Datei lassen sich die Patches nicht mehr zuruecknehmen.')\n    $lines.Add('# Do not edit! Without this file the patches can no longer be removed.')\n",
 "    $lines.Add('# Nicht von Hand aendern! Nur zur Beschleunigung - ohne diese Datei ermittelt der Patcher den Patchstand ueber das Wasserzeichen.')\n    $lines.Add('# Do not edit! Only speeds things up - without this file the patcher determines the patch state via the watermark.')\n"),
],crlf=True)

ed('README.md',[
("""5. SHA256-Integritätsprüfung: Beim ersten Start muss die `Wow.exe` original und
   unmodifiziert sein, danach exakt die Datei, die der Patcher zuletzt erzeugt
   hat. Alles andere führt zum Abbruch.
""","""5. Prüfung der `Wow.exe`: Beim ersten Start muss sie original und unmodifiziert
   sein (SHA256). Danach erkennt der Patcher eine von ihm gepatchte `Wow.exe` am
   Wasserzeichen und ermittelt, welche Patches darin stecken. Alles andere führt
   zum Abbruch.
"""),
("""10. Der Patcher merkt sich den Hash der neuen `Wow.exe` samt Original-Bytes in
    `patcher_state.ini` und zeigt eine Abschlussmeldung.
""","""10. Der Patcher merkt sich den Hash der neuen `Wow.exe` samt Original-Bytes in
    `patcher_state.ini` (für einen schnelleren nächsten Start) und zeigt eine
    Abschlussmeldung.
"""),
("""- **Erster Start:** Die `Wow.exe` muss original sein (SHA256-Prüfung), sonst
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
""","""- **Erster Start:** Die `Wow.exe` muss original sein (SHA256-Prüfung), sonst
  bricht der Patcher ab. Beim Patchen wird `Wow.exe.BAK` angelegt, und jede
  gepatchte `Wow.exe` bekommt ein [Wasserzeichen](#hinweise).
- **Jeder weitere Start:** Ob die `Wow.exe` mit diesem Patcher gepatcht wurde,
  erkennt er am Wasserzeichen. Fehlt es (und ist die Datei nicht original),
  bricht er ab – etwa bei einer Exe, die mit einem anderen Tool gepatcht wurde.
- **Patchstand ermitteln:** Passt der Hash aus `patcher_state.ini` (dort merkt
  sich der Patcher nach jedem Lauf Hash, Patches, Werte und Original-Bytes),
  geht es über diese Datei – das ist der schnelle Weg. Sonst, z. B. wenn die
  Datei fehlt oder die `Wow.exe` von einem anderen Rechner stammt, prüft der
  Patcher alle Patch-Stellen in der Exe selbst: Welche Patches sind drin, und
  mit welchen Werten (Sprunghöhe, Build-Datum usw.)? Dafür enthält das Skript
  eine kleine Tabelle mit den Original-Bytes an allen Patch-Stellen.
- **Original wiederherstellen:** Aus der gepatchten Exe baut der Patcher im
  Speicher das Original wieder auf, prüft es per SHA256 gegen das Original und
  spielt darauf die neue Auswahl ein. Klappt das nicht exakt – etwa weil die
  Exe nach dem Patchen noch anderweitig verändert wurde –, bricht er ab.
- Vor dem Schreiben prüft der Patcher außerdem, dass sich das neue Ergebnis
  wieder sauber zum Original zurücknehmen lässt.
- Ein vorhandenes `Wow.exe.BAK` wird bei weiteren Läufen nicht angefasst und
  bleibt das Original.

> [!NOTE]
> Ein Patch mit einem Wert, der genau dem Original entspricht (z. B. die
> Sprunghöhe `-7.9555473`), ändert keine Bytes und wird bei der Prüfung der Exe
> deshalb nicht als eingespielt erkannt – er ist dann ja auch wirkungslos.
"""),
("""| `patcher_state.ini` | Wird beim Patchen angelegt: Hash der gepatchten `Wow.exe`, eingespielte Patches und Original-Bytes zum Zurücknehmen |""",
 """| `patcher_state.ini` | Wird beim Patchen angelegt: Hash der gepatchten `Wow.exe`, eingespielte Patches, Werte und Original-Bytes – beschleunigt den nächsten Start, ist aber nicht zwingend nötig |"""),
("""- Vor dem Patchen wird die `Wow.exe` per SHA256-Hash geprüft. Akzeptiert wird
  nur die originale, unmodifizierte `Wow.exe` oder die Datei, die der Patcher
  zuletzt selbst erzeugt hat. Eine mit anderen Tools oder älteren
  Patcher-Versionen gepatchte Datei wird abgelehnt.
""","""- Vor dem Patchen wird die `Wow.exe` geprüft. Akzeptiert wird nur die
  originale, unmodifizierte `Wow.exe` (SHA256) oder eine mit diesem Patcher
  gepatchte (Wasserzeichen), die sich exakt zum Original zurücknehmen lässt.
  Eine mit anderen Tools oder älteren Patcher-Versionen gepatchte Datei wird
  abgelehnt.
"""),
("""  Beim Zurücknehmen aller Patches verschwindet er wieder.
- Zum Wiederherstellen des Originals den Patcher starten und `N` und ENTER drücken. Ohne
  `patcher_state.ini` geht es nur über das Backup: gepatchte `Wow.exe` löschen
  und `Wow.exe.BAK` in `Wow.exe` umbenennen.
""","""  Beim Zurücknehmen aller Patches verschwindet er wieder. Am Wasserzeichen
  erkennt der Patcher auch selbst, dass eine `Wow.exe` von ihm stammt.
- Zum Wiederherstellen des Originals den Patcher starten und `N` und ENTER
  drücken – mit oder ohne `patcher_state.ini`. Alternativ geht es über das
  Backup: gepatchte `Wow.exe` löschen und `Wow.exe.BAK` in `Wow.exe` umbenennen.
- **Für Entwickler:** Die Original-Byte-Tabelle im Skript wird mit
  `apply_patches.ps1 -BuildTable -Path <originale Wow.exe>` neu erzeugt. Das ist
  nach jeder Änderung an einem Patch nötig; passt sie nicht mehr, weist der
  Patcher nach dem Patchen darauf hin.
"""),
])

ed('README.en.md',[
("""10. The patcher remembers the hash of the new `Wow.exe` together with the
    original bytes in `patcher_state.ini` and shows a final message.
""","""10. The patcher remembers the hash of the new `Wow.exe` together with the
    original bytes in `patcher_state.ini` (for a faster next start) and shows a
    final message.
"""),
("""- **First start:** `Wow.exe` must be original (SHA256 check), otherwise the
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
""","""- **First start:** `Wow.exe` must be original (SHA256 check), otherwise the
  patcher aborts. Patching creates `Wow.exe.BAK`, and every patched `Wow.exe`
  gets a [watermark](#notes).
- **Every later start:** the patcher recognizes a `Wow.exe` patched by itself
  by the watermark. If it is missing (and the file is not original), it aborts
  – e.g. for an exe patched with another tool.
- **Determining the patch state:** if the hash in `patcher_state.ini` matches
  (the patcher stores hash, patches, values and original bytes there after
  every run), it uses that file – the fast way. Otherwise, e.g. if the file is
  missing or the `Wow.exe` comes from another computer, the patcher checks all
  patch locations in the exe itself: which patches are in it, and with which
  values (jump height, build date etc.)? For this the script contains a small
  table with the original bytes at all patch locations.
- **Restoring the original:** from the patched exe the patcher rebuilds the
  original in memory, verifies it against the original's SHA256 and applies the
  new selection on top. If that does not work exactly – e.g. because the exe
  was changed in some other way after patching – it aborts.
- Before writing, the patcher also checks that the new result can be reverted
  cleanly to the original.
- An existing `Wow.exe.BAK` is not touched on later runs and stays the
  original.

> [!NOTE]
> A patch with a value exactly matching the original (e.g. the jump height
> `-7.9555473`) changes no bytes and is therefore not detected as applied when
> the exe is checked – it has no effect then anyway.
"""),
("""| `patcher_state.ini` | Created when patching: hash of the patched `Wow.exe`, applied patches and original bytes for removing them |""",
 """| `patcher_state.ini` | Created when patching: hash of the patched `Wow.exe`, applied patches, values and original bytes – speeds up the next start, but is not strictly required |"""),
("""- Before patching, `Wow.exe` is verified by its SHA256 hash. Only the original,
  unmodified `Wow.exe` or the file the patcher produced itself last time is
  accepted. A file patched with other tools or older patcher versions is
  rejected.
""","""- Before patching, `Wow.exe` is checked. Only the original, unmodified
  `Wow.exe` (SHA256) or one patched with this patcher (watermark) that can be
  reverted exactly to the original is accepted. A file patched with other tools
  or older patcher versions is rejected.
"""),
("""  Removing all patches removes it again.
- To restore the original, run the patcher and press `N` and ENTER. Without
  `patcher_state.ini` only the backup helps: delete the patched `Wow.exe` and
  rename `Wow.exe.BAK` to `Wow.exe`.
""","""  Removing all patches removes it again. The patcher itself also uses the
  watermark to recognize that a `Wow.exe` comes from it.
- To restore the original, run the patcher and press `N` and ENTER – with or
  without `patcher_state.ini`. Alternatively use the backup: delete the patched
  `Wow.exe` and rename `Wow.exe.BAK` to `Wow.exe`.
- **For developers:** the original bytes table in the script is regenerated
  with `apply_patches.ps1 -BuildTable -Path <original Wow.exe>`. This is needed
  after every change to a patch; if it no longer matches, the patcher points it
  out after patching.
"""),
])
print('ok')

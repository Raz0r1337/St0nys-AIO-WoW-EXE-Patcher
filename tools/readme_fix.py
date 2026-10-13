import re, sys

def ed(p, pairs):
    s = open(p, encoding='utf-8', newline='').read()
    for o, n in pairs:
        c = s.count(o)
        if c != 1: sys.exit(f"{p}: count {c} for {o[:90]!r}")
        s = s.replace(o, n)
    open(p, 'w', encoding='utf-8', newline='').write(s)

BAN_DE = "**Viele Server tolerieren eine veränderte Dateigröße der `Wow.exe` nicht – das\n> kann zu einem Bann führen.**"
BAN_EN = "**Many servers do not tolerate a changed file size of `Wow.exe` – this can lead\n> to a ban.**"

ed('README.md', [
# Voraussetzungen
("""  (beim ersten Start; danach die zuletzt vom Patcher erzeugte `Wow.exe`)
""", """  (beim ersten Start; danach eine mit diesem Patcher gepatchte `Wow.exe`)
"""),
# Ablauf 8
("""8. Automatisches Backup als `Wow.exe.BAK` – nur vom Original, also beim ersten
   Patchen.
""", """8. Backup als `Wow.exe.BAK` – beim ersten Patchen eine Kopie des Originals. Fehlt
   es bei einem späteren Lauf, wird es aus dem rekonstruierten Original neu
   angelegt.
"""),
# Patch-Auswahl Intro + Hinweise
("""die [Patch-Übersicht](#patch-übersicht). Vorausgewählt ist die Standard-Auswahl,
das **Preset „Billy's_Wow.exe“** (Spalte „Standard“ in der Übersicht). Patches, die
zusätzlich etwas benötigen, zeigen das in Klammern hinter dem Namen, der Link
dazu steht direkt darunter.
""", """die [Patch-Übersicht](#patch-übersicht). Beim ersten Start ist das
**Preset „Billy's_Wow.exe“** vorausgewählt (Spalte „Standard“ in der Übersicht),
danach die gespeicherte Auswahl bzw. die Patches, die gerade in der `Wow.exe`
stecken. Patches, die zusätzlich etwas benötigen, zeigen das in Klammern hinter
dem Namen, der Link dazu steht direkt darunter.
"""),
("""Einige Patches wirken nur zusammen mit anderen voll (z. B. die erweiterten
Slider-Maxima brauchen die CVar-Unlocks). Fehlt so ein Ergänzungs-Patch in der
Auswahl, zeigt der Patcher vor der Sicherheitsabfrage einen **Hinweis** an –
gesperrt wird nichts. Ebenso weist er darauf hin, wenn ein Patch einen anderen
überflüssig macht (Warden komplett abschalten ersetzt den RCE-Fix).
""", """Vor der Sicherheitsabfrage zeigt der Patcher **Hinweise** an, gesperrt wird
nichts: wenn ein Ergänzungs-Patch fehlt (z. B. brauchen die erweiterten
Slider-Maxima die CVar-Unlocks), wenn ein Patch einen anderen überflüssig macht
(Warden komplett abschalten ersetzt den RCE-Fix) und wenn die gewählten Patches
die `Wow.exe` größer machen (Bann-Gefahr, siehe [Hinweise](#hinweise)).
"""),
# Patches aendern
("""oder bei den Client-Info-Patches die Werte ändern. Mit `N` und ENTER nimmst du
""", """oder Werte ändern (Sprunghöhe, Doppelsprung, Client-Infos). Mit `N` und ENTER nimmst du
"""),
("""- Ein vorhandenes `Wow.exe.BAK` wird bei weiteren Läufen nicht angefasst und
  bleibt das Original.
""", """- Ein vorhandenes `Wow.exe.BAK` wird bei weiteren Läufen nicht angefasst und
  bleibt das Original. Fehlt es, legt der Patcher es aus dem rekonstruierten
  Original neu an.
"""),
# Nr. 4 Boxen
("""> [!IMPORTANT]
> **Teilt sich die Code-Höhle mit dem Slider-Patch (Nr. 46).** Der Code liegt in der freien Lücke am Ende von `.text`, die
> auch Nr. 52 nutzt. Nr. 4 und Nr. 52 passen
> zusammen hinein, nicht aber neben den Slider-Patch: Ist Nr. 46 gewählt, weicht der
> Patch automatisch auf eine eigene kleine Sektion `.wfcfix` am Dateiende aus, und
> der Patcher weist vor der Sicherheitsabfrage darauf hin. Die `Wow.exe` wird
> dadurch etwas größer: Jede ausgelagerte Höhle bekommt eine 512-Byte-Sektion,
> dazu kommt das Auffüllen des Dateiendes – mit Nr. 4 und 49 zusammen rund 1,4 KB.
> Beim Zurücknehmen fällt das wieder weg.

> [!WARNING]
> Alle drei Patches (Nr. 4, die NPC-Ausblendung und der Slider-Patch) lassen sich
> zusammen einspielen, die `Wow.exe` wird dann aber größer. **Viele Server
> tolerieren eine veränderte Dateigröße der `Wow.exe` nicht – das kann zu einem
> Bann führen.**
""", """> [!IMPORTANT]
> **Teilt sich die Code-Höhle mit dem Slider-Patch (Nr. 46).** Der Code liegt in
> der freien Lücke am Ende von `.text`, die auch Nr. 52 nutzt. Nr. 4 und 52 passen
> zusammen hinein, nicht aber neben den Slider-Patch: Ist Nr. 46 gewählt, weicht
> der Patch automatisch auf eine eigene kleine Sektion `.wfcfix` am Dateiende aus,
> und der Patcher weist vor der Sicherheitsabfrage darauf hin. Die `Wow.exe` wird
> dadurch etwas größer (512-Byte-Sektion plus Auffüllen des Dateiendes, mit Nr. 4
> und 52 zusammen rund 1,4 KB; beim Zurücknehmen fällt das wieder weg).
> """ + BAN_DE + """
"""),
# Nr. 44 Querverweis
("""multiplizieren (siehe Patch Nr. 47 und 46) – im
Original nur die der Kategorien 1 bis 3, mit Patch Nr. 47 alle fünf. Es ist
""", """multiplizieren (siehe Patch Nr. 47) – im Original nur die der Kategorien 1 bis
3, mit Patch Nr. 47 alle fünf. Es ist
"""),
# Nr. 42 Querverweis auf Slider-Patch
("""Patch Nr. 46 „Slider-Maxima im Video-Menü erweitern“).
""", """Patch Nr. 46 „Grafikoptionen: Slider-Maxima erweitern“).
"""),
# Nr. 46 Boxen
("""> [!NOTE]
> Die Code-Höhle am Ende von `.text` nutzen auch Nr. 4 und Nr. 52. Sind sie
> zusammen mit diesem Patch gewählt, weichen sie automatisch auf eigene kleine
> Sektionen am Dateiende aus – die `Wow.exe` wird dadurch etwas größer.

> [!WARNING]
> Alle drei Patches (Nr. 4, die NPC-Ausblendung und der Slider-Patch) lassen sich
> zusammen einspielen, die `Wow.exe` wird dann aber größer. **Viele Server
> tolerieren eine veränderte Dateigröße der `Wow.exe` nicht – das kann zu einem
> Bann führen.**
""", """> [!WARNING]
> Die Code-Höhle am Ende von `.text` nutzen auch Nr. 4 und Nr. 52. Zusammen mit
> diesem Patch weichen sie automatisch auf eigene kleine Sektionen am Dateiende
> aus – die `Wow.exe` wird dadurch etwas größer. """ + BAN_DE + """
"""),
# Nr. 52 Boxen
("""> **Teilt sich die Code-Höhle mit dem Slider-Patch (Nr. 46).** Wie bei Nr. 4: Mit
> dem Slider-Patch weicht der Patch automatisch auf eine eigene kleine Sektion
> `.nofade` am Dateiende aus. Auch hier wird die `Wow.exe` dadurch etwas größer
> (siehe Nr. 4).

> [!WARNING]
> Alle drei Patches (Nr. 4, die NPC-Ausblendung und der Slider-Patch) lassen sich
> zusammen einspielen, die `Wow.exe` wird dann aber größer. **Viele Server
> tolerieren eine veränderte Dateigröße der `Wow.exe` nicht – das kann zu einem
> Bann führen.**
""", """> **Teilt sich die Code-Höhle mit dem Slider-Patch (Nr. 46).** Wie bei Nr. 4: Mit
> dem Slider-Patch weicht der Patch automatisch auf eine eigene kleine Sektion
> `.nofade` am Dateiende aus, die `Wow.exe` wird dadurch etwas größer.
> """ + BAN_DE + """
"""),
# Nr. 41 Boxen
("""> [!WARNING]
> Server mit Anti-Cheat können Sprünge in der Luft erkennen.

> [!WARNING]
> Dieser Patch hängt eine eigene Sektion an, die `Wow.exe` wird dadurch größer.
> **Viele Server tolerieren eine veränderte Dateigröße der `Wow.exe` nicht – das
> kann zu einem Bann führen.**
""", """> [!WARNING]
> Server mit Anti-Cheat können Sprünge in der Luft erkennen.
>
> Dieser Patch hängt eine eigene Sektion an, die `Wow.exe` wird dadurch größer.
> """ + BAN_DE + """
"""),
# Nr. 53 Boxen
("""> [!NOTE]
> Dieser Patch hängt eine neue PE-Sektion (`.hdp`) an die `Wow.exe` an
> (generierte 256er-Alphamaske + Code-Caves + Detour des Masken-Builders). Die
> Datei wächst dadurch um ca. 69 KB.

> [!WARNING]
> Dieser Patch hängt eine eigene Sektion an, die `Wow.exe` wird dadurch größer.
> **Viele Server tolerieren eine veränderte Dateigröße der `Wow.exe` nicht – das
> kann zu einem Bann führen.**
""", """> [!WARNING]
> Dieser Patch hängt eine neue PE-Sektion `.hdp` an die `Wow.exe` an (generierte
> 256er-Alphamaske + Code-Caves + Detour des Masken-Builders), die Datei wächst
> dadurch um ca. 69 KB. """ + BAN_DE + """
"""),
# Nr. 64 Boxen
("""> [!NOTE]
> Dieser Patch verändert wie die HD-Portraits die Dateigröße und die
> PE-Struktur, weil er eine Sektion anhängt. Server, die den Client auf Größe
> oder Sektionsaufbau prüfen, können das bemerken.

> [!WARNING]
> Dieser Patch hängt eine eigene Sektion an, die `Wow.exe` wird dadurch größer.
> **Viele Server tolerieren eine veränderte Dateigröße der `Wow.exe` nicht – das
> kann zu einem Bann führen.**
""", """> [!WARNING]
> Dieser Patch hängt wie die HD-Portraits eine eigene Sektion an (etwa +1 KB),
> die `Wow.exe` wird dadurch größer. """ + BAN_DE + """
"""),
# Doppelte Leerzeile
("""> [OpenAL Soft](https://github.com/kcat/openal-soft).


### Client-Infos""", """> [OpenAL Soft](https://github.com/kcat/openal-soft).

### Client-Infos"""),
# Client-Infos Intro
("""Steckt ein Patch schon in der `Wow.exe`, ist sein aktueller Wert der Vorschlag.
Bei der Abfrage steht der Vorschlag hinter dem Patchnamen mit dem Originalwert.
""", """Steckt ein Patch schon in der `Wow.exe`, ist sein aktueller Wert der Vorschlag.
Bei der Abfrage steht er auch hinter dem Patchnamen (`-> Vorschlag: …`, bei einem
bereits eingespielten Patch `-> aktuell: …`).
"""),
# Nr. 69 Dopplung
("""zuletzt gewählt hast); mit `-Unattended` gilt der gemerkte Wert. Ist der Patch
schon eingespielt, steht dort das aktuelle Datum der `Wow.exe`. Bei der Abfrage
steht der Vorschlag außerdem hinter dem Originaldatum, z. B.
`Build-Datum aendern (Original Jun 24 2010) -> Vorschlag: 2026-10-01` bzw.
`-> aktuell: …`, wenn der Patch bereits eingespielt ist.
""", """zuletzt gewählt hast); mit `-Unattended` gilt der gemerkte Wert. Ist der Patch
schon eingespielt, steht dort das aktuelle Datum der `Wow.exe`.
"""),
# Nr. 59 Umbruch
("""nicht mehr automatisch aus, man startet mit dem Standard-Aussehen. Der Zufall-Knopf funktioniert weiter – er nutzt im Client einen
eigenen Weg.
""", """nicht mehr automatisch aus, man startet mit dem Standard-Aussehen. Der
Zufall-Knopf funktioniert weiter – er nutzt im Client einen eigenen Weg.
"""),
# Hinweise
("""- Vor dem Patchen wird die `Wow.exe` geprüft. Akzeptiert wird nur die
  originale, unmodifizierte `Wow.exe` (SHA256) oder eine mit diesem Patcher
  gepatchte (Wasserzeichen), die sich exakt zum Original zurücknehmen lässt.
  Eine mit anderen Tools oder älteren Patcher-Versionen gepatchte Datei wird
  abgelehnt.
- Das Backup `Wow.exe.BAK` wird nur vom Original erstellt, also beim ersten
  Patchen, und erst wenn die Auswahl bestätigt ist. Ein vorhandenes Backup wird
  dabei überschrieben (es ist ja nachweislich wieder das Original).
- Falls keine `Wow.exe` im Ordner liegt, bricht der Patcher ab.
- **Wasserzeichen:** Jede gepatchte `Wow.exe` enthält den Text
""", """- **Dateigröße und Banns:** Patches, die eine Sektion an die `Wow.exe` anhängen
  (Nr. 41, 53 und 64 immer, Nr. 4 und 52 zusammen mit Nr. 46), machen die Datei
  größer. Viele Server tolerieren eine veränderte Dateigröße nicht – das kann zu
  einem Bann führen. Diese Patches sind in der Übersicht markiert, und der
  Patcher warnt vor der Sicherheitsabfrage. Alle anderen Patches ändern die
  Dateigröße nicht.
- **Wasserzeichen:** Jede gepatchte `Wow.exe` enthält den Text
"""),
("""  Beim Zurücknehmen aller Patches verschwindet er wieder. Am Wasserzeichen
  erkennt der Patcher auch selbst, dass eine `Wow.exe` von ihm stammt.
- Zum Wiederherstellen des Originals den Patcher starten und `N` und ENTER
  drücken – mit oder ohne `patcher_state.ini`. Alternativ geht es über das
  Backup: gepatchte `Wow.exe` löschen und `Wow.exe.BAK` in `Wow.exe` umbenennen.
""", """  Beim Zurücknehmen aller Patches verschwindet er wieder. Am Wasserzeichen
  erkennt der Patcher auch selbst, dass eine `Wow.exe` von ihm stammt.
- **Original wiederherstellen:** Patcher starten, `N` und ENTER drücken – mit
  oder ohne `patcher_state.ini`. Alternativ gepatchte `Wow.exe` löschen und
  `Wow.exe.BAK` in `Wow.exe` umbenennen.
"""),
])

ed('README.en.md', [
("""  (on the first start; after that the `Wow.exe` last produced by the patcher)
""", """  (on the first start; after that a `Wow.exe` patched with this patcher)
"""),
("""8. Automatic backup as `Wow.exe.BAK` – of the original only, i.e. on the first
   patch run.
""", """8. Backup as `Wow.exe.BAK` – a copy of the original on the first patch run. If
   it is missing on a later run, it is recreated from the reconstructed
   original.
"""),
("""[patch overview](#patch-overview). The default selection is preselected:
the **preset "Billy's_Wow.exe"** (see the "Default" column in the overview). Patches
that need something additional say so in parentheses after their name, with
the link right below.
""", """[patch overview](#patch-overview). On the first start the
**preset "Billy's_Wow.exe"** is preselected (see the "Default" column in the
overview), after that the saved selection or the patches currently in
`Wow.exe`. Patches that need something additional say so in parentheses after
their name, with the link right below.
"""),
("""Some patches only take full effect together with others (e.g. the extended
slider maximums need the CVar unlocks). If such a companion patch is missing
from the selection, the patcher shows a **note** before the confirmation
prompt – nothing is blocked. It also points out when one patch makes another
unnecessary (disabling Warden completely replaces the RCE fix).
""", """Before the confirmation prompt the patcher shows **notes**, nothing is blocked:
when a companion patch is missing (e.g. the extended slider maximums need the
CVar unlocks), when one patch makes another unnecessary (disabling Warden
completely replaces the RCE fix) and when the selected patches make `Wow.exe`
larger (ban risk, see [Notes](#notes)).
"""),
("""you can add patches, deselect them or change the values of the client info
patches as you like. `N` and ENTER removes every patch – afterwards `Wow.exe`
""", """you can add patches, deselect them or change values (jump height, double
jump, client info) as you like. `N` and ENTER removes every patch – afterwards `Wow.exe`
"""),
("""- An existing `Wow.exe.BAK` is not touched on later runs and stays the
  original.
""", """- An existing `Wow.exe.BAK` is not touched on later runs and stays the
  original. If it is missing, the patcher recreates it from the reconstructed
  original.
"""),
("""> [!IMPORTANT]
> **Shares the code cave with the slider patch (No. 46).** The code lives in the free gap at the end of `.text`, which No. 52
> uses as well. No. 4 and No. 52 fit in there together,
> but not next to the slider patch: if No. 46 is selected, the patch automatically
> moves to a small section `.wfcfix` of its own at the end of the file, and the
> patcher points this out before the confirmation prompt. This makes `Wow.exe`
> slightly larger: each moved cave gets a 512-byte section, plus padding of the
> end of the file – about 1.4 KB for No. 4 and 49 together. Removing the patches
> takes this away again.

> [!WARNING]
> All three patches (No. 4, the NPC fade-out and the slider patch) can be applied
> together, but then `Wow.exe` becomes larger. **Many servers do not tolerate a
> changed file size of `Wow.exe` – this can lead to a ban.**
""", """> [!IMPORTANT]
> **Shares the code cave with the slider patch (No. 46).** The code lives in the
> free gap at the end of `.text`, which No. 52 uses as well. No. 4 and 52 fit in
> there together, but not next to the slider patch: if No. 46 is selected, the
> patch automatically moves to a small section `.wfcfix` of its own at the end
> of the file, and the patcher points this out before the confirmation prompt.
> This makes `Wow.exe` slightly larger (a 512-byte section plus padding of the
> end of the file, about 1.4 KB for No. 4 and 52 together; removing the patches
> takes this away again). """ + BAN_EN + """
"""),
("""(see patches No. 47 and 46) – in the original
only for categories 1 to 3, with patch No. 47 for all five. That makes it the
""", """(see patch No. 47) – in the original only for categories 1 to 3, with patch
No. 47 for all five. That makes it the
"""),
("""patch No. 46 "Extend slider maximums in the video menu").
""", """patch No. 46 "Graphics options: extend slider maximums").
"""),
("""> [!NOTE]
> No. 4 and No. 52 use the code cave at the end of `.text` as well. If they are
> selected together with this patch, they automatically move to small sections
> of their own at the end of the file – this makes `Wow.exe` slightly larger.

> [!WARNING]
> All three patches (No. 4, the NPC fade-out and the slider patch) can be applied
> together, but then `Wow.exe` becomes larger. **Many servers do not tolerate a
> changed file size of `Wow.exe` – this can lead to a ban.**
""", """> [!WARNING]
> No. 4 and No. 52 use the code cave at the end of `.text` as well. Together with
> this patch they automatically move to small sections of their own at the end
> of the file – this makes `Wow.exe` slightly larger. """ + BAN_EN + """
"""),
("""> **Shares the code cave with the slider patch (No. 46).** As with No. 4: together
> with the slider patch, the patch automatically moves to a small section
> `.nofade` of its own at the end of the file. Here too `Wow.exe` becomes slightly
> larger (see No. 4).

> [!WARNING]
> All three patches (No. 4, the NPC fade-out and the slider patch) can be applied
> together, but then `Wow.exe` becomes larger. **Many servers do not tolerate a
> changed file size of `Wow.exe` – this can lead to a ban.**
""", """> **Shares the code cave with the slider patch (No. 46).** As with No. 4: together
> with the slider patch, the patch automatically moves to a small section
> `.nofade` of its own at the end of the file, which makes `Wow.exe` slightly
> larger. """ + BAN_EN + """
"""),
("""> [!WARNING]
> Servers with anti-cheat may detect jumps in the air.

> [!WARNING]
> This patch appends a section of its own, which makes `Wow.exe` larger. **Many
> servers do not tolerate a changed file size of `Wow.exe` – this can lead to a
> ban.**
""", """> [!WARNING]
> Servers with anti-cheat may detect jumps in the air.
>
> This patch appends a section of its own, which makes `Wow.exe` larger.
> """ + BAN_EN + """
"""),
("""> [!NOTE]
> This patch appends a new PE section (`.hdp`) to `Wow.exe` (generated 256px
> alpha mask + code caves + detour of the mask builder). The file grows by
> about 69 KB.

> [!WARNING]
> This patch appends a section of its own, which makes `Wow.exe` larger. **Many
> servers do not tolerate a changed file size of `Wow.exe` – this can lead to a
> ban.**
""", """> [!WARNING]
> This patch appends a new PE section `.hdp` to `Wow.exe` (generated 256px alpha
> mask + code caves + detour of the mask builder), the file grows by about
> 69 KB. """ + BAN_EN + """
"""),
("""> [!NOTE]
> Like the HD portraits, this patch changes the file size and PE structure
> because it appends a section. Servers that check the client's size or section
> layout may notice this.

> [!WARNING]
> This patch appends a section of its own, which makes `Wow.exe` larger. **Many
> servers do not tolerate a changed file size of `Wow.exe` – this can lead to a
> ban.**
""", """> [!WARNING]
> Like the HD portraits, this patch appends a section of its own (about +1 KB),
> which makes `Wow.exe` larger. """ + BAN_EN + """
"""),
("""> [OpenAL Soft](https://github.com/kcat/openal-soft).


### Client info""", """> [OpenAL Soft](https://github.com/kcat/openal-soft).

### Client info"""),
("""values or the original values are used. If a patch is already in `Wow.exe`,
its current value is the suggestion. When asking, the patcher shows the
suggestion after the patch name with the original value.
""", """values or the original values are used. If a patch is already in `Wow.exe`,
its current value is the suggestion. When asking, it is also shown after the
patch name (`-> suggestion: …`, or `-> current: …` for an already applied patch).
"""),
("""time); with `-Unattended` the remembered value is used. If the patch is already
applied, the current date of `Wow.exe` is suggested. When asking for the value,
the patcher also shows the suggestion after the original date, e.g.
`Change build date (original Jun 24 2010) -> suggestion: 2026-10-01`, or
`-> current: …` if the patch is already applied.
""", """time); with `-Unattended` the remembered value is used. If the patch is already
applied, the current date of `Wow.exe` is suggested.
"""),
("""etc. automatically; you start with the default appearance. The randomize button keeps working – it uses a separate path in
the client.
""", """etc. automatically; you start with the default appearance. The randomize button
keeps working – it uses a separate path in the client.
"""),
("""from Alastor StrixEfuartus' 12th Generation EXE, ported and adjusted by St0ny: the original redirects the check into a code cave
that ignores its result. That cave, however, sits exactly where the slider
""", """from Alastor StrixEfuartus' 12th Generation EXE, ported and adjusted by St0ny:
the original redirects the check into a code cave that ignores its result.
That cave, however, sits exactly where the slider
"""),
("""- Before patching, `Wow.exe` is checked. Only the original, unmodified
  `Wow.exe` (SHA256) or one patched with this patcher (watermark) that can be
  reverted exactly to the original is accepted. A file patched with other tools
  or older patcher versions is rejected.
- The backup `Wow.exe.BAK` is only created from the original, i.e. on the first
  patch run, and only after the selection has been confirmed. An existing
  backup is overwritten (the input has just been verified to be the original).
- If there is no `Wow.exe` in the folder, the patcher aborts.
- **Watermark:** every patched `Wow.exe` contains the text
""", """- **File size and bans:** patches that append a section to `Wow.exe` (No. 41,
  53 and 64 always, No. 4 and 52 together with No. 46) make the file larger.
  Many servers do not tolerate a changed file size – this can lead to a ban.
  These patches are marked in the overview, and the patcher warns before the
  confirmation prompt. All other patches do not change the file size.
- **Watermark:** every patched `Wow.exe` contains the text
"""),
("""  Removing all patches removes it again. The patcher itself also uses the
  watermark to recognize that a `Wow.exe` comes from it.
- To restore the original, run the patcher and press `N` and ENTER – with or
  without `patcher_state.ini`. Alternatively use the backup: delete the patched
  `Wow.exe` and rename `Wow.exe.BAK` to `Wow.exe`.
""", """  Removing all patches removes it again. The patcher itself also uses the
  watermark to recognize that a `Wow.exe` comes from it.
- **Restoring the original:** run the patcher, press `N` and ENTER – with or
  without `patcher_state.ini`. Alternatively delete the patched `Wow.exe` and
  rename `Wow.exe.BAK` to `Wow.exe`.
"""),
])

# Ueberschriften der Beschreibungen = Namen aus der Uebersicht
for p, key in (('README.md', 'Nr'), ('README.en.md', 'No')):
    s = open(p, encoding='utf-8', newline='').read()
    names = {}
    for m in re.finditer(r'(?m)^\| (\d+) +\| (.+?) \| [^|]* \| (?:✅|–) \|$', s):
        names[int(m.group(1))] = re.sub(r' \*\(.*\)\*$', '', m.group(2))
    assert len(names) == 69, (p, len(names))
    changed = []
    def fix(m):
        n = int(m.group(3)); tn = names[n]
        if m.group(1) != tn: changed.append((n, m.group(1), tn))
        return f"**{tn}** *({m.group(2)}. {n}{m.group(4)}"
    s2 = re.sub(r'(?m)^\*\*(.+?)\*\* \*\((Nr|No)\. (\d+)([,)])', fix, s)
    open(p, 'w', encoding='utf-8', newline='').write(s2)
    for c in changed: print(p, c[0], '|', c[1], '->', c[2])
print('ok')

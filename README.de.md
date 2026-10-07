# St0nys-AIO-WoW-EXE-Patcher

🇩🇪 Deutsch | [🇬🇧 English](README.md)

Ein All-in-One-Patcher (AIO) für die `Wow.exe` von **World of Warcraft 3.3.5a
(Build 12340)**.
Er spielt Bugfixes, Performance-Optimierungen, erweiterte Sichtweiten,
verbesserte Sound-Einstellungen und einige Komfort-Funktionen direkt in die
EXE ein – in einem Durchgang, ohne zusätzliche Tools oder DLL-Injector.

Beim Start wählst du die **Sprache** (Deutsch / English) und danach in einem
Menü, **welche Patches** eingespielt werden sollen. Eingespielte Patches lassen
sich später jederzeit wieder **abwählen oder ergänzen** – bis zurück zur
originalen `Wow.exe`.

> [!IMPORTANT]
> Dieses Repository enthält **keine** `Wow.exe` und keine anderen Dateien von
> Blizzard. Du brauchst deine eigene, unveränderte `Wow.exe` 3.3.5a (12340).

> [!WARNING]
> **Benutzung auf eigene Gefahr.** Als sicher (🟢) eingestufte Patches sind im
> Spiel getestet und sollten auch auf öffentlichen Servern unbedenklich sein –
> eine 100-%-Garantie gibt es aber nicht: Was auf einem Server erkannt und
> geduldet wird, entscheidet der jeweilige Serverbetreiber, und das kann sich
> auch ändern. Alle anderen Patches tragen in der Übersicht und im Patcher eine
> einheitliche Warnung (siehe [Hinweise](#hinweise)). Im Zweifel prüfe die Richtlinien deines Servers,
> bevor du eine gepatchte `Wow.exe` dort benutzt. Der Patcher zeigt diesen
> Hinweis auch bei jedem Start an.

---

## Inhalt

- [Voraussetzungen](#voraussetzungen)
- [Benutzung](#benutzung)
- [Ablauf](#ablauf)
- [Patch-Auswahl](#patch-auswahl)
- [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen)
- [Parameter für den unbeaufsichtigten Betrieb](#parameter-für-den-unbeaufsichtigten-betrieb)
- [Dateien](#dateien)
- [Patch-Übersicht](#patch-übersicht)
- [Patch-Beschreibungen](#patch-beschreibungen)
- [Hinweise](#hinweise)
- [Danksagung](#danksagung)
- [Lizenz](#lizenz)

---

## Voraussetzungen

- Windows mit PowerShell (Windows PowerShell 5.1 ist ab Windows 10 vorinstalliert)
- Eine **originale, unmodifizierte** `Wow.exe` 3.3.5a, Build 12340 mit
  SHA256 `AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8`
  (nur beim ersten Start; danach genügt eine mit diesem Patcher gepatchte
  `Wow.exe`)

## Benutzung

1. `patcher.bat` und `apply_patches.ps1` in den WoW-Ordner kopieren
   (dorthin, wo die `Wow.exe` liegt).
2. WoW beenden, falls es noch läuft.
3. `patcher.bat` per Doppelklick starten.
4. Sprache wählen (nur beim ersten Start), Patches auswählen, bestätigen – fertig.

Patches **ändern oder zurücknehmen:** `patcher.bat` einfach erneut starten,
siehe [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen).

> [!NOTE]
> Windows warnt beim Start der gepatchten `Wow.exe` wahrscheinlich vor einer
> nicht signierten, möglicherweise schädlichen App. Das ist bei jeder
> veränderten `Wow.exe` so: Jede Änderung macht Blizzards digitale Signatur
> ungültig, und eine neue, von Windows anerkannte Signatur lässt sich für eine
> veränderte Blizzard-Datei nicht erstellen. Starten lässt sie sich trotzdem,
> z. B. über „Weitere Informationen“ → „Trotzdem ausführen“. Mehr dazu unter
> [Hinweise](#hinweise).

## Ablauf

1. ASCII-Banner wird angezeigt.
2. **Sprachauswahl:** `1` = Deutsch, `2` = English. Nur beim ersten Start – danach
   ist die Sprache gemerkt und lässt sich im Menü mit `L` umschalten.
3. Begrüßung, ENTER zum Starten.
4. Prüfung, ob eine `Wow.exe` im Ordner vorhanden ist.
5. Prüfung der `Wow.exe`: Beim ersten Start muss sie original und unmodifiziert
   sein (SHA256). Danach erkennt der Patcher eine von ihm gepatchte `Wow.exe` am
   Wasserzeichen und ermittelt, welche Patches darin stecken. Alles andere führt
   zum Abbruch.
6. **Patch-Auswahl** im Menü (siehe unten). Vorausgewählt ist die Auswahl vom
   letzten Mal bzw. bei einer gepatchten `Wow.exe` die Patches, die gerade
   darin stecken.
7. Bei Patches mit eigenem Wert (Sprunghöhe, Doppelsprung, Client-Infos) fragt
   der Patcher die Werte ab; danach speichert er die Auswahl.
8. Zusammenfassung der gewählten Patches (bei einer gepatchten `Wow.exe`: was
   neu dazukommt, was zurückgenommen wird), Hinweise (fehlende oder
   überflüssige Ergänzungs-Patches, Warnungen) und Sicherheitsabfrage (J/N).
9. Backup: Beim ersten Patchen wird das Original als `Wow.exe.ORI` gesichert,
   bei jedem weiteren Lauf die bisherige `Wow.exe` als `Wow.exe.BAK`.
10. Alle gewählten Patches werden im Speicher eingespielt (mit
    Fortschrittsanzeige) und die `Wow.exe` danach **einmal** zurückgeschrieben.
    Tritt dabei ein Fehler auf, bleibt die `Wow.exe` unverändert.
11. Der Patcher merkt sich den Hash der neuen `Wow.exe` samt Original-Bytes in
    `patcher_state.ini` (für einen schnelleren nächsten Start) und zeigt eine
    Abschlussmeldung.

## Patch-Auswahl

Das Menü listet alle Patches mit Nummer auf. `[X]` = wird eingespielt,
`[ ]` = wird übersprungen. Das Menü ist in dieselben Kategorien gegliedert wie
die [Patch-Übersicht](#patch-übersicht). Beim ersten Start ist das
**Preset „Reforged“** vorausgewählt (Spalte „Reforged“ in der
Übersicht), danach die gespeicherte Auswahl bzw. die Patches, die gerade in der
`Wow.exe` stecken. Mit `B` lädst du das Preset **„Billy's_Wow.exe“** (Spalte
„Billy“), mit `S` das Preset **„St0nys_Wow.exe“** (Spalte „St0ny“). Patches,
die zusätzlich etwas benötigen, zeigen das in Klammern hinter dem Namen; der
Link dazu steht direkt darunter.

| Eingabe            | Wirkung                                     |
|--------------------|---------------------------------------------|
| `5`                | Patch 5 an-/abwählen                        |
| `3 7 12` / `3,7,12`| mehrere Patches an-/abwählen                |
| `10-15`            | einen Bereich an-/abwählen                  |
| `A`                | alle Patches an                             |
| `N`                | alle Patches aus (bei gepatchter `Wow.exe` + ENTER: Original wiederherstellen) |
| `L`                | Sprache umschalten (Deutsch ↔ English)      |
| `R`                | Preset „Reforged“ laden (= Standard) (**Sicher** – offizielles Preset von [Project Reforged](https://projectreforged.github.io/wotlk/)) |
| `B`                | Preset „Billy's_Wow.exe“ laden (**Sicher** – basiert auf Billys erprobter Exe) |
| `S`                | Preset „St0nys_Wow.exe“ laden (**Nicht sicher**, nur auf eigenen Servern verwenden) |
| `Q`                | abbrechen, die `Wow.exe` bleibt unverändert |
| `ENTER`            | Auswahl übernehmen und weiter               |

Vor der Sicherheitsabfrage zeigt der Patcher **Hinweise** an, gesperrt wird
nichts: wenn ein Ergänzungs-Patch fehlt (z. B. brauchen die erweiterten
Slider-Maxima die CVar-Unlocks), wenn ein Patch einen anderen überflüssig macht
(Warden komplett abschalten ersetzt den RCE-Fix) und wenn gewählte Patches eine
Warnung tragen – mit roter Warnung bei Bann-Gefahr und bei Patches, die auf
öffentlichen Servern oder im Spiel noch ungetestet sind, gelb bei vergrößerter
`Wow.exe` (siehe [Hinweise](#hinweise)).

### Auswahl wird gespeichert

Sobald du die Auswahl mit ENTER übernimmst, speichert der Patcher sie in der
Datei `patcher_selection.ini` neben dem Skript. Beim nächsten Start ist genau
diese Auswahl wieder vorausgewählt – auch wenn du vorher bei der
Sicherheitsabfrage abgebrochen hast.

- Gespeichert wird pro Patch (über eine interne Kennung), nicht pro Nummer.
  Kommen in einer neueren Version Patches hinzu, bleibt deine Auswahl korrekt,
  und die neuen Patches starten mit ihrer Standard-Einstellung.
- Die Datei ist eine einfache Textdatei (`laa=1`, `cache=0`, …) und kann auch
  von Hand bearbeitet werden. Dort stehen auch die eingegebenen Werte der
  Patches mit eigenem Wert – Client-Infos, Sprunghöhe, Doppelsprung
  (`value.clientversion=3.3.6` usw.).
- Auch die Sprache wird dort gemerkt (`language=de` bzw. `en`).
- **Zurücksetzen:** im Menü `R` drücken oder `patcher_selection.ini` löschen –
  dann gilt wieder das Preset „Reforged“ (beim Löschen der Datei werden
  auch Sprache und gemerkte Werte wieder abgefragt).

Das Preset „Reforged“ (Taste `R`) ist das offizielle Preset des
Projekts [Project Reforged](https://projectreforged.github.io/wotlk/),
zusammengestellt von Stormhand, und die Standard-Auswahl. Es enthält nur
sichere Patches (🟢), die Stormhand alle mehrere Stunden auf Warmane getestet
hat – **das Preset ist sicher** und kann auch auf öffentlichen Servern
verwendet werden. Drei davon (Nr. 9, 63 und 64) vergrößern die `Wow.exe`; auf
Warmane war das kein Problem, andere Server können die Dateigröße aber prüfen. Welche Patches
dazugehören, zeigt die Spalte „Reforged“ in der
[Patch-Übersicht](#patch-übersicht); im Skript steht die Liste unter
`$PRESET_REFORGED`.

Das Preset „Billy's_Wow.exe“ (Taste `B`) ist das Patch-Set von Billy Hoyle.
Es ist in `apply_patches.ps1` festgelegt: Jeder Patch hat dort
einen Eintrag `On = $true` (im Preset) bzw. `On = $false` (nicht im Preset).

Es basiert auf Billys `Wow.exe`, die lange auf öffentlichen Servern im Einsatz
war. Einige Patches daraus wurden inzwischen korrigiert, weil sie Abstürze des
Clients oder fehlerhafte Animationen verursachen konnten. In der Übersicht
erkennst du sie am Zusatz „fixed by St0ny“ beim Autor. Die korrigierten Patches
sind im Spiel getestet und funktionieren – **das Preset ist sicher**.

Solltest du trotzdem auf Probleme stoßen, melde dich bitte über ein
[Issue](https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/issues).

Das zweite Preset „St0nys_Wow.exe“ (Taste `S`) ist St0nys eigene Auswahl für
eigene Server. Es enthält auch Patches mit Bann-Gefahr und solche, die die
`Wow.exe` vergrößern – **nur auf eigenen Servern verwenden**. Welche Patches
dazugehören, zeigt die Spalte „St0ny“ in der
[Patch-Übersicht](#patch-übersicht); im Skript steht die Liste unter
`$PRESET_STONY`. **Achtung: Dieses Preset sollte unter keinen Umständen
auf öffentlichen Servern verwendet werden – das führt wahrscheinlich zu einem
Bann!** Der Patcher zeigt das beim Laden mit `S` als gelben Hinweis an.

## Patches ändern oder zurücknehmen

Eingespielte Patches sind nicht endgültig. Starte `patcher.bat` einfach erneut:
Im Menü sind dann genau die Patches angehakt, die gerade in der `Wow.exe`
stecken. Neu angehakte Patches sind mit **(neu)** markiert, abgewählte mit
**(wird zurückgenommen)**. So kannst du beliebig Patches dazunehmen, abwählen
oder Werte ändern (Sprunghöhe, Doppelsprung, Client-Infos). Mit `N` und ENTER
nimmst du alle Patches zurück – danach ist die `Wow.exe` wieder **byte-genau
das Original**.

So funktioniert es:

- **Erster Start:** Die `Wow.exe` muss original sein (SHA256-Prüfung), sonst
  bricht der Patcher ab. Beim Patchen wird das Original als `Wow.exe.ORI`
  gesichert, und jede gepatchte `Wow.exe` bekommt ein [Wasserzeichen](#hinweise).
- **Jeder weitere Start:** Ob die `Wow.exe` mit diesem Patcher gepatcht wurde,
  erkennt er am Wasserzeichen. Fehlt es (und ist die Datei nicht original),
  bricht er ab – etwa bei einer Exe, die mit einem anderen Tool gepatcht wurde.
- **Patchstand ermitteln:** Passt der Hash aus `patcher_state.ini` (dort merkt
  sich der Patcher nach jedem Lauf Hash, Patches, Werte und Original-Bytes),
  geht es über diese Datei – das ist der schnelle Weg. Sonst, z. B. wenn die
  Datei fehlt oder die `Wow.exe` von einem anderen Rechner stammt, prüft der
  Patcher alle Patch-Stellen in der Exe selbst: Welche Patches sind drin, und
  mit welchen Werten (Sprunghöhe, Build-Datum usw.)? Dafür enthält das Skript
  eine kleine Tabelle mit den Original-Bytes an allen Patch-Stellen. Gibt es
  danach nichts zu tun, legt der Patcher die `patcher_state.ini` trotzdem neu
  an, damit der nächste Start wieder den schnellen Weg nimmt.
- **Original wiederherstellen:** Aus der gepatchten Exe baut der Patcher im
  Speicher das Original wieder auf, prüft es per SHA256 und spielt darauf die
  neue Auswahl ein. Klappt das nicht exakt – etwa weil die Exe nach dem
  Patchen noch anderweitig verändert wurde –, bricht er ab.
- Vor dem Schreiben prüft der Patcher außerdem, dass sich das neue Ergebnis
  wieder sauber zum Original zurücknehmen lässt.
- `Wow.exe.ORI` bleibt bei weiteren Läufen unangetastet und ist immer das
  Original. Fehlt es, legt der Patcher es aus dem rekonstruierten Original neu
  an. Zusätzlich sichert er bei jedem weiteren Lauf die bisherige `Wow.exe` als
  `Wow.exe.BAK` – ein Schritt zurück ist also immer möglich.

> [!NOTE]
> Ein Patch mit einem Wert, der genau dem Original entspricht (z. B. die
> Sprunghöhe `-7.9555473`), ändert keine Bytes und wird bei der Prüfung der Exe
> deshalb nicht als eingespielt erkannt – er ist dann ja auch wirkungslos.

## Parameter für den unbeaufsichtigten Betrieb

Alle Parameter sind optional und werden von `patcher.bat` an
`apply_patches.ps1` durchgereicht.

| Parameter              | Bedeutung                                                                   |
|------------------------|-----------------------------------------------------------------------------|
| `-Language de\|en`     | Sprache für diesen Lauf festlegen. Zusammen mit `-Select` bleibt die gemerkte Sprache unverändert; wird die Auswahl im Menü mit ENTER übernommen, wird sie mitgespeichert. |
| `-Select <Auswahl>`    | Auswahlmenü überspringen: `saved` (gespeicherte Auswahl), `reforged` (Preset „Reforged“, auch `default`), `billy` (Preset „Billy's_Wow.exe“), `stony` (Preset „St0nys_Wow.exe“), `all`, `none` (alle Patches zurücknehmen, Original wiederherstellen) oder Nummern/Bereiche wie `"1,3,5-8"`. Die Auswahl ersetzt die Patches in der `Wow.exe` komplett. Mit `-Select` wird die gespeicherte Auswahl nicht verändert. |
| `-Unattended`          | keine Rückfragen und keine Pausen. Ohne `-Language` gilt die gemerkte Sprache bzw. Deutsch, ohne `-Select` die gespeicherte Auswahl bzw. das Preset „Reforged“. |
| `-Path <Datei>`        | eine andere `Wow.exe` als die im Skriptordner patchen                        |

Beispiel:

```bat
patcher.bat -Language de -Select saved -Unattended
```

Exit-Codes: `0` = erfolgreich (oder nichts zu tun), `1` = Fehler, `2` =
abgebrochen (vom Benutzer oder weil keine Eingabe mehr möglich ist).

## Dateien

| Datei               | Zweck |
|---------------------|-------|
| `patcher.bat`       | Startdatei, ruft `apply_patches.ps1` auf |
| `apply_patches.ps1` | Patch-Engine: Sprachwahl, Prüfungen, Auswahlmenü, Backup; liest die EXE einmal, patcht im Speicher, schreibt einmal zurück |
| `README.md`         | Englische Anleitung |
| `README.de.md`      | Diese Datei |
| `PATCHES.de.md`     | Ausführliche Beschreibungen aller Patches |
| `PATCHES.en.md`     | Patch-Beschreibungen auf Englisch |
| `patcher_selection.ini` | Wird beim ersten Start angelegt (gemerkte Sprache) und speichert die übernommene Auswahl samt eingegebenen Werten |
| `patcher_state.ini` | Wird beim Patchen angelegt: Hash der gepatchten `Wow.exe`, eingespielte Patches, Werte und Original-Bytes – beschleunigt den nächsten Start, ist aber nicht zwingend nötig |
| `Wow.exe.ORI`       | Sicherung der originalen `Wow.exe`, angelegt beim ersten Patchen |
| `Wow.exe.BAK`       | Sicherung der bisherigen `Wow.exe` vor dem letzten Lauf |
| `LICENSE`           | MIT-Lizenz |

---

## Patch-Übersicht

Ein Klick auf die Nummer eines Patches springt zu seiner Beschreibung.

<details>
<summary><b>Übersicht aller Patches mit Autor und Preset-Zuordnung anzeigen</b></summary>

#### Was die Kennzeichnungen bedeuten

| Kennzeichnung | Bedeutung | Im Patcher |
|---------------|-----------|------------|
| 🟢 **[sicher]** | Im Spiel getestet und sicher nutzbar. | keine Warnung |
| 🔴 **[unsicher]** | Bestätigte Bann-Gefahr: kann auf vielen Servern zu einem Bann führen. Nur auf Servern nutzen, die das erlauben. | rote Warnung |
| 🟠 **[online ungetestet]** | Nicht auf öffentlichen Servern getestet, mögliche Bann-Gefahr: Niemand kann vorhersagen, wie der Server reagiert. Vorsicht, kann zu Kick/Bann führen. | rote Warnung |
| 🟠 **[ingame ungetestet]** | Die Funktion ist im Spiel noch nicht geprüft: Niemand kann vorhersagen, wie das Spiel reagiert, möglicherweise verbuggt. | rote Warnung |
| 🟠 **[ungetestet]** | Weder online noch ingame getestet. | rote Warnung |
| 🟡 **[Exe wird größer]** | Der Patch hängt eine Sektion an die `Wow.exe` an. Keine sichere Bann-Gefahr, aber ein Risiko: Manche Server prüfen die Dateigröße. | gelber Hinweis |

Ein Patch kann mehrere Kennzeichnungen tragen, z. B. 🟢 **[sicher]** und
🟡 **[Exe wird größer]**. Im Patcher stehen die Warnungen in eckigen
Klammern hinter dem Namen, vor dem Patchen listet er sie noch einmal auf.

#### System & Leistung

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [1](PATCHES.de.md#patch-laa) | 4GB-Patch (Large Address Aware) | 🟢 **[sicher]** | Alastor StrixEfuartus / Kebabstorm / Robinsch | ✅ | ✅ | ✅ |
| [2](PATCHES.de.md#patch-cache) | CACHE-Ordner-Erstellung deaktivieren | 🟢 **[sicher]** | Alastor StrixEfuartus / Kebabstorm | – | – | – |
| [3](PATCHES.de.md#patch-itemcache) | Item-Cache sofort aktualisieren | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [4](PATCHES.de.md#patch-worldcrash) | WorldFrame-Absturzfix (ungültige Dreiecks-Indizes) | 🟠 **[online ungetestet]** | Alyst3r (0x539wowmod) (fixed by St0ny) | – | – | ✅ |
| [5](PATCHES.de.md#patch-timer) | Genauen Timer immer nutzen (Ruckeln beim Drehen behoben) | 🟢 **[sicher]** | St0ny | ✅ | – | ✅ |
| [6](PATCHES.de.md#patch-nothrottle) | Gegenstands- und Namensabfragen nicht drosseln | 🟢 **[sicher]** | tb (ported by St0ny) | – | – | ✅ |
| [7](PATCHES.de.md#patch-mirrorfix) | Mirror-Image-Absturzfix (Speicherleck bei Spiegelbildern) | 🟢 **[sicher]** | tb (ported by St0ny) | ✅ | – | ✅ |
| [8](PATCHES.de.md#patch-wmocube) | Fehlende WMO-Datei: Fehlerwürfel statt ERROR #134 | 🟢 **[sicher]** | Alyst3r (ported by St0ny) | ✅ | – | ✅ |
| [9](PATCHES.de.md#patch-glyphfix) | Schrift-Glyphen-Fix (falsche oder kaputte Zeichen in Texten) | 🟢 **[sicher]**<br>🟡 **[Exe wird größer]** | tb (ported by St0ny) | ✅ | – | ✅ |

#### Sicherheit & Datenschutz

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [10](PATCHES.de.md#patch-rce) | Remote Code Execution Exploit Fix | 🔴 **[unsicher]** | Robinsch | – | – | – |
| [11](PATCHES.de.md#patch-wardenoff) | Warden komplett abschalten, RCE-Fix | 🔴 **[unsicher]** | Robinsch | – | – | ✅ |
| [12](PATCHES.de.md#patch-scandll) | Scan.dll deaktivieren | 🟢 **[sicher]** | Alastor StrixEfuartus | ✅ | – | ✅ |
| [13](PATCHES.de.md#patch-noserverpatch) | Client-Patches vom Server verbieten | 🟢 **[sicher]** | Kebabstorm | ✅ | – | ✅ |
| [14](PATCHES.de.md#patch-nosurvey) | Hardware-Umfragen vom Server verbieten | 🟢 **[sicher]** | Kebabstorm | ✅ | – | ✅ |

#### Login & Verbindung

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [15](PATCHES.de.md#patch-skipbnet) | Battle.net-Login überspringen | 🟢 **[sicher]** | Kebabstorm | ✅ | – | ✅ |
| [16](PATCHES.de.md#patch-skiprdp) | Remote-Desktop-Prüfung überspringen | 🟢 **[sicher]** | Kebabstorm | ✅ | – | ✅ |
| [17](PATCHES.de.md#patch-nohttp) | HTTP-Anfragen an Battle.net deaktivieren | 🟢 **[sicher]** | Kebabstorm | ✅ | – | ✅ |
| [18](PATCHES.de.md#patch-afk) | Idle-Kick nach Character-Autologin verhindern *(wird für Character-Autologin benötigt; AFK- und Idle-Timer bleiben aktiv, [Discord](https://discord.com/channels/858041817043042364/1515439916878663701))* | 🟢 **[sicher]** | St0ny | – | – | ✅ |

#### Modding: Interface, MPQs & Addons

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [19](PATCHES.de.md#patch-glue) | Custom Glue-XML erlauben | 🟢 **[sicher]** | Alastor StrixEfuartus / Kebabstorm (fixed by St0ny) | ✅ | ✅ | ✅ |
| [20](PATCHES.de.md#patch-mpqsig) | Falsch/Nicht signierte MPQs zulassen | 🟢 **[sicher]** | Alastor StrixEfuartus | – | – | ✅ |
| [21](PATCHES.de.md#patch-mpqnames) | Erweiterte MPQ-Namen erlauben | 🟢 **[sicher]** | unbekannt | – | ✅ | ✅ |
| [22](PATCHES.de.md#patch-localdata) | Daten direkt aus dem Data-Ordner laden (ohne MPQ) | 🟢 **[sicher]** | Alastor StrixEfuartus | – | ✅ | ✅ |
| [23](PATCHES.de.md#patch-luaunlock) | LUA Unlock (Zauber, Bewegung, Makros) | 🔴 **[unsicher]** | Alastor StrixEfuartus | – | – | – |
| [24](PATCHES.de.md#patch-luaunlockfull) | LUA Unlock (vollständig): alle geschützten Funktionen freigeben | 🔴 **[unsicher]** | St0ny | – | – | – |
| [25](PATCHES.de.md#patch-keyprop) | Alle Tastatur-Ereignisse an Addons weiterreichen (OnKeyDown) | 🔴 **[unsicher]**<br>🟠 **[ingame ungetestet]** | Alyst3r (0x539wowmod) | – | – | – |
| [26](PATCHES.de.md#patch-globalsv) | Addon-Daten aller Accounts zusammenlegen (SavedVariables) *(gemeinsamer Ordner `WTF\Account\global`)* | 🟠 **[ungetestet]** | St0ny (original by boredatom) | – | – | – |

#### DLL-Loader

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [27](PATCHES.de.md#patch-awesome) | AwesomeWotlkLib.dll Unterstützung aktivieren *(benötigt [awesome_wotlk](https://github.com/noname08662/awesome_wotlk))* | 🟢 **[sicher]** | FrostAtom | ✅ | ✅ | ✅ |
| [28](PATCHES.de.md#patch-wotlkext) | WotLKExtensions.dll Unterstützung aktivieren *(benötigt [WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions))* | 🟢 **[sicher]** | St0ny (original by Alyst3r) | – | – | – |
| [29](PATCHES.de.md#patch-voicedll) | voice.dll beim Start laden (mod-voicechat) [ALPHA] *(Modul noch unfertig, [mod-voicechat](https://github.com/Raz0r1337/mod-voicechat))* | 🟠 **[ungetestet]** | St0ny | – | – | – |

#### Gameplay-Fixes

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [30](PATCHES.de.md#patch-areatrigger) | Area-Trigger-Timer genauer (50 ms statt 100 ms) | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [31](PATCHES.de.md#patch-swing) | Nahkampf-Schwung bei Rechtsklick entfernt | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [32](PATCHES.de.md#patch-npcanim) | NPC-Angriffsanimation beim Drehen unterdrückt | 🟢 **[sicher]** | Robinsch (fixed by St0ny) | ✅ | ✅ | ✅ |
| [33](PATCHES.de.md#patch-spellanim) | Zauber-Animation nach Abbruch repariert | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [34](PATCHES.de.md#patch-ghostattack) | „Geister“-Angriff von NPCs beim Evade behoben | 🟢 **[sicher]** | Robinsch (fixed by St0ny) | ✅ | ✅ | ✅ |
| [35](PATCHES.de.md#patch-naked) | Nackter-Charakter-Bug behoben | 🟢 **[sicher]** | Robinsch (fixed by St0ny) | ✅ | ✅ | ✅ |
| [36](PATCHES.de.md#patch-forcereaction) | Force-Reaction bei /reload erhalten | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [37](PATCHES.de.md#patch-mail) | Neue Post ohne 60 Sekunden Wartezeit | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [38](PATCHES.de.md#patch-deadchat) | Chat-Befehle auch im Tod erlauben | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [39](PATCHES.de.md#patch-follow) | /follow auch bei NPCs erlauben | 🟠 **[online ungetestet]** | St0ny (original by Alastor StrixEfuartus) | – | – | ✅ |
| [40](PATCHES.de.md#patch-level101) | Level 101+ Fix (Spielwert-Tabellen, Barbierstuhl, Grundwerte) | 🟢 **[sicher]** | Alastor StrixEfuartus (fixed by St0ny) | ✅ | – | ✅ |
| [41](PATCHES.de.md#patch-raceclass) | Charaktererstellung: mehr als 10 Klassen (Zufallsklasse) *(für eigene Klassen; Server muss es unterstützen)* | 🔴 **[unsicher]** | Alastor StrixEfuartus / Robinsch | – | – | – |
| [42](PATCHES.de.md#patch-namecheck) | Namensprüfung bei der Charaktererstellung abschalten (z. B. Zahlen im Namen) *(Server muss die Namen ebenfalls erlauben)* | 🔴 **[unsicher]** | Alyst3r (0x539wowmod) (fixed by St0ny) | – | – | – |
| [43](PATCHES.de.md#patch-maxchars) | Max. Charaktere pro Server auf 255 erhöht | 🟢 **[sicher]** | St0ny | – | ✅ | – |
| [44](PATCHES.de.md#patch-customitem) | Custom Item Fix (BETA) v2 *(Custom-Items ohne DBC-Anpassung: Modell, Icon und Item-Typ aus den Serverdaten)* | 🟠 **[ungetestet]** | Kebabstorm (fixed by St0ny) | – | – | – |
| [45](PATCHES.de.md#patch-climb) | Steigwinkel-Begrenzung aufheben (jeden Hang hochlaufen) | 🔴 **[unsicher]** | Alastor StrixEfuartus | – | – | – |
| [46](PATCHES.de.md#patch-jump) | Sprunghöhe ändern (Original -7.9555473) *(fragt den Wert ab)* | 🔴 **[unsicher]** | Alastor StrixEfuartus | – | – | – |
| [47](PATCHES.de.md#patch-airforward) | Im Sprung vorwärts/rückwärts steuern | 🔴 **[unsicher]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | ✅ |
| [48](PATCHES.de.md#patch-airlateral) | Im Sprung seitwärts steuern | 🔴 **[unsicher]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | ✅ |
| [49](PATCHES.de.md#patch-airturn) | Im Sprung drehen ändert die Flugrichtung | 🔴 **[unsicher]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | ✅ |
| [50](PATCHES.de.md#patch-doublejump) | Doppelsprung (weitere Sprünge in der Luft) *(fragt den Wert ab)* | 🔴 **[unsicher]**<br>🟡 **[Exe wird größer]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | ✅ |
| [51](PATCHES.de.md#patch-noammo) | Fernkampf ohne Munition *(Server muss mitspielen, sonst meldet er weiter „Keine Munition“)* | 🟠 **[ungetestet]** | Alyst3r (ported by St0ny) | – | – | – |

#### Grafik & Sichtweite

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [52](PATCHES.de.md#patch-farclip) | CVar farclip unlock (max 10000) | 🟢 **[sicher]** | Alastor StrixEfuartus | ✅ | ✅ | ✅ |
| [53](PATCHES.de.md#patch-horizon) | CVar horizonFarclipScale unlock (max 12) | 🟢 **[sicher]** | St0ny | ✅ | ✅ | ✅ |
| [54](PATCHES.de.md#patch-envdetail) | CVar environmentDetail unlock (kein Limit statt 1.5) | 🟢 **[sicher]** | St0ny | ✅ | ✅ | ✅ |
| [55](PATCHES.de.md#patch-grounddist) | CVar groundEffectDist unlock (max 3166 statt 140) | 🟢 **[sicher]** | unbekannt | ✅ | ✅ | ✅ |
| [56](PATCHES.de.md#patch-sliders) | Grafikoptionen: Slider-Maxima erweitern | 🟢 **[sicher]** | St0ny | ✅ | – | ✅ |
| [57](PATCHES.de.md#patch-goscale) | GameObject Sichtweite: Cat 0 und Cat 4 auf environmentDetail reagieren lassen | 🟢 **[sicher]** | St0ny | ✅ | – | ✅ |
| [58](PATCHES.de.md#patch-cat0) | GameObject Sichtweite: Cat 0 von 30 auf 50 Yards *(kostet Leistung, mehr Kleinkram sichtbar)* | 🟢 **[sicher]** | St0ny | – | – | ✅ |
| [59](PATCHES.de.md#patch-occluder) | Occluder Fix für Stormwind (Open Azeroth) | 🟢 **[sicher]** | Robinsch | ✅ | – | ✅ |
| [60](PATCHES.de.md#patch-bluemoon) | Blauer Mond am Nachthimmel reaktiviert | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [61](PATCHES.de.md#patch-notransparency) | Keine Transparenz beim Heranzoomen | 🟢 **[sicher]** | Alastor StrixEfuartus | ✅ | ✅ | ✅ |
| [62](PATCHES.de.md#patch-nofade) | Kein Ausblenden für NPCs mit Flag DO_NOT_FADE_IN *(Server muss das Flag setzen)* | 🟠 **[ungetestet]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | – |
| [63](PATCHES.de.md#patch-hdportraits) | HD Unit-Frame Portraits: Renderauflösung 256 statt 64 Pixel | 🟢 **[sicher]**<br>🟡 **[Exe wird größer]** | St0ny (original by Badgermilk0) | ✅ | – | – |
| [64](PATCHES.de.md#patch-iconsnap) | Icons im Text pixelgenau (scharf statt verschwommen) | 🟢 **[sicher]**<br>🟡 **[Exe wird größer]** | tb (ported by St0ny) | ✅ | – | ✅ |
| [65](PATCHES.de.md#patch-outline) | Umrandung für Ziel und Mouseover (Proof of Concept) *(nur gxApi d3d9)* | 🟠 **[ungetestet]**<br>🟡 **[Exe wird größer]** | St0ny | – | – | – |

#### Interface & Komfort

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [66](PATCHES.de.md#patch-tracker) | Quest-Tracker automatisch sortieren | 🟢 **[sicher]** | unbekannt | ✅ | – | ✅ |
| [67](PATCHES.de.md#patch-worldmap) | Erweiterte Weltkarte standardmäßig aktiv | 🟢 **[sicher]** | unbekannt | ✅ | – | ✅ |
| [68](PATCHES.de.md#patch-castbars) | Cast Bars auf allen Frames | 🟢 **[sicher]** | Kebabstorm | ✅ | ✅ | ✅ |
| [69](PATCHES.de.md#patch-emblems) | Retail-Gildenembleme: Auswahl von 170 auf 196 erweitert *(benötigt [Patch-G](https://discord.com/channels/407664041016688662/1541873346608889936))* | 🟠 **[online ungetestet]** | MacWarrior | – | – | ✅ |
| [70](PATCHES.de.md#patch-flash) | FlashWindow Patch *(benötigt [FlashWindow-Addon](https://github.com/noname08662/awesome_wotlk/tree/main/addons/Flash))* | 🟢 **[sicher]** | Kebabstorm | – | ✅ | ✅ |
| [71](PATCHES.de.md#patch-charrandom) | Charaktererstellung: Aussehen nicht automatisch auswürfeln | 🟢 **[sicher]** | Alyst3r (0x539wowmod) | ✅ | – | – |
| [72](PATCHES.de.md#patch-lootopen) | Lootfenster bleibt beim Laufen offen | 🟠 **[online ungetestet]** | tb (ported by St0ny) | – | – | – |
| [73](PATCHES.de.md#patch-showlevel) | Echtes Level statt „??“ bei Gegnern ab 10 Level über dir *(Bosse zeigen weiter „??“ – dafür Nr. 74)* | 🟠 **[online ungetestet]** | tb (ported by St0ny) | – | – | – |
| [74](PATCHES.de.md#patch-showlevelboss) | Echtes Level auch bei Bossen statt „??“ (Erweiterung zu Nr. 73) | 🟠 **[online ungetestet]** | St0ny | – | – | – |
| [75](PATCHES.de.md#patch-holdrepeat) | Aktionstasten gedrückt halten zum Wiederholen | 🔴 **[unsicher]**<br>🟡 **[Exe wird größer]** | tb (ported by St0ny) | – | – | ✅ |
| [76](PATCHES.de.md#patch-bubblerange) | Sprechblasen-Reichweite erhöhen (Original 25 Meter) *(fragt den Wert ab)* | 🟢 **[sicher]** | St0ny | ✅ | – | ✅ |

#### Fenster, Maus & Kamera

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [77](PATCHES.de.md#patch-window) | Fenstermodus als Standard setzen *(startet als kleines Fenster mitten auf dem Desktop – maximiert nur zusammen mit Nr. 78)* | 🟢 **[sicher]** | St0ny | ✅ | – | ✅ |
| [78](PATCHES.de.md#patch-maximize) | Fenstermodus maximiert als Standard setzen *(wirkt nur zusammen mit Nr. 77)* | 🟢 **[sicher]** | St0ny | ✅ | – | ✅ |
| [79](PATCHES.de.md#patch-windowfix) | Kein schwarzer Bildschirm beim Wechsel in den Fenstermodus | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [80](PATCHES.de.md#patch-mouse) | Mausflackern / Kamerasprünge Fix | 🟢 **[sicher]** | Robinsch | ✅ | ✅ | ✅ |
| [81](PATCHES.de.md#patch-camera) | CameraReforged [BETA]: Kamerahöhe und Zoom-Grenzen *(Schulterversatz noch ohne Wirkung)* | 🟠 **[online ungetestet]**<br>🟡 **[Exe wird größer]** | Stormhand (fixed by St0ny) | – | – | – |

#### Sound

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [82](PATCHES.de.md#patch-sound) | Sound-Einstellungen optimieren *(benötigt [OpenAL](https://github.com/kcat/openal-soft), sonst wirken die Einstellungen nicht)* | 🟢 **[sicher]** | St0ny | ✅ | – | ✅ |

#### Client-Infos: Version, Build, Titel, Datum, Icon

| Nr. | Patch | Status | Autor | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [83](PATCHES.de.md#patch-clientversion) | Client-Version ändern (Original 3.3.5) *(fragt den Wert ab)* | 🔴 **[unsicher]** | MacWarrior | – | – | – |
| [84](PATCHES.de.md#patch-clientbuild) | Build-Nummer ändern (Original 12340) *(fragt den Wert ab)* | 🔴 **[unsicher]** | MacWarrior | – | – | – |
| [85](PATCHES.de.md#patch-clienttitle) | Programmtitel ändern (Dateieigenschaften und Fenstertitel) *(fragt den Wert ab)* | 🔴 **[unsicher]** | MacWarrior (fixed by St0ny) | – | – | – |
| [86](PATCHES.de.md#patch-clientdate) | Build-Datum ändern (Original Jun 24 2010) *(fragt den Wert ab)* | 🔴 **[unsicher]** | St0ny (original by MacWarrior) | – | – | – |
| [87](PATCHES.de.md#patch-clienticon) | Programm-Icon ändern (Symbol der Wow.exe) *(fragt den Wert ab)* | 🔴 **[unsicher]** | St0ny (original by MacWarrior) | – | – | – |

</details>

> [!NOTE]
> **Urheber gesucht:** Bei Patches ohne Eintrag in der Spalte „Autor“ ist der
> Urheber noch nicht bekannt. Wenn du weißt, von wem einer dieser Patches
> stammt, schreib es bitte als [Issue](https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/issues) – dann wird es nachgetragen.

---

## Patch-Beschreibungen

Die ausführlichen Beschreibungen aller Patches stehen in einer eigenen Datei:
**[PATCHES.de.md](PATCHES.de.md)**. In der [Patch-Übersicht](#patch-übersicht) führt
ein Klick auf die Nummer eines Patches direkt zu seiner Beschreibung.

---

## Hinweise

- **Warnungen:** Jeder Patch hat eine einheitliche Einstufung. In der
  [Patch-Übersicht](#patch-übersicht) steht sie in der Spalte „Status“, im Patcher in
  eckigen Klammern, und vor der Sicherheitsabfrage listet der Patcher die
  gewählten Patches mit Warnung noch einmal auf:
  - 🟢 **sicher** – im Spiel getestet, im Patcher ohne Warnung.
  - 🔴 **unsicher** – Bann-Gefahr, kann auf vielen Servern zu einem Bann führen: Nr. 10,
    11, 23–25, 41, 42, 45–50, 75 und 83–87 (rote Warnung).
  - 🟠 **online ungetestet** – nicht auf öffentlichen Servern getestet, mögliche Bann-Gefahr, Vorsicht,
    kann zu Kick/Bann führen: Nr. 4, 26, 29, 39, 44, 51, 62, 65, 69, 72–74 und 81
    (rote Warnung).
  - 🟠 **ingame ungetestet** – die Funktion ist im Spiel noch nicht geprüft,
    möglicherweise verbuggt: Nr. 25, 26, 29, 44, 51, 62 und 65 (rote Warnung).
  - 🟡 **Exe wird größer** – diese Patches hängen eine Sektion an die `Wow.exe` an:
    Nr. 9, 50, 63–65, 75 und 81. Das ist keine sichere Bann-Gefahr,
    aber ein Risiko: Manche Server prüfen die Dateigröße (gelber Hinweis). Alle
    anderen Patches ändern die Dateigröße nicht.
- **Signatur:** Die originale `Wow.exe` ist von Blizzard digital signiert. Jeder
  Patch macht diese Signatur ungültig. Windows warnt deshalb wahrscheinlich
  beim Start vor einer nicht signierten, möglicherweise schädlichen App; mit
  „Weitere Informationen“ → „Trotzdem ausführen“ startet WoW ganz normal. Eine
  neue Signatur, der Windows vertraut, gibt es nur von Zertifizierungsstellen
  mit Identitätsprüfung – für eine veränderte Blizzard-Datei bekommt man sie
  nicht. Die Patches, die eine Sektion anhängen (Nr. 9, 50, 63–65, 75 und 81), entfernen
  zusätzlich den Verweis auf die Signatur im Header: Die neue Sektion liegt hinter der
  Signatur, und manche Werkzeuge würden die Datei sonst als beschädigt melden.
  Die Signatur-Bytes selbst bleiben unangetastet, die Rücknahme stellt das
  Original samt Signatur wieder her. Eine Download-Markierung („Diese Datei
  stammt von einem anderen Computer“) entfernt der Patcher unter Windows nach
  dem Schreiben von der `Wow.exe`, wie das Häkchen „Zulassen“ in den
  Dateieigenschaften.
- **Wasserzeichen:** Jede gepatchte `Wow.exe` enthält den Text
  `Patched with St0nys AIO WoW.exe Patcher by St0ny (Raz0r1337) - https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher`.
  Daran erkennt der Patcher eine `Wow.exe` eindeutig als seine eigene: So
  vermischt er nie seine Patches mit denen anderer Patcher, und er kann seinen
  Patchstand auch dann aus der Exe auslesen, wenn `patcher_state.ini` gelöscht
  wurde. Der Text steht im ungenutzten Füllbereich hinter der `.tls`-Sektion
  (Datei-Offset `0x72DE20`), wird nie in den Speicher geladen und ändert die
  Dateigröße nicht. Beim Zurücknehmen aller Patches verschwindet er wieder.
  Nebeneffekt: Man kann jederzeit nachsehen, ob eine `Wow.exe` mit diesem
  Patcher erstellt wurde – z. B. per Hex-Editor oder in der Eingabeaufforderung
  mit `findstr /m /c:"St0nys AIO" Wow.exe` (gibt den Dateinamen aus, wenn er drin
  ist).
- **Original wiederherstellen:** Patcher starten, `N` und ENTER drücken – mit
  oder ohne `patcher_state.ini`. Alternativ gepatchte `Wow.exe` löschen und
  `Wow.exe.ORI` in `Wow.exe` umbenennen. `Wow.exe.BAK` ist dagegen die `Wow.exe`
  von vor dem letzten Lauf.
- **Für Entwickler:** Die Original-Byte-Tabelle im Skript wird mit
  `apply_patches.ps1 -BuildTable -Path <originale Wow.exe>` neu erzeugt. Das ist
  nach jeder Änderung an einem Patch nötig; passt sie nicht mehr, weist der
  Patcher nach dem Patchen darauf hin.
- Nutzung auf eigene Gefahr. Dieses Projekt steht in keiner Verbindung zu
  Blizzard Entertainment.

## Danksagung

- Ein ganz besonderer Dank geht an **Billy Hoyle** – für all seine Hilfe, Tipps,
  Expertise und Tests in den letzten Monaten und für die Unterstützung beim
  Zusammentragen der Patches. Sein Patch-Set steckt als Preset
  „Billy's_Wow.exe“ in diesem Patcher.
- Danke auch an **MacWarrior**, der ebenfalls beim Zusammentragen der Patches
  geholfen und einige eigene Patches beigesteuert hat.
- Danke auch an **Stormhand** für die Erlaubnis, seinen CameraReforged-Patch
  einzubauen. Das offizielle Preset seines Projekts
  [Project Reforged](https://projectreforged.github.io/wotlk/) steckt als Preset
  „Reforged“ in diesem Patcher und ist die Standard-Auswahl.
- Ein großes Dankeschön an **Stormhand**, **MacWarrior** und **Billy Hoyle** für
  die vielen Tests im Spiel – und an Stormhand ganz besonders dafür, den eigenen
  Warmane-Account riskiert zu haben, um herauszufinden, welche Patches „sicher“
  nutzbar sind. 😄
- Danke an **Moroes**, der den Patch [#26](PATCHES.de.md#patch-globalsv)
  aufgespürt und mir zugespielt hat.
- Und natürlich danke an alle Autoren der Patches, die in der
  [Patch-Übersicht](#patch-übersicht) genannt sind.

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).
Copyright (c) 2026 St0ny (Raz0r1337).

Kurz gesagt: Jeder darf den Patcher nutzen, verändern und weitergeben – auch in
eigenen Projekten –, solange der Copyright-Hinweis und der Lizenztext erhalten
bleiben (Namensnennung).

# Patch-Beschreibungen

🇩🇪 Deutsch | [🇬🇧 English](PATCHES.en.md)

Ausführliche Beschreibungen aller Patches des
[St0nys-AIO-WoW-EXE-Patcher](README.de.md). Die Übersicht mit Autoren und
Preset-Zuordnung steht in der [README](README.de.md#patch-übersicht). Dort
steht auch, was die Kennzeichnungen hinter den Namen bedeuten, z. B.
🔴 **[unsicher]** oder 🟡 **[sicher - Exe wird größer]**.

- [System & Leistung](#system--leistung)
- [Sicherheit & Datenschutz](#sicherheit--datenschutz)
- [Login & Verbindung](#login--verbindung)
- [Modding: Interface, MPQs & Addons](#modding-interface-mpqs--addons)
- [DLL-Loader](#dll-loader)
- [Gameplay-Fixes](#gameplay-fixes)
- [Grafik & Sichtweite](#grafik--sichtweite)
- [Interface & Komfort](#interface--komfort)
- [Fenster, Maus & Kamera](#fenster-maus--kamera)
- [Sound](#sound)
- [Client-Infos: Version, Build, Titel, Datum, Icon](#client-infos-version-build-titel-datum-icon)

## System & Leistung

<a id="patch-laa"></a>
**4GB-Patch (Large Address Aware)** *(Nr. 1, Autor: Alastor StrixEfuartus / Kebabstorm / Robinsch)* 🟢 **[sicher]**

Ermöglicht der `Wow.exe`, bis zu 4 GB RAM zu nutzen statt der
standardmäßigen 2-GB-Grenze für 32-Bit-Anwendungen.

<a id="patch-cache"></a>
**CACHE-Ordner-Erstellung deaktivieren** *(Nr. 2, Autor: Alastor StrixEfuartus / Kebabstorm)* 🟢 **[sicher]**

Verhindert, dass der Client automatisch einen `CACHE`-Ordner anlegt.

<a id="patch-itemcache"></a>
**Item-Cache sofort aktualisieren** *(Nr. 3, Autor: Robinsch)* 🟢 **[sicher]**

Entfernt die 30-Sekunden-Verzögerung beim Aktualisieren des Item-Caches.
Änderungen an Items werden sofort sichtbar.

<a id="patch-worldcrash"></a>
**WorldFrame-Absturzfix (ungültige Dreiecks-Indizes)** *(Nr. 4, Autor: Alyst3r (0x539wowmod) (fixed by St0ny))* 🔴 **[unsicher]**

Verhindert einen Absturz in einer Funktion der Weltdarstellung (VA `0x81D510`).
Sie läuft über Dreiecke aus je drei Vertex-Indizes und rechnet „Index minus
Basis“ in eine Speicheradresse um. Ist ein Index kleiner als die Basis, zeigt
die Adresse vor den Puffer und der Client stürzt ab. Der Patch prüft vorher die
drei Indizes des ersten Dreiecks und überspringt die Funktion in diesem Fall.
Gegenüber dem Original sind die drei Sprungweiten korrigiert und der Code ist
kürzer.

> [!NOTE]
> Der Code liegt in der freien Lücke am Ende von `.text`, die auch Nr. 63 nutzt.
> Beide passen zusammen hinein, die Dateigröße ändert sich nicht.

> [!NOTE]
> Ein heuristischer Fix, wie ihn auch der Autor nennt: Geprüft wird nur das erste
> Dreieck jedes Aufrufs. Er stört nicht, wenn alles stimmt, fängt aber nicht jeden
> denkbaren Fall ab.

<a id="patch-timer"></a>
**Precise Timer Fix (behebt das Ruckeln beim Drehen des Charakters)** *(Nr. 5, Autor: St0ny)* 🟢 **[sicher]**

Behebt einen alten Blizzard-Fehler: Dreht man den Charakter, ruckelt sich der
Unterkörper in die neue Richtung, statt flüssig nachzudrehen – mal direkt nach
dem Start, mal gar nicht.

Beim Start wählt der Client seine Zeitquelle. Dazu vergleicht er 250 ms lang
den genauen Timer (QueryPerformanceCounter) mit dem groben Windows-Timer
(GetTickCount). Weichen beide um 5 ms oder mehr voneinander ab – das reicht
schon, wenn ein Treiber den Thread einmal kurz aufhält –, nutzt der Client für
die ganze Sitzung GetTickCount. Der zählt nur in Schritten von etwa 16 ms.

Beim Drehen verdreht der Client zuerst Oberkörper und Kopf und zieht den
Unterkörper dann nach. Wie weit, hängt von der Zeit seit der letzten
Richtungsänderung ab – meist nur wenige Millisekunden. Mit dem groben Timer ist
diese Zeit fast immer 0 und springt dann auf 16 ms: Der Unterkörper bleibt
stehen und springt dann ein großes Stück weiter.

Der Patch lässt den 250-ms-Vergleich weg (bedingter Sprung → fester Sprung bei
VA `0x86AC8E`). Ist der genaue Timer vorhanden, nutzt der Client ihn damit
immer. Erhalten bleiben die Prüfung, ob der genaue Timer auf allen CPU-Kernen
vorwärts läuft, und die CVar `timingMethod`: Wer `SET timingMethod "1"` in der
`Config.wtf` stehen hat, bekommt weiterhin GetTickCount. Nebenbei startet der
Client etwa eine Viertelsekunde schneller.

> [!TIP]
> Ob der grobe Timer gerade aktiv ist, zeigt im Spiel
> `/run print(GetCVar("timingTestError"))`: `3` heißt, der Test ist beim Start
> gescheitert. Ohne Patch hilft auch `SET timingMethod "2"` in der `Config.wtf`.

<a id="patch-nothrottle"></a>
**Gegenstands- und Namensabfragen nicht drosseln** *(Nr. 6, Autor: tb (ported by St0ny))* 🟢 **[sicher]**

Kennt der Client einen Gegenstand, eine Kreatur, eine Quest oder einen Namen
noch nicht, fragt er beim Server nach. Zwei dieser Abfragen begrenzt der
Client selbst: Gegenstands-Infos auf 512 und Spielernamen auf 256 pro Minute.
Ist die Grenze erreicht, warten weitere Anfragen in einer Schlange – deshalb
stehen z. B. beim ersten Öffnen voller Taschen, der Bank oder des Auktionshauses
eine Weile „Lade Gegenstandsinformationen“ oder leere Tooltips, und in vollen
Städten oder großen Schlachtzügen zeigen Namen kurz „Unbekannt“. Der Patch hebt
diese beiden Grenzen auf (0 = unbegrenzt, je ein Byte in den Konstruktoren von
`itemcache` und `namecache`), die Infos kommen sofort. Alle anderen Abfragen
(Kreaturen, Quests, Gilden …) sind schon im Original unbegrenzt – mit dem Patch
sind damit alle 15 Datenbank-Abfragen des Clients ungedrosselt.

> [!NOTE]
> Der Client schickt dadurch mehr Anfragen auf einmal. Server mit
> Flood-Schutz könnten das bemängeln – auf öffentlichen Servern also erst
> testen.

<a id="patch-mirrorfix"></a>
**Mirror-Image-Absturzfix (Speicherleck bei Spiegelbildern)** *(Nr. 7, Autor: tb (ported by St0ny))* 🟢 **[sicher]**

Behebt einen Blizzard-Fehler: Bekommt eine Einheit, die das Aussehen eines
Spielers kopiert (Spiegelbilder, auf manchen Servern auch Spieler-Kopien als
Kreaturen), neue Aussehensdaten, legt der Client eine neue
Charakter-Komponente an, ohne die alte freizugeben. Die alte bleibt mit ihrer
Textur am Grafikgerät hängen – beim Beenden greift der Client dann auf schon
freigegebenen Speicher zu und stürzt ab.

Der Patch gibt eine noch vorhandene alte Komponente vorher mit der
Original-Funktion frei. Der kleine Zusatzcode (29 Byte) liegt in einer
ungenutzten Funktion der Exe – die Dateigröße ändert sich nicht.

<a id="patch-wmocube"></a>
**Fehlende WMO-Datei: Fehlerwürfel statt ERROR #134** *(Nr. 8, Autor: Alyst3r (ported by St0ny))* 🟢 **[sicher]**

Fehlt eine WMO-Datei (große Weltobjekte wie Gebäude oder Dungeons, z. B. in
eigenen MPQs), bricht der Client mit „ERROR #134 Fatal Condition:
CMap::SafeOpen() failed“ ab. Mit dem Patch lädt er stattdessen den
Fehlerwürfel `Spells\ErrorCube.mdx` – wie in WotLK-Extensions, wo das fest in
der DLL steckt. Die Änderung passt in die Original-Funktion, die Dateigröße
ändert sich nicht.

<a id="patch-glyphfix"></a>
**Schrift-Glyphen-Fix (falsche oder kaputte Zeichen in Texten)** *(Nr. 9, Autor: tb (ported by St0ny))* 🟡 **[sicher - Exe wird größer]**

Behebt Blizzard-Fehler im Glyphen-Cache, der die gerenderten Schriftzeichen
auf Textur-Seiten ablegt: Texte (vor allem Zahlen, Schaden und Chat) zeigen
sonst zeitweise falsche, abgeschnittene oder fremde Zeichen, besonders wenn
viele verschiedene Zeichen und Schriftgrößen gleichzeitig zu sehen sind.

- Beim Einfügen eines Zeichens wird die breiteste freie Lücke einer Zeile
  neu berechnet – das Original aktualisiert diesen Wert nie.
- Wird eine Seite verdrängt, merken sich die betroffenen Texte das und
  werden vor dem Zeichnen komplett neu aufgebaut (bis zu vier Durchgänge,
  falls der Neuaufbau weitere Texte verdrängt).
- Beim Löschen eines Textes werden auch seine Seiten-Merker gelöscht.
- Vor dem Hochladen einer neuen Seite wird der Upload-Puffer geleert, damit
  keine Reste alter Zeichen mitkommen.

Das entspricht dem Glyphen-Fix aus WotLK-Extensions (Fork von tb), dort
per DLL. Hier stecken die vier Hooks in einer eigenen Sektion (`.glyph`,
223 Byte), eine Funktion wird an Ort und Stelle neu geschrieben.

> [!NOTE]
> Verträgt sich mit awesome_wotlk: Dessen MSDF-Schriften hängen sich an
> andere Stellen derselben Funktionen oder setzen auf die neu geschriebene
> Funktion auf.

## Sicherheit & Datenschutz

<a id="patch-rce"></a>
**Remote Code Execution Exploit Fix** *(Nr. 10, Autor: Robinsch)* 🔴 **[unsicher]**

Schließt eine Sicherheitslücke, die Remote-Code-Ausführung über manipulierte
Pakete ermöglichen konnte: Die Sektion `.zdata` verliert ihr Ausführungsrecht,
und Warden-Module werden nicht mehr aus dem lokalen Cache geladen. Warden selbst
läuft weiter.

> [!WARNING]
> Öffentliche Server können die Änderung über Warden erkennen – auf
> öffentlichen Servern besteht Bann-Gefahr.

> [!NOTE]
> „Warden komplett abschalten“ (Nr. 11) schließt die Lücke ebenfalls und macht
> diesen Patch überflüssig. Wählst du beide, weist der Patcher darauf hin;
> schaden tun sie zusammen nicht.

<a id="patch-wardenoff"></a>
**Warden komplett abschalten, RCE-Fix** *(Nr. 11, Autor: Robinsch)* 🔴 **[unsicher]**

Der Client verwirft alle Warden-Pakete des Servers (`SMSG_WARDEN_DATA`).
Warden-Module sind Code, den der Server im Client ausführen lässt – mit diesem
Patch ist das überhaupt nicht mehr möglich, auch nicht über künftige Tricks.
Macht den RCE-Fix (Nr. 10) überflüssig; beide zusammen schaden nicht, der
Patcher weist dann nur darauf hin.

> [!WARNING]
> Der Client antwortet danach nicht mehr auf Warden. Server mit aktivem Warden
> (z. B. AzerothCore oder TrinityCore in der Standardeinstellung) können dich
> deshalb kicken. Auf öffentlichen Servern besteht außerdem Bann-Gefahr.

<a id="patch-scandll"></a>
**Scan.dll deaktivieren** *(Nr. 12, Autor: Alastor StrixEfuartus)* 🟢 **[sicher]**

Verhindert das Laden der `Scan.dll`, die der Login-Server per „Scan“-Befehl
nachladen kann (ein Prüfmodul des Login-Servers, unabhängig von Warden): Aus
`.\Scan.dll` und `.\Scan.dll.new` wird `.\||an.dll` – `|` ist in Dateinamen
verboten, das Laden schlägt damit garantiert fehl.

<a id="patch-noserverpatch"></a>
**Client-Patches vom Server verbieten** *(Nr. 13, Autor: Kebabstorm)* 🟢 **[sicher]**

Der Server kann dem Client keine Patch-Dateien mehr schicken und installieren
lassen.

<a id="patch-nosurvey"></a>
**Hardware-Umfragen vom Server verbieten** *(Nr. 14, Autor: Kebabstorm)* 🟢 **[sicher]**

Der Server kann keine Hardware-Umfrage (Informationen über deinen PC) mehr beim
Client anfordern.

## Login & Verbindung

<a id="patch-skipbnet"></a>
**Battle.net-Login überspringen** *(Nr. 15, Autor: Kebabstorm)* 🟢 **[sicher]**

Der Client überspringt den Battle.net-Login-Schritt und nutzt direkt den
klassischen Login.

<a id="patch-skiprdp"></a>
**Remote-Desktop-Prüfung überspringen** *(Nr. 16, Autor: Kebabstorm)* 🟢 **[sicher]**

Der Client prüft nicht mehr, ob er über eine Remote-Desktop-Verbindung läuft –
WoW lässt sich damit z. B. per RDP spielen.

<a id="patch-nohttp"></a>
**HTTP-Anfragen an Battle.net deaktivieren** *(Nr. 17, Autor: Kebabstorm)* 🟢 **[sicher]**

Der Client ruft keine News, Hilfe-Artikel und Nutzungsbedingungen mehr von
Blizzards Servern ab – die gibt es für 3.3.5 ohnehin nicht mehr.

<a id="patch-afk"></a>
**CharAutoLogin Idle-Kick Fix** *(Nr. 18, Autor: St0ny)* 🟢 **[sicher]**

Nach einem Autologin ohne jede Tastatur- oder Mauseingabe steht der
Zeitstempel der letzten Eingabe noch auf 0 – der Client hält den Spieler sofort
für untätig und kickt ihn (CharAutoLogin-Bug). Der Patch setzt den Zeitstempel
beim ersten Durchlauf auf „jetzt“, wenn er noch leer ist, und entfernt einen
Fatal-Error-Check, der dabei auslösen kann. Die eigentlichen Timer bleiben
unverändert: AFK-Status nach 5 Minuten, Logout nach 30 Minuten ohne Eingabe.
**Wird für Character-Autologin benötigt** – Details im [Discord](https://discord.com/channels/858041817043042364/1515439916878663701).

## Modding: Interface, MPQs & Addons

<a id="patch-glue"></a>
**Custom Glue-XML erlauben** *(Nr. 19, Autor: Alastor StrixEfuartus / Kebabstorm (fixed by St0ny))* 🟢 **[sicher]**

Ermöglicht Änderungen am Login- und Charakterauswahl-Bildschirm durch eigene
XML/Lua-Dateien (Glue-Screen-Modding): Die Signaturprüfung der Interface-Dateien
meldet immer „gültig“, und lokale Ordner `Interface\GlueXML` und
`Interface\FrameXML` werden nicht mehr in `*.old` umbenannt.

> [!NOTE]
> Nebenwirkung, die jede Fassung dieses Patches hat: Auch Addons ohne
> Signaturdatei gelten damit als „sicher“ (wie Blizzard-Code) und dürfen
> geschützte Funktionen aufrufen – in der Wirkung ähnlich dem LUA Unlock
> (Nr. 23). Server mit Anti-Cheat können das genauso werten.

Die verbreitete Fassung (Alastor/Kebabstorm) läuft bei fehlender Signaturdatei
mit uninitialisierten Variablen weiter und gibt dabei einen Zeiger ins Nichts
frei (undefiniertes Verhalten). Hier gibt der Fehlerausgang stattdessen direkt
„gültig“ zurück – gleiche Wirkung, ohne wilden Speicherzugriff.

<a id="patch-mpqsig"></a>
**Falsch/Nicht signierte MPQs zulassen** *(Nr. 20, Autor: Alastor StrixEfuartus)* 🟢 **[sicher]**

Die Signaturprüfung für MPQ-Archive meldet immer „gültig“. Der Client prüft
damit nur Archive, die der Server schickt: `wow-patch.mpq` (Client-Patch vom
Server) und `Cache\Survey.mpq` (Hardware-Umfrage). Die normalen `Data\*.MPQ`
lädt der Client ohnehin ohne Signaturprüfung – für eigene Patch-MPQs ist dieser
Patch also nicht nötig. Zusammen mit Nr. 13 und Nr. 14 hat er keine Wirkung mehr,
weil beide Wege dann gar nicht erst laufen.

<a id="patch-mpqnames"></a>
**Erweiterte MPQ-Namen erlauben** *(Nr. 21)* 🟢 **[sicher]**

Ermöglicht die Nutzung von Wildcard-Namen für MPQ-Archive
(`patch-*.MPQ` und `patch-locale-*.MPQ`).

<a id="patch-localdata"></a>
**Daten direkt aus dem Data-Ordner laden (ohne MPQ)** *(Nr. 22, Autor: Alastor StrixEfuartus)* 🟢 **[sicher]**

Der Client liest Dateien direkt aus dem Data-Ordner, ohne dass sie in ein MPQ
gepackt werden müssen – z. B. `Data\DBFilesClient\ItemDisplayInfo.dbc`.
Praktisch für Modder.

<a id="patch-luaunlock"></a>
**LUA Unlock (Zauber, Bewegung, Makros)** *(Nr. 23, Autor: Alastor StrixEfuartus)* 🔴 **[unsicher]**

Addons und Makros dürfen geschützte Funktionen aufrufen: Bewegungsfunktionen
(`MoveForwardStart`, `TurnLeftStart`, …), `CastSpellByName`, `CastSpell`,
`UseAction`, `PetAttack`, `RunMacro`/`RunMacroText` und die
GM-Ticket-Funktionen. Nicht freigegeben, weil sie eigene Prüfungen im Code
haben: `TargetUnit`, `FocusUnit`, `InteractUnit`, `ReloadUI`; `AttackTarget`
meldet weiterhin einen Fehler. Diese und alle übrigen gibt Nr. 24 frei.

> [!WARNING]
> Das ermöglicht Automatisierung. Server mit Anti-Cheat können das als Botting
> werten – das kann zu einem Bann führen.

<a id="patch-luaunlockfull"></a>
**LUA Unlock (vollständig): alle geschützten Funktionen freigeben** *(Nr. 24, Autor: St0ny)* 🔴 **[unsicher]**

Erweitert Nr. 23 auf alle geschützten Funktionen. Die zentrale Schutzprüfung
des Clients kennt 24 Schutztypen in drei Klassen (immer verboten, nur nach
einem Hardware-Ereignis erlaubt, nur bei erlaubten Attribut-Änderungen) – sie
meldet mit diesem Patch für alle „erlaubt“. Zusätzlich werden die eigenen
Prüfungen der Funktionen umgangen, die nicht über diese zentrale Stelle laufen:
`TargetUnit`, `AssistUnit`, `TargetLastTarget`, `TargetNearest…`,
`TargetDirection…`, `AttackTarget`, `StartAttack`, `FocusUnit`, `ClearFocus`,
`InteractUnit`, `ReloadUI`, `UninviteUnit`, `CancelLogout`, die Pet-Befehle
(`PetAttack`, `PetFollow`, …) sowie `UseAction`, Handel, Auktionshaus,
Kalender, LFG, Raid-Untergruppen und das Anlegen und Ändern von Makros. Auch die
Sperrliste für Zauber aus unsicherem Code wird nicht mehr geprüft.

Nicht angetastet bleiben die Frame-Schutzprüfung (`SetAttribute`, `Show`,
`Hide` auf geschützten Frames) und `RegisterForSave` – sie betreffen keine
Spielaktionen. Macht Nr. 23 überflüssig; beide zusammen schaden nicht, der
Patcher weist dann nur darauf hin.

> [!WARNING]
> Das ermöglicht Automatisierung in vollem Umfang. Server mit Anti-Cheat können
> das als Botting werten – das kann zu einem Bann führen.

<a id="patch-keyprop"></a>
**Alle Tastatur-Ereignisse an Addons weiterreichen (OnKeyDown)** *(Nr. 25, Autor: Alyst3r (0x539wowmod))* 🔴 **[unsicher - ingame ungetestet]**

Hat ein Frame ein OnKeyDown-Skript, meldet der Client die Taste danach als
erledigt – sie erreicht die Tastenbelegungen dann nicht mehr. Mit dem Patch läuft
jede Taste nach dem OnKeyDown-Skript weiter zu den Tastenbelegungen. So können
Addons alle Tastendrücke mitlesen, ohne die normale Steuerung zu blockieren.

> [!NOTE]
> Addons, die sich darauf verlassen, dass OnKeyDown eine Taste „schluckt“, lösen
> damit zusätzlich die belegte Aktion aus.

<a id="patch-globalsv"></a>
**Addon-Daten aller Accounts zusammenlegen (SavedVariables)** *(Nr. 26, Autor: St0ny (original by boredatom))* 🟠 **[ungetestet]**

WoW speichert die Daten der Addons normalerweise pro Account unter
`WTF\Account\<ACCOUNT>\`. Mit dem Patch nutzen alle Accounts dafür den
gemeinsamen Ordner `WTF\Account\global\` – wer mehrere Accounts spielt, richtet
seine Addons so nur einmal ein. Zusammengelegt werden:

- die accountweiten Addon-Daten (`SavedVariables\*.lua`),
- die Addon-Daten der Charaktere (`<Realm>\<Charakter>\SavedVariables\*.lua`),
- die Liste der aktivierten Addons (`AddOns.txt`, accountweit und je Charakter).

Makros, Tastenbelegungen sowie Chat- und Spieleinstellungen bleiben wie bisher
pro Account getrennt.

> [!NOTE]
> Vorhandene Addon-Daten zieht der Patch nicht um. Wer sie behalten will,
> kopiert vor dem ersten Start den Inhalt von `WTF\Account\<ACCOUNT>\` nach
> `WTF\Account\global\`. Nimmt man den Patch zurück, nutzt WoW wieder die
> Ordner der einzelnen Accounts; `global` bleibt unverändert liegen.

Technisch ändert der Patch 9 Byte in der Funktion, die nach dem Login den
Account-Namen für die Addon-Pfade übernimmt (VA `0x5F9080`): Statt des Namens
kopiert sie den Text `global`, der schon in der `Wow.exe` steht. Das Original
von boredatom (`patch_globalvariables.exe`) verschiebt dafür den Rest der
Funktion um 4 Byte, hier bleibt alles an seinem Platz. Die Werbung, die das
Original zusätzlich in die `Wow.exe` schreibt (ein Telegram-Hinweis im
Login-Bildschirm), ist nicht enthalten.

## DLL-Loader

<a id="patch-wowoptimize"></a>
**wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST)** *(Nr. 27, Autor: St0ny)* 🟡 **[sicher - DLL riskant]**

Lädt beim Start die `wow_optimize.dll` aus dem WoW-Ordner –
[wow_optimize](https://github.com/suprepupre/wow-optimize) von SUPREMATIST
optimiert den Client auf Engine-Ebene: Speicherverwaltung, Lua-VM, Timer sowie
Datei- und Netzwerkzugriffe. Bisher wurde die DLL über die mitgelieferte
`version.dll` (Proxy) oder einen Injector geladen. Mit diesem Patch lädt die
Exe sie selbst. Fehlt die DLL, startet WoW ganz normal.

> [!CAUTION]
> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten
> ist. Die geladene `wow_optimize.dll` kann aber auf öffentlichen Servern
> erkannt oder blockiert werden: Laut dem Autor von wow_optimize führt sie auf
> manchen öffentlichen Servern zu einem **dauerhaften Bann**, auf anderen zum
> Disconnect. Nur auf Servern verwenden, die das erlauben.

So wird es eingerichtet: Nur die `wow_optimize.dll` aus dem
wow_optimize-Download in den WoW-Ordner legen. Die `version.dll` von
wow_optimize wird nicht gebraucht; liegt sie noch im Ordner, wird die DLL
trotzdem nur einmal geladen. Ihre Einstellungen liest wow_optimize aus der
`wow_opt.ini`, ohne diese Datei gelten die Standardwerte.

Dateigröße und PE-Header bleiben unverändert: Wie die Proxy-`version.dll` legt
die Exe beim Start einen eigenen Thread an, der 3 Sekunden wartet und dann
`LoadLibraryA("wow_optimize.dll")` aufruft. Eingehängt ist das in den
einmaligen Aufruf bei VA `0x76E490`, den der Einstiegspunkt gleich zu Beginn
ausführt. Der Code verteilt sich auf acht freie Lücken zwischen Funktionen,
den DLL-Namen legt der Thread auf dem Stack ab. Der Patch verträgt sich mit dem
Lexara-Lader (Nr. 30).

<a id="patch-awesome"></a>
**AwesomeWotlkLib.dll Unterstützung aktivieren (Client-Erweiterungen von noname08662)** *(Nr. 28, Autor: FrostAtom)* 🟡 **[sicher - DLL riskant]**

Ermöglicht das Laden der `AwesomeWotlkLib.dll` beim Client-Start. Diese DLL
erweitert den Client um zusätzliche Funktionen und Verbesserungen für private
Server.
**Benötigt** die `AwesomeWotlkLib.dll` aus [awesome_wotlk](https://github.com/noname08662/awesome_wotlk).
Gehört zusammen mit dem 4GB-Patch (Nr. 1); fehlt der in der Auswahl, weist der
Patcher darauf hin.

Der Lader sitzt am Start der Haupt-Fiber des Clients (kurz vor `WinMain`) und
überschreibt dafür den Anfang der Scan.dll-Startfunktion; die Lua-Funktion
`ScanDLLStart` wird zum Leerlauf und das Scan.dll-Flag auf „bestanden“ gesetzt.
Der Patch schaltet damit nebenbei den Scan.dll-Mechanismus ab (wie Nr. 12).
Fehlt die DLL, startet WoW normal weiter.

> [!WARNING]
> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten
> ist. Die geladene `AwesomeWotlkLib.dll` kann aber auf öffentlichen Servern
> erkannt oder blockiert werden – also nur dort einsetzen, wo awesome_wotlk
> erlaubt ist.

> [!NOTE]
> Ist zusätzlich Nr. 64 (HD-Portraits) eingespielt, hat die CVar
> `portraitResolution` von awesome_wotlk keine Wirkung – es gilt immer die
> Auflösung des Exe-Patches.

<a id="patch-wotlkext"></a>
**WotLKExtensions.dll Unterstützung aktivieren (Client-Erweiterungen von Alyst3r)** *(Nr. 29, Autor: St0ny (original by Alyst3r))* 🟡 **[sicher - DLL riskant]**

Lädt beim Client-Start die `WotLKExtensions.dll` aus dem WoW-Ordner. Die DLL aus
[WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions) von Alyst3r
erweitert den Client für eigene Server-Projekte, u. a. um eigene DBC-Dateien,
eigene Pakete und neue Lua-Funktionen.
**Benötigt** die `WotLKExtensions.dll` aus WotLK-Extensions. Gehört zusammen
mit dem 4GB-Patch (Nr. 1); fehlt der in der Auswahl, weist der Patcher darauf
hin.

Der Original-Patcher von WotLK-Extensions setzt seinen Lader an dieselbe Stelle
wie Nr. 28 – beide zusammen gingen nicht. Dieser Lader hängt sich stattdessen
an die erste Funktion, die der Client von dort aus aufruft, und liegt im
ungenutzten Teil der Scan.dll-Startfunktion hinter dem Lader von Nr. 28. So
lassen sich Nr. 28 und Nr. 29 einzeln oder zusammen einspielen; zusammen lädt
der Client beide DLLs. Wie bei Nr. 28 wird die Lua-Funktion `ScanDLLStart` zum
Leerlauf und das Scan.dll-Flag auf „bestanden“ gesetzt – der Scan.dll-Mechanismus
ist damit abgeschaltet (wie Nr. 12). Fehlt die DLL, startet WoW normal weiter.
Die Dateigröße ändert sich nicht.

> [!WARNING]
> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten
> ist. Die geladene `WotLKExtensions.dll` kann aber auf öffentlichen Servern
> erkannt oder blockiert werden; laut dem Projekt können manche Server Aufrufe
> seiner Lua-Funktionen erkennen. WotLK-Extensions ist für eigene
> Server-Projekte gedacht – nur dort einsetzen, wo es erlaubt ist.

> [!NOTE]
> Die DLL spielt beim Start selbst einige Patches im Speicher ein, darunter
> immer ihren eigenen Jahr-2031-Fix. Keiner davon kollidiert mit den Patches
> dieses Patchers: Wo die DLL dieselben Stellen ändert (ihr LUA-Unlock wie
> Nr. 24, ihr GlueXML-Unlock wie Nr. 19), entsteht kein kaputter Code, und mit
> DLL gilt deren Fassung. Ihr Zeit-Fix lässt allerdings jährliche Feiertage mit
> festem Datum und wöchentliche Feiertage aus dem Kalender verschwinden.

<a id="patch-lexara"></a>
**Lexara.dll beim Start laden (HD-Schriften von Stormhand)** *(Nr. 30, Autor: St0ny)* 🟡 **[sicher - DLL riskant]**

Lädt beim Start die `Lexara.dll` aus dem WoW-Ordner –
[Lexara](https://github.com/Stormhand-dev/Lexara---HD-Font-Renderer-for-WoW-3.3.5) von Stormhand ersetzt die Schriftdarstellung
des Clients durch scharfe HD-Schriften (MSDF). Bisher lief Lexara als
`dinput8.dll` neben der Exe und kam sich dabei mit anderen Mods in die Quere,
die denselben Dateinamen benutzen. Mit diesem Patch lädt die Exe Lexara selbst.
Fehlt die DLL, startet WoW ganz normal.

> [!WARNING]
> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten
> ist. Die geladene `Lexara.dll` kann aber auf öffentlichen Servern erkannt
> oder blockiert werden – also nur dort einsetzen, wo Lexara erlaubt ist.

So wird es eingerichtet: Die `dinput8.dll` aus dem Lexara-Download in
`Lexara.dll` umbenennen und zusammen mit `skia.dll` in den WoW-Ordner legen.
Keine zusätzliche `dinput8.dll` von Lexara liegen lassen, sonst wird Lexara
doppelt geladen.

Dateigröße und PE-Header bleiben unverändert: Der Einstiegspunkt (VA
`0x401000`) ruft zuerst `__security_init_cookie` auf. Dieser Aufruf zeigt jetzt
auf eine freie 16-Byte-Lücke (VA `0x6DC8C0`) mit `push "Lexara.dll"` →
`call [LoadLibraryA]` → Sprung zu `__security_init_cookie`. Der Name steht in
einer zweiten Lücke (VA `0x6DC0E0`). Eine Proxy-DLL wird ebenfalls vor dem
Einstiegspunkt geladen, der Zeitpunkt passt also.

## Gameplay-Fixes

<a id="patch-areatrigger"></a>
**Area-Trigger-Timer genauer (50 ms statt 100 ms)** *(Nr. 31, Autor: Robinsch)* 🟢 **[sicher]**

Erhöht die Prüffrequenz für Area-Trigger von 100 ms auf 50 ms. Dadurch werden
Zonen-Übergänge und Trigger präziser erkannt.

<a id="patch-swing"></a>
**Nahkampf-Schwung bei Rechtsklick entfernt** *(Nr. 32, Autor: Robinsch)* 🟢 **[sicher]**

Verhindert den fehlerhaften Auto-Attack-Swing, der beim Rechtsklick auf ein
Ziel ausgelöst wurde.

<a id="patch-npcanim"></a>
**NPC-Angriffsanimation beim Drehen unterdrückt** *(Nr. 33, Autor: Robinsch (fixed by St0ny))* 🟢 **[sicher]**

Unterdrückt die Angriffsanimation von NPCs beim Drehen, wenn kein echter
Angriff stattfindet.

Dreht sich eine Einheit auf der Stelle, verdreht der Client zuerst Oberkörper
und Kopf; die Beine ziehen mit der Schritt-Animation (ShuffleLeft/-Right) nach.
Diese Animation startet der Client, indem er die Animation der Einheit neu
bestimmt – bei NPCs kam dabei die Angriffsanimation heraus. Robinschs Patch
(bedingter Sprung → fester Sprung bei VA `0x73E3C9`) schaltete diesen Aufruf
aber für **alle** Einheiten ab, also auch für Spieler: Beim Drehen machten ihre
Beine keine Schritte mehr, nur der Oberkörper verdrehte sich seltsam.

Hier ist der Block bei VA `0x73E385`–`0x73E3D5` kompakter neu geschrieben
(gleiche Logik) und prüft zusätzlich, ob die Einheit ein Spieler ist: Spieler
drehen sich wie im Original, NPCs verhalten sich wie mit Robinschs Patch.

<a id="patch-spellanim"></a>
**Zauber-Animation nach Abbruch repariert** *(Nr. 34, Autor: Robinsch)* 🟢 **[sicher]**

Behebt einen Bug, bei dem nach dem Abbrechen eines kanalisierten Zaubers die
Vorbereitungsanimation hängen blieb.

<a id="patch-ghostattack"></a>
**„Geister“-Angriff von NPCs beim Evade behoben** *(Nr. 35, Autor: Robinsch (fixed by St0ny))* 🟢 **[sicher]**

Bevor der Client ein neues Nahkampf-Ergebnis anzeigt, spielt er den zuletzt
gespeicherten Schlag noch einmal auf dem Ziel ab. Hat ein NPC inzwischen den
Kampf abgebrochen (Evade), ist das ein veralteter Schlag – der „Geister“-Angriff.
Mit dem Patch wird der gespeicherte Schlag nur noch verworfen, nicht mehr
abgespielt (bedingter Sprung → fester Sprung bei VA `0x7561BF` in
`UnitCombat_C`).

In Robinschs Liste steht der Offset `0x355BF` – dort fehlt eine 5. Er traf einen
`call` in einer String-Hilfsfunktion und hätte daraus eine Endlosschleife
gemacht. Hier ist er auf `0x3555BF` korrigiert.

<a id="patch-naked"></a>
**Nackter-Charakter-Bug behoben** *(Nr. 36, Autor: Robinsch (fixed by St0ny))* 🟢 **[sicher]**

Behebt nackt dargestellte Charaktere, wie sie auf privaten Servern vorkommen,
wenn neue Items nur über `ItemDisplayInfo` verteilt werden. Der Patch schaltet
`SPELL_AURA_X_RAY` ab: Die Abfrage, ob der eigene Spieler diese Aura hat
(VA `0x6DE840`), meldet immer „nein“. Mit der Aura zeichnet der Client andere
Einheiten ohne Ausrüstung.

Robinsch hat für diesen Patch mit der Basisadresse `0x500C00` statt `0x400C00`
gerechnet (so notiert in seinem Quellcode). Sein Offset `0x1DDC5D` traf deshalb
ein `push 0` in der Lua-Funktion `GetTradeSkillTools`. Hier ist er auf
`0x2DDC5D` korrigiert.

<a id="patch-forcereaction"></a>
**Force-Reaction bei /reload erhalten** *(Nr. 37, Autor: Robinsch)* 🟢 **[sicher]**

Verhindert, dass Force-Reaction-Werte (z. B. Fraktionsstatus) beim Neuladen
der UI zurückgesetzt werden. Wichtig für Custom-Server.

<a id="patch-mail"></a>
**Neue Post ohne 60 Sekunden Wartezeit** *(Nr. 38, Autor: Robinsch)* 🟢 **[sicher]**

Der Client fragt neue Post sofort ab – kein Warten mehr von 60 Sekunden und kein
Relog, um neue Post zu bekommen.

<a id="patch-deadchat"></a>
**Chat-Befehle auch im Tod erlauben** *(Nr. 39, Autor: Robinsch)* 🟢 **[sicher]**

Slash-Befehle funktionieren auch, während der Charakter tot ist.

<a id="patch-follow"></a>
**/follow auch bei NPCs erlauben** *(Nr. 40, Autor: St0ny (original by Alastor StrixEfuartus))* 🟠 **[online ungetestet]**

Mit `/follow` lässt sich auch NPCs folgen, nicht nur Spielern. Basiert auf
dem `/follow`-Patch aus der 12th Generation EXE von Alastor StrixEfuartus,
Portierung und Anpassung von St0ny: Das Original leitet die Prüfung in
eine Code-Höhle um, die ihr Ergebnis ignoriert. Diese Höhle läge aber genau
in der Lücke am Ende von `.text`, die Nr. 4 und Nr. 63 nutzen. Hier wird
stattdessen der bedingte Sprung hinter der Prüfung unbedingt gemacht – ein
einziges Byte, gleiche Wirkung, und die Patches vertragen sich.

<a id="patch-level101"></a>
**Level 101+ Druid Fix (Druiden-Werte im Charakterfenster, Barbierstuhl für alle)** *(Nr. 41, Autor: Alastor StrixEfuartus (fixed by St0ny))* 🟢 **[sicher]**

Die Spielwert-Tabellen des Clients (`gtCombatRatings`, `gtBarberShopCostBase`,
`gtOCTRegenHP`/`MP`, `gtChanceToMeleeCrit` … – elf Tabellen) haben je Spalte
100 Zeilen, eine pro Level. Ab Level 101 greift der Client außerhalb der Spalte
zu. Das fällt vor allem an zwei Stellen auf:
- **Druiden** sehen im Charakterfenster (Reiter Charakterinfo) ihre Werte nicht
  mehr richtig.
- Der **Barbierstuhl** funktioniert für **alle Klassen** nicht mehr.

Im schlimmsten Fall stürzt der Client ab. Der Patch begrenzt die Zeile auf die
letzte der Spalte: Level 101+ bekommt die Werte für Level 100, alles
darunter bleibt unverändert.

> [!NOTE]
> Die verbreitete Fassung aus der 12th Generation EXE entfernt stattdessen das
> Level komplett aus der Rechnung – damit zeigen *alle* Charaktere die Werte
> für Level 1 (Wertungen, kritische Trefferchance, Regeneration …). Hier sind
> die beiden Zugriffsfunktionen (VA `0x7F69B0` und `0x7F69E0`) dafür neu
> geschrieben.

**Benötigt** laut Quelle den Patch „Custom Glue-XML erlauben“ (Nr. 19). In der
Quelle heißt er „Disable XML SIG MD5“, daher der dortige Hinweis „Use XML MD5“.

<a id="patch-raceclass"></a>
**Charaktererstellung: mehr als 10 Klassen (Zufallsklasse)** *(Nr. 42, Autor: Alastor StrixEfuartus / Robinsch)* 🔴 **[unsicher]**

Die Zufallsauswahl der Klasse bei der Charaktererstellung sammelt die
erlaubten Klassen in einem Feld mit 10 Plätzen. Mit eigenen Klassen
(`ChrClasses.dbc` mit mehr als 10 Einträgen) würde es überlaufen; der Patch
vergrößert es auf 30 Plätze. Welche Rasse welche Klasse darf, prüft weiterhin
der Server – mehr macht dieser Patch nicht.

<a id="patch-namecheck"></a>
**Namensprüfung bei der Charaktererstellung abschalten (z. B. Zahlen im Namen)** *(Nr. 43, Autor: Alyst3r (0x539wowmod) (fixed by St0ny))* 🔴 **[unsicher]**

Schaltet die komplette clientseitige Namensprüfung bei der Charaktererstellung
ab: Die Prüffunktion (VA `0x6B0F90`) meldet immer „Name gültig“. Damit sind z. B.
Zahlen im Namen möglich – es entfallen aber auch alle anderen Regeln des Clients
(Länge, erlaubte Zeichen usw.). Im Original (0x539wowmod) per Detour mit falscher
Aufrufkonvention gelöst, hier direkt in der Funktion (`mov eax, 57h` / `ret`).

**Wird benötigt für [mod-two-names](https://github.com/lightninjay/mod-two-names)**
(AzerothCore-Modul für Vor- und Nachnamen, z. B. „Arthas Menethil“): Ohne diesen
Patch lehnt der Client Namen mit Leerzeichen ab. Das Projekt bringt selbst
denselben Exe-Patch mit (`tools/patch_wow_safe.py`, gleiche Bytes an derselben
Stelle). Dazu gehören das Server-Modul und die GlueXML-Dateien des Projekts als
Patch-MPQ, für die geänderten Interface-Dateien außerdem „Custom Glue-XML
erlauben“ (Nr. 19).

> [!WARNING]
> Der Server prüft Namen weiterhin selbst und muss sie ebenfalls erlauben, sonst
> lehnt er den Charakter ab.

<a id="patch-maxchars"></a>
**Max. Charaktere pro Server auf 255 erhöht** *(Nr. 44, Autor: St0ny)* 🟢 **[sicher]**

Hebt die clientseitige Begrenzung von 10 auf 255 Charaktere pro Server an.
Der Server muss dies ebenfalls unterstützen. Zusätzliche
Interface-Anpassungen (Glue-XML) sind nötig, damit der
Charakterauswahl-Bildschirm mehr als 10 Slots anzeigt.

<a id="patch-customitem"></a>
**Custom Item Fix (BETA) v2** *(Nr. 45, Autor: St0ny (original by Kebabstorm))* 🟠 **[ungetestet]**

Macht Custom-Items möglich, ohne die `Item.dbc` des Clients anzupassen. Viele
Stellen im Client lesen Display-ID, Inventartyp, Klasse, Unterklasse und Scheide
eines Items nur aus der `Item.dbc`. Items, die nur in der Datenbank des Servers
stehen, fehlen dort – der Client zeigt dann z. B. kein Modell am Charakter und
kein Icon. Die `Wow.exe` hat aber schon Hilfsfunktionen, die diese Werte zuerst
im Item-Cache suchen (also in den Daten, die der Server zu jedem Item schickt)
und erst danach in der `Item.dbc`. Der Patch leitet die reinen DBC-Zugriffe auf
diese Hilfsfunktionen um. Steht ein Item in beiden, gelten damit die Werte des
Servers. Auf dem Server reicht für ein Custom-Item dann der Eintrag in
`item_template`; bei TrinityCore muss dazu in der `worldserver.conf`
`DBC.EnforceItemAttributes = 0` gesetzt sein. Nur das Material (das Geräusch
beim Verschieben im Inventar) kommt weiter allein aus der `Item.dbc`.

Vorlage ist der „Custom Item Fix (BETA) v1“ aus Kebabstorms
[WoW 3.3.5 Patcher (Custom Item Fix)](https://www.wowmodding.net/files/file/283-wow-335-patcher-custom-item-fix/).

**Empfohlen** zusammen mit „CACHE-Ordner-Erstellung deaktivieren“ (Nr. 2): Dann
speichert WoW den Item-Cache nicht auf der Festplatte und holt geänderte
Custom-Items bei jedem Start frisch vom Server. Fehlt Nr. 2 in der Auswahl,
weist der Patcher darauf hin.

> [!NOTE]
> Die Patch-Liste von v1, aus der dieser Patch übernommen wurde, enthielt zwei
> Fehler, mit denen der Client abgestürzt wäre: In einer Zeile fehlte ein Byte
> (die Funktion für die Item-Klasse wurde dadurch zu Datenmüll), eine andere
> war eine Kopie der Zeile davor (ein Aufruf landete mitten in einer fremden
> Funktion). v2 behebt beides. Alle umgebauten Stellen
> wurden per Emulation mit Test-Items geprüft: nur im Cache, nur in der
> `Item.dbc`, in beiden und in keinem.

Aus v1 nicht übernommen: die PE-Prüfsumme (Windows prüft sie bei Programmen
nicht) und die Änderung `Cache` → `||che` – das ist genau Patch Nr. 2.

<a id="patch-climb"></a>
**Steigwinkel-Begrenzung aufheben (jeden Hang hochlaufen)** *(Nr. 46, Autor: Alastor StrixEfuartus)* 🔴 **[unsicher]**

Der Charakter kommt jeden Hang hoch, egal wie steil. Im Original ist bei 50°
Schluss: Der Client vergleicht die Neigung mit dem Kosinus dieses Winkels
(`0.6427876` bei VA `0xA37F0C`). Der Patch setzt ihn auf `0.0` = cos 90°.

> [!WARNING]
> Server mit Anti-Cheat können das als Climb-Hack erkennen – das kann zu einem
> Bann führen.

<a id="patch-jump"></a>
**Sprunghöhe ändern (Original -7.9555473)** *(Nr. 47, Autor: Alastor StrixEfuartus)* 🔴 **[unsicher]**

Ändert die Anfangsgeschwindigkeit des Sprungs (VA `0xAA33DC`, Original
`-7.9555473`). Der Patcher fragt den Wert nach der Auswahl ab: eine negative
Zahl von `-100` bis knapp unter `0`, Komma oder Punkt als Dezimaltrenner. Je
kleiner der Wert, desto höher der Sprung; die Höhe wächst mit dem Quadrat, d. h.
`-11.25` ergibt etwa die doppelte, `-15.91` etwa die vierfache Sprunghöhe. Der
Wert wird wie bei den Client-Info-Patches gemerkt.

> [!WARNING]
> Server mit Anti-Cheat können das als Jump-Hack erkennen – das kann zu einem
> Bann führen.

<a id="patch-airforward"></a>
**Im Sprung vorwärts/rückwärts steuern** *(Nr. 48, Autor: Alyst3r (0x539wowmod) (ported by St0ny))* 🔴 **[unsicher]**

Normalerweise ignoriert der Client Vorwärts- und Rückwärts-Eingaben, solange der
Charakter springt oder fällt. Mit dem Patch lässt sich die Richtung auch in der
Luft ändern, bis hin zur Gegenrichtung. 0x539wowmod ersetzt dafür per DLL die
Vorwärts-Eingabe des Clients; deren Version weicht vom Original nur in zwei
Sprüngen ab (in der Luft nicht abbrechen, Geschwindigkeit neu berechnen), die
hier direkt in der EXE geändert werden – ohne DLL und ohne Code-Höhle. Dazu kommt
der Byte-Patch aus 0x539wowmod, der die Bewegung in der Luft aktualisiert.

> [!WARNING]
> Server mit Anti-Cheat können veränderte Bewegung in der Luft erkennen – das
> kann zu einem Bann führen.

<a id="patch-airlateral"></a>
**Im Sprung seitwärts steuern** *(Nr. 49, Autor: Alyst3r (0x539wowmod) (ported by St0ny))* 🔴 **[unsicher]**

Wie der vorige Patch, nur für seitliche Bewegung (Strafen): zwei Sprünge in der
Seitwärts-Eingabe des Clients plus der Byte-Patch aus 0x539wowmod, der die
Bewegung bei gesetztem Fall-Flag nicht mehr vorzeitig abbricht.

> [!WARNING]
> Server mit Anti-Cheat können veränderte Bewegung in der Luft erkennen – das
> kann zu einem Bann führen.

<a id="patch-airturn"></a>
**Im Sprung drehen ändert die Flugrichtung** *(Nr. 50, Autor: Alyst3r (0x539wowmod) (ported by St0ny))* 🔴 **[unsicher]**

Dreht man sich im Sprung (Maus oder Tasten), behält der Charakter im Original
seine Flugrichtung. Mit dem Patch setzt der Client die Bewegungsrichtung auch in
der Luft neu, wie es die DLL von 0x539wowmod tut. Passt am besten zusammen mit
den beiden vorigen Patches.

> [!WARNING]
> Server mit Anti-Cheat können veränderte Bewegung in der Luft erkennen – das
> kann zu einem Bann führen.

<a id="patch-doublejump"></a>
**Doppelsprung (weitere Sprünge in der Luft)** *(Nr. 51, Autor: Alyst3r (0x539wowmod) (ported by St0ny))* 🔴 **[unsicher - Exe wird größer]**

Erlaubt weitere Sprünge, während der Charakter in der Luft ist. Der Patcher fragt
nach der Auswahl, wie viele zusätzliche Sprünge es sein sollen (1 bis 9, `1` =
Doppelsprung); der Wert wird wie bei den Client-Info-Patches gemerkt.

Die Sprungfunktion des Clients (VA `0x9883F0`) lehnt jeden Sprung ab, solange der
Charakter fällt. 0x539wowmod ersetzt sie per DLL und zählt Sprungladungen mit.
Hier geschieht dasselbe in einer kleinen Code-Höhle: Beim Sprung vom Boden wird
ein Zähler auf die gewählte Anzahl gesetzt, in der Luft ist ein Sprung erlaubt,
solange der Zähler nicht 0 ist. Festgewurzelt oder fliegend bleibt Springen
gesperrt. Jeder Luftsprung nutzt dieselbe Sprunghöhe wie ein normaler Sprung
(also auch den Wert aus „Sprunghöhe ändern“, Nr. 47). Den doppelten Sprung aus
0x539wowmod mit eigener zweiter Sprunghöhe gibt es hier nicht. Der Zähler wird
erst beim nächsten Sprung vom Boden neu gesetzt, nicht beim Landen: Wer nach
einem Sprung landet und dann von einer Kante läuft, hat in der Luft wieder die
gewählte Anzahl Sprünge.

Der Zähler ist ein Byte, das der Client beschreiben muss. Darum bekommt der Patch
eine eigene kleine Sektion `.djump` am Dateiende (die Lücke in `.text` ist nicht
beschreibbar); die `Wow.exe` wird dadurch etwas größer.

> [!WARNING]
> Server mit Anti-Cheat können Sprünge in der Luft erkennen – das kann zu einem
> Bann führen.

<a id="patch-noammo"></a>
**Fernkampf ohne Munition** *(Nr. 52, Autor: Alyst3r (ported by St0ny))* 🟠 **[ungetestet]**

Der Client prüft bei Schießen, Automatischem Schuss und anderen Fähigkeiten,
die Munition brauchen, ob Pfeile oder Kugeln vorhanden sind. Der Patch lässt
diese Prüfung im Client weg (Sprung zum Erfolgsausgang bei VA `0x809540`).

> [!IMPORTANT]
> Der Server prüft selbst. Nur wenn er so angepasst ist, dass er keine
> Munition verlangt, funktioniert Fernkampf ohne Munition – sonst meldet er
> weiter „Keine Munition“. Ohne angepasste Anzeige fliegen die Geschosse
> unsichtbar.

## Grafik & Sichtweite

<a id="patch-farclip"></a>
**CVar farclip unlock (max 10000)** *(Nr. 53, Autor: Alastor StrixEfuartus)* 🟢 **[sicher]**

Entsperrt die maximale Sichtweite (Farclip) auf 10000 Yards. Der Client klemmt
den Wert beim Setzen in einer einzigen Funktion (VA `0x780770`) nach oben ab
und hält dafür zwei Grenzen bereit: 1583 Yards im Normalfall und 791 Yards als
Rückfallwert. Die 791 greifen auf den alten Vanilla-Zonen sowie auf Rechnern
mit höchstens 1 GB Arbeitsspeicher – der Client fragt die RAM-Größe an dieser
Stelle tatsächlich ab. Der Patch hebt beide Grenzen auf 10000, sonst fällt die
Sichtweite je nach Zone wieder auf 791 zurück.
Die Untergrenze von 183 Yards bleibt unangetastet, und ein davon getrenntes
Eingabelimit für das CVar gibt es nicht – diese Klemme ist das Limit.
Nicht zu verwechseln mit der 1277 aus dem Video-Menü: Das ist die Obergrenze
des Sichtweite-Reglers und eine völlig andere Stelle in der EXE (siehe
Patch Nr. 57 „Grafikoptionen: Slider-Maxima erweitern“).

<a id="patch-horizon"></a>
**CVar horizonFarclipScale unlock (max 12)** *(Nr. 54, Autor: St0ny)* 🟢 **[sicher]**

Entsperrt das CVar `horizonFarclipScale` und setzt den maximalen Wert auf 12.
Erhöht die Sichtweite des Horizonts deutlich.

<a id="patch-envdetail"></a>
**CVar environmentDetail unlock (kein Limit statt 1.5)** *(Nr. 55, Autor: St0ny)* 🟢 **[sicher]**

Entfernt die Obergrenze des CVars `environmentDetail` komplett. Original wird
der Wert auf den Bereich 0.5 bis 1.5 begrenzt; der Patch ersetzt am gemeinsamen
Ausgang der Prüfung den geklemmten Wert durch den Rohwert – damit fällt auch
die Untergrenze 0.5 weg, beliebige Werte werden durchgereicht (sinnvoll sind
Werte ab 0.5).
Wichtig: Dieses CVar tut nichts anderes, als die GameObject-Sichtweiten zu
multiplizieren (siehe Patch Nr. 58) – im Original nur die der Kategorien 1 bis
3, mit Patch Nr. 58 alle fünf. Es ist damit der bequemste FPS-Hebel im
Objekt-Rendering, weil er ohne Neupatchen im Spiel wirkt.

<a id="patch-grounddist"></a>
**CVar groundEffectDist unlock (max 3166 statt 140)** *(Nr. 56)* 🟢 **[sicher]**

Erhöht die maximale Sichtweite für Bodeneffekte (Gras, Blumen, Bodendeko) von
140 auf 3166 Yards.

<a id="patch-sliders"></a>
**Grafikoptionen: Slider-Maxima erweitern** *(Nr. 57, Autor: St0ny)* 🟢 **[sicher]**

Hebt die Obergrenzen von vier Reglern im Video-Menü an, Reiter „Effekte“. Die
CVars selbst sind durch die Unlock-Patches längst entsperrt – die Regler
blieben trotzdem auf Blizzards Werten stehen, weil sie ihr Maximum nicht aus
dem CVar-Limit beziehen.

| CVar                  | Regler vorher | Regler nachher |
|-----------------------|--------------:|---------------:|
| `farclip`             | 1277          | 2477           |
| `environmentDetail`   | 1.5           | 2.5            |
| `groundEffectDist`    | 140           | 250            |
| `groundEffectDensity` | 64            | 256            |

Die Untergrenzen bleiben unverändert (177 / 0.5 / 70 / 16), ebenso die
Schrittweiten aus dem Interface. Sie gehen glatt auf: bei `environmentDetail`
8 Stufen, bei `groundEffectDist` 18, bei `groundEffectDensity` 30. Beim
Sichtweiten-Regler rechnet das Interface die Schrittweite ohnehin selbst als
(max−min)/10 aus, hier also 230 Yards pro Raste.

<details>
<summary><b>Hintergrund: Warum die Regler nicht schon vorher mitgewachsen sind</b></summary>

Das Interface baut jeden Regler nach diesem Muster auf:

```lua
minValue = GetCVarMin(cvar)  -- oder Ersatzwert aus der Lua
maxValue = GetCVarMax(cvar)  -- oder Ersatzwert aus der Lua
```

Es fragt also zuerst die EXE und nimmt nur dann den in
`VideoOptionsPanels.lua` hinterlegten Ersatzwert, wenn die EXE nichts liefert.
Die Funktion `GetCVarMax` kennt im Original aber nur zwei CVars:
`extShadowQuality` und `farclip`. Für alles andere gibt sie nichts zurück, und
dann greifen die fest verdrahteten Lua-Werte 1.5 / 140 / 64. Bei `farclip`
lieferte sie eine feste 1277 – ebenfalls unabhängig davon, wie weit das CVar
entsperrt ist.

Der Patch ersetzt den festen farclip-Vergleich durch den Aufruf einer kleinen
Such-Routine, die eine Liste von CVar-Namen durchläuft. Steht ein CVar drin,
bekommt das Interface das zugehörige Maximum; steht es nicht drin, läuft alles
wie bisher. Die Routine (18 Byte) liegt in einer freien Lücke zwischen zwei
Funktionen der Code-Sektion, die Liste mit den Maxima im ungenutzten Rest von
`.rdata` – die Datei wächst dadurch nicht.

Wichtig: `GetCVarMax` liegt zweimal in der EXE – einmal für den
Anmelde-/Charakterbildschirm und einmal für das laufende Spiel. Beide Stellen
rufen dieselbe Such-Routine auf. Wird nur eine davon gepatcht, bleiben die
Regler im Spiel unverändert auf 1277 / 1.5 / 140 / 64 stehen, ohne dass
irgendetwas auffällt.

</details>

**Zwei Einschränkungen**

- Der Regler setzt nur das CVar. Ohne die Unlock-Patches klemmt der Client den
  Wert beim Setzen sofort wieder auf sein Original zurück – die Patches
  „CVar farclip unlock“ (Nr. 53), „CVar environmentDetail unlock“ (Nr. 55) und
  „CVar groundEffectDist unlock“ (Nr. 56) gehören also dazu. Fehlen sie in der
  Auswahl, weist der Patcher darauf hin.
- Bei `groundEffectDensity` wirkt oberhalb von 64 nichts mehr: Der Vertexbuffer
  der Bodendeko ist im Client fest auf Dichte × 64 ≤ 4096 geklemmt. Der Regler
  läuft dann bis 256, sichtbar ändert sich ab 64 aber nichts.

**Das Ultra-Preset bleibt auf Blizzards Werten**

Der Master-Regler „Grafikqualität“ setzt auf Ultra weiterhin 1277 / 1.5 / 140 /
64, nicht die neuen Maxima. Das lässt sich von der EXE aus nicht ändern: Die
Preset-Werte stehen als reine Lua-Konstanten in
`Interface\FrameXML\GraphicsQualityLevels.lua` und werden von dort direkt in
die Regler geschrieben. Der einzige Draht von der EXE in diesen Pfad ist
`VideoOptionsEffectsPanel_FixupQualityLevels`, und die Funktion kann nur
klemmen – Werte über dem Maximum runter, Werte unter dem Minimum hoch. Beides
gilt pro CVar für alle sechs Qualitätsstufen gleichzeitig, eine einzelne Stufe
ist nicht ansprechbar.

> [!CAUTION]
> Verlockende Sackgasse: Über das Minimum ließe sich Ultra zwar hochziehen
> (`GetCVarMin("farclip")` ist der double bei `0x9F5798`, original 177.0), aber
> dann werden ALLE sechs Stufen auf diesen Wert gezogen – Niedrig wie Ultra –
> und der Regler bekommt Minimum über Maximum, klebt am Anschlag und hat eine
> negative Schrittweite. Genau das ist bei einem früheren Versuch passiert und
> hat über die `Config.wtf` Startabstürze verursacht. Den Minimum-Double also
> in Ruhe lassen.

Wer Ultra wirklich auf die neuen Maxima heben will, braucht die
Interface-Seite, also eine MPQ mit geänderter `GraphicsQualityLevels.lua` –
dann liegen die Werte fest im Client, statt nachträglich von einem Addon
gesetzt zu werden. Das ist bewusst nicht Teil dieses Patchers: Er bleibt ein
reiner EXE-Patcher, der außer der `Wow.exe` nichts anfasst.

**Kein Regler für horizonFarclipScale**

Für dieses CVar gibt es im Video-Menü überhaupt keinen Regler – es kommt im
gesamten Interface nicht vor. Ein EXE-Patch kann hier nichts anheben, weil es
nichts anzuheben gibt. Der Wert lässt sich weiterhin nur über die
`Config.wtf`, `/console horizonFarclipScale 12` oder ein CVar-Addon setzen
(entsperrt ist er bis 12, siehe oben).

> [!NOTE]
> Die Dateigröße ändert sich nicht: Die kleine Such-Routine liegt in einer
> freien Lücke zwischen zwei Funktionen, die Tabelle mit den Maxima im
> ungenutzten Rest von `.rdata`. Mit Nr. 4 und Nr. 63 gibt es keine Überschneidung.

<a id="patch-goscale"></a>
**GameObject Sichtweite: Cat 0 und Cat 4 auf environmentDetail reagieren lassen** *(Nr. 58, Autor: St0ny)* 🟢 **[sicher]**

Behebt eine Auslassung im Client: Die Funktion, die aus den Basiswerten die
Laufzeit-Sichtweiten rechnet, multipliziert nur Cat 1 bis 3 mit dem CVar
`environmentDetail`. Cat 0 (Kleinkram) und Cat 4 (riesige Gebäude) übernehmen
ihren Basiswert unverändert – der Regler lässt sie schlicht kalt.
Der Patch ergänzt die fehlende Multiplikation in beiden Blöcken. Platz dafür
entsteht, indem eine redundante Kopie der Größen-Schwellen entfällt (die beiden
Tabellen sind identisch und werden nie verändert). Danach skaliert
`environmentDetail` alle fünf Kategorien gleichmäßig – der Regler wird zum
echten Gesamtregler. Die Basis-Sichtweiten bleiben auf den Blizzard-Werten,
geregelt wird über das CVar:

| environmentDetail | Cat 0 | Cat 1 | Cat 2 | Cat 3 | Cat 4 |
|------------------:|------:|------:|------:|------:|------:|
| 1.0               | 30    | 100   | 200   | 750   | 1250  |
| 2.0               | 60    | 200   | 400   | 1500  | 2500  |
| 10 | 300   | 1000  | 2000  | 7500  | 12500 |

Mit Patch Nr. 59 liegt Cat 0 bei 50 statt 30 Yards (in der Tabelle oben also
50 / 100 / 500). Werte über 1.5 setzen den Patch „CVar environmentDetail
unlock“ (Nr. 55) voraus.

<a id="patch-cat0"></a>
**GameObject Sichtweite: Cat 0 von 30 auf 50 Yards** *(Nr. 59, Autor: St0ny)* 🟢 **[sicher]**

Der Patch kostet Leistung: Es ist deutlich mehr Kleinkram gleichzeitig
sichtbar, und die Anzahl der gezeichneten Objekte ist der Performance-Hebel.
Wer die Sichtweiten komplett auf Blizzards Werten lassen möchte, lässt ihn
weg. Er hebt ausschließlich die kleinste Objektkategorie an: Kerzen, Bücher,
Säcke, Werkzeug. Cat 0 ist im Original mit 30 Yards so knapp bemessen, dass
Kleinkram deutlich früher verschwindet als alles andere; 50 verbessert das
Verhältnis zu Cat 1 von 1:3.3 auf 1:2, und der `environmentDetail`-Regler zieht
ihn proportional mit. Cat 1 bis 4 werden nicht angefasst – geregelt wird die
Sichtweite über das CVar, das mit dem Code-Patch Nr. 58 alle fünf Kategorien
gleichmäßig streckt.

Geändert werden fünf zusammengehörige Werte:

| Wert                    | Blizzard | Patch |
|-------------------------|---------:|------:|
| Basis-Sichtweite        | 30       | 50    |
| Laufzeit-Sichtweite     | 30       | 50    |
| Sichtweite im Quadrat   | 900      | 2500  |
| Fade-Start              | 25       | 45    |
| Fade-Start im Quadrat   | 625      | 2025  |

Der Laufzeitwert muss dem Basiswert entsprechen, die Quadrate sind die Quadrate
davon, der Fade-Start ist Sichtweite minus Fade-Band. Das Fade-Band bleibt auf
Blizzards 5 Yards.

<details>
<summary><b>Hintergrund: Wie die Kategorien zustande kommen</b></summary>

Der Client nimmt die Bounding-Box eines Objekts, bildet die **längste Kante**
(nicht den Radius, nicht das Volumen) und sucht die erste Schwelle, die größer
oder gleich dieser Kante ist:

| Kategorie | Längste Kante  | Beispiele                                |
|-----------|----------------|------------------------------------------|
| Cat 0     | bis 1 Yard     | Kerzen, Bücher, Säcke, Werkzeug          |
| Cat 1     | 1 bis 4 Yards  | Kisten, Fässer, Schränke, Feuerschalen   |
| Cat 2     | 4 bis 15 Yards | große Tische, Banner, Kanonen            |
| Cat 3     | 15 bis 100 Yards | Tore, Käfige, Throne, Raid-Türen       |
| Cat 4     | ab 100 Yards   | Zeppeline, schwebende Plattformen        |

Die Schwellen stehen als eigene Tabelle in der EXE und werden von diesem Patch
NICHT angetastet. Die Beispiele stammen aus `GameObjectDisplayInfo.dbc` des
Clients. Achtung: Klassifiziert wird die fertig transformierte Box, ein
hochskaliertes Objekt kann also eine Kategorie höher landen, als sein Modell
vermuten lässt.

**Zusammenspiel mit dem CVar environmentDetail**

Die Werte in diesem Patch sind Basiswerte. Der Client rechnet sie bei jedem
Setzen von `environmentDetail` um:

```
Sichtweite = Basiswert * environmentDetail
```

Im Original gilt das NUR für Cat 1, 2 und 3 – bei Cat 0 und Cat 4 fehlt die
Multiplikation im Code. Der Patch „Cat 0 und Cat 4 auf environmentDetail
reagieren lassen“ (Nr. 58) ergänzt sie, sodass alle fünf Kategorien gleichmäßig
mitwachsen.

Wichtig beim Nachrechnen: Die beiden Faktoren **multiplizieren** sich.
Basiswert ×2 bei CVar 1.5 ergibt ×3, nicht ×2. Wer einen Zielfaktor Z am
CVar-Wert E erreichen will, trägt Z/E als Basiswert ein.
Ohne Patch Nr. 58 gilt das nur für Cat 1–3, und dann laufen die Kategorien
bei hohen CVar-Werten auseinander: Cat 3 würde irgendwann Cat 4 überholen,
mittelgroße Objekte wären also weiter sichtbar als riesige.

Zu beachten: Liegt eine Kategorie-Distanz oberhalb des CVars `farclip`,
schneidet die allgemeine Sichtweite vorher ab und die Kategorie hat keinen
sichtbaren Effekt mehr. Bei farclip 1100 ist Cat 4 also faktisch auf 1100
gedeckelt – höhere Werte wirken erst, wenn farclip entsprechend mitwächst.

**Abgeleitete Tabellen**

Sichtweite und Fade-Band liegen als je eine Tabelle in der EXE, dazu kommen
vier weitere, die der Client daraus selbst berechnet – bei jedem Setzen von
`environmentDetail`:

```
Laufzeit-Sichtweite = Basiswert * environmentDetail
Fade-Start          = Laufzeit-Sichtweite - Fade-Band
Quadrat-Tabellen    = jeweils das Quadrat davon
                      (über die Quadrate cullt die Engine, das spart die Wurzel)
```

Echte Eingangswerte sind also nur die Basis-Sichtweiten und die Fade-Bänder.
Wer die vier abgeleiteten Tabellen trotzdem schreibt, muss sie konsistent
halten, sonst springen die Werte beim ersten Umrechnen.

**Fade-Bänder**

Die Fade-Band-Breiten stehen auf Blizzard-Original (5/10/15/20/50) und werden
nicht mitskaliert. Das Band ist die Strecke, über die ein Objekt vor der
Cull-Grenze ausblendet – enge Bänder halten Objekte bis kurz davor deckend,
statt sie über viele Yards halbtransparent auslaufen zu lassen.
Der Fade-Start ergibt sich immer als Sichtweite minus Band und wandert mit
`environmentDetail` mit: bei 1.0 sind es 25/90/185/730/1200, bei 2.0 dann
55/190/385/1480/2450. Weil das Band gleich bleibt, wächst der Fade-Start etwas
stärker als die Sichtweite selbst.

Hinweis: Die Sichtweite bestimmt, wie viele Objekte gleichzeitig gezeichnet
werden, und ist damit der Performance-Hebel. Die Fade-Bänder kosten praktisch
keine FPS – wer Pop-in störender findet als ein paar Bilder pro Sekunde, kann
sie unabhängig von den Distanzen verbreitern.

</details>

<a id="patch-occluder"></a>
**Occluder Fix für Stormwind (Open Azeroth)** *(Nr. 60, Autor: Robinsch)* 🟢 **[sicher]**

Schaltet die fest in den Client eingebauten Occluder (Sichtblocker) für
Stormwind ab: Der Karten-Schlüssel des Tabelleneintrags für die Östlichen
Königreiche wird auf 99999 gesetzt, sodass er zu keiner Karte mehr passt. So
werden auf Custom-Servern mit umgebautem Stormwind keine Gebäude und Objekte
mehr fälschlich ausgeblendet.

<a id="patch-bluemoon"></a>
**Blauer Mond am Nachthimmel reaktiviert** *(Nr. 61, Autor: Robinsch)* 🟢 **[sicher]**

Stellt ein entferntes Legacy-Feature wieder her: den blauen Mond, der früher
am Nachthimmel sichtbar war.

<a id="patch-notransparency"></a>
**Keine Transparenz beim Heranzoomen** *(Nr. 62, Autor: Alastor StrixEfuartus)* 🟢 **[sicher]**

Der eigene Charakter wird nicht mehr durchsichtig, wenn die Kamera nah
herangezoomt wird. Der Patch entfernt die Transparenz-Zuweisung für den
Normalfall; sitzt der Charakter in einem Fahrzeug oder hängt an einem anderen
Objekt, kann er beim Heranzoomen weiterhin durchsichtig werden (so auch im
Original-Patch).

<a id="patch-nofade"></a>
**Kein Ausblenden für NPCs mit Flag DO_NOT_FADE_IN** *(Nr. 63, Autor: Alyst3r (0x539wowmod) (ported by St0ny))* 🟠 **[ungetestet]**

Beim Entfernen eines NPCs (z. B. Despawn) blendet der Client das Modell
normalerweise langsam aus. Mit dem Patch verschwinden NPCs sofort, bei denen der
Server in `UNIT_FIELD_FLAGS_2` das Flag `UNIT_FLAG2_DO_NOT_FADE_IN` (`0x20`) setzt –
passend zum fehlenden Einblenden. Spieler und NPCs ohne das Flag verhalten sich
wie bisher.

> [!IMPORTANT]
> Wirkt nur, wenn der Server das Flag setzt. Ohne Unterstützung durch den Server
> ändert sich nichts.
>
> Der Code liegt wie bei Nr. 4 in der freien Lücke am Ende von `.text`. Beide
> passen zusammen hinein, die Dateigröße ändert sich nicht.

<a id="patch-hdportraits"></a>
**HD Unit-Frame Portraits: Renderauflösung 256 statt 64 Pixel** *(Nr. 64, Autor: St0ny (original by Badgermilk0))* 🟡 **[sicher - Exe wird größer]**

Die Unit-Frames (Spieler, Ziel, Gruppe, Bosse usw.) zeigen im Client schon im
Original das 3D-Modell des jeweiligen Charakters. Der Patch erzeugt also
**keine neuen Portraits, keine Bilder und keine Animationen** – er ändert nur
eine Zahl: Der Client rendert dieses Modell für den Frame in eine Textur, und
die ist im Original 64×64 Pixel groß. Der Patch hebt genau diese
Renderauflösung auf 256×256 Pixel an, fest eingebaut über den Aufruf
`Add-HdPortraits 256` in `apply_patches.ps1`. Das Original von Badgermilk0
lässt bis zu 4096×4096 zu; hier ist bewusst 256 gewählt, weil mehr nur Speicher
kostet, ohne sichtbar besser auszusehen. Bildausschnitt, Neigung und Zoom
bleiben unverändert, die Portraits werden nur deutlich schärfer.
Nur der 3D-Modell-Pfad wird angehoben; der Icon-/Datei-Pfad (feste
64×64-Bilder für Item-/Zauber-Icons) bleibt bewusst auf 64, da dessen
Kopierschleife sonst über die Quelle hinaus liest.

Der Patch hängt eine neue PE-Sektion `.hdp` an die `Wow.exe` an (generierte
256er-Alphamaske + Code-Höhlen + Detour des Masken-Builders), die Datei wächst
dadurch um ca. 69 KB.

> [!NOTE]
> **Zusammen mit awesome_wotlk (Nr. 28):** Die `AwesomeWotlkLib.dll` bringt mit
> der CVar `portraitResolution` eine eigene Einstellung für die
> Portrait-Auflösung mit. Ist Nr. 64 eingespielt, ist diese Funktion von
> awesome_wotlk blockiert – es gilt immer die Auflösung des Exe-Patches (256),
> egal was in `portraitResolution` steht.

<a id="patch-iconsnap"></a>
**Icons im Text pixelgenau (scharf statt verschwommen)** *(Nr. 65, Autor: tb (ported by St0ny))* 🟡 **[sicher - Exe wird größer]**

Texte können Icons enthalten (`|T…|t`, z. B. Zielmarkierungen, Währungen oder
Questsymbole in Chat, Tooltips und Addons). Ihre Größe und Lage rechnet der
Client in Pixeln mit Nachkommastellen aus – bei skalierten Schriften landen die
Icons dann zwischen zwei Pixeln und werden unscharf oder um einen Pixel
verzerrt. Der Patch rundet Höhe und Breite (mindestens 1 Pixel) und den
Versatz der Icons auf ganze Pixel, wie der Pixel-Snap aus WotLK-Extensions
(Fork von tb), dort per DLL. Icons in Originalgröße der Schrift bleiben
unverändert.

Der Code liegt in einer eigenen kleinen Sektion (`.isnap`, 179 Byte).

## Interface & Komfort

<a id="patch-tracker"></a>
**Quest-Tracker automatisch sortieren** *(Nr. 66)* 🟢 **[sicher]**

Setzt das CVar `trackerSorting` standardmäßig auf 1. Quests im Tracker werden
automatisch sortiert.

<a id="patch-worldmap"></a>
**Erweiterte Weltkarte standardmäßig aktiv** *(Nr. 67)* 🟢 **[sicher]**

Setzt das CVar `advancedWorldMap` standardmäßig auf 1. Die erweiterte
Kartenansicht ist von Anfang an aktiviert.

<a id="patch-castbars"></a>
**Cast Bars auf allen Frames** *(Nr. 68, Autor: Kebabstorm)* 🟢 **[sicher]**

Ermöglicht die Anzeige von Zauberbalken auf allen Unit-Frames (Party, Arena,
Boss etc.), nicht nur auf Target und Focus, sowie auf allen
Standard-Nameplates. Entspricht dem Verhalten ab Cataclysm.

<a id="patch-emblems"></a>
**Retail-Gildenembleme: Auswahl von 170 auf 196 erweitert** *(Nr. 69, Autor: MacWarrior)* 🟠 **[online ungetestet]**

Der Client hält die Anzahl der wählbaren Tabard-Varianten in einer kleinen
Tabelle (VA `0xA14908`, Datei-Offset `0x613108`): 170 Embleme, 17 Emblemfarben,
6 Bordüren, 17 Bordürenfarben, 51 Hintergrundfarben. Der Tabard-Designer
schaltet mit „Index modulo Zähler“ durch, das Zufalls-Tabard zieht
„rand() mal Zähler“ – beide lesen den Wert zur Laufzeit, eine zweite fest
verdrahtete 170 gibt es nirgends. Der Patch hebt den Emblem-Zähler auf die 196
von Retail an, damit fällt die Grenze vollständig.

> [!WARNING]
> **Zusätzliches MPQ-Patch-Archiv nötig.** Dieser Patch hebt ausschließlich
> den Zähler in der EXE an, er bringt keine Grafiken mit. Die 26 neuen Wappen
> (Index 170 bis 195) müssen als eigenes MPQ-Archiv im `Data`-Ordner liegen.
> Ohne dieses Archiv sind die neuen Plätze im Tabard-Designer zwar anwählbar,
> bleiben aber leer.
>
> Das passende Archiv ist **Patch-G**: [Discord](https://discord.com/channels/407664041016688662/1541873346608889936)

Der Client setzt die Dateinamen aus Emblem-Index und Farbindex zusammen, in
dieser Reihenfolge:

```
Textures\GuildEmblems\Emblem_<Index>_<Farbe>_TU_U   (obere Hälfte)
Textures\GuildEmblems\Emblem_<Index>_<Farbe>_TL_U   (untere Hälfte)
```

Die Endung `.blp` hängt der Texturlader an. Pro Wappen sind das 17 Farben × 2
Hälften = 34 Dateien, für alle 26 neuen Wappen zusammen 884. Der Archivname
ist frei wählbar (`patch-*.MPQ`), dafür sorgt der Patch
„Erweiterte MPQ-Namen erlauben“ (Nr. 21).

<a id="patch-flash"></a>
**FlashWindow Patch** *(Nr. 70, Autor: Kebabstorm)* 🟢 **[sicher]**

Lässt das WoW-Fenster in der Taskleiste blinken, wenn ein relevantes Ereignis
eintritt und das Spiel im Hintergrund läuft. Dafür wird die in 3.3.5a
funktionslose Lua-Funktion `BNRemoveFriend` durch `FlashWindow()` ersetzt, die
Addons aufrufen können (Windows-API `FlashWindow(hwnd, FALSE)`, genau wie die
Fassung in der `AwesomeWotlkLib.dll`).
**Benötigt** ein Addon, das `FlashWindow()` aufruft, z. B. das
[Flash-Addon](https://github.com/noname08662/awesome_wotlk/tree/main/addons/Flash) aus awesome_wotlk –
das braucht zusätzlich `IsWindowFocused()` aus der `AwesomeWotlkLib.dll`
(Nr. 28).

<a id="patch-charrandom"></a>
**Charaktererstellung: Aussehen nicht automatisch auswürfeln** *(Nr. 71, Autor: Alyst3r (0x539wowmod))* 🟢 **[sicher]**

Beim Öffnen der Charaktererstellung (Klick auf „Neuer Charakter“) und beim
Wechsel von Volk oder Geschlecht würfelt der Client Gesicht, Haut, Frisur usw.
nicht mehr automatisch aus, man startet mit dem Standard-Aussehen. Der
Zufall-Knopf funktioniert weiter – er nutzt im Client einen eigenen Weg.

<a id="patch-lootopen"></a>
**Lootfenster bleibt beim Laufen offen** *(Nr. 72, Autor: tb (ported by St0ny))* 🟠 **[online ungetestet]**

Im Original schließt sich das Lootfenster, sobald du läufst, seitwärts gehst
oder dich drehst. Mit dem Patch bleibt es offen. Die zehn Stellen in den
Bewegungs-Handlern, die das Fenster schließen, werden übersprungen (je ein
Byte).

<a id="patch-showlevel"></a>
**Echtes Level statt „??“ bei Gegnern ab 10 Level über dir** *(Nr. 73, Autor: tb (ported by St0ny))* 🟠 **[online ungetestet]**

Ist ein feindliches Ziel 10 oder mehr Level über dir, zeigt der Client statt
des Levels „??“ (bzw. einen Totenkopf auf der Namensplakette, `UnitLevel`
liefert -1). Mit dem Patch zeigen Tooltip, Namensplakette und `UnitLevel` das
echte Level. Bosse zeigen weiterhin „??“ – diese Prüfung bleibt erhalten, sie
nimmt Nr. 74 heraus.

<a id="patch-showlevelboss"></a>
**Echtes Level auch bei Bossen statt „??“ (Erweiterung zu Nr. 73)** *(Nr. 74, Autor: St0ny)* 🟠 **[online ungetestet]**

Kreaturen, die als Boss markiert sind (Flag in den Kreaturdaten, z. B.
Schlachtzug- und Dungeonbosse), zeigen im Original immer „??“ – im Tooltip,
auf der Namensplakette (Totenkopf) und über `UnitLevel` (-1), egal wie hoch
dein eigenes Level ist. Der Patch nimmt diese drei Boss-Prüfungen heraus, dann
steht dort das Level, das der Server für den Boss schickt. Die Beschriftung
„Boss“ im Tooltip und das Elite-Symbol der Namensplakette bleiben.

> [!NOTE]
> Ist ein Boss 10 oder mehr Level über dir, greift zusätzlich die
> Level-Prüfung – deren „??“ entfernt Nr. 73. Für alle Bosse daher zusammen mit
> Nr. 73 einspielen; der Patcher weist darauf hin, wenn Nr. 73 fehlt.

<a id="patch-holdrepeat"></a>
**Aktionstasten gedrückt halten zum Wiederholen** *(Nr. 75, Autor: tb (ported by St0ny))* 🔴 **[unsicher - Exe wird größer]**

Hältst du die Taste einer Aktionsleisten-Belegung gedrückt (die Hauptleiste,
`ACTIONBUTTON1`–`12`, mit Seiten-, Haltungs- und Gestaltleisten), löst der
Client die Aktion wiederholt aus – so wie die Option „Gedrückt halten zum
Zaubern“, die Retail-WoW seit Dragonflight hat.

- Die erste Wiederholung kommt frühestens 500 ms nach dem Drücken.
- Wiederholt wird nur, wenn die Aktion bereit ist: keine Abklingzeit (auch
  keine globale), keine laufende Zauberleiste oder Kanalisierung, kein Zauber,
  der auf sein Ziel wartet, und erst 100 ms nachdem sie wieder bereit ist.
  Danach höchstens alle 100 ms.
- Hat die Taste schon wiederholt, löst das Loslassen die Aktion nicht noch
  einmal aus. Ein kurzer Druck verhält sich wie im Original.
- Verliert das WoW-Fenster den Fokus (z. B. Alt+Tab), werden alle gehaltenen
  Tasten vergessen.

Das entspricht `actionButtonHoldRepeat = 2` (dauerhaft) aus WotLK-Extensions
(Fork von tb), dort per DLL und mit einstellbaren Zeiten. Hier sind die
Zeiten fest, der Code und die Zustände stecken in einer eigenen,
beschreibbaren Sektion (`.hrep`). Bis zu 8 Tasten können gleichzeitig gehalten
werden.

> [!WARNING]
> Server mit Anti-Cheat können das als Automatisierung (Bot) werten, viele
> Server verbieten „ein Tastendruck = mehrere Aktionen“.

<a id="patch-bubblerange"></a>
**Sprechblasen-Reichweite erhöhen (Original 25 Meter)** *(Nr. 76, Autor: St0ny)* 🟢 **[sicher]**

Der Client zeigt Sprechblasen (Sagen, Gruppe, Schreien, NPC-Sagen und
NPC-Schreien) nur für Sprecher bis 25 Meter Entfernung. Schickt der Server
zum Beispiel ein Schreien aus 100 Metern, steht es nur im Chat. Der Patch
erhöht diese Grenze; der Patcher fragt die Reichweite ab: 50 (Vorschlag), 100,
150, 200 oder 0 = unbegrenzt.

Der Client vergleicht das Quadrat des Abstands an zwei Stellen mit der
Konstante 625.0 (= 25²): beim Eintreffen der Nachricht (VA `0x7200CE`, sonst
entsteht keine Blase) und beim Aktualisieren der Blase (VA `0x56C5E9`, sonst
wird sie ausgeblendet). Dieselbe Konstante nutzen auch die Fußspuren, deshalb
bleibt sie unverändert: Der Patch lässt nur die beiden Sprechblasen-Stellen auf
eine andere, schon vorhandene Konstante zeigen (2500, 10000, 22500, 40000 oder
den größten float-Wert). Daher gibt es nur diese festen Stufen; Dateigröße und
PE-Header bleiben unverändert.

> [!NOTE]
> Eine Blase erscheint nur, wenn der Server die Nachricht schickt und der
> Sprecher für dich sichtbar ist – die Sichtweite legt der Server fest (oft um
> die 100 Meter). Sagen begrenzt der Server ohnehin auf 25 Meter, dort ändert
> sich nichts. Gruppen-Blasen erscheinen dagegen auch über weiter entfernten
> Gruppenmitgliedern.

## Fenster, Maus & Kamera

<a id="patch-window"></a>
**Fenstermodus als Standard setzen** *(Nr. 77, Autor: St0ny)* 🟢 **[sicher]**

Setzt das CVar `gxWindow` standardmäßig auf 1. Das Spiel startet im
Fenstermodus statt im Vollbild.

> [!TIP]
> **Nr. 77 und Nr. 78 gehören zusammen:** Nr. 77 schaltet den Fenstermodus ein,
> Nr. 78 maximiert das Fenster.
> - **Beide gewählt:** WoW startet als maximiertes Fenster über den ganzen
>   Bildschirm.
> - **Nur Nr. 77:** WoW startet als kleines Fenster in der Mitte des Desktops.
> - **Nur Nr. 78:** keine Wirkung, WoW startet im Vollbild. Die Option „Fenster
>   maximieren“ ist zwar aktiv, aber ausgegraut.

<a id="patch-maximize"></a>
**Fenstermodus maximiert als Standard setzen** *(Nr. 78, Autor: St0ny)* 🟢 **[sicher]**

Setzt das CVar `gxMaximize` standardmäßig auf 1. Das Fenster wird beim Start
automatisch maximiert.

> [!TIP]
> **Nr. 77 und Nr. 78 gehören zusammen:** Nr. 77 schaltet den Fenstermodus ein,
> Nr. 78 maximiert das Fenster.
> - **Beide gewählt:** WoW startet als maximiertes Fenster über den ganzen
>   Bildschirm.
> - **Nur Nr. 77:** WoW startet als kleines Fenster in der Mitte des Desktops.
> - **Nur Nr. 78:** keine Wirkung, WoW startet im Vollbild. Die Option „Fenster
>   maximieren“ ist zwar aktiv, aber ausgegraut.

<a id="patch-windowfix"></a>
**Kein schwarzer Bildschirm beim Wechsel in den Fenstermodus** *(Nr. 79, Autor: Robinsch)* 🟢 **[sicher]**

Wer im laufenden Spiel in den Fenstermodus wechselt, bekommt danach keinen
schwarzen Bildschirm mehr. Technisch nimmt der Callback des CVars
`DesktopGamma` immer den Weg über die Spiel-Gamma; der Desktop-Gamma-Weg und
damit das CVar `DesktopGamma` sind ohne Wirkung.

<a id="patch-mouse"></a>
**Mausflackern / Kamerasprünge Fix** *(Nr. 80, Autor: Robinsch)* 🟢 **[sicher]**

Ein umfangreicher Patch (4 Teile), der Probleme mit Mäusen behebt, die eine
hohe Abtastrate (Polling-Rate) verwenden. Verhindert Flackern des Mauszeigers
und unkontrollierte Kamerabewegungen.

## Sound

<a id="patch-sound"></a>
**Sound-Einstellungen optimieren** *(Nr. 81, Autor: St0ny)* 🟢 **[sicher]**

Umfasst folgende Änderungen:

- Sound-Kanal-Hardware-Limit auf 126 angehoben
- `Sound_OutputQuality` auf Maximum (2) gesetzt
- `Sound_NumChannels` von 32 auf 64 erhöht
- `Sound_EnableReverb` aktiviert (Hall-Effekt)
- `Sound_EnableHardware` aktiviert (Hardware-Audiobeschleunigung)

Das Kanal-Limit von 126 steht fest im Initialisierungscode; der Startwert 64
für `Sound_NumChannels` gilt nur an der zweiten Stelle, an der der Client das
CVar liest.

> [!IMPORTANT]
> Damit diese Einstellungen überhaupt greifen, wird **OpenAL** benötigt, z. B.
> [OpenAL Soft](https://github.com/kcat/openal-soft).

## Client-Infos: Version, Build, Titel, Datum, Icon

Diese fünf Patches von MacWarrior (portiert aus seinen Python-Skripten
`edit_version.py`, `edit_revision.py`, `edit_title.py`, `edit_date.py` und
`edit_icon.py`) ändern, wie sich der Client ausweist. Sind sie ausgewählt,
**fragt der Patcher nach der Auswahl die gewünschten Werte ab**. In eckigen
Klammern steht ein Vorschlag, ENTER übernimmt ihn. Ungültige Eingaben werden mit
einer Meldung neu abgefragt, und alle Werte werden geprüft, bevor irgendetwas
geschrieben wird. Die Werte merkt sich der Patcher in `patcher_selection.ini`
(`value.<Id>=…`); mit `-Unattended` gelten die gemerkten Werte, ohne gemerkten
Wert die Originalwerte – Ausnahmen: Build-Datum (aktueller Zeitpunkt) und Icon
(Abbruch), siehe Nr. 85 und 86. Steckt ein Patch schon in der `Wow.exe`, ist
sein aktueller Wert der Vorschlag.
Bei der Abfrage steht er auch hinter dem Patchnamen (`-> Vorschlag: …`, bei einem
bereits eingespielten Patch `-> aktuell: …`).

> [!NOTE]
> Server können die Client-Version bzw. Build-Nummer prüfen. Ein geänderter Wert
> muss also zum Server passen.

<a id="patch-clientversion"></a>
**Client-Version ändern (Original 3.3.5)** *(Nr. 82, Autor: MacWarrior)* 🔴 **[unsicher]**

Setzt eine neue Version im Format `x.y.z` (z. B. `3.3.6` oder `3.3.123`, höchstens
7 Zeichen). Geändert werden die Version, die der Client im Spiel anzeigt, die
FileVersion und die ProductVersion (`Version x.y`) der Versionsressource sowie
`VS_FIXEDFILEINFO`. Die Build-Nummer in `VS_FIXEDFILEINFO` bleibt erhalten; der
FileVersion-Text (`3, 3, 5, 12340`) wird zur reinen Version (`3.3.6`). Haupt-
und Nebenversion müssen zusammen in das ProductVersion-Feld passen (z. B. `3.3`).

<a id="patch-clientbuild"></a>
**Build-Nummer ändern (Original 12340)** *(Nr. 83, Autor: MacWarrior)* 🔴 **[unsicher]**

Setzt eine neue Build-Nummer (6142 bis 65535, Original `12340`): die interne
Build-Nummer, die sichtbare Build-Nummer und den vierten Teil der FileVersion
in `VS_FIXEDFILEINFO`. Die Texte `3, 3, 5, 12340` (FileVersion-Text) und
`WoW [Release] Build 12340 (…)` bleiben unverändert.
Builds bis 6141 lässt der Patcher nicht zu: Server wie AzerothCore oder
TrinityCore halten den Client dann für einen Classic-Client (Pre-BC) und
verwenden ein anderes Login-Protokoll – ein 3.3.5-Client kommt so nicht mehr auf
den Server.

> [!TIP]
> **AzerothCore:** Der Authserver lässt nur Builds zu, die in der Tabelle
> `build_info` der Auth-Datenbank stehen. Für einen eigenen Build, z. B. `12341`:
>
> ```sql
> INSERT INTO build_info (majorVersion, minorVersion, bugfixVersion, hotfixVersion, build, winChecksumSeed, macChecksumSeed)
> VALUES (3, 3, 5, 'a', 12341, NULL, NULL);
> UPDATE realmlist SET gamebuild = 12341 WHERE id = 1;
> ```
>
> `winChecksumSeed` leer lassen (wird nur mit `StrictVersionCheck = 1` in der
> `authserver.conf` geprüft und passt zu einer gepatchten Exe ohnehin nicht).
> Major/Minor/Bugfix sind nur Anzeige in der Realmliste. Danach den Authserver
> neu starten – er liest `build_info` nur beim Start. Ein Realm nimmt nur den
> Build aus `realmlist.gamebuild` an; Spieler mit älterem Client sehen ihn als
> offline.

<a id="patch-clienttitle"></a>
**Programmtitel ändern (Dateieigenschaften und Fenstertitel)** *(Nr. 84, Autor: MacWarrior (fixed by St0ny))* 🔴 **[unsicher]**

Setzt FileDescription, InternalName und ProductName der Versionsressource, also
das, was Windows z. B. in den Dateieigenschaften und im Task-Manager anzeigt.
Höchstens 17 Zeichen, nur ASCII.

Dazu ändert der Patch den Titel des Spielfensters: WoW legt sein Fenster mit
dem Text „World of Warcraft“ an (Datei-Offset `0x5E0288`) und setzt den Titel
danach noch zweimal neu (Aufrufe bei VA `0x76A119` und `0x76B204`). Der Patch
schreibt den eigenen Titel an die erste Stelle und schaltet die beiden Aufrufe
ab, damit er stehen bleibt.

> [!NOTE]
> Der Text bei `0x5E0288` wird im Client auch an anderen Stellen benutzt, z. B.
> wohl als Titel von Fehlermeldungen – dort erscheint dann ebenfalls der eigene
> Titel.

<a id="patch-clientdate"></a>
**Build-Datum ändern (Original Jun 24 2010)** *(Nr. 85, Autor: St0ny (original by MacWarrior))* 🔴 **[unsicher]**

Setzt das Build-Datum (Original `Jun 24 2010`) an allen drei Stellen in der EXE
und das Jahr im Copyright-Vermerk, dazu die Uhrzeit. Die steht an zwei Stellen:
im Build-Text `WoW [Release] Build 12340 (Jun 24 2010 23:54:57)` und als
Zeitstempel im Programmkopf, den Analyse-Werkzeuge als Erstellungszeit der
`Wow.exe` anzeigen (Original 25.06.2010 06:55:58 UTC). Datum und Uhrzeit gelten
als Ortszeit des Rechners, auf dem du patchst.

Eingabe als `JJJJ-MM-TT HH:MM:SS`, optional mit `FR` dahinter für französische
Monatsnamen (z. B. `2026-09-28 14:30:15 FR` → `Sep 28 2026 14:30:15`). Ohne
Sekunden (`14:30`) nimmt der Patcher `00`. Als Vorschlag steht in den Klammern
**„Zeitpunkt der Bestätigung mit J“** (mit `FR`, wenn du das zuletzt gewählt
hast): Übernimmst du ihn mit ENTER, setzt der Patcher Datum und Uhrzeit des
Rechners in dem Moment, in dem du das Patchen mit `J` bestätigst. Mit
`-Unattended` gilt der gemerkte Wert, ohne gemerkten Wert der Zeitpunkt des
Patchens. Ist der Patch schon eingespielt, steht dort das aktuelle Datum samt
Uhrzeit der `Wow.exe`.

<a id="patch-clienticon"></a>
**Programm-Icon ändern (Symbol der Wow.exe)** *(Nr. 86, Autor: St0ny (original by MacWarrior))* 🔴 **[unsicher]**

Tauscht das Icon aus, das Windows für die `Wow.exe` anzeigt (Explorer,
Taskleiste, Verknüpfungen). Der Patcher fragt nach dem Pfad einer `.ico`-
oder `.png`-Datei, absolut oder relativ zum Ordner der `Wow.exe`. Aus der Datei baut er
die vier Größen, die in der `Wow.exe` stecken (48, 32, 24 und 16 Pixel, je
32 Bit mit Alphakanal): Ist eine Größe in der ICO enthalten, wird sie direkt
übernommen, sonst wird das nächstgrößere Bild per Flächenmittelung
herunterskaliert (zur Not das größte hochskaliert). Eine PNG liefert alle vier
Größen durch Skalieren. Transparenz bleibt erhalten.

MacWarriors `edit_icon.py` tauscht die Ressourcen über die Windows-API aus, was
die `.rsrc`-Sektion neu schreibt. Hier werden stattdessen nur die Bilddaten der
acht vorhandenen Icon-Bitmaps (vier Größen in zwei Sprachvarianten) an Ort und
Stelle überschrieben – gleiche Größe, gleiche Bittiefe, gleicher Platz.
Ressourcenverzeichnis, Offsets und Dateigröße bleiben unverändert, und der
Patch lässt sich wie jeder andere wieder zurücknehmen. Die anderen Patches
verschieben sich dadurch nicht, auch nicht die, die eine Sektion anhängen: Sie
landen hinter dem Dateiende, die Icon-Bilder liegen davor. Vor dem Schreiben
prüft der Patcher im Ressourcenverzeichnis, dass an allen acht Stellen
tatsächlich ein Icon-Bild genau dieser Größe liegt. Stimmt das nicht, bricht er
ab, ohne etwas zu schreiben. ICO-Bilder in BMP-Form (1, 4, 8, 16, 24 oder
32 Bit) und PNG (nicht interlaced) liest der Patcher selbst, ohne
Zusatzmodule. Der Pfad wird in `patcher_selection.ini` gemerkt;
mit `-Unattended` muss er dort stehen, sonst bricht der Patcher mit einer
Meldung ab.

> [!NOTE]
> Zeigt der Explorer danach noch das alte Icon, liegt das am Icon-Cache von
> Windows: `Wow.exe` kurz umbenennen oder in einen anderen Ordner kopieren,
> Verknüpfungen neu anlegen oder den Explorer neu starten. Das Icon im Spiel
> selbst (Fenstertitel) kommt ebenfalls aus diesen Ressourcen.

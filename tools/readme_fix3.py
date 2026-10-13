import re,sys
def rep(s,o,n,p):
    c=s.count(o)
    if c!=1: sys.exit(f'{p}: count {c} for {o[:100]!r}')
    return s.replace(o,n)
def row(s,num,new,p):
    s2,k=re.subn(r'(?m)^\| %d +\|.*$'%num,lambda m_: new,s); 
    if k!=1: sys.exit(f'{p}: row {num} count {k}')
    return s2
DISC='https://discord.com/channels/858041817043042364/1515439916878663701'
# ---------------- German
p='README.md'; s=open(p,encoding='utf-8',newline='').read()
s=rep(s,"Deaktiviert den Warden-Scan-DLL-Mechanismus im Client.\n",
"""Verhindert das Laden der `Scan.dll`, die der Login-Server per „Scan“-Befehl
nachladen kann (ein Prüfmodul des Login-Servers, unabhängig von Warden): Aus
`.\\Scan.dll` und `.\\Scan.dll.new` wird `.\\||an.dll` – `|` ist in Dateinamen
verboten, das Laden schlägt damit garantiert fehl.
""",p)
s=rep(s,"**AFK-Timer / IDLE-Check deaktivieren** *(Nr. 13, standardmäßig aus, Autor: St0ny)*",
        "**Idle-Kick nach Character-Autologin verhindern** *(Nr. 13, standardmäßig aus, Autor: St0ny)*",p)
s=rep(s,"""Deaktiviert den IDLE-Login-Check, lässt den automatischen
AFK-Disconnect-Timer aber aktiv. Verhindert gleichzeitig den
CharAutoLogin-Bug.
""","""Nach einem Autologin ohne jede Tastatur- oder Mauseingabe steht der
Zeitstempel der letzten Eingabe noch auf 0 – der Client hält den Spieler sofort
für untätig und kickt ihn (CharAutoLogin-Bug). Der Patch setzt den Zeitstempel
beim ersten Durchlauf auf „jetzt“, wenn er noch leer ist, und entfernt einen
Fatal-Error-Check, der dabei auslösen kann. Die eigentlichen Timer bleiben
unverändert: AFK-Status nach 5 Minuten, Logout nach 30 Minuten ohne Eingabe.
""",p)
s=row(s,13,"| 13 | Idle-Kick nach Character-Autologin verhindern *(wird für Character-Autologin benötigt; AFK- und Idle-Timer bleiben aktiv, [Discord](%s))* | St0ny | – | – |"%DISC,p)
s=rep(s,"""Ermöglicht Änderungen am Login- und Charakterauswahl-Bildschirm durch eigene
XML/Lua-Dateien (Glue-Screen-Modding).
""","""Ermöglicht Änderungen am Login- und Charakterauswahl-Bildschirm durch eigene
XML/Lua-Dateien (Glue-Screen-Modding): Die Signaturprüfung der Interface-Dateien
meldet immer „gültig“, und lokale Ordner `Interface\\GlueXML` und
`Interface\\FrameXML` werden nicht mehr in `*.old` umbenannt.

> [!NOTE]
> Nebenwirkung, die jede Fassung dieses Patches hat: Auch Addons ohne
> Signaturdatei gelten damit als „sicher“ (wie Blizzard-Code) und dürfen
> geschützte Funktionen aufrufen – in der Wirkung ähnlich dem LUA Unlock
> (Nr. 18). Server mit Anti-Cheat können das genauso werten.

Die verbreitete Fassung (Alastor/Kebabstorm) läuft bei fehlender Signaturdatei
mit uninitialisierten Variablen weiter und gibt dabei einen Zeiger ins Nichts
frei (undefiniertes Verhalten). Hier gibt der Fehlerausgang stattdessen direkt
„gültig“ zurück – gleiche Wirkung, ohne wilden Speicherzugriff.
""",p)
s=rep(s,"""Erlaubt das Laden von MPQ-Archiven ohne gültige Signatur. Notwendig für
Custom-Content auf privaten Servern.
""","""Die Signaturprüfung für MPQ-Archive meldet immer „gültig“. Der Client prüft
damit nur Archive, die der Server schickt: `wow-patch.mpq` (Client-Patch vom
Server) und `Cache\\Survey.mpq` (Hardware-Umfrage). Die normalen `Data\\*.MPQ`
lädt der Client ohnehin ohne Signaturprüfung – für eigene Patch-MPQs ist dieser
Patch also nicht nötig. Zusammen mit Nr. 8 und Nr. 9 hat er keine Wirkung mehr,
weil beide Wege dann gar nicht erst laufen.
""",p)
s=rep(s,"""Addons und Makros dürfen geschützte Funktionen aufrufen, z. B.
`CastSpellByName`, `CastSpellByID`, `TargetUnit`, `FocusUnit`, `InteractUnit`,
Bewegungsfunktionen oder `ReloadUI`. `AttackTarget` meldet weiterhin einen
Fehler.
""","""Addons und Makros dürfen geschützte Funktionen aufrufen: Bewegungsfunktionen
(`MoveForwardStart`, `TurnLeftStart`, …), `CastSpellByName`, `CastSpell`,
`UseAction`, `PetAttack`, `RunMacro`/`RunMacroText` und die
GM-Ticket-Funktionen. Nicht freigegeben, weil sie eigene Prüfungen im Code
haben: `TargetUnit`, `FocusUnit`, `InteractUnit`, `ReloadUI`; `AttackTarget`
meldet weiterhin einen Fehler.
""",p)
s=rep(s,"""Gehört zusammen mit dem 4GB-Patch (Nr. 1); fehlt der in der Auswahl, weist der
Patcher darauf hin.
""","""Gehört zusammen mit dem 4GB-Patch (Nr. 1); fehlt der in der Auswahl, weist der
Patcher darauf hin.

Der Lader sitzt am Start der Haupt-Fiber des Clients (kurz vor `WinMain`) und
überschreibt dafür den Anfang der Scan.dll-Startfunktion; die Lua-Funktion
`ScanDLLStart` wird zum Leerlauf und das Scan.dll-Flag auf „bestanden“ gesetzt.
Der Patch schaltet damit nebenbei den Scan.dll-Mechanismus ab (wie Nr. 7).
Fehlt die DLL, startet WoW normal weiter.
""",p)
s=rep(s,"**Level 101+ Fix (Druiden-Grundwerte und Barbierstuhl)** *(Nr. 31, standardmäßig aus, Autor: Alastor StrixEfuartus)*",
        "**Level 101+ Fix (Spielwert-Tabellen, Barbierstuhl, Grundwerte)** *(Nr. 31, standardmäßig aus, Autor: Alastor StrixEfuartus / St0ny)*",p)
s=rep(s,"""Druiden ab Level 101 können ihre Grundwerte wieder ansehen, und der
Barbierstuhl funktioniert für alle Charaktere ab Level 101.
**Benötigt** den Patch „Custom Glue-XML erlauben“ (Nr. 14). In der Quelle
heißt er „Disable XML SIG MD5“, daher der dortige Hinweis „Use XML MD5“.
""","""Die Spielwert-Tabellen des Clients (`gtCombatRatings`, `gtBarberShopCostBase`,
`gtOCTRegenHP`/`MP`, `gtChanceToMeleeCrit` … – elf Tabellen) haben je Spalte
100 Zeilen, eine pro Level. Ab Level 101 greift der Client außerhalb der Spalte
zu – Druiden sehen ihre Grundwerte nicht mehr, der Barbierstuhl funktioniert
nicht, im schlimmsten Fall stürzt der Client ab. Der Patch begrenzt die Zeile
auf die letzte der Spalte: Level 101+ bekommt die Werte für Level 100, alles
darunter bleibt unverändert.

> [!NOTE]
> Die verbreitete Fassung aus der 12th Generation EXE entfernt stattdessen das
> Level komplett aus der Rechnung – damit zeigen *alle* Charaktere die Werte
> für Level 1 (Wertungen, kritische Trefferchance, Regeneration …). Hier sind
> die beiden Zugriffsfunktionen (VA `0x7F69B0` und `0x7F69E0`) dafür neu
> geschrieben.

**Benötigt** laut Quelle den Patch „Custom Glue-XML erlauben“ (Nr. 14). In der
Quelle heißt er „Disable XML SIG MD5“, daher der dortige Hinweis „Use XML MD5“.
""",p)
s=row(s,31,"| 31 | Level 101+ Fix (Spielwert-Tabellen, Barbierstuhl, Grundwerte) | Alastor StrixEfuartus / St0ny | – | ✅ |",p)
s=rep(s,"**Unbegrenzte Rasse/Klasse-Kombinationen** *(Nr. 32, standardmäßig aus, Autor: Alastor StrixEfuartus / Robinsch)*",
        "**Charaktererstellung: mehr als 10 Klassen (Zufallsklasse)** *(Nr. 32, standardmäßig aus, Autor: Alastor StrixEfuartus / Robinsch)*",p)
s=rep(s,"""Die Charaktererstellung lässt jede Rasse mit jeder Klasse zu. Der Server muss
das ebenfalls unterstützen.
""","""Die Zufallsauswahl der Klasse bei der Charaktererstellung sammelt die
erlaubten Klassen in einem Feld mit 10 Plätzen. Mit eigenen Klassen
(`ChrClasses.dbc` mit mehr als 10 Einträgen) würde es überlaufen; der Patch
vergrößert es auf 30 Plätze. Welche Rasse welche Klasse darf, prüft weiterhin
der Server – mehr macht dieser Patch nicht.
""",p)
s=row(s,32,"| 32 | Charaktererstellung: mehr als 10 Klassen (Zufallsklasse) *(für eigene Klassen; Server muss es unterstützen)* | Alastor StrixEfuartus / Robinsch | – | – |",p)
s=rep(s,"""(also auch den Wert aus „Sprunghöhe ändern“, Nr. 37). Den doppelten Sprung aus
0x539wowmod mit eigener zweiter Sprunghöhe gibt es hier nicht.
""","""(also auch den Wert aus „Sprunghöhe ändern“, Nr. 37). Den doppelten Sprung aus
0x539wowmod mit eigener zweiter Sprunghöhe gibt es hier nicht. Der Zähler wird
erst beim nächsten Sprung vom Boden neu gesetzt, nicht beim Landen: Wer nach
einem Sprung landet und dann von einer Kante läuft, hat in der Luft wieder die
gewählte Anzahl Sprünge.
""",p)
s=rep(s,"""Entfernt die Obergrenze des CVars `environmentDetail` komplett. Original wird
der Wert auf den Bereich 0.5 bis 1.5 begrenzt; der Patch hebelt die obere
Begrenzung aus, sodass beliebig hohe Werte durchgereicht werden.
""","""Entfernt die Obergrenze des CVars `environmentDetail` komplett. Original wird
der Wert auf den Bereich 0.5 bis 1.5 begrenzt; der Patch ersetzt am gemeinsamen
Ausgang der Prüfung den geklemmten Wert durch den Rohwert – damit fällt auch
die Untergrenze 0.5 weg, beliebige Werte werden durchgereicht (sinnvoll sind
Werte ab 0.5).
""",p)
s=rep(s,"""Erhöht den Occluder-Schwellenwert für Stormwind, damit Gebäude und Objekte
nicht fälschlicherweise ausgeblendet werden. Behebt Grafikfehler auf
Custom-Servern mit umgebautem Stormwind.
""","""Schaltet die fest in den Client eingebauten Occluder (Sichtblocker) für
Stormwind ab: Der Karten-Schlüssel des Tabelleneintrags für die Östlichen
Königreiche wird auf 99999 gesetzt, sodass er zu keiner Karte mehr passt. So
werden auf Custom-Servern mit umgebautem Stormwind keine Gebäude und Objekte
mehr fälschlich ausgeblendet.
""",p)
s=rep(s,"""Der eigene Charakter wird nicht mehr durchsichtig, wenn die Kamera nah
herangezoomt wird.
""","""Der eigene Charakter wird nicht mehr durchsichtig, wenn die Kamera nah
herangezoomt wird. Der Patch entfernt die Transparenz-Zuweisung für den
Normalfall; sitzt der Charakter in einem Fahrzeug oder hängt an einem anderen
Objekt, kann er beim Heranzoomen weiterhin durchsichtig werden (so auch im
Original-Patch).
""",p)
s=rep(s,"""Lässt das WoW-Fenster in der Taskleiste blinken, wenn ein
relevantes Ereignis eintritt und das Spiel im Hintergrund läuft.
Die Funktion kann per Addon angesprochen werden.
**Benötigt** das [FlashWindow-Addon](https://github.com/noname08662/awesome_wotlk/tree/main/addons/Flash) aus awesome_wotlk.
""","""Lässt das WoW-Fenster in der Taskleiste blinken, wenn ein relevantes Ereignis
eintritt und das Spiel im Hintergrund läuft. Dafür wird die in 3.3.5a
funktionslose Lua-Funktion `BNRemoveFriend` durch `FlashWindow()` ersetzt, die
Addons aufrufen können (Windows-API `FlashWindow(hwnd, FALSE)`, genau wie die
Fassung in der `AwesomeWotlkLib.dll`).
**Benötigt** ein Addon, das `FlashWindow()` aufruft, z. B. das
[Flash-Addon](https://github.com/noname08662/awesome_wotlk/tree/main/addons/Flash) aus awesome_wotlk –
das braucht zusätzlich `IsWindowFocused()` aus der `AwesomeWotlkLib.dll`
(Nr. 21).
""",p)
s=rep(s,"""Wer im laufenden Spiel in den Fenstermodus wechselt, bekommt danach keinen
schwarzen Bildschirm mehr.
""","""Wer im laufenden Spiel in den Fenstermodus wechselt, bekommt danach keinen
schwarzen Bildschirm mehr. Technisch nimmt der Callback des CVars
`DesktopGamma` immer den Weg über die Spiel-Gamma; der Desktop-Gamma-Weg und
damit das CVar `DesktopGamma` sind ohne Wirkung.
""",p)
s=rep(s,"**CameraReforged [BETA]: Kamerahöhe, Schulterversatz, Zoom-Grenzen** *(Nr. 64, standardmäßig aus, Autor: Stormhand / St0ny)*",
        "**CameraReforged [BETA]: Kamerahöhe und Zoom-Grenzen** *(Nr. 64, standardmäßig aus, Autor: Stormhand / St0ny)*",p)
s=row(s,64,"| 64 | CameraReforged [BETA]: Kamerahöhe und Zoom-Grenzen *(Schulterversatz noch ohne Wirkung; Exe wird größer – Bann-Gefahr)* | Stormhand / St0ny | – | – |",p)
s=rep(s,"""> **BETA** – dieser Patch funktioniert noch nicht zu 100 %, hier fließt noch
> Arbeit hinein. Deshalb ist er standardmäßig abgewählt.
""","""> **BETA** – dieser Patch funktioniert noch nicht zu 100 %, hier fließt noch
> Arbeit hinein. Deshalb ist er standardmäßig abgewählt. Der Schulterversatz
> (`test_cameraOverShoulder`) hat derzeit keine Wirkung: Die vier Lesestellen,
> die die Vorlage dafür umbiegt, gehören nicht zur Kamera, sondern zum
> Chat-Fenster (Anzeigedauer der Nachrichten). Sie bleiben hier unangetastet.
""",p)
s=rep(s,"| `test_cameraOverShoulder` | (fehlt)  | 0.00  | -2.0 bis 2.0  |",
        "| `test_cameraOverShoulder` | (fehlt)  | 0.00  | -2.0 bis 2.0 (ohne Wirkung) |",p)
s=rep(s,"""- `test_cameraOverShoulder` verschiebt die Kamera seitlich, negative Werte nach
  links. 0 lässt sie mittig, alles andere ergibt eine Schulterperspektive.
""","""- `test_cameraOverShoulder` soll die Kamera seitlich verschieben, negative
  Werte nach links – derzeit ohne Wirkung (siehe oben).
""",p)
s=rep(s,"""Detour auf den Kamera-Fokuspfad (dort kommt die Höhe drauf), zwei umgebogene
Vorgabewert-Zeiger und vier umgebogene Lesestellen für den Schulterversatz.
""","""Detour auf den Kamera-Fokuspfad (dort kommt die Höhe drauf) und zwei umgebogene
Vorgabewert-Zeiger.
""",p)
s=rep(s,"""- `Sound_EnableHardware` aktiviert (Hardware-Audiobeschleunigung)
""","""- `Sound_EnableHardware` aktiviert (Hardware-Audiobeschleunigung)

Das Kanal-Limit von 126 steht fest im Initialisierungscode; der Startwert 64
für `Sound_NumChannels` gilt nur an der zweiten Stelle, an der der Client das
CVar liest.
""",p)
s=rep(s,"""`VS_FIXEDFILEINFO`. Die Build-Nummer bleibt erhalten. Haupt- und Nebenversion
müssen zusammen in das ProductVersion-Feld passen (z. B. `3.3`).
""","""`VS_FIXEDFILEINFO`. Die Build-Nummer in `VS_FIXEDFILEINFO` bleibt erhalten; der
FileVersion-Text (`3, 3, 5, 12340`) wird zur reinen Version (`3.3.6`). Haupt-
und Nebenversion müssen zusammen in das ProductVersion-Feld passen (z. B. `3.3`).
""",p)
s=rep(s,"""Setzt eine neue Build-Nummer (6142 bis 65535, Original `12340`): die interne
Build-Nummer, die sichtbare Build-Nummer und den vierten Teil der FileVersion.
""","""Setzt eine neue Build-Nummer (6142 bis 65535, Original `12340`): die interne
Build-Nummer, die sichtbare Build-Nummer und den vierten Teil der FileVersion
in `VS_FIXEDFILEINFO`. Die Texte `3, 3, 5, 12340` (FileVersion-Text) und
`WoW [Release] Build 12340 (…)` bleiben unverändert.
""",p)
s=rep(s,"## Danksagung\n","""## Entfernte Patches

Zwei Patches aus Robinschs Sammlung, die frühere Versionen dieses Patchers
enthielten, sind nach der Codeprüfung entfernt – ihre Offsets passen nicht zu
dieser `Wow.exe`:

- **„Geister“-Angriff von NPCs beim Evade behoben** (`0x355BF`: `E8` → `EB`).
  Das Byte macht aus einem `call` in einer String-Hilfsfunktion (VA `0x4361BF`)
  einen Rücksprung um 5 Byte – eine Endlosschleife, die bei jedem Durchlauf
  4 Byte auf den Stack legt, bis der Client abstürzt. Die Funktion wird selten
  aufgerufen, deshalb fiel das im Spiel nicht auf.
- **Nackter-Charakter-Bug behoben** (`0x1DDC5D`: `00` → `EB`). Das Byte ist
  das Argument eines `push 0` in der Lua-Funktion `GetTradeSkillTools`
  (VA `0x5DE85C`) und macht daraus `push -21` – es verfälscht nur einen
  Parameter der Berufe-Werkzeugprüfung und hat nichts mit `SPELL_AURA_X_RAY`
  zu tun.

Eine `Wow.exe`, die noch mit diesen beiden Patches erstellt wurde, erkennt der
Patcher ohne `patcher_state.ini` nicht mehr: dann `Wow.exe.ORI` zurückkopieren
und neu patchen.

## Danksagung
""",p)
open(p,'w',encoding='utf-8',newline='').write(s); print('de ok')

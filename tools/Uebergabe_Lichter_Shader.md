# Übergabe: Shader für 8 Punktlichter (WoW 3.3.5a, Build 12340)

Projektauftrag für einen neuen Agenten. Ziel: neue Vertex-Shader, die die von der
Exe schon gelieferten Punktlichter 5–8 darstellen. Die Exe-Seite ist fertig (Patch
„Mehr Lichter“), sie wird hier nicht geändert.

## 1. Arbeitsregeln des Users (bitte genau einhalten)

- Immer auf **Deutsch** antworten.
- **Nichts committen oder pushen ohne ausdrückliches OK** des Users. Vor einem Push
  sagen, was gepusht wird. Kein Force-Push, keine PRs, **niemals Zweige mergen
  oder vermischen**.
- Commits mit `git -c user.name=Claude -c user.email=noreply@anthropic.com commit`.
  Die Nachricht endet nur mit `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  Keine privaten Bemerkungen des Users in Commit-Nachrichten.
- Vor jedem Push `git ls-remote origin <branch>` prüfen.
- `apply_patches.ps1` ist reines ASCII mit CRLF, die `.md`-Dateien UTF-8 mit LF.
- Niemals eine Test-`Wow.exe` und **keine Blizzard-Dateien** (auch keine
  veränderten Shader) ins Repo legen (Lizenz, wie damals bei CameraReforged).
  Ins Repo darf nur eigenes Werkzeug, das die Dateien des Users bei ihm umbaut.
- Patches werden mit ihrer Nummer genannt. Dev-Patches sind mit [BETA] markiert.
  Autoren ohne Links nennen.
- Der User arbeitet gern mit Agenten. Hilfsagenten arbeiten nur in eigenen
  Scratch-Ordnern und ohne git.

## 2. Repo und Stand

- Repo: `Raz0r1337/St0nys-AIO-WoW-EXE-Patcher`. Die alte Adresse
  `…/St0nys-WoW-EXE-Patcher` leitet weiter.
- Zweig mit dem Lichter-Patch: **`st0ny-dev-lights`**, Stand `d83df5c`. Der Zweig
  wird gerade auf den aktuellen `st0ny-dev` gebracht, danach ändern sich die
  Nummern. Vor Beginn neu prüfen.
- Patch **Nr. 66 „Mehr Lichter: 8 statt 4 Punktlichter (Grundlage für neue
  Shader) [BETA]“**, Anker `patch-lights` in `docs/PATCHES.de.md` / `.en.md`.
  - Code im Patcher: `apply_patches.ps1`, Block mit dem Kopfkommentar
    „Mehr Lichter: 8 statt 4 Punktlichter“ (eigene Sektion `.lght`, 0x590 Byte).
- Patch **Nr. 67 „Lichter bleiben an, wenn ihre Quelle außerhalb des Bildes ist
  [BETA]“** (Anker `patch-lightstay`, 1 Byte bei VA `0x81E548`, `je` → `jmp`).
  - Zum Testen sinnvoll, sonst gehen Lichter aus, sobald die Quelle aus dem Bild
    gedreht wird.
  - Kleiner Doku-Fehler im Lichter-Zweig: Der TIP bei Nr. 66 verweist auf
    „Nr. 68“, gemeint ist Nr. 67.

## 3. Was die Exe liefert (Nr. 66)

- Das Spiel sammelt je Modell, Gebäude und Bodenstück die nächsten Lichter in
  `CM2Lighting` (0xD4 Byte, Lichter +0x84, Abstände +0x94, Anzahl +0xA4).
  - Original: höchstens 4.
  - Patch: Licht 5–8 kommt in eine Zusatzliste (Ring, 320 KB, beim ersten Bedarf
    angelegt).
- Exe-Stellen: AddLight (VA `0x834FC7` / `0x834FCD`), TransformLights
  (VA `0x83510E`, Zusatzlichter in Kamerasicht).
- **Shader-Weg:** Nach dem Original lädt die Exe Licht 5–8 im selben Format wie
  Licht 1–4 in die Vertex-Shader-Register **c236–c246**:
  - VA `0x873E85` für Modelle (M2).
  - VA `0x7A91A9` für Gebäude (WMO).
  - Das passiert nur, wenn die Karte mindestens 247 VS-Konstanten hat. Jede Karte
    mit Shader-Modell 2 oder 3 hat 256.
- **Weg ohne Shader** (`/console fixedFunction 1`, Neustart): 8 Lichtplätze am
  Gx-Gerät, SetupGxLights (VA `0x8353D0`) belegt Slot 1–7. Damit lässt sich die
  Exe-Seite ohne neue Shader prüfen.

Registerbelegung (Vertex-Shader, Modelle und Gebäude):

| Register | Inhalt |
|---|---|
| c17–c20 / c236–c239 | Farbe von Licht 1–4 / 5–8 (rgb, w = 1; freier Platz = 0) |
| c21–c24 / c240–c243 | Position von Licht 1–4 / 5–8 in Kamerasicht (xyz, w = 1) |
| c25 / c244 | Abschwächung 0 von Licht 1–4 / 5–8 (x = erstes … w = viertes Licht) |
| c26 / c245 | Abschwächung 1, Aufteilung wie oben |
| c27 / c246 | Abschwächung 2, Aufteilung wie oben |

**Shader-Auswahl:** Sie bleibt unverändert. Ab 4 Lichtern nimmt das Spiel die
Varianten für „4 Lichter“, in jeder `Diffuse_*.bls` die Varianten **9, 19, …, 89**.
- Nur diese Varianten brauchen den Zusatzcode für c236–c246.
- Anzahl und Reihenfolge der Varianten müssen gleich bleiben.
- Bei weniger als 5 Lichtern sind die Farben in c236–c239 = 0. Der Zusatzcode
  muss das ohne Sonderfall vertragen (Farbe 0 → kein Beitrag).

**Nicht im Umfang:**
- Boden und Wasser bleiben im Shader-Weg bei 3 Lichtern. Sie haben eigene Shader
  und einen eigenen Datenweg (spätere Stufe).
- Der OpenGL-Weg (`arbvp1`) bleibt unverändert.

## 4. Woher die Shader kommen (aus der Original-Exe ermittelt)

- Pfad, den die Exe baut: Formatstring `"%s\%s\%s.bls"` (VA `0xA2DBA8`), benutzt
  in der Ladefunktion VA `0x684970` (Aufruf bei `0x6849B5`):
  `<Basis>\<Profil>\<Name>.bls`.
  - Basis: `Shaders\Vertex` bzw. `Shaders\Pixel`.
  - Beispiel: `Shaders\Vertex\vs_3_0\Diffuse_T1.bls`.
- Profilnamen (Tabelle VA `0xAD8890`, Vertex-Typ):
  `none, vs_1_1, vs_2_0, vs_3_0, vs_4_0, vs_5_0, arbvp1, arbvp1_cg12`.
- **Rückfall beim Laden** (VA `0x684A4C` ff.): Fehlt die Datei für ein Profil,
  versucht das Spiel das nächstkleinere, bei Vertex-Shadern
  `vs_3_0` → `vs_2_0` → `vs_1_1`.
  - Neue Shader also für **vs_3_0 und vs_2_0** liefern. Sonst lädt das Spiel auf
    SM3-Karten weiter das Original aus `vs_3_0`.
  - `vs_1_1` kann c236 nicht ansprechen (zu wenige Konstanten). Diese Varianten
    bleiben bei 4 Lichtern.
- Dateikopf der `.bls` (Prüfung bei VA `0x6849E3`/`0x6849FE`):
  - Magic `0x47585348` als DWORD (Bytes `48 53 58 47`, „HSXG“).
  - Version `0x10003`.
  - Danach ein DWORD, dann je Variante ein Block, den das Shader-Objekt über seine
    vtable-Methode 0 selbst einliest (VA `0x684A2B`, Lesehilfe `0x422530`).
  - Den genauen Aufbau je Variante (Bytecode-Länge, Konstanten-/Parameter-Infos)
    am Code und an den Originaldateien klären.
  - Sicherheitsnetz: Auspacken und Wiedereinpacken muss **bitgleich** sein.
- Datei öffnen: `0x424F80` → `0x424B50` (Spiel-Dateisystem, MPQ).

**Wohin mit den neuen Dateien:**
- Am saubersten in ein eigenes Patch-MPQ im `Data`-Ordner, z. B. `patch-5.MPQ`.
  - `Data\*.MPQ` lädt der Client ohne Signaturprüfung.
  - Mit Nr. 21 gehen auch Namen wie `patch-*.MPQ`.
- Oder lose im Data-Ordner, wenn Nr. 22 („Daten direkt aus dem Data-Ordner
  laden“) aktiv ist, z. B. `Data\Shaders\Vertex\vs_3_0\Diffuse_T1.bls`.
  Prüfen, ob Nr. 22 auch für diesen Ladeweg (`0x424B50`) greift.

## 4b. Frühere Recherche (Oktober, teils verifiziert – vor Gebrauch gegenprüfen)

- **Laden:** ShaderCreate über `[0xC5DF88]`-vtable +0x110 (D3D9 `0x6AA130`)
  → Basis `0x6897C0` (Hash je Typ, Schlüssel Name bzw. `"%s:%d"`) → Lader
  `0x684970`.
  - Typ 0 = VS, 4 = PS.
  - Profil-Index bei Gerät +0x2C8 (VS) / +0x2D8 (PS).
- **BLS je Variante** (`CGxShader::Load` `0x689A70`): `u32, u32, u16, u16, u32
  size, Bytecode[size]`, dann Auffüllung auf 4 Byte.
  - Das DWORD „Anzahl“ im Kopf wird ignoriert, es zählt die Anzahl, die der
    Aufrufer erwartet.
  - Der Bytecode geht unverändert an CreateVertexShader (`0x6AA105`) bzw.
    CreatePixelShader (`0x6AA0A5`), angelegt erst beim ersten Binden
    (`0x6AA2F0` / `0x6AA210`).
- **M2:** `0x872D30` erwartet **90 VS-Varianten** (push 0x5A bei `0x872DA0`)
  und **16 PS-Varianten** (push 0x10 bei `0x872DC5`).
  - VS-Namen: `Diffuse_T1`, `Diffuse_T2`, `Diffuse_Env`, `Diffuse_T1_T2`,
    `Diffuse_T1_Env`, `Diffuse_Env_T2`, `Diffuse_Env_Env`.
  - PS-Namen: `Combiners_*`.
  - Effekt-Dateien `.wfx` (MapObj, MapObjU, Model2, Particle, ShadowMap) lädt
    `0x876D90` (`Shaders\Effects\%s`). **Gebäude (WMO) laufen
    vermutlich über `MapObj*.wfx`, nicht über `.bls` – klären.**
- **VS-Index** (`0x873160`; vorberechnet in `0x81F1D0`, Element +0x34 VS /
  +0x38 PS): `lit + 2*(L + 5*(a + 3*b))`, L = Lichtanzahl 0..4.
  - 4-Lichter-Varianten: Index 9, 19, …, 89 (lit = 1, L = 4).
- **Rechnung im Original:** Die M2-Beleuchtung läuft nur im Vertex-Shader, die
  Pixel-Shader rechnen kein Licht. Der Original-Shader rechnet die 4 Lichter
  parallel (Abschwächung 4-breit in c25–c27).
  - Gx setzt nie int/bool-Konstanten, Schleifen brauchen also `defi`-Literale.
- **Abschwächung (unbestätigt, Fremdquelle WebWowViewerCpp):**
  `att = 1 - saturate((d - start) / (end - start))`,
  `accum += (att * colour)^2 * diff`. Am Original-Bytecode prüfen.
- **ComputeLocalLights** `0x872900`: Typ ≠ 1 → Farbe 0. Bei freien Plätzen wird
  nur die Farbe genullt.
- **SetLocalLighting** `0x873CA0`: bei Anzahl 0 werden c17–c27 nicht neu
  geladen (alte Werte stehen noch).
- **Register:** Das Spiel schreibt höchstens bis c235 (c224–c235
  Schatten-Matrizen, Bones ab c31 mit 3 Registern je Bone). c236–c255 waren frei,
  c236–c246 nutzt jetzt Nr. 66.
  - Bone-Budget `0x83CC80`: bei 256 Konstanten (C − 64) / 3 Bones.
- **Original-Bytecode auf der Tester-Maschine abgreifen**, falls die Dateien
  schwer zu bekommen sind: Haken-Stelle `0x6AA0E7` (VS) / `0x6AA087` (PS), 13 Byte
  `83 7E 4C 00 C7 46 30 01 00 00 00 74 2C`. Name bei `[esi+0x18]`, Bytecode
  `[esi+0x50]`, Länge `[esi+0x4C]`.

## 5. Was gebraucht wird (Eingaben vom User)

- Die Original-Shader-Dateien aus den MPQs des Users:
  - mindestens `Shaders\Vertex\vs_2_0\` und `Shaders\Vertex\vs_3_0\`;
  - besser auch `Shaders\Pixel\` und die übrigen Profile (zum Vergleich).
- Herausholen z. B. mit Ladik's MPQ Editor. Es gilt die Datei im **höchsten**
  Patch-MPQ, das überschreibt ältere.
- Die Gebäude-Shader (WMO, Upload bei `0x7A91A9`) haben eigene `.bls`-Namen.
  Welche das sind, am Ladecode bzw. an den Dateien klären.

## 6. Vorgehen (Vorschlag)

1. **BLS-Format:** Leser und Schreiber bauen. Rundlauf über alle Dateien muss
   bitgleich sein.
2. **Analyse:** Die 4-Lichter-Varianten (9, 19, …, 89) disassemblieren. Den
   Rechenblock für Licht 1–4 (c17–c27) finden und die Abschwächungsformel
   verstehen.
3. **Ändern:** Denselben Block für Licht 5–8 mit c236–c246 anhängen.
   - Grenzen beachten: vs_2_0 erlaubt 256 Befehle, vs_3_0 mindestens 512.
   - Temp-Register beachten.
   - Licht 1–4 müssen exakt gleich bleiben.
4. **Übersetzen:** Neu assemblieren und gegen die Original-Tokens prüfen
   (Disassembler).
5. **Test unter Wine D3D9:** Testprogramm mit Testlichtern rendern (mingw-Build).
   - Original und neuer Shader mit Licht 5–8 = 0 müssen pixelgleich sein.
   - Mit Licht 5–8 muss das Ergebnis zu einer CPU-Referenz passen.
6. **Ausliefern:** Als Werkzeug (Skript), das beim User aus seinen Dateien das
   Patch-MPQ bzw. die losen Dateien erzeugt. Keine Blizzard-Daten ins Repo.
7. **Doku:** `docs/PATCHES.de.md` / `.en.md` bei Nr. 66 ergänzen, wie man die
   Shader erzeugt und einspielt. DE und EN gleich halten.
8. **Spieltest durch den User:**
   - `fixedFunction 0`, Patches 66 + 67 aktiv.
   - Ort mit vielen Lichtern, z. B. Fackeln in Sturmwind oder Dalaran.

## 7. Werkzeuge, die sich bewährt haben

- **Wine:** Die eingebaute `d3dx9` liefert `D3DXAssembleShader` und
  `D3DXDisassembleShader`, dazu kommen ein D3D9-Testprogramm unter Xvfb und ein
  Cross-Compiler `x86_64-w64-mingw32-gcc`.
- **vkd3d:** `vkd3d-compiler` zum Gegenprüfen beim Disassemblieren.
- **Python:** `capstone` zum Lesen der Exe-Stellen.
- **MPQ unter Linux:** StormLib bauen. Oder der User packt unter Windows mit
  Ladik's MPQ Editor.
- Die Original-Exe hat der User. Zum Nachsehen von Adressen reicht eine
  unveränderte `Wow.exe` 3.3.5a (12340).
  - VA → Dateioffset für `.text`: VA − 0x400C00.

## 8. Offene Fragen an den User vor Beginn

- Welche Shader-Familien zuerst? Vorschlag: nur Modelle (`Diffuse_*`), dann
  Gebäude.
- Lieferung: als Patch-MPQ oder als lose Dateien (Nr. 22)?
- Auf welchem Zweig soll das Werkzeug landen (`st0ny-dev-lights`)?

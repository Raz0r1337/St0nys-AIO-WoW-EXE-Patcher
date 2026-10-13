<a id="patch-lights"></a>
**Mehr Lichter: 8 statt 4 Punktlichter (Grundlage für neue Shader)** *(Nr. 65, Autor: St0ny)* 🟠 **[ungetestet]** 🟡 **[Exe wird größer]**

> [!WARNING]
> **Online ungetestet** – nicht auf öffentlichen Servern getestet, mögliche Bann-Gefahr. Vorsicht, kann zu Kick/Bann führen.
>
> **Ingame ungetestet** – die Funktion ist im Spiel noch nicht geprüft, möglicherweise verbuggt.

Im Original bekommt jedes Modell und jedes Gebäude neben der Sonne höchstens
die 4 nächsten Punktlichter ab (Fackeln, Zauber, Lichter an Modellen). Der
Patch lässt das Spiel die 8 nächsten sammeln und an die Grafik weitergeben.
Er ist die Exe-Grundlage für neue Shader, die mehr Lichter darstellen.

So funktioniert es:
- Die 4 nächsten Lichter bleiben wie bisher an ihrem Platz, Spiel und
  Original-Shader arbeiten unverändert damit. Licht 5–8 kommt in eine
  Zusatzliste (320 KB Speicher, einmalig beim ersten Bedarf angelegt).
- **Shader-Weg (Standard):** Für Modelle und Gebäude schickt die Exe Licht 5–8
  zusätzlich an die Vertex-Shader-Register c236–c246, im selben Format, in dem
  das Original Licht 1–4 in c17–c27 schickt. Die Original-Shader lesen diese
  Register nicht – zu sehen ist das erst mit neuen Shadern.
- **Weg ohne Shader** (`/console fixedFunction 1`, danach Neustart): Das
  Grafikgerät bekommt 8 statt 4 Lichtplätze. Modelle, Gebäude, Boden und
  Wasser werden von der Sonne und bis zu 7 Punktlichtern beleuchtet. So lässt
  sich der Patch ohne neue Shader ausprobieren; das Spiel sieht in diesem
  Modus insgesamt schlichter aus (keine Pixel-Shader).
- Behebt dabei einen Fehler des Originals im Weg ohne Shader: Bei 4 Lichtern
  fiel ausgerechnet das nächste weg.
- Code und Daten liegen in einer eigenen Sektion (`.lght`, 0x590 Byte).

Registerbelegung für Shader-Autoren (Vertex-Shader, Modelle und Gebäude):

| Register | Inhalt |
|---|---|
| c17–c20 / c236–c239 | Farbe von Licht 1–4 / 5–8 (rgb, w = 1; freier Platz = 0) |
| c21–c24 / c240–c243 | Position von Licht 1–4 / 5–8 in Kamerasicht (xyz, w = 1) |
| c25 / c244 | Abschwächung 0 von Licht 1–4 / 5–8 (x = erstes … w = viertes Licht) |
| c26 / c245 | Abschwächung 1, Aufteilung wie oben |
| c27 / c246 | Abschwächung 2, Aufteilung wie oben |

> [!NOTE]
> Die Shader-Auswahl bleibt unverändert: Ab 4 Lichtern nimmt das Spiel die
> Varianten für „4 Lichter“ (in jeder `Diffuse_*.bls` die Varianten 9, 19, …,
> 89). Nur diese brauchen den Zusatzcode für c236–c246; Anzahl und
> Reihenfolge der Varianten bleiben gleich. Die Zusatzlichter werden nur
> geschickt, wenn die Grafikkarte mindestens 247 Vertex-Shader-Register hat
> (jede Karte mit Shader-Modell 2 oder 3 hat 256).

> [!NOTE]
> Im Shader-Weg bleiben Boden und Wasser bei 3 Lichtern. Sie haben eigene
> Shader und einen eigenen Datenweg; der folgt in einer späteren Stufe.

> [!NOTE]
> Sind alle Patches mit eigener Sektion gleichzeitig aktiv, ist im PE-Header
> kein Platz mehr für einen weiteren Sektionseintrag. Dann verlängert der
> Patcher die zuletzt angehängte Sektion, statt eine neue anzulegen.


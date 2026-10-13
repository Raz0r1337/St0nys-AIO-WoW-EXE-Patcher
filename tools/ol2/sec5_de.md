<a id="patch-outline"></a>
**Umrandung für Ziel und Mouseover [BETA]** *(Nr. 68, Autor: St0ny)* 🟠 **[ungetestet - Exe wird größer]**

Wie in Retail bekommt die 3D-Figur des markierten Ziels und die Figur unter
dem Mauszeiger eine dünne Umrandung (etwa 2 Pixel). Spieler bekommen ihre
Klassenfarbe wie in den Raid-Frames, alle anderen die Farbe des Auswahlkreises:
rot feindlich, gelb neutral, grün freundlich. Feindliche Spieler pulsieren
sanft zwischen ihrer Klassenfarbe und Rot, damit man sie trotz Klassenfarbe als
Feind erkennt. Der Rand erscheint nur dort, wo die Figur sichtbar ist; steht
eine Wand davor, bekommt sie dort keinen Rand. Waffen, Helm und Reittier
gehören mit zur Figur.

> [!WARNING]
> **BETA** – noch ungetestet, online wie im Spiel. Deshalb ist der Patch
> standardmäßig abgewählt und vorerst nur in den dev-Zweigen, nicht in
> `st0ny-main`.

> [!WARNING]
> **Auf öffentlichen Servern bitte die Standard-Einstellung lassen:** alle
> Fragen vor dem Patchen mit N beantworten. Wird der Patch auf einem Server
> gebannt, hast du Pech gehabt – daran kann ich nichts ändern. Ab dann ist er
> nur noch auf eigenen privaten Servern nutzbar. Also pass bitte auf.

**Einstellungen:** Nach der Patch-Auswahl fragt der Patcher sechs Punkte mit
J/N ab. ENTER übernimmt den Vorschlag in Klammern – beim ersten Mal N, bei
einer gepatchten `Wow.exe` den aktuellen Stand. Standard ist überall N: nur
Ziel und Mouseover, nicht durch Wände.

| Frage | Wirkung bei J |
|-------|---------------|
| Durch Wände sichtbar? | Der Rand erscheint auch dort, wo die Figur verdeckt ist, bei allen Rändern. **Unsicher** – kann als Cheat gewertet werden, der Patcher warnt dann rot. |
| Eigener Charakter immer umrandet? | Deine Figur hat immer einen Rand. |
| Eigene 5er-Gruppe immer umrandet? | Die bis zu 4 Mitspieler deiner Gruppe (`party1` bis `party4`) haben immer einen Rand. |
| Ganzer Schlachtzug immer umrandet? | Alle Mitspieler im Schlachtzug (bis zu 39) haben immer einen Rand, deine Gruppe auch außerhalb eines Schlachtzugs – **kostet viele FPS**. |
| Eigener Charakter nur dort umrandet, wo er verdeckt ist? | Deine Figur bekommt nur dort einen Rand, wo sie verdeckt ist, etwa hinter einer Hauswand oder einem Hügel. Gilt für dich vor „immer umrandet“ und „durch Wände“. |
| Gesinnungsfarbe statt Klassenfarbe? | Alle Ränder in der Farbe des Auswahlkreises (bei Spielern meist blau), auch Ziel und Mouseover. Feindliche Spieler sind dann einfach rot und pulsieren nicht. |

Ist eine Figur gerade Ziel oder unter dem Mauszeiger, gilt dieser Rand.
Mitspieler außer Sichtweite haben keinen. Die Antworten merkt sich der Patcher
wie andere Werte in `patcher_selection.ini`, z. B. `value.outline=self,party`
(`none` = Standard; die Punkte heißen der Reihe nach `walls`, `self`, `party`,
`raid`, `hidden` und `react`).

> [!WARNING]
> **Ganzer Schlachtzug kostet viele FPS:** Jede umrandete Figur wird zehnmal
> gezeichnet. Bei 25 oder 40 Spielern sind das sehr viele zusätzliche
> Zeichenaufrufe pro Bild. Auf schwächeren Rechnern lieber nur die 5er-Gruppe
> nehmen.

> [!NOTE]
> **Nur dort, wo verdeckt:** Erkannt wird nur, was vor deiner Figur gezeichnet
> wird. Gelände und Gebäude zeichnet das Spiel normalerweise vor den Figuren;
> ob auch Bäume oder andere Figuren davor erkannt werden, hängt von der
> Reihenfolge ab, in der das Spiel zeichnet – das muss der Test im Spiel
> zeigen.

So funktioniert es:
- Der Tiefenpuffer bekommt einen Stencil-Anteil (D24S8 statt D24X8). Das Spiel
  selbst nutzt Stencil nirgends.
- Beim Zeichnen der Figur werden ihre sichtbaren Pixel im Stencil markiert.
  Danach wird sie noch achtmal unsichtbar gezeichnet, je um 2 Pixel in alle
  Richtungen verschoben (über die Projektionsmatrix des Shaders), mit
  Tiefentest – diese Kopien markieren den Rand und tragen dort die Tiefe der
  Figur ein. Jede umrandete Figur (Ziel, Mouseover, du, jedes Gruppen- und
  Schlachtzug-Mitglied, bis zu 48) bekommt dabei ihren eigenen Wert und so
  ihre eigene Farbe.
- Was danach gezeichnet wird und vor der Figur liegt (z. B. Büsche, Pilze,
  Gras), löscht die Markierung an seinen Pixeln und verdeckt so auch den Rand.
  Dinge dahinter bleiben dank der eingetragenen Tiefe hinter dem Rand.
  Durchsichtiges wie Wasser oder Zaubereffekte lässt den Rand stehen.
- Weitere Teile derselben Figur (Umhang, Waffe, Reittier) werden auf ihrem
  eigenen Rand noch einmal ohne Tiefentest gezeichnet, damit kein Rand
  zwischen den Teilen hängen bleibt.
- Mit „durch Wände“ wird die Figur auch dort markiert, wo sie verdeckt ist,
  und die Kopien laufen ohne Tiefentest. Später Gezeichnetes löscht den Rand
  dann nicht mehr.
- Mit „nur dort, wo verdeckt“ wird deine Figur ebenfalls auch dort markiert,
  wo sie verdeckt ist; ihre Kopien markieren den Rand aber nur dort, wo
  bereits Gezeichnetes vor ihnen liegt.
- Nach den Modellen und vor dem Interface färbt je umrandeter Figur eine
  bildschirmfüllende Fläche nur ihre Rand-Pixel ein; danach wird der Stencil
  geleert und das Spiel setzt alle Grafik-Einstellungen neu.
- Feindlich heißt: Der Auswahlkreis des Spielers wäre rot. Dann mischt die
  Fläche seine Klassenfarbe mit Rot; der Rot-Anteil steigt und fällt sanft
  (Kosinus), ein Puls dauert 1,5 Sekunden.
- Code und Daten liegen in einer eigenen Sektion (`.outl`, 0x118E Byte). Jede
  Einstellung ist ein einzelnes Füllbyte zwischen zwei Funktionen in `.text`,
  das bei J auf 1 gesetzt wird; der Code liest diese Schalter beim Zeichnen.
  Daran erkennt der Patcher die Einstellungen auch in einer gepatchten
  `Wow.exe`.

> [!NOTE]
> Nur mit `gxApi d3d9` (Standard) und 24-Bit-Tiefenpuffer (Standard). Mit
> D3D9Ex, OpenGL oder `gxDepthBits` 16/32 schaltet sich der Patch ab. Mit
> DXVK lief die erste Fassung im Spiel ebenfalls, weil WoW auch dort
> Direct3D 9 nutzt.

> [!NOTE]
> Sind alle Patches mit eigener Sektion gleichzeitig aktiv, ist im PE-Header
> kein Platz mehr für einen weiteren Sektionseintrag. Dann verlängert der
> Patcher die zuletzt angehängte Sektion, statt eine neue anzulegen.


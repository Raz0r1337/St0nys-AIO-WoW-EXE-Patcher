# Doku Nr. 68: Leuchtrand in 3 Stufen, duenne Linie fuer Schlachtzug (outline9). Aufruf: docs_ol9.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

edit('docs/PATCHES.de.md', [
("""Wie in Retail bekommt die 3D-Figur des markierten Ziels und die Figur unter
dem Mauszeiger eine dünne Umrandung (etwa 2 Pixel). Spieler bekommen ihre""",
"""Wie in Retail bekommt die 3D-Figur des markierten Ziels und die Figur unter
dem Mauszeiger einen leuchtenden Rand: direkt an der Figur hell, nach außen
auf etwa 6 Pixeln auslaufend. Schlachtzug-Mitglieder außerhalb deiner
5er-Gruppe bekommen nur eine dünne Linie (etwa 2 Pixel), das spart Leistung.
Spieler bekommen ihre"""),
("""> **Ganzer Schlachtzug kostet viele FPS:** Jede umrandete Figur wird zehnmal
> gezeichnet. Bei 25 oder 40 Spielern sind das sehr viele zusätzliche
> Zeichenaufrufe pro Bild.""",
"""> **Ganzer Schlachtzug kostet viele FPS:** Jede Figur mit Leuchtrand wird
> 26-mal gezeichnet, Schlachtzug-Mitglieder außerhalb deiner 5er-Gruppe mit
> der dünnen Linie immer noch zehnmal. Bei 25 oder 40 Spielern sind das sehr
> viele zusätzliche Zeichenaufrufe pro Bild."""),
("""- Beim Zeichnen der Figur werden ihre sichtbaren Pixel im Stencil markiert.
  Danach wird sie noch achtmal unsichtbar gezeichnet, je um 2 Pixel in alle
  Richtungen verschoben (über die Projektionsmatrix des Shaders), mit
  Tiefentest – diese Kopien markieren den Rand und tragen dort die Tiefe der
  Figur ein. Jede umrandete Figur (Ziel, Mouseover, du, jedes Gruppen- und
  Schlachtzug-Mitglied, bis zu 48) bekommt dabei ihren eigenen Wert und so
  ihre eigene Farbe.""",
"""- Beim Zeichnen der Figur werden ihre sichtbaren Pixel im Stencil markiert.
  Danach wird sie noch 24-mal unsichtbar gezeichnet, je achtmal um 2, 4 und
  6 Pixel in alle Richtungen verschoben (über die Projektionsmatrix des
  Shaders), mit Tiefentest – diese Kopien markieren die drei Stufen des
  Rands; die innere trägt dort auch die Tiefe der Figur ein. Für die dünne
  Linie gibt es nur die acht Kopien der inneren Stufe. Jede umrandete Figur
  (Ziel, Mouseover, du, jedes Gruppen- und Schlachtzug-Mitglied, bis zu 48)
  bekommt dabei ihren eigenen Wert und so ihre eigene Farbe."""),
("""- Nach den Modellen und vor dem Interface färbt je umrandeter Figur eine
  bildschirmfüllende Fläche nur ihre Rand-Pixel ein; danach wird der Stencil
  geleert und das Spiel setzt alle Grafik-Einstellungen neu.""",
"""- Nach den Modellen und vor dem Interface färbt je umrandeter Figur und Stufe
  eine bildschirmfüllende Fläche nur ihre Rand-Pixel ein: innen ihre Farbe zur
  Hälfte Richtung Weiß, in der Mitte zu etwa 60 %, außen zu etwa 25 % deckend
  – so wird der Rand nach außen dunkler. Die dünne Linie bekommt die volle
  Farbe. Danach wird der Stencil geleert und das Spiel setzt alle
  Grafik-Einstellungen neu."""),
("""- Code und Daten liegen in einer eigenen Sektion (`.outl`, 0x14F0 Byte). Jeder""",
 """- Code und Daten liegen in einer eigenen Sektion (`.outl`, 0x16AC Byte). Jeder"""),
])

edit('docs/PATCHES.en.md', [
("""Like in retail, the 3D figure of your target and the figure under the mouse
cursor get a thin outline (about 2 pixels). Players get their class color like""",
"""Like in retail, the 3D figure of your target and the figure under the mouse
cursor get a glowing outline: bright right at the figure, fading out over
about 6 pixels. Raid members outside your party of 5 only get a thin line
(about 2 pixels), which saves performance. Players get their class color like"""),
("""> **Whole raid costs a lot of FPS:** every outlined figure is drawn ten times.
> With 25 or 40 players that is a lot of extra draw calls per frame.""",
"""> **Whole raid costs a lot of FPS:** every figure with a glowing outline is
> drawn 26 times, raid members outside your party of 5 with the thin line
> still ten times. With 25 or 40 players that is a lot of extra draw calls per
> frame."""),
("""- While the figure is drawn, its visible pixels are marked in the stencil.
  Then it is drawn eight more times invisibly, each shifted by 2 pixels in
  every direction (via the shader's projection matrix), with depth test –
  these copies mark the outline and store the figure's depth there. Every
  outlined figure (target, mouseover, you, every party and raid member, up to
  48) gets a value of its own and so a color of its own.""",
"""- While the figure is drawn, its visible pixels are marked in the stencil.
  Then it is drawn 24 more times invisibly, eight times each shifted by 2, 4
  and 6 pixels in every direction (via the shader's projection matrix), with
  depth test – these copies mark the three steps of the outline; the inner
  one also stores the figure's depth there. The thin line only gets the eight
  copies of the inner step. Every outlined figure (target, mouseover, you,
  every party and raid member, up to 48) gets a value of its own and so a
  color of its own."""),
("""- After the models and before the interface, a full-screen quad per outlined
  figure colors only its outline pixels; then the stencil is cleared and the
  game sends all its graphics states again.""",
"""- After the models and before the interface, a full-screen quad per outlined
  figure and step colors only its outline pixels: inside its color halfway
  towards white, in the middle about 60 %, outside about 25 % opaque – so the
  outline gets darker towards the outside. The thin line gets the full color.
  Then the stencil is cleared and the game sends all its graphics states
  again."""),
("""- Code and data live in a section of their own (`.outl`, 0x14F0 bytes). Each""",
 """- Code and data live in a section of their own (`.outl`, 0x16AC bytes). Each"""),
])
print('ok')

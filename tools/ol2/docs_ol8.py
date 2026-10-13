# Doku Nr. 68: umrandete Figuren zuletzt zeichnen (outline8). Aufruf: docs_ol8.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

edit('docs/PATCHES.de.md', [
("""> **Nur dort, wo verdeckt** (auch für Gruppe/Schlachtzug): Erkannt wird nur,
> was vor deiner Figur gezeichnet wird. Gelände und Gebäude zeichnet das Spiel
> normalerweise vor den Figuren. Was erst danach kommt – etwa ein Teller auf
> dem Tisch vor dir –, verdeckt deine Figur, ohne dass dort ein Rand erscheint.
> Außerdem muss das Verdeckende ein Stück vor der Figur liegen, sonst gäbe es
> direkt unter den Füßen eine Linie am Boden: rund 0,1 Yards bei 10 Yards
> Kameraabstand, 0,2 Yards bei 15 und knapp 1 Yard bei 30.""",
"""> **Nur dort, wo verdeckt** (auch für Gruppe/Schlachtzug): Erkannt wird, was
> vor deiner Figur gezeichnet wird. Gelände und Gebäude zeichnet das Spiel
> normalerweise zuerst; alle anderen Figuren und Objekte – etwa eine Laterne,
> ein Briefkasten oder ein Teller auf dem Tisch vor dir – zeichnet der Patch
> ebenfalls vor den umrandeten Figuren. Durchsichtiges wie Wasser oder
> Zaubereffekte verdeckt nicht. Außerdem muss das Verdeckende ein Stück vor der
> Figur liegen, sonst gäbe es direkt unter den Füßen eine Linie am Boden: rund
> 0,1 Yards bei 10 Yards Kameraabstand, 0,2 Yards bei 15 und knapp 1 Yard bei
> 30."""),
("""  Schlachtzug-Mitglied, bis zu 48) bekommt dabei ihren eigenen Wert und so
  ihre eigene Farbe.
- Was danach gezeichnet wird und vor der Figur liegt (z. B. Büsche, Pilze,
  Gras), löscht die Markierung an seinen Pixeln und verdeckt so auch den Rand.""",
"""  Schlachtzug-Mitglied, bis zu 48) bekommt dabei ihren eigenen Wert und so
  ihre eigene Farbe.
- Undurchsichtige Modelle sortiert das Spiel nach Modell und Textur, nicht nach
  Entfernung, und zeichnet gebündelte Deko-Objekte (`M2BatchDoodads`) erst
  danach. Der Patch stellt die Teile umrandeter Figuren ans Ende dieser
  Reihenfolge, untereinander bleibt sie, wie sie war. So liegt alles andere
  schon im Tiefenpuffer, wenn die umrandeten Figuren gezeichnet werden.
- Was danach noch gezeichnet wird und vor der Figur liegt, löscht die
  Markierung an seinen Pixeln und verdeckt so auch den Rand."""),
("""- Code und Daten liegen in einer eigenen Sektion (`.outl`, 0x1310 Byte). Jeder""",
 """- Code und Daten liegen in einer eigenen Sektion (`.outl`, 0x14F0 Byte). Jeder"""),
])

edit('docs/PATCHES.en.md', [
("""> **Only where hidden** (also for party/raid): only what is drawn before your
> figure is detected. The game normally draws terrain and buildings before the
> figures. Whatever comes afterwards – a plate on the table in front of you,
> say – hides your figure without an outline appearing there. Also, whatever
> hides it has to lie a bit in front of the figure, otherwise there would be a
> line on the ground right under the feet: about 0.1 yards at 10 yards camera
> distance, 0.2 yards at 15 and almost 1 yard at 30.""",
"""> **Only where hidden** (also for party/raid): what is drawn before your
> figure is detected. The game normally draws terrain and buildings first; all
> other figures and objects – a lantern, a mailbox or a plate on the table in
> front of you, say – are drawn before the outlined figures by the patch as
> well. Transparent things like water or spell effects do not hide anything.
> Also, whatever hides it has to lie a bit in front of the figure, otherwise
> there would be a line on the ground right under the feet: about 0.1 yards at
> 10 yards camera distance, 0.2 yards at 15 and almost 1 yard at 30."""),
("""  48) gets a value of its own and so a color of its own.
- Whatever is drawn afterwards in front of the figure (e.g. bushes,
  mushrooms, grass) clears the mark at its pixels and so hides the outline as
  well.""",
"""  48) gets a value of its own and so a color of its own.
- The game sorts opaque models by model and texture, not by distance, and
  draws batched doodads (`M2BatchDoodads`) after them. The patch moves the
  parts of outlined figures to the end of this order; among themselves it
  stays as it was. So everything else is already in the depth buffer when the
  outlined figures are drawn.
- Whatever is still drawn afterwards in front of the figure clears the mark at
  its pixels and so hides the outline as well."""),
("""- Code and data live in a section of their own (`.outl`, 0x1310 bytes). Each""",
 """- Code and data live in a section of their own (`.outl`, 0x14F0 bytes). Each"""),
])
print('ok')

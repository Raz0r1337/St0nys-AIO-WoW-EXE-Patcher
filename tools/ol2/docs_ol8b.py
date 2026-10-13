# Ergaenzung zu docs_ol8.py: Absaetze neu umbrechen. Aufruf: docs_ol8b.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)
edit('docs/PATCHES.de.md', [
("""> Zaubereffekte verdeckt nicht. Außerdem muss das Verdeckende ein Stück vor der
> Figur liegen, sonst gäbe es direkt unter den Füßen eine Linie am Boden: rund
> 0,1 Yards bei 10 Yards Kameraabstand, 0,2 Yards bei 15 und knapp 1 Yard bei
> 30.""",
"""> Zaubereffekte verdeckt nicht. Außerdem muss das Verdeckende ein Stück vor
> der Figur liegen, sonst gäbe es direkt unter den Füßen eine Linie am Boden:
> rund 0,1 Yards bei 10 Yards Kameraabstand, 0,2 Yards bei 15 und knapp
> 1 Yard bei 30."""),
("""- Was danach noch gezeichnet wird und vor der Figur liegt, löscht die
  Markierung an seinen Pixeln und verdeckt so auch den Rand.
  Dinge dahinter bleiben dank der eingetragenen Tiefe hinter dem Rand.
  Durchsichtiges wie Wasser oder Zaubereffekte lässt den Rand stehen.""",
"""- Was danach noch gezeichnet wird und vor der Figur liegt, löscht die
  Markierung an seinen Pixeln und verdeckt so auch den Rand. Dinge dahinter
  bleiben dank der eingetragenen Tiefe hinter dem Rand. Durchsichtiges wie
  Wasser oder Zaubereffekte lässt den Rand stehen."""),
])
edit('docs/PATCHES.en.md', [
("""- Whatever is still drawn afterwards in front of the figure clears the mark at
  its pixels and so hides the outline as well. Things behind stay behind the outline thanks to the stored depth.
  Transparent things like water or spell effects leave the outline in place.""",
"""- Whatever is still drawn afterwards in front of the figure clears the mark at
  its pixels and so hides the outline as well. Things behind stay behind the
  outline thanks to the stored depth. Transparent things like water or spell
  effects leave the outline in place."""),
])
print('ok')

# Doku Umrandung Nr. 68: Standard jetzt "nur wo verdeckt" = J; Erklaerung zu verdeckt (Abstand, spaeter Gezeichnetes).
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)
edit('docs/README.de.md', [
("""> verwendest, lass bitte die Standard-Einstellung – alle Fragen vor dem
> Patchen mit N beantworten. Wird der Patch auf einem Server gebannt, hast du
""", """> verwendest, lass bitte die Standard-Einstellung – vor dem Patchen nur
> „Eigener Charakter nur dort umrandet, wo er verdeckt ist?“ mit J
> beantworten, alle anderen Fragen mit N. Wird der Patch auf einem Server gebannt, hast du
"""),
])
edit('docs/README.md', [
("""> keep the default setting – answer all questions before patching with N. If
> the patch gets banned on a server, that is bad luck; there is nothing I can
""", """> keep the default setting – before patching, answer only "Own character
> outlined only where it is hidden?" with Y and all other questions with N. If
> the patch gets banned on a server, that is bad luck; there is nothing I can
"""),
])
edit('docs/PATCHES.de.md', [
("""> **Auf öffentlichen Servern bitte die Standard-Einstellung lassen:** alle
> Fragen vor dem Patchen mit N beantworten. Wird der Patch auf einem Server
""", """> **Auf öffentlichen Servern bitte die Standard-Einstellung lassen:** vor dem
> Patchen nur „Eigener Charakter nur dort umrandet, wo er verdeckt ist?“ mit J
> beantworten, alle anderen Fragen mit N. Wird der Patch auf einem Server
"""),
("""J/N ab. ENTER übernimmt den Vorschlag in Klammern – beim ersten Mal N, bei
einer gepatchten `Wow.exe` den aktuellen Stand. Standard ist überall N: nur
Ziel und Mouseover, nicht durch Wände.
""", """J/N ab. ENTER übernimmt den Vorschlag in Klammern – beim ersten Mal den
Standard, bei einer gepatchten `Wow.exe` den aktuellen Stand. Standard ist nur
„Eigener Charakter nur dort umrandet, wo er verdeckt ist“ mit J, alles andere
N: Ziel und Mouseover umrandet, nicht durch Wände, und deine Figur nur dort, wo
sie verdeckt ist.
"""),
("""etwa hinter einer Hauswand oder einem Hügel. Gilt für dich vor „immer umrandet“ und „durch Wände“. |""",
 """etwa hinter einer Hauswand oder einem Hügel; sichtbare Teile bleiben ohne Rand. Gilt für dich vor „immer umrandet“ und „durch Wände“. **Standard: J** |"""),
("""(`none` = Standard; die Punkte heißen der Reihe nach `walls`, `self`, `party`,
`raid`, `hidden` und `react`).""", """(Standard ist `hidden`, `none` heißt alles N; die Punkte heißen der Reihe nach
`walls`, `self`, `party`, `raid`, `hidden` und `react`)."""),
("""> **Nur dort, wo verdeckt:** Erkannt wird nur, was vor deiner Figur gezeichnet
> wird. Gelände und Gebäude zeichnet das Spiel normalerweise vor den Figuren;
> ob auch Bäume oder andere Figuren davor erkannt werden, hängt von der
> Reihenfolge ab, in der das Spiel zeichnet – das muss der Test im Spiel
> zeigen.""", """> **Nur dort, wo verdeckt:** Erkannt wird nur, was vor deiner Figur gezeichnet
> wird. Gelände und Gebäude zeichnet das Spiel normalerweise vor den Figuren.
> Was erst danach kommt – etwa ein Teller auf dem Tisch vor dir –, verdeckt
> deine Figur, ohne dass dort ein Rand erscheint. Außerdem muss das
> Verdeckende ein Stück vor der Figur liegen, sonst gäbe es direkt unter den
> Füßen eine Linie am Boden: rund 0,1 Yards bei 10 Yards Kameraabstand,
> 0,2 Yards bei 15 und knapp 1 Yard bei 30."""),
("""- Mit „nur dort, wo verdeckt“ wird deine Figur ebenfalls auch dort markiert,
  wo sie verdeckt ist; ihre Kopien markieren den Rand aber nur dort, wo
  bereits Gezeichnetes vor ihnen liegt.""", """- Mit „nur dort, wo verdeckt“ wird deine Figur ebenfalls auch dort markiert,
  wo sie verdeckt ist; ihre Kopien markieren den Rand aber nur dort, wo
  bereits Gezeichnetes deutlich vor ihnen liegt. Dafür zieht die
  Projektionsmatrix ihre Tiefe ein Stück nach vorn (siehe oben)."""),
])
edit('docs/PATCHES.en.md', [
("""> **On public servers please keep the default setting:** answer all questions
> before patching with N. If the patch gets banned on a server, that is bad
""", """> **On public servers please keep the default setting:** before patching,
> answer only "Own character outlined only where it is hidden?" with Y and all
> other questions with N. If the patch gets banned on a server, that is bad
"""),
("""Y/N. ENTER takes the suggestion in brackets – N the first time, the current
state for a patched `Wow.exe`. The default is N everywhere: only target and
mouseover, not through walls.
""", """Y/N. ENTER takes the suggestion in brackets – the default the first time, the
current state for a patched `Wow.exe`. By default only "Own character outlined
only where it is hidden" is Y, everything else N: target and mouseover
outlined, not through walls, and your figure only where it is hidden.
"""),
("""for example behind a house wall or a hill. For you it takes precedence over "always outlined" and "through walls". |""",
 """for example behind a house wall or a hill; visible parts get no outline. For you it takes precedence over "always outlined" and "through walls". **Default: Y** |"""),
("""values in `patcher_selection.ini`, e.g. `value.outline=self,party` (`none` =
default; in order, the settings are called `walls`, `self`, `party`, `raid`,
`hidden` and `react`).""", """values in `patcher_selection.ini`, e.g. `value.outline=self,party` (the
default is `hidden`, `none` means all N; in order, the settings are called
`walls`, `self`, `party`, `raid`, `hidden` and `react`)."""),
("""> **Only where hidden:** only what is drawn before your figure is detected.
> The game normally draws terrain and buildings before the figures; whether
> trees or other figures in front are detected as well depends on the order in
> which the game draws – the test in game has to show that.""", """> **Only where hidden:** only what is drawn before your figure is detected.
> The game normally draws terrain and buildings before the figures. Whatever
> comes afterwards – a plate on the table in front of you, say – hides your
> figure without an outline appearing there. Also, whatever hides it has to
> lie a bit in front of the figure, otherwise there would be a line on the
> ground right under the feet: about 0.1 yards at 10 yards camera distance,
> 0.2 yards at 15 and almost 1 yard at 30."""),
("""- With "only where hidden" your figure is also marked where it is hidden as
  well; its copies, however, only mark the outline where something already
  drawn lies in front of them.""", """- With "only where hidden" your figure is also marked where it is hidden as
  well; its copies, however, only mark the outline where something already
  drawn lies clearly in front of them. For that, the projection matrix pulls
  their depth forward a bit (see above)."""),
])
print('ok')

# Doku fuer die Outline-Optionen (st0ny-dev): Zeilen 69-74, Nummern ab 69 (+6), Listen, Warnung,
# neuer Outline-Abschnitt und sechs Options-Abschnitte. Aufruf: docs_ol.py <worktree> <altes Skript>
import re, sys
wt = sys.argv[1]; d = wt + '/docs/'
old_src = open(sys.argv[2], encoding='ascii').read().replace('\r\n', '\n')
new_src = open(wt + '/apply_patches.ps1', encoding='ascii').read().replace('\r\n', '\n')
oh = re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$", old_src); nh = re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$", new_src)
NID = [i for i, _ in nh]; C = NID.index('outlinewalls') + 1
assert C == 69 and NID[67] == 'outline' and NID[74] == 'tracker' and [i for i, _ in oh][68] == 'tracker'
FLAGS = ('BanRisk', 'PublicUntested', 'GameUntested', 'GrowsExe', 'DllRisky')
fl = lambda hs: {k: [i + 1 for i, (_, h) in enumerate(hs) if k + ' = $true' in h] for k in FLAGS}
OF, NF = fl(oh), fl(nh)
def rng(L):
    out = []; i = 0
    while i < len(L):
        j = i
        while j + 1 < len(L) and L[j + 1] == L[j] + 1: j += 1
        out += ([str(L[i])] if j == i else ([str(L[i]), str(L[j])] if j == i + 1 else ['%d–%d' % (L[i], L[j])])); i = j + 1
    return out
def txt(L, und):
    r = rng(L); return r[0] if len(r) == 1 else ', '.join(r[:-1]) + ' ' + und + ' ' + r[-1]
def relist(s, old, new):
    pat = re.escape(old).replace('\\ ', r'\s+')
    def f(m):
        span = m.group(0)
        if '\n' not in span: return new
        k = span.index('\n'); before = re.sub(r'\s+', ' ', span[:k]); ind = re.match(r'\n(\s*)', span[k:]).group(1)
        cut = new.rfind(' ', 0, len(before) + 1)
        return new if cut <= 0 else new[:cut] + '\n' + ind + new[cut + 1:]
    return re.subn(pat, f, s)
def sh(n):
    n = int(n); return str(n + 6 if n >= C else n)
def refs(s):
    def f(m):
        out = '%s %s' % (m.group(1), sh(m.group(2)))
        if m.group(3): out += m.group(3) + sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?', f, s)
TXT = {'de': dict(ban='unsicher', both='ungetestet', pub='online ungetestet', game='ingame ungetestet', grow='Exe wird größer', dll='DLL riskant', safe='sicher'),
       'en': dict(ban='unsafe', both='untested', pub='untested online', game='untested ingame', grow='exe grows', dll='DLL risky', safe='safe')}
def badge(pid, lang):
    h = dict(nh)[pid]; t = TXT[lang]; f = lambda k: (k + ' = $true') in h
    tags = []
    if f('BanRisk'): tags.append(t['ban'])
    if f('PublicUntested') and f('GameUntested'): tags.append(t['both'])
    elif f('PublicUntested'): tags.append(t['pub'])
    elif f('GameUntested'): tags.append(t['game'])
    base = bool(tags)
    if f('GrowsExe'): tags.append(t['grow'])
    if f('DllRisky'): tags.append(t['dll'])
    if not base: tags.insert(0, t['safe'])
    dot = '🔴' if f('BanRisk') else '🟠' if (f('PublicUntested') or f('GameUntested')) else '🟡' if (f('GrowsExe') or f('DllRisky')) else '🟢'
    return '%s **[%s]**' % (dot, ' - '.join(tags))
def once(s, a, b):
    n = s.count(a); assert n == 1, (a[:90], n); return s.replace(a, b)

ROWS = {'de': [('outlinewalls', 'Umrandung: auch durch Wände sichtbar [BETA]'),
               ('outlineself', 'Umrandung: eigener Charakter immer umrandet [BETA]'),
               ('outlineparty', 'Umrandung: eigene Gruppe immer umrandet [BETA] *(nur 5er-Gruppe)*'),
               ('outlineraid', 'Umrandung: ganzer Schlachtzug immer umrandet [BETA] *(kostet im Schlachtzug viele FPS)*'),
               ('outlinehidden', 'Umrandung: eigener Charakter nur dort, wo er verdeckt ist [BETA]'),
               ('outlinereact', 'Umrandung: Gesinnungsfarbe statt Klassenfarbe [BETA] *(für alle Ränder von Spielern)*')],
        'en': [('outlinewalls', 'Outline: visible through walls too [BETA]'),
               ('outlineself', 'Outline: own character always outlined [BETA]'),
               ('outlineparty', 'Outline: own party always outlined [BETA] *(party of 5 only)*'),
               ('outlineraid', 'Outline: whole raid always outlined [BETA] *(costs a lot of FPS in raids)*'),
               ('outlinehidden', 'Outline: own character only where it is hidden [BETA]'),
               ('outlinereact', 'Outline: reaction color instead of class color [BETA] *(for all outlines of players)*')]}
WARN = {'de': '''
> [!WARNING]
> **Umrandung (Nr. 68–74) auf öffentlichen Servern:** Wenn du den Patch dort
> verwendest, lass bitte die Standard-Einstellung – nur Nr. 68, ohne die
> Zusatzoptionen Nr. 69–74. Wird der Patch auf einem Server gebannt, hast du
> Pech gehabt; daran kann ich nichts ändern. Ab dann ist er nur noch auf eigenen
> privaten Servern nutzbar. Also pass bitte auf.
''', 'en': '''
> [!WARNING]
> **Outline (No. 68–74) on public servers:** if you use the patch there, please
> keep the default setting – only No. 68, without the extra options No. 69–74.
> If the patch gets banned on a server, that is bad luck; there is nothing I can
> do about it. From then on it can only be used on your own private servers. So
> please be careful.
'''}
SEC = {'de': '''<a id="patch-outline"></a>
**Umrandung für Ziel und Mouseover [BETA]** *(Nr. 68, Autor: St0ny)* {B68}

Wie in Retail bekommt die 3D-Figur des markierten Ziels und die Figur unter
dem Mauszeiger eine dünne Umrandung (etwa 2 Pixel). Spieler bekommen ihre
Klassenfarbe wie in den Raid-Frames, alle anderen die Farbe des Auswahlkreises:
rot feindlich, gelb neutral, grün freundlich. Der Rand erscheint nur dort, wo
die Figur sichtbar ist; steht eine Wand davor, bekommt sie dort keinen Rand.
Waffen, Helm und Reittier gehören mit zur Figur.

> [!WARNING]
> **BETA** – noch ungetestet, online wie im Spiel. Deshalb ist der Patch
> standardmäßig abgewählt und vorerst nur in den dev-Zweigen, nicht in
> `st0ny-main`.

> [!WARNING]
> **Auf öffentlichen Servern bitte die Standard-Einstellung lassen:** nur
> Nr. 68, ohne die Zusatzoptionen Nr. 69–74. Wird der Patch auf einem Server
> gebannt, hast du Pech gehabt – daran kann ich nichts ändern. Ab dann ist er
> nur noch auf eigenen privaten Servern nutzbar. Also pass bitte auf.

**Zusatzoptionen** – eigene Patches im Menü, die Nr. 68 brauchen; alle sind
standardmäßig aus:

| Nr. | Option | Wirkung |
|----:|--------|---------|
| [69](#patch-outlinewalls) | durch Wände sichtbar | Der Rand erscheint auch dort, wo die Figur verdeckt ist. |
| [70](#patch-outlineself) | eigener Charakter | Deine Figur hat immer einen Rand. |
| [71](#patch-outlineparty) | eigene Gruppe | Die bis zu 4 Mitspieler deiner 5er-Gruppe haben immer einen Rand. |
| [72](#patch-outlineraid) | ganzer Schlachtzug | Alle Mitspieler im Schlachtzug haben immer einen Rand – kostet viele FPS. |
| [73](#patch-outlinehidden) | eigener Charakter nur verdeckt | Deine Figur bekommt nur dort einen Rand, wo sie verdeckt ist. |
| [74](#patch-outlinereact) | Gesinnungsfarbe | Alle Ränder in der Farbe des Auswahlkreises, auch bei Spielern. |

Ist eine Figur gerade Ziel oder unter dem Mauszeiger, gilt dieser Rand. Jede
umrandete Figur wird zehnmal gezeichnet (mit Nr. 69 bzw. 73 neunmal) – viele
Ränder kosten Leistung, im Schlachtzug mit Nr. 72 deutlich.

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
- Mit Nr. 69 wird die Figur auch dort markiert, wo sie verdeckt ist, und die
  Kopien laufen ohne Tiefentest. Später Gezeichnetes löscht den Rand dann
  nicht mehr.
- Mit Nr. 73 wird deine Figur ebenfalls auch dort markiert, wo sie verdeckt
  ist; ihre Kopien markieren den Rand aber nur dort, wo bereits Gezeichnetes
  vor ihnen liegt.
- Nach den Modellen und vor dem Interface färbt je umrandeter Figur eine
  bildschirmfüllende Fläche nur ihre Rand-Pixel ein; danach wird der Stencil
  geleert und das Spiel setzt alle Grafik-Einstellungen neu.
- Code und Daten liegen in einer eigenen Sektion (`.outl`, {SIZE} Byte). Die
  Zusatzoptionen setzen je ein einzelnes Füllbyte zwischen zwei Funktionen in
  `.text` auf 1; der Code liest diese Schalter beim Zeichnen.

> [!NOTE]
> Nur mit `gxApi d3d9` (Standard) und 24-Bit-Tiefenpuffer (Standard). Mit
> D3D9Ex, OpenGL oder `gxDepthBits` 16/32 schaltet sich der Patch ab. Mit
> DXVK lief die erste Fassung im Spiel ebenfalls, weil WoW auch dort
> Direct3D 9 nutzt.

> [!NOTE]
> Sind alle Patches mit eigener Sektion gleichzeitig aktiv, ist im PE-Header
> kein Platz mehr für einen weiteren Sektionseintrag. Dann verlängert der
> Patcher die zuletzt angehängte Sektion, statt eine neue anzulegen.

<a id="patch-outlinewalls"></a>
**Umrandung: auch durch Wände sichtbar [BETA]** *(Nr. 69, Autor: St0ny)* {B69}

Zusatzoption zu Nr. 68: Der Rand erscheint auch dort, wo die Figur hinter
einer Wand, einem Baum oder einer anderen Figur steht – man sieht ihre Umrisse
durch alles hindurch. Das gilt für alle Ränder: Ziel, Mouseover und die
dauerhaften aus Nr. 70 bis 72.

> [!WARNING]
> Durch Wände sehen verschafft einen Vorteil und kann als Cheat gewertet
> werden – **nur auf eigenen Servern verwenden.**

<a id="patch-outlineself"></a>
**Umrandung: eigener Charakter immer umrandet [BETA]** *(Nr. 70, Autor: St0ny)* {B70}

Zusatzoption zu Nr. 68: Deine eigene Figur hat immer einen Rand, in deiner
Klassenfarbe (mit Nr. 74 in der Farbe des Auswahlkreises). Bist du selbst das
Ziel oder unter dem Mauszeiger, gilt dieser Rand. Mit Nr. 73 zusammen gilt
Nr. 73: nur die verdeckten Teile.

<a id="patch-outlineparty"></a>
**Umrandung: eigene Gruppe immer umrandet [BETA]** *(Nr. 71, Autor: St0ny)* {B71}

Zusatzoption zu Nr. 68: Die bis zu 4 Mitspieler deiner Gruppe (`party1` bis
`party4`) haben immer einen Rand, jeder in seiner Klassenfarbe (mit Nr. 74 in
der Farbe des Auswahlkreises). Wer gerade Ziel oder unter dem Mauszeiger ist,
bekommt dessen Rand. Mitspieler außer Sichtweite haben keinen.

<a id="patch-outlineraid"></a>
**Umrandung: ganzer Schlachtzug immer umrandet [BETA]** *(Nr. 72, Autor: St0ny)* {B72}

Zusatzoption zu Nr. 68: Alle Mitspieler deines Schlachtzugs (bis zu 39) haben
immer einen Rand, jeder in seiner Klassenfarbe (mit Nr. 74 in der Farbe des
Auswahlkreises). Deine Gruppe ist dabei, auch außerhalb eines Schlachtzugs –
Nr. 71 braucht es dann nicht. Dich selbst umrandet nur Nr. 70 bzw. 73.

> [!WARNING]
> **Kostet viele FPS:** Jede umrandete Figur wird zehnmal gezeichnet. Bei 25
> oder 40 Spielern sind das sehr viele zusätzliche Zeichenaufrufe pro Bild.
> Auf schwächeren Rechnern lieber nur Nr. 71 nehmen.

<a id="patch-outlinehidden"></a>
**Umrandung: eigener Charakter nur dort, wo er verdeckt ist [BETA]** *(Nr. 73, Autor: St0ny)* {B73}

Zusatzoption zu Nr. 68: Deine Figur bekommt nur dort einen Rand, wo sie
verdeckt ist – steht etwa eine Hauswand oder ein Hügel zwischen Kamera und
dir, siehst du deinen Umriss auf der Wand. Sichtbare Teile bekommen keinen
Rand. Hast du auch Nr. 70 gewählt, gilt diese Option; mit Nr. 69 ebenfalls.

> [!NOTE]
> Erkannt wird nur, was vor deiner Figur gezeichnet wird. Gelände und Gebäude
> zeichnet das Spiel normalerweise vor den Figuren; ob auch Bäume oder andere
> Figuren davor erkannt werden, hängt von der Reihenfolge ab, in der das Spiel
> zeichnet – das muss der Test im Spiel zeigen.

<a id="patch-outlinereact"></a>
**Umrandung: Gesinnungsfarbe statt Klassenfarbe [BETA]** *(Nr. 74, Autor: St0ny)* {B74}

Zusatzoption zu Nr. 68: Alle Ränder bekommen die Farbe des Auswahlkreises
(bei Spielern meist blau), auch Ziel und Mouseover. Ohne diese Option haben
Spieler ihre Klassenfarbe, alle anderen die Farbe des Auswahlkreises.

''', 'en': '''<a id="patch-outline"></a>
**Outline for target and mouseover [BETA]** *(No. 68, Author: St0ny)* {B68}

Like in retail, the 3D figure of your target and the figure under the mouse
cursor get a thin outline (about 2 pixels). Players get their class color like
in the raid frames, everyone else the color of the selection circle: red
hostile, yellow neutral, green friendly. The outline only appears where the
figure is visible; where a wall stands in front of it, there is no outline.
Weapons, helmet and mount belong to the figure.

> [!WARNING]
> **BETA** – still untested, online and in game. That is why the patch is
> deselected by default and only in the dev branches for now, not in
> `st0ny-main`.

> [!WARNING]
> **On public servers please keep the default setting:** only No. 68, without
> the extra options No. 69–74. If the patch gets banned on a server, that is
> bad luck – there is nothing I can do about it. From then on it can only be
> used on your own private servers. So please be careful.

**Extra options** – patches of their own in the menu that need No. 68; all of
them are off by default:

| No. | Option | Effect |
|----:|--------|--------|
| [69](#patch-outlinewalls) | through walls | The outline also appears where the figure is hidden. |
| [70](#patch-outlineself) | own character | Your figure always has an outline. |
| [71](#patch-outlineparty) | own party | The up to 4 other players of your party of 5 always have an outline. |
| [72](#patch-outlineraid) | whole raid | All other players in the raid always have an outline – costs a lot of FPS. |
| [73](#patch-outlinehidden) | own character only hidden | Your figure only gets an outline where it is hidden. |
| [74](#patch-outlinereact) | reaction color | All outlines in the color of the selection circle, players too. |

If a figure is the target or under the mouse cursor, that outline applies.
Every outlined figure is drawn ten times (nine times with No. 69 or 73) – so
many outlines cost performance, noticeably in raids with No. 72.

How it works:
- The depth buffer gets a stencil part (D24S8 instead of D24X8). The game
  itself never uses stencil.
- While the figure is drawn, its visible pixels are marked in the stencil.
  Then it is drawn eight more times invisibly, each shifted by 2 pixels in
  every direction (via the shader's projection matrix), with depth test –
  these copies mark the outline and store the figure's depth there. Every
  outlined figure (target, mouseover, you, every party and raid member, up to
  48) gets a value of its own and so a color of its own.
- Whatever is drawn afterwards in front of the figure (e.g. bushes,
  mushrooms, grass) clears the mark at its pixels and so hides the outline as
  well. Things behind stay behind the outline thanks to the stored depth.
  Transparent things like water or spell effects leave the outline in place.
- Further parts of the same figure (cloak, weapon, mount) are drawn once more
  on their own outline without depth test, so no outline is left between the
  parts.
- With No. 69 the figure is also marked where it is hidden, and the copies run
  without depth test. Things drawn later no longer clear the outline then.
- With No. 73 your figure is also marked where it is hidden as well; its
  copies, however, only mark the outline where something already drawn lies in
  front of them.
- After the models and before the interface, a full-screen quad per outlined
  figure colors only its outline pixels; then the stencil is cleared and the
  game sends all its graphics states again.
- Code and data live in a section of their own (`.outl`, {SIZE} bytes). The
  extra options each set a single padding byte between two functions in
  `.text` to 1; the code reads these switches while drawing.

> [!NOTE]
> Only with `gxApi d3d9` (default) and a 24-bit depth buffer (default). With
> D3D9Ex, OpenGL or `gxDepthBits` 16/32 the patch switches itself off. The
> first version also ran in game with DXVK, because WoW uses Direct3D 9 there
> as well.

> [!NOTE]
> If all patches with a section of their own are active at the same time,
> there is no room left in the PE header for another section entry. Then the
> patcher extends the last appended section instead of adding a new one.

<a id="patch-outlinewalls"></a>
**Outline: visible through walls too [BETA]** *(No. 69, Author: St0ny)* {B69}

Extra option for No. 68: the outline also appears where the figure stands
behind a wall, a tree or another figure – you see its contours through
everything. This applies to all outlines: target, mouseover and the permanent
ones of No. 70 to 72.

> [!WARNING]
> Seeing through walls gives an advantage and may be considered cheating –
> **use it on your own servers only.**

<a id="patch-outlineself"></a>
**Outline: own character always outlined [BETA]** *(No. 70, Author: St0ny)* {B70}

Extra option for No. 68: your own figure always has an outline, in your class
color (with No. 74 in the color of the selection circle). If you are the
target or under the mouse cursor yourself, that outline applies. Together with
No. 73, No. 73 applies: only the hidden parts.

<a id="patch-outlineparty"></a>
**Outline: own party always outlined [BETA]** *(No. 71, Author: St0ny)* {B71}

Extra option for No. 68: the up to 4 other players of your party (`party1` to
`party4`) always have an outline, each in their class color (with No. 74 in
the color of the selection circle). Whoever is the target or under the mouse
cursor gets that outline. Players out of sight have none.

<a id="patch-outlineraid"></a>
**Outline: whole raid always outlined [BETA]** *(No. 72, Author: St0ny)* {B72}

Extra option for No. 68: all other players of your raid (up to 39) always
have an outline, each in their class color (with No. 74 in the color of the
selection circle). Your party is included, also outside of a raid – No. 71 is
not needed then. You yourself are only outlined by No. 70 or 73.

> [!WARNING]
> **Costs a lot of FPS:** every outlined figure is drawn ten times. With 25 or
> 40 players that is a lot of extra draw calls per frame. On weaker computers
> better use only No. 71.

<a id="patch-outlinehidden"></a>
**Outline: own character only where it is hidden [BETA]** *(No. 73, Author: St0ny)* {B73}

Extra option for No. 68: your figure only gets an outline where it is hidden
– if, for example, a house wall or a hill stands between the camera and you,
you see your contour on the wall. Visible parts get no outline. If you also
chose No. 70, this option applies; with No. 69 as well.

> [!NOTE]
> Only what is drawn before your figure is detected. The game normally draws
> terrain and buildings before the figures; whether trees or other figures in
> front are detected as well depends on the order in which the game draws –
> the test in game has to show that.

<a id="patch-outlinereact"></a>
**Outline: reaction color instead of class color [BETA]** *(No. 74, Author: St0ny)* {B74}

Extra option for No. 68: all outlines get the color of the selection circle
(mostly blue for players), target and mouseover too. Without this option
players have their class color, everyone else the color of the selection
circle.

'''}
SIZE = int(re.search(r"Add-CodeSection '\.outl' (0x[0-9A-F]+)", new_src).group(1), 16)
for lang, rd, pd, nr, und in (('de', 'README.de.md', 'PATCHES.de.md', 'Nr.', 'und'), ('en', 'README.md', 'PATCHES.en.md', 'No.', 'and')):
    s = open(d + rd, encoding='utf-8').read()
    for k in FLAGS:
        o, nw = nr + ' ' + txt(OF[k], und), nr + ' ' + txt(NF[k], und)
        if o == nw: continue
        s, n = relist(s, o, nw); assert n >= 1, (rd, k, o); print(rd, k, n, 'x:', o, '->', nw)
    s = re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(pd), lambda m: '| [%s](%s#' % (sh(m.group(1)), pd), s)
    s = re.sub(r'(?m)^\| \[\d+\]\(.*$', lambda m: refs(m.group(0)), s)
    m = re.search(r'(?m)^\| \[68\]\(%s#patch-outline\) \|.*\n' % re.escape(pd), s); assert m
    row = re.sub(r'[🟢🟡🟠🔴] \*\*\[[^\]]+\]\*\*', badge('outline', lang), m.group(0), count=1)
    new = ''.join('| [%d](%s#patch-%s) | %s | %s | St0ny | – | – | – |\n' % (69 + i, pd, pid, name, badge(pid, lang)) for i, (pid, name) in enumerate(ROWS[lang]))
    s = s[:m.start()] + row + new + WARN[lang] + s[m.end():]
    open(d + rd, 'w', encoding='utf-8', newline='\n').write(s)
    p = open(d + pd, encoding='utf-8').read()
    p = refs(p)
    a = p.index('<a id="patch-outline"></a>'); z = p.index('\n## ', a) + 1
    sec = SEC[lang].replace('{SIZE}', '0x%X' % SIZE)
    for n_, pid in ((68, 'outline'), (69, 'outlinewalls'), (70, 'outlineself'), (71, 'outlineparty'), (72, 'outlineraid'), (73, 'outlinehidden'), (74, 'outlinereact')):
        sec = sec.replace('{B%d}' % n_, badge(pid, lang))
    p = p[:a] + sec + p[z:]
    open(d + pd, 'w', encoding='utf-8', newline='\n').write(p)
print('Doku angepasst')

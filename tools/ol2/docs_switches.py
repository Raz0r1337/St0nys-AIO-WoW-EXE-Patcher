# Doku Umrandung: vier Umschalter statt J/N, Durch Waende nur Gruppe/Schlachtzug. Aufruf: docs_switches.py <Worktree>
import sys, re
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)
def block(p, start, end, new):
    s = open(w + '/' + p, encoding='utf-8').read()
    a = s.index(start); z = s.index(end, a)
    s = s[:a] + new + s[z:]
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

DE_SET = """**Einstellungen:** Nach der Patch-Auswahl fragt der Patcher vier Punkte als
Umschalter ab, je Punkt eine Zahl. ENTER übernimmt den Vorschlag in Klammern –
beim ersten Mal den Standard (fett), bei einer gepatchten `Wow.exe` den
aktuellen Stand.

| Punkt | Wahlen |
|-------|--------|
| Eigener Charakter | 1 = aus · **2 = nur wo verdeckt:** Rand nur dort, wo deine Figur verdeckt ist, etwa hinter einer Hauswand oder einem Hügel; sichtbare Teile bleiben ohne Rand · 3 = immer |
| Gruppe / Schlachtzug immer umrandet | **1 = aus** · 2 = 5er-Gruppe: die bis zu 4 Mitspieler (`party1` bis `party4`) · 3 = ganzer Schlachtzug: alle Mitspieler im Schlachtzug (bis zu 39), außerhalb eines Schlachtzugs deine Gruppe – **kostet viele FPS** |
| Durch Wände sichtbar | **1 = nie** · 2 = nur Gruppe/Schlachtzug: die Mitspieler aus dem Punkt davor auch dort, wo sie verdeckt sind; steht der auf „aus“, bekommen Gruppe bzw. Schlachtzug wie dein Charakter nur dort einen Rand, wo sie verdeckt sind · 3 = alle: jeder Rand, auch Ziel und Mouseover – **unsicher**, kann als Cheat gewertet werden, der Patcher warnt dann rot |
| Farbe | **1 = Klassenfarbe** · 2 = Gesinnungsfarbe: alle Ränder in der Farbe des Auswahlkreises (bei Spielern meist blau), auch Ziel und Mouseover; feindliche Spieler sind dann einfach rot und pulsieren nicht |

Ist eine Figur gerade Ziel oder unter dem Mauszeiger, gilt dieser Rand.
Mitspieler außer Sichtweite haben keinen. Die Einstellungen merkt sich der
Patcher wie andere Werte in `patcher_selection.ini` als Liste der
eingeschalteten Schalter, z. B. `value.outline=hidden,party` (Standard ist
`hidden`, `none` heißt alles aus; die Schalter heißen `hidden`, `self`,
`party`, `raid`, `wallsgroup`, `walls` und `react`).

"""
EN_SET = """**Settings:** After the patch selection the patcher asks four points as
switches, one number per point. ENTER takes the suggestion in brackets – the
default (bold) the first time, the current state for a patched `Wow.exe`.

| Point | Choices |
|-------|---------|
| Own character | 1 = off · **2 = only where hidden:** an outline only where your figure is hidden, for example behind a house wall or a hill; visible parts get no outline · 3 = always |
| Party / raid always outlined | **1 = off** · 2 = party of 5: the up to 4 other players (`party1` to `party4`) · 3 = whole raid: all other players in the raid (up to 39), your party outside of a raid – **costs a lot of FPS** |
| Visible through walls | **1 = never** · 2 = party/raid only: the other players from the point before also where they are hidden; if that one is "off", party or raid get an outline only where they are hidden, like your character · 3 = all: every outline, target and mouseover too – **unsafe**, may be considered cheating, the patcher then warns in red |
| Color | **1 = class color** · 2 = reaction color: all outlines in the color of the selection circle (mostly blue for players), target and mouseover too; hostile players are then simply red and do not pulse |

If a figure is the target or under the mouse cursor, that outline applies.
Players out of sight have none. The patcher remembers the settings like other
values in `patcher_selection.ini` as a list of the switches that are on, e.g.
`value.outline=hidden,party` (the default is `hidden`, `none` means all off;
the switches are called `hidden`, `self`, `party`, `raid`, `wallsgroup`,
`walls` and `react`).

"""
block('docs/PATCHES.de.md', '**Einstellungen:** Nach der Patch-Auswahl fragt der Patcher sechs Punkte mit', '> [!WARNING]\n> **Ganzer Schlachtzug kostet viele FPS:**', DE_SET)
block('docs/PATCHES.en.md', '**Settings:** After the patch selection the patcher asks six questions with', '> [!WARNING]\n> **Whole raid costs a lot of FPS:**', EN_SET)
edit('docs/PATCHES.de.md', [
("""> **Auf öffentlichen Servern bitte die Standard-Einstellung lassen:** vor dem
> Patchen nur „Eigener Charakter nur dort umrandet, wo er verdeckt ist?“ mit J
> beantworten, alle anderen Fragen mit N. Wird der Patch auf einem Server""",
 """> **Auf öffentlichen Servern bitte die Standard-Einstellung lassen:** vor dem
> Patchen bei allen Punkten ENTER drücken (eigener Charakter nur wo verdeckt,
> alles andere aus bzw. nie). Wird der Patch auf einem Server"""),
("""> Zeichenaufrufe pro Bild. Auf schwächeren Rechnern lieber nur die 5er-Gruppe
> nehmen.""", """> Zeichenaufrufe pro Bild. Auf schwächeren Rechnern lieber nur die 5er-Gruppe
> nehmen. Das gilt auch für „durch Wände: nur Gruppe/Schlachtzug“, wenn die
> Gruppe auf „aus“ steht: Dann werden im Schlachtzug alle Mitspieler so
> gezeichnet."""),
("""> **Nur dort, wo verdeckt:** Erkannt wird nur, was vor deiner Figur gezeichnet""",
 """> **Nur dort, wo verdeckt** (auch für Gruppe/Schlachtzug): Erkannt wird nur, was vor deiner Figur gezeichnet"""),
("""- Mit „nur dort, wo verdeckt“ wird deine Figur ebenfalls auch dort markiert,""",
 """- Mit „durch Wände: nur Gruppe/Schlachtzug“ gilt das nur für die Mitspieler:
  Sie stehen zuerst in der Liste der umrandeten Figuren, später Gezeichnetes
  löscht dann nur die Ränder der anderen. Steht die Gruppe auf „aus“, kommen
  Gruppe bzw. Schlachtzug trotzdem in die Liste und werden wie dein Charakter
  nur dort umrandet, wo sie verdeckt sind.
- Mit „nur dort, wo verdeckt“ wird deine Figur ebenfalls auch dort markiert,"""),
("""- Code und Daten liegen in einer eigenen Sektion (`.outl`, 0x118E Byte). Jede
  Einstellung ist ein einzelnes Füllbyte zwischen zwei Funktionen in `.text`,
  das bei J auf 1 gesetzt wird; der Code liest diese Schalter beim Zeichnen.""",
 """- Code und Daten liegen in einer eigenen Sektion (`.outl`, 0x1310 Byte). Jeder
  Schalter ist ein einzelnes Füllbyte zwischen zwei Funktionen in `.text`, das
  die gewählte Einstellung auf 1 setzt; der Code liest diese Schalter beim
  Zeichnen."""),
])
edit('docs/PATCHES.en.md', [
("""> **On public servers please keep the default setting:** before patching,
> answer only "Own character outlined only where it is hidden?" with Y and all
> other questions with N. If the patch gets banned on a server, that is bad""",
 """> **On public servers please keep the default setting:** before patching,
> press ENTER for every point (own character only where hidden, everything
> else off or never). If the patch gets banned on a server, that is bad"""),
("""> With 25 or 40 players that is a lot of extra draw calls per frame. On weaker
> computers better use only the party of 5.""", """> With 25 or 40 players that is a lot of extra draw calls per frame. On weaker
> computers better use only the party of 5. This also applies to "through
> walls: party/raid only" with party/raid set to "off": then all other players
> in the raid are drawn that way."""),
("""> **Only where hidden:** only what is drawn before your figure is detected.""",
 """> **Only where hidden** (also for party/raid): only what is drawn before your figure is detected."""),
("""- With "only where hidden" your figure is also marked where it is hidden as""",
 """- With "through walls: party/raid only" this applies to the other players
  only: they come first in the list of outlined figures, and things drawn
  later then only clear the outlines of the others. If party/raid is set to
  "off", party or raid are still put on the list and are outlined only where
  they are hidden, like your character.
- With "only where hidden" your figure is also marked where it is hidden as"""),
("""- Code and data live in a section of their own (`.outl`, 0x118E bytes). Each
  setting is a single padding byte between two functions in `.text` that is
  set to 1 with Y; the code reads these switches while drawing.""",
 """- Code and data live in a section of their own (`.outl`, 0x1310 bytes). Each
  switch is a single padding byte between two functions in `.text` that the
  chosen setting sets to 1; the code reads these switches while drawing."""),
])
edit('docs/README.de.md', [
("""   der Patcher die Werte ab, bei der Umrandung die Einstellungen mit J/N;
   danach speichert er die Auswahl.""", """   der Patcher die Werte ab, bei der Umrandung die Einstellungen (Umschalter,
   je Punkt eine Zahl); danach speichert er die Auswahl."""),
("""> verwendest, lass bitte die Standard-Einstellung – vor dem Patchen nur
> „Eigener Charakter nur dort umrandet, wo er verdeckt ist?“ mit J
> beantworten, alle anderen Fragen mit N. Wird der Patch auf einem Server""",
 """> verwendest, lass bitte die Standard-Einstellung – vor dem Patchen bei allen
> Punkten ENTER drücken (eigener Charakter nur wo verdeckt, alles andere aus
> bzw. nie). Wird der Patch auf einem Server"""),
])
edit('docs/README.md', [
("""   patcher asks for the values, for the outline the settings with Y/N; then it
   saves the selection.""", """   patcher asks for the values, for the outline the settings (switches, one
   number per point); then it saves the selection."""),
("""> keep the default setting – before patching, answer only "Own character
> outlined only where it is hidden?" with Y and all other questions with N. If""",
 """> keep the default setting – before patching, press ENTER for every point (own
> character only where hidden, everything else off or never). If"""),
])
# lange Zeilen in den beiden NOTE-Kaesten neu umbrechen
import textwrap
for fn, a in (('docs/PATCHES.de.md', '> **Nur dort, wo verdeckt** (auch'), ('docs/PATCHES.en.md', '> **Only where hidden** (also')):
    s = open(w + '/' + fn, encoding='utf-8').read()
    i = s.index(a); j = s.index('\n\n', i)
    para = ' '.join(l[2:] for l in s[i:j].split('\n'))
    s = s[:i] + '\n'.join('> ' + l for l in textwrap.wrap(para, 77, break_long_words=False, break_on_hyphens=False)) + s[j:]
    open(w + '/' + fn, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')

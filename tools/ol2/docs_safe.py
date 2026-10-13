# Doku Nr. 68: sicherer Standard (hidden,wallsgroup) und Abfrage 1 = Standard / 2 = Optionen. Aufruf: docs_safe.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

edit('docs/PATCHES.de.md', [
("""> **Auf öffentlichen Servern bitte die Standard-Einstellung lassen:** vor dem
> Patchen bei allen Punkten ENTER drücken (eigener Charakter nur wo verdeckt,
> alles andere aus bzw. nie). Wird der Patch auf einem Server
> gebannt, hast du Pech gehabt – daran kann ich nichts ändern. Ab dann ist er
> nur noch auf eigenen privaten Servern nutzbar. Also pass bitte auf.""",
"""> **Auf öffentlichen Servern bitte den sicheren Standard nehmen:** vor dem
> Patchen bei der Umrandung `1` wählen (dein Charakter sowie Gruppe und
> Schlachtzug nur dort umrandet, wo sie verdeckt sind). Wird der Patch auf
> einem Server gebannt, hast du Pech gehabt – daran kann ich nichts ändern. Ab
> dann ist er nur noch auf eigenen privaten Servern nutzbar. Also pass bitte
> auf."""),
("""**Einstellungen:** Nach der Patch-Auswahl fragt der Patcher vier Punkte als
Umschalter ab, je Punkt eine Zahl. ENTER übernimmt den Vorschlag in Klammern –
beim ersten Mal den Standard (fett), bei einer gepatchten `Wow.exe` den
aktuellen Stand.""",
"""**Einstellungen:** Nach der Patch-Auswahl fragt der Patcher zuerst nur:
`1` = sicheren Standard anwenden oder `2` = Patch-Optionen aufrufen (Achtung:
das kann den Patch unsicher machen). Der sichere Standard ist in der Tabelle
fett: dein Charakter nur wo verdeckt, Gruppe und Schlachtzug nicht immer
umrandet, aber durch Wände – und damit wie dein Charakter nur dort, wo sie
verdeckt sind –, Klassenfarbe. Vorgeschlagen ist `1`, wenn der bisherige Stand
der sichere Standard ist oder der Patch neu dazukommt, sonst `2`; eigene
Einstellungen gehen mit ENTER also nicht verloren. Nur bei `2` folgen die vier
Punkte als Umschalter, je Punkt eine Zahl. ENTER übernimmt dort den Vorschlag
in Klammern – beim ersten Mal den Standard, bei einer gepatchten `Wow.exe` den
aktuellen Stand."""),
("""| Durch Wände sichtbar | **1 = nie** · 2 = nur Gruppe/Schlachtzug: die Mitspieler""",
 """| Durch Wände sichtbar | 1 = nie · **2 = nur Gruppe/Schlachtzug:** die Mitspieler"""),
("""eingeschalteten Schalter, z. B. `value.outline=hidden,party` (Standard ist
`hidden`, `none` heißt alles aus; die Schalter heißen `hidden`, `self`,""",
"""eingeschalteten Schalter, z. B. `value.outline=hidden,party` (Standard ist
`hidden,wallsgroup`, `none` heißt alles aus; die Schalter heißen `hidden`, `self`,"""),
("""> **Ganzer Schlachtzug kostet viele FPS:** Jede Figur mit Leuchtrand wird
> 26-mal gezeichnet, Schlachtzug-Mitglieder außerhalb deiner 5er-Gruppe mit
> der dünnen Linie immer noch zehnmal. Bei 25 oder 40 Spielern sind das sehr
> viele zusätzliche Zeichenaufrufe pro Bild. Auf schwächeren Rechnern lieber nur die 5er-Gruppe
> nehmen. Das gilt auch für „durch Wände: nur Gruppe/Schlachtzug“, wenn die
> Gruppe auf „aus“ steht: Dann werden im Schlachtzug alle Mitspieler so
> gezeichnet.""",
"""> **Ganzer Schlachtzug kostet viele FPS:** Jede Figur mit Leuchtrand wird
> 26-mal gezeichnet, Schlachtzug-Mitglieder außerhalb deiner 5er-Gruppe mit
> der dünnen Linie immer noch zehnmal. Bei 25 oder 40 Spielern sind das sehr
> viele zusätzliche Zeichenaufrufe pro Bild. Auf schwächeren Rechnern lieber
> nur die 5er-Gruppe nehmen. Das gilt auch für „durch Wände: nur
> Gruppe/Schlachtzug“, wenn die Gruppe auf „aus“ steht – also auch für den
> sicheren Standard: Dann werden im Schlachtzug alle Mitspieler so
> gezeichnet."""),
])

edit('docs/PATCHES.en.md', [
("""> **On public servers please keep the default setting:** before patching,
> press ENTER for every point (own character only where hidden, everything
> else off or never). If the patch gets banned on a server, that is bad
> luck – there is nothing I can do about it. From then on it can only be used
> on your own private servers. So please be careful.""",
"""> **On public servers please use the safe default:** before patching, choose
> `1` for the outline (your character as well as party and raid outlined only
> where they are hidden). If the patch gets banned on a server, that is bad
> luck – there is nothing I can do about it. From then on it can only be used
> on your own private servers. So please be careful."""),
("""**Settings:** After the patch selection the patcher asks four points as
switches, one number per point. ENTER takes the suggestion in brackets – the
default (bold) the first time, the current state for a patched `Wow.exe`.""",
"""**Settings:** After the patch selection the patcher first only asks: `1` =
apply the safe default or `2` = open the patch options (caution: this can make
the patch unsafe). The safe default is bold in the table: your character only
where hidden, party and raid not always outlined but through walls – and so,
like your character, only where they are hidden –, class color. `1` is
suggested if the current state is the safe default or the patch is new,
otherwise `2`; so your own settings are not lost with ENTER. Only with `2`
the four points follow as switches, one number per point. ENTER takes the
suggestion in brackets there – the default the first time, the current state
for a patched `Wow.exe`."""),
("""| Visible through walls | **1 = never** · 2 = party/raid only: the other players""",
 """| Visible through walls | 1 = never · **2 = party/raid only:** the other players"""),
("""`value.outline=hidden,party` (the default is `hidden`, `none` means all off;""",
 """`value.outline=hidden,party` (the default is `hidden,wallsgroup`, `none` means all off;"""),
("""> **Whole raid costs a lot of FPS:** every figure with a glowing outline is
> drawn 26 times, raid members outside your party of 5 with the thin line
> still ten times. With 25 or 40 players that is a lot of extra draw calls per
> frame. On weaker
> computers better use only the party of 5. This also applies to "through
> walls: party/raid only" with party/raid set to "off": then all other players
> in the raid are drawn that way.""",
"""> **Whole raid costs a lot of FPS:** every figure with a glowing outline is
> drawn 26 times, raid members outside your party of 5 with the thin line
> still ten times. With 25 or 40 players that is a lot of extra draw calls per
> frame. On weaker computers better use only the party of 5. This also
> applies to "through walls: party/raid only" with party/raid set to "off" –
> so to the safe default as well: then all other players in the raid are
> drawn that way."""),
])

edit('docs/README.de.md', [
("""7. Bei Patches mit eigenem Wert (Sprunghöhe, Doppelsprung, Client-Infos) fragt
   der Patcher die Werte ab, bei der Umrandung die Einstellungen (Umschalter,
   je Punkt eine Zahl); danach speichert er die Auswahl.""",
"""7. Bei Patches mit eigenem Wert (Sprunghöhe, Doppelsprung, Client-Infos) fragt
   der Patcher die Werte ab, bei der Umrandung erst „sicherer Standard oder
   eigene Einstellungen“ und bei eigenen Einstellungen die Umschalter (je
   Punkt eine Zahl); danach speichert er die Auswahl."""),
("""> verwendest, lass bitte die Standard-Einstellung – vor dem Patchen bei allen
> Punkten ENTER drücken (eigener Charakter nur wo verdeckt, alles andere aus
> bzw. nie). Wird der Patch auf einem Server""",
"""> verwendest, nimm bitte den sicheren Standard – vor dem Patchen bei der
> Umrandung `1` wählen (dein Charakter sowie Gruppe und Schlachtzug nur dort
> umrandet, wo sie verdeckt sind). Wird der Patch auf einem Server"""),
])

edit('docs/README.md', [
("""7. For patches with their own value (jump height, double jump, client info) the
   patcher asks for the values, for the outline the settings (switches, one
   number per point); then it saves the selection.""",
"""7. For patches with their own value (jump height, double jump, client info) the
   patcher asks for the values, for the outline first "safe default or own
   settings" and with own settings the switches (one number per point); then
   it saves the selection."""),
("""> keep the default setting – before patching, press ENTER for every point (own
> character only where hidden, everything else off or never). If""",
"""> use the safe default – before patching, choose `1` for the outline (your
> character as well as party and raid outlined only where they are hidden). If"""),
])
print('ok')

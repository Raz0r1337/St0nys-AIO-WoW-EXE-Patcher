# Preset-Dank an Stormhand aus der Danksagung entfernen. Aufruf: thx.py <worktree> main|dev
import sys
wt, kind = sys.argv[1], sys.argv[2]
R = {'main': {
        'README.de.md': ('- Danke auch an **Stormhand** für das offizielle Preset seines Projekts\n'
                         '  [Project Reforged](https://projectreforged.github.io/wotlk/): Es steckt als\n'
                         '  Preset „Reforged“ in diesem Patcher und ist die Standard-Auswahl.\n', ''),
        'README.md': ('- Thanks also to **Stormhand** for the official preset of his project\n'
                      '  [Project Reforged](https://projectreforged.github.io/wotlk/): it is included\n'
                      '  as the preset "Reforged" and is the default selection.\n', '')},
     'dev': {
        'README.de.md': ('- Danke auch an **Stormhand** für die Erlaubnis, seine LuxShoulderCam\n'
                         '  einzubinden und als Vorlage für Visus – St0nyCam zu nutzen. Das offizielle\n'
                         '  Preset seines Projekts [Project Reforged](https://projectreforged.github.io/wotlk/)\n'
                         '  steckt als Preset „Reforged“ in diesem Patcher und ist die Standard-Auswahl.\n',
                         '- Danke auch an **Stormhand** für die Erlaubnis, seine LuxShoulderCam\n'
                         '  einzubinden und als Vorlage für Visus – St0nyCam zu nutzen.\n'),
        'README.md': ('- Thanks also to **Stormhand** for the permission to include his\n'
                      '  LuxShoulderCam and to use it as the template for Visus – St0nyCam. The\n'
                      '  official preset of his project\n'
                      '  [Project Reforged](https://projectreforged.github.io/wotlk/) is included as\n'
                      '  the preset "Reforged" and is the default selection.\n',
                      '- Thanks also to **Stormhand** for the permission to include his\n'
                      '  LuxShoulderCam and to use it as the template for Visus – St0nyCam.\n')}}
for f, (a, b) in R[kind].items():
    p = wt + '/docs/' + f
    raw = open(p, 'rb').read(); assert b'\r' not in raw, f
    s = raw.decode('utf-8'); assert s.count(a) == 1, (f, s.count(a))
    open(p, 'w', encoding='utf-8', newline='\n').write(s.replace(a, b))
    print(wt.split('/')[-1], f, 'ok')

import sys
wt = sys.argv[1]
R = {'docs/README.de.md': ('- Danke auch an **Stormhand** für die Erlaubnis, seinen CameraReforged-Patch\n  einzubauen. Das offizielle Preset seines Projekts\n  [Project Reforged](https://projectreforged.github.io/wotlk/) steckt als Preset\n  „Reforged“ in diesem Patcher und ist die Standard-Auswahl.\n',
                           '- Danke auch an **Stormhand** für das offizielle Preset seines Projekts\n  [Project Reforged](https://projectreforged.github.io/wotlk/): Es steckt als\n  Preset „Reforged“ in diesem Patcher und ist die Standard-Auswahl.\n'),
     'docs/README.md': ('- Thanks also to **Stormhand** for the permission to include his\n  CameraReforged patch. The official preset of his project\n  [Project Reforged](https://projectreforged.github.io/wotlk/) is included as\n  the preset "Reforged" and is the default selection.\n',
                        '- Thanks also to **Stormhand** for the official preset of his project\n  [Project Reforged](https://projectreforged.github.io/wotlk/): it is included\n  as the preset "Reforged" and is the default selection.\n')}
for f, (a, b) in R.items():
    p = wt + '/' + f; s = open(p, encoding='utf-8').read()
    assert s.count(a) == 1, (wt, f, s.count(a))
    open(p, 'w', encoding='utf-8', newline='\n').write(s.replace(a, b))
    assert 'CameraReforged' not in open(p, encoding='utf-8').read(), 'Rest in ' + f
print(wt.split('/')[-1], 'ok')

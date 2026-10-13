# Dank an Zendevve (Autor von CameraReforged) fuer die Idee hinter Visus - St0nyCam (README DE/EN).
# Aufruf: credit_zendevve.py <Worktree>
import sys
w = sys.argv[1]
def edit(path, a, b):
    s = open(path, encoding='utf-8').read()
    assert s.count(a) == 1, (path, s.count(a))
    open(path, 'w', encoding='utf-8', newline='\n').write(s.replace(a, a + b))
edit(w + '/docs/README.de.md',
     "- Danke auch an **Stormhand** für die Erlaubnis, seine LuxShoulderCam\n  einzubinden und als Vorlage für Visus – St0nyCam zu nutzen.\n",
     "- Danke an **Zendevve**, den Autor von CameraReforged, für die Idee hinter\n  Visus – St0nyCam.\n")
edit(w + '/docs/README.md',
     "- Thanks also to **Stormhand** for the permission to include his\n  LuxShoulderCam and to use it as the template for Visus – St0nyCam.\n",
     "- Thanks to **Zendevve**, the author of CameraReforged, for the idea behind\n  Visus – St0nyCam.\n")
print('ok')

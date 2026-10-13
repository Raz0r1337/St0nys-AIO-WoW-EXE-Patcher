import sys, os
wt = sys.argv[1]
reps = [
    ('AwesomeWotlkLib.dll Unterstuetzung aktivieren (Client-Erweiterungen von noname08662)',
     'AwesomeWotlkLib.dll beim Start laden (Client-Erweiterungen von noname08662)'),
    ('Enable AwesomeWotlkLib.dll support (client extensions by noname08662)',
     'Load AwesomeWotlkLib.dll at startup (client extensions by noname08662)'),
    ('WotLKExtensions.dll Unterstuetzung aktivieren (Client-Erweiterungen von Alyst3r)',
     'WotLKExtensions.dll beim Start laden (Client-Erweiterungen von Alyst3r)'),
    ('Enable WotLKExtensions.dll support (client extensions by Alyst3r)',
     'Load WotLKExtensions.dll at startup (client extensions by Alyst3r)'),
    ('AwesomeWotlkLib.dll Unterstützung aktivieren (Client-Erweiterungen von noname08662)',
     'AwesomeWotlkLib.dll beim Start laden (Client-Erweiterungen von noname08662)'),
    ('WotLKExtensions.dll Unterstützung aktivieren (Client-Erweiterungen von Alyst3r)',
     'WotLKExtensions.dll beim Start laden (Client-Erweiterungen von Alyst3r)'),
]
expect = {'apply_patches.ps1': 4, 'docs/PATCHES.de.md': 2, 'docs/PATCHES.en.md': 2,
          'docs/README.de.md': 2, 'docs/README.md': 2}
for rel, want in expect.items():
    p = os.path.join(wt, rel)
    b = open(p, 'rb').read()
    n = 0
    for old, new in reps:
        ob, nb = old.encode('utf-8'), new.encode('utf-8')
        c = b.count(ob)
        n += c
        b = b.replace(ob, nb)
    assert n == want, (rel, n, want)
    open(p, 'wb').write(b)
    print(rel, n)

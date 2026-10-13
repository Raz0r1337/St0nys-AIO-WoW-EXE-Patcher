# Kurzanleitung: Startmenue erwaehnen. Aufruf: usage.py <worktree>
import sys
wt = sys.argv[1]
for fn, a, b in (('README.de.md', '4. Sprache wählen (nur beim ersten Start), Patches auswählen, bestätigen.\n',
                  '4. Sprache wählen (nur beim ersten Start), im [Startmenü](#startmenü) `1` für das\n   Patch-Menü, Patches auswählen, bestätigen.\n'),
                 ('README.md', '4. Choose the language (first start only), select patches, confirm.\n',
                  '4. Choose the language (first start only), `1` in the [start menu](#start-menu)\n   for the patch menu, select patches, confirm.\n')):
    p = wt + '/docs/' + fn
    s = open(p, encoding='utf-8').read(); assert s.count(a) == 1, (fn, s.count(a))
    open(p, 'w', encoding='utf-8', newline='\n').write(s.replace(a, b))
print('usage ok', wt.split('/')[-1])

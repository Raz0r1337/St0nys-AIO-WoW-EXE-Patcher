# Absatz "Patches aendern oder zuruecknehmen" neu umbrechen. Aufruf: rewrap.py <worktree>
import sys, textwrap
wt = sys.argv[1]
for p, start in (('docs/README.de.md', 'Eingespielte Patches sind nicht endgültig.'), ('docs/README.md', 'Applied patches are not final.')):
    p = wt + '/' + p
    s = open(p, encoding='utf-8').read()
    a = s.index(start); z = s.index('\n\n', a)
    para = ' '.join(s[a:z].split('\n'))
    new = '\n'.join(textwrap.wrap(para, width=80, break_long_words=False, break_on_hyphens=False))
    s = s[:a] + new + s[z:]
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('rewrap ok')

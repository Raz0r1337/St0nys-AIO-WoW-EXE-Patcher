# AwesomeWotlkLib-Lader (awesome) aus dem Preset "Reforged" nehmen.
import re, sys
wt = sys.argv[1]
PS = wt + '/apply_patches.ps1'
raw = open(PS, encoding='ascii', newline='').read()
assert raw.count('\r\n') == raw.count('\n') and raw.count('\r\r') == 0
s = raw.replace('\r\n', '\n')
a = s.index('\n$PRESET_REFORGED = @(\n') + 1
z = s.index('\n)\n', a) + 3
block = s[a:z]
assert block.count("'awesome'") == 1, 'awesome nicht genau einmal im Preset'
for old, new in (("    'glue', 'awesome', 'lexara',\n", "    'glue', 'lexara',\n"),
                 ("    'glue', 'awesome',\n", "    'glue',\n")):
    if block.count(old) == 1:
        block = block.replace(old, new)
        break
else:
    raise SystemExit('Zeile mit awesome nicht gefunden')
assert "'awesome'" not in block
s = s[:a] + block + s[z:]
open(PS, 'w', encoding='ascii', newline='').write(s.replace('\n', '\r\n'))

for fn, md in (('README.de.md', 'PATCHES.de.md'), ('README.md', 'PATCHES.en.md')):
    p = wt + '/docs/' + fn
    t = open(p, encoding='utf-8', newline='').read()
    assert '\r' not in t
    lines = t.split('\n')
    hit = [i for i, l in enumerate(lines) if l.startswith('| [') and '(%s#patch-awesome)' % md in l]
    assert len(hit) == 1
    l = lines[hit[0]]
    old = '| FrostAtom | ✅ | ✅ | ✅ |'
    assert l.endswith(old), l[-60:]
    lines[hit[0]] = l[:-len(old)] + '| FrostAtom | – | ✅ | ✅ |'
    open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print(wt.split('/')[-1], 'noreforged OK')

# README-Spalten Reforged/Billy/St0ny gegen die Presets im Skript pruefen.
import re, sys
wt = sys.argv[1]
s = open(wt + '/apply_patches.ps1', encoding='ascii').read().replace('\r\n', '\n')
heads = re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$", s)
def preset(name):
    a = s.index('\n$%s = @(\n' % name); z = s.index('\n)\n', a)
    return re.findall(r"'([^']+)'", s[a:z])
R = preset('PRESET_REFORGED'); ST = preset('PRESET_STONY')
ids = [i for i, _ in heads]
assert set(R) <= set(ids) and set(ST) <= set(ids)
bad = 0
for fn, md in (('README.de.md', 'PATCHES.de.md'), ('README.md', 'PATCHES.en.md')):
    t = open(wt + '/docs/' + fn, encoding='utf-8').read()
    n = 0
    for pid, h in heads:
        row = [l for l in t.split('\n') if l.startswith('| [') and '(%s#patch-%s)' % (md, pid) in l]
        assert len(row) == 1, pid
        cells = [c.strip() for c in row[0].split('|')][-4:-1]
        exp = ['✅' if pid in R else '–', '✅' if 'On = $true' in h else '–', '✅' if pid in ST else '–']
        if cells != exp: print('  MISMATCH', fn, pid, cells, exp); bad = 1
        n += 1
    print(wt.split('/')[-1], fn, 'rows', n)
print('PRESETS BAD' if bad else 'PRESETS OK')

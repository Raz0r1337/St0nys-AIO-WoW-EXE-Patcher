# Welche der betroffenen Ids steckten in den Presets der alten Versionen? Aufruf: preset_hit.py <Repo> <Commit-Liste>
import sys, re, subprocess
repo = sys.argv[1]
aff = {'camera', 'ghostattack', 'glue', 'naked', 'sliders', 'nothrottle', 'year2031', 'voicedll'}
res = {}
for c in open(sys.argv[2]).read().split():
    src = subprocess.run(['git', '-C', repo, 'show', c + ':apply_patches.ps1'], capture_output=True, text=True).stdout
    date = subprocess.run(['git', '-C', repo, 'log', '-1', '--format=%ad', '--date=format:%m-%d %H:%M', c], capture_output=True, text=True).stdout.strip()
    for m in re.finditer(r'(?m)^\$PRESET_(\w+) = @\(([^)]*)\)', src):
        ids = set(re.findall(r"'([a-z0-9]+)'", m.group(2)))
        for i in sorted(ids & aff):
            r = res.setdefault((m.group(1), i), [date, date]); r[0] = min(r[0], date); r[1] = max(r[1], date)
    # Default (On = $true) = Preset Reforged in fruehen Versionen?
    for m in re.finditer(r"@\{ Id = '([a-z0-9]+)'; Cat = '[a-z]+'; On = \$true", src):
        if m.group(1) in aff:
            r = res.setdefault(('On', m.group(1)), [date, date]); r[0] = min(r[0], date); r[1] = max(r[1], date)
for (p, i), (a, z) in sorted(res.items()):
    print('%-9s %-12s %s bis %s' % (p, i, a, z))

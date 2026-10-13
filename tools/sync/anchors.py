import re, sys, os
wt = sys.argv[1]
def slugs(path):
    out, seen = set(), {}
    incode = False
    for line in open(path, encoding='utf-8'):
        if line.startswith('```'):
            incode = not incode
            continue
        if incode:
            continue
        m = re.match(r'^(#{1,6})\s+(.*?)\s*$', line)
        if m:
            s = re.sub(r'[^\w\- ]', '', m.group(2).strip().lower()).replace(' ', '-')
            n = seen.get(s, 0)
            seen[s] = n + 1
            out.add(s if n == 0 else f'{s}-{n}')
        for a in re.findall(r'<a (?:id|name)="([^"]+)"', line):
            out.add(a)
    return out
bad = 0
for f in ['docs/README.md', 'docs/README.de.md', 'docs/PATCHES.de.md', 'docs/PATCHES.en.md']:
    p = os.path.join(wt, f)
    own = slugs(p)
    txt = open(p, encoding='utf-8').read()
    n = 0
    for target, anc in re.findall(r'\]\(([^)#\s]*)#([^)\s]+)\)', txt):
        n += 1
        tp = p if not target else os.path.join(os.path.dirname(p), target)
        if target.startswith('http'):
            continue
        s = own if not target else slugs(tp)
        if anc not in s:
            bad += 1
            print('BROKEN', f, target + '#' + anc)
    print(f, 'links', n)
# Links aus dem Release-Workflow
wf = os.path.join(wt, '.github/workflows/release.yml')
if os.path.exists(wf):
    s = slugs(os.path.join(wt, 'docs/README.md'))
    for anc in re.findall(r'README\.md#([\w-]+)', open(wf, encoding='utf-8').read()):
        ok = anc in s
        bad += not ok
        print('release.yml #' + anc, 'OK' if ok else 'BROKEN')
print('ANCHORS OK' if bad == 0 else f'{bad} BROKEN')

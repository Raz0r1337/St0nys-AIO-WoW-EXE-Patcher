# Doku fuer die Umrandung (Outline) in st0ny-dev: Zeile, Abschnitt aus dem Outline-Zweig,
# Nummern ab 68 (+1), Listen. Aufruf: docs_edit.py <dev-worktree> <altes dev-Skript> <outline-worktree>
import re, sys
wt = sys.argv[1]; d = wt + '/docs/'; od = sys.argv[3] + '/docs/'
old_src = open(sys.argv[2], encoding='ascii').read().replace('\r\n', '\n')
new_src = open(wt + '/apply_patches.ps1', encoding='ascii').read().replace('\r\n', '\n')
oh = re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$", old_src); nh = re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$", new_src)
C = [i for i, _ in nh].index('outline') + 1
assert C == 68 and [i for i, _ in oh][C - 1] == 'tracker' and [i for i, _ in oh][C - 2] == 'iconsnap'
FLAGS = ('BanRisk', 'PublicUntested', 'GameUntested', 'GrowsExe', 'DllRisky')
fl = lambda hs: {k: [i + 1 for i, (_, h) in enumerate(hs) if k + ' = $true' in h] for k in FLAGS}
OF, NF = fl(oh), fl(nh)
def rng(L):
    out = []; i = 0
    while i < len(L):
        j = i
        while j + 1 < len(L) and L[j + 1] == L[j] + 1: j += 1
        out += ([str(L[i])] if j == i else ([str(L[i]), str(L[j])] if j == i + 1 else ['%d–%d' % (L[i], L[j])])); i = j + 1
    return out
def txt(L, und):
    r = rng(L); return r[0] if len(r) == 1 else ', '.join(r[:-1]) + ' ' + und + ' ' + r[-1]
def relist(s, old, new):
    pat = re.escape(old).replace('\\ ', r'\s+')
    def f(m):
        span = m.group(0)
        if '\n' not in span: return new
        k = span.index('\n'); before = re.sub(r'\s+', ' ', span[:k]); ind = re.match(r'\n(\s*)', span[k:]).group(1)
        cut = new.rfind(' ', 0, len(before) + 1)
        return new if cut <= 0 else new[:cut] + '\n' + ind + new[cut + 1:]
    return re.subn(pat, f, s)
def sh(n):
    n = int(n); return str(n + 1 if n >= C else n)
def refs(s):
    def f(m):
        out = '%s %s' % (m.group(1), sh(m.group(2)))
        if m.group(3): out += m.group(3) + sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?', f, s)
def section(path):
    s = open(path, encoding='utf-8').read()
    a = s.index('<a id="patch-outline"></a>'); z = s.index('\n## ', a) + 1
    return s[a:z]
for lang, rd, pd, nr, und in (('de', 'README.de.md', 'PATCHES.de.md', 'Nr.', 'und'), ('en', 'README.md', 'PATCHES.en.md', 'No.', 'and')):
    s = open(d + rd, encoding='utf-8').read()
    for k in FLAGS:
        o, nw = nr + ' ' + txt(OF[k], und), nr + ' ' + txt(NF[k], und)
        if o == nw: continue
        s, n = relist(s, o, nw); assert n >= 1, (rd, k, o); print(rd, k, n, 'x:', o, '->', nw)
    s = re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(pd), lambda m: '| [%s](%s#' % (sh(m.group(1)), pd), s)
    s = re.sub(r'(?m)^\| \[\d+\]\(.*$', lambda m: refs(m.group(0)), s)
    row = [l for l in open(od + rd, encoding='utf-8').read().split('\n') if l.startswith('| [65](%s#patch-outline)' % pd)]
    assert len(row) == 1; row = row[0].replace('| [65](', '| [68](', 1) + '\n'
    m = re.search(r'(?m)^\| \[67\]\(%s#patch-iconsnap\).*\n' % re.escape(pd), s); assert m
    s = s[:m.end()] + row + s[m.end():]
    open(d + rd, 'w', encoding='utf-8', newline='\n').write(s)
    s = open(d + pd, encoding='utf-8').read()
    s = refs(s)
    sec = section(od + pd); t = '*(%s 65, ' % nr; assert sec.count(t) == 1 and sec.count(nr + ' ') == 1, lang
    sec = sec.replace(t, '*(%s 68, ' % nr)
    a = s.index('<a id="patch-iconsnap"></a>'); z = s.index('\n## ', a) + 1
    s = s[:z] + sec + s[z:]
    open(d + pd, 'w', encoding='utf-8', newline='\n').write(s)
print('Doku angepasst')

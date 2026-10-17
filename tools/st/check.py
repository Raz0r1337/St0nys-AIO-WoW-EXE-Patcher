#!/usr/bin/env python3
# Abgleich Patcher <-> Doku: Nummern/Anker, Status je Patch (Tabelle + Ueberschrift), Namen,
# Preset-Spalten (Reforged/Billy/St0ny) und die Status-Listen unter "Hinweise".
# Aufruf: check.py <Zweig-Ordner>
import re, sys, os
D = sys.argv[1]
src = open(os.path.join(D, 'apply_patches.ps1'), encoding='ascii').read().replace('\r\n', '\n')
ents = []
for m in re.finditer(r"(?m)^    @\{ Id = '([^']+)';([^\n]*)\n(.*?)\n    \}\}\n", src, re.S):
    body = m.group(3); head = m.group(2)
    def g(k):
        x = re.search(r"(?m)^       %s = '((?:[^']|'')*)'" % k, body); return x.group(1).replace("''", "'") if x else None
    ents.append(dict(id=m.group(1), flags={k for k in ('On', 'BanRisk', 'Blocked', 'PublicUntested', 'GameUntested', 'GrowsExe', 'DllRisky') if re.search(k + r' = \$true', head)}, de=g('De'), en=g('En')))
ids = [e['id'] for e in ents]
def preset(name):
    m = re.search(r'(?m)^\$%s = @\((.*?)\n\)' % name, src, re.S); return set(re.findall(r"'(\w+)'", m.group(1)))
REF, STONY = preset('PRESET_REFORGED'), preset('PRESET_STONY')
T = {'de': dict(BanRisk='unsicher', Blocked='riskant', Both='ungetestet', PublicUntested='online ungetestet', GameUntested='ingame ungetestet', GrowsExe='Exe wird größer', DllRisky='DLL riskant', safe='sicher'),
     'en': dict(BanRisk='unsafe', Blocked='risky', Both='untested', PublicUntested='untested online', GameUntested='untested ingame', GrowsExe='exe grows', DllRisky='DLL risky', safe='safe')}
def status(e, lang):
    f = e['flags']; t = T[lang]; tags = []
    if 'BanRisk' in f: tags.append(t['BanRisk'])
    if 'Blocked' in f: tags.append(t['Blocked'])
    if {'PublicUntested', 'GameUntested'} <= f: tags.append(t['Both'])
    elif 'PublicUntested' in f: tags.append(t['PublicUntested'])
    elif 'GameUntested' in f: tags.append(t['GameUntested'])
    warn = bool(tags)
    if not warn: tags.append(t['safe'])
    if 'GrowsExe' in f: tags.append(t['GrowsExe'])
    if 'DllRisky' in f: tags.append(t['DllRisky'])
    col = '🔴' if 'BanRisk' in f else '🟠' if warn else '🟡' if f & {'GrowsExe', 'DllRisky'} else '🟢'
    return '%s **[%s]**' % (col, ' - '.join(tags))
def norm(s): return s.replace('„', '"').replace('“', '"').replace('”', '"').replace('z. B.', 'z.B.').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss').replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue')
bad = 0
def err(*a):
    global bad; bad += 1; print('  FEHLER', *a)
for lang, rd, pd, nr, und in (('de', 'README.de.md', 'PATCHES.de.md', 'Nr.', 'und'), ('en', 'README.md', 'PATCHES.en.md', 'No.', 'and')):
    r = open(os.path.join(D, 'docs', rd), encoding='utf-8').read(); p = open(os.path.join(D, 'docs', pd), encoding='utf-8').read()
    rows = re.findall(r'(?m)^\| \[(\d+)\]\(%s#patch-([^)]+)\) \| (.*?) \| ([🟢🟡🟠🔴] \*\*\[[^]]*\]\*\*) \| (.*?) \| (✅|–) \| (✅|–) \| (✅|–) \|$' % re.escape(pd), r)
    print(rd, 'Zeilen', len(rows), 'Patches', len(ids))
    if [int(x[0]) for x in rows] != list(range(1, len(ids) + 1)) or [x[1] for x in rows] != ids: err(rd, 'Nummern/Anker passen nicht')
    for e, x in zip(ents, rows):
        n = norm(x[2]); want = e[lang]
        if not n.startswith(norm(want)): err(rd, x[0], 'Name', repr(x[2][:70]), '!=', repr(want))
        if x[3] != status(e, lang): err(rd, x[0], 'Status', x[3], '!=', status(e, lang))
        for col, has in ((5, e['id'] in REF), (6, 'On' in e['flags']), (7, e['id'] in STONY)):
            if (x[col] == '✅') != has: err(rd, x[0], e['id'], ['', '', '', '', '', 'Reforged', 'Billy', 'St0ny'][col], x[col])
    heads = re.findall(r'<a id="patch-([^"]+)"></a>\n\*\*(.*?)\*\* \*\(%s (\d+)(?:, [^\n]*?)?\)\* ([🟢🟡🟠🔴] \*\*\[[^]]*\]\*\*)\n' % re.escape(nr), p)
    print(pd, 'Abschnitte', len(heads))
    if [h[0] for h in heads] != ids or [int(h[2]) for h in heads] != list(range(1, len(ids) + 1)): err(pd, 'Anker/Nummern passen nicht')
    for e, h in zip(ents, heads):
        if norm(h[1]) != norm(e[lang]): err(pd, h[2], 'Name', repr(h[1][:70]), '!=', repr(e[lang]))
        if h[3] != status(e, lang): err(pd, h[2], 'Status', h[3], '!=', status(e, lang))
    # Listen unter "Hinweise"
    flat = re.sub(r'\s*\n\s*', ' ', r)
    def rng(L):
        out = []; i = 0
        while i < len(L):
            j = i
            while j + 1 < len(L) and L[j + 1] == L[j] + 1: j += 1
            out += [str(L[i])] if j == i else ([str(L[i]), str(L[j])] if j == i + 1 else ['%d–%d' % (L[i], L[j])]); i = j + 1
        return out
    def txt(L):
        x = rng(L); return nr + ' ' + (x[0] if len(x) == 1 else ', '.join(x[:-1]) + ' ' + und + ' ' + x[-1])
    for k in ('BanRisk', 'Blocked', 'PublicUntested', 'GameUntested', 'GrowsExe', 'DllRisky'):
        L = [i + 1 for i, e in enumerate(ents) if k in e['flags']]
        t = txt(L)
        if t not in flat: err(rd, 'Liste', k, 'fehlt:', t)
print('ALLES OK' if not bad else '%d FEHLER' % bad)
sys.exit(1 if bad else 0)

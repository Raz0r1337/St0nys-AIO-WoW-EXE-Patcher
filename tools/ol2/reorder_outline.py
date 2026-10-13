# Umrandung (outline) hinter Nr. 65 (nofade) einsortieren: outline 68 -> 66, hdportraits 66 -> 67,
# iconsnap 67 -> 68. Skript, README DE/EN, PATCHES DE/EN. Aufruf: reorder_outline.py <Worktree>
import sys, re
w = sys.argv[1]
MAP = {66: 67, 67: 68, 68: 66}

def rd(p, crlf=False):
    raw = open(w + '/' + p, 'rb').read()
    s = raw.decode('ascii' if crlf else 'utf-8')
    return s.replace('\r\n', '\n') if crlf else s

def wr(p, s, crlf=False):
    if crlf: open(w + '/' + p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
    else: open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

def once(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)

def renum(s):
    # "Nr. 66" / "No. 66" (nur die Zahl direkt dahinter) nach MAP
    return re.sub(r'(Nr\.|No\.) (6[678])(?!\d)', lambda m: '%s %d' % (m.group(1), MAP[int(m.group(2))]), s)

# --- Skript: Eintrag verschieben ---
s = rd('apply_patches.ps1', crlf=True)
a = s.index("    @{ Id = 'outline'")
z = s.index("    @{ Id = ", a + 10)
if s.rfind('    # ---', a, z) >= 0: z = s.rfind('    # ---', a, z)
block = s[a:z]
assert block.endswith('}}\n\n'), repr(block[-20:])
s = s[:a] + s[z:]
h = s.index("    @{ Id = 'hdportraits'")
s = s[:h] + block + s[h:]
s = once(s, '(Nr. 9, 66 und 67 vergroessern die Wow.exe)', '(Nr. 9, 67 und 68 vergroessern die Wow.exe)')
ids = re.findall(r"(?m)^    @\{ Id = '([^']+)'", s)
assert ids[63:68] == ['notransparency', 'nofade', 'outline', 'hdportraits', 'iconsnap'] and len(ids) == 90, ids[62:69]
wr('apply_patches.ps1', s, crlf=True)

# --- README: Zeilen umstellen und umnummerieren, Listen ---
for fn, md, nr in (('docs/README.de.md', 'PATCHES.de.md', 'Nr.'), ('docs/README.md', 'PATCHES.en.md', 'No.')):
    s = rd(fn)
    rows = {}
    for idn, num in (('hdportraits', 66), ('iconsnap', 67), ('outline', 68)):
        m = re.search(r'(?m)^\| \[%d\]\(%s#patch-%s\) .*\n' % (num, re.escape(md), idn), s)
        rows[idn] = m.group(0)
    old = rows['hdportraits'] + rows['iconsnap'] + rows['outline']
    new = (rows['outline'].replace('| [68]', '| [66]', 1) + rows['hdportraits'].replace('| [66]', '| [67]', 1)
           + rows['iconsnap'].replace('| [67]', '| [68]', 1))
    s = once(s, old, new)
    if nr == 'Nr.':
        s = once(s, 'Drei davon (Nr. 9, 66 und 67)', 'Drei davon (Nr. 9, 67 und 68)')
        s = once(s, 'Nr. 26, 31, 32, 42, 47, 54, 65, 68, 72, 75–77 und 84', 'Nr. 26, 31, 32, 42, 47, 54, 65, 66, 72, 75–77 und 84')
        s = once(s, 'Nr. 25, 26, 31, 32, 47, 54, 65, 68 und 84', 'Nr. 25, 26, 31, 32, 47, 54, 65, 66 und 84')
        s = once(s, '**Umrandung (Nr. 68) auf öffentlichen Servern:**', '**Umrandung (Nr. 66) auf öffentlichen Servern:**')
    else:
        s = once(s, '(No. 9, 66 and 67)', '(No. 9, 67 and 68)')
        s = once(s, 'No. 26, 31, 32, 42, 47, 54, 65, 68, 72, 75–77 and 84', 'No. 26, 31, 32, 42, 47, 54, 65, 66, 72, 75–77 and 84')
        s = once(s, 'No. 25, 26, 31, 32, 47, 54, 65, 68 and 84', 'No. 25, 26, 31, 32, 47, 54, 65, 66 and 84')
        s = once(s, '**Outline (No. 68) on public servers:**', '**Outline (No. 66) on public servers:**')
    assert not re.search(r'(Nr\.|No\.) 6[678](?!\d)', s.replace('(Nr. 66)', '').replace('(No. 66)', '')), fn
    wr(fn, s)

# --- PATCHES: Abschnitt verschieben, Kopfzeilen und Verweise umnummerieren ---
for fn, nxt in (('docs/PATCHES.de.md', '## Interface & Komfort'), ('docs/PATCHES.en.md', '## Interface & comfort')):
    s = rd(fn)
    a = s.index('<a id="patch-outline"></a>')
    z = s.index(nxt, a)
    sec = s[a:z]
    s = s[:a] + s[z:]
    h = s.index('<a id="patch-hdportraits"></a>')
    s = s[:h] + sec + s[h:]
    s = renum(s)
    wr(fn, s)
print('ok')

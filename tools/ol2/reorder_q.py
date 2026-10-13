# Umrandung: Frage "nur wo verdeckt" direkt ueber "immer umrandet"; J/N-Werte aus patcher_state.ini in die
# Reihenfolge der Fragen bringen. Aufruf: reorder_q.py <Worktree> [<mkoutline6.py>]
import sys
w = sys.argv[1]
HID = """    @{ Key = 'hidden'; Va = 0x6ABF3F
       De = 'Eigener Charakter nur dort umrandet, wo er verdeckt ist?'; En = 'Own character outlined only where it is hidden?'
       ShortDe = 'eigener Charakter nur verdeckt'; ShortEn = 'own character only hidden' }
"""
SELF = """    @{ Key = 'self'; Va = 0x6ABAAF
"""
def reorder(s, hid, selfh):
    assert s.count(hid) == 1 and s.count(selfh) == 1
    s = s.replace(hid, '')
    return s.replace(selfh, hid + selfh)
def edit(p, fn, crlf=False):
    raw = open(p, 'rb').read()
    if crlf: assert raw.count(b'\r\n') == raw.count(b'\n')
    s = raw.decode('ascii' if crlf else 'utf-8').replace('\r\n', '\n')
    s = fn(s)
    if crlf: open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
    else: open(p, 'w', encoding='utf-8', newline='\n').write(s)
def once(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a)); return s.replace(a, b)
def script(s):
    s = reorder(s, HID, SELF)
    s = once(s, """    if ($st.Values.ContainsKey('clientdate')) { $st.Values['clientdate'] = ConvertTo-ClientDate $st.Values['clientdate'] }   # aeltere Versionen: ohne Uhrzeit
""", """    if ($st.Values.ContainsKey('clientdate')) { $st.Values['clientdate'] = ConvertTo-ClientDate $st.Values['clientdate'] }   # aeltere Versionen: ohne Uhrzeit
    # J/N-Werte (z.B. Umrandung) in die Reihenfolge der Fragen bringen - die
    # kann sich zwischen Versionen aendern, gleiche Antworten sind keine Aenderung.
    foreach ($p in $patches) {
        if (-not $p.Questions -or -not $st.Values.ContainsKey($p.Id)) { continue }
        $k = Get-OptionKeys $p.Questions $st.Values[$p.Id]
        if ($null -ne $k) { $st.Values[$p.Id] = ConvertTo-OptionValue $p.Questions $k }
    }
""")
    return s
edit(w + '/apply_patches.ps1', script, crlf=True)
if len(sys.argv) > 2:
    # Generator: dort mit Platzhalter 0x%X
    def gen(s):
        hid = HID.replace('0x6ABF3F', '0x%X'); selfh = SELF.replace('0x6ABAAF', '0x%X')
        s = reorder(s, hid, selfh)
        return once(s, "% (F['FWALLS'], F['FSELF'], F['FPARTY'], F['FRAID'], F['FHIDDEN'], F['FREACT'])",
                       "% (F['FWALLS'], F['FHIDDEN'], F['FSELF'], F['FPARTY'], F['FRAID'], F['FREACT'])")
    edit(sys.argv[2], gen)
def docs_de(s):
    rows = s.split('\n')
    i = [k for k, l in enumerate(rows) if l.startswith('| Eigener Charakter nur dort umrandet')][0]
    j = [k for k, l in enumerate(rows) if l.startswith('| Eigener Charakter immer umrandet?')][0]
    r = rows.pop(i); rows.insert(j, r)
    s = '\n'.join(rows)
    return once(s, """`walls`, `self`, `party`, `raid`, `hidden` und `react`).""", """`walls`, `hidden`, `self`, `party`, `raid` und `react`).""")
def docs_en(s):
    rows = s.split('\n')
    i = [k for k, l in enumerate(rows) if l.startswith('| Own character outlined only where it is hidden?')][0]
    j = [k for k, l in enumerate(rows) if l.startswith('| Own character always outlined?')][0]
    r = rows.pop(i); rows.insert(j, r)
    s = '\n'.join(rows)
    return once(s, """`walls`, `self`, `party`, `raid`, `hidden` and `react`).""", """`walls`, `hidden`, `self`, `party`, `raid` and `react`).""")
edit(w + '/docs/PATCHES.de.md', docs_de)
edit(w + '/docs/PATCHES.en.md', docs_en)
print('ok')

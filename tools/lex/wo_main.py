# wow_optimize-Lader als Nr. 27 nach main (vor awesome), Nummern ab 27 +1.
# Aufruf: python3 wo_main.py <main-worktree> <dev-worktree>
import re, sys
wt, devwt = sys.argv[1], sys.argv[2]
def once(s, a, b, label=''):
    n = s.count(a); assert n == 1, '%s: %d Treffer fuer %r' % (label, n, a[:100]); return s.replace(a, b)
def mp(n): n = int(n); return n if n < 27 else n + 1
def refs(s):
    def f(m):
        out = '%s %s' % (m.group(1), mp(m.group(2)))
        if m.group(3): out += m.group(3) + str(mp(m.group(4)))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?', f, s)
def section(s, anchor):
    a = s.index('<a id="patch-%s"></a>' % anchor)
    nx = [k for k in (s.find('\n<a id="', a + 1), s.find('\n## ', a + 1)) if k != -1]
    return a, min(nx) + 1
rd = lambda p: open(p, encoding='utf-8', newline='').read()
def wr(p, s): open(p, 'w', encoding='utf-8', newline='\n').write(s)

# ------------------------------------------------------------ Skript
dev = open(devwt + '/apply_patches.ps1', 'rb').read().decode('ascii').replace('\r\n', '\n')
a = dev.index("    @{ Id = 'wowoptimize'"); b = dev.index("    @{ Id = 'awesome'")
entry = dev[a:b]; assert entry.endswith('    }}\n\n') and 'Nr.' not in entry and '[BETA]' not in entry
entry = once(entry, "        # 0x76E490, den nur der Einstiegspunkt erreicht (nach dem Lexara-Lader,\n"
                    "        # vor dem Sprung, den der voice.dll-Lader umbiegt). Der Code steht in\n"
                    "        # acht freien Luecken zwischen Funktionen, den DLL-Namen baut der Thread\n"
                    "        # auf dem Stack. Dateigroesse und PE-Header bleiben unveraendert.\n",
                    "        # 0x76E490, den nur der Einstiegspunkt erreicht (nach dem Lexara-Lader).\n"
                    "        # Der Code steht in acht freien Luecken zwischen Funktionen, den\n"
                    "        # DLL-Namen baut der Thread auf dem Stack. Dateigroesse und PE-Header\n"
                    "        # bleiben unveraendert.\n", 'voice-Kommentar')
p = wt + '/apply_patches.ps1'
s = open(p, 'rb').read().decode('ascii'); assert s.count('\r\n') == s.count('\n'); s = s.replace('\r\n', '\n')
assert "Id = 'wowoptimize'" not in s
s = once(s, "    @{ Id = 'awesome'", entry + "    @{ Id = 'awesome'", 'Einfuegen')
out = []
for x in s.split('\n'):
    if re.match(r'^[a-z0-9]+;', x) or 'Name mit Patch-Nummer davor' in x or x.startswith('# Warmane getestet (Nr. 9, 63 und 64'):
        out.append(x)
    else:
        out.append(refs(x))
s = '\n'.join(out)
s = once(s, "# Warmane getestet (Nr. 9, 63 und 64 vergroessern die Wow.exe); dazu der\n",
            "# Warmane getestet (Nr. 9, 64 und 65 vergroessern die Wow.exe); dazu der\n", 'Reforged-Kommentar')
assert '# Lexara-Lader (Nr. 30, Patch sicher, DLL riskant)' in s
# St0ny-Preset: Block aus dev uebernehmen (gleiche Liste plus wowoptimize)
pat = re.compile(r'(?ms)^\$PRESET_STONY = @\(\n.*?^\)\n')
blk_dev = pat.search(dev).group(0); blk_main = pat.search(s).group(0)
ids = lambda t: re.findall(r"'([^']+)'", t)
assert [i for i in ids(blk_dev) if i != 'wowoptimize'] == ids(blk_main), 'St0ny-Preset weicht ab'
s = s.replace(blk_main, blk_dev)
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))

# ------------------------------------------------------------ README
LEG = {'de': [("Nr. 4, 10,\n    11, 23–25, 41, 42, 45–50, 74 und 81–85 (rote Warnung).", "Nr. 4, 10,\n    11, 23–25, 42, 43, 46–51, 75 und 82–86 (rote Warnung)."),
              ("Nr. 26, 39, 44, 51, 62, 68 und 71–73 (orange Warnung).", "Nr. 26, 40, 45, 52, 63, 69 und 72–74 (orange Warnung)."),
              ("Nr. 25, 26, 44, 51 und 62 (orange Warnung).", "Nr. 25, 26, 45, 52 und 63 (orange Warnung)."),
              ("Nr. 9, 50, 63, 64 und 74. Das ist", "Nr. 9, 51, 64, 65 und 75. Das ist"),
              ("erkannt oder blockiert werden kann: Nr. 27–29\n", "erkannt oder blockiert werden kann: Nr. 27–30\n"),
              ("(Nr. 9, 50, 63, 64 und 74), entfernen", "(Nr. 9, 51, 64, 65 und 75), entfernen"),
              ("Drei davon (Nr. 9, 63 und 64) vergrößern", "Drei davon (Nr. 9, 64 und 65) vergrößern")],
       'en': [("No. 4, 10, 11, 23–25,\n    41, 42, 45–50, 74 and 81–85 (red warning).", "No. 4, 10, 11, 23–25,\n    42, 43, 46–51, 75 and 82–86 (red warning)."),
              ("No. 26, 39, 44, 51, 62, 68 and 71–73 (orange warning).", "No. 26, 40, 45, 52, 63, 69 and 72–74 (orange warning)."),
              ("No. 25, 26, 44, 51 and 62 (orange warning).", "No. 25, 26, 45, 52 and 63 (orange warning)."),
              ("No. 9, 50,\n    63, 64 and 74. This does not", "No. 9, 51,\n    64, 65 and 75. This does not"),
              ("detected or blocked on public servers: No. 27–29 (yellow note).", "detected or blocked on public servers: No. 27–30 (yellow note)."),
              ("(No. 9, 50, 63, 64 and 74) also remove", "(No. 9, 51, 64, 65 and 75) also remove"),
              ("(No. 9, 63 and 64) make `Wow.exe` larger", "(No. 9, 64 and 65) make `Wow.exe` larger")]}
for fn, md, lang in (('README.de.md', 'PATCHES.de.md', 'de'), ('README.md', 'PATCHES.en.md', 'en')):
    s = rd(wt + '/docs/' + fn); assert '\r' not in s
    s = refs(s)
    s = re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(md), lambda m: '| [%d](%s#' % (mp(m.group(1)), md), s)
    row = re.search(r'(?m)^\| \[27\]\(%s#patch-wowoptimize\).*\n' % re.escape(md), rd(devwt + '/docs/' + fn)).group(0)
    assert '[BETA]' not in row
    m = re.search(r'(?m)^\| \[28\]\(%s#patch-awesome\)' % re.escape(md), s); assert m
    s = s[:m.start()] + row + s[m.start():]
    for x, y in LEG[lang]: s = once(s, refs(x), y, 'README ' + lang)
    wr(wt + '/docs/' + fn, s)

# ------------------------------------------------------------ PATCHES
for fn, lang in (('PATCHES.de.md', 'de'), ('PATCHES.en.md', 'en')):
    d = rd(devwt + '/docs/' + fn); a, b = section(d, 'wowoptimize'); sec = d[a:b]
    assert '[BETA]' not in sec and '**BETA**' not in sec
    if lang == 'de':
        sec = once(sec, "den DLL-Namen legt der Thread auf dem Stack ab. Der Patch verträgt sich mit dem\n"
                        "Lexara-Lader (Nr. 30) und dem voice.dll-Lader (Nr. 31).\n",
                        "den DLL-Namen legt der Thread auf dem Stack ab. Der Patch verträgt sich mit dem\n"
                        "Lexara-Lader (Nr. 30).\n", 'voice-Satz')
    else:
        sec = once(sec, "the stack. The patch works together with the Lexara loader (No. 30) and the\n"
                        "voice.dll loader (No. 31).\n",
                        "the stack. The patch works together with the Lexara loader (No. 30).\n", 'voice-Satz')
    s = rd(wt + '/docs/' + fn); assert '\r' not in s
    s = refs(s)
    i = s.index('<a id="patch-awesome"></a>')
    s = s[:i] + sec + s[i:]
    wr(wt + '/docs/' + fn, s)
print('wo_main OK')

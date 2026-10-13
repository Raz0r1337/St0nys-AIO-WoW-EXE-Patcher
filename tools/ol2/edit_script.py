# Outline mit Zusatzoptionen in apply_patches.ps1 (st0ny-dev): neues Add-Outline, Outline-Eintrag
# ungetestet, Nr. 69-72 als Optionen, Nummern ab 69 um 4 schieben.
# Aufruf: edit_script.py <apply_patches.ps1> <outline2_ps.txt>
import sys, re
path, gen = sys.argv[1], sys.argv[2]
raw = open(path, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
new = open(gen, encoding='ascii').read().rstrip('\n') + '\n'

def once(a, b):
    global s
    n = s.count(a); assert n == 1, (a[:80], n)
    s = s.replace(a, b)

# 0) Nummern ab 69 um 4 schieben - im alten Text, vor dem Einfuegen der neuen Eintraege
C = 69
ids0 = [re.match(r"^    @\{ Id = '([^']+)'", l).group(1) for l in s.split('\n') if re.match(r"^    @\{ Id = '", l)]
assert ids0[C - 2] == 'outline' and ids0[C - 1] == 'tracker', ids0[C - 2:C]
def sh(m):
    n = int(m.group(2)); return '%s %d' % (m.group(1), n + 4 if n >= C else n)
out = []
for l in s.split('\n'):
    nl = re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)', sh, l)
    if nl != l: print('  %s\n    -> %s' % (l.strip()[:110], nl.strip()[:110]))
    out.append(nl)
s = '\n'.join(out)

# 1) Add-Outline samt Kommentarkopf ersetzen
a = s.index('#  Umrandung fuer Ziel und Mouseover (St0ny)\n')
a = s.rindex('# ====', 0, a)
z = s.index('\n}\n', s.index('function Add-Outline {', a)) + 3
s = s[:a] + new + s[z:]

# 2) Outline-Eintrag: ungetestet, Hinweis auf die Optionen
once("""    @{ Id = 'outline'; Cat = 'graphics'; On = $false; GrowsExe = $true; PublicUntested = $true
       Author = 'St0ny'
       De = 'Umrandung fuer Ziel und Mouseover [BETA]'
       En = 'Outline for target and mouseover [BETA]'
       NoteDe = 'nur gxApi d3d9'
       NoteEn = 'gxApi d3d9 only'
       Code = {
        # Eigene Sektion (.outl), siehe Add-Outline.
        Add-Outline
    }}
""", """    @{ Id = 'outline'; Cat = 'graphics'; On = $false; GrowsExe = $true; PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Umrandung fuer Ziel und Mouseover [BETA]'
       En = 'Outline for target and mouseover [BETA]'
       NoteDe = 'nur gxApi d3d9'
       NoteEn = 'gxApi d3d9 only'
       Code = {
        # Eigene Sektion (.outl), siehe Add-Outline. Ohne die Zusatzoptionen
        # (Nr. 69-72) nur Ziel und Mouseover, nicht durch Waende.
        Add-Outline
    }}

    @{ Id = 'outlinewalls'; Cat = 'graphics'; On = $false; Needs = @('outline'); BanRisk = $true; PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Umrandung: auch durch Waende sichtbar [BETA]'
       En = 'Outline: visible through walls too [BETA]'
       Code = {
        # Schalter fuer Add-Outline: CC-Fuellbyte hinter einem ret (VA 0x6AB7DF)
        # wird 1. Der Rand erscheint dann auch dort, wo die Figur verdeckt ist.
        Assert-Bytes 0x2AABDF @(0xCC) 'Umrandung durch Waende'
        Patch 0x2AABDF @(0x01)
    }}

    @{ Id = 'outlineself'; Cat = 'graphics'; On = $false; Needs = @('outline'); PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Umrandung: eigener Charakter immer umrandet [BETA]'
       En = 'Outline: own character always outlined [BETA]'
       Code = {
        # Schalter fuer Add-Outline: CC-Fuellbyte hinter einem ret (VA 0x6ABAAF)
        # wird 1. Die eigene Figur bekommt dann immer einen Rand.
        Assert-Bytes 0x2AAEAF @(0xCC) 'Umrandung eigener Charakter'
        Patch 0x2AAEAF @(0x01)
    }}

    @{ Id = 'outlineparty'; Cat = 'graphics'; On = $false; Needs = @('outline'); PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Umrandung: eigene Gruppe immer umrandet [BETA]'
       En = 'Outline: own party always outlined [BETA]'
       NoteDe = 'nur 5er-Gruppe'
       NoteEn = 'party of 5 only'
       Code = {
        # Schalter fuer Add-Outline: CC-Fuellbyte hinter einem ret (VA 0x6ABE2F)
        # wird 1. Die bis zu 4 Mitspieler der Gruppe (GUIDs ab 0xBD1948) bekommen
        # dann immer einen Rand.
        Assert-Bytes 0x2AB22F @(0xCC) 'Umrandung Gruppe'
        Patch 0x2AB22F @(0x01)
    }}

    @{ Id = 'outlinereact'; Cat = 'graphics'; On = $false; Needs = @('outline'); PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Umrandung: Gesinnungsfarbe statt Klassenfarbe [BETA]'
       En = 'Outline: reaction color instead of class color [BETA]'
       NoteDe = 'fuer Nr. 70 und 71'
       NoteEn = 'for No. 70 and 71'
       Code = {
        # Schalter fuer Add-Outline: CC-Fuellbyte hinter einem ret (VA 0x6ABE5F)
        # wird 1. Eigener Charakter und Gruppe bekommen dann die Farbe des
        # Auswahlkreises statt ihrer Klassenfarbe.
        Assert-Bytes 0x2AB25F @(0xCC) 'Umrandung Gesinnungsfarbe'
        Patch 0x2AB25F @(0x01)
    }}
""")

ids = [re.match(r"^    @\{ Id = '([^']+)'", l).group(1) for l in s.split('\n') if re.match(r"^    @\{ Id = '", l)]
assert ids.index('outlinewalls') + 1 == 69 and ids[67] == 'outline' and ids[72] == 'tracker' and len(ids) == 94, len(ids)
open(path, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok, Patches:', len(ids))

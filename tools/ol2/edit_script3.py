# Outline mit Zusatzoptionen in apply_patches.ps1 (st0ny-dev): neues Add-Outline, Outline-Eintrag
# ungetestet, Nr. 69-74 als Optionen, Nummern ab 69 um 6 schieben.
# Aufruf: edit_script3.py <apply_patches.ps1> <outline3_ps.txt>
import sys, re
path, gen = sys.argv[1], sys.argv[2]
raw = open(path, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
new = open(gen, encoding='ascii').read().rstrip('\n') + '\n'

def once(a, b):
    global s
    n = s.count(a); assert n == 1, (a[:80], n)
    s = s.replace(a, b)

# 0) Nummern ab 69 um 6 schieben - im alten Text, vor dem Einfuegen der neuen Eintraege
C = 69
ids0 = [re.match(r"^    @\{ Id = '([^']+)'", l).group(1) for l in s.split('\n') if re.match(r"^    @\{ Id = '", l)]
assert ids0[C - 2] == 'outline' and ids0[C - 1] == 'tracker', ids0[C - 2:C]
def sh(m):
    n = int(m.group(2)); return '%s %d' % (m.group(1), n + 6 if n >= C else n)
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
        # (Nr. 69-74) nur Ziel und Mouseover, nicht durch Waende.
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

    @{ Id = 'outlineraid'; Cat = 'graphics'; On = $false; Needs = @('outline'); PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Umrandung: ganzer Schlachtzug immer umrandet [BETA]'
       En = 'Outline: whole raid always outlined [BETA]'
       NoteDe = 'kostet im Schlachtzug viele FPS'
       NoteEn = 'costs a lot of FPS in raids'
       Code = {
        # Schalter fuer Add-Outline: CC-Fuellbyte hinter einem ret (VA 0x6ABE8F)
        # wird 1. Alle Mitglieder des Schlachtzugs (Zeiger ab 0xBEB568, Anzahl
        # 0xBEB608) und der Gruppe bekommen dann immer einen Rand.
        Assert-Bytes 0x2AB28F @(0xCC) 'Umrandung Schlachtzug'
        Patch 0x2AB28F @(0x01)
    }}

    @{ Id = 'outlinehidden'; Cat = 'graphics'; On = $false; Needs = @('outline'); PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Umrandung: eigener Charakter nur dort, wo er verdeckt ist [BETA]'
       En = 'Outline: own character only where it is hidden [BETA]'
       Code = {
        # Schalter fuer Add-Outline: CC-Fuellbyte hinter einem ret (VA 0x6ABF3F)
        # wird 1. Die eigene Figur bekommt dann nur dort einen Rand, wo vorher
        # Gezeichnetes (Gebaeude, Gelaende) vor ihr liegt.
        Assert-Bytes 0x2AB33F @(0xCC) 'Umrandung nur verdeckt'
        Patch 0x2AB33F @(0x01)
    }}

    @{ Id = 'outlinereact'; Cat = 'graphics'; On = $false; Needs = @('outline'); PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Umrandung: Gesinnungsfarbe statt Klassenfarbe [BETA]'
       En = 'Outline: reaction color instead of class color [BETA]'
       NoteDe = 'fuer alle Raender von Spielern'
       NoteEn = 'for all outlines of players'
       Code = {
        # Schalter fuer Add-Outline: CC-Fuellbyte hinter einem ret (VA 0x6ABE5F)
        # wird 1. Alle Raender bekommen dann die Farbe des Auswahlkreises, auch
        # bei Spielern (sonst Klassenfarbe).
        Assert-Bytes 0x2AB25F @(0xCC) 'Umrandung Gesinnungsfarbe'
        Patch 0x2AB25F @(0x01)
    }}
""")

ids = [re.match(r"^    @\{ Id = '([^']+)'", l).group(1) for l in s.split('\n') if re.match(r"^    @\{ Id = '", l)]
assert ids[68:74] == ['outlinewalls', 'outlineself', 'outlineparty', 'outlineraid', 'outlinehidden', 'outlinereact'] and ids[67] == 'outline' and ids[74] == 'tracker' and len(ids) == 96, len(ids)
open(path, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok, Patches:', len(ids))

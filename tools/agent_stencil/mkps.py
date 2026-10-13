# Derives mkoutline10_fix.py (this directory) from ol2/mkoutline10.py for outline10_fix.py: second hook site
# DrawPrimitive VA 0x6A3706 (same 9-byte shape as the DIP site), doc bullets for the U-bit stencil values.
# Running it writes outline10_fix_ps.txt into this directory (the Add-Outline PowerShell function).
# ol2/mkoutline10.py is only read. usage: python3 -B mkps.py && python3 -B mkoutline10_fix.py
import os, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'ol2', 'mkoutline10.py')
s = open(SRC).read(); orig = s
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)
rep("from outline10 import *", "from outline10_fix import *")
rep("'outline10_ps.txt'", "'outline10_fix_ps.txt'")
rep('''#    Index + 1 ist ihr Stencil-Wert (Rand), die Figur selbst bekommt 0x80.''',
    '''#    Index + 1 ist ihre Kategorie, Stencil-Wert des Rands 0x40 + Kategorie,
#    die Figur selbst bekommt 0xC0 (0x80 Figur, 0x40 = sichtbar).''')
rep('''#  - DrawIndexedPrimitive (VA 0x6A36C8): bei gesetztem CUR zeichnet das echte
#    Teil Stencil 0x80 (Figur).''', '''#  - DrawIndexedPrimitive (VA 0x6A36C8): bei gesetztem CUR zeichnet das echte
#    Teil Stencil 0xC0 (Figur).''')
rep('''#    schreiben CUR nur dort, wo noch keine Figur ist (Rand).
#  - Alles, was danach noch gezeichnet wird und Tiefe schreibt, setzt den
#    Stencil dort auf 0, wo es vor der Figur bzw. ihrem Rand liegt - so
#    verdeckt es den Rand. Durchsichtiges (Wasser, Effekte) schreibt keine
#    Tiefe und laesst den Rand stehen.''', '''#    schreiben 0x40 + CUR nur dort, wo noch keine Figur ist (Rand).
#  - Alles, was danach noch gezeichnet wird und Tiefe schreibt (ueber
#    DrawIndexedPrimitive VA 0x6A36C8 oder DrawPrimitive VA 0x6A3706), wird
#    ganz normal gezeichnet und loescht dabei dort, wo es vor der Figur bzw.
#    ihrem Rand liegt, Figur- und Sichtbar-Bit (Stencil-Test ALWAYS, ZERO,
#    Schreibmaske 0xC0) - so verdeckt es den Rand. Durchsichtiges (Wasser,
#    Effekte) schreibt keine Tiefe und laesst den Rand stehen.''')
rep('''#  - Durch Waende: die Figur bekommt Stencil 0x80 auch dort, wo sie verdeckt''',
    '''#  - Durch Waende: die Figur bekommt Stencil 0xC0 auch dort, wo sie verdeckt''')
rep('''#    wie durch Waende, spaeter Gezeichnetes loescht dann nur Raender ueber
#    GRPN (Stencil-Test "kleiner" gegen WPROT, ZERO). Ohne Gruppen-Umrandung''',
    '''#    wie durch Waende; ihre Raender (Kategorie bis WPROT = GRPN) faerbt Post
#    mit Stencil-Maske 0x3F, also auch dort, wo spaeter Gezeichnetes davor
#    liegt und das Sichtbar-Bit geloescht hat. Ohne Gruppen-Umrandung''')
rep('''#  - Nur wo verdeckt (eigener Charakter bzw. Gruppe, s.o.): die Figur bekommt Stencil 0x80 auch''',
    '''#  - Nur wo verdeckt (eigener Charakter bzw. Gruppe, s.o.): die Figur bekommt Stencil 0xC0 auch''')
rep('''out.append("    $VPSITE = 0x6A9B10; $BATCH = 0x823A81; $DIPSITE = 0x6A36C8; $POSTSITE = 0x4F91E5")''',
    '''out.append("    $VPSITE = 0x6A9B10; $BATCH = 0x823A81; $DIPSITE = 0x6A36C8; $DPSITE = 0x6A3706; $POSTSITE = 0x4F91E5")''')
rep('''out.append("    Assert-Bytes ($DIPSITE - 0x400C00) @(0x8B, 0x88, 0x48, 0x01, 0x00, 0x00, 0x52, 0xFF, 0xD1) 'Umrandung'")''',
    '''out.append("    Assert-Bytes ($DIPSITE - 0x400C00) @(0x8B, 0x88, 0x48, 0x01, 0x00, 0x00, 0x52, 0xFF, 0xD1) 'Umrandung'")
out.append("    Assert-Bytes ($DPSITE - 0x400C00) @(0x8B, 0x88, 0x44, 0x01, 0x00, 0x00, 0x52, 0xFF, 0xD1) 'Umrandung'")''')
rep('''out.append("    Patch ($DIPSITE - 0x400C00) ([byte[]]([byte[]](0x52) + (Get-Rel32 @(0xE8) ($DIPSITE + 1) ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90)))" % L['dip'])''',
    '''out.append("    Patch ($DIPSITE - 0x400C00) ([byte[]]([byte[]](0x52) + (Get-Rel32 @(0xE8) ($DIPSITE + 1) ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90)))" % L['dip'])
out.append("    Patch ($DPSITE - 0x400C00) ([byte[]]([byte[]](0x52) + (Get-Rel32 @(0xE8) ($DPSITE + 1) ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90)))   # DrawPrimitive-Zweig" % L['dp'])''')
open(os.path.join(HERE, 'mkoutline10_fix.py'), 'w').write(s)
open(os.path.join(HERE, 'mkoutline10_fix.diff'), 'w').writelines(difflib.unified_diff(orig.splitlines(True), s.splitlines(True), 'ol2/mkoutline10.py', 'agent_stencil/mkoutline10_fix.py'))
print('wrote mkoutline10_fix.py')

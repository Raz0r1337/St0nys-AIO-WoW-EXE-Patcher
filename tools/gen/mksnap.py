import snap
from emitps import *
from mkfuncs import name
NAMES_EXTRA={}
body=emit(snap.tpl,0,snap.SRC,snap.absf,snap.relf)
import mkfuncs
mkfuncs.NAMES[0x6C0E86]='ParseEmbeddedTexture+6'
body=name(body)
L=snap.LAB
txt='''# ============================================================
#  Icons im Text pixelgenau (Hour of Twilight, ported by St0ny)
#  Texte koennen Icons enthalten (|T...|t, z.B. Raidmarker, Waehrungen,
#  Questsymbole). Ihre Groesse und Lage rechnet der Client in Pixeln mit
#  Nachkommastellen aus - bei skalierten Schriften landen die Icons dann
#  zwischen zwei Pixeln und werden unscharf oder um einen Pixel verzerrt.
#  Der Hook hinter ParseEmbeddedTexture (VA 0x6C0E80, cdecl: Text, Info,
#  Hoehe, Skalierung, Schrifthoehe) rundet - wenn das Parsen geklappt hat
#  und die Hoehe von der Schrifthoehe abweicht - Hoehe [Info+18h] und
#  Breite [Info+1Ch] auf ganze Pixel (mindestens 1) und den Versatz
#  [Info+20h] / [Info+24h] auf ganze Pixel. Gerundet wird wie im Fork mit
#  floor(x + 0,5): Rundungsmodus der FPU kurz auf "abrunden", danach wieder
#  zurueck. Eigene Sektion (.isnap), nur ausfuehrbar.
# ============================================================
function Add-IconPixelSnap {
    $PARSE = 0x6C0E80
    Assert-Bytes ($PARSE - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x44) 'Icons pixelgenau'
    $loc = Add-CodeSection '.isnap' 0x%X
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
'''%len(snap.tpl)
txt+='\n'.join(body)+'\n'
txt+='''    if ($c.Count -ne 0x%X) { throw 'Icons pixelgenau: Sektion hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    Patch ($PARSE - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $PARSE ($CAVE + 0x%X)) + [byte[]](0x90)))
}
'''%(len(snap.tpl),L['snap'])
txt=txt.replace('    # snap:\n','    # snap:  Original aufrufen (Argumente neu ablegen), danach runden\n').replace('    # tramp:\n','    # tramp: ueberschriebene Befehle, weiter im Original\n')
assert all(ord(ch)<128 for ch in txt)
open('snapfunc.ps1','w').write(txt)
print(txt[-900:])

# Erzeugt Add-Outline (mit Kommentarkopf) fuer apply_patches.ps1 -> ol2/outline6_ps.txt
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/gen')
from outline6 import *
from emitps import emit, hx
s = src(B1)
lines = emit(code, CODE_OFF, s, absf, relf, comment_src=src(B1, sym=True))
d = data()
head = r'''# ============================================================
#  Umrandung fuer Ziel und Mouseover (St0ny), mit Einstellungen
#  Wie in Retail bekommt die 3D-Figur des markierten Ziels und die unter dem
#  Mauszeiger eine duenne Umrandung. Nur fuer gxApi d3d9 mit 24-Bit-
#  Tiefenpuffer; sonst schaltet sich der Patch ab. Eigene beschreibbare
#  Sektion (.outl).
#  Einstellungen ($OUTLINE_OPTIONS, J/N-Fragen vor dem Patchen) setzen je ein
#  CC-Fuellbyte nach einem ret in .text auf 1, der Code liest sie zur
#  Laufzeit: 0x6AB7DF durch Waende, 0x6ABAAF eigener Charakter, 0x6ABE2F
#  5er-Gruppe (GUIDs ab 0xBD1948), 0x6ABE8F Schlachtzug (Zeiger ab 0xBEB568,
#  Anzahl 0xBEB608), 0x6ABF3F eigener Charakter nur wo verdeckt, 0x6ABE5F
#  Gesinnungs- statt Klassenfarbe. Standard: nur "eigener Charakter nur wo
#  verdeckt" an, sonst Ziel und Mouseover, nicht durch Waende.
#  - Pro Bild eine Tabelle der umrandeten Einheiten (bis 48): Schlachtzug,
#    Gruppe, eigener Charakter, Ziel, Mouseover - jede nur einmal. Ihr
#    Index + 1 ist ihr Stencil-Wert (Rand), die Figur selbst bekommt 0x80.
#    Spaeter Eingetragene gewinnen am gemeinsamen Rand (Ziel, Mouseover).
#  - Farbe: bei Spielern die Klassenfarbe ([[obj+0xD0]+0x45] wie UnitClass,
#    Spieler = ObjectPtr mit Typmaske 0x10 wie UnitIsPlayer, Tabelle mit den
#    Farben der Raid-Frames), sonst und mit der Einstellung Gesinnungsfarbe
#    die Farbe des Auswahlkreises (0x521BF0). Ist der Auswahlkreis eines
#    Spielers in Klassenfarbe rot (0xFFFF0000, feindlich), pulsiert sein Rand
#    sanft zwischen Klassenfarbe und Rot (GetTickCount, 1,5 s je Puls).
#  - Tiefenpuffer D24X8 -> D24S8 (Formattabelle 0xA2E4A8, Index 5), damit es
#    einen Stencil-Puffer gibt. Das Spiel selbst nutzt Stencil nie.
#  - SetViewport (VA 0x6A9B10): der zuletzt gesetzte Viewport wird gemerkt.
#  - M2-Batch (VA 0x823A81, nur Welt-Szene [0xCD754C]): gehoert das Modell
#    (oder sein Elternmodell, z.B. Waffe/Reittier) zu einer umrandeten
#    Einheit, wird CUR = ihr Stencil-Wert gesetzt.
#  - DrawIndexedPrimitive (VA 0x6A36C8): bei gesetztem CUR zeichnet das echte
#    Teil Stencil 0x80 (Figur). Ein zweiter Durchgang ohne Tiefentest zeichnet
#    das Teil nur auf den Randpixeln derselben Figur (Stencil = CUR), damit
#    Umhang, Waffe usw. nicht am Rand eines frueheren Teils haengen bleiben.
#    Danach 8 unsichtbare Kopien (keine Farbe, aber mit Tiefe), per
#    Projektionsmatrix (VS c2-c5) um 2 Pixel verschoben, mit Tiefentest: sie
#    schreiben CUR nur dort, wo noch keine Figur ist (Rand).
#  - Alles, was danach gezeichnet wird und Tiefe schreibt (z.B. Buesche,
#    Pilze, Gras), setzt den Stencil dort auf 0, wo es vor der Figur bzw.
#    ihrem Rand liegt - so verdeckt es den Rand. Durchsichtiges (Wasser,
#    Effekte) schreibt keine Tiefe und laesst den Rand stehen.
#  - Durch Waende: die Figur bekommt Stencil 0x80 auch dort, wo sie verdeckt
#    ist, die Kopien laufen ohne Tiefentest und ohne Tiefe, der zweite
#    Durchgang und das Verdecken durch spaeter Gezeichnetes entfallen.
#  - Nur wo verdeckt (eigener Charakter): die Figur bekommt Stencil 0x80 auch
#    dort, wo sie verdeckt ist. Die Kopien laufen ohne Tiefe mit Tiefentest
#    "groesser" (bei nicht bestandenem Test bleibt der Stencil) und markieren
#    den Rand nur dort, wo vorher Gezeichnetes deutlich vor ihnen liegt: Ihre
#    Tiefe wird per Projektionsmatrix (VS c4 + KZ * c5) um 0,001 * Entfernung^2
#    Yards nach vorn gezogen, KZ aus c4/c5 berechnet - sonst laege am Boden
#    direkt unter den Fuessen eine Linie. Was erst nach der Figur gezeichnet
#    wird, erkennt das nicht.
#  - Vor den Auswahlkreisen (VA 0x4F91E5): je umrandeter Einheit ein
#    bildschirmfuellendes Viereck in ihrer Farbe nur auf ihrem Stencil-Wert
#    (pulsierend: Klassenfarbe und Rot gemischt, Anteil Rot (1 - cos)/2),
#    dann Stencil leeren und alle Render-States des Spiels neu senden lassen.
# ============================================================'''
out = head.split('\n')
out.append("function Add-Outline {")
out.append("    $VPSITE = 0x6A9B10; $BATCH = 0x823A81; $DIPSITE = 0x6A36C8; $POSTSITE = 0x4F91E5")
out.append("    Assert-Bytes ($VPSITE - 0x400C00) @(0x8B, 0x86, 0x7C, 0x39, 0x00, 0x00) 'Umrandung'")
out.append("    Assert-Bytes ($BATCH - 0x400C00) @(0x8B, 0xCE, 0xE8, 0x28, 0xC9, 0xFF, 0xFF) 'Umrandung'")
out.append("    Assert-Bytes ($DIPSITE - 0x400C00) @(0x8B, 0x88, 0x48, 0x01, 0x00, 0x00, 0x52, 0xFF, 0xD1) 'Umrandung'")
out.append("    Assert-Bytes ($POSTSITE - 0x400C00) @(0xE8, 0xA6, 0xDD, 0xFF, 0xFF) 'Umrandung'")
out.append("    Assert-Bytes 0x62CCBC @(0x4D) 'Umrandung'")
out.append("    $loc = Add-CodeSection '.outl' 0x%X -Writable" % len(TPL))
out.append("    $CAVE = $loc[0]")
out.append("    $c = New-Object System.Collections.Generic.List[byte]")
out.append("    for ($i = 0; $i -lt 0x%X; $i++) { $c.Add([byte]0) }                 # Daten, beginnen bei 0" % CODE_OFF)
blocks = [(DO['TWO'], 12, 'Konstanten 2.0, -2.0, 0.5'),
          (DO['VERTS'], 80, 'Viereck (4 Ecken: x, y, z=0, rhw=1, Farbe)'),
          (DO['OFFS'], 64, 'Versatz der 8 unsichtbaren Kopien in Pixeln (x, y)'),
          (DO['PSCODE'], 20, 'Pixelshader ps_1_1: mov r0, v0'),
          (DO['CLS'], 48, 'Klassenfarben (Index = Klassen-Id): Krieger, Paladin, Jaeger, Schurke, Priester, Todesritter, Schamane, Magier, Hexenmeister, Druide'),
          (DO['KAP'], 4, 'Nur wo verdeckt: Abstand in Yards = 0.001 * Entfernung^2'),
          (DO['K128'], 8, 'Puls: Konstanten 128.0 und 2*Pi/1500 ms')]
for st, n, nm in blocks:
    out.append("    # %s" % nm)
    out.append("    $i = 0x%X; foreach ($b in [byte[]]@(%s)) { $c[$i] = $b; $i++ }" % (st, hx(d[st:st + n])))
assert all(d[k] == 0 for k in range(len(d)) if not any(st <= k < st + n for st, n, _ in blocks))
out += lines
out.append("    if ($c.Count -ne 0x%X) { throw 'Umrandung: Sektion hat die falsche Groesse.' }" % len(TPL))
out.append("    Patch $loc[1] $c.ToArray()")
L = LAB
out.append("    Patch ($VPSITE - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $VPSITE ($CAVE + 0x%X)) + [byte[]](0x90)))" % L['vpcap'])
out.append("    Patch ($BATCH - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $BATCH ($CAVE + 0x%X)) + [byte[]](0x90, 0x90)))" % L['batch'])
out.append("    Patch ($DIPSITE - 0x400C00) ([byte[]]([byte[]](0x52) + (Get-Rel32 @(0xE8) ($DIPSITE + 1) ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90)))" % L['dip'])
out.append("    Patch ($POSTSITE - 0x400C00) (Get-Rel32 @(0xE8) $POSTSITE ($CAVE + 0x%X))" % L['post'])
out.append("    Patch 0x62CCBC @(0x4B)                                     # Tiefenpuffer D24X8 -> D24S8 (mit Stencil)")
out.append("}")
F = FLAGS
opts = r'''
# Einstellungen der Umrandung: J/N-Fragen vor dem Patchen (Questions). Der Wert
# sind die eingeschalteten Punkte durch Komma getrennt (z.B. "self,party")
# oder "none". Jeder Punkt ist ein CC-Fuellbyte hinter einem ret in .text
# (Va), 1 = an.
$OUTLINE_OPTIONS = @(
    @{ Key = 'walls'; Va = 0x%X; BanRisk = $true
       De = 'Durch Waende sichtbar? (unsicher, Bann-Gefahr)'; En = 'Visible through walls? (unsafe, ban risk)'
       ShortDe = 'durch Waende'; ShortEn = 'through walls' }
    @{ Key = 'hidden'; Va = 0x%X
       De = 'Eigener Charakter nur dort umrandet, wo er verdeckt ist?'; En = 'Own character outlined only where it is hidden?'
       ShortDe = 'eigener Charakter nur verdeckt'; ShortEn = 'own character only hidden' }
    @{ Key = 'self'; Va = 0x%X
       De = 'Eigener Charakter immer umrandet?'; En = 'Own character always outlined?'
       ShortDe = 'eigener Charakter'; ShortEn = 'own character' }
    @{ Key = 'party'; Va = 0x%X
       De = 'Eigene 5er-Gruppe immer umrandet?'; En = 'Own party of 5 always outlined?'
       ShortDe = '5er-Gruppe'; ShortEn = 'party' }
    @{ Key = 'raid'; Va = 0x%X
       De = 'Ganzer Schlachtzug immer umrandet? (kostet viele FPS)'; En = 'Whole raid always outlined? (costs a lot of FPS)'
       ShortDe = 'Schlachtzug'; ShortEn = 'raid' }
    @{ Key = 'react'; Va = 0x%X
       De = 'Gesinnungsfarbe statt Klassenfarbe?'; En = 'Reaction color instead of class color?'
       ShortDe = 'Gesinnungsfarbe'; ShortEn = 'reaction color' }
)

function Set-OutlineOptions([string]$v) {
    $on = Get-OptionKeys $OUTLINE_OPTIONS $v
    foreach ($o in $OUTLINE_OPTIONS) {
        $off = $o.Va - 0x400C00
        Assert-Bytes $off @(0xCC) 'Umrandung'
        # Auch ein ausgeschalteter Punkt wird (unveraendert) geschrieben, damit
        # die Stelle in der Original-Byte-Tabelle landet.
        if ($on -contains $o.Key) { Patch $off @(0x01) } else { Patch $off @(0xCC) }
    }
}

function Get-OutlineOptionsFromExe {
    $on = @()
    foreach ($o in $OUTLINE_OPTIONS) {
        $b = $script:f[$o.Va - 0x400C00]
        if ($b -eq 1) { $on += $o.Key } elseif ($b -ne 0xCC) { return $null }
    }
    return (ConvertTo-OptionValue $OUTLINE_OPTIONS $on)
}''' % (F['FWALLS'], F['FHIDDEN'], F['FSELF'], F['FPARTY'], F['FRAID'], F['FREACT'])
out += opts.split('\n')
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outline6_ps.txt'), 'w').write('\n'.join(out) + '\n')
print(len(out), 'Zeilen')

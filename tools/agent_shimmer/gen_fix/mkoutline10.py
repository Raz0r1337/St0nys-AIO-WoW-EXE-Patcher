# Erzeugt Add-Outline (mit Kommentarkopf) fuer apply_patches.ps1 -> ol2/outline10_ps.txt
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/gen')
from outline10 import *
from emitps import emit, hx
s = src(B1)
lines = emit(code, CODE_OFF, s, absf, relf, comment_src=src(B1, sym=True))
d = data()
head = r'''# ============================================================
#  Umrandung fuer Ziel und Mouseover (St0ny), mit Einstellungen
#  Wie in Retail bekommt die 3D-Figur des markierten Ziels und die unter dem
#  Mauszeiger eine Umrandung mit weichem Schein: direkt an der Figur hell,
#  nach aussen auslaufend. Nur fuer gxApi d3d9 mit 24-Bit-
#  Tiefenpuffer; sonst schaltet sich der Patch ab. Eigene beschreibbare
#  Sektion (.outl).
#  Einstellungen ($OUTLINE_OPTIONS, Umschalter vor dem Patchen) setzen je ein
#  CC-Fuellbyte nach einem ret in .text auf 1 ($OUTLINE_FLAGS), der Code liest
#  sie zur Laufzeit: 0x6AB7DF durch Waende, 0x6AC02F durch Waende nur Gruppe/
#  Schlachtzug, 0x6ABAAF eigener Charakter, 0x6ABF3F eigener Charakter nur wo
#  verdeckt, 0x6ABE2F 5er-Gruppe (GUIDs ab 0xBD1948), 0x6ABE8F Schlachtzug
#  (Zeiger ab 0xBEB568, Anzahl 0xBEB608), 0x6ABE5F Gesinnungs- statt
#  Klassenfarbe. Standard: nur "eigener Charakter nur wo verdeckt" an, sonst
#  Ziel und Mouseover, nicht durch Waende.
#  - Pro Bild eine Tabelle der umrandeten Einheiten (bis 48): Schlachtzug,
#    Gruppe, eigener Charakter, Ziel, Mouseover - jede nur einmal. Ihr
#    Index + 1 ist ihre Kategorie, Stencil-Wert des Rands 0x40 + Kategorie,
#    die Figur selbst bekommt 0xC0 (0x80 Figur, 0x40 = sichtbar).
#    Spaeter Eingetragene gewinnen am gemeinsamen Rand (Ziel, Mouseover).
#    Schlachtzug-Mitglieder ausserhalb der eigenen 5er-Gruppe (THIN) bekommen
#    nur die duenne Linie ohne Schein.
#  - Begleiter: Nach Gruppe und Schlachtzug laeuft die Objektliste des Spiels
#    durch (Objektmanager 0x4D3730, erstes Objekt [mgr+0xAC], naechstes
#    [obj+[mgr+0xA4]+4]). Einheiten, die keine Spieler sind und deren
#    CHARMEDBY, SUMMONEDBY oder CREATEDBY (Deskriptor +0x30/+0x38/+0x40) ein
#    Gruppen-Eintrag ist, kommen mit Farbe und THIN ihres Besitzers in die
#    Tabelle (zaehlen zur Gruppe, PETF 1). Ist der eigene Charakter "nur wo
#    verdeckt" umrandet, kommen am Ende auch die eigenen Begleiter und die von
#    Gruppe/Schlachtzug, die noch fehlen, in die Tabelle - nur fuer die
#    Sortierung, ohne Umrandung (PETF 2). Platz bleibt fuer ich, Ziel,
#    Mouseover (Begleiter bis Eintrag 45).
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
#  - Reihenfolge der undurchsichtigen M2-Teile (Pass 0, nur Welt-Szene): Das
#    Spiel sortiert sie nach Modell, Shader und Textur, nicht nach Entfernung
#    (VA 0x822FDD), und zeichnet gebuendelte Doodads (M2BatchDoodads) erst
#    danach (VA 0x823D3B). Teile umrandeter Einheiten bekommen fuer die
#    Sortierung kurz den Typ 0x10 (Begleiter 0x11, also nach allen anderen
#    umrandeten Teilen - so loest ein Begleiter vor dir oder der Gruppe "nur
#    wo verdeckt" nicht aus) und landen so am Ende, untereinander in der
#    Reihenfolge des Spiels (0x81EAD0); danach wieder Typ 0. Beim Zeichnen
#    (VA 0x823D1F) bleiben diese NMARK Teile zuerst weg und kommen erst nach
#    den gebuendelten Doodads. So liegen alle anderen Figuren und Objekte
#    (Laternen, Briefkaesten usw.) schon im Tiefenpuffer, wenn die umrandeten
#    gezeichnet werden.
#  - DrawIndexedPrimitive (VA 0x6A36C8): bei gesetztem CUR zeichnet das echte
#    Teil Stencil 0xC0 (Figur). Ein zweiter Durchgang ohne Tiefentest zeichnet
#    das Teil nur auf den Randpixeln derselben Figur (Stencil 0x40 + CUR), damit
#    Umhang, Waffe usw. nicht am Rand eines frueheren Teils haengen bleiben.
#    Danach 8 unsichtbare Kopien (keine Farbe, aber mit Tiefe), per
#    Projektionsmatrix (VS c2-c5) um 2 Pixel verschoben, mit Tiefentest: sie
#    schreiben 0x40 + CUR nur dort, wo noch keine Figur ist (Rand).
#  - Alles, was danach noch gezeichnet wird und Tiefe schreibt (ueber
#    DrawIndexedPrimitive VA 0x6A36C8 oder DrawPrimitive VA 0x6A3706), wird
#    ganz normal gezeichnet und loescht dabei dort, wo es vor der Figur bzw.
#    ihrem Rand liegt, Figur- und Sichtbar-Bit (Stencil-Test ALWAYS, ZERO,
#    Schreibmaske 0xC0) - so verdeckt es den Rand. Durchsichtiges (Wasser,
#    Effekte) schreibt keine Tiefe und laesst den Rand stehen.
#  - Durch Waende: die Figur bekommt Stencil 0xC0 auch dort, wo sie verdeckt
#    ist, die Kopien laufen ohne Tiefentest und ohne Tiefe, der zweite
#    Durchgang und das Verdecken durch spaeter Gezeichnetes entfallen.
#  - Durch Waende nur Gruppe/Schlachtzug: Gruppe und Schlachtzug stehen zuerst
#    in der Tabelle (Kategorien 1 bis GRPN). Mit Gruppen-Umrandung laufen sie
#    wie durch Waende; ihre Raender (Kategorie bis WPROT = GRPN) faerbt Post
#    mit Stencil-Maske 0x3F, also auch dort, wo spaeter Gezeichnetes davor
#    liegt und das Sichtbar-Bit geloescht hat. Ohne Gruppen-Umrandung
#    kommen Gruppe und Schlachtzug trotzdem in die Tabelle und werden wie der
#    eigene Charakter nur wo verdeckt umrandet (GMODE 2).
#  - Aussortierte Figuren (VA 0x7934C6 in 0x793450): Was das Spiel nicht
#    zeichnet, weil es in einem anderen Gebaeude oder zu weit weg ist, laeuft
#    hier durch. Ist es eine Einheit der Gruppe (Kategorie bis GRPN, mit GMODE
#    1 oder 2; durch Waende alle: jede Einheit der Tabelle) und liegt im
#    Sichtkegel (0x983D20), wird es wie im sichtbaren Zweig von 0x793060
#    trotzdem in die Liste der sichtbaren Objekte (0xCDB098) gehaengt.
#  - Nur wo verdeckt (eigener Charakter bzw. Gruppe, s.o.): die Figur bekommt Stencil 0xC0 auch
#    dort, wo sie verdeckt ist. Die Kopien laufen ohne Tiefe mit Tiefentest
#    "groesser" (bei nicht bestandenem Test bleibt der Stencil) und markieren
#    den Rand nur dort, wo vorher Gezeichnetes deutlich vor ihnen liegt: Ihre
#    Tiefe wird per Projektionsmatrix (VS c4 + KZ * c5) um 0,001 * Entfernung^2
#    Yards nach vorn gezogen, KZ aus c4/c5 berechnet - sonst laege am Boden
#    direkt unter den Fuessen eine Linie. Was erst nach den umrandeten Figuren
#    gezeichnet wird, erkennt das nicht.
#  - Vor den Auswahlkreisen (VA 0x4F91E5): je umrandeter Einheit ein
#    bildschirmfuellendes Viereck in ihrer Farbe nur auf ihrem Stencil-Wert
#    (pulsierend: Klassenfarbe und Rot gemischt, Anteil Rot (1 - cos)/2),
#    dann Stencil leeren. Das Spiel sendet danach seine Zustaende neu: alle
#    GxStates als geaendert markiert (0x685A70), in seinem Zustands-Cache
#    [Geraet+0x3BC4] nur die geaenderten Eintraege ungueltig (0xFFFFFFFF) -
#    fuer andere wie D3DRS_AMBIENT ist 0xFFFFFFFF ein echter Wert.
#  - Weicher Schein (vor diesen Vierecken, nur Einheiten ohne THIN): die
#    Vierecke in voller Deckkraft zuerst in eine eigene Render-Textur (MSRT,
#    Groesse und Kantenglaettung wie das aktuelle Render-Target 0, gleicher
#    Tiefen-/Stencil-Puffer), aufloesen in TEX0 (StretchRect), mit einem
#    4x4-Zelt verkleinern nach TEX1 (halbe Aufloesung, 4 bilineare Abgriffe
#    bei +-0.75 Texeln), mit einem ps_2_0-Weichzeichner (5 bilineare Abgriffe,
#    Gauss) waagrecht nach TEX2, senkrecht zurueck nach TEX1 - dabei gleich
#    die Kurve 1-(1-y)^2 mit y = 2.5 * Wert (gesaettigt), so bleiben in TEX1
#    volle 8 Bit fuer die Deckkraft (ruhiger bei kleinen Bewegungen).
#    Dann ueber den Viewport eingeblendet (vormultipliziertes Alpha, Faktor 1,
#    nur RGB), nur wo keine Figur ist (Stencil kleiner 0x80). Die
#    TEXTURETRANSFORMFLAGS der Stufen 0-4 (fuer die 5 Texturkoordinaten auf 0)
#    kommen danach wieder auf den Wert aus dem Zustands-Cache; ist der
#    unbekannt, wird die Texturmatrix der Stufe beim Spiel als geaendert
#    markiert ([Geraet+0x100C+0x118*Stufe]), dann setzt es sie neu. Die duennen
#    Linien der Einheiten mit Schein werden danach aufgehellt gezeichnet
#    (Farbe * 5/8 + 0x5E je Kanal). Render-Target, Tiefenpuffer und Viewport
#    werden wiederhergestellt, Viewport und Scissor zusaetzlich beim Spiel
#    als geaendert markiert ([Geraet+0xF6C], [Geraet+0x2534]).
#  - Die Texturen liegen im Grafikspeicher (D3DPOOL_DEFAULT) und muessen vor
#    IDirect3DDevice9::Reset freigegeben werden: die drei Aufrufe von 0x690150
#    (Formatwechsel VA 0x69029D, verlorenes Geraet VA 0x6A337F, Abbau VA
#    0x69040B) gehen zuerst durch glrel (beim Abbau auch die Pixelshader).
#    Schlaegt etwas fehl (z.B. zu wenig Grafikspeicher), gibt es fuer dieses
#    Geraet nur die duennen Linien.
# ============================================================'''
out = head.split('\n')
out.append("function Add-Outline {")
out.append("    $VPSITE = 0x6A9B10; $BATCH = 0x823A81; $DIPSITE = 0x6A36C8; $DPSITE = 0x6A3706; $POSTSITE = 0x4F91E5")
out.append("    $SORTSITE = 0x822FDD; $DRAW1 = 0x823D1F; $DRAW2 = 0x823D3B; $CULLSITE = 0x%X" % CULLSITE)
out.append("    Assert-Bytes ($VPSITE - 0x400C00) @(0x8B, 0x86, 0x7C, 0x39, 0x00, 0x00) 'Umrandung'")
out.append("    Assert-Bytes ($BATCH - 0x400C00) @(0x8B, 0xCE, 0xE8, 0x28, 0xC9, 0xFF, 0xFF) 'Umrandung'")
out.append("    Assert-Bytes ($DIPSITE - 0x400C00) @(0x8B, 0x88, 0x48, 0x01, 0x00, 0x00, 0x52, 0xFF, 0xD1) 'Umrandung'")
out.append("    Assert-Bytes ($DPSITE - 0x400C00) @(0x8B, 0x88, 0x44, 0x01, 0x00, 0x00, 0x52, 0xFF, 0xD1) 'Umrandung'")
out.append("    Assert-Bytes ($POSTSITE - 0x400C00) @(0xE8, 0xA6, 0xDD, 0xFF, 0xFF) 'Umrandung'")
out.append("    Assert-Bytes ($SORTSITE - 0x400C00) @(0xE8, 0x0E, 0xAD, 0x01, 0x00) 'Umrandung'")
out.append("    Assert-Bytes ($DRAW1 - 0x400C00) @(0xE8, 0x0C, 0xF4, 0xFF, 0xFF) 'Umrandung'")
out.append("    Assert-Bytes ($DRAW2 - 0x400C00) @(0xE8, 0xF0, 0xF3, 0xFF, 0xFF) 'Umrandung'")
out.append("    Assert-Bytes ($CULLSITE - 0x400C00) @(0x8B, 0x4B, 0x34, 0x33, 0xD2) 'Umrandung'")
for k, va in enumerate(RESETSITES):
    rel = struct.pack('<i', X['RESETFN'] - (va + 5))
    out.append("    Assert-Bytes (0x%X - 0x400C00) @(0xE8, %s) 'Umrandung'" % (va, ', '.join('0x%02X' % x for x in rel)))
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
          (DO['K128'], 8, 'Puls: Konstanten 128.0 und 2*Pi/1500 ms'),
          (DO['O1'], 8, 'Schein: Abstand der Abgriffe 1.3846 und 3.2308 Texel'),
          (DO['GPSCODE'], len(psasm.blur_ps(*BLUR_W)), 'Schein: Pixelshader ps_2_0 Weichzeichner (Gewichte 0.2270, 0.3162, 0.0703)'),
          (DO['CPSCODE'], len(psasm.comp_ps(GLOW_GAIN)), 'Schein: Pixelshader ps_2_0 Einblenden (mul_sat mal %g)' % GLOW_GAIN),
          (DO['TQ'], 4, 'Schein: 0.75 / 1.3846 (Zelt-Abgriffe +-0.75 Texel ueber mkq)'),
          (DO['TPSCODE'], len(psasm.tent_ps()), 'Schein: Pixelshader ps_2_0 Verkleinern mit 4x4-Zelt (4 bilineare Abgriffe)'),
          (DO['VPSCODE'], len(psasm.blur_soft_ps(*BLUR_W, GLOW_K)), 'Schein: Pixelshader ps_2_0 senkrecht weichzeichnen + Kurve 1-(1-sat(%g*x))^2' % GLOW_K)]
for st, n, nm in blocks:
    out.append("    # %s" % nm)
    out.append("    $i = 0x%X; foreach ($b in [byte[]]@(%s)) { $c[$i] = $b; $i++ }" % (st, hx(d[st:st + n])))
out.append("    # Schein: Viereck mit 5 Texturkoordinaten (4 Ecken je 56 Bytes: x, y, z=0, rhw=1, 5 x (u, v)), hier rhw = 1.0")
out.append("    foreach ($k in 0..3) { $i = 0x%X + 56 * $k; foreach ($b in [byte[]]@(%s)) { $c[$i] = $b; $i++ } }" % (DO['VERTT'] + 12, hx(d[DO['VERTT'] + 12:DO['VERTT'] + 16])))
blocks += [(DO['VERTT'] + 56 * k + 12, 4, '') for k in range(4)]
assert all(d[k] == 0 for k in range(len(d)) if not any(st <= k < st + n for st, n, _ in blocks))
out += lines
out.append("    if ($c.Count -ne 0x%X) { throw 'Umrandung: Sektion hat die falsche Groesse.' }" % len(TPL))
out.append("    Patch $loc[1] $c.ToArray()")
L = LAB
out.append("    Patch ($VPSITE - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $VPSITE ($CAVE + 0x%X)) + [byte[]](0x90)))" % L['vpcap'])
out.append("    Patch ($BATCH - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $BATCH ($CAVE + 0x%X)) + [byte[]](0x90, 0x90)))" % L['batch'])
out.append("    Patch ($DIPSITE - 0x400C00) ([byte[]]([byte[]](0x52) + (Get-Rel32 @(0xE8) ($DIPSITE + 1) ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90)))" % L['dip'])
out.append("    Patch ($DPSITE - 0x400C00) ([byte[]]([byte[]](0x52) + (Get-Rel32 @(0xE8) ($DPSITE + 1) ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90)))   # DrawPrimitive-Zweig" % L['dp'])
out.append("    Patch ($POSTSITE - 0x400C00) (Get-Rel32 @(0xE8) $POSTSITE ($CAVE + 0x%X))" % L['post'])
out.append("    Patch ($SORTSITE - 0x400C00) (Get-Rel32 @(0xE8) $SORTSITE ($CAVE + 0x%X))" % L['sortp'])
out.append("    Patch ($DRAW1 - 0x400C00) (Get-Rel32 @(0xE8) $DRAW1 ($CAVE + 0x%X))" % L['draw1'])
out.append("    Patch ($DRAW2 - 0x400C00) (Get-Rel32 @(0xE8) $DRAW2 ($CAVE + 0x%X))" % L['draw2'])
out.append("    Patch ($CULLSITE - 0x400C00) (Get-Rel32 @(0xE9) $CULLSITE ($CAVE + 0x%X))   # aussortierte Gruppen-Figuren trotzdem zeichnen" % L['cull'])
for va in RESETSITES:
    out.append("    Patch (0x%X - 0x400C00) (Get-Rel32 @(0xE8) 0x%X ($CAVE + 0x%X))   # vor Reset/Abbau: Texturen des Scheins freigeben" % (va, va, L['glrel']))
out.append("    Patch 0x62CCBC @(0x4B)                                     # Tiefenpuffer D24X8 -> D24S8 (mit Stencil)")
out.append("}")
F = FLAGS
opts = r'''
# Einstellungen der Umrandung: Umschalter vor dem Patchen (Questions), je Punkt
# eine Zahl. Jede Wahl schaltet bestimmte Schalter (Keys) ein; die erste Wahl
# eines Punkts ist immer "aus". Der Wert sind die eingeschalteten Keys durch
# Komma getrennt (z.B. "hidden,party") oder "none". Jeder Key ist ein
# CC-Fuellbyte hinter einem ret in .text ($OUTLINE_FLAGS), 1 = an. Passen
# mehrere Wahlen eines Punkts (aeltere Werte), gilt die mit der hoechsten
# Prio - so wie im Code der Umrandung.
$OUTLINE_FLAGS = [ordered]@{ walls = 0x%X; wallsgroup = 0x%X; self = 0x%X; hidden = 0x%X
    party = 0x%X; raid = 0x%X; react = 0x%X }
$OUTLINE_OPTIONS = @(
    @{ De = 'Eigener Charakter'; En = 'Own character'
       Choices = @(
        @{ Keys = @(); De = 'aus'; En = 'off' }
        @{ Keys = @('hidden'); Prio = 2; De = 'nur wo verdeckt'; En = 'only where hidden'
           ShortDe = 'eigener Charakter nur verdeckt'; ShortEn = 'own character only hidden' }
        @{ Keys = @('self'); Prio = 1; De = 'immer'; En = 'always'
           ShortDe = 'eigener Charakter'; ShortEn = 'own character' }) }
    @{ De = 'Gruppe / Schlachtzug immer umrandet'; En = 'Party / raid always outlined'
       NoteDe = '(Schlachtzug kostet viele FPS)'; NoteEn = '(raid costs a lot of FPS)'
       Choices = @(
        @{ Keys = @(); De = 'aus'; En = 'off' }
        @{ Keys = @('party'); Prio = 1; De = '5er-Gruppe'; En = 'party of 5'
           ShortDe = '5er-Gruppe'; ShortEn = 'party' }
        @{ Keys = @('raid'); Prio = 2; De = 'ganzer Schlachtzug'; En = 'whole raid'
           ShortDe = 'Schlachtzug'; ShortEn = 'raid' }) }
    @{ De = 'Durch Waende sichtbar'; En = 'Visible through walls'
       NoteDe = '(nur Gruppe/Schlachtzug: steht die Gruppe oben auf aus, nur wo verdeckt)'
       NoteEn = '(party/raid only: with party/raid off above, only where hidden)'
       Choices = @(
        @{ Keys = @(); De = 'nie'; En = 'never' }
        @{ Keys = @('wallsgroup'); Prio = 1; De = 'nur Gruppe/Schlachtzug'; En = 'party/raid only'
           ShortDe = 'durch Waende nur Gruppe/Schlachtzug'; ShortEn = 'through walls party/raid only' }
        @{ Keys = @('walls'); Prio = 2; BanRisk = $true; De = 'alle (unsicher, Bann-Gefahr)'; En = 'all (unsafe, ban risk)'
           ShortDe = 'durch Waende'; ShortEn = 'through walls' }) }
    @{ De = 'Farbe'; En = 'Color'
       Choices = @(
        @{ Keys = @(); De = 'Klassenfarbe'; En = 'class color' }
        @{ Keys = @('react'); Prio = 1; De = 'Gesinnungsfarbe'; En = 'reaction color'
           ShortDe = 'Gesinnungsfarbe'; ShortEn = 'reaction color' }) }
)

function Set-OutlineOptions([string]$v) {
    $on = Get-OptionKeys $OUTLINE_OPTIONS $v
    foreach ($k in $OUTLINE_FLAGS.Keys) {
        $off = $OUTLINE_FLAGS[$k] - 0x400C00
        Assert-Bytes $off @(0xCC) 'Umrandung'
        # Auch ein ausgeschalteter Schalter wird (unveraendert) geschrieben,
        # damit die Stelle in der Original-Byte-Tabelle landet.
        if ($on -contains $k) { Patch $off @(0x01) } else { Patch $off @(0xCC) }
    }
}

function Get-OutlineOptionsFromExe {
    $on = @()
    foreach ($k in $OUTLINE_FLAGS.Keys) {
        $b = $script:f[$OUTLINE_FLAGS[$k] - 0x400C00]
        if ($b -eq 1) { $on += $k } elseif ($b -ne 0xCC) { return $null }
    }
    return (ConvertTo-OptionValue $OUTLINE_OPTIONS $on)
}''' % (F['FWALLS'], F['FWALLSGRP'], F['FSELF'], F['FHIDDEN'], F['FPARTY'], F['FRAID'], F['FREACT'])
out += opts.split('\n')
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outline10_ps.txt'), 'w').write('\n'.join(out) + '\n')
print(len(out), 'Zeilen')

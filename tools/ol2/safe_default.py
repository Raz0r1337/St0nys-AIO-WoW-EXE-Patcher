# Nr. 68: zuerst "sicheren Standard anwenden" oder "Patch-Optionen aufrufen"; Standard hidden,wallsgroup.
# Aufruf: safe_default.py <apply_patches.ps1>
import sys
path = sys.argv[1]
raw = open(path, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
def once(a, b):
    global s
    n = s.count(a); assert n == 1, (a[:90], n)
    s = s.replace(a, b)
once("""        ChoiceHint    = 'Je Punkt eine Zahl eingeben, ENTER = Vorschlag in Klammern.'
""", """        ChoiceHint    = 'Je Punkt eine Zahl eingeben, ENTER = Vorschlag in Klammern.'
        SafeOpt1      = '1 = sicheren Standard anwenden ({0})'
        SafeOpt2      = '2 = Patch-Optionen aufrufen (Achtung: das kann den Patch unsicher machen)'
        SafeAsk       = 'Auswahl'
""")
once("""        ChoiceHint    = 'Enter a number for each point, ENTER = suggestion in brackets.'
""", """        ChoiceHint    = 'Enter a number for each point, ENTER = suggestion in brackets.'
        SafeOpt1      = '1 = apply the safe default ({0})'
        SafeOpt2      = '2 = open the patch options (caution: this can make the patch unsafe)'
        SafeAsk       = 'Choice'
""")
once("""       Questions = $OUTLINE_OPTIONS
       Default = 'hidden'
""", """       Questions = $OUTLINE_OPTIONS
       Default = 'hidden,wallsgroup'
       SafeDefault = $true
""")
once("""        # Eigene Sektion (.outl), siehe Add-Outline. Die Einstellungen
        # (Umschalter vor dem Patchen, Standard: eigener Charakter nur wo
        # verdeckt) setzt Set-OutlineOptions.""",
"""        # Eigene Sektion (.outl), siehe Add-Outline. Die Einstellungen
        # (sicherer Standard: eigener Charakter nur wo verdeckt, durch Waende
        # nur Gruppe/Schlachtzug - oder eigene Umschalter) setzt
        # Set-OutlineOptions.""")
# Doku-Kommentar der Patch-Eigenschaften
once("""#            Der Wert sind die eingeschalteten Keys durch Komma getrennt
#            (z.B. "hidden,party") oder "none"
""", """#            Der Wert sind die eingeschalteten Keys durch Komma getrennt
#            (z.B. "hidden,party") oder "none"
#    SafeDefault - optional mit Questions: Default ist der sichere Standard.
#            Vor den Umschaltern fragt der Patcher dann nur "1 = sicheren
#            Standard anwenden" oder "2 = Patch-Optionen aufrufen"
""")
# Abfrage
once("""    if ($p.Questions) {
        $v = Read-OptionAnswers $p.Questions $def
    } else {""", """    if ($p.Questions) {
        $v = $null
        if ($p.SafeDefault) { $v = Read-SafeChoice $p $def }
        if ($null -eq $v) { $v = Read-OptionAnswers $p.Questions $def }
    } else {""")
once("""# Fragt jeden Punkt als Umschalter ab:""", """# Patches mit SafeDefault: zuerst nur "1 = sicheren Standard anwenden" oder
# "2 = Patch-Optionen aufrufen". Vorschlag ist 1, wenn der bisherige Wert der
# sichere Standard ist (oder es keinen gibt), sonst 2 - eigene Einstellungen
# gehen mit ENTER also nicht verloren. Liefert den sicheren Wert oder $null
# (dann folgen die Umschalter, mit dem bisherigen Wert als Vorschlag).
function Read-SafeChoice($p, [string]$def) {
    $opts = $p.Questions
    $safe = ConvertTo-OptionValue $opts (Get-OptionKeys $opts $p.Default)
    $cur = $safe
    $k = Get-OptionKeys $opts $def
    if ($def -ne '' -and $null -ne $k) { $cur = ConvertTo-OptionValue $opts $k }
    $n = 2; if ($cur -eq $safe) { $n = 1 }
    Say "  $(T 'SafeOpt1' (Format-OptionValue $opts $safe))"
    Say "  $(T 'SafeOpt2')" 'DarkYellow'
    while ($true) {
        $a = Ask "  $(T 'SafeAsk') [$n]"
        if ($a -eq '') { $a = [string]$n }
        if ($a -eq '1') { return $safe }
        if ($a -eq '2') { return $null }
        Say (T 'ChoiceBad' 2) 'Yellow'
    }
}

# Fragt jeden Punkt als Umschalter ab:""")
open(path, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')

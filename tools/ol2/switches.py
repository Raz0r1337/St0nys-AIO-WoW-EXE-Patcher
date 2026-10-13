# Umrandung: Umschalter statt J/N-Fragen (outline7), Durch Waende nur Gruppe/Schlachtzug.
# Aufruf: switches.py <Worktree> <outline7_ps.txt>
import sys
w, gen = sys.argv[1], sys.argv[2]
p = w + '/apply_patches.ps1'
raw = open(p, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
new = open(gen, encoding='ascii').read().rstrip('\n') + '\n'
def once(a, b):
    global s
    n = s.count(a); assert n == 1, (a[:90], n)
    s = s.replace(a, b)
# 1) Umrandung: Kopf + Add-Outline + Einstellungen
a = s.index('#  Umrandung fuer Ziel und Mouseover (St0ny), mit Einstellungen\n')
a = s.rindex('# ====', 0, a)
g = s.index('function Get-OutlineOptionsFromExe {', a)
z = s.index('\n}\n', g) + 3
s = s[:a] + new + s[z:]
# 2) allgemeine Hilfen fuer Questions
a = s.index('# Patches mit Questions (J/N-Fragen statt einer Eingabezeile, z.B. die\n')
z = s.index('function Get-SelectedCount')
s = s[:a] + '''# Patches mit Questions (Umschalter statt einer Eingabezeile, z.B. die
# Umrandung): Jeder Punkt hat mehrere Wahlen (Choices), die erste ist "aus",
# jede andere schaltet bestimmte Keys ein. Der Wert sind die eingeschalteten
# Keys, durch Komma getrennt in der Reihenfolge der Punkte, oder "none".
# Get-OptionKeys liefert die Keys (leeres Array bei "none") oder $null bei
# einem ungueltigen Wert.
function Get-OptionKeys($opts, [string]$v) {
    $all = @(); foreach ($q in $opts) { foreach ($c in $q.Choices) { $all += $c.Keys } }
    $keys = @()
    $t = $v.Trim().ToLowerInvariant()
    if ($t -eq '' -or $t -eq 'none') { return , $keys }
    foreach ($k in ($t -split '\\s*,\\s*')) {
        if ($all -notcontains $k) { return $null }
        if ($keys -notcontains $k) { $keys += $k }
    }
    return , $keys
}

# Gewaehlte Wahl eines Punkts (Index) zu den Keys: von den passenden die mit
# der hoechsten Prio, sonst die erste ("aus").
function Get-OptionChoice($q, $keys) {
    $pick = 0; $prio = -1
    for ($i = 1; $i -lt $q.Choices.Count; $i++) {
        $c = $q.Choices[$i]
        $all = $true; foreach ($k in $c.Keys) { if ($keys -notcontains $k) { $all = $false } }
        if ($all -and [int]$c.Prio -gt $prio) { $pick = $i; $prio = [int]$c.Prio }
    }
    return $pick
}

function Test-OptionValue($opts, [string]$v) {
    if ($null -ne (Get-OptionKeys $opts $v)) { return $null }
    $all = @(); foreach ($q in $opts) { foreach ($c in $q.Choices) { $all += $c.Keys } }
    $list = $all -join ','
    return (L "Erlaubt sind none oder eine Liste aus $list (durch Komma getrennt)." "Allowed are none or a comma-separated list of $list.")
}

# Einheitlicher Wert: je Punkt die Keys der gewaehlten Wahl.
function ConvertTo-OptionValue($opts, $keys) {
    $out = @()
    foreach ($q in $opts) { $out += @($q.Choices[(Get-OptionChoice $q $keys)].Keys) }
    if ($out.Count -eq 0) { return 'none' }
    return ($out -join ',')
}

# Wert fuer die Anzeige: die eingeschalteten Wahlen in Kurzform.
function Format-OptionValue($opts, [string]$v) {
    $keys = Get-OptionKeys $opts $v
    if ($null -eq $keys) { return $v }
    $out = @()
    foreach ($q in $opts) {
        $c = $q.Choices[(Get-OptionChoice $q $keys)]
        if (@($c.Keys).Count -gt 0) { $out += (L $c.ShortDe $c.ShortEn) }
    }
    if ($out.Count -eq 0) { return (T 'OptNone') }
    return ($out -join ', ')
}

# Fragt jeden Punkt als Umschalter ab: die Wahlen nummeriert (in Zeilen bis
# etwa 64 Zeichen, die letzte Zeile ist die Eingabe), ENTER uebernimmt den
# Vorschlag aus $def.
function Read-OptionAnswers($opts, [string]$def) {
    $keys = Get-OptionKeys $opts $def
    if ($null -eq $keys) { $keys = @() }
    Say (T 'ChoiceHint') 'DarkGray'
    $on = @()
    foreach ($q in $opts) {
        $cur = Get-OptionChoice $q $keys
        $lines = @(); $line = ''
        for ($i = 0; $i -lt $q.Choices.Count; $i++) {
            $x = "$($i + 1) = $(L $q.Choices[$i].De $q.Choices[$i].En)"
            if ($line -and ($line.Length + 3 + $x.Length) -gt 64) { $lines += $line; $line = $x }
            elseif ($line) { $line += "   $x" }
            else { $line = $x }
        }
        $lines += $line
        Write-Host ''
        Say "  $(L $q.De $q.En):"
        if ($q.NoteDe) { Say "    $(L $q.NoteDe $q.NoteEn)" 'DarkGray' }
        for ($i = 0; $i -lt $lines.Count - 1; $i++) { Say "    $($lines[$i])" }
        while ($true) {
            $a = Ask "    $($lines[$lines.Count - 1]) [$($cur + 1)]"
            if ($a -eq '') { $n = $cur; break }
            $n = 0
            if ([int]::TryParse($a, [ref]$n) -and $n -ge 1 -and $n -le $q.Choices.Count) { $n--; break }
            Say (T 'ChoiceBad' $q.Choices.Count) 'Yellow'
        }
        $on += @($q.Choices[$n].Keys)
    }
    return (ConvertTo-OptionValue $opts $on)
}

''' + s[z:]
# 3) Warnung bei unsicheren Wahlen
once("""    foreach ($o in $p.Questions) { if ($o.BanRisk -and $keys -contains $o.Key) { $risky += (L $o.ShortDe $o.ShortEn) } }""",
     """    foreach ($q in $p.Questions) { $c = $q.Choices[(Get-OptionChoice $q $keys)]; if ($c.BanRisk) { $risky += (L $c.ShortDe $c.ShortEn) } }""")
# 4) Texte
once("""        No            = 'N'
        YesNo         = '(J/N)'
        YesNoBad      = 'Bitte J oder N eingeben (ENTER = Vorschlag in Klammern).'
        OptNone       = 'alles N'
""", """        ChoiceHint    = 'Je Punkt eine Zahl eingeben, ENTER = Vorschlag in Klammern.'
        ChoiceBad     = 'Bitte eine Zahl von 1 bis {0} eingeben (ENTER = Vorschlag in Klammern).'
        OptNone       = 'alles aus'
""")
once("""        No            = 'N'
        YesNo         = '(Y/N)'
        YesNoBad      = 'Please enter Y or N (ENTER = suggestion in brackets).'
        OptNone       = 'all N'
""", """        ChoiceHint    = 'Enter a number for each point, ENTER = suggestion in brackets.'
        ChoiceBad     = 'Please enter a number from 1 to {0} (ENTER = suggestion in brackets).'
        OptNone       = 'all off'
""")
# 5) Kommentare
once("""#    Questions - optional, statt PromptDe/PromptEn: J/N-Fragen (Key, De, En,
#            ShortDe, ShortEn, optional BanRisk = rote Warnung, wenn mit J
#            beantwortet). Der Wert sind die mit J beantworteten Keys durch
#            Komma getrennt (z.B. "self,party") oder "none\"""", """#    Questions - optional, statt PromptDe/PromptEn: Umschalter (je Punkt De,
#            En, optional NoteDe/NoteEn und Choices = Wahlen mit Keys, De,
#            En, ShortDe, ShortEn, Prio, optional BanRisk = rote Warnung).
#            Der Wert sind die eingeschalteten Keys durch Komma getrennt
#            (z.B. "hidden,party") oder "none\"""")
once("""        # Eigene Sektion (.outl), siehe Add-Outline. Die Einstellungen (J/N vor
        # dem Patchen, Standard: nur "eigener Charakter nur wo verdeckt" = J)
        # setzt Set-OutlineOptions.""", """        # Eigene Sektion (.outl), siehe Add-Outline. Die Einstellungen
        # (Umschalter vor dem Patchen, Standard: eigener Charakter nur wo
        # verdeckt) setzt Set-OutlineOptions.""")
once("""    # J/N-Werte (z.B. Umrandung) in die Reihenfolge der Fragen bringen - die
    # kann sich zwischen Versionen aendern, gleiche Antworten sind keine Aenderung.""",
     """    # Werte der Umschalter (z.B. Umrandung) vereinheitlichen - die Reihenfolge
    # kann sich zwischen Versionen aendern, gleiche Einstellungen sind keine
    # Aenderung.""")
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')

# Umrandung Nr. 68 mit Einstellungen als J/N-Fragen (statt Einzelpatches Nr. 69-74).
# Basis: apply_patches.ps1 aus 3f13cfc (90 Patches). Aufruf: edit_script5.py <apply_patches.ps1> <outline5_ps.txt>
import sys, re
path, gen = sys.argv[1], sys.argv[2]
raw = open(path, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
new = open(gen, encoding='ascii').read().rstrip('\n') + '\n'

def once(a, b):
    global s
    n = s.count(a); assert n == 1, (a[:90], n)
    s = s.replace(a, b)

# 1) Add-Outline samt Kommentarkopf ersetzen (neue Fassung + Einstellungen)
a = s.index('#  Umrandung fuer Ziel und Mouseover (St0ny)\n')
a = s.rindex('# ====', 0, a)
z = s.index('\n}\n', s.index('function Add-Outline {', a)) + 3
assert s[a:z].count('function ') == 1
s = s[:a] + new + s[z:]

# 2) Sprachtexte fuer die J/N-Fragen
once("""        Yes           = 'J'
""", """        Yes           = 'J'
        No            = 'N'
        YesNo         = '(J/N)'
        YesNoBad      = 'Bitte J oder N eingeben (ENTER = Vorschlag in Klammern).'
        OptNone       = 'Standard (alles N)'
""")
once("""        Yes           = 'Y'
""", """        Yes           = 'Y'
        No            = 'N'
        YesNo         = '(Y/N)'
        YesNoBad      = 'Please enter Y or N (ENTER = suggestion in brackets).'
        OptNone       = 'default (all N)'
""")

# 3) Beschreibung der Patch-Felder
once("""#    Normalize - optional: Scriptblock, der einen gueltigen Wert in eine
#            einheitliche Schreibweise bringt (z.B. Build-Datum mit Uhrzeit)
""", """#    Normalize - optional: Scriptblock, der einen gueltigen Wert in eine
#            einheitliche Schreibweise bringt (z.B. Build-Datum mit Uhrzeit)
#    Questions - optional, statt PromptDe/PromptEn: J/N-Fragen (Key, De, En,
#            ShortDe, ShortEn, optional BanRisk = rote Warnung, wenn mit J
#            beantwortet). Der Wert sind die mit J beantworteten Keys durch
#            Komma getrennt (z.B. "self,party") oder "none"
""")

# 4) Outline-Eintrag: ungetestet, Einstellungen als Fragen
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
       Questions = $OUTLINE_OPTIONS
       Default = 'none'
       Check = { param($v) Test-OptionValue $OUTLINE_OPTIONS $v }
       Normalize = { param($v) ConvertTo-OptionValue $OUTLINE_OPTIONS (Get-OptionKeys $OUTLINE_OPTIONS $v) }
       Decode = { Get-OutlineOptionsFromExe }
       Code = {
        # Eigene Sektion (.outl), siehe Add-Outline. Die Einstellungen (J/N vor
        # dem Patchen, Standard alles N = nur Ziel und Mouseover, nicht durch
        # Waende) setzt Set-OutlineOptions.
        Add-Outline
        Set-OutlineOptions $script:VALUES['outline']
    }}
""")

# 5) Allgemeine Hilfen fuer Questions, vor Get-SelectedCount
once("""function Get-SelectedCount($sel) {
""", """# Patches mit Questions (J/N-Fragen statt einer Eingabezeile, z.B. die
# Umrandung): Der Wert sind die mit J beantworteten Keys, durch Komma getrennt
# in der Reihenfolge der Fragen, oder "none". Get-OptionKeys liefert die Keys
# (leeres Array bei "none") oder $null bei einem ungueltigen Wert.
function Get-OptionKeys($opts, [string]$v) {
    $keys = @()
    $t = $v.Trim().ToLowerInvariant()
    if ($t -eq '' -or $t -eq 'none') { return , $keys }
    foreach ($k in ($t -split '\\s*,\\s*')) {
        if (@($opts | Where-Object { $_.Key -eq $k }).Count -eq 0) { return $null }
        if ($keys -notcontains $k) { $keys += $k }
    }
    return , $keys
}

function Test-OptionValue($opts, [string]$v) {
    if ($null -ne (Get-OptionKeys $opts $v)) { return $null }
    $list = @($opts | ForEach-Object { $_.Key }) -join ','
    return (L "Erlaubt sind none oder eine Liste aus $list (durch Komma getrennt)." "Allowed are none or a comma-separated list of $list.")
}

function ConvertTo-OptionValue($opts, $keys) {
    $out = @()
    foreach ($o in $opts) { if ($keys -contains $o.Key) { $out += $o.Key } }
    if ($out.Count -eq 0) { return 'none' }
    return ($out -join ',')
}

# Wert fuer die Anzeige: die eingeschalteten Punkte in Kurzform.
function Format-OptionValue($opts, [string]$v) {
    $keys = Get-OptionKeys $opts $v
    if ($null -eq $keys) { return $v }
    if ($keys.Count -eq 0) { return (T 'OptNone') }
    $out = @()
    foreach ($o in $opts) { if ($keys -contains $o.Key) { $out += (L $o.ShortDe $o.ShortEn) } }
    return ($out -join ', ')
}

# Fragt jeden Punkt mit J/N ab, ENTER uebernimmt den Vorschlag aus $def.
function Read-OptionAnswers($opts, [string]$def) {
    $keys = Get-OptionKeys $opts $def
    if ($null -eq $keys) { $keys = @() }
    $on = @()
    foreach ($o in $opts) {
        $cur = $keys -contains $o.Key
        $hint = T 'No'; if ($cur) { $hint = T 'Yes' }
        while ($true) {
            $a = (Ask "  $(L $o.De $o.En) $(T 'YesNo') [$hint]").ToUpperInvariant()
            if ($a -eq '') { $yes = $cur; break }
            if ($a -eq 'J' -or $a -eq 'Y') { $yes = $true; break }
            if ($a -eq 'N') { $yes = $false; break }
            Say (T 'YesNoBad') 'Yellow'
        }
        if ($yes) { $on += $o.Key }
    }
    return (ConvertTo-OptionValue $opts $on)
}

function Get-SelectedCount($sel) {
""")

# 6) Anzeige des Werts
once("""        if ($v -match '\\sFR\\s*$') { $t += ' FR' }
        return $t
    }
    return $v
}
""", """        if ($v -match '\\sFR\\s*$') { $t += ' FR' }
        return $t
    }
    if ($p.Questions) { return (Format-OptionValue $p.Questions $v) }
    return $v
}
""")

# 7) Abfrage: Questions statt Eingabezeile
once("""    $shown = $def
    if ($useNow) { $shown = T 'ValueAtYes'; if ($def -match '\\sFR\\s*$') { $shown += ' FR' } }
    if ($def -ne '') { Say "$(PatchName $p) $(T $label $shown)" } else { Say (PatchName $p) }
    while ($true) {
        $hint = ''; if ($def -ne '') { $hint = " [$shown]" }
        $v = Ask "  $(L $p.PromptDe $p.PromptEn)$hint"
        $takeNow = $false
        if ($v -eq '') { $v = $def; $takeNow = $useNow }
        $err = & $p.Check $v
        if (-not $err) { break }
        Say $err 'Yellow'
    }
""", """    $shown = $def
    if ($useNow) { $shown = T 'ValueAtYes'; if ($def -match '\\sFR\\s*$') { $shown += ' FR' } }
    if ($p.Questions) { $shown = Format-OptionValue $p.Questions $def }
    if ($def -ne '') { Say "$(PatchName $p) $(T $label $shown)" } else { Say (PatchName $p) }
    $takeNow = $false
    if ($p.Questions) {
        $v = Read-OptionAnswers $p.Questions $def
    } else {
        while ($true) {
            $hint = ''; if ($def -ne '') { $hint = " [$shown]" }
            $v = Ask "  $(L $p.PromptDe $p.PromptEn)$hint"
            $takeNow = $false
            if ($v -eq '') { $v = $def; $takeNow = $useNow }
            $err = & $p.Check $v
            if (-not $err) { break }
            Say $err 'Yellow'
        }
    }
""")

# 8) Zusammenfassung: alter Wert in Kurzform
once("""            $old = $state.Values[$p.Id]; if (-not $old) { $old = '?' }
""", """            $old = $state.Values[$p.Id]; if (-not $old) { $old = '?' } elseif ($p.Questions) { $old = Format-OptionValue $p.Questions $old }
""")

# 9) Rote Warnung auch fuer einzelne Punkte (Umrandung: durch Waende)
once("""$cheat = @()
foreach ($p in $chosen) { if ($p.BanRisk) { $cheat += PatchRef $p } }
""", """$cheat = @()
foreach ($p in $chosen) {
    if ($p.BanRisk) { $cheat += PatchRef $p; continue }
    if (-not $p.Questions) { continue }
    $keys = Get-OptionKeys $p.Questions $VALUES[$p.Id]
    $risky = @()
    foreach ($o in $p.Questions) { if ($o.BanRisk -and $keys -contains $o.Key) { $risky += (L $o.ShortDe $o.ShortEn) } }
    if ($risky.Count -gt 0) { $cheat += "$(PatchRef $p): $($risky -join ', ')" }
}
""")

ids = [re.match(r"^    @\{ Id = '([^']+)'", l).group(1) for l in s.split('\n') if re.match(r"^    @\{ Id = '", l)]
assert len(ids) == 90 and ids[67] == 'outline' and ids[68] == 'tracker', (len(ids), ids[66:70])
assert '[^\\x00-\\x7F]' and not re.search(r'[^\x00-\x7F]', s)
open(path, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok, Patches:', len(ids))

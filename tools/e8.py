R("""# ============================================================
#  PATCH-DEFINITIONEN
""", """# ============================================================
#  Helfer fuer den Sprunghoehen-Patch
#  Der Wert ist die Anfangsgeschwindigkeit des Sprungs (float, im Original
#  -7.9555473). Negativ heisst nach oben; die Sprunghoehe waechst mit dem
#  Quadrat des Betrags. Komma oder Punkt als Dezimaltrenner.
# ============================================================
function ConvertTo-JumpValue([string]$v) {
    $d = 0.0
    $ok = [double]::TryParse($v.Trim().Replace(',', '.'), [System.Globalization.NumberStyles]::Float,
        [System.Globalization.CultureInfo]::InvariantCulture, [ref]$d)
    if (-not $ok -or $d -ge 0 -or $d -lt -100) { return $null }
    return [float]$d
}

function Test-JumpValue([string]$v) {
    if ($null -eq (ConvertTo-JumpValue $v)) { return (L 'Eine negative Zahl von -100 bis knapp unter 0, z.B. -11.25.' 'A negative number from -100 to just below 0, e.g. -11.25.') }
    return $null
}

# ============================================================
#  PATCH-DEFINITIONEN
""")
R("""       Code = {
        Patch 0x6404F @(0xFF)
    }}
""", """       Code = {
        Patch 0x6404F @(0xFF)
    }}

    @{ Id = 'climb'; Cat = 'gameplay'; On = $false
       Author = 'Alastor StrixEfuartus'
       De = 'Steigwinkel-Begrenzung aufheben (jeden Hang hochlaufen)'
       En = 'Remove the climb angle limit (walk up any slope)'
       NoteDe = 'kann vom Server als Cheat erkannt werden'
       NoteEn = 'may be detected as cheating by the server'
       Code = {
        # Aus der 12th Generation EXE (Alastor StrixEfuartus). VA 0xA37F0C ist
        # der Kosinus des steilsten begehbaren Hangs, im Original 0.6427876 =
        # cos(50 Grad). Die Bewegungs-/Kollisionsroutinen vergleichen die
        # Neigung damit; 0.0 = cos(90 Grad) macht jeden Hang begehbar.
        Patch 0x63670C @(0x00, 0x00, 0x00, 0x00)
    }}

    @{ Id = 'jump'; Cat = 'gameplay'; On = $false
       Author = 'Alastor StrixEfuartus'
       De = 'Sprunghoehe aendern (Original -7.9555473)'
       En = 'Change jump height (original -7.9555473)'
       NoteDe = 'kann vom Server als Cheat erkannt werden'
       NoteEn = 'may be detected as cheating by the server'
       PromptDe = 'Neuer Wert, negativ - je kleiner, desto hoeher (z.B. -11.25 = doppelte Hoehe)'
       PromptEn = 'New value, negative - the lower, the higher (e.g. -11.25 = double height)'
       Default = '-7.9555473'
       Check = { param($v) Test-JumpValue $v }
       Code = {
        # Aus der 12th Generation EXE (Alastor StrixEfuartus). VA 0xAA33DC ist
        # die Anfangsgeschwindigkeit des Sprungs (float, einzige Lesestelle
        # fld bei VA 0x98845C), im Original -7.9555473 = D8 93 FE C0.
        Patch 0x6A1BDC ([BitConverter]::GetBytes([float](ConvertTo-JumpValue $script:VALUES['jump'])))
    }}
""")

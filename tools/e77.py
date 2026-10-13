# 1) ConvertTo-Indices: no int overflow
R("""        if ($tok -match '^(\\d+)-(\\d+)$') {
            $a = [int]$matches[1]; $b = [int]$matches[2]
            if ($a -gt $b) { $t = $a; $a = $b; $b = $t }
        } elseif ($tok -match '^\\d+$') {""", """        if ($tok -match '^(\\d{1,6})-(\\d{1,6})$') {
            $a = [int]$matches[1]; $b = [int]$matches[2]
            if ($a -gt $b) { $t = $a; $a = $b; $b = $t }
        } elseif ($tok -match '^\\d{1,6}$') {""")
# 2) trap for unexpected errors
R("""function Exit-Patcher([int]$code) {
    if (-not $Unattended) {
        Write-Host ''
        [void](Read-Host "  $(T 'PressEnter')")
    }
    exit $code
}
""", """function Exit-Patcher([int]$code) {
    if (-not $Unattended) {
        Write-Host ''
        [void](Read-Host "  $(T 'PressEnter')")
    }
    exit $code
}

# Unerwarteter Fehler irgendwo im Skript: Meldung zeigen und wie bei jedem
# anderen Fehler mit Pause beenden - sonst schliesst sich das Fenster beim
# Start per Doppelklick einfach, ohne dass man etwas lesen kann.
trap {
    if (-not $script:lang) { $script:lang = 'de' }
    Write-Host ''
    Say ('[FEHLER/ERROR] ' + $_.Exception.Message) 'Red'
    if ($_.InvocationInfo -and $_.InvocationInfo.PositionMessage) { Say $_.InvocationInfo.PositionMessage 'DarkGray' }
    Exit-Patcher 1
}
""")
# 3) atomic write
R("""# --- 8. Datei einmal zurueckschreiben ---
try {
    [System.IO.File]::WriteAllBytes($file, $f)
} catch {
    Write-Host ''
    Say (T 'WriteFail') 'Red'
    Say $_.Exception.Message 'Red'
    try { Remove-Item -LiteralPath $stateTmp -Force -ErrorAction SilentlyContinue } catch { }
    Exit-Patcher 1
}
""", """# --- 8. Datei einmal zurueckschreiben ---
# Erst in eine .tmp-Datei, dann in einem Schritt an die Stelle der Wow.exe -
# bricht das Schreiben ab (Platte voll, Absturz), bleibt die bisherige Wow.exe
# unversehrt. Geht das Ersetzen nicht (z.B. Dateisystem ohne Replace), wird
# direkt geschrieben.
$fileTmp = $file + '.tmp'
try {
    [System.IO.File]::WriteAllBytes($fileTmp, $f)
    try {
        [System.IO.File]::Replace($fileTmp, $file, $null)
    } catch {
        [System.IO.File]::WriteAllBytes($file, $f)
        try { [System.IO.File]::Delete($fileTmp) } catch { }
    }
} catch {
    Write-Host ''
    Say (T 'WriteFail') 'Red'
    Say $_.Exception.Message 'Red'
    try { Remove-Item -LiteralPath $fileTmp -Force -ErrorAction SilentlyContinue } catch { }
    try { Remove-Item -LiteralPath $stateTmp -Force -ErrorAction SilentlyContinue } catch { }
    Exit-Patcher 1
}
""")
# 13a) stale state tmp when nothing applied
R("""    } elseif (Test-Path -LiteralPath $stateFile -PathType Leaf) {
        [System.IO.File]::Delete($stateFile)
    }
} catch {
    $stateWarn = $_.Exception.Message
}""", """    } elseif (Test-Path -LiteralPath $stateFile -PathType Leaf) {
        [System.IO.File]::Delete($stateFile)
    }
    if ($total -eq 0 -and (Test-Path -LiteralPath $stateTmp -PathType Leaf)) { [System.IO.File]::Delete($stateTmp) }
} catch {
    $stateWarn = $_.Exception.Message
}""")
# 4) Save-Values for -Select mode
R("""# Gemerkte Werte (Zeilen "value.<Id>=<Wert>") aus patcher_selection.ini lesen.
function Get-SavedValues {""", """# Nur die Werte (value.<Id>=...) in patcher_selection.ini erneuern, die Auswahl
# bleibt stehen - fuer -Select, das die gespeicherte Auswahl nicht veraendern
# soll. Fehler beim Schreiben sind hier unkritisch und werden ignoriert.
function Save-Values($values) {
    if ($values.Count -eq 0) { return }
    try {
        $lines = New-Object System.Collections.Generic.List[string]
        if (Test-Path -LiteralPath $settingsFile -PathType Leaf) {
            foreach ($l in [System.IO.File]::ReadAllLines($settingsFile)) {
                if ($l -notmatch '^\\s*value\\.') { $lines.Add($l) }
            }
        }
        foreach ($k in ($values.Keys | Sort-Object)) { $lines.Add("value.$k=$($values[$k])") }
        [System.IO.File]::WriteAllLines($settingsFile, $lines.ToArray())
    } catch { }
}

# Gemerkte Werte (Zeilen "value.<Id>=<Wert>") aus patcher_selection.ini lesen.
function Get-SavedValues {""")
R("""if ($fromMenu) {
    $allValues = @{}
    foreach ($k in $savedValues.Keys) { $allValues[$k] = $savedValues[$k] }
    foreach ($k in $VALUES.Keys) { $allValues[$k] = $VALUES[$k] }
    Write-Host ''
    $saveError = Save-Selection $selection $allValues
    if ($saveError) { Say (T 'SaveFail' $saveError) 'Yellow' } else { Say (T 'Saved') 'DarkGray' }
}
""", """$allValues = @{}
foreach ($k in $savedValues.Keys) { $allValues[$k] = $savedValues[$k] }
foreach ($k in $VALUES.Keys) { $allValues[$k] = $VALUES[$k] }
if ($fromMenu) {
    Write-Host ''
    $saveError = Save-Selection $selection $allValues
    if ($saveError) { Say (T 'SaveFail' $saveError) 'Yellow' } else { Say (T 'Saved') 'DarkGray' }
} elseif ($VALUES.Count -gt 0) {
    # -Select laesst die gespeicherte Auswahl unveraendert, eingegebene Werte
    # werden aber gemerkt (die Icon-Erkennung braucht z.B. den Pfad).
    Save-Values $allValues
}
""")
# 5) unattended: saved value wins over the active one
R("""# Default; Patches mit Suggest berechnen ihren Vorschlag selbst (Build-Datum:
# heute). Ohne Rueckfragen (-Unattended) gilt der gemerkte Wert. Ist der Patch
# schon in der Wow.exe, ist sein aktueller Wert der Vorschlag.""", """# Default; Patches mit Suggest berechnen ihren Vorschlag selbst (Build-Datum:
# heute). Ist der Patch schon in der Wow.exe, ist sein aktueller Wert der
# Vorschlag. Ohne Rueckfragen (-Unattended) gilt der gemerkte Wert - auch wenn
# der Patch schon mit einem anderen Wert drin ist, sonst liesse sich der Wert
# unbeaufsichtigt nie aendern.""")
R("""    if ($active) { $saved = $script:state.Values[$p.Id] }""",
  """    if ($active -and -not ($Unattended -and $saved)) { $saved = $script:state.Values[$p.Id] }""")
# 6) header slot check before growing (hdp, camr)
R("""    $vsize = $MASK_OFF + $maskLen + $codeArr.Length
    $raw_size = AlignUp ($CODE_OFF + $codeArr.Length) $FA
""", """    $vsize = $CODE_OFF + $codeArr.Length
    $raw_size = AlignUp $vsize $FA
    $hoff = $sectBase + 40 * $nsec
    if (($hoff + 40) -gt (RU32 $script:f ($sectBase + 20))) { throw 'HD-Portraits: kein Platz im PE-Header fuer einen weiteren Sektionseintrag.' }
""")
R("""    Patch ($e + 24 + 56) ([BitConverter]::GetBytes([uint32](AlignUp ($new_rva + $vsize) $SA)))
    $hoff = $sectBase + 40 * $nsec
    if (($hoff + 40) -gt (RU32 $script:f ($sectBase + 20))) { throw 'HD-Portraits: kein Platz im PE-Header fuer einen weiteren Sektionseintrag.' }
""", """    Patch ($e + 24 + 56) ([BitConverter]::GetBytes([uint32](AlignUp ($new_rva + $vsize) $SA)))
""")
R("""    # --- Datei vergroessern: padding bis FileAlignment, dann Sektion anhaengen ---
    $raw_size = AlignUp $SEC_SIZE $FA
    $oldLen = $script:f.Length""", """    # --- Datei vergroessern: padding bis FileAlignment, dann Sektion anhaengen ---
    $hoff = $sectBase + 40 * $nsec
    if (($hoff + 40) -gt (RU32 $script:f ($sectBase + 20))) { throw 'CameraReforged: kein Platz im PE-Header fuer einen weiteren Sektionseintrag.' }
    $raw_size = AlignUp $SEC_SIZE $FA
    $oldLen = $script:f.Length""")
R("""    Patch ($e + 24 + 56) ([BitConverter]::GetBytes([uint32](AlignUp ($new_rva + $SEC_SIZE) $SA)))
    $hoff = $sectBase + 40 * $nsec
    if (($hoff + 40) -gt (RU32 $script:f ($sectBase + 20))) { throw 'CameraReforged: kein Platz im PE-Header fuer einen weiteren Sektionseintrag.' }
""", """    Patch ($e + 24 + 56) ([BitConverter]::GetBytes([uint32](AlignUp ($new_rva + $SEC_SIZE) $SA)))
""")
# 8) icon path relative to the Wow.exe folder; 13e) cache decoded icons
R("""function Resolve-IconPath([string]$v) {
    $p = $v.Trim().Trim('"')
    if (-not [System.IO.Path]::IsPathRooted($p)) { $p = Join-Path $scriptDir $p }
    return $p
}""", """# Relative Pfade gelten ab dem Ordner der Wow.exe (bei -Path kann der ein anderer
# als der Skriptordner sein).
function Resolve-IconPath([string]$v) {
    $p = $v.Trim().Trim('"')
    if (-not [System.IO.Path]::IsPathRooted($p)) { $p = Join-Path (Split-Path -Parent $file) $p }
    return $p
}""")
R("""# Die vier Bilder fuer die Slots: Hashtable Groesse -> dekodiertes Bild.
function Get-IconImages([string]$path) {
    $entries = Read-IconFile $path
    $result = @{}
    foreach ($slot in $ICON_SLOTS) {
        $e = Select-IconSource $entries $slot.Size
        try { $result[$slot.Size] = Get-IconImage $e } catch { throw ((L "Bild $($e.W)x$($e.H): " "Image $($e.W)x$($e.H): ") + $_.Exception.Message) }
    }
    return $result
}""", """# Die vier Bilder fuer die Slots: Hashtable Groesse -> dekodiertes Bild. Einmal
# dekodierte Dateien werden fuer diesen Lauf gemerkt (Pruefung, Patchen und
# Erkennung brauchen dieselbe Datei).
$iconCache = @{}
function Get-IconImages([string]$path) {
    if ($script:iconCache.ContainsKey($path)) { return $script:iconCache[$path] }
    $entries = Read-IconFile $path
    $result = @{}
    foreach ($slot in $ICON_SLOTS) {
        $e = Select-IconSource $entries $slot.Size
        try { $result[$slot.Size] = Get-IconImage $e } catch { throw ((L "Bild $($e.W)x$($e.H): " "Image $($e.W)x$($e.H): ") + $_.Exception.Message) }
    }
    $script:iconCache[$path] = $result
    return $result
}""")
# 9) returns
R("""    return @($d, $lng)
}""", """    return , @($d, $lng)
}""")
R("""    if ($w -eq $S -and $h -eq $S) { return $src }""", """    if ($w -eq $S -and $h -eq $S) { return , $src }""")
# 10) table regex
R("""        elseif ($l -match '^([a-z0-9]+);([0-9A-F]+);([0-9A-F]+);([01])$') {""",
  """        elseif ($l -match '^([A-Za-z0-9_]+);([0-9A-F]+);([0-9A-F]+);([01])$') {""")
# 11) BuildTable marker order, dead assignment
R("""    $a = $src.IndexOf('# BEGIN ORIGINAL-BYTES' + "`r`n")
    $z = $src.IndexOf('# END ORIGINAL-BYTES', $a)
    if ($a -lt 0 -or $z -lt 0) { Write-Host 'BuildTable: Markierungen nicht gefunden.'; exit 1 }""",
  """    $a = $src.IndexOf('# BEGIN ORIGINAL-BYTES' + "`r`n")
    $z = -1; if ($a -ge 0) { $z = $src.IndexOf('# END ORIGINAL-BYTES', $a) }
    if ($a -lt 0 -or $z -lt 0) { Write-Host 'BuildTable: Markierungen nicht gefunden.'; exit 1 }""")
R("""        $script:f = [byte[]]$orig.Clone()
        $script:chosenIds = $cfg
        $script:VALUES = @{}""", """        $script:f = [byte[]]$orig.Clone()
        $script:VALUES = @{}""")
# 12) comments
R("""# -Unattended stellt keine Rueckfragen: ohne -Language Deutsch, ohne -Select
# die gespeicherte Auswahl (bzw. die Standard-Auswahl, wenn es keine gibt).""",
  """# -Unattended stellt keine Rueckfragen: ohne -Language die gemerkte Sprache
# bzw. Deutsch, ohne -Select die gespeicherte Auswahl (bzw. die Standard-
# Auswahl, wenn es keine gibt).""")
R("""#  nur 120 Spalten. Ist das Fenster schmaler als das Banner, kommt dieselbe
#  Schrift zweizeilig (max. 78 Zeichen), damit nichts umbricht.""",
  """#  nur 120 Spalten. Ist das Fenster nicht breiter als das Banner (bei genau
#  136 Spalten wuerde die letzte Spalte schon umbrechen), kommt dieselbe
#  Schrift zweizeilig (max. 78 Zeichen), damit nichts umbricht.""")
# 13c) bilingual decoder messages
for de,en in [("Keine PNG-Datei.","Not a PNG file."),("PNG-Datei ist beschaedigt.","PNG file is damaged."),
    ("PNG: ungueltige oder zu grosse Abmessungen (max. 1024).","PNG: invalid or too large dimensions (max. 1024)."),
    ("PNG: unbekannter Farbtyp.","PNG: unknown colour type."),("PNG: Palette fehlt.","PNG: palette missing."),
    ("PNG: Bilddaten unvollstaendig.","PNG: image data incomplete."),("ICO: unbekanntes Bitmap-Format.","ICO: unknown bitmap format."),
    ("ICO: ungueltige Abmessungen.","ICO: invalid dimensions."),("ICO: komprimierte Bitmaps werden nicht unterstuetzt.","ICO: compressed bitmaps are not supported."),
    ("ICO: Bilddaten unvollstaendig.","ICO: image data incomplete."),("Interlaced PNG wird nicht unterstuetzt.","Interlaced PNG is not supported.")]:
    s=s.replace("throw '%s'"%de, "throw (L '%s' '%s')"%(de,en))
R("""throw 'PNG: ungueltige Bittiefe.' }
    if ($depth -lt 8 -and $ctype -notin @(0, 3)) { throw 'PNG: ungueltige Bittiefe.' }""",
  """throw (L 'PNG: ungueltige Bittiefe.' 'PNG: invalid bit depth.') }
    if ($depth -lt 8 -and $ctype -notin @(0, 3)) { throw (L 'PNG: ungueltige Bittiefe.' 'PNG: invalid bit depth.') }""")
R("""throw "ICO: Bittiefe $bpp wird nicht unterstuetzt." }""", """throw (L "ICO: Bittiefe $bpp wird nicht unterstuetzt." "ICO: bit depth $bpp is not supported.") }""")

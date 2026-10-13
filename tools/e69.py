R('''# ICO- oder PNG-Datei lesen. Liefert die Liste der enthaltenen Bilder.
function Read-IconFile([string]$path) {
    $data = [System.IO.File]::ReadAllBytes($path)
    if ($data.Length -ge 8 -and $data[0] -eq 0x89 -and $data[1] -eq 0x50) { return , @(Read-PngImage $data) }
    if ($data.Length -lt 6 -or (RU16 $data 0) -ne 0 -or (RU16 $data 2) -notin @(1, 2)) { throw (L 'Keine ICO- oder PNG-Datei.' 'Not an ICO or PNG file.') }
    $count = RU16 $data 4
    if ($count -lt 1 -or $data.Length -lt 6 + 16 * $count) { throw (L 'ICO-Datei ist leer oder beschaedigt.' 'ICO file is empty or damaged.') }
    $images = @()
    $errors = @()
    for ($i = 0; $i -lt $count; $i++) {
        $e = 6 + 16 * $i
        $size = RU32 $data ($e + 8); $off = RU32 $data ($e + 12)
        if ($size -lt 8 -or $off + $size -gt $data.Length) { $errors += "Bild $($i + 1): unvollstaendig"; continue }
        $sub = New-Object byte[] $size
        [Array]::Copy($data, $off, $sub, 0, $size)
        try {
            if ($sub[0] -eq 0x89 -and $sub[1] -eq 0x50) { $images += Read-PngImage $sub } else { $images += Read-DibImage $sub }
        } catch { $errors += "Bild $($i + 1): $($_.Exception.Message)" }
    }
    if ($images.Count -eq 0) { throw ((L 'Kein lesbares Bild in der ICO-Datei: ' 'No readable image in the ICO file: ') + ($errors -join '; ')) }
    return , $images
}

# Bild fuer eine Zielgroesse auswaehlen: exakt, sonst das kleinste groessere, sonst das groesste.
function Select-IconSource($images, [int]$S) {
    $exact = $images | Where-Object { $_.W -eq $S -and $_.H -eq $S } | Select-Object -First 1
    if ($exact) { return $exact }
    $larger = $images | Where-Object { $_.W -ge $S -and $_.H -ge $S } | Sort-Object { $_.W * $_.H } | Select-Object -First 1
    if ($larger) { return $larger }
    return ($images | Sort-Object { $_.W * $_.H } -Descending | Select-Object -First 1)
}
''','''# ICO- oder PNG-Datei lesen. Liefert die Bildeintraege (W, H, Rohdaten);
# dekodiert wird erst bei Bedarf (Get-IconImage) - ein 256er-PNG im ICO
# wuerde sonst unnoetig Zeit kosten, obwohl nur bis 48 Pixel gebraucht werden.
function Read-IconFile([string]$path) {
    $data = [System.IO.File]::ReadAllBytes($path)
    if ($data.Length -ge 24 -and $data[0] -eq 0x89 -and $data[1] -eq 0x50) {
        return , @(@{ W = [int](BE32 $data 16); H = [int](BE32 $data 20); Data = $data; Img = $null })
    }
    if ($data.Length -lt 6 -or (RU16 $data 0) -ne 0 -or (RU16 $data 2) -notin @(1, 2)) { throw (L 'Keine ICO- oder PNG-Datei.' 'Not an ICO or PNG file.') }
    $count = RU16 $data 4
    if ($count -lt 1 -or $data.Length -lt 6 + 16 * $count) { throw (L 'ICO-Datei ist leer oder beschaedigt.' 'ICO file is empty or damaged.') }
    $entries = @()
    for ($i = 0; $i -lt $count; $i++) {
        $e = 6 + 16 * $i
        $w = [int]$data[$e]; if ($w -eq 0) { $w = 256 }
        $h = [int]$data[$e + 1]; if ($h -eq 0) { $h = 256 }
        $size = RU32 $data ($e + 8); $off = RU32 $data ($e + 12)
        if ($size -lt 8 -or $off + $size -gt $data.Length) { continue }
        $sub = New-Object byte[] $size
        [Array]::Copy($data, $off, $sub, 0, $size)
        $entries += @{ W = $w; H = $h; Data = $sub; Img = $null }
    }
    if ($entries.Count -eq 0) { throw (L 'Kein Bild in der ICO-Datei.' 'No image in the ICO file.') }
    return , $entries
}

function Get-IconImage($entry) {
    if ($null -eq $entry.Img) {
        if ($entry.Data[0] -eq 0x89 -and $entry.Data[1] -eq 0x50) { $entry.Img = Read-PngImage $entry.Data } else { $entry.Img = Read-DibImage $entry.Data }
    }
    return $entry.Img
}

# Eintrag fuer eine Zielgroesse auswaehlen: exakt, sonst der kleinste groessere, sonst der groesste.
function Select-IconSource($entries, [int]$S) {
    $exact = $entries | Where-Object { $_.W -eq $S -and $_.H -eq $S } | Select-Object -First 1
    if ($exact) { return $exact }
    $larger = $entries | Where-Object { $_.W -ge $S -and $_.H -ge $S } | Sort-Object { $_.W * $_.H } | Select-Object -First 1
    if ($larger) { return $larger }
    return ($entries | Sort-Object { $_.W * $_.H } -Descending | Select-Object -First 1)
}

# Die vier Bilder fuer die Slots: Hashtable Groesse -> dekodiertes Bild.
function Get-IconImages([string]$path) {
    $entries = Read-IconFile $path
    $result = @{}
    foreach ($slot in $ICON_SLOTS) {
        $e = Select-IconSource $entries $slot.Size
        try { $result[$slot.Size] = Get-IconImage $e } catch { throw ((L "Bild $($e.W)x$($e.H): " "Image $($e.W)x$($e.H): ") + $_.Exception.Message) }
    }
    return $result
}
''')
R('''    try { [void](Read-IconFile $p) } catch { return $_.Exception.Message }
    return $null
}''','''    try { [void](Get-IconImages $p) } catch { return $_.Exception.Message }
    return $null
}''')
R('''    $images = Read-IconFile (Resolve-IconPath $v)
    foreach ($slot in $ICON_SLOTS) {
        $S = $slot.Size
        $dib = New-IconDib (Resize-Rgba (Select-IconSource $images $S) $S) $S''','''    $images = Get-IconImages (Resolve-IconPath $v)
    foreach ($slot in $ICON_SLOTS) {
        $S = $slot.Size
        $dib = New-IconDib (Resize-Rgba $images[$S] $S) $S''')

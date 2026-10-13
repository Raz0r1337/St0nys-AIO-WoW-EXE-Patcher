# ============================================================
#  Helfer fuer den Icon-Patch (Programm-Icon der Wow.exe)
#  Nach edit_icon.py von MacWarrior. Sein Script tauscht die Icon-Ressourcen
#  ueber die Windows-API (UpdateResource) aus, was die .rsrc-Sektion neu
#  schreibt. Hier bleibt alles an Ort und Stelle: Die Wow.exe traegt ihr Icon
#  als vier RT_ICON-Bilder (48, 32, 24 und 16 Pixel, je 32 Bit mit
#  Alphakanal) in zwei Sprachvarianten (1024 und 1033), dazu zwei
#  RT_GROUP_ICON-Verzeichnisse. Der Patch ueberschreibt nur die Bilddaten in
#  diesen acht Slots - gleiche Groesse, gleiche Bittiefe, gleicher Platz.
#  Verzeichnisse, Offsets und Dateigroesse bleiben unveraendert.
#  Die Eingabe (ICO mit BMP- oder PNG-Bildern, oder eine PNG-Datei) liest
#  und skaliert der Patcher selbst (Flaechenmittelung), ohne System.Drawing.
# ============================================================
$ICON_SLOTS = @(
    @{ Size = 48; Offsets = @(0x74ED84, 0x75132C) }
    @{ Size = 32; Offsets = @(0x7538D4, 0x75497C) }
    @{ Size = 24; Offsets = @(0x755A24, 0x7563AC) }
    @{ Size = 16; Offsets = @(0x756D34, 0x75719C) }
)

function Get-IconDibLength([int]$S) { return 40 + $S * $S * 4 + [int](([Math]::Floor(($S + 31) / 32)) * 4) * $S }

function Resolve-IconPath([string]$v) {
    $p = $v.Trim().Trim('"')
    if (-not [System.IO.Path]::IsPathRooted($p)) { $p = Join-Path $scriptDir $p }
    return $p
}

function BE32([byte[]]$a, [int]$o) { return ([int64]$a[$o] -shl 24) -bor ([int64]$a[$o + 1] -shl 16) -bor ([int64]$a[$o + 2] -shl 8) -bor [int64]$a[$o + 3] }

# PNG -> @{ W; H; Px = RGBA-Bytes zeilenweise von oben }. Nur nicht-interlaced.
function Read-PngImage([byte[]]$data) {
    $sig = @(0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)
    if ($data.Length -lt 8) { throw 'Keine PNG-Datei.' }
    for ($i = 0; $i -lt 8; $i++) { if ($data[$i] -ne $sig[$i]) { throw 'Keine PNG-Datei.' } }
    $idat = New-Object System.IO.MemoryStream
    $pal = $null; $trns = $null
    $w = 0; $h = 0; $depth = 0; $ctype = 0
    $pos = 8
    while ($pos + 12 -le $data.Length) {
        $len = [int](BE32 $data $pos)
        $type = [System.Text.Encoding]::ASCII.GetString($data, $pos + 4, 4)
        $body = $pos + 8
        if ($body + $len + 4 -gt $data.Length) { throw 'PNG-Datei ist beschaedigt.' }
        switch ($type) {
            'IHDR' {
                $w = [int](BE32 $data $body); $h = [int](BE32 $data ($body + 4))
                $depth = [int]$data[$body + 8]; $ctype = [int]$data[$body + 9]
                if ($data[$body + 12] -ne 0) { throw 'Interlaced PNG wird nicht unterstuetzt.' }
            }
            'PLTE' { $pal = New-Object byte[] $len; [Array]::Copy($data, $body, $pal, 0, $len) }
            'tRNS' { $trns = New-Object byte[] $len; [Array]::Copy($data, $body, $trns, 0, $len) }
            'IDAT' { $idat.Write($data, $body, $len) }
        }
        if ($type -eq 'IEND') { break }
        $pos = $body + $len + 4
    }
    if ($w -le 0 -or $h -le 0 -or $w -gt 1024 -or $h -gt 1024) { throw 'PNG: ungueltige oder zu grosse Abmessungen (max. 1024).' }
    $channels = switch ($ctype) { 0 { 1 } 2 { 3 } 3 { 1 } 4 { 2 } 6 { 4 } default { throw 'PNG: unbekannter Farbtyp.' } }
    if ($depth -notin @(1, 2, 4, 8, 16)) { throw 'PNG: ungueltige Bittiefe.' }
    if ($depth -lt 8 -and $ctype -notin @(0, 3)) { throw 'PNG: ungueltige Bittiefe.' }
    if ($ctype -eq 3 -and $null -eq $pal) { throw 'PNG: Palette fehlt.' }
    # zlib-Kopf (2 Byte) ueberspringen, dann roher Deflate-Strom
    $idat.Position = 2
    $inf = New-Object System.IO.Compression.DeflateStream($idat, [System.IO.Compression.CompressionMode]::Decompress)
    $outMs = New-Object System.IO.MemoryStream
    $inf.CopyTo($outMs); $inf.Dispose()
    $raw = $outMs.ToArray()
    $bitsPP = $channels * $depth
    $rowBytes = [int][Math]::Floor(($w * $bitsPP + 7) / 8)
    $fb = [Math]::Max(1, [int][Math]::Floor($bitsPP / 8))     # Abstand fuer die Filter
    if ($raw.Length -lt ($rowBytes + 1) * $h) { throw 'PNG: Bilddaten unvollstaendig.' }
    # Filter rueckgaengig machen, Ergebnis zeilenweise in $img (ohne Filterbyte)
    $img = New-Object byte[] ($rowBytes * $h)
    $prev = New-Object int[] $rowBytes
    $cur = New-Object int[] $rowBytes
    for ($y = 0; $y -lt $h; $y++) {
        $base = $y * ($rowBytes + 1)
        $ft = [int]$raw[$base]
        $base++
        for ($x = 0; $x -lt $rowBytes; $x++) {
            $v = [int]$raw[$base + $x]
            $a = 0; if ($x -ge $fb) { $a = $cur[$x - $fb] }
            $b = $prev[$x]
            $c = 0; if ($x -ge $fb) { $c = $prev[$x - $fb] }
            switch ($ft) {
                1 { $v += $a }
                2 { $v += $b }
                3 { $v += [int][Math]::Floor(($a + $b) / 2) }
                4 {
                    $p = $a + $b - $c
                    $pa = [Math]::Abs($p - $a); $pb = [Math]::Abs($p - $b); $pc = [Math]::Abs($p - $c)
                    if ($pa -le $pb -and $pa -le $pc) { $v += $a } elseif ($pb -le $pc) { $v += $b } else { $v += $c }
                }
            }
            $cur[$x] = $v -band 0xFF
        }
        for ($x = 0; $x -lt $rowBytes; $x++) { $img[$y * $rowBytes + $x] = [byte]$cur[$x]; $prev[$x] = $cur[$x] }
    }
    # nach RGBA
    $px = New-Object byte[] ($w * $h * 4)
    $maxv = (1 -shl $depth) - 1
    for ($y = 0; $y -lt $h; $y++) {
        $row = $y * $rowBytes
        for ($x = 0; $x -lt $w; $x++) {
            $o = ($y * $w + $x) * 4
            if ($depth -ge 8) {
                $step = [int]($depth / 8)
                $s = $row + $x * $channels * $step
                switch ($ctype) {
                    0 { $g = $img[$s]; $px[$o] = $g; $px[$o + 1] = $g; $px[$o + 2] = $g; $px[$o + 3] = 255
                        if ($trns -and $trns.Length -ge 2 -and $g -eq $trns[1 - ($step - 1)]) { $px[$o + 3] = 0 } }
                    2 { $px[$o] = $img[$s]; $px[$o + 1] = $img[$s + $step]; $px[$o + 2] = $img[$s + 2 * $step]; $px[$o + 3] = 255
                        if ($trns -and $trns.Length -ge 6 -and $px[$o] -eq $trns[$step - 1] -and $px[$o + 1] -eq $trns[2 + $step - 1] -and $px[$o + 2] -eq $trns[4 + $step - 1]) { $px[$o + 3] = 0 } }
                    3 { $idx = [int]$img[$s]; $px[$o] = $pal[3 * $idx]; $px[$o + 1] = $pal[3 * $idx + 1]; $px[$o + 2] = $pal[3 * $idx + 2]
                        $px[$o + 3] = 255; if ($trns -and $idx -lt $trns.Length) { $px[$o + 3] = $trns[$idx] } }
                    4 { $g = $img[$s]; $px[$o] = $g; $px[$o + 1] = $g; $px[$o + 2] = $g; $px[$o + 3] = $img[$s + $step] }
                    6 { $px[$o] = $img[$s]; $px[$o + 1] = $img[$s + $step]; $px[$o + 2] = $img[$s + 2 * $step]; $px[$o + 3] = $img[$s + 3 * $step] }
                }
            } else {
                $bit = $x * $depth
                $val = ([int]$img[$row + ($bit -shr 3)] -shr (8 - $depth - ($bit -band 7))) -band $maxv
                if ($ctype -eq 3) {
                    $px[$o] = $pal[3 * $val]; $px[$o + 1] = $pal[3 * $val + 1]; $px[$o + 2] = $pal[3 * $val + 2]
                    $px[$o + 3] = 255; if ($trns -and $val -lt $trns.Length) { $px[$o + 3] = $trns[$val] }
                } else {
                    $g = [byte][int][Math]::Round($val * 255 / $maxv)
                    $px[$o] = $g; $px[$o + 1] = $g; $px[$o + 2] = $g; $px[$o + 3] = 255
                }
            }
        }
    }
    return @{ W = $w; H = $h; Px = $px }
}

# BMP-Bild aus einer ICO-Datei (BITMAPINFOHEADER, XOR-Bitmap, AND-Maske) -> RGBA
function Read-DibImage([byte[]]$data) {
    if ($data.Length -lt 40 -or (RU32 $data 0) -ne 40) { throw 'ICO: unbekanntes Bitmap-Format.' }
    $w = [int][BitConverter]::ToInt32($data, 4); $h = [int]([BitConverter]::ToInt32($data, 8) / 2)
    $bpp = RU16 $data 14; $comp = RU32 $data 16; $clrUsed = RU32 $data 32
    if ($w -le 0 -or $h -le 0 -or $w -gt 1024 -or $h -gt 1024) { throw 'ICO: ungueltige Abmessungen.' }
    if ($bpp -notin @(1, 4, 8, 16, 24, 32)) { throw "ICO: Bittiefe $bpp wird nicht unterstuetzt." }
    if ($comp -ne 0 -and -not ($comp -eq 3 -and $bpp -ge 16)) { throw 'ICO: komprimierte Bitmaps werden nicht unterstuetzt.' }
    $xorOff = 40
    $pal = $null
    if ($bpp -le 8) {
        $n = [int]$clrUsed; if ($n -le 0) { $n = 1 -shl $bpp }
        $pal = $n; $xorOff += 4 * $n
    } elseif ($comp -eq 3) { $xorOff += 12 }
    $xorRow = [int]([Math]::Floor(($w * $bpp + 31) / 32) * 4)
    $andRow = [int]([Math]::Floor(($w + 31) / 32) * 4)
    $andOff = $xorOff + $xorRow * $h
    $hasMask = ($data.Length -ge $andOff + $andRow * $h)
    if ($data.Length -lt $andOff) { throw 'ICO: Bilddaten unvollstaendig.' }
    $px = New-Object byte[] ($w * $h * 4)
    $alphaUsed = $false
    for ($y = 0; $y -lt $h; $y++) {
        $srcRow = $xorOff + ($h - 1 - $y) * $xorRow
        $maskRow = $andOff + ($h - 1 - $y) * $andRow
        for ($x = 0; $x -lt $w; $x++) {
            $o = ($y * $w + $x) * 4
            $a = 255
            switch ($bpp) {
                32 { $s = $srcRow + $x * 4; $px[$o] = $data[$s + 2]; $px[$o + 1] = $data[$s + 1]; $px[$o + 2] = $data[$s]; $a = $data[$s + 3]; if ($a -ne 0) { $alphaUsed = $true } }
                24 { $s = $srcRow + $x * 3; $px[$o] = $data[$s + 2]; $px[$o + 1] = $data[$s + 1]; $px[$o + 2] = $data[$s] }
                16 { $v = RU16 $data ($srcRow + $x * 2); $px[$o] = [byte]((($v -shr 10) -band 31) * 255 / 31); $px[$o + 1] = [byte]((($v -shr 5) -band 31) * 255 / 31); $px[$o + 2] = [byte](($v -band 31) * 255 / 31) }
                default {
                    $bit = $x * $bpp
                    $idx = ([int]$data[$srcRow + ($bit -shr 3)] -shr (8 - $bpp - ($bit -band 7))) -band ((1 -shl $bpp) - 1)
                    if ($idx -ge $pal) { $idx = 0 }
                    $px[$o] = $data[40 + 4 * $idx + 2]; $px[$o + 1] = $data[40 + 4 * $idx + 1]; $px[$o + 2] = $data[40 + 4 * $idx]
                }
            }
            if ($hasMask -and (($data[$maskRow + ($x -shr 3)] -shr (7 - ($x -band 7))) -band 1) -eq 1) { $px[$o + 3] = 0 } else { $px[$o + 3] = 255 }
            if ($bpp -eq 32) { $px[$o + 3] = $a }
        }
    }
    # 32 Bit ohne genutzten Alphakanal: Transparenz kommt aus der AND-Maske
    if ($bpp -eq 32 -and -not $alphaUsed) {
        for ($y = 0; $y -lt $h; $y++) {
            $maskRow = $andOff + ($h - 1 - $y) * $andRow
            for ($x = 0; $x -lt $w; $x++) {
                $o = ($y * $w + $x) * 4
                if ($hasMask -and (($data[$maskRow + ($x -shr 3)] -shr (7 - ($x -band 7))) -band 1) -eq 1) { $px[$o + 3] = 0 } else { $px[$o + 3] = 255 }
            }
        }
    }
    return @{ W = $w; H = $h; Px = $px }
}

# ICO- oder PNG-Datei lesen. Liefert die Liste der enthaltenen Bilder.
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

# RGBA auf SxS umrechnen: Flaechenmittelung mit vormultipliziertem Alpha.
function Resize-Rgba($img, [int]$S) {
    $w = $img.W; $h = $img.H; $src = $img.Px
    if ($w -eq $S -and $h -eq $S) { return $src }
    $out = New-Object byte[] ($S * $S * 4)
    for ($y = 0; $y -lt $S; $y++) {
        $y0 = [int][Math]::Floor($y * $h / $S); $y1 = [int][Math]::Floor(($y + 1) * $h / $S); if ($y1 -le $y0) { $y1 = $y0 + 1 }
        for ($x = 0; $x -lt $S; $x++) {
            $x0 = [int][Math]::Floor($x * $w / $S); $x1 = [int][Math]::Floor(($x + 1) * $w / $S); if ($x1 -le $x0) { $x1 = $x0 + 1 }
            $sr = 0.0; $sg = 0.0; $sb = 0.0; $sa = 0.0; $n = 0
            for ($sy = $y0; $sy -lt $y1; $sy++) {
                for ($sx = $x0; $sx -lt $x1; $sx++) {
                    $o = ($sy * $w + $sx) * 4
                    $a = [double]$src[$o + 3]
                    $sr += $src[$o] * $a; $sg += $src[$o + 1] * $a; $sb += $src[$o + 2] * $a; $sa += $a; $n++
                }
            }
            $d = ($y * $S + $x) * 4
            if ($sa -gt 0) {
                $out[$d] = [byte][Math]::Round($sr / $sa); $out[$d + 1] = [byte][Math]::Round($sg / $sa); $out[$d + 2] = [byte][Math]::Round($sb / $sa)
                $out[$d + 3] = [byte][Math]::Round($sa / $n)
            }
        }
    }
    return , $out
}

# RGBA (SxS) -> Icon-Bitmap wie in der Wow.exe: BITMAPINFOHEADER, XOR-Bitmap
# (BGRA, Zeilen von unten), AND-Maske (1 Bit, gesetzt = durchsichtig).
function New-IconDib([byte[]]$rgba, [int]$S) {
    $maskRow = [int](([Math]::Floor(($S + 31) / 32)) * 4)
    $b = New-Object byte[] (Get-IconDibLength $S)
    [Array]::Copy([BitConverter]::GetBytes([int32]40), 0, $b, 0, 4)
    [Array]::Copy([BitConverter]::GetBytes([int32]$S), 0, $b, 4, 4)
    [Array]::Copy([BitConverter]::GetBytes([int32](2 * $S)), 0, $b, 8, 4)
    $b[12] = 1; $b[14] = 32
    $xor = 40; $and = 40 + $S * $S * 4
    for ($y = 0; $y -lt $S; $y++) {
        $srcY = $S - 1 - $y
        for ($x = 0; $x -lt $S; $x++) {
            $s = ($srcY * $S + $x) * 4; $d = $xor + ($y * $S + $x) * 4
            $b[$d] = $rgba[$s + 2]; $b[$d + 1] = $rgba[$s + 1]; $b[$d + 2] = $rgba[$s]; $b[$d + 3] = $rgba[$s + 3]
            if ($rgba[$s + 3] -eq 0) { $m = $and + $y * $maskRow + ($x -shr 3); $b[$m] = $b[$m] -bor (0x80 -shr ($x -band 7)) }
        }
    }
    return , $b
}

function Test-ClientIcon([string]$v) {
    if ($v.Trim() -eq '') { return (L 'Pfad zu einer .ico- oder .png-Datei angeben.' 'Enter the path to an .ico or .png file.') }
    $p = Resolve-IconPath $v
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { return (L "Datei nicht gefunden: $p" "File not found: $p") }
    try { [void](Read-IconFile $p) } catch { return $_.Exception.Message }
    return $null
}

function Set-ClientIcon([string]$v) {
    if ($v.Trim() -eq '') {
        # Nur fuer -BuildTable: Slots unveraendert "beschreiben", damit sie in der Tabelle landen.
        foreach ($slot in $ICON_SLOTS) {
            $len = Get-IconDibLength $slot.Size
            foreach ($off in $slot.Offsets) { $b = New-Object byte[] $len; [Array]::Copy($script:f, $off, $b, 0, $len); Patch $off $b }
        }
        return
    }
    $images = Read-IconFile (Resolve-IconPath $v)
    foreach ($slot in $ICON_SLOTS) {
        $S = $slot.Size
        $dib = New-IconDib (Resize-Rgba (Select-IconSource $images $S) $S) $S
        if ($dib.Length -ne (Get-IconDibLength $S)) { throw 'Icon: Bitmap hat die falsche Groesse.' }
        foreach ($off in $slot.Offsets) {
            Assert-Bytes $off ([byte[]](0x28, 0x00, 0x00, 0x00, [byte]$S, 0x00, 0x00, 0x00, [byte](2 * $S), 0x00, 0x00, 0x00, 0x01, 0x00, 0x20, 0x00)) 'Icon'
            Patch $off $dib
        }
    }
}


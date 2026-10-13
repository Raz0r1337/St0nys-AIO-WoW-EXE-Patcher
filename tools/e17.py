# 1. Kopfkommentar: -Select none
R("""#    -Select   <Auswahl>      Auswahlmenue ueberspringen. Erlaubt sind
#                             "saved" (gespeicherte Auswahl), "billy" (Preset
#                             Billy's_Wow.exe = Standard), "all" oder
#                             Nummern/Bereiche wie "1,3,5-8"
""", """#    -Select   <Auswahl>      Auswahlmenue ueberspringen. Erlaubt sind
#                             "saved" (gespeicherte Auswahl), "billy" (Preset
#                             Billy's_Wow.exe = Standard), "all", "none" (alle
#                             Patches zuruecknehmen) oder Nummern/Bereiche
#                             wie "1,3,5-8"
""")
# 2. Add-CodeSection Kommentar
R("""# ============================================================
#  Eigene Code-Sektion fuer kleine Code-Hoehlen
#  In .text gibt es keine freie Luecke mehr, die gross genug und nicht schon
#  von einem anderen Patch belegt ist. Patches mit Code-Hoehle bekommen darum
#  wie HD-Portraits und CameraReforged eine eigene Sektion am Dateiende:
#  Padding bis FileAlignment, Sektion anhaengen, PE-Header anpassen
#  (NumberOfSections, SizeOfImage, neuer Sektionsheader, ausfuehrbar).
#  Liefert @(VA der Sektion, Dateioffset der Sektion).
# ============================================================
""", """# ============================================================
#  Eigene Code-Sektion fuer kleine Code-Hoehlen
#  Wie HD-Portraits und CameraReforged: Padding bis FileAlignment, Sektion
#  am Dateiende anhaengen, PE-Header anpassen (NumberOfSections, SizeOfImage,
#  neuer Sektionsheader, ausfuehrbar, mit -Writable auch beschreibbar).
#  Genutzt vom Doppelsprung (braucht beschreibbaren Speicher) und als
#  Ausweichmodus von WorldFrame-Absturzfix und NPC-Ausblenden, wenn der
#  Slider-Patch die Luecke in .text belegt (siehe Get-CodeCave).
#  Liefert @(VA der Sektion, Dateioffset der Sektion).
# ============================================================
""")
# 3. Add-HdPortraits: Platz im Header pruefen
R("""    $hoff = $sectBase + 40 * $nsec
    $sh = New-Object byte[] 40
    [Array]::Copy([System.Text.Encoding]::ASCII.GetBytes('.hdp'), 0, $sh, 0, 4)
""", """    $hoff = $sectBase + 40 * $nsec
    if (($hoff + 40) -gt (RU32 $script:f ($sectBase + 20))) { throw 'HD-Portraits: kein Platz im PE-Header fuer einen weiteren Sektionseintrag.' }
    $sh = New-Object byte[] 40
    [Array]::Copy([System.Text.Encoding]::ASCII.GetBytes('.hdp'), 0, $sh, 0, 4)
""")
# 4. Wasserzeichen: Erkennung ueber den festen Anfang des Textes
R("""$WATERMARK_OFF = 0x72DE20
$WATERMARK = 'Patched with St0nys AIO WoW.exe Patcher by St0ny (Raz0r1337) - https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher'
""", """$WATERMARK_OFF = 0x72DE20
$WATERMARK = 'Patched with St0nys AIO WoW.exe Patcher by St0ny (Raz0r1337) - https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher'
# Erkannt wird nur dieser Anfang - der Rest (Link) darf sich zwischen Versionen aendern.
$WATERMARK_MARK = 'Patched with St0nys AIO WoW.exe Patcher'
""")
R("""function Test-Watermark([byte[]]$data) {
    $b = [System.Text.Encoding]::ASCII.GetBytes($WATERMARK)
""", """function Test-Watermark([byte[]]$data) {
    $b = [System.Text.Encoding]::ASCII.GetBytes($WATERMARK_MARK)
""")
# 5. BuildTable: PE-Header generisch, kein Non-ASCII, pe ohne Warnung
R("""#  Patch alle Stellen im Original, die er beschreibt. Stellen, die nur ein
#  Patch beschreibt, bekommen die Markierung 1 (fuer die Erkennung).
#  Das Ergebnis ersetzt den Block $ORIGINAL_TABLE in diesem Skript.
# ============================================================
""", """#  Patch alle Stellen im Original, die er beschreibt. Stellen, die nur ein
#  Patch beschreibt, bekommen die Markierung 1 (fuer die Erkennung).
#  Dazu kommt der Pseudo-Eintrag "pe": NumberOfSections, SizeOfImage und die
#  freien Sektionsheader-Slots. Welcher Patch seine Sektion in welchem Slot
#  anlegt, haengt von der Kombination ab - so werden alle Slots unabhaengig
#  davon zurueckgesetzt und gelten fuer keinen Patch als eigene Stelle.
#  Das Ergebnis ersetzt den Block $ORIGINAL_TABLE in diesem Skript.
# ============================================================
""")
R("""        $start = $script:writes.Count
        Add-Watermark
        Add-BuildRanges $ranges 'watermark' $start $orig.Length
    }
""", """        $start = $script:writes.Count
        Add-Watermark
        Add-BuildRanges $ranges 'watermark' $start $orig.Length
    }
    # PE-Header: NumberOfSections, SizeOfImage, freie Sektionsheader-Slots bis zu den ersten Rohdaten
    $e = RU32 $orig 0x3C
    $nsec = RU16 $orig ($e + 6)
    $sectBase = $e + 24 + (RU16 $orig ($e + 20))
    $firstRaw = RU32 $orig ($sectBase + 20)
    for ($i = 1; $i -lt $nsec; $i++) { $r = RU32 $orig ($sectBase + 40 * $i + 20); if ($r -lt $firstRaw) { $firstRaw = $r } }
    $ranges['pe'] = New-Object System.Collections.Generic.List[object]
    $ranges['pe'].Add(@(($e + 6), ($e + 8)))
    $ranges['pe'].Add(@(($e + 24 + 56), ($e + 24 + 60)))
    $ranges['pe'].Add(@(($sectBase + 40 * $nsec), $firstRaw))
""")
R("""    foreach ($id in (@($allIds) + 'watermark')) {
        if (-not $merged.ContainsKey($id)) { continue }
""", """    foreach ($id in (@($allIds) + 'watermark' + 'pe')) {
        if (-not $merged.ContainsKey($id)) { continue }
""")
R("""        if ($own -eq 0) { Write-Host "  WARNUNG: $id hat keine eigene Stelle und ist nicht erkennbar." }
    }
""", """        if ($own -eq 0 -and $id -ne 'pe') { Write-Host "  WARNUNG: $id hat keine eigene Stelle und ist nicht erkennbar." }
    }
""")
R("""    $src = [System.IO.File]::ReadAllText($scriptPath)
    $a = $src.IndexOf('# BEGIN ORIGINAL-BYTES' + "`r`n")
""", """    $src = [System.IO.File]::ReadAllText($scriptPath)
    if ($src -match '[^\\x00-\\x7F]') { Write-Host 'BuildTable: Skript enthaelt Nicht-ASCII-Zeichen, Abbruch (es wird als ASCII zurueckgeschrieben).'; exit 1 }
    $a = $src.IndexOf('# BEGIN ORIGINAL-BYTES' + "`r`n")
""")
# 6. Kategorie-Kommentar
R("""    # --- Fenster & Maus ---
""", """    # --- Fenster, Maus & Kamera ---
""")
# 7. Texte: Backup, Zustand
R("""        BackupSkip    = 'Kein neues Backup: Die Wow.exe ist bereits gepatcht, die Original-Bytes stehen in patcher_state.ini.'
""", """        BackupSkip    = 'Kein neues Backup noetig: Wow.exe.BAK ist vorhanden und bleibt unveraendert.'
        BackupRedo    = 'Wow.exe.BAK fehlte und wurde aus dem rekonstruierten Original neu angelegt: {0}'
""")
R("""        BackupSkip    = 'No new backup: Wow.exe is already patched, the original bytes are stored in patcher_state.ini.'
""", """        BackupSkip    = 'No new backup needed: Wow.exe.BAK exists and stays untouched.'
        BackupRedo    = 'Wow.exe.BAK was missing and has been recreated from the reconstructed original: {0}'
""")
R("""        StateFail     = '[FEHLER] Konnte patcher_state.ini nicht schreiben:'
""", "")
R("""        StateFail     = '[ERROR] Could not write patcher_state.ini:'
""", "")
# 8. Backup-Schritt
R("""# --- 5. Backup (nur vom Original, eine vorhandene Sicherung bleibt sonst stehen) ---
if ($patchedMode) {
    Say (T 'BackupSkip')
} else {
    try {
        Copy-Item -LiteralPath $file -Destination $backup -Force
    } catch {
        Say (T 'BackupFail') 'Red'
        Say $_.Exception.Message 'Red'
        Exit-Patcher 1
    }
    Say (T 'BackupOk' $backup)
}
""", """# --- 5. Backup ---
# Wow.exe.BAK ist immer das Original: beim ersten Patchen eine Kopie der
# Datei, bei einer gepatchten Wow.exe bleibt eine vorhandene Sicherung stehen;
# fehlt sie (z.B. Exe von einem anderen Rechner), wird sie aus dem
# rekonstruierten Original ($f, per SHA256 geprueft) neu angelegt.
$bakExists = Test-Path -LiteralPath $backup -PathType Leaf
if ($patchedMode -and $bakExists) {
    Say (T 'BackupSkip')
} else {
    try {
        if ($patchedMode) { [System.IO.File]::WriteAllBytes($backup, $f) } else { Copy-Item -LiteralPath $file -Destination $backup -Force }
    } catch {
        Say (T 'BackupFail') 'Red'
        Say $_.Exception.Message 'Red'
        Exit-Patcher 1
    }
    if ($patchedMode) { Say (T 'BackupRedo' $backup) } else { Say (T 'BackupOk' $backup) }
}
""")
# 9. Zustandsdatei: Schreibfehler nur noch Warnung
R("""    if ($null -eq (Restore-FromTable $f)) { Write-Host ''; Say (T 'TableWarn') 'Yellow' }
    $stateError = Write-State $stateTmp (Get-Sha256 $f) $origBytes.Length $chosenIds $VALUES $undo
    if ($stateError) {
        Write-Host ''
        Say (T 'StateFail') 'Red'
        Say $stateError 'Red'
        Say (T 'NotWritten') 'Red'
        Exit-Patcher 1
    }
}
""", """    if ($null -eq (Restore-FromTable $f)) { Write-Host ''; Say (T 'TableWarn') 'Yellow' }
    # Die Zustandsdatei ist nur eine Beschleunigung - ein Schreibfehler
    # verhindert das Patchen nicht (Hinweis am Ende).
    $stateWarn = Write-State $stateTmp (Get-Sha256 $f) $origBytes.Length $chosenIds $VALUES $undo
}
""")
R("""# --- 9. Zustand uebernehmen (ohne Patches ist die Wow.exe original, dann weg damit) ---
$stateWarn = $null
try {
    if ($total -gt 0) {
""", """# --- 9. Zustand uebernehmen (ohne Patches ist die Wow.exe original, dann weg damit) ---
try {
    if ($total -gt 0 -and $stateWarn) {
        # .tmp konnte nicht geschrieben werden - alten Zustand nicht stehen lassen
        if (Test-Path -LiteralPath $stateFile -PathType Leaf) { [System.IO.File]::Delete($stateFile) }
    } elseif ($total -gt 0) {
""")
R("""# --- 7. Zustand vorbereiten ---
# Erst die Original-Bytes sammeln und pruefen, dass sich das Ergebnis damit
# exakt zum Original zuruecknehmen laesst. Der neue Zustand geht zuerst in
# eine .tmp-Datei und ersetzt den alten erst, wenn die Wow.exe geschrieben ist.
$stateTmp = $stateFile + '.tmp'
""", """# --- 7. Zustand vorbereiten ---
# Erst die Original-Bytes sammeln und pruefen, dass sich das Ergebnis damit
# exakt zum Original zuruecknehmen laesst. Der neue Zustand geht zuerst in
# eine .tmp-Datei und ersetzt den alten erst, wenn die Wow.exe geschrieben ist.
$stateTmp = $stateFile + '.tmp'
$stateWarn = $null
""")
# 10. "Keine Aenderung" nur, wenn ueberhaupt Patches gewaehlt sind (sonst Original
#     schreiben - z.B. wenn nur noch das Wasserzeichen in der Exe steht)
R("""    foreach ($id in $appliedIds) { if ($chosenIds -notcontains $id) { $removed += $id } }
    if ($added.Count + $changed.Count + $removed.Count -eq 0) {
        Say (T 'NoChange') 'Green'
        Exit-Patcher 0
    }
""", """    foreach ($id in $appliedIds) { if ($chosenIds -notcontains $id) { $removed += $id } }
    if ($added.Count + $changed.Count + $removed.Count -eq 0 -and $chosen.Count -gt 0) {
        Say (T 'NoChange') 'Green'
        Exit-Patcher 0
    }
""")
# 11. Wertaenderung: alter Wert unbekannt -> "?"
R("""        foreach ($p in $changed) { Say "  ~ $(PatchName $p): $($state.Values[$p.Id]) -> $($VALUES[$p.Id])" 'Green' }
""", """        foreach ($p in $changed) {
            $old = $state.Values[$p.Id]; if (-not $old) { $old = '?' }
            Say "  ~ $(PatchName $p): $old -> $($VALUES[$p.Id])" 'Green'
        }
""")

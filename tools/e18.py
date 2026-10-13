import re
# --- Backup: .ORI = Original, .BAK = vorherige Wow.exe ---
R("""#    4. Bestaetigen, Backup Wow.exe.BAK anlegen, patchen
""", """#    4. Bestaetigen, Backup anlegen (Wow.exe.ORI = Original beim ersten
#       Patchen, danach Wow.exe.BAK = vorherige Wow.exe), patchen
""")
R("""$backup = $file + '.BAK'
""", """$backup = $file + '.ORI'       # Original, wird beim ersten Patchen angelegt
$backupPrev = $file + '.BAK'   # vorherige (gepatchte) Wow.exe bei jedem weiteren Lauf
""")
R("""        Welcome4      = 'Beim ersten Patchen wird ein Backup als Wow.exe.BAK erstellt.'
""", """        Welcome4      = 'Beim ersten Patchen wird das Original als Wow.exe.ORI gesichert, danach die vorherige Wow.exe als Wow.exe.BAK.'
""")
R("""        Welcome4      = 'The first patch run creates a backup as Wow.exe.BAK.'
""", """        Welcome4      = 'The first patch run saves the original as Wow.exe.ORI, later runs save the previous Wow.exe as Wow.exe.BAK.'
""")
R("""        BackupOk      = 'Backup der Wow.exe erfolgreich erstellt: {0}'
        BackupSkip    = 'Kein neues Backup noetig: Wow.exe.BAK ist vorhanden und bleibt unveraendert.'
        BackupRedo    = 'Wow.exe.BAK fehlte und wurde aus dem rekonstruierten Original neu angelegt: {0}'
""", """        BackupOk      = 'Original gesichert als: {0}'
        BackupSkip    = 'Wow.exe.ORI (Original) ist vorhanden und bleibt unveraendert.'
        BackupRedo    = 'Wow.exe.ORI fehlte und wurde aus dem rekonstruierten Original neu angelegt: {0}'
        BackupPrev    = 'Bisherige Wow.exe gesichert als: {0}'
""")
R("""        BackupOk      = 'Backup of Wow.exe created successfully: {0}'
        BackupSkip    = 'No new backup needed: Wow.exe.BAK exists and stays untouched.'
        BackupRedo    = 'Wow.exe.BAK was missing and has been recreated from the reconstructed original: {0}'
""", """        BackupOk      = 'Original saved as: {0}'
        BackupSkip    = 'Wow.exe.ORI (original) exists and stays untouched.'
        BackupRedo    = 'Wow.exe.ORI was missing and has been recreated from the reconstructed original: {0}'
        BackupPrev    = 'Previous Wow.exe saved as: {0}'
""")
R("""# Hinweis auf Wow.exe.BAK, wenn sie das Original enthaelt.
function Show-BakHint {
    try {
        if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) { return }
        if ((Get-Sha256 ([System.IO.File]::ReadAllBytes($backup))) -ne $EXPECTED_HASH) { return }
        Write-Host ''
        Say (T 'BakHint' $backup) 'Yellow'
    } catch { }
}
""", """# Hinweis auf Wow.exe.ORI bzw. Wow.exe.BAK, wenn eine davon das Original enthaelt
# (.BAK war in aelteren Versionen das Original).
function Show-BakHint {
    foreach ($b in @($backup, $backupPrev)) {
        try {
            if (-not (Test-Path -LiteralPath $b -PathType Leaf)) { continue }
            if ((Get-Sha256 ([System.IO.File]::ReadAllBytes($b))) -ne $EXPECTED_HASH) { continue }
            Write-Host ''
            Say (T 'BakHint' $b) 'Yellow'
            return
        } catch { }
    }
}
""")
R("""# --- 5. Backup ---
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
""", """# --- 5. Backup ---
# Wow.exe.ORI ist immer das Original: beim ersten Patchen eine Kopie der
# Datei. Bei einer gepatchten Wow.exe bleibt es stehen; fehlt es (z.B. Exe von
# einem anderen Rechner), wird es aus dem rekonstruierten Original ($f, per
# SHA256 geprueft) neu angelegt - VOR dem .BAK, falls dort noch ein Original
# aus einer aelteren Patcher-Version liegt. Danach wird die bisherige
# (gepatchte) Wow.exe als Wow.exe.BAK gesichert, man kann also immer einen
# Schritt zurueck.
try {
    if (-not $patchedMode) {
        Copy-Item -LiteralPath $file -Destination $backup -Force
        Say (T 'BackupOk' $backup)
    } else {
        if (Test-Path -LiteralPath $backup -PathType Leaf) {
            Say (T 'BackupSkip')
        } else {
            [System.IO.File]::WriteAllBytes($backup, $f)
            Say (T 'BackupRedo' $backup)
        }
        Copy-Item -LiteralPath $file -Destination $backupPrev -Force
        Say (T 'BackupPrev' $backupPrev)
    }
} catch {
    Say (T 'BackupFail') 'Red'
    Say $_.Exception.Message 'Red'
    Exit-Patcher 1
}
""")
# --- Bann-Hinweis fuer Anti-Cheat-Patches ---
R("""#    GrowsExe - optional: $true, wenn der Patch immer eine Sektion anhaengt und
#            die Wow.exe damit groesser macht (erzeugt einen Bann-Hinweis)
""", """#    GrowsExe - optional: $true, wenn der Patch immer eine Sektion anhaengt und
#            die Wow.exe damit groesser macht (erzeugt einen Bann-Hinweis)
#    BanRisk - optional: $true, wenn Server mit Anti-Cheat den Patch als Cheat
#            oder Botting werten koennen (erzeugt einen Bann-Hinweis)
""")
R("""        GrowHead      = 'HINWEIS: Diese Patches haengen eine Sektion an und machen die Wow.exe groesser:'
        GrowBan       = 'Viele Server tolerieren eine veraenderte Groesse der Wow.exe nicht - das kann zu einem Bann fuehren!'
""", """        GrowHead      = 'HINWEIS: Diese Patches haengen eine Sektion an und machen die Wow.exe groesser:'
        GrowBan       = 'Viele Server tolerieren eine veraenderte Groesse der Wow.exe nicht - das kann zu einem Bann fuehren!'
        CheatHead     = 'HINWEIS: Diese Patches koennen von Servern mit Anti-Cheat als Cheat oder Botting gewertet werden:'
        CheatBan      = 'Das kann zu einem Bann fuehren - nur auf Servern nutzen, die das erlauben!'
""")
R("""        GrowHead      = 'NOTE: These patches append a section and make Wow.exe larger:'
        GrowBan       = 'Many servers do not tolerate a changed size of Wow.exe - this can lead to a ban!'
""", """        GrowHead      = 'NOTE: These patches append a section and make Wow.exe larger:'
        GrowBan       = 'Many servers do not tolerate a changed size of Wow.exe - this can lead to a ban!'
        CheatHead     = 'NOTE: Servers with anti-cheat may treat these patches as cheating or botting:'
        CheatBan      = 'This can lead to a ban - only use them on servers that allow it!'
""")
R("""$grow = @()
foreach ($p in $chosen) { if ($p.GrowsExe) { $grow += PatchName $p } }
if ($grow.Count -gt 0) {
    Write-Host ''
    Say (T 'GrowHead') 'Yellow'
    foreach ($m in $grow) { Say "  - $m" 'Yellow' }
    Say (T 'GrowBan') 'Red'
}
""", """$cheat = @()
foreach ($p in $chosen) { if ($p.BanRisk) { $cheat += PatchName $p } }
if ($cheat.Count -gt 0) {
    Write-Host ''
    Say (T 'CheatHead') 'Yellow'
    foreach ($m in $cheat) { Say "  - $m" 'Yellow' }
    Say (T 'CheatBan') 'Red'
}
$grow = @()
foreach ($p in $chosen) { if ($p.GrowsExe) { $grow += PatchName $p } }
if ($grow.Count -gt 0) {
    Write-Host ''
    Say (T 'GrowHead') 'Yellow'
    foreach ($m in $grow) { Say "  - $m" 'Yellow' }
    Say (T 'GrowBan') 'Red'
}
""")
# Notes und BanRisk-Feld
R("""    @{ Id = 'luaunlock'; Cat = 'modding'; On = $false
""", """    @{ Id = 'luaunlock'; Cat = 'modding'; On = $false; BanRisk = $true
""")
R("""       NoteDe = 'kann als Botting gewertet werden'
       NoteEn = 'may be treated as botting'
""", """       NoteDe = 'kann als Botting gewertet werden - Bann-Gefahr'
       NoteEn = 'may be treated as botting - ban risk'
""")
for pid in ('climb', 'jump', 'airforward', 'airlateral', 'airturn'):
    R(f"""    @{{ Id = '{pid}'; Cat = 'gameplay'; On = $false
""", f"""    @{{ Id = '{pid}'; Cat = 'gameplay'; On = $false; BanRisk = $true
""")
R("""    @{ Id = 'doublejump'; Cat = 'gameplay'; On = $false; GrowsExe = $true
""", """    @{ Id = 'doublejump'; Cat = 'gameplay'; On = $false; GrowsExe = $true; BanRisk = $true
""")
s = s.replace("""       NoteDe = 'kann vom Server als Cheat erkannt werden'
       NoteEn = 'may be detected as cheating by the server'
""", """       NoteDe = 'kann vom Server als Cheat erkannt werden - Bann-Gefahr'
       NoteEn = 'may be detected as cheating by the server - ban risk'
""")
R("""       NoteDe = 'kann vom Server als Cheat erkannt werden; Exe wird groesser - Bann-Gefahr'
       NoteEn = 'may be detected as cheating by the server; exe grows - ban risk'
""", """       NoteDe = 'kann vom Server als Cheat erkannt werden, Exe wird groesser - Bann-Gefahr'
       NoteEn = 'may be detected as cheating by the server, exe grows - ban risk'
""")
# --- Nr. 48: kostet Leistung ---
R("""    @{ Id = 'cat0'; Cat = 'graphics'; On = $false
       Author = 'St0ny'
       De = 'GameObject Sichtweite: Cat 0 von 30 auf 50 Yards'
       En = 'GameObject view distance: Cat 0 from 30 to 50 yards'
""", """    @{ Id = 'cat0'; Cat = 'graphics'; On = $false
       Author = 'St0ny'
       De = 'GameObject Sichtweite: Cat 0 von 30 auf 50 Yards'
       En = 'GameObject view distance: Cat 0 from 30 to 50 yards'
       NoteDe = 'kostet Leistung, mehr Kleinkram sichtbar'
       NoteEn = 'costs performance, more small objects visible'
""")

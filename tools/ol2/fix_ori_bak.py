# Nr. 4: alte Sprungstelle in die Bytetabelle; fehlende Wow.exe.ORI/.BAK schon beim Start anlegen.
# Aufruf: fix_ori_bak.py <Worktree>  (st0ny-dev oder st0ny-main, Skript + README DE/EN + PATCHES DE/EN)
import sys
w = sys.argv[1]
def edit(p, pairs, crlf=False):
    raw = open(w + '/' + p, 'rb').read()
    if crlf: assert raw.count(b'\r\n') == raw.count(b'\n')
    s = raw.decode('ascii' if crlf else 'utf-8').replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    if crlf: open(w + '/' + p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
    else: open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

edit('apply_patches.ps1', [
# --- Nr. 4: alte Stelle mitschreiben ---
("""    Patch $loc[1] $c.ToArray()
    Patch ($HOOK_VA - 0x400C00) ([byte[]](Get-Rel32 @(0xE9) $HOOK_VA $CAVE))
}
""", """    Patch $loc[1] $c.ToArray()
    Patch ($HOOK_VA - 0x400C00) ([byte[]](Get-Rel32 @(0xE9) $HOOK_VA $CAVE))
    # Die Fassung bis 9.10.2026 sprang schon bei VA 0x81D51B ab (6 Byte, jae).
    # Die Stelle bleibt unveraendert, wird aber mit ihren Original-Bytes
    # geschrieben, damit sie in der Original-Byte-Tabelle steht: So erkennt der
    # Patcher auch Exes mit der alten Fassung und kann sie zuruecknehmen.
    Assert-Bytes 0x41C91B @(0x0F, 0x83, 0x4D, 0x01, 0x00, 0x00) 'WorldFrame-Absturzfix'
    Patch 0x41C91B @(0x0F, 0x83, 0x4D, 0x01, 0x00, 0x00)
}
"""),
# --- Texte ---
("""        BackupPrev    = 'Bisherige Wow.exe gesichert als: {0}'
""", """        BackupPrev    = 'Bisherige Wow.exe gesichert als: {0}'
        BakRedo       = 'Wow.exe.BAK fehlte - die aktuelle Wow.exe wurde als Backup gesichert: {0}'
        BackupWarn    = 'HINWEIS: Sicherung konnte nicht angelegt werden: {0}'
"""),
("""        BackupPrev    = 'Previous Wow.exe saved as: {0}'
""", """        BackupPrev    = 'Previous Wow.exe saved as: {0}'
        BakRedo       = 'Wow.exe.BAK was missing - the current Wow.exe has been saved as the backup: {0}'
        BackupWarn    = 'NOTE: Could not create the backup: {0}'
"""),
# --- BAK-Bytes behalten (fuer spaetere Pruefungen nicht noetig, Hash reicht) / Sicherungen beim Start ---
("""# Ohne verwendbare Wow.exe geht es nur ueber eine Sicherung weiter - ohne
# Rueckfragen (-Unattended) oder ohne Sicherung ist hier Schluss.
""", """# Fehlende Sicherungen gleich anlegen, wie beim Patchen - auch wenn danach
# nichts gepatcht wird: Wow.exe.ORI aus dem Original (gelesen oder aus der
# gepatchten Exe zurueckgerechnet und per SHA256 geprueft), bei einer
# gepatchten Wow.exe ausserdem Wow.exe.BAK als Kopie ihres jetzigen Stands.
# Vorhandene Sicherungen bleiben unangetastet.
if ($haveExe -and -not $broken) {
    $made = $false
    if (-not $oriFile) {
        try {
            [System.IO.File]::WriteAllBytes($backup, $f)
            if ($patchedMode) { Say (T 'BackupRedo' $backup) } else { Say (T 'BackupOk' $backup) }
            $oriFile = $backup; $oriOk = $true; $made = $true
        } catch { Say (T 'BackupWarn' $_.Exception.Message) 'Yellow' }
    }
    if ($patchedMode -and -not $bakFile) {
        try {
            [System.IO.File]::Copy($file, $backupPrev, $false)
            Say (T 'BakRedo' $backupPrev)
            $bakFile = $backupPrev; $bakOk = $true; $bakHash = $hash; $made = $true
        } catch { Say (T 'BackupWarn' $_.Exception.Message) 'Yellow' }
    }
    if ($made) { Write-Host '' }
}

# Ohne verwendbare Wow.exe geht es nur ueber eine Sicherung weiter - ohne
# Rueckfragen (-Unattended) oder ohne Sicherung ist hier Schluss.
"""),
# --- beim Patchen: vorhandenes (oder eben angelegtes) Original nicht nochmal kopieren ---
("""    } elseif (-not $patchedMode) {
        Copy-Item -LiteralPath $file -Destination $backup -Force
        Say (T 'BackupOk' $backup)
    } else {
        if (Test-Path -LiteralPath $backup -PathType Leaf) {
""", """    } elseif (-not $patchedMode) {
        if ($oriOk) {
            Say (T 'BackupSkip')
        } else {
            Copy-Item -LiteralPath $file -Destination $backup -Force
            Say (T 'BackupOk' $backup)
        }
    } else {
        if ($oriFile -or (Test-Path -LiteralPath $backup -PathType Leaf)) {
"""),
("""# Wow.exe.ORI ist immer das Original: beim ersten Patchen eine Kopie der
# Datei. Bei einer gepatchten Wow.exe bleibt es stehen; fehlt es (z.B. Exe von
# einem anderen Rechner), wird es aus dem rekonstruierten Original ($f, per
# SHA256 geprueft) neu angelegt - VOR dem .BAK, falls dort noch ein Original
# aus einer aelteren Patcher-Version liegt. Danach wird die bisherige
# (gepatchte) Wow.exe als Wow.exe.BAK gesichert, man kann also immer einen
# Schritt zurueck.
""", """# Wow.exe.ORI ist immer das Original: beim ersten Patchen eine Kopie der
# Datei. Bei einer gepatchten Wow.exe bleibt es stehen; fehlt es (z.B. Exe von
# einem anderen Rechner), wird es aus dem rekonstruierten Original ($f, per
# SHA256 geprueft) neu angelegt - VOR dem .BAK, falls dort noch ein Original
# aus einer aelteren Patcher-Version liegt. Danach wird die bisherige
# (gepatchte) Wow.exe als Wow.exe.BAK gesichert, man kann also immer einen
# Schritt zurueck. Fehlende Sicherungen legt der Patcher meist schon beim
# Start an (siehe oben); dann bleibt Wow.exe.ORI hier stehen.
"""),
], crlf=True)

edit('docs/README.de.md', [
("""9. Backup: Beim ersten Patchen wird das Original als `Wow.exe.ORI` gesichert,
   bei jedem weiteren Lauf die bisherige `Wow.exe` als `Wow.exe.BAK`.
""", """9. Backup: Beim ersten Patchen wird das Original als `Wow.exe.ORI` gesichert,
   bei jedem weiteren Lauf die bisherige `Wow.exe` als `Wow.exe.BAK`. Fehlende
   Sicherungen legt der Patcher schon nach der Prüfung in Schritt 4 an, auch
   wenn danach nichts gepatcht wird (siehe
   [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen)).
"""),
("""- `Wow.exe.ORI` bleibt bei weiteren Läufen unangetastet und ist immer das
  Original. Fehlt es, legt der Patcher es aus dem rekonstruierten Original neu
  an. Zusätzlich sichert er bei jedem weiteren Lauf die bisherige `Wow.exe` als
  `Wow.exe.BAK` – ein Schritt zurück ist also immer möglich.
""", """- `Wow.exe.ORI` bleibt bei weiteren Läufen unangetastet und ist immer das
  Original. Zusätzlich sichert der Patcher bei jedem weiteren Lauf die bisherige
  `Wow.exe` als `Wow.exe.BAK` – ein Schritt zurück ist also immer möglich.
- **Fehlende Sicherungen** legt der Patcher gleich beim Start an, auch wenn
  danach nichts gepatcht wird – etwa wenn du eine gepatchte `Wow.exe` in einen
  neuen Patcher-Ordner kopierst: `Wow.exe.ORI` aus dem Original (bei einer
  gepatchten `Wow.exe` zurückgerechnet und per SHA256 geprüft) und bei einer
  gepatchten `Wow.exe` ihren jetzigen Stand als `Wow.exe.BAK`. Vorhandene
  Sicherungen bleiben unangetastet.
"""),
])
edit('docs/README.md', [
("""9. Backup: on the first patch run the original is saved as `Wow.exe.ORI`, on
   every later run the previous `Wow.exe` is saved as `Wow.exe.BAK`.
""", """9. Backup: on the first patch run the original is saved as `Wow.exe.ORI`, on
   every later run the previous `Wow.exe` is saved as `Wow.exe.BAK`. Missing
   backups are created right after the check in step 4, even if nothing is
   patched afterwards (see
   [Changing or removing patches](#changing-or-removing-patches)).
"""),
])
print('ok')

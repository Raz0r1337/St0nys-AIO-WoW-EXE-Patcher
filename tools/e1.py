R("""$settingsFile = Join-Path $scriptDir 'patcher_selection.ini'
""", """$settingsFile = Join-Path $scriptDir 'patcher_selection.ini'
$stateFile = Join-Path $scriptDir 'patcher_state.ini'
""")
R("""# Datei-Inhalt, wird einmal gelesen, im Speicher gepatcht und einmal geschrieben
$f = $null

function Patch([int64]$offset, [byte[]]$bytes) {
    [System.Array]::Copy($bytes, 0, $script:f, $offset, $bytes.Length)
}
""", """# Datei-Inhalt, wird einmal gelesen, im Speicher gepatcht und einmal geschrieben
$f = $null

# Jeder Schreibzugriff ins Original geht ueber Patch() und wird als
# Offset/Laenge-Paar mitgeschrieben. Daraus entsteht nach dem Patchen die
# Liste der Original-Bytes, mit der sich die Patches wieder zuruecknehmen
# lassen (siehe patcher_state.ini). Angehaengte Sektionen liegen hinter dem
# Ende des Originals und fallen beim Zuruecknehmen einfach weg.
$writes = New-Object System.Collections.Generic.List[int64]

function Patch([int64]$offset, [byte[]]$bytes) {
    [System.Array]::Copy($bytes, 0, $script:f, $offset, $bytes.Length)
    $script:writes.Add($offset)
    $script:writes.Add($bytes.Length)
}
""")
# --- Texte DE ---
R("""        Welcome4      = 'Ein Backup wird automatisch als Wow.exe.BAK erstellt.'
""", """        Welcome4      = 'Beim ersten Patchen wird ein Backup als Wow.exe.BAK erstellt.'
        Welcome5      = 'Eingespielte Patches lassen sich spaeter wieder abwaehlen - bis zurueck zum Original.'
""")
R("""        HashBad2      = '         Sie wurde bereits gepatcht oder ist eine andere Version.'
        Expected      = 'Erwartet:  {0}'
        Found         = 'Gefunden:  {0}'
        HashBad3      = 'Bitte eine unmodifizierte Wow.exe verwenden.'
        HashOk        = '[OK] Wow.exe ist original und unmodifiziert.'
""", """        HashBad2      = '         Sie wurde bereits gepatcht (anderes Tool, alte Patcher-Version) oder ist eine andere Version.'
        HashBad3      = 'Beim ersten Start wird eine unmodifizierte Wow.exe benoetigt.'
        HashBadState1 = '[FEHLER] Die Wow.exe ist weder das Original noch die zuletzt von diesem Patcher erzeugte Datei.'
        HashBadState2 = '         Sie wurde seitdem veraendert (anderes Tool, Client-Update o.ae.).'
        HashBadState3 = 'Bitte die zuletzt gepatchte oder eine unmodifizierte Wow.exe verwenden.'
        Expected      = 'Original:  {0}'
        ExpectedLast  = 'Zuletzt:   {0}'
        Found         = 'Gefunden:  {0}'
        BakHint       = 'Tipp: {0} ist die originale Wow.exe. Zurueck nach Wow.exe kopieren und den Patcher neu starten.'
        HashOk        = '[OK] Wow.exe ist original und unmodifiziert.'
        HashKnown     = '[OK] Wow.exe ist die zuletzt von diesem Patcher erzeugte Datei ({0} Patches aktiv).'
        RevertOk      = '[OK] Original aus patcher_state.ini rekonstruiert und per SHA256 geprueft.'
        StateBroken1  = '[FEHLER] patcher_state.ini passt zur Wow.exe, das Original laesst sich daraus aber nicht'
        StateBroken2  = '         wiederherstellen (Datei beschaedigt oder von Hand geaendert?).'
""")
R("""        MenuHelp3     = 'ENTER = Auswahl uebernehmen, speichern und weiter'
        SavedLoaded   = 'Deine gespeicherte Auswahl vom letzten Mal wurde geladen.'
""", """        MenuHelp3     = 'ENTER = Auswahl uebernehmen, speichern und weiter'
        MenuHelp4     = 'O = Original wiederherstellen (alle Patches zuruecknehmen)'
        SavedLoaded   = 'Deine gespeicherte Auswahl vom letzten Mal wurde geladen.'
        AppliedLoaded = 'Ausgewaehlt sind die Patches, die gerade in der Wow.exe stecken. Abwaehlen nimmt einen Patch zurueck.'
        MarkNew       = '(neu)'
        MarkRemove    = '(wird zurueckgenommen)'
""")
R("""        BadSelect     = '[FEHLER] Ungueltiger Wert fuer -Select: {0}'
        Summary       = 'Folgende {0} Patches werden eingespielt:'
""", """        BadSelect     = '[FEHLER] Ungueltiger Wert fuer -Select: {0}'
        Summary       = 'Folgende {0} Patches werden eingespielt:'
        SumAdd        = 'Neu einspielen ({0}):'
        SumChange     = 'Wert aendern ({0}):'
        SumRemove     = 'Zuruecknehmen ({0}):'
        SumKeep       = 'Bleiben unveraendert aktiv: {0}'
        SumOriginal   = 'Danach ist die Wow.exe wieder die originale Datei.'
        NoChange      = 'Keine Aenderung gegenueber der aktuellen Wow.exe - es gibt nichts zu tun.'
        AlreadyOrig   = 'Die Wow.exe ist bereits original - es gibt nichts zurueckzunehmen.'
""")
R("""        BackupOk      = 'Backup der Wow.exe erfolgreich erstellt: {0}'
""", """        BackupOk      = 'Backup der Wow.exe erfolgreich erstellt: {0}'
        BackupSkip    = 'Kein neues Backup: Die Wow.exe ist bereits gepatcht, die Original-Bytes stehen in patcher_state.ini.'
""")
R("""        WriteFail     = '[FEHLER] Konnte die Wow.exe nicht schreiben (laeuft WoW noch?):'
        Done1         = '[FERTIG] Wow.exe wurde erfolgreich gepatcht.'
        Done2         = 'Gesamt: {0} Patches eingespielt.'
""", """        WriteFail     = '[FEHLER] Konnte die Wow.exe nicht schreiben (laeuft WoW noch?):'
        UndoFail      = '[FEHLER] Selbsttest fehlgeschlagen: Die Patches liessen sich nicht sauber zuruecknehmen.'
        StateFail     = '[FEHLER] Konnte patcher_state.ini nicht schreiben:'
        StateWarn1    = 'WARNUNG: Die Wow.exe ist gepatcht, patcher_state.ini konnte aber nicht gespeichert werden:'
        StateWarn2    = 'Ohne diese Datei lassen sich die Patches nicht mehr zuruecknehmen - dafuer Wow.exe.BAK verwenden.'
        Done1         = '[FERTIG] Wow.exe wurde erfolgreich gepatcht.'
        Done2         = 'Gesamt: {0} Patches eingespielt.'
        Done3         = 'Neu: {0}   Geaendert: {1}   Zurueckgenommen: {2}   Aktiv: {3}'
        DoneOrig      = '[FERTIG] Alle Patches zurueckgenommen, die Wow.exe ist wieder original.'
        StateSaved    = 'Zustand in patcher_state.ini gemerkt - beim naechsten Start kannst du Patches dazu- oder abwaehlen.'
""")
# --- Texte EN ---
R("""        Welcome4      = 'A backup is created automatically as Wow.exe.BAK.'
""", """        Welcome4      = 'The first patch run creates a backup as Wow.exe.BAK.'
        Welcome5      = 'Applied patches can be deselected later - all the way back to the original.'
""")
R("""        HashBad2      = '        It has already been patched or is a different version.'
        Expected      = 'Expected:  {0}'
        Found         = 'Found:     {0}'
        HashBad3      = 'Please use an unmodified Wow.exe.'
        HashOk        = '[OK] Wow.exe is original and unmodified.'
""", """        HashBad2      = '        It has already been patched (another tool, old patcher version) or is a different version.'
        HashBad3      = 'The first run requires an unmodified Wow.exe.'
        HashBadState1 = '[ERROR] This Wow.exe is neither the original nor the file last produced by this patcher.'
        HashBadState2 = '        It has been changed since (another tool, client update or similar).'
        HashBadState3 = 'Please use the last patched or an unmodified Wow.exe.'
        Expected      = 'Original:  {0}'
        ExpectedLast  = 'Last run:  {0}'
        Found         = 'Found:     {0}'
        BakHint       = 'Tip: {0} is the original Wow.exe. Copy it back to Wow.exe and start the patcher again.'
        HashOk        = '[OK] Wow.exe is original and unmodified.'
        HashKnown     = '[OK] Wow.exe is the file last produced by this patcher ({0} patches active).'
        RevertOk      = '[OK] Original reconstructed from patcher_state.ini and verified by SHA256.'
        StateBroken1  = '[ERROR] patcher_state.ini matches Wow.exe, but the original cannot be restored from it'
        StateBroken2  = '        (file damaged or edited by hand?).'
""")
R("""        MenuHelp3     = 'ENTER = accept and save selection, continue'
        SavedLoaded   = 'Your saved selection from last time has been loaded.'
""", """        MenuHelp3     = 'ENTER = accept and save selection, continue'
        MenuHelp4     = 'O = restore original (remove all patches)'
        SavedLoaded   = 'Your saved selection from last time has been loaded.'
        AppliedLoaded = 'Selected are the patches currently in Wow.exe. Deselecting a patch removes it.'
        MarkNew       = '(new)'
        MarkRemove    = '(will be removed)'
""")
R("""        BadSelect     = '[ERROR] Invalid value for -Select: {0}'
        Summary       = 'The following {0} patches will be applied:'
""", """        BadSelect     = '[ERROR] Invalid value for -Select: {0}'
        Summary       = 'The following {0} patches will be applied:'
        SumAdd        = 'Apply ({0}):'
        SumChange     = 'Change value ({0}):'
        SumRemove     = 'Remove ({0}):'
        SumKeep       = 'Stay active unchanged: {0}'
        SumOriginal   = 'Afterwards Wow.exe is the original file again.'
        NoChange      = 'No change compared to the current Wow.exe - nothing to do.'
        AlreadyOrig   = 'Wow.exe is already original - nothing to remove.'
""")
R("""        BackupOk      = 'Backup of Wow.exe created successfully: {0}'
""", """        BackupOk      = 'Backup of Wow.exe created successfully: {0}'
        BackupSkip    = 'No new backup: Wow.exe is already patched, the original bytes are stored in patcher_state.ini.'
""")
R("""        WriteFail     = '[ERROR] Could not write Wow.exe (is WoW still running?):'
        Done1         = '[DONE] Wow.exe has been patched successfully.'
        Done2         = 'Total: {0} patches applied.'
""", """        WriteFail     = '[ERROR] Could not write Wow.exe (is WoW still running?):'
        UndoFail      = '[ERROR] Self-test failed: the patches could not be removed cleanly.'
        StateFail     = '[ERROR] Could not write patcher_state.ini:'
        StateWarn1    = 'WARNING: Wow.exe is patched, but patcher_state.ini could not be saved:'
        StateWarn2    = 'Without this file the patches cannot be removed anymore - use Wow.exe.BAK for that.'
        Done1         = '[DONE] Wow.exe has been patched successfully.'
        Done2         = 'Total: {0} patches applied.'
        Done3         = 'New: {0}   Changed: {1}   Removed: {2}   Active: {3}'
        DoneOrig      = '[DONE] All patches removed, Wow.exe is original again.'
        StateSaved    = 'State remembered in patcher_state.ini - next time you can add or deselect patches.'
""")

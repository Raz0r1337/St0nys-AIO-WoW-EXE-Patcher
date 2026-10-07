# ============================================================
#  St0nys-AIO-WoW-EXE-Patcher - Patch Engine
#  Copyright (c) 2026 St0ny (Raz0r1337) - MIT-Lizenz, siehe LICENSE
#
#  Interaktiver Ablauf:
#    1. Sprache waehlen (Deutsch / English)
#    2. Pruefen: Wow.exe vorhanden und original (SHA256) bzw. mit diesem
#       Patcher gepatcht (Wasserzeichen) - dann Patchstand ermitteln
#    3. Patches auswaehlen (Menue mit Vorauswahl)
#    4. Bestaetigen, Backup anlegen (Wow.exe.ORI = Original beim ersten
#       Patchen, danach Wow.exe.BAK = vorherige Wow.exe), patchen
#
#  Die Auswahl aus dem Menue wird in patcher_selection.ini neben dem Skript
#  gespeichert und beim naechsten Start wieder vorausgewaehlt.
#
#  Optionale Parameter fuer den unbeaufsichtigten Betrieb:
#    -Language de|en          Sprachabfrage ueberspringen
#    -Select   <Auswahl>      Auswahlmenue ueberspringen. Erlaubt sind
#                             "saved" (gespeicherte Auswahl), "reforged"
#                             (Preset Reforged = Standard), "billy"
#                             (Preset Billy's_Wow.exe), "stony" (Preset
#                             St0nys_Wow.exe), "all", "none"
#                             (alle Patches zuruecknehmen) oder Nummern/Bereiche
#                             wie "1,3,5-8"
#    -Unattended              Keine Rueckfragen und keine Pausen. Ohne
#                             -Language die gemerkte Sprache bzw. Deutsch, ohne -Select die
#                             gespeicherte Auswahl bzw. das Preset Reforged
#    -Path     <Datei>        Andere Wow.exe als die im Skriptordner
#
#  Fuer Entwickler:
#    -BuildTable              Erzeugt die eingebaute Original-Byte-Tabelle
#                             neu (braucht die originale Wow.exe, siehe
#                             Invoke-BuildTable). Nach jeder Aenderung an
#                             einem Patch ausfuehren.
# ============================================================

param(
    [ValidateSet('de', 'en')][string]$Language,
    [string]$Select,
    [switch]$Unattended,
    [string]$Path,
    [switch]$BuildTable
)

$ErrorActionPreference = 'Stop'

$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
if (-not $Path) {
    $Path = Join-Path $scriptDir 'Wow.exe'
} elseif (-not [System.IO.Path]::IsPathRooted($Path)) {
    # .NET loest relative Pfade gegen das Prozessverzeichnis auf, nicht gegen
    # das aktuelle PowerShell-Verzeichnis - daher selbst absolut machen.
    $Path = Join-Path (Get-Location).ProviderPath $Path
}

# -Unattended stellt keine Rueckfragen: ohne -Language die gemerkte Sprache
# bzw. Deutsch, ohne -Select die gespeicherte Auswahl (bzw. die Standard-
# Auswahl, wenn es keine gibt).
if ($Unattended) {
    if (-not $Select) { $Select = 'saved' }
}
$file = $Path
$backup = $file + '.ORI'       # Original, wird beim ersten Patchen angelegt
$backupPrev = $file + '.BAK'   # vorherige (gepatchte) Wow.exe bei jedem weiteren Lauf
$settingsFile = Join-Path $scriptDir 'patcher_selection.ini'
$stateFile = Join-Path $scriptDir 'patcher_state.ini'

# SHA256 der originalen Wow.exe 3.3.5a (Build 12340)
$EXPECTED_HASH = 'AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8'

# Datei-Inhalt, wird einmal gelesen, im Speicher gepatcht und einmal geschrieben
$f = $null

# Gepatchte Wow.exe aus einem frueheren Lauf? Dann die dort aktiven Patch-Ids.
$patchedMode = $false
$appliedIds = @()

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

# ============================================================
#  Texte (Deutsch / English)
# ============================================================
$TEXT = @{
    de = @{
        Welcome1      = 'Willkommen. Dieses Tool patcht deine Wow.exe mit'
        Welcome2      = 'Verbesserungen: Bugfixes, Performance-Optimierungen,'
        Welcome3      = 'erweiterte Sichtweiten und verbesserte Sound-Einstellungen.'
        Welcome4      = 'Beim ersten Patchen wird das Original als Wow.exe.ORI gesichert, danach die vorherige Wow.exe als Wow.exe.BAK.'
        Welcome5      = 'Eingespielte Patches lassen sich spaeter wieder abwaehlen - bis zurueck zum Original.'
        StartWarn1    = 'HINWEIS: Patches ohne Warnung in eckigen Klammern sind im Spiel getestet und sollten auch'
        StartWarn2    = 'auf oeffentlichen Servern unbedenklich sein - eine 100%-Garantie gibt es aber nicht.'
        StartWarn3    = 'Warnungen: [unsicher] (Bann-Gefahr), [online ungetestet] (Vorsicht, kann zu Kick/Bann fuehren),'
        StartWarn4    = '[ingame ungetestet] (moeglicherweise verbuggt), [ungetestet], [Exe wird groesser] (Bann-Risiko).'
        StartWarn5    = 'Im Zweifel pruefe die Richtlinien deines Servers, bevor du eine gepatchte Wow.exe dort benutzt.'
        StartWarn6    = 'Benutzung auf eigene Gefahr.'
        Thanks        = 'Danke an Billy Hoyle, MacWarrior und Stormhand fuer ihre Hilfe und die vielen Tests im Spiel!'
        PressStart    = 'ENTER druecken um zu starten'
        NotFound      = '[FEHLER] Keine Wow.exe gefunden: {0}'
        Checking      = 'Pruefe Wow.exe Integritaet...'
        HashBad1      = '[FEHLER] Die Wow.exe ist weder original noch mit diesem Patcher gepatcht (kein Wasserzeichen).'
        HashBad2      = '         Sie wurde mit einem anderen Tool oder einer alten Patcher-Version gepatcht oder ist eine andere Version.'
        HashBad3      = 'Beim ersten Start wird eine unmodifizierte Wow.exe benoetigt.'
        Expected      = 'Original:  {0}'
        Found         = 'Gefunden:  {0}'
        BakHint       = 'Tipp: {0} ist die originale Wow.exe. Zurueck nach Wow.exe kopieren und den Patcher neu starten.'
        HashOk        = '[OK] Wow.exe ist original und unmodifiziert.'
        HashKnown     = '[OK] Wow.exe ist die zuletzt von diesem Patcher erzeugte Datei ({0} Patches aktiv).'
        RevertOk      = '[OK] Original aus patcher_state.ini rekonstruiert und per SHA256 geprueft.'
        Scanning      = 'Wasserzeichen gefunden, ermittle den Patchstand aus der Wow.exe...'
        WmFound       = '[OK] Wasserzeichen gefunden: Die Wow.exe wurde mit diesem Patcher gepatcht.'
        WmScanned     = '[OK] Patchstand aus der Exe ermittelt ({0} Patches erkannt), Original per SHA256 geprueft.'
        WmBroken1     = '[FEHLER] Die Wow.exe traegt das Wasserzeichen dieses Patchers, das Original laesst sich aber'
        WmBroken2     = '         nicht sicher wiederherstellen (danach veraendert oder mit einer anderen Patcher-Version erstellt).'
        TableWarn     = 'HINWEIS: Die eingebaute Original-Byte-Tabelle passt nicht zu dieser Auswahl - ohne patcher_state.ini liesse sich diese Wow.exe nicht zuruecknehmen.'
        MenuTitle     = 'PATCH-AUSWAHL  ({0} von {1} ausgewaehlt)'
        MenuHelp1     = 'Nummer(n) eingeben um Patches an-/abzuwaehlen, z.B.:  5   oder  3 7 12   oder  10-15'
        MenuHelp2     = 'A = alle an    N = alle aus    L = English    Q = abbrechen'
        MenuPresetR   = 'R = Preset Reforged (Standard, sicher)'
        MenuPresets   = 'B = Preset Billy''s_Wow.exe (erprobte Basis, sicher)    S = Preset St0nys_Wow.exe (unsicher)'
        StonyWarning  = 'Achtung: Das Preset St0nys_Wow.exe sollte unter keinen Umstaenden auf oeffentlichen Servern verwendet werden - das fuehrt wahrscheinlich zu einem Bann!'
        LangInfo      = 'Sprache: Deutsch (gemerkt, im Menue mit L umschaltbar)'
        MenuHelp3     = 'ENTER = Auswahl uebernehmen, speichern und weiter'
        SavedLoaded   = 'Deine gespeicherte Auswahl vom letzten Mal wurde geladen.'
        AppliedLoaded = 'Ausgewaehlt sind die Patches, die gerade in der Wow.exe stecken. Abwaehlen nimmt einen Patch zurueck.'
        MarkNew       = '(neu)'
        MarkRemove    = '(wird zurueckgenommen)'
        ValueSuggest  = '-> Vorschlag: {0}'
        ValueNow      = '-> aktuell: {0}'
        ValueAtYes    = 'Zeitpunkt der Bestaetigung mit J'
        ValueAtStart  = 'Zeitpunkt des Patchens'
        Saved         = 'Auswahl fuer den naechsten Start gespeichert.'
        SaveFail      = 'HINWEIS: Auswahl konnte nicht gespeichert werden: {0}'
        Prompt        = 'Eingabe'
        BadInput      = 'Ungueltige Eingabe: {0}'
        NoneSelected  = 'Es ist kein Patch ausgewaehlt.'
        BadSelect     = '[FEHLER] Ungueltiger Wert fuer -Select: {0}'
        Summary       = 'Folgende {0} Patches werden eingespielt:'
        SumAdd        = 'Neu einspielen ({0}):'
        SumChange     = 'Wert aendern ({0}):'
        SumRemove     = 'Zuruecknehmen ({0}):'
        SumKeep       = 'Bleiben unveraendert aktiv: {0}'
        SumOriginal   = 'Danach ist die Wow.exe wieder die originale Datei.'
        NoChange      = 'Keine Aenderung gegenueber der aktuellen Wow.exe - es gibt nichts zu tun.'
        AlreadyOrig   = 'Die Wow.exe ist bereits original - es gibt nichts zurueckzunehmen.'
        InputHead     = 'Werte fuer die gewaehlten Patches (ENTER = Vorschlag in Klammern):'
        BadValue      = '[FEHLER] Ungueltiger gemerkter Wert fuer "{0}": {1}'
        HintHead      = 'HINWEIS zu "{0}":'
        Hint          = 'wirkt nur vollstaendig zusammen mit:'
        Obsolete      = 'macht diese Patches ueberfluessig (beide zusammen schaden nicht):'
        GrowHead      = 'HINWEIS: Diese Patches haengen eine Sektion an und machen die Wow.exe groesser:'
        GrowBan       = 'Das ist keine sichere Bann-Gefahr, aber ein Risiko: Manche Server pruefen die Groesse der Wow.exe.'
        CheatHead     = 'ACHTUNG - unsicher, Bann-Gefahr: Diese Patches koennen von Servern als Cheat oder Botting gewertet werden:'
        CheatBan      = 'Das kann zu einem Bann fuehren - nur auf Servern nutzen, die das erlauben!'
        PublicHead    = 'VORSICHT: Diese Patches sind nicht auf oeffentlichen Servern getestet - moegliche Bann-Gefahr:'
        PublicBan     = 'ACHTUNG: Ungetestet - niemand kann vorhersagen, wie der Server darauf reagiert. Das kann zu einem Kick oder Bann fuehren!'
        UntestedHead  = 'HINWEIS: Die Funktion dieser Patches ist im Spiel ungetestet - moeglicherweise verbuggt:'
        UntestedWarn  = 'ACHTUNG: Ungetestet - niemand kann vorhersagen, wie das Spiel darauf reagiert. Fehler oder Abstuerze sind moeglich!'
        TagBan        = 'unsicher'
        TagPublic     = 'online ungetestet'
        TagGame       = 'ingame ungetestet'
        TagBoth       = 'ungetestet'
        TagGrow       = 'Exe wird groesser'
        Confirm       = 'Patchen jetzt starten? (J/N)'
        Yes           = 'J'
        Aborted       = 'Abgebrochen. Die Wow.exe wurde nicht veraendert.'
        BackupFail    = '[FEHLER] Konnte Wow.exe nicht sichern. Abbruch.'
        BackupOk      = 'Original gesichert als: {0}'
        BackupSkip    = 'Wow.exe.ORI (Original) ist vorhanden und bleibt unveraendert.'
        BackupRedo    = 'Wow.exe.ORI fehlte und wurde aus dem rekonstruierten Original neu angelegt: {0}'
        BackupPrev    = 'Bisherige Wow.exe gesichert als: {0}'
        Starting      = 'Starte Patch-Vorgang...'
        PatchFail     = '[FEHLER] Beim Patchen ist ein Fehler aufgetreten:'
        NotWritten    = 'Die Wow.exe wurde nicht veraendert.'
        WriteFail     = '[FEHLER] Konnte die Wow.exe nicht schreiben (laeuft WoW noch?):'
        UndoFail      = '[FEHLER] Selbsttest fehlgeschlagen: Die Patches liessen sich nicht sauber zuruecknehmen.'
        StateWarn1    = 'WARNUNG: Die Wow.exe ist gepatcht, patcher_state.ini konnte aber nicht gespeichert werden:'
        StateWarn2    = 'Kein Problem: Beim naechsten Start ermittelt der Patcher den Patchstand ueber das Wasserzeichen (dauert nur etwas laenger).'
        Done1         = '[FERTIG] Wow.exe wurde erfolgreich gepatcht.'
        Done2         = 'Gesamt: {0} Patches eingespielt.'
        Done3         = 'Neu: {0}   Geaendert: {1}   Zurueckgenommen: {2}   Aktiv: {3}'
        DoneOrig      = '[FERTIG] Alle Patches zurueckgenommen, die Wow.exe ist wieder original.'
        StateSaved    = 'Zustand in patcher_state.ini gemerkt - beim naechsten Start kannst du Patches dazu- oder abwaehlen.'
        PressEnter    = 'ENTER druecken zum Beenden'
    }
    en = @{
        Welcome1      = 'Welcome. This tool patches your Wow.exe with'
        Welcome2      = 'improvements: bug fixes, performance optimizations,'
        Welcome3      = 'extended view distances and improved sound settings.'
        Welcome4      = 'The first patch run saves the original as Wow.exe.ORI, later runs save the previous Wow.exe as Wow.exe.BAK.'
        Welcome5      = 'Applied patches can be deselected later - all the way back to the original.'
        StartWarn1    = 'NOTE: Patches without a warning in square brackets have been tested in game and should be'
        StartWarn2    = 'harmless on public servers as well - but there is no 100% guarantee.'
        StartWarn3    = 'Warnings: [unsafe] (ban risk), [untested online] (careful, may get you kicked/banned),'
        StartWarn4    = '[untested ingame] (possibly buggy), [untested], [exe grows] (possible ban risk).'
        StartWarn5    = 'If in doubt, check the rules of your server before using a patched Wow.exe there.'
        StartWarn6    = 'Use at your own risk.'
        Thanks        = 'Thanks to Billy Hoyle, MacWarrior and Stormhand for their help and all the testing in game!'
        PressStart    = 'Press ENTER to start'
        NotFound      = '[ERROR] No Wow.exe found: {0}'
        Checking      = 'Checking Wow.exe integrity...'
        HashBad1      = '[ERROR] This Wow.exe is neither original nor patched with this patcher (no watermark).'
        HashBad2      = '        It has been patched with another tool or an old patcher version, or is a different version.'
        HashBad3      = 'The first run requires an unmodified Wow.exe.'
        Expected      = 'Original:  {0}'
        Found         = 'Found:     {0}'
        BakHint       = 'Tip: {0} is the original Wow.exe. Copy it back to Wow.exe and start the patcher again.'
        HashOk        = '[OK] Wow.exe is original and unmodified.'
        HashKnown     = '[OK] Wow.exe is the file last produced by this patcher ({0} patches active).'
        RevertOk      = '[OK] Original reconstructed from patcher_state.ini and verified by SHA256.'
        Scanning      = 'Watermark found, determining the patch state from Wow.exe...'
        WmFound       = '[OK] Watermark found: this Wow.exe was patched with this patcher.'
        WmScanned     = '[OK] Patch state read from the exe ({0} patches detected), original verified by SHA256.'
        WmBroken1     = '[ERROR] This Wow.exe carries the watermark of this patcher, but the original cannot be'
        WmBroken2     = '        restored safely (changed afterwards or made with another patcher version).'
        TableWarn     = 'NOTE: The built-in original bytes table does not match this selection - without patcher_state.ini this Wow.exe could not be reverted.'
        MenuTitle     = 'PATCH SELECTION  ({0} of {1} selected)'
        MenuHelp1     = 'Enter number(s) to toggle patches, e.g.:  5   or  3 7 12   or  10-15'
        MenuHelp2     = 'A = all on    N = all off    L = Deutsch    Q = quit'
        MenuPresetR   = 'R = preset Reforged (default, safe)'
        MenuPresets   = 'B = preset Billy''s_Wow.exe (proven base, safe)    S = preset St0nys_Wow.exe (unsafe)'
        StonyWarning  = 'Warning: the preset St0nys_Wow.exe should never be used on public servers under any circumstances - it will most likely get you banned!'
        LangInfo      = 'Language: English (remembered, switch with L in the menu)'
        MenuHelp3     = 'ENTER = accept and save selection, continue'
        SavedLoaded   = 'Your saved selection from last time has been loaded.'
        AppliedLoaded = 'Selected are the patches currently in Wow.exe. Deselecting a patch removes it.'
        MarkNew       = '(new)'
        MarkRemove    = '(will be removed)'
        ValueSuggest  = '-> suggestion: {0}'
        ValueNow      = '-> current: {0}'
        ValueAtYes    = 'time of confirming with Y'
        ValueAtStart  = 'time of patching'
        Saved         = 'Selection saved for next time.'
        SaveFail      = 'NOTE: Could not save the selection: {0}'
        Prompt        = 'Input'
        BadInput      = 'Invalid input: {0}'
        NoneSelected  = 'No patch is selected.'
        BadSelect     = '[ERROR] Invalid value for -Select: {0}'
        Summary       = 'The following {0} patches will be applied:'
        SumAdd        = 'Apply ({0}):'
        SumChange     = 'Change value ({0}):'
        SumRemove     = 'Remove ({0}):'
        SumKeep       = 'Stay active unchanged: {0}'
        SumOriginal   = 'Afterwards Wow.exe is the original file again.'
        NoChange      = 'No change compared to the current Wow.exe - nothing to do.'
        AlreadyOrig   = 'Wow.exe is already original - nothing to remove.'
        InputHead     = 'Values for the selected patches (ENTER = suggestion in brackets):'
        BadValue      = '[ERROR] Invalid saved value for "{0}": {1}'
        HintHead      = 'NOTE on "{0}":'
        Hint          = 'only takes full effect together with:'
        Obsolete      = 'makes these patches unnecessary (both together do no harm):'
        GrowHead      = 'NOTE: These patches append a section and make Wow.exe larger:'
        GrowBan       = 'This does not mean a certain ban, but it is a risk: some servers check the size of Wow.exe.'
        CheatHead     = 'WARNING - unsafe, ban risk: servers may treat these patches as cheating or botting:'
        CheatBan      = 'This can lead to a ban - only use them on servers that allow it!'
        PublicHead    = 'CAUTION: These patches have not been tested on public servers - possible ban risk:'
        PublicBan     = 'WARNING: Untested - nobody can predict how the server will react. This may get you kicked or banned!'
        UntestedHead  = 'NOTE: These patches have not been tested in game - possibly buggy:'
        UntestedWarn  = 'WARNING: Untested - nobody can predict how the game will react. Bugs or crashes are possible!'
        TagBan        = 'unsafe'
        TagPublic     = 'untested online'
        TagGame       = 'untested ingame'
        TagBoth       = 'untested'
        TagGrow       = 'exe grows'
        Confirm       = 'Start patching now? (Y/N)'
        Yes           = 'Y'
        Aborted       = 'Aborted. Wow.exe has not been modified.'
        BackupFail    = '[ERROR] Could not back up Wow.exe. Aborting.'
        BackupOk      = 'Original saved as: {0}'
        BackupSkip    = 'Wow.exe.ORI (original) exists and stays untouched.'
        BackupRedo    = 'Wow.exe.ORI was missing and has been recreated from the reconstructed original: {0}'
        BackupPrev    = 'Previous Wow.exe saved as: {0}'
        Starting      = 'Starting patch process...'
        PatchFail     = '[ERROR] An error occurred while patching:'
        NotWritten    = 'Wow.exe has not been modified.'
        WriteFail     = '[ERROR] Could not write Wow.exe (is WoW still running?):'
        UndoFail      = '[ERROR] Self-test failed: the patches could not be removed cleanly.'
        StateWarn1    = 'WARNING: Wow.exe is patched, but patcher_state.ini could not be saved:'
        StateWarn2    = 'No problem: next time the patcher determines the patch state via the watermark (just takes a bit longer).'
        Done1         = '[DONE] Wow.exe has been patched successfully.'
        Done2         = 'Total: {0} patches applied.'
        Done3         = 'New: {0}   Changed: {1}   Removed: {2}   Active: {3}'
        DoneOrig      = '[DONE] All patches removed, Wow.exe is original again.'
        StateSaved    = 'State remembered in patcher_state.ini - next time you can add or deselect patches.'
        PressEnter    = 'Press ENTER to exit'
    }
}

function T([string]$key) {
    $s = $TEXT[$script:lang][$key]
    if ($args.Count -gt 0) { $s = $s -f $args }
    return $s
}

function Say([string]$text, [string]$color) {
    if ($color) { Write-Host "  $text" -ForegroundColor $color } else { Write-Host "  $text" }
}

function PatchName($p, [switch]$NoTags) {
    if ($script:lang -eq 'en') { $n = $p.En; $note = $p.NoteEn } else { $n = $p.De; $note = $p.NoteDe }
    if ($note) { $n = "$n ($note)" }
    if ($NoTags) { return $n }
    $tags = @(PatchTags $p)
    if ($tags.Count -gt 0) { $n = "$n [$($tags -join ', ')]" }
    return $n
}

# Einheitliche Warnungen (Warn-Codes): BanRisk = Bann-Gefahr (2),
# PublicUntested = nicht auf oeffentlichen Servern getestet (3),
# GameUntested = Funktion im Spiel ungetestet (4), dazu GrowsExe.
function PatchTags($p) {
    $tags = @()
    if ($p.BanRisk) { $tags += T 'TagBan' }
    if ($p.PublicUntested -and $p.GameUntested) { $tags += T 'TagBoth' }
    elseif ($p.PublicUntested) { $tags += T 'TagPublic' }
    elseif ($p.GameUntested) { $tags += T 'TagGame' }
    if ($p.GrowsExe) { $tags += T 'TagGrow' }
    return $tags
}

# Name mit Patch-Nummer davor ("Nr. 64 ..."), fuer Hinweise auf andere Patches
# (ohne Warnungen - die Hinweisliste nennt sie schon).
function PatchRef($p) {
    $nr = [array]::IndexOf($patches, $p) + 1
    if ($script:lang -eq 'en') { return "No. $nr $(PatchName $p -NoTags)" }
    return "Nr. $nr $(PatchName $p -NoTags)"
}

# Eingabe lesen. Read-Host liefert bei Strg+Z bzw. geschlossener Eingabe $null -
# dann gibt es keine Antwort mehr, also abbrechen (Exit-Code 2, nichts geaendert).
function Ask([string]$prompt) {
    $r = Read-Host $prompt
    if ($null -eq $r) {
        Write-Host ''
        exit 2
    }
    return ([string]$r).Trim()
}

function Exit-Patcher([int]$code) {
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

# ============================================================
#  Helfer fuer den HD-Portrait-Patch
#  Haengt eine neue PE-Sektion ".hdp" an die EXE an (256x256-Alphamaske
#  + Code-Caves + Detour des Masken-Builders). Originalgetreuer Port von
#  apply_hd_portraits.py, byte-fuer-byte gegen dessen Ausgabe verifiziert.
#  Wie CameraReforged veraendert dieser Patch die Dateigroesse/PE-Struktur.
# ============================================================
function RU32([byte[]]$a, [int]$o) { return [int64][BitConverter]::ToUInt32($a, $o) }
function RU16([byte[]]$a, [int]$o) { return [int][BitConverter]::ToUInt16($a, $o) }
function AlignUp([int64]$v, [int64]$a) { $r = $v % $a; if ($r -eq 0) { return $v } else { return ($v + $a - $r) } }
function AddRaw($list, [byte[]]$bytes) { foreach ($b in $bytes) { [void]$list.Add([byte]$b) } }
function AddLE32($list, [int64]$v) { $b = [BitConverter]::GetBytes([int32]$v); for ($i = 0; $i -lt 4; $i++) { [void]$list.Add($b[$i]) } }

function New-PortraitMask([int]$N) {
    # Row-major NxN, 1 Byte/Pixel: kreisfoermige Alpha, 255 innen (1px Feather), 0 aussen.
    $R = $N / 2.0 - 1.0
    $c = ($N - 1) / 2.0
    $m = New-Object byte[] ($N * $N)
    for ($y = 0; $y -lt $N; $y++) {
        $row = $y * $N
        $dy = [double]$y - $c
        for ($x = 0; $x -lt $N; $x++) {
            $dx = [double]$x - $c
            $d = [Math]::Sqrt($dx * $dx + $dy * $dy)
            $a = [Math]::Round(($R - $d + 0.5) * 255.0, [System.MidpointRounding]::ToEven)
            if ($a -lt 0) { $a = 0 } elseif ($a -gt 255) { $a = 255 }
            $m[$row + $x] = [byte]$a
        }
    }
    return , $m
}

# ============================================================
#  Signatur-Verweis entfernen (fuer alle Patches, die eine Sektion anhaengen)
#  Die originale Wow.exe traegt am Dateiende eine Authenticode-Signatur
#  (Datenverzeichnis 4 "Security", Datei 0x757C00, 0x1298 Byte). Angehaengte
#  Sektionen landen dahinter, die Signatur steht dann nicht mehr am Ende und
#  manche Werkzeuge melden die Datei als beschaedigt. Gueltig ist sie nach
#  jedem Patch ohnehin nicht mehr. Der Verweis im Header wird daher geleert;
#  die Signatur-Bytes selbst bleiben unangetastet als ungenutzte Daten liegen,
#  so stellt die Ruecknahme das Original Byte fuer Byte wieder her.
# ============================================================
function Clear-CertificateTable {
    $e = RU32 $script:f 0x3C
    Patch ($e + 24 + 96 + 4 * 8) ([byte[]](0, 0, 0, 0, 0, 0, 0, 0))
}

function Add-HdPortraits([int]$SIZE) {
    # --- Engine-Adressen (VA, build 12340) ---
    $TEX_LOW = 0x4B8C80; $TEX_WRP = 0x4B9200; $MASKFN = 0x6176A0; $MASKFN_CONT = 0x6176A9
    $S_RT = 0x6180E8; $S_TEX = 0x619B72; $S_READ = 0x616E09; $S_MASK = 0x619FAE
    $IB = 0x400000

    # --- PE-Header / Sektionstabelle lesen ---
    $e = RU32 $script:f 0x3C
    $nsec = RU16 $script:f ($e + 6)
    $opt = RU16 $script:f ($e + 20)
    $SA = RU32 $script:f ($e + 24 + 32)
    $FA = RU32 $script:f ($e + 24 + 36)
    $sectBase = $e + 24 + $opt
    $TVA = 0; $TRO = 0
    for ($i = 0; $i -lt $nsec; $i++) {
        $so = $sectBase + 40 * $i
        $nm = ''
        for ($k = 0; $k -lt 8; $k++) { $bb = $script:f[$so + $k]; if ($bb -ne 0) { $nm += [char]$bb } }
        if ($nm -eq '.text') { $TVA = $IB + (RU32 $script:f ($so + 12)); $TRO = RU32 $script:f ($so + 20) }
    }
    $lastSo = $sectBase + 40 * ($nsec - 1)
    $lastVA = RU32 $script:f ($lastSo + 12)
    $lastVS = RU32 $script:f ($lastSo + 8)
    $new_rva = AlignUp ($lastVA + $lastVS) $SA
    $new_sva = $IB + $new_rva

    # --- Maske + Adressen der Caves ---
    $MASK_OFF = 0x10
    $maskCore = New-PortraitMask $SIZE
    $maskLen = $maskCore.Length + 0x1000          # + Ueberlese-Sicherheitspuffer
    $CODE_OFF = AlignUp ($MASK_OFF + $maskLen) 16
    $mask_va = $new_sva + $MASK_OFF
    $slot_va = $new_sva
    $cA = $new_sva + $CODE_OFF
    $cB = $cA + 21
    $det_va = $cB + 21

    # --- Code-Caves zusammenbauen ---
    $code = New-Object System.Collections.Generic.List[byte]
    # caveA: mov [esp+08],SIZE ; mov [esp+0C],SIZE ; jmp TEX_LOW
    AddRaw $code @(0xC7, 0x44, 0x24, 0x08); AddLE32 $code $SIZE
    AddRaw $code @(0xC7, 0x44, 0x24, 0x0C); AddLE32 $code $SIZE
    AddRaw $code @(0xE9);                   AddLE32 $code ($TEX_LOW - ($cA + 16 + 5))
    # caveB: mov [esp+04],SIZE ; mov [esp+08],SIZE ; jmp TEX_WRP
    AddRaw $code @(0xC7, 0x44, 0x24, 0x04); AddLE32 $code $SIZE
    AddRaw $code @(0xC7, 0x44, 0x24, 0x08); AddLE32 $code $SIZE
    AddRaw $code @(0xE9);                   AddLE32 $code ($TEX_WRP - ($cB + 16 + 5))
    # detour: cmp eax,SIZE ; jne +6 ; mov eax,slot ; ret ; <verschobene Prologue> ; jmp MASKFN_CONT
    AddRaw $code @(0x3D);                   AddLE32 $code $SIZE
    AddRaw $code @(0x75, 0x06)
    AddRaw $code @(0xB8);                   AddLE32 $code $slot_va
    AddRaw $code @(0xC3)
    AddRaw $code @(0x55, 0x8B, 0xEC, 0x81, 0xEC, 0x04, 0x05, 0x00, 0x00)
    AddRaw $code @(0xE9);                   AddLE32 $code ($MASKFN_CONT - ($det_va + 22 + 5))
    $codeArr = $code.ToArray()

    $vsize = $CODE_OFF + $codeArr.Length
    $raw_size = AlignUp $vsize $FA
    $hoff = $sectBase + 40 * $nsec
    if (($hoff + 40) -gt (RU32 $script:f ($sectBase + 20))) { throw 'HD-Portraits: kein Platz im PE-Header fuer einen weiteren Sektionseintrag.' }

    # --- Sektions-Rohdaten: [slot][maske][pad][code][pad] ---
    $sec = New-Object byte[] $raw_size
    [Array]::Copy([BitConverter]::GetBytes([int32]0), 0, $sec, 0, 4)                 # slot.flags = 0
    [Array]::Copy([BitConverter]::GetBytes([int32]($SIZE * $SIZE)), 0, $sec, 4, 4)   # slot.count = N*N
    [Array]::Copy([BitConverter]::GetBytes([int32]$mask_va), 0, $sec, 8, 4)          # slot.ptr   = &maske
    [Array]::Copy($maskCore, 0, $sec, $MASK_OFF, $maskCore.Length)
    [Array]::Copy($codeArr, 0, $sec, $CODE_OFF, $codeArr.Length)

    # --- Datei vergroessern: padding bis FileAlignment, dann Sektion anhaengen ---
    $oldLen = $script:f.Length
    $new_raw = AlignUp $oldLen $FA
    $nf = New-Object byte[] ($new_raw + $raw_size)
    [Array]::Copy($script:f, 0, $nf, 0, $oldLen)
    [Array]::Copy($sec, 0, $nf, $new_raw, $sec.Length)
    $script:f = $nf

    # --- PE-Header anpassen (NumberOfSections, SizeOfImage, neuer Sektionsheader) ---
    Patch ($e + 6) ([BitConverter]::GetBytes([uint16]($nsec + 1)))
    Patch ($e + 24 + 56) ([BitConverter]::GetBytes([uint32](AlignUp ($new_rva + $vsize) $SA)))
    Clear-CertificateTable
    $sh = New-Object byte[] 40
    [Array]::Copy([System.Text.Encoding]::ASCII.GetBytes('.hdp'), 0, $sh, 0, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$vsize), 0, $sh, 8, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$new_rva), 0, $sh, 12, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$raw_size), 0, $sh, 16, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$new_raw), 0, $sh, 20, 4)
    [Array]::Copy([byte[]](0x60, 0x00, 0x00, 0xE0), 0, $sh, 36, 4)                    # chars = 0xE0000060 (RWX | init data)
    Patch $hoff $sh

    # --- In-Place-Edits: Aufruf-Sites auf die Caves umbiegen, Groessen auf SIZE ---
    $toRT = $TRO + ($S_RT - $TVA); $toTEX = $TRO + ($S_TEX - $TVA)
    $toRD = $TRO + ($S_READ - $TVA); $toMK = $TRO + ($S_MASK - $TVA); $toMF = $TRO + ($MASKFN - $TVA)
    Patch ($toRT + 1) ([BitConverter]::GetBytes([int32]($cA - ($S_RT + 5))))
    Patch ($toTEX + 1) ([BitConverter]::GetBytes([int32]($cB - ($S_TEX + 5))))
    Patch ($toRD + 1) ([BitConverter]::GetBytes([int32]$SIZE))
    Patch ($toMK + 1) ([BitConverter]::GetBytes([int32]$SIZE))
    $hook = New-Object byte[] 9
    $hook[0] = 0xE9
    [Array]::Copy([BitConverter]::GetBytes([int32]($det_va - ($MASKFN + 5))), 0, $hook, 1, 4)
    $hook[5] = 0x90; $hook[6] = 0x90; $hook[7] = 0x90; $hook[8] = 0x90
    Patch $toMF $hook
}

# ============================================================
#  Helfer fuer den CameraReforged-Patch
#  Portierung von CameraReforged (Stormhand) in die Patch-Engine dieses Tools,
#  eingebaut mit seiner ausdruecklichen Erlaubnis.
#  Quelle: https://github.com/Zendevve/CameraReforged
#  BETA: funktioniert noch nicht zu 100 Prozent.
#
#  Haengt eine eigene Sektion ".camr" an (RWX, etwa +1 KB), registriert darin
#  beim Start test_cameraHeight und test_cameraOverShoulder als echte CVars
#  und biegt die Kamera-Lesestellen darauf um. Anders als alle uebrigen Patches
#  ausser Add-HdPortraits veraendert dieser die Dateigroesse und die
#  PE-Struktur. Beide vertragen sich: die Sektionsdaten werden bei jedem Aufruf
#  frisch aus dem aktuellen Header berechnet, die Reihenfolge spielt keine Rolle.
#
#  ZWEI ABWEICHUNGEN VON DER VORLAGE, BEIDE NOTWENDIG
#
#  1. EIGENE SEKTION STATT .rdata-PADDING
#  Der Original-Patcher legt Code und Daten ins ungenutzte Padding am Ende der
#  .rdata-Sektion und hebt diese dafuer im PE-Header auf ausfuehrbar. Genau das
#  laesst diesen Client beim Start mit dem MSVC-Runtimefehler R6002
#  ("floating point support not loaded") abbrechen - nachgewiesen mit einem
#  Build, der NUR dieses eine Byte aenderte und sonst nichts. Umgekehrt liefen
#  Builds, die die Cave-Bytes ins Padding schrieben ohne die Sektion
#  umzuflaggen, einwandfrei. Das Padding traegt also Daten, laesst sich aber
#  nicht ausfuehrbar machen. Eine angehaengte Sektion umgeht das vollstaendig
#  und ist auch der Fallback, den die Vorlage selbst vorsieht.
#
#  2. ZEIGER STATT CALLBACK
#  Die Vorlage haengt an jedes CVar einen Callback, der den geparsten float aus
#  dem CVar-Objekt (+0x2C) in den Datenblock kopieren soll. Das kann nicht
#  funktionieren: der Callback bei VA 0x7668EC ist ein PRUEF-Callback und laeuft,
#  BEVOR der neue Wert gespeichert wird - er sieht also immer noch den alten.
#  Bei der Anlage steht dort ausserdem eine glatte 0 (fldz/fstp bei 0x76812B),
#  der eingebackene Startwert wird beim Start also sofort ueberschrieben. In der
#  Praxis hinkt der Wert damit jeder Aenderung um einen Schritt hinterher, was
#  sich wie eine willkuerlich reagierende Kamera anfuehlt.
#  Hier merkt sich der Init-Hook stattdessen den Zeiger auf das CVar-Objekt, den
#  CVars_Register in eax zurueckgibt, und der Kamera-Hook liest den float bei
#  jedem Bild frisch von dort. Damit wirkt /console sofort und exakt.
# ============================================================
function Add-CameraReforged([double]$Height, [double]$Shoulder, [double]$MaxFactor, [double]$ZoomSpeed) {

    # Grenzen wie in der Vorlage. Sie sichern nebenbei ab, dass die als Text
    # abgelegten Vorgabewerte in ihre Slots passen (siehe Feldlage unten).
    if ($Height    -lt  0.0 -or $Height    -gt   3.0) { throw 'CameraReforged: Height muss zwischen 0.0 und 3.0 liegen.' }
    if ($Shoulder  -lt -2.0 -or $Shoulder  -gt   2.0) { throw 'CameraReforged: Shoulder muss zwischen -2.0 und 2.0 liegen.' }
    if ($MaxFactor -lt  1.0 -or $MaxFactor -gt   5.0) { throw 'CameraReforged: MaxFactor muss zwischen 1.0 und 5.0 liegen.' }
    if ($ZoomSpeed -lt  1.0 -or $ZoomSpeed -gt 100.0) { throw 'CameraReforged: ZoomSpeed muss zwischen 1.0 und 100.0 liegen.' }

    # --- Engine-Adressen (VA, build 12340) ---
    $REGISTER    = 0x767FC0   # CVars_Register(name, desc, flags, default, callback, 0,0,0,0) - cdecl, 9 Argumente
    $INIT_VA     = 0x51D9B0   # CVars_Initialize, Prolog (push ebp / mov ebp,esp / sub esp,80h)
    $INIT_CONT   = 0x51D9B9   # dahinter, dort steht schon die erste eigene Registrierung
    $HEIGHT_VA   = 0x6070CB   # fld [0x9F1670] im Kamera-Fokuspfad
    $HEIGHT_CONT = 0x6070D1   # dahinter
    $IB          = 0x400000

    # --- Platz fuer die neue Sektion hinter der letzten vorhandenen suchen ---
    $e = RU32 $script:f 0x3C
    $nsec = RU16 $script:f ($e + 6)
    $opt = RU16 $script:f ($e + 20)
    $SA = RU32 $script:f ($e + 24 + 32)
    $FA = RU32 $script:f ($e + 24 + 36)
    $sectBase = $e + 24 + $opt
    $lastSo = $sectBase + 40 * ($nsec - 1)
    $new_rva = AlignUp ((RU32 $script:f ($lastSo + 12)) + (RU32 $script:f ($lastSo + 8))) $SA
    $new_sva = $IB + $new_rva

    $SEC_SIZE = 0x200         # 512 Byte: Code ab +0, Daten ab +0x100
    $CODE_VA  = $new_sva
    $DATA_VA  = $new_sva + 0x100

    # --- Feldlage im Datenblock (Byte-Offsets ab $DATA_VA) ---
    #   0x00 dword    Zeiger auf das CVar-Objekt test_cameraHeight
    #   0x04 dword    Zeiger auf das CVar-Objekt test_cameraOverShoulder
    #   0x08 float    Schulterversatz, vom Kamera-Hook je Bild aufgefrischt
    #   0x0C char[8]  Vorgabetext cameraDistanceMaxFactor
    #   0x14 char[8]  Vorgabetext cameraDistanceMoveSpeed
    #   0x20 char[18] "test_cameraHeight"
    #   0x32 char[5]  Vorgabetext Hoehe      -> max. 4 Zeichen, daher Height <= 3.0
    #   0x37 char[24] "test_cameraOverShoulder"
    #   0x4F char[9]  Vorgabetext Schulter   -> "-2.00" passt
    $P_HEIGHT = 0x00; $P_SHOULDER = 0x04; $O_SHOULDER = 0x08
    $O_MAXF = 0x0C; $O_ZOOM = 0x14
    $O_HNAME = 0x20; $O_HDEF = 0x32; $O_SNAME = 0x37; $O_SDEF = 0x4F

    $c = New-Object System.Collections.Generic.List[byte]

    # --- cvar_init_hook ---
    # Haengt sich vor CVars_Initialize, meldet beide CVars an und legt die
    # zurueckgegebenen Objektzeiger im Datenblock ab. Der Zeitpunkt ist
    # unkritisch - CVars_Initialize registriert direkt hinter dem Prolog selbst
    # ihr erstes CVar ueber genau diese Funktion, die Registry steht also.
    $initHook = $CODE_VA + $c.Count
    AddRaw $c @(0x60)                                                 # pushad
    $regs = @( ,@($O_HNAME, $O_HDEF, $P_HEIGHT) ) + @( ,@($O_SNAME, $O_SDEF, $P_SHOULDER) )
    foreach ($r in $regs) {
        AddRaw $c @(0x6A, 0x00, 0x6A, 0x00, 0x6A, 0x00, 0x6A, 0x00)   # push 0 x4 (Argumente 6 bis 9)
        AddRaw $c @(0x6A, 0x00)                                       # push callback = 0, siehe Kopf
        AddRaw $c @(0x68); AddLE32 $c ($DATA_VA + $r[1])              # push default (Text)
        AddRaw $c @(0x6A, 0x10, 0x6A, 0x00)                           # push flags=0x10 ; push desc=0
        #  ^^^^ Die Flags landen im CVar-Objekt bei +0x1C, Bits 4 und 5 bilden
        #  darin eine Kategorie. Der Client schreibt beim Beenden nur die
        #  Kategorien 0x10 und 0x20 in die Config.wtf, Blizzards eigene CVars
        #  werden mit 0x10 registriert. Mit der 1 der Vorlage waere die Kategorie
        #  0 und der Wert nach jedem Neustart wieder auf dem Startwert.
        AddRaw $c @(0x68); AddLE32 $c ($DATA_VA + $r[0])              # push name
        $site = $CODE_VA + $c.Count
        AddRaw $c @(0xE8); AddLE32 $c ($REGISTER - ($site + 5))       # call CVars_Register -> eax = CVar*
        AddRaw $c @(0x83, 0xC4, 0x24)                                 # add esp,24h (9 Argumente, cdecl)
        AddRaw $c @(0xA3); AddLE32 $c ($DATA_VA + $r[2])              # mov [zeiger], eax
    }
    AddRaw $c @(0x61)                                                 # popad
    AddRaw $c @(0xDB, 0xE3)                                           # fninit - popad rettet die FPU nicht,
                                                                      # und am Funktionseingang ist der
                                                                      # x87-Stack per Konvention leer
    AddRaw $c @(0x55, 0x8B, 0xEC, 0x81, 0xEC, 0x80, 0x00, 0x00, 0x00) # verschobener Prolog
    $site = $CODE_VA + $c.Count
    AddRaw $c @(0xE9); AddLE32 $c ($INIT_CONT - ($site + 5))

    # --- camera_height_hook ---
    # Sitzt im Kamera-Fokuspfad. [ebp-2Ch] ist dort die Z-Koordinate des Punkts,
    # auf den die Kamera zielt (der Vektor beginnt bei [ebp-34h], gefuellt von
    # call 0x603090 kurz davor). Der Client legt ihn auf Brusthoehe.
    #
    # Zuerst wird der Schulterversatz aufgefrischt: die vier Lesestellen weiter
    # unten koennen nur ein festes "fld [adresse]" aufnehmen (6 Byte), fuer eine
    # Zeiger-Dereferenzierung ist dort kein Platz. Also holt der Hook den Wert
    # hier je Bild aus dem CVar-Objekt und legt ihn an der festen Adresse ab.
    # Danach kommt die Hoehe auf [ebp-2Ch]. Beide Zugriffe sind gegen einen
    # Nullzeiger abgesichert, falls eine Registrierung fehlschlagen sollte.
    $heightHook = $CODE_VA + $c.Count
    AddRaw $c @(0xA1); AddLE32 $c ($DATA_VA + $P_SHOULDER)            # mov eax,[zeiger schulter]
    AddRaw $c @(0x85, 0xC0, 0x74, 0x09)                               # test eax,eax ; je ueberspringen
    AddRaw $c @(0xD9, 0x40, 0x2C)                                     # fld [eax+2Ch]
    AddRaw $c @(0xD9, 0x1D); AddLE32 $c ($DATA_VA + $O_SHOULDER)      # fstp [schulterwert]
    AddRaw $c @(0xA1); AddLE32 $c ($DATA_VA + $P_HEIGHT)              # mov eax,[zeiger hoehe]
    AddRaw $c @(0x85, 0xC0, 0x74, 0x09)                               # test eax,eax ; je ueberspringen
    AddRaw $c @(0xD9, 0x40, 0x2C)                                     # fld [eax+2Ch]
    AddRaw $c @(0xD8, 0x45, 0xD4, 0xD9, 0x5D, 0xD4)                   # fadd [ebp-2Ch] ; fstp [ebp-2Ch]
    AddRaw $c @(0xD9, 0x05, 0x70, 0x16, 0x9F, 0x00)                   # verschobene fld [0x9F1670]
    $site = $CODE_VA + $c.Count
    AddRaw $c @(0xE9); AddLE32 $c ($HEIGHT_CONT - ($site + 5))

    if ($c.Count -gt 0x100) { throw "CameraReforged: Code-Cave zu gross ($($c.Count) Byte, Platz bis 0x100)." }

    # --- Sektionsinhalt: [code][pad bis 0x100][daten] ---
    $sec = New-Object byte[] $SEC_SIZE
    [Array]::Copy($c.ToArray(), 0, $sec, 0, $c.Count)
    # Startwert des Schulterversatzes, bis der Hook ihn das erste Mal auffrischt
    [Array]::Copy([BitConverter]::GetBytes([float]$Shoulder), 0, $sec, (0x100 + $O_SHOULDER), 4)
    $inv = [System.Globalization.CultureInfo]::InvariantCulture
    $strings = @(
        ,@($O_MAXF,  $MaxFactor.ToString('0.00', $inv))
        ,@($O_ZOOM,  $ZoomSpeed.ToString('0.00', $inv))
        ,@($O_HNAME, 'test_cameraHeight')
        ,@($O_HDEF,  $Height.ToString('0.00', $inv))
        ,@($O_SNAME, 'test_cameraOverShoulder')
        ,@($O_SDEF,  $Shoulder.ToString('0.00', $inv))
    )
    foreach ($s in $strings) {
        $b = [System.Text.Encoding]::ASCII.GetBytes([string]$s[1])
        [Array]::Copy($b, 0, $sec, (0x100 + [int]$s[0]), $b.Length)   # Terminator: Array ist genullt
    }

    # --- Datei vergroessern: padding bis FileAlignment, dann Sektion anhaengen ---
    $hoff = $sectBase + 40 * $nsec
    if (($hoff + 40) -gt (RU32 $script:f ($sectBase + 20))) { throw 'CameraReforged: kein Platz im PE-Header fuer einen weiteren Sektionseintrag.' }
    $raw_size = AlignUp $SEC_SIZE $FA
    $oldLen = $script:f.Length
    $new_raw = AlignUp $oldLen $FA
    $nf = New-Object byte[] ($new_raw + $raw_size)
    [Array]::Copy($script:f, 0, $nf, 0, $oldLen)
    [Array]::Copy($sec, 0, $nf, $new_raw, $sec.Length)
    $script:f = $nf

    # --- PE-Header anpassen (NumberOfSections, SizeOfImage, neuer Sektionsheader) ---
    Patch ($e + 6) ([BitConverter]::GetBytes([uint16]($nsec + 1)))
    Patch ($e + 24 + 56) ([BitConverter]::GetBytes([uint32](AlignUp ($new_rva + $SEC_SIZE) $SA)))
    Clear-CertificateTable
    $sh = New-Object byte[] 40
    [Array]::Copy([System.Text.Encoding]::ASCII.GetBytes('.camr'), 0, $sh, 0, 5)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$SEC_SIZE), 0, $sh, 8, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$new_rva), 0, $sh, 12, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$raw_size), 0, $sh, 16, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$new_raw), 0, $sh, 20, 4)
    [Array]::Copy([byte[]](0x40, 0x00, 0x00, 0xE0), 0, $sh, 36, 4)     # 0xE0000040 = init data | RWX
    Patch $hoff $sh

    # --- Detour auf CVars_Initialize (VA 0x51D9B0 -> Datei 0x11CDB0) ---
    $j = New-Object byte[] 9
    $j[0] = 0xE9
    [Array]::Copy([BitConverter]::GetBytes([int32]($initHook - ($INIT_VA + 5))), 0, $j, 1, 4)
    $j[5] = 0x90; $j[6] = 0x90; $j[7] = 0x90; $j[8] = 0x90
    Patch 0x11CDB0 $j

    # --- Detour auf den Kamera-Fokuspfad (VA 0x6070CB -> Datei 0x2064CB) ---
    $j = New-Object byte[] 6
    $j[0] = 0xE9
    [Array]::Copy([BitConverter]::GetBytes([int32]($heightHook - ($HEIGHT_VA + 5))), 0, $j, 1, 4)
    $j[5] = 0x90
    Patch 0x2064CB $j

    # --- Vorgabewerte der beiden vorhandenen Kamera-CVars umbiegen ---
    # Beide Registrierungen bekommen ihren Standardwert als Textzeiger. Statt
    # der Blizzard-Strings ("1.0" bei VA 0x9E1340, "8.33" bei VA 0xA1E7E0)
    # zeigen sie jetzt auf die Texte im Datenblock. Die CVars selbst existieren
    # im Client, bleiben also unabhaengig davon per /console regelbar.
    $j = New-Object byte[] 5; $j[0] = 0x68
    [Array]::Copy([BitConverter]::GetBytes([int32]($DATA_VA + $O_MAXF)), 0, $j, 1, 4)
    Patch 0x1FD5B2 $j                                  # cameraDistanceMaxFactor, VA 0x5FE1B2
    [Array]::Copy([BitConverter]::GetBytes([int32]($DATA_VA + $O_ZOOM)), 0, $j, 1, 4)
    Patch 0x1FCE36 $j                                  # cameraDistanceMoveSpeed, VA 0x5FDA36

    # --- Schulterversatz: NICHT umgesetzt ---
    # Die Vorlage biegt vier "fld [reg+2E4h]"-Lesestellen (VA 0x969392,
    # 0x96944F, 0x96AAE1, 0x9739D8) auf den Schulterwert um. Diese Stellen
    # gehoeren aber nicht zur Kamera, sondern zum Chat-Fenster
    # (CSimpleMessageScrollFrame: +0x2E4 = timeVisible, +0x2E8 = fadeDuration;
    # 0x9739D8 liegt in der Lua-Methode GetTimeVisible). Umgebogen bekaeme jede
    # Chat-Nachricht den Schulterwert als Anzeigedauer. Darum bleiben diese vier
    # Stellen hier unangetastet; das CVar test_cameraOverShoulder wird zwar
    # registriert und vom Kamera-Hook gelesen, hat aber noch keine Wirkung.
}

# ============================================================
#  Helfer fuer die Client-Info-Patches von MacWarrior
#  Portierung von edit_version.py, edit_revision.py, edit_title.py und
#  edit_date.py. Die Werte fragt der Patcher nach der Auswahl ab (Felder
#  PromptDe/PromptEn/Default/Check bei den Patches) und merkt sie sich in
#  patcher_selection.ini. Alle Felder werden vor dem Schreiben komplett
#  geprueft, damit die EXE nie halb geaendert wird.
# ============================================================
function L([string]$de, [string]$en) { if ($script:lang -eq 'en') { return $en } else { return $de } }

function PatchU16([int64]$offset, [int64]$value) { Patch $offset ([BitConverter]::GetBytes([uint16]$value)) }
function PatchU32([int64]$offset, [int64]$value) { Patch $offset ([BitConverter]::GetBytes([uint32]$value)) }

# Text in ein Feld fester Groesse schreiben, Rest mit Nullbytes auffuellen.
function PatchText([int64]$offset, [int]$size, [string]$text, [System.Text.Encoding]$enc) {
    $t = $enc.GetBytes($text)
    if ($t.Length -gt $size) { throw ('"{0}" passt nicht in das Feld bei 0x{1:X} ({2} Byte).' -f $text, $offset, $size) }
    $b = New-Object byte[] $size
    [Array]::Copy($t, 0, $b, 0, $t.Length)
    Patch $offset $b
}
function PatchAscii([int64]$offset, [int]$size, [string]$text) { PatchText $offset $size $text ([System.Text.Encoding]::ASCII) }
function PatchUtf16([int64]$offset, [int]$size, [string]$text) {
    # Inklusive UTF-16-Nullterminator, daher muessen 2 Byte frei bleiben.
    if (($text.Length + 1) * 2 -gt $size) { throw ('"{0}" passt nicht in das Feld bei 0x{1:X}.' -f $text, $offset) }
    PatchText $offset $size $text ([System.Text.Encoding]::Unicode)
}

# VS_FIXEDFILEINFO der Versionsressource (Datei 0x7576C0):
#   +0x00 Signatur 0xFEEF04BD   +0x08 FileVersionMS    +0x0C FileVersionLS
#   +0x10 ProductVersionMS      +0x14 ProductVersionLS
#   FileVersionLS: unteres Wort = Build (12340), oberes Wort = Patch (5)
$VSFFI = 0x7576C0
function Assert-VersionInfo {
    if ((RU32 $script:f $VSFFI) -ne 4277077181) { throw 'VS_FIXEDFILEINFO nicht an der erwarteten Stelle gefunden.' }
}

function Test-ClientVersion([string]$v) {
    if ($v -notmatch '^\d{1,5}\.\d{1,5}\.\d{1,5}$') { return (L 'Format: drei Zahlen mit Punkten, z.B. 3.3.6' 'Format: three numbers with dots, e.g. 3.3.6') }
    if ($v.Length -gt 7) { return (L 'Hoechstens 7 Zeichen (z.B. 3.3.123).' 'At most 7 characters (e.g. 3.3.123).') }
    $p = $v.Split('.')
    foreach ($x in $p) { if ([int]$x -gt 65535) { return (L 'Jede Zahl darf hoechstens 65535 sein.' 'Each number must be at most 65535.') } }
    if (('Version {0}.{1}' -f [int]$p[0], [int]$p[1]).Length -gt 11) {
        return (L 'Haupt- und Nebenversion passen so nicht in das ProductVersion-Feld (max. z.B. 3.3).' 'Major and minor version do not fit into the ProductVersion field (max. e.g. 3.3).')
    }
    return $null
}

function Set-ClientVersion([string]$v) {
    Assert-VersionInfo
    $p = $v.Split('.')
    $maj = [int]$p[0]; $min = [int]$p[1]; $pat = [int]$p[2]
    $pv = 'Version {0}.{1}' -f $maj, $min
    PatchAscii 0x5F3A08 8 $v                          # Version im Spiel ("3.3.5")
    PatchU32 ($VSFFI + 0x08) ($maj * 65536 + $min)    # FileVersionMS
    PatchU16 ($VSFFI + 0x0E) $pat                     # FileVersionLS oben, Build bleibt
    PatchU32 ($VSFFI + 0x10) ($maj * 65536 + $min)    # ProductVersionMS
    PatchU32 ($VSFFI + 0x14) 0                        # ProductVersionLS
    PatchU16 0x7577F6 ($v.Length + 1)                 # FileVersion: wValueLength (wLength bleibt)
    PatchUtf16 0x757814 30 $v                         # FileVersion-Text
    PatchU16 0x757986 ($pv.Length + 1)                # ProductVersion: wValueLength
    PatchUtf16 0x7579A8 24 $pv                        # ProductVersion-Text ("Version 3.3")
}

function Test-ClientBuild([string]$v) {
    # Server (AzerothCore, TrinityCore) behandeln Builds bis 6141 als Classic-
    # Client (Pre-BC) mit anderem Login-Protokoll - damit kaeme ein 3.3.5-Client
    # nicht mehr auf den Server. Darum erst ab 6142.
    if ($v -notmatch '^\d{1,5}$' -or [int]$v -lt 6142 -or [int]$v -gt 65535) {
        return (L 'Eine Zahl von 6142 bis 65535 (bis 6141 halten Server den Client fuer einen Classic-Client).' 'A number from 6142 to 65535 (up to 6141 servers treat the client as a Classic client).')
    }
    return $null
}

function Set-ClientBuild([string]$v) {
    Assert-VersionInfo
    $r = [int]$v
    PatchU16 0x4C99F0 $r                              # interne Build-Nummer
    PatchAscii 0x5F3A00 6 ([string]$r)                # sichtbare Build-Nummer ("12340")
    PatchU16 ($VSFFI + 0x0C) $r                       # FileVersionLS unten
}

function Test-ClientTitle([string]$v) {
    if ($v -eq '') { return (L 'Der Titel darf nicht leer sein.' 'The title must not be empty.') }
    if ($v -notmatch '^[\x20-\x7E]+$') { return (L 'Nur ASCII-Zeichen (keine Umlaute).' 'ASCII characters only.') }
    if ($v.Length -gt 17) { return (L 'Hoechstens 17 Zeichen.' 'At most 17 characters.') }
    return $null
}

function Set-ClientTitle([string]$v) {
    # Je String-Eintrag der Versionsressource: Text und wValueLength (Zeichen
    # inklusive Nullterminator) im Eintragskopf (+2).
    PatchUtf16 0x7577C0 50 $v                         # FileDescription (Kopf 0x757798)
    PatchU16 0x75779A ($v.Length + 1)
    PatchUtf16 0x757854 36 $v                         # InternalName (Kopf 0x757834)
    PatchU16 0x757836 ($v.Length + 1)
    PatchUtf16 0x757960 36 $v                         # ProductName (Kopf 0x757940)
    PatchU16 0x757942 ($v.Length + 1)
    # Fenstertitel: Text, mit dem WoW sein Hauptfenster anlegt (CreateWindowExA),
    # 20 Byte ASCII inkl. Nullterminator.
    PatchText 0x5E0288 20 $v ([System.Text.Encoding]::ASCII)
    # Danach setzt WoW den Titel zweimal neu (SetWindowTextW-Wrapper bei
    # VA 0x86C650, Aufrufe bei VA 0x76A119 und 0x76B204) - beide Aufrufe
    # werden zu NOPs, damit der eigene Titel stehen bleibt.
    Patch 0x369519 @(0x90, 0x90, 0x90, 0x90, 0x90)
    Patch 0x36A604 @(0x90, 0x90, 0x90, 0x90, 0x90)
}

# Wert: "JJJJ-MM-TT HH:MM:SS" (ohne Sekunden: 00), optional mit " FR" fuer
# franzoesische Monatsnamen. Liefert @(Datum mit Uhrzeit, 'EN'|'FR').
$CLIENT_TIME_ORIG = '23:54:57'
function Get-ClientDateParts([string]$v) {
    if ($v -notmatch '^\s*(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s+(EN|FR|en|fr))?\s*$') { return $null }
    $date = $matches[1]; $hh = $matches[2]; $mm = $matches[3]; $ss = $matches[4]; $lng = 'EN'
    if ($matches[5]) { $lng = $matches[5].ToUpperInvariant() }
    $d = [datetime]::MinValue
    $ok = [datetime]::TryParseExact($date, 'yyyy-MM-dd', [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::None, [ref]$d)
    if (-not $ok) { return $null }
    if (-not $ss) { $ss = '0' }
    if ([int]$hh -gt 23 -or [int]$mm -gt 59 -or [int]$ss -gt 59) { return $null }
    $d = $d.Date.AddHours([int]$hh).AddMinutes([int]$mm).AddSeconds([int]$ss)
    return , @($d, $lng)
}

# Einheitliche Schreibweise eines gueltigen Werts: "JJJJ-MM-TT HH:MM:SS [FR]".
# So vergleicht der Patcher eingegebene, gemerkte und aus der Exe gelesene
# Werte richtig. Ein gemerkter Wert aus einer aelteren Version ohne Uhrzeit
# bekommt die originale 23:54:57.
function Format-ClientDate($parts) {
    $s = $parts[0].ToString('yyyy-MM-dd HH:mm:ss', [System.Globalization.CultureInfo]::InvariantCulture)
    if ($parts[1] -eq 'FR') { $s += ' FR' }
    return $s
}
function ConvertTo-ClientDate([string]$v) {
    if ($v -match '^\s*(\d{4}-\d{2}-\d{2})((?:\s+(?:EN|FR|en|fr))?)\s*$') { $v = $matches[1] + ' ' + $CLIENT_TIME_ORIG + $matches[2] }
    $parts = Get-ClientDateParts $v
    if ($null -eq $parts) { return $v }
    return (Format-ClientDate $parts)
}

# Vorschlag im Dialog: immer jetzt (Datum und Uhrzeit des Rechners), die
# Sprache (FR) vom gemerkten Wert.
function Get-ClientDateSuggestion([string]$saved) {
    $now = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss', [System.Globalization.CultureInfo]::InvariantCulture)
    if ($saved -match '\sFR\s*$') { return "$now FR" }
    return $now
}

function Test-ClientDate([string]$v) {
    $parts = Get-ClientDateParts $v
    if ($null -eq $parts) { return (L 'Format: JJJJ-MM-TT HH:MM oder JJJJ-MM-TT HH:MM:SS, optional mit FR dahinter (z.B. 2026-09-28 14:30 FR).' 'Format: YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS, optionally followed by FR (e.g. 2026-09-28 14:30 FR).') }
    if ($parts[0].Year -lt 1971 -or $parts[0].Year -gt 2105) { return (L 'Das Jahr muss zwischen 1971 und 2105 liegen.' 'The year must be between 1971 and 2105.') }
    return $null
}

function Set-ClientDate([string]$v) {
    $parts = Get-ClientDateParts $v
    $d = $parts[0]
    if ($parts[1] -eq 'FR') {
        $months = @('Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec')
    } else {
        $months = @('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    }
    $text = '{0} {1:00} {2:0000}' -f $months[$d.Month - 1], $d.Day, $d.Year   # immer 11 Zeichen
    foreach ($o in @(0x5F39F4, 0x62F3F3, 0x636F5F)) {
        $old = [System.Text.Encoding]::ASCII.GetString($script:f, $o, 11)
        if ($old -notmatch '^[A-Za-z]{3} \d{2} \d{4}$') { throw ('Unerwartetes Datumsfeld bei 0x{0:X}: {1}' -f $o, $old) }
        PatchAscii $o 11 $text
    }
    # Uhrzeit im Build-Text "WoW [Release] Build 12340 (Jun 24 2010 23:54:57)"
    $old = [System.Text.Encoding]::ASCII.GetString($script:f, 0x62F3FF, 8)
    if ($old -notmatch '^\d\d:\d\d:\d\d$') { throw ('Unerwartetes Zeitfeld bei 0x62F3FF: {0}' -f $old) }
    PatchAscii 0x62F3FF 8 ($d.ToString('HH:mm:ss', [System.Globalization.CultureInfo]::InvariantCulture))
    Patch 0x7578B4 ([System.Text.Encoding]::Unicode.GetBytes(('{0:0000}' -f $d.Year)))   # Jahr im LegalCopyright
    # Zeitstempel im PE-Kopf (TimeDateStamp, Sekunden seit 1970 in UTC), den
    # Analyse-Werkzeuge als Erstellungszeit zeigen. Datum und Uhrzeit gelten
    # als Ortszeit dieses Rechners, so zeigt Windows sie hier wieder genauso an.
    $e = RU32 $script:f 0x3C
    $local = [datetime]::SpecifyKind($d, [System.DateTimeKind]::Local)
    $epoch = [int64]($local.ToUniversalTime() - [datetime]::new(1970, 1, 1, 0, 0, 0, [System.DateTimeKind]::Utc)).TotalSeconds
    if ($epoch -lt 0) { $epoch = 0 }
    Patch ($e + 8) ([BitConverter]::GetBytes([uint32]$epoch))
}

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

# Liest aus dem Ressourcen-Verzeichnis der aktuellen Wow.exe alle RT_ICON-
# Eintraege als "Dateioffset/Groesse". Damit prueft Set-ClientIcon vor dem
# Schreiben, dass jeder Slot wirklich ein Icon-Bild genau dieser Groesse ist -
# ein Bild kann so nie ueber seinen Platz hinaus in andere Daten laufen, auch
# wenn die Exe von einem anderen Werkzeug veraendert wurde.
function Get-IconResourceSlots {
    $list = New-Object System.Collections.Generic.List[string]
    $e = RU32 $script:f 0x3C
    $IB = RU32 $script:f ($e + 24 + 28)
    $rva = RU32 $script:f ($e + 24 + 96 + 2 * 8)        # Datenverzeichnis 2 = Ressourcen
    if ($rva -eq 0) { return , $list }
    $base = ConvertTo-FileOffset ($IB + $rva)
    if ($base -lt 0) { return , $list }
    $HI = [int64]2147483648                             # Bit 31: Unterverzeichnis
    $n1 = (RU16 $script:f ($base + 12)) + (RU16 $script:f ($base + 14))
    for ($i = 0; $i -lt $n1; $i++) {
        $id = RU32 $script:f ($base + 16 + 8 * $i); $p1 = RU32 $script:f ($base + 20 + 8 * $i)
        if ($id -ne 3 -or $p1 -lt $HI) { continue }      # nur RT_ICON
        $d2 = $base + ($p1 - $HI)
        $n2 = (RU16 $script:f ($d2 + 12)) + (RU16 $script:f ($d2 + 14))
        for ($j = 0; $j -lt $n2; $j++) {
            $p2 = RU32 $script:f ($d2 + 20 + 8 * $j)
            if ($p2 -lt $HI) { continue }
            $d3 = $base + ($p2 - $HI)
            $n3 = (RU16 $script:f ($d3 + 12)) + (RU16 $script:f ($d3 + 14))
            for ($k = 0; $k -lt $n3; $k++) {
                $p3 = RU32 $script:f ($d3 + 20 + 8 * $k)
                if ($p3 -ge $HI) { continue }
                $leaf = $base + $p3
                $off = ConvertTo-FileOffset ($IB + (RU32 $script:f $leaf))
                $list.Add(('{0}/{1}' -f $off, (RU32 $script:f ($leaf + 4))))
            }
        }
    }
    return , $list
}

# Relative Pfade gelten ab dem Ordner der Wow.exe (bei -Path kann der ein anderer
# als der Skriptordner sein).
function Resolve-IconPath([string]$v) {
    $p = $v.Trim().Trim('"')
    if (-not [System.IO.Path]::IsPathRooted($p)) { $p = Join-Path (Split-Path -Parent $file) $p }
    return $p
}

function BE32([byte[]]$a, [int]$o) { return ([int64]$a[$o] -shl 24) -bor ([int64]$a[$o + 1] -shl 16) -bor ([int64]$a[$o + 2] -shl 8) -bor [int64]$a[$o + 3] }

# PNG -> @{ W; H; Px = RGBA-Bytes zeilenweise von oben }. Nur nicht-interlaced.
function Read-PngImage([byte[]]$data) {
    $sig = @(0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)
    if ($data.Length -lt 8) { throw (L 'Keine PNG-Datei.' 'Not a PNG file.') }
    for ($i = 0; $i -lt 8; $i++) { if ($data[$i] -ne $sig[$i]) { throw (L 'Keine PNG-Datei.' 'Not a PNG file.') } }
    $idat = New-Object System.IO.MemoryStream
    $pal = $null; $trns = $null
    $w = 0; $h = 0; $depth = 0; $ctype = 0
    $pos = 8
    while ($pos + 12 -le $data.Length) {
        $len = [int](BE32 $data $pos)
        $type = [System.Text.Encoding]::ASCII.GetString($data, $pos + 4, 4)
        $body = $pos + 8
        if ($body + $len + 4 -gt $data.Length) { throw (L 'PNG-Datei ist beschaedigt.' 'PNG file is damaged.') }
        switch ($type) {
            'IHDR' {
                $w = [int](BE32 $data $body); $h = [int](BE32 $data ($body + 4))
                $depth = [int]$data[$body + 8]; $ctype = [int]$data[$body + 9]
                if ($data[$body + 12] -ne 0) { throw (L 'Interlaced PNG wird nicht unterstuetzt.' 'Interlaced PNG is not supported.') }
            }
            'PLTE' { $pal = New-Object byte[] $len; [Array]::Copy($data, $body, $pal, 0, $len) }
            'tRNS' { $trns = New-Object byte[] $len; [Array]::Copy($data, $body, $trns, 0, $len) }
            'IDAT' { $idat.Write($data, $body, $len) }
        }
        if ($type -eq 'IEND') { break }
        $pos = $body + $len + 4
    }
    if ($w -le 0 -or $h -le 0 -or $w -gt 1024 -or $h -gt 1024) { throw (L 'PNG: ungueltige oder zu grosse Abmessungen (max. 1024).' 'PNG: invalid or too large dimensions (max. 1024).') }
    $channels = switch ($ctype) { 0 { 1 } 2 { 3 } 3 { 1 } 4 { 2 } 6 { 4 } default { throw (L 'PNG: unbekannter Farbtyp.' 'PNG: unknown colour type.') } }
    if ($depth -notin @(1, 2, 4, 8, 16)) { throw (L 'PNG: ungueltige Bittiefe.' 'PNG: invalid bit depth.') }
    if ($depth -lt 8 -and $ctype -notin @(0, 3)) { throw (L 'PNG: ungueltige Bittiefe.' 'PNG: invalid bit depth.') }
    if ($ctype -eq 3 -and $null -eq $pal) { throw (L 'PNG: Palette fehlt.' 'PNG: palette missing.') }
    # zlib-Kopf (2 Byte) ueberspringen, dann roher Deflate-Strom
    $idat.Position = 2
    $inf = New-Object System.IO.Compression.DeflateStream($idat, [System.IO.Compression.CompressionMode]::Decompress)
    $outMs = New-Object System.IO.MemoryStream
    $inf.CopyTo($outMs); $inf.Dispose()
    $raw = $outMs.ToArray()
    $bitsPP = $channels * $depth
    $rowBytes = [int][Math]::Floor(($w * $bitsPP + 7) / 8)
    $fb = [Math]::Max(1, [int][Math]::Floor($bitsPP / 8))     # Abstand fuer die Filter
    if ($raw.Length -lt ($rowBytes + 1) * $h) { throw (L 'PNG: Bilddaten unvollstaendig.' 'PNG: image data incomplete.') }
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
    if ($data.Length -lt 40 -or (RU32 $data 0) -ne 40) { throw (L 'ICO: unbekanntes Bitmap-Format.' 'ICO: unknown bitmap format.') }
    $w = [int][BitConverter]::ToInt32($data, 4); $h = [int]([BitConverter]::ToInt32($data, 8) / 2)
    $bpp = RU16 $data 14; $comp = RU32 $data 16; $clrUsed = RU32 $data 32
    if ($w -le 0 -or $h -le 0 -or $w -gt 1024 -or $h -gt 1024) { throw (L 'ICO: ungueltige Abmessungen.' 'ICO: invalid dimensions.') }
    if ($bpp -notin @(1, 4, 8, 16, 24, 32)) { throw (L "ICO: Bittiefe $bpp wird nicht unterstuetzt." "ICO: bit depth $bpp is not supported.") }
    if ($comp -ne 0 -and -not ($comp -eq 3 -and $bpp -ge 16)) { throw (L 'ICO: komprimierte Bitmaps werden nicht unterstuetzt.' 'ICO: compressed bitmaps are not supported.') }
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
    if ($data.Length -lt $andOff) { throw (L 'ICO: Bilddaten unvollstaendig.' 'ICO: image data incomplete.') }
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

# ICO- oder PNG-Datei lesen. Liefert die Bildeintraege (W, H, Rohdaten);
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

# Die vier Bilder fuer die Slots: Hashtable Groesse -> dekodiertes Bild. Einmal
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
}

# RGBA auf SxS umrechnen: Flaechenmittelung mit vormultipliziertem Alpha.
function Resize-Rgba($img, [int]$S) {
    $w = $img.W; $h = $img.H; $src = $img.Px
    if ($w -eq $S -and $h -eq $S) { return , $src }
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
            # ($si/$di statt $s/$d: PowerShell-Variablen sind nicht case-sensitiv, $s waere $S)
            $si = ($srcY * $S + $x) * 4; $di = $xor + ($y * $S + $x) * 4
            $b[$di] = $rgba[$si + 2]; $b[$di + 1] = $rgba[$si + 1]; $b[$di + 2] = $rgba[$si]; $b[$di + 3] = $rgba[$si + 3]
            if ($rgba[$si + 3] -eq 0) { $m = $and + $y * $maskRow + ($x -shr 3); $b[$m] = $b[$m] -bor (0x80 -shr ($x -band 7)) }
        }
    }
    return , $b
}

# Fuer die Erkennung ueber das Wasserzeichen: Der Pfad selbst steht nicht in
# der Exe. Liefert den gemerkten Pfad aus patcher_selection.ini, wenn die
# Datei existiert und genau die Bitmaps ergibt, die in der Exe stecken.
function Get-ClientIconFromExe {
    $saved = (Get-SavedValues)['clienticon']
    if (-not $saved) { return $null }
    $p = Resolve-IconPath $saved
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { return $null }
    $images = Get-IconImages $p
    foreach ($slot in $ICON_SLOTS) {
        $dib = New-IconDib (Resize-Rgba $images[$slot.Size] $slot.Size) $slot.Size
        foreach ($off in $slot.Offsets) {
            for ($i = 0; $i -lt $dib.Length; $i++) { if ($script:f[$off + $i] -ne $dib[$i]) { return $null } }
        }
    }
    return $saved
}

function Test-ClientIcon([string]$v) {
    if ($v.Trim() -eq '') { return (L 'Pfad zu einer .ico- oder .png-Datei angeben.' 'Enter the path to an .ico or .png file.') }
    $p = Resolve-IconPath $v
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { return (L "Datei nicht gefunden: $p" "File not found: $p") }
    try { [void](Get-IconImages $p) } catch { return $_.Exception.Message }
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
    # Erst alle acht Slots gegen das Ressourcen-Verzeichnis pruefen, dann schreiben.
    $res = Get-IconResourceSlots
    foreach ($slot in $ICON_SLOTS) {
        foreach ($off in $slot.Offsets) {
            if (-not $res.Contains(('{0}/{1}' -f $off, (Get-IconDibLength $slot.Size)))) {
                throw ('Icon: Bei Datei 0x{0:X} liegt kein Icon-Bild mit {1} Pixeln - die Icon-Ressourcen dieser Wow.exe sind veraendert.' -f $off, $slot.Size)
            }
        }
    }
    $images = Get-IconImages (Resolve-IconPath $v)
    foreach ($slot in $ICON_SLOTS) {
        $S = $slot.Size
        $dib = New-IconDib (Resize-Rgba $images[$S] $S) $S
        if ($dib.Length -ne (Get-IconDibLength $S)) { throw 'Icon: Bitmap hat die falsche Groesse.' }
        foreach ($off in $slot.Offsets) {
            Assert-Bytes $off ([byte[]](0x28, 0x00, 0x00, 0x00, [byte]$S, 0x00, 0x00, 0x00, [byte](2 * $S), 0x00, 0x00, 0x00, 0x01, 0x00, 0x20, 0x00)) 'Icon'
            Patch $off $dib
        }
    }
}

# ============================================================
#  Helfer fuer den voice.dll-Loader (mod-voicechat, ALPHA)
#  Uebernommen aus Add-VoiceLoader.ps1 aus https://github.com/Raz0r1337/mod-voicechat
#  Dateigroesse und PE-Header bleiben unveraendert. Genutzt wird eine
#  27-Byte-int3-Luecke zwischen zwei Funktionen (VA 0x944B45, Datei 0x543F45);
#  der Sprung am Einstiegspunkt (VA 0x401005: jmp 0x40BA9B, direkt vor
#  __security_init_cookie/__tmainCRTStartup) wird dorthin umgebogen:
#      push "voice.dll" / call [LoadLibraryA] / jmp 0x40BA9B
#  eax/ecx/edx/Flags sind an dieser Stelle tot, ebx/esi/edi/ebp sichert
#  LoadLibraryA selbst. Fehlt die DLL, startet WoW ganz normal.
# ============================================================
function Add-VoiceLoader([string]$DllName) {
    $IB        = 0x400000
    $TEXT_DIFF = 0x400C00          # VA - Dateioffset in .text
    $RDATA_DIFF = 0x401800         # VA - Dateioffset in .rdata
    $JMP_VA    = 0x401005          # jmp in die __tmainCRTStartup-Kette
    $CRT_VA    = 0x40BA9B          # urspruengliches Sprungziel
    $CAVE_VA   = 0x944B45          # int3-Luecke
    $CAVE_LEN  = 27
    $IAT_LLA   = 0x9DF248          # KERNEL32!LoadLibraryA (IAT)
    $jmpOff  = $JMP_VA - $TEXT_DIFF
    $caveOff = $CAVE_VA - $TEXT_DIFF

    # --- Pruefen: Einstiegspunkt, Einstiegscode, freie Luecke, Import ---
    $e = RU32 $script:f 0x3C
    if ((RU32 $script:f ($e + 24 + 16)) -ne ($JMP_VA - 5 - $IB)) { throw 'voice.dll-Loader: unerwarteter Einstiegspunkt.' }
    if ($script:f[$jmpOff - 5] -ne 0xE8 -or $script:f[$jmpOff] -ne 0xE9) { throw 'voice.dll-Loader: Einstiegscode unbekannt.' }
    $target = $JMP_VA + 5 + [BitConverter]::ToInt32($script:f, $jmpOff + 1)
    if ($target -ne $CRT_VA) { throw ('voice.dll-Loader: Einstiegssprung ist bereits umgebogen (0x{0:X}).' -f $target) }
    for ($i = 0; $i -lt $CAVE_LEN; $i++) {
        if ($script:f[$caveOff + $i] -ne 0xCC) { throw 'voice.dll-Loader: Luecke bei 0x944B45 ist belegt.' }
    }
    $thunk = RU32 $script:f ($IAT_LLA - $RDATA_DIFF)
    if ($thunk -ge 2147483648 -or [System.Text.Encoding]::ASCII.GetString($script:f, ($thunk + $IB - $RDATA_DIFF + 2), 12) -cne 'LoadLibraryA') {
        throw 'voice.dll-Loader: IAT-Eintrag LoadLibraryA nicht gefunden.'
    }

    # --- Payload: push str / call [LoadLibraryA] / jmp CRT / "voice.dll\0" ---
    $nameBytes = [System.Text.Encoding]::ASCII.GetBytes($DllName)
    if ($nameBytes.Length -lt 1 -or $nameBytes.Length -gt ($CAVE_LEN - 17)) { throw 'voice.dll-Loader: DLL-Name max. 10 Zeichen.' }
    $p = New-Object System.Collections.Generic.List[byte]
    AddRaw $p @(0x68);       AddLE32 $p ($CAVE_VA + 16)              # push offset Name
    AddRaw $p @(0xFF, 0x15); AddLE32 $p $IAT_LLA                     # call [LoadLibraryA]
    AddRaw $p @(0xE9);       AddLE32 $p ($CRT_VA - ($CAVE_VA + 16))  # jmp urspruengliches Ziel
    AddRaw $p $nameBytes;    AddRaw $p @(0x00)                       # "voice.dll\0"
    Patch $caveOff $p.ToArray()
    Patch ($jmpOff + 1) ([BitConverter]::GetBytes([int32]($CAVE_VA - ($JMP_VA + 5))))
}

# ============================================================
#  Eigene Code-Sektion fuer kleine Code-Hoehlen
#  Wie HD-Portraits und CameraReforged: Padding bis FileAlignment, Sektion
#  am Dateiende anhaengen, PE-Header anpassen (NumberOfSections, SizeOfImage,
#  neuer Sektionsheader, ausfuehrbar, mit -Writable auch beschreibbar).
#  Genutzt vom Doppelsprung, der beschreibbaren Speicher braucht.
#  Liefert @(VA der Sektion, Dateioffset der Sektion).
# ============================================================
function Add-CodeSection([string]$Name, [int]$Size, [switch]$Writable) {
    $e = RU32 $script:f 0x3C
    $nsec = RU16 $script:f ($e + 6)
    $opt = RU16 $script:f ($e + 20)
    $IB = RU32 $script:f ($e + 24 + 28)
    $SA = RU32 $script:f ($e + 24 + 32)
    $FA = RU32 $script:f ($e + 24 + 36)
    $sectBase = $e + 24 + $opt
    $lastSo = $sectBase + 40 * ($nsec - 1)
    $new_rva = AlignUp ((RU32 $script:f ($lastSo + 12)) + (RU32 $script:f ($lastSo + 8))) $SA
    $hoff = $sectBase + 40 * $nsec
    if (($hoff + 40) -gt (RU32 $script:f ($sectBase + 20))) { throw "${Name}: kein Platz im PE-Header fuer einen weiteren Sektionseintrag." }

    $raw_size = AlignUp $Size $FA
    $oldLen = $script:f.Length
    $new_raw = AlignUp $oldLen $FA
    $nf = New-Object byte[] ($new_raw + $raw_size)
    [Array]::Copy($script:f, 0, $nf, 0, $oldLen)
    for ($i = $new_raw; $i -lt $nf.Length; $i++) { $nf[$i] = 0xCC }
    $script:f = $nf

    Patch ($e + 6) ([BitConverter]::GetBytes([uint16]($nsec + 1)))
    Patch ($e + 24 + 56) ([BitConverter]::GetBytes([uint32](AlignUp ($new_rva + $Size) $SA)))
    Clear-CertificateTable
    $sh = New-Object byte[] 40
    $nm = [System.Text.Encoding]::ASCII.GetBytes($Name)
    [Array]::Copy($nm, 0, $sh, 0, [Math]::Min(8, $nm.Length))
    [Array]::Copy([BitConverter]::GetBytes([uint32]$Size), 0, $sh, 8, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$new_rva), 0, $sh, 12, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$raw_size), 0, $sh, 16, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$new_raw), 0, $sh, 20, 4)
    if ($Writable) {
        [Array]::Copy([byte[]](0x20, 0x00, 0x00, 0xE0), 0, $sh, 36, 4) # 0xE0000020 = Code | ausfuehrbar | lesbar | schreibbar
    } else {
        [Array]::Copy([byte[]](0x20, 0x00, 0x00, 0x60), 0, $sh, 36, 4) # 0x60000020 = Code | ausfuehrbar | lesbar
    }
    Patch $hoff $sh
    return , @(($IB + $new_rva), $new_raw)
}

# ============================================================
#  Code-Hoehle am Ende von .text
#  Hinter dem Code von .text liegen 77 freie Bytes (Datei 0x5DD7B3-0x5DD7FF,
#  Nullen). WorldFrame-Absturzfix (38 Byte) und NPC-Ausblenden (37 Byte)
#  teilen sie sich. Liefert @(VA, Dateioffset) der Hoehle.
# ============================================================
$TEXT_CAVE = @{ worldcrash = 0x5DD7B3; nofade = 0x5DD7D9 }

function Get-CodeCave([string]$Id, [int]$Size) {
    $off = $TEXT_CAVE[$Id]
    for ($i = 0; $i -lt $Size; $i++) {
        if ($script:f[$off + $i] -ne 0) { throw ('Code-Hoehle bei 0x{0:X} ist belegt.' -f ($off + $i)) }
    }
    # VirtualSize von .text bis hinter die Hoehle anheben, damit der Lader sie
    # sicher mit einblendet (bleibt innerhalb von SizeOfRawData).
    $e = RU32 $script:f 0x3C
    $textSo = $e + 24 + (RU16 $script:f ($e + 20))
    $need = $off + $Size - (RU32 $script:f ($textSo + 20))
    if ((RU32 $script:f ($textSo + 8)) -lt $need) { Patch ($textSo + 8) ([BitConverter]::GetBytes([uint32]$need)) }
    return , @(($off + 0x400C00), $off)
}

# Relativer Sprung/Aufruf: Opcode + rel32 von $FromVA nach $ToVA.
function Get-Rel32([byte[]]$Op, [int64]$FromVA, [int64]$ToVA) {
    $b = New-Object byte[] ($Op.Length + 4)
    [Array]::Copy($Op, 0, $b, 0, $Op.Length)
    [Array]::Copy([BitConverter]::GetBytes([int32]($ToVA - ($FromVA + $b.Length))), 0, $b, $Op.Length, 4)
    return , $b
}

function Assert-Bytes([int64]$Off, [byte[]]$Expected, [string]$What) {
    for ($i = 0; $i -lt $Expected.Length; $i++) {
        if ($script:f[$Off + $i] -ne $Expected[$i]) { throw "${What}: Code bei Datei 0x$('{0:X}' -f $Off) unbekannt." }
    }
}

# ============================================================
#  WorldFrame-Absturzfix (0x539wowmod, Alyst3r)
#  Die Funktion bei VA 0x81D510 laeuft ueber Dreiecke aus Index-Tripeln
#  (WORDs) und rechnet Index minus Basis ([ebp+10h]) in eine Vertex-Adresse
#  um. Ist ein Index kleiner als die Basis, landet die Adresse vor dem Puffer
#  und der Client stuerzt ab. Die Hoehle prueft die drei Indizes des ersten
#  Dreiecks und springt in dem Fall zum Funktionsende (VA 0x81D66E).
#  Einstieg ist das jae bei VA 0x81D51B, das genau dorthin springt (leere
#  Liste) - es wird in der Hoehle nachgebildet, der Stack ist derselbe.
#  edx ist hier frei (wird erst bei VA 0x81D547 gesetzt).
#  Neu umgesetzt: Im Original sind die Sprungweiten der drei jg falsch
#  berechnet, ausserdem ist diese Form kuerzer (38 statt 59 Byte).
# ============================================================
function Add-WorldFrameCrashFix {
    $HOOK_VA = 0x81D51B; $BACK_VA = 0x81D521; $EXIT_VA = 0x81D66E
    Assert-Bytes ($HOOK_VA - 0x400C00) @(0x0F, 0x83, 0x4D, 0x01, 0x00, 0x00) 'WorldFrame-Absturzfix'
    $loc = Get-CodeCave 'worldcrash' 38
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
    AddRaw $c @(0x73, 0x1F)                      # jae Ausgang (leere Liste, wie im Original)
    AddRaw $c @(0x8B, 0x55, 0x10)                # mov edx, [ebp+10h]   (Basis)
    AddRaw $c @(0x0F, 0xB7, 0x07)                # movzx eax, word [edi]
    AddRaw $c @(0x3B, 0xD0, 0x7F, 0x15)          # cmp edx, eax / jg Ausgang
    AddRaw $c @(0x0F, 0xB7, 0x47, 0x02)          # movzx eax, word [edi+2]
    AddRaw $c @(0x3B, 0xD0, 0x7F, 0x0D)          # cmp edx, eax / jg Ausgang
    AddRaw $c @(0x0F, 0xB7, 0x47, 0x04)          # movzx eax, word [edi+4]
    AddRaw $c @(0x3B, 0xD0, 0x7F, 0x05)          # cmp edx, eax / jg Ausgang
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $BACK_VA)     # jmp zurueck
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $EXIT_VA)     # Ausgang: jmp Funktionsende
    if ($c.Count -ne 38) { throw 'WorldFrame-Absturzfix: Hoehle hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    $hook = (Get-Rel32 @(0xE9) $HOOK_VA $CAVE) + [byte[]](0x90)
    Patch ($HOOK_VA - 0x400C00) ([byte[]]$hook)
}

# ============================================================
#  Kein Ausblenden fuer NPCs mit UNIT_FLAG2_DO_NOT_FADE_IN (0x539wowmod, Alyst3r)
#  Beim Entfernen eines Objekts (Funktion bei VA 0x743D50) blendet der
#  Client das Modell normalerweise aus. Die Hoehle prueft vorher: Ist es
#  ein CGUnit (vtable 0xA34D90, Spieler haben eine eigene) und ist in
#  UNIT_FIELD_FLAGS_2 das Bit 0x20 (DO_NOT_FADE_IN) gesetzt, geht es direkt
#  zum Zweig ohne Ausblenden (VA 0x743DE3), sonst normal weiter. Das Flag
#  muss der Server setzen. Ersetzt werden die 5 Byte "mov eax, [esi] /
#  mov edx, [eax+40h]" bei VA 0x743DA3; edx ist bis dahin frei.
# ============================================================
function Add-NoFadeOutFlag {
    $HOOK_VA = 0x743DA3; $BACK_VA = 0x743DA8; $NOFADE_VA = 0x743DE3
    Assert-Bytes ($HOOK_VA - 0x400C00) @(0x8B, 0x06, 0x8B, 0x50, 0x40) 'NPC-Ausblenden'
    $loc = Get-CodeCave 'nofade' 37
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
    AddRaw $c @(0x8B, 0x06)                                  # mov eax, [esi]          (Original)
    AddRaw $c @(0x3D); AddLE32 $c 0xA34D90                   # cmp eax, CGUnit-vtable
    AddRaw $c @(0x75, 0x0F)                                  # jne normal
    AddRaw $c @(0x8B, 0x96, 0xD0, 0x00, 0x00, 0x00)          # mov edx, [esi+0D0h]     (Unit-Felder)
    AddRaw $c @(0xF6, 0x82, 0xD8, 0x00, 0x00, 0x00, 0x20)    # test byte [edx+0D8h], 20h (FLAGS_2)
    AddRaw $c @(0x75, 0x08)                                  # jnz ohne Ausblenden
    AddRaw $c @(0x8B, 0x50, 0x40)                            # normal: mov edx, [eax+40h] (Original)
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $BACK_VA)     # jmp zurueck
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $NOFADE_VA)   # jmp ohne Ausblenden
    if ($c.Count -ne 37) { throw 'NPC-Ausblenden: Hoehle hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    Patch ($HOOK_VA - 0x400C00) (Get-Rel32 @(0xE9) $HOOK_VA $CAVE)
}

# ============================================================
#  Doppelsprung (nach 0x539wowmod, Alyst3r)
#  Die Sprungfunktion (VA 0x9883F0) lehnt bei VA 0x98842A jeden Sprung ab,
#  solange eines der Flags ROOT (0x800), FALLING (0x1000) oder FLYING
#  (0x2000000) gesetzt ist. 0x539wowmod ersetzt sie per DLL und zaehlt
#  Sprungladungen mit. Hier dasselbe als Code-Hoehle: Beim Sprung vom Boden
#  wird der Zaehler auf N gesetzt, in der Luft ist ein Sprung erlaubt,
#  solange der Zaehler > 0 ist (dann -1). ROOT und FLYING sperren weiter.
#  Der Zaehler ist ein Byte in derselben Sektion, die darum beschreibbar
#  sein muss - deshalb eine eigene Sektion (.djump) statt der Luecke in .text.
# ============================================================
function Add-DoubleJump([int]$Extra) {
    $HOOK_VA = 0x98842A; $OK_VA = 0x988435; $FAIL_VA = 0x988479
    Assert-Bytes ($HOOK_VA - 0x400C00) @(0x8B, 0x7E, 0x44, 0xF7, 0xC7, 0x00, 0x18, 0x00, 0x02, 0x75, 0x44) 'Doppelsprung'
    $loc = Add-CodeSection '.djump' 0x44 -Writable
    $CAVE = $loc[0]; $DATA = $CAVE + 0x40
    $c = New-Object System.Collections.Generic.List[byte]
    AddRaw $c @(0x8B, 0x7E, 0x44)                                  # mov edi, [esi+44h]      (Original)
    AddRaw $c @(0xF7, 0xC7, 0x00, 0x10, 0x00, 0x00)                # test edi, 1000h         (in der Luft?)
    AddRaw $c @(0x75, 0x14)                                        # jnz Luft
    AddRaw $c @(0xC6, 0x05); AddLE32 $c $DATA; AddRaw $c @([byte]$Extra)   # mov byte [Zaehler], N
    AddRaw $c @(0xF7, 0xC7, 0x00, 0x18, 0x00, 0x02)                # test edi, 2001800h      (Original)
    AddRaw $c @(0x75, 0x21)                                        # jnz Abbruch
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $OK_VA)        # jmp weiter
    # Luft:
    AddRaw $c @(0xF7, 0xC7, 0x00, 0x08, 0x00, 0x02)                # test edi, 2000800h      (ROOT/FLYING)
    AddRaw $c @(0x75, 0x14)                                        # jnz Abbruch
    AddRaw $c @(0x80, 0x3D); AddLE32 $c $DATA; AddRaw $c @(0x00)   # cmp byte [Zaehler], 0
    AddRaw $c @(0x74, 0x0B)                                        # je Abbruch
    AddRaw $c @(0xFE, 0x0D); AddLE32 $c $DATA                      # dec byte [Zaehler]
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $OK_VA)        # jmp weiter
    # Abbruch:
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $FAIL_VA)      # jmp Sprung ablehnen
    AddRaw $c @(0x00, 0x00, 0x00, 0x00)                            # Zaehler, beginnt bei 0
    if ($c.Count -ne 0x44) { throw 'Doppelsprung: Hoehle hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    $hook = (Get-Rel32 @(0xE9) $HOOK_VA $CAVE) + [byte[]](0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    Patch ($HOOK_VA - 0x400C00) ([byte[]]$hook)
}

function Test-DoubleJump([string]$v) {
    if ($v -notmatch '^[1-9]$') { return (L 'Eine Zahl von 1 bis 9.' 'A number from 1 to 9.') }
    return $null
}

# ============================================================
#  Schrift-Glyphen-Fix (tb, ported by St0ny)
#  Blizzard-Fehler im Glyphen-Cache: Texte (vor allem Zahlen, Schaden,
#  Chat) zeigen zeitweise falsche, abgeschnittene oder fremde Zeichen.
#  Der Cache legt die gerenderten Zeichen auf 256 Pixel breiten Zeilen
#  von Textur-Seiten ab und verdraengt alte, wenn er voll ist. Dabei
#  passieren mehrere Fehler, die WotLK-Extensions (Fork von tb)
#  per DLL behebt - hier dasselbe in einer eigenen Sektion (.glyph):
#  - CreateNewDesc (VA 0x6C5120): Der Merker "breiteste freie Luecke"
#    einer Zeile ([Zeile+0]) wird nie aktualisiert. Der Hook rechnet ihn
#    vor jedem Einfuegen aus der Zeichenliste der Zeile neu aus
#    (Knoten: Start +30h, Ende +34h, naechster [Knoten+Linkoffset+4]).
#  - ClearInstanceData (VA 0x6C6B90): Die Merker "benutzte Seiten" (+60h)
#    und "Seite verdraengt" (+64h) des Strings bleiben stehen - werden
#    jetzt mit geloescht. Die Original-Funktion liest beide nicht.
#  - CheckGeometry (VA 0x6C7480, an Ort und Stelle neu geschrieben): Ist
#    eine Seite des Strings verdraengt worden, wird er immer komplett
#    geloescht und neu aufgebaut (das Original loescht ihn nur, wenn
#    eine weitere Pruefung bei VA 0x6C29A0 fehlschlaegt).
#  - RenderBatch (VA 0x6C4AD0): Vor dem Zeichnen werden alle Strings des
#    Batches neu aufgebaut; verdraengt das einen anderen String, folgen
#    bis zu drei weitere Durchgaenge nur fuer die verdraengten.
#  - TextureCallback (VA 0x6C9F50): Beim Hochladen einer Seite (Befehl 1)
#    wird der Upload-Puffer (VA 0xC7D328, 128 KB) erst geleert, sonst
#    landen Reste alter Zeichen auf der neuen Seite.
#  Code-Sprungadressen werden beim Patchen aus der Lage der Sektion
#  berechnet ($CAVE). Die Sektion ist nur ausfuehrbar, nicht beschreibbar.
# ============================================================
function Add-GlyphCacheFix {
    $NEWDESC = 0x6C5120; $CLEAR = 0x6C6B90; $CHECK = 0x6C7480; $RENDER = 0x6C4AD0; $TEXCB = 0x6C9F50
    Assert-Bytes ($NEWDESC - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C) 'Glyphen-Fix'
    Assert-Bytes ($CLEAR - 0x400C00) @(0x56, 0x57, 0x8B, 0xF1, 0x6A, 0x00) 'Glyphen-Fix'
    Assert-Bytes ($CHECK - 0x400C00) @(
        0x56, 0x8B, 0xF1, 0x83, 0x7E, 0x64, 0x00, 0x74, 0x1E, 0x8B, 0x46, 0x48, 0x8B, 0x4E, 0x44, 0x50,
        0xE8, 0x0B, 0xB5, 0xFF, 0xFF, 0x85, 0xC0, 0x75, 0x07, 0x8B, 0xCE, 0xE8, 0xF0, 0xF6, 0xFF, 0xFF,
        0xC7, 0x46, 0x64, 0x00, 0x00, 0x00, 0x00, 0x8B, 0xCE, 0xE8, 0x62, 0x06, 0x00, 0x00, 0x33, 0xC0,
        0x39, 0x86, 0xB0, 0x00, 0x00, 0x00, 0xC7, 0x86, 0xD4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x0F, 0x95, 0xC0, 0x5E, 0xC3
    ) 'Glyphen-Fix'
    Assert-Bytes ($RENDER - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x20) 'Glyphen-Fix'
    Assert-Bytes ($TEXCB - 0x400C00) @(0x55, 0x8B, 0xEC, 0x51, 0x83, 0x7D, 0x08, 0x01) 'Glyphen-Fix'
    $loc = Add-CodeSection '.glyph' 0xDF
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
    # --- CreateNewDesc (VA 0x6C5120), ecx = Zeile: breiteste freie Luecke neu berechnen ---
    # newdesc:
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0x31, 0xD2)                                    # xor edx,edx
    AddRaw $c @(0x8B, 0x71, 0x0C)                              # mov esi,[ecx+0xC]
    AddRaw $c @(0x8B, 0x79, 0x04)                              # mov edi,[ecx+4]
    # nd_loop:
    AddRaw $c @(0x85, 0xF6)                                    # test esi,esi
    AddRaw $c @(0x74, 0x21)                                    # jz nd_end
    AddRaw $c @(0xF7, 0xC6, 0x01, 0x00, 0x00, 0x00)            # test esi,1
    AddRaw $c @(0x75, 0x19)                                    # jnz nd_end
    AddRaw $c @(0x8B, 0x5E, 0x30)                              # mov ebx,[esi+0x30]
    AddRaw $c @(0x39, 0xD3)                                    # cmp ebx,edx
    AddRaw $c @(0x76, 0x08)                                    # jbe nd_skip
    AddRaw $c @(0x29, 0xD3)                                    # sub ebx,edx
    AddRaw $c @(0x39, 0xC3)                                    # cmp ebx,eax
    AddRaw $c @(0x76, 0x02)                                    # jbe nd_skip
    AddRaw $c @(0x89, 0xD8)                                    # mov eax,ebx
    # nd_skip:
    AddRaw $c @(0x8B, 0x56, 0x34)                              # mov edx,[esi+0x34]
    AddRaw $c @(0x42)                                          # inc edx
    AddRaw $c @(0x8B, 0x74, 0x3E, 0x04)                        # mov esi,[esi+edi+4]
    AddRaw $c @(0xEB, 0xDB)                                    # jmp nd_loop
    # nd_end:
    AddRaw $c @(0xBB, 0x00, 0x01, 0x00, 0x00)                  # mov ebx,0x100
    AddRaw $c @(0x39, 0xD3)                                    # cmp ebx,edx
    AddRaw $c @(0x76, 0x08)                                    # jbe nd_store
    AddRaw $c @(0x29, 0xD3)                                    # sub ebx,edx
    AddRaw $c @(0x39, 0xC3)                                    # cmp ebx,eax
    AddRaw $c @(0x76, 0x02)                                    # jbe nd_store
    AddRaw $c @(0x89, 0xD8)                                    # mov eax,ebx
    # nd_store:
    AddRaw $c @(0x89, 0x01)                                    # mov [ecx],eax
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x0C)                              # sub esp,0xC
    AddRaw $c @(0xE9); AddLE32 $c (0x6C5126 - ($CAVE + 0x53))  # jmp 0x6C5126  (CreateNewDesc+6)
    # --- ClearInstanceData (VA 0x6C6B90), ecx = String: Seiten-Merker loeschen ---
    # clear:
    AddRaw $c @(0x83, 0x61, 0x60, 0x00)                        # and dword ptr [ecx+0x60],0
    AddRaw $c @(0x83, 0x61, 0x64, 0x00)                        # and dword ptr [ecx+0x64],0
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x89, 0xCE)                                    # mov esi,ecx
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0xE9); AddLE32 $c (0x6C6B96 - ($CAVE + 0x66))  # jmp 0x6C6B96  (ClearInstanceData+6)
    # --- RenderBatch (VA 0x6C4AD0), ecx = Batch: Geometrie vor dem Zeichnen neu aufbauen ---
    # render:
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xCB)                                    # mov ebx,ecx
    AddRaw $c @(0x31, 0xED)                                    # xor ebp,ebp
    # rb_pass:
    AddRaw $c @(0x31, 0xFF)                                    # xor edi,edi
    AddRaw $c @(0x8B, 0x73, 0x24)                              # mov esi,[ebx+0x24]
    # rb_str:
    AddRaw $c @(0x85, 0xF6)                                    # test esi,esi
    AddRaw $c @(0x74, 0x25)                                    # jz rb_end
    AddRaw $c @(0xF7, 0xC6, 0x01, 0x00, 0x00, 0x00)            # test esi,1
    AddRaw $c @(0x75, 0x1D)                                    # jnz rb_end
    AddRaw $c @(0x8B, 0x46, 0x64)                              # mov eax,[esi+0x64]
    AddRaw $c @(0x85, 0xED)                                    # test ebp,ebp
    AddRaw $c @(0x74, 0x04)                                    # jz rb_do
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x74, 0x09)                                    # jz rb_next
    # rb_do:
    AddRaw $c @(0x09, 0xC7)                                    # or edi,eax
    AddRaw $c @(0x89, 0xF1)                                    # mov ecx,esi
    AddRaw $c @(0xE8); AddLE32 $c (0x6C7480 - ($CAVE + 0x93))  # call 0x6C7480  (CheckGeometry)
    # rb_next:
    AddRaw $c @(0x8B, 0x43, 0x1C)                              # mov eax,[ebx+0x1C]
    AddRaw $c @(0x8B, 0x74, 0x06, 0x04)                        # mov esi,[esi+eax+4]
    AddRaw $c @(0xEB, 0xD7)                                    # jmp rb_str
    # rb_end:
    AddRaw $c @(0x85, 0xFF)                                    # test edi,edi
    AddRaw $c @(0x74, 0x06)                                    # jz rb_out
    AddRaw $c @(0x45)                                          # inc ebp
    AddRaw $c @(0x83, 0xFD, 0x04)                              # cmp ebp,4
    AddRaw $c @(0x72, 0xC8)                                    # jb rb_pass
    # rb_out:
    AddRaw $c @(0x89, 0xD9)                                    # mov ecx,ebx
    AddRaw $c @(0x5D)                                          # pop ebp
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x20)                              # sub esp,0x20
    AddRaw $c @(0xE9); AddLE32 $c (0x6C4AD6 - ($CAVE + 0xB7))  # jmp 0x6C4AD6  (RenderBatch+6)
    # --- TextureCallback (VA 0x6C9F50, cdecl): Upload-Puffer vor dem Fuellen leeren ---
    # tex:
    AddRaw $c @(0x83, 0x7C, 0x24, 0x04, 0x01)                  # cmp dword ptr [esp+4],1
    AddRaw $c @(0x75, 0x14)                                    # jne tx_go
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x51)                                          # push ecx
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xBF, 0x28, 0xD3, 0xC7, 0x00)                  # mov edi,0xC7D328  (Glyphen-Upload-Puffer)
    AddRaw $c @(0xB9, 0x00, 0x80, 0x00, 0x00)                  # mov ecx,0x8000
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0xF3, 0xAB)                                    # rep stosd
    AddRaw $c @(0x58)                                          # pop eax
    AddRaw $c @(0x59)                                          # pop ecx
    AddRaw $c @(0x5F)                                          # pop edi
    # tx_go:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x51)                                          # push ecx
    AddRaw $c @(0x83, 0x7D, 0x08, 0x01)                        # cmp dword ptr [ebp+8],1
    AddRaw $c @(0xE9); AddLE32 $c (0x6C9F58 - ($CAVE + 0xDF))  # jmp 0x6C9F58  (TextureCallback+8)
    if ($c.Count -ne 0xDF) { throw 'Glyphen-Fix: Sektion hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    # Einspruenge: jmp in die Sektion, Rest der ueberschriebenen Befehle mit nop
    Patch ($NEWDESC - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $NEWDESC ($CAVE + 0x0)) + [byte[]](0x90)))
    Patch ($CLEAR - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $CLEAR ($CAVE + 0x53)) + [byte[]](0x90)))
    Patch ($RENDER - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $RENDER ($CAVE + 0x66)) + [byte[]](0x90)))
    Patch ($TEXCB - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $TEXCB ($CAVE + 0xB7)) + [byte[]](0x90, 0x90, 0x90)))
    # CheckGeometry neu (45 statt 69 Byte, Rest int3). Der Aufruf von
    # ClearInstanceData laeuft ueber den Hook oben und loescht +60h/+64h mit.
    $k = New-Object System.Collections.Generic.List[byte]
    AddRaw $k @(0x56)                                          # push esi
    AddRaw $k @(0x89, 0xCE)                                    # mov esi,ecx
    AddRaw $k @(0x83, 0x7E, 0x64, 0x00)                        # cmp dword ptr [esi+0x64],0
    AddRaw $k @(0x74, 0x07)                                    # je L
    AddRaw $k @(0x89, 0xF1)                                    # mov ecx,esi
    AddRaw $k @(0xE8, 0x00, 0xF7, 0xFF, 0xFF)                  # call 0x6C6B90  (ClearInstanceData)
    # L:
    AddRaw $k @(0x89, 0xF1)                                    # mov ecx,esi
    AddRaw $k @(0xE8, 0x79, 0x06, 0x00, 0x00)                  # call 0x6C7B10  (CreateGeometry)
    AddRaw $k @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $k @(0x89, 0x46, 0x64)                              # mov [esi+0x64],eax
    AddRaw $k @(0x89, 0x86, 0xD4, 0x00, 0x00, 0x00)            # mov [esi+0xD4],eax
    AddRaw $k @(0x39, 0x86, 0xB0, 0x00, 0x00, 0x00)            # cmp [esi+0xB0],eax
    AddRaw $k @(0x0F, 0x95, 0xC0)                              # setne al
    AddRaw $k @(0x5E)                                          # pop esi
    AddRaw $k @(0xC3)                                          # ret
    while ($k.Count -lt 69) { $k.Add([byte]0xCC) }
    Patch ($CHECK - 0x400C00) $k.ToArray()
}

# ============================================================
#  Aktionstasten gedrueckt halten zum Wiederholen (tb, ported by St0ny)
#  Haelt man die Taste einer Aktionsleisten-Belegung (ACTIONBUTTON1-12,
#  die Hauptleiste mit Seiten- und Bonusleisten-Wechsel wie im Fork),
#  loest der Client die Aktion wiederholt aus - wie in WotLK-Extensions
#  (Fork von tb) mit actionButtonHoldRepeat = 2 (dauerhaft):
#  - ExecKey (VA 0x563150): Beim Druecken merkt sich der Hook Taste,
#    Aktions-Slot und Zeit (bis 8 Tasten gleichzeitig). Beim Loslassen
#    wird der Eintrag geloescht; hat er schon wiederholt, unterdrueckt er
#    das normale Ausloesen beim Loslassen (UseAction-Hook).
#  - OnWorldRender (VA 0x4F8EA0): Nach jedem Bild prueft der Hook jede
#    gehaltene Taste: fruehestens 500 ms nach dem Druecken, nicht waehrend
#    der Spieler zaubert oder kanalisiert (Zauberleiste: laufender Zauber
#    [Spieler+A6Ch] bis [Spieler+A7Ch], Kanalisierung [Spieler+A80h] bis
#    [Spieler+A88h], wie UnitCastingInfo/UnitChannelInfo) oder ein Zauber
#    auf sein Ziel wartet ([0xD3F4E4]), nicht waehrend der Abklingzeit
#    (GetCooldown, auch globale), erst 100 ms nachdem die Aktion wieder
#    bereit ist und hoechstens alle 100 ms ruft er UseAction auf.
#  - Fokus-Ereignis (EventRegisterEx, Ereignis 2, beim ersten Druck
#    angemeldet): Verliert das Fenster den Fokus, werden alle gehaltenen
#    Tasten vergessen (sonst wiederholt es ohne Loslassen ewig).
#  Die Zustaende stehen in derselben Sektion (.hrep), die darum
#  beschreibbar sein muss: +0 acht Eintraege zu 32 Byte (Taste, Slot,
#  Druckzeit, letzte Wiederholung, bereit seit, wiederholt, aktiv),
#  +100h Unterdrueck-Merker, +104h Ereignis angemeldet, +108h GUID (0),
#  +110h leerer Text, +114h "ACTIONBUTTON". Code ab +120h.
# ============================================================
function Add-HoldRepeat {
    $EXEC = 0x563150; $USE = 0x5ABBC0; $RENDER = 0x4F8EA0
    Assert-Bytes ($EXEC - 0x400C00) @(0x55, 0x8B, 0xEC, 0x81, 0xEC, 0xC4, 0x00, 0x00, 0x00) 'Gedrueckt halten'
    Assert-Bytes ($USE - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C) 'Gedrueckt halten'
    Assert-Bytes ($RENDER - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x34) 'Gedrueckt halten'
    $loc = Add-CodeSection '.hrep' 0x473 -Writable
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
    for ($i = 0; $i -lt 0x114; $i++) { $c.Add([byte]0) }                 # Zustaende, beginnen bei 0
    AddRaw $c ([System.Text.Encoding]::ASCII.GetBytes('ACTIONBUTTON'))  # +114h, ohne Null
    # --- ExecKey (VA 0x563150, thiscall: mods, slot, isDown, argC, keyMode) ---
    # exec:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x81, 0xEC, 0x04, 0x01, 0x00, 0x00)            # sub esp,0x104
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x89, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov [ebp-0x104],ecx
    AddRaw $c @(0xC6, 0x85, 0x00, 0xFF, 0xFF, 0xFF, 0x00)      # mov byte ptr [ebp-0x100],0
    AddRaw $c @(0x68, 0x80, 0x00, 0x00, 0x00)                  # push 0x80
    AddRaw $c @(0x8D, 0x85, 0x00, 0xFF, 0xFF, 0xFF)            # lea eax,[ebp-0x100]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xFF, 0x75, 0x0C)                              # push dword ptr [ebp+0xC]
    AddRaw $c @(0xFF, 0x75, 0x18)                              # push dword ptr [ebp+0x18]
    AddRaw $c @(0xE8); AddLE32 $c (0x5622E0 - ($CAVE + 0x150)) # call 0x5622E0  (GetReducedKeyBinding)
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0x47, 0x01, 0x00, 0x00)            # jz ex_orig
    AddRaw $c @(0xFF, 0x75, 0x18)                              # push dword ptr [ebp+0x18]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0x8B, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov ecx,[ebp-0x104]
    AddRaw $c @(0xE8); AddLE32 $c (0x55E470 - ($CAVE + 0x167)) # call 0x55E470  (GetCommandForBinding)
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0x30, 0x01, 0x00, 0x00)            # jz ex_orig
    AddRaw $c @(0x89, 0xC6)                                    # mov esi,eax
    AddRaw $c @(0xBF); AddLE32 $c ($CAVE + 0x114)              # mov edi,strab
    AddRaw $c @(0xB9, 0x0C, 0x00, 0x00, 0x00)                  # mov ecx,12
    # ex_cmp:
    AddRaw $c @(0x8A, 0x06)                                    # mov al,[esi]
    AddRaw $c @(0x3C, 0x61)                                    # cmp al,0x61
    AddRaw $c @(0x72, 0x06)                                    # jb ex_c1
    AddRaw $c @(0x3C, 0x7A)                                    # cmp al,0x7A
    AddRaw $c @(0x77, 0x02)                                    # ja ex_c1
    AddRaw $c @(0x2C, 0x20)                                    # sub al,0x20
    # ex_c1:
    AddRaw $c @(0x3A, 0x07)                                    # cmp al,[edi]
    AddRaw $c @(0x0F, 0x85, 0x10, 0x01, 0x00, 0x00)            # jne ex_orig
    AddRaw $c @(0x46)                                          # inc esi
    AddRaw $c @(0x47)                                          # inc edi
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xE7)                                    # jnz ex_cmp
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    # ex_dig:
    AddRaw $c @(0x0F, 0xB6, 0x16)                              # movzx edx,byte ptr [esi]
    AddRaw $c @(0x83, 0xEA, 0x30)                              # sub edx,0x30
    AddRaw $c @(0x83, 0xFA, 0x09)                              # cmp edx,9
    AddRaw $c @(0x77, 0x11)                                    # ja ex_num
    AddRaw $c @(0x6B, 0xC0, 0x0A)                              # imul eax,eax,10
    AddRaw $c @(0x01, 0xD0)                                    # add eax,edx
    AddRaw $c @(0x83, 0xF8, 0x0C)                              # cmp eax,12
    AddRaw $c @(0x0F, 0x87, 0xF0, 0x00, 0x00, 0x00)            # ja ex_orig
    AddRaw $c @(0x46)                                          # inc esi
    AddRaw $c @(0xEB, 0xE4)                                    # jmp ex_dig
    # ex_num:
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0xE5, 0x00, 0x00, 0x00)            # jz ex_orig
    AddRaw $c @(0x8D, 0x58, 0xFF)                              # lea ebx,[eax-1]
    AddRaw $c @(0x83, 0x3D, 0xA0, 0xE5, 0xC1, 0x00, 0x00)      # cmp dword ptr [0xC1E5A0],0  (Seitenwechsel aktiv)
    AddRaw $c @(0x74, 0x07)                                    # je ex_p1
    AddRaw $c @(0xBA, 0x01, 0x00, 0x00, 0x00)                  # mov edx,1
    AddRaw $c @(0xEB, 0x07)                                    # jmp ex_p2
    # ex_p1:
    AddRaw $c @(0x8B, 0x15, 0x98, 0xE5, 0xC1, 0x00)            # mov edx,dword ptr [0xC1E598]  (aktuelle Seite)
    AddRaw $c @(0x42)                                          # inc edx
    # ex_p2:
    AddRaw $c @(0x83, 0xFA, 0x01)                              # cmp edx,1
    AddRaw $c @(0x75, 0x0D)                                    # jne ex_p3
    AddRaw $c @(0x8B, 0x0D, 0x9C, 0xE5, 0xC1, 0x00)            # mov ecx,dword ptr [0xC1E59C]  (Bonusleiste)
    AddRaw $c @(0x85, 0xC9)                                    # test ecx,ecx
    AddRaw $c @(0x74, 0x03)                                    # jz ex_p3
    AddRaw $c @(0x8D, 0x51, 0x06)                              # lea edx,[ecx+6]
    # ex_p3:
    AddRaw $c @(0x4A)                                          # dec edx
    AddRaw $c @(0x6B, 0xD2, 0x0C)                              # imul edx,edx,12
    AddRaw $c @(0x01, 0xD3)                                    # add ebx,edx
    AddRaw $c @(0x8B, 0x55, 0x0C)                              # mov edx,[ebp+0xC]
    AddRaw $c @(0xE8, 0xC5, 0x00, 0x00, 0x00)                  # call find
    AddRaw $c @(0x83, 0x7D, 0x10, 0x00)                        # cmp dword ptr [ebp+0x10],0
    AddRaw $c @(0x74, 0x5D)                                    # je ex_up
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x75, 0x0D)                                    # jnz ex_init
    AddRaw $c @(0xE8, 0xD3, 0x00, 0x00, 0x00)                  # call findfree
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0x94, 0x00, 0x00, 0x00)            # jz ex_orig
    # ex_init:
    AddRaw $c @(0x89, 0xC6)                                    # mov esi,eax
    AddRaw $c @(0x89, 0x5E, 0x04)                              # mov [esi+4],ebx
    AddRaw $c @(0xE8); AddLE32 $c (0x86AE20 - ($CAVE + 0x215)) # call 0x86AE20  (OsGetAsyncTimeMs)
    AddRaw $c @(0x89, 0x46, 0x08)                              # mov [esi+8],eax
    AddRaw $c @(0x89, 0x46, 0x0C)                              # mov [esi+12],eax
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0x89, 0x46, 0x10)                              # mov [esi+16],eax
    AddRaw $c @(0x89, 0x46, 0x14)                              # mov [esi+20],eax
    AddRaw $c @(0x8B, 0x55, 0x0C)                              # mov edx,[ebp+0xC]
    AddRaw $c @(0x89, 0x16)                                    # mov [esi],edx
    AddRaw $c @(0xC7, 0x46, 0x18, 0x01, 0x00, 0x00, 0x00)      # mov dword ptr [esi+24],1
    AddRaw $c @(0x83, 0x3D); AddLE32 $c ($CAVE + 0x104); AddRaw $c @(0x00) # cmp dword ptr [evreg],0
    AddRaw $c @(0x75, 0x67)                                    # jne ex_orig
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x104); AddRaw $c @(0x01, 0x00, 0x00, 0x00) # mov dword ptr [evreg],1
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0x68); AddLE32 $c ($CAVE + 0x2EF)              # push focus
    AddRaw $c @(0x6A, 0x02)                                    # push 2
    AddRaw $c @(0xE8); AddLE32 $c (0x47D3C0 - ($CAVE + 0x252)) # call 0x47D3C0  (EventRegisterEx)
    AddRaw $c @(0x83, 0xC4, 0x10)                              # add esp,16
    AddRaw $c @(0xEB, 0x48)                                    # jmp ex_orig
    # ex_up:
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x74, 0x44)                                    # jz ex_orig
    AddRaw $c @(0xC7, 0x40, 0x18, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [eax+24],0
    AddRaw $c @(0x83, 0x78, 0x14, 0x00)                        # cmp dword ptr [eax+20],0
    AddRaw $c @(0x74, 0x37)                                    # je ex_orig
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x01, 0x00, 0x00, 0x00) # mov dword ptr [suppress],1
    AddRaw $c @(0xFF, 0x75, 0x18)                              # push dword ptr [ebp+0x18]
    AddRaw $c @(0xFF, 0x75, 0x14)                              # push dword ptr [ebp+0x14]
    AddRaw $c @(0xFF, 0x75, 0x10)                              # push dword ptr [ebp+0x10]
    AddRaw $c @(0xFF, 0x75, 0x0C)                              # push dword ptr [ebp+0xC]
    AddRaw $c @(0xFF, 0x75, 0x08)                              # push dword ptr [ebp+8]
    AddRaw $c @(0x8B, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov ecx,[ebp-0x104]
    AddRaw $c @(0xE8, 0x1F, 0x00, 0x00, 0x00)                  # call exec_tramp
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x00, 0x00, 0x00, 0x00) # mov dword ptr [suppress],0
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x89, 0xEC)                                    # mov esp,ebp
    AddRaw $c @(0x5D)                                          # pop ebp
    AddRaw $c @(0xC2, 0x14, 0x00)                              # ret 0x14
    # ex_orig:
    AddRaw $c @(0x8B, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov ecx,[ebp-0x104]
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x89, 0xEC)                                    # mov esp,ebp
    AddRaw $c @(0x5D)                                          # pop ebp
    # exec_tramp:  (ex_orig laeuft direkt hier hinein)
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x81, 0xEC, 0xC4, 0x00, 0x00, 0x00)            # sub esp,0xC4
    AddRaw $c @(0xE9); AddLE32 $c (0x563159 - ($CAVE + 0x2B9)) # jmp 0x563159  (ExecKey+9)
    # --- Hilfsfunktionen: Eintrag zu edx (Taste) / freien Eintrag suchen ---
    # find:
    AddRaw $c @(0xB8); AddLE32 $c ($CAVE + 0x0)                # mov eax,held
    AddRaw $c @(0xB9, 0x08, 0x00, 0x00, 0x00)                  # mov ecx,8
    # f_l:
    AddRaw $c @(0x83, 0x78, 0x18, 0x00)                        # cmp dword ptr [eax+24],0
    AddRaw $c @(0x74, 0x04)                                    # je f_n
    AddRaw $c @(0x39, 0x10)                                    # cmp [eax],edx
    AddRaw $c @(0x74, 0x08)                                    # je f_r
    # f_n:
    AddRaw $c @(0x83, 0xC0, 0x20)                              # add eax,32
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xF0)                                    # jnz f_l
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    # f_r:
    AddRaw $c @(0xC3)                                          # ret
    # findfree:
    AddRaw $c @(0xB8); AddLE32 $c ($CAVE + 0x0)                # mov eax,held
    AddRaw $c @(0xB9, 0x08, 0x00, 0x00, 0x00)                  # mov ecx,8
    # ff_l:
    AddRaw $c @(0x83, 0x78, 0x18, 0x00)                        # cmp dword ptr [eax+24],0
    AddRaw $c @(0x74, 0x08)                                    # je ff_r
    AddRaw $c @(0x83, 0xC0, 0x20)                              # add eax,32
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xF4)                                    # jnz ff_l
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    # ff_r:
    AddRaw $c @(0xC3)                                          # ret
    # --- Fokus-Ereignis (cdecl): alle gehaltenen Tasten vergessen ---
    # focus:
    AddRaw $c @(0xB8); AddLE32 $c ($CAVE + 0x0)                # mov eax,held
    AddRaw $c @(0xB9, 0x08, 0x00, 0x00, 0x00)                  # mov ecx,8
    # fo_l:
    AddRaw $c @(0xC7, 0x40, 0x18, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [eax+24],0
    AddRaw $c @(0x83, 0xC0, 0x20)                              # add eax,32
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xF3)                                    # jnz fo_l
    AddRaw $c @(0xB8, 0x01, 0x00, 0x00, 0x00)                  # mov eax,1
    AddRaw $c @(0xC3)                                          # ret
    # --- UseAction (VA 0x5ABBC0, cdecl: slot, guid*, button) ---
    # use:
    AddRaw $c @(0x83, 0x3D); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x00) # cmp dword ptr [suppress],0
    AddRaw $c @(0x74, 0x0B)                                    # je use_tramp
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x00, 0x00, 0x00, 0x00) # mov dword ptr [suppress],0
    AddRaw $c @(0xC3)                                          # ret
    # use_tramp:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x0C)                              # sub esp,0xC
    AddRaw $c @(0xE9); AddLE32 $c (0x5ABBC6 - ($CAVE + 0x32B)) # jmp 0x5ABBC6  (UseAction+6)
    # --- OnWorldRender (VA 0x4F8EA0, thiscall): Original, danach Wiederholung pruefen ---
    # render:
    AddRaw $c @(0xE8, 0x08, 0x00, 0x00, 0x00)                  # call render_tramp
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xE8, 0x0D, 0x00, 0x00, 0x00)                  # call update
    AddRaw $c @(0x58)                                          # pop eax
    AddRaw $c @(0xC3)                                          # ret
    # render_tramp:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x34)                              # sub esp,0x34
    AddRaw $c @(0xE9); AddLE32 $c (0x4F8EA6 - ($CAVE + 0x343)) # jmp 0x4F8EA6  (OnWorldRender+6)
    # --- Wiederholung: Zauberleiste/Kanalisierung des Spielers, dann jede gehaltene Taste pruefen ---
    # update:
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x83, 0xEC, 0x10)                              # sub esp,16
    AddRaw $c @(0x89, 0xE3)                                    # mov ebx,esp
    AddRaw $c @(0xE8); AddLE32 $c (0x86AE20 - ($CAVE + 0x351)) # call 0x86AE20  (OsGetAsyncTimeMs)
    AddRaw $c @(0x89, 0xC5)                                    # mov ebp,eax
    AddRaw $c @(0xE8); AddLE32 $c (0x4D3790 - ($CAVE + 0x358)) # call 0x4D3790  (Spieler-GUID)
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0x68, 0xD4, 0x2C, 0xA2, 0x00)                  # push 0xA22CD4
    AddRaw $c @(0x6A, 0x10)                                    # push 0x10
    AddRaw $c @(0x52)                                          # push edx
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xE8); AddLE32 $c (0x4D4DB0 - ($CAVE + 0x368)) # call 0x4D4DB0  (Objekt zur GUID)
    AddRaw $c @(0x83, 0xC4, 0x14)                              # add esp,0x14
    AddRaw $c @(0xB9, 0x01, 0x00, 0x00, 0x00)                  # mov ecx,1
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x74, 0x28)                                    # jz cast_done
    AddRaw $c @(0x83, 0xB8, 0x6C, 0x0A, 0x00, 0x00, 0x00)      # cmp dword ptr [eax+0xA6C],0
    AddRaw $c @(0x74, 0x0A)                                    # je cast_chan
    AddRaw $c @(0x89, 0xEA)                                    # mov edx,ebp
    AddRaw $c @(0x2B, 0x90, 0x7C, 0x0A, 0x00, 0x00)            # sub edx,[eax+0xA7C]
    AddRaw $c @(0x78, 0x15)                                    # js cast_done
    # cast_chan:
    AddRaw $c @(0x83, 0xB8, 0x80, 0x0A, 0x00, 0x00, 0x00)      # cmp dword ptr [eax+0xA80],0
    AddRaw $c @(0x74, 0x0A)                                    # je cast_no
    AddRaw $c @(0x89, 0xEA)                                    # mov edx,ebp
    AddRaw $c @(0x2B, 0x90, 0x88, 0x0A, 0x00, 0x00)            # sub edx,[eax+0xA88]
    AddRaw $c @(0x78, 0x02)                                    # js cast_done
    # cast_no:
    AddRaw $c @(0x31, 0xC9)                                    # xor ecx,ecx
    # cast_done:
    AddRaw $c @(0x89, 0x4B, 0x0C)                              # mov [ebx+12],ecx
    AddRaw $c @(0xBE); AddLE32 $c ($CAVE + 0x0)                # mov esi,held
    AddRaw $c @(0xBF, 0x08, 0x00, 0x00, 0x00)                  # mov edi,8
    # up_l:
    AddRaw $c @(0x83, 0x7E, 0x18, 0x00)                        # cmp dword ptr [esi+24],0
    AddRaw $c @(0x0F, 0x84, 0xAE, 0x00, 0x00, 0x00)            # je up_n
    AddRaw $c @(0x89, 0xE8)                                    # mov eax,ebp
    AddRaw $c @(0x2B, 0x46, 0x08)                              # sub eax,[esi+8]
    AddRaw $c @(0x3D, 0xF4, 0x01, 0x00, 0x00)                  # cmp eax,500
    AddRaw $c @(0x0F, 0x82, 0x9E, 0x00, 0x00, 0x00)            # jb up_n
    AddRaw $c @(0x83, 0x3D, 0xE4, 0xF4, 0xD3, 0x00, 0x00)      # cmp dword ptr [0xD3F4E4],0  (laufender Zauber)
    AddRaw $c @(0x75, 0x06)                                    # jne up_busy
    AddRaw $c @(0x83, 0x7B, 0x0C, 0x00)                        # cmp dword ptr [ebx+12],0
    AddRaw $c @(0x74, 0x0C)                                    # je up_nc
    # up_busy:
    AddRaw $c @(0xC7, 0x46, 0x10, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [esi+16],0
    AddRaw $c @(0xE9, 0x83, 0x00, 0x00, 0x00)                  # jmp up_n
    # up_nc:
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0x89, 0x03)                                    # mov [ebx],eax
    AddRaw $c @(0x89, 0x43, 0x04)                              # mov [ebx+4],eax
    AddRaw $c @(0x89, 0x43, 0x08)                              # mov [ebx+8],eax
    AddRaw $c @(0x8D, 0x43, 0x08)                              # lea eax,[ebx+8]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0x8D, 0x43, 0x04)                              # lea eax,[ebx+4]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0xFF, 0x76, 0x04)                              # push dword ptr [esi+4]
    AddRaw $c @(0xE8); AddLE32 $c (0x5A8E40 - ($CAVE + 0x3F9)) # call 0x5A8E40  (GetCooldown)
    AddRaw $c @(0x83, 0xC4, 0x10)                              # add esp,16
    AddRaw $c @(0x8B, 0x43, 0x04)                              # mov eax,[ebx+4]
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x7E, 0x11)                                    # jle up_ready
    AddRaw $c @(0x89, 0xE9)                                    # mov ecx,ebp
    AddRaw $c @(0x2B, 0x0B)                                    # sub ecx,[ebx]
    AddRaw $c @(0x39, 0xC1)                                    # cmp ecx,eax
    AddRaw $c @(0x73, 0x09)                                    # jae up_ready
    AddRaw $c @(0xC7, 0x46, 0x10, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [esi+16],0
    AddRaw $c @(0xEB, 0x4D)                                    # jmp up_n
    # up_ready:
    AddRaw $c @(0x83, 0x7E, 0x10, 0x00)                        # cmp dword ptr [esi+16],0
    AddRaw $c @(0x75, 0x03)                                    # jne up_r2
    AddRaw $c @(0x89, 0x6E, 0x10)                              # mov [esi+16],ebp
    # up_r2:
    AddRaw $c @(0x89, 0xE8)                                    # mov eax,ebp
    AddRaw $c @(0x2B, 0x46, 0x10)                              # sub eax,[esi+16]
    AddRaw $c @(0x83, 0xF8, 0x64)                              # cmp eax,100
    AddRaw $c @(0x72, 0x3A)                                    # jb up_n
    AddRaw $c @(0x89, 0xE8)                                    # mov eax,ebp
    AddRaw $c @(0x2B, 0x46, 0x0C)                              # sub eax,[esi+12]
    AddRaw $c @(0x83, 0xF8, 0x64)                              # cmp eax,100
    AddRaw $c @(0x72, 0x30)                                    # jb up_n
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0xA3); AddLE32 $c ($CAVE + 0x108)              # mov dword ptr [guid],eax
    AddRaw $c @(0xA3); AddLE32 $c ($CAVE + 0x10C)              # mov dword ptr [guid+4],eax
    AddRaw $c @(0xA3); AddLE32 $c ($CAVE + 0x110)              # mov dword ptr [btn],eax
    AddRaw $c @(0x68); AddLE32 $c ($CAVE + 0x110)              # push btn
    AddRaw $c @(0x68); AddLE32 $c ($CAVE + 0x108)              # push guid
    AddRaw $c @(0xFF, 0x76, 0x04)                              # push dword ptr [esi+4]
    AddRaw $c @(0xE8, 0xCC, 0xFE, 0xFF, 0xFF)                  # call use_tramp
    AddRaw $c @(0x83, 0xC4, 0x0C)                              # add esp,12
    AddRaw $c @(0x89, 0x6E, 0x0C)                              # mov [esi+12],ebp
    AddRaw $c @(0xC7, 0x46, 0x14, 0x01, 0x00, 0x00, 0x00)      # mov dword ptr [esi+20],1
    # up_n:
    AddRaw $c @(0x83, 0xC6, 0x20)                              # add esi,32
    AddRaw $c @(0x4F)                                          # dec edi
    AddRaw $c @(0x0F, 0x85, 0x3E, 0xFF, 0xFF, 0xFF)            # jnz up_l
    AddRaw $c @(0x83, 0xC4, 0x10)                              # add esp,16
    AddRaw $c @(0x5D)                                          # pop ebp
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0xC3)                                          # ret
    if ($c.Count -ne 0x473) { throw 'Gedrueckt halten: Sektion hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    Patch ($EXEC - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $EXEC ($CAVE + 0x120)) + [byte[]](0x90, 0x90, 0x90, 0x90)))
    Patch ($USE - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $USE ($CAVE + 0x30C)) + [byte[]](0x90)))
    Patch ($RENDER - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $RENDER ($CAVE + 0x32B)) + [byte[]](0x90)))
}

# ============================================================
#  Icons im Text pixelgenau (tb, ported by St0ny)
#  Texte koennen Icons enthalten (|T...|t, z.B. Raidmarker, Waehrungen,
#  Questsymbole). Ihre Groesse und Lage rechnet der Client in Pixeln mit
#  Nachkommastellen aus - bei skalierten Schriften landen die Icons dann
#  zwischen zwei Pixeln und werden unscharf oder um einen Pixel verzerrt.
#  Der Hook hinter ParseEmbeddedTexture (VA 0x6C0E80, cdecl: Text, Info,
#  Hoehe, Skalierung, Schrifthoehe) rundet - wenn das Parsen geklappt hat
#  und die Hoehe von der Schrifthoehe abweicht - Hoehe [Info+18h] und
#  Breite [Info+1Ch] auf ganze Pixel (mindestens 1) und den Versatz
#  [Info+20h] / [Info+24h] auf ganze Pixel. Gerundet wird wie im Fork mit
#  floor(x + 0,5): Rundungsmodus der FPU kurz auf "abrunden", danach wieder
#  zurueck. Eigene Sektion (.isnap), nur ausfuehrbar.
# ============================================================
function Add-IconPixelSnap {
    $PARSE = 0x6C0E80
    Assert-Bytes ($PARSE - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x44) 'Icons pixelgenau'
    $loc = Add-CodeSection '.isnap' 0xB3
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
    # snap:  Original aufrufen (Argumente neu ablegen), danach runden
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xE8, 0x8E, 0x00, 0x00, 0x00)                  # call tramp
    AddRaw $c @(0x83, 0xC4, 0x14)                              # add esp,0x14
    AddRaw $c @(0x84, 0xC0)                                    # test al,al
    AddRaw $c @(0x0F, 0x84, 0x81, 0x00, 0x00, 0x00)            # jz out
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xD9, 0x44, 0x24, 0x14)                        # fld dword ptr [esp+0x14]
    AddRaw $c @(0xD8, 0x5C, 0x24, 0x1C)                        # fcomp dword ptr [esp+0x1C]
    AddRaw $c @(0xDF, 0xE0)                                    # fnstsw ax
    AddRaw $c @(0x80, 0xE4, 0x45)                              # and ah,0x45
    AddRaw $c @(0x80, 0xFC, 0x40)                              # cmp ah,0x40
    AddRaw $c @(0x74, 0x6D)                                    # je out_pop
    AddRaw $c @(0x8B, 0x74, 0x24, 0x10)                        # mov esi,[esp+0x10]
    AddRaw $c @(0x83, 0xEC, 0x08)                              # sub esp,8
    AddRaw $c @(0xD9, 0x3C, 0x24)                              # fnstcw word ptr [esp]
    AddRaw $c @(0x66, 0x8B, 0x04, 0x24)                        # mov ax,word ptr [esp]
    AddRaw $c @(0x66, 0x25, 0xFF, 0xF3)                        # and ax,0xF3FF
    AddRaw $c @(0x66, 0x0D, 0x00, 0x04)                        # or ax,0x400
    AddRaw $c @(0x66, 0x89, 0x44, 0x24, 0x02)                  # mov word ptr [esp+2],ax
    AddRaw $c @(0xC7, 0x44, 0x24, 0x04, 0x00, 0x00, 0x00, 0x3F) # mov dword ptr [esp+4],0x3F000000
    AddRaw $c @(0xD9, 0x6C, 0x24, 0x02)                        # fldcw word ptr [esp+2]
    AddRaw $c @(0xD9, 0x46, 0x18)                              # fld dword ptr [esi+0x18]
    AddRaw $c @(0xD8, 0x44, 0x24, 0x04)                        # fadd dword ptr [esp+4]
    AddRaw $c @(0xD9, 0xFC)                                    # frndint
    AddRaw $c @(0xD9, 0xE8)                                    # fld1
    AddRaw $c @(0xDB, 0xF1)                                    # fcomi st(0),st(1)
    AddRaw $c @(0xDA, 0xD1)                                    # fcmovbe st(0),st(1)
    AddRaw $c @(0xD9, 0x5E, 0x18)                              # fstp dword ptr [esi+0x18]
    AddRaw $c @(0xDD, 0xD8)                                    # fstp st(0)
    AddRaw $c @(0xD9, 0x46, 0x1C)                              # fld dword ptr [esi+0x1C]
    AddRaw $c @(0xD8, 0x44, 0x24, 0x04)                        # fadd dword ptr [esp+4]
    AddRaw $c @(0xD9, 0xFC)                                    # frndint
    AddRaw $c @(0xD9, 0xE8)                                    # fld1
    AddRaw $c @(0xDB, 0xF1)                                    # fcomi st(0),st(1)
    AddRaw $c @(0xDA, 0xD1)                                    # fcmovbe st(0),st(1)
    AddRaw $c @(0xD9, 0x5E, 0x1C)                              # fstp dword ptr [esi+0x1C]
    AddRaw $c @(0xDD, 0xD8)                                    # fstp st(0)
    AddRaw $c @(0xD9, 0x46, 0x20)                              # fld dword ptr [esi+0x20]
    AddRaw $c @(0xD8, 0x44, 0x24, 0x04)                        # fadd dword ptr [esp+4]
    AddRaw $c @(0xD9, 0xFC)                                    # frndint
    AddRaw $c @(0xD9, 0x5E, 0x20)                              # fstp dword ptr [esi+0x20]
    AddRaw $c @(0xD9, 0x46, 0x24)                              # fld dword ptr [esi+0x24]
    AddRaw $c @(0xD8, 0x44, 0x24, 0x04)                        # fadd dword ptr [esp+4]
    AddRaw $c @(0xD9, 0xFC)                                    # frndint
    AddRaw $c @(0xD9, 0x5E, 0x24)                              # fstp dword ptr [esi+0x24]
    AddRaw $c @(0xD9, 0x2C, 0x24)                              # fldcw word ptr [esp]
    AddRaw $c @(0x83, 0xC4, 0x08)                              # add esp,8
    # out_pop:
    AddRaw $c @(0x58)                                          # pop eax
    # out:
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0xC3)                                          # ret
    # tramp: ueberschriebene Befehle, weiter im Original
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x44)                              # sub esp,0x44
    AddRaw $c @(0xE9); AddLE32 $c (0x6C0E86 - ($CAVE + 0xB3))  # jmp 0x6C0E86  (ParseEmbeddedTexture+6)
    if ($c.Count -ne 0xB3) { throw 'Icons pixelgenau: Sektion hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    Patch ($PARSE - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $PARSE ($CAVE + 0x0)) + [byte[]](0x90)))
}

# ============================================================
#  Wasserzeichen
#  Jede gepatchte Wow.exe bekommt einen Text, an dem der Patcher sie eindeutig
#  als seine eigene erkennt: So vermischt er nie Patches mit denen anderer
#  Patcher und kann seinen Patchstand auch ohne patcher_state.ini aus der Exe
#  auslesen. Dass sich die Herkunft damit auch belegen laesst, ist nur ein
#  Nebeneffekt. Der Text steht im Fuellbereich hinter der .tls-Sektion (Datei
#  0x72DE19-0x72DFFF, 487 Byte Nullen): ausserhalb der VirtualSize, wird also
#  nie geladen, und kein Patch nutzt diesen Bereich. Die Dateigroesse bleibt
#  gleich. Geschrieben wird ueber Patch(), beim Zuruecknehmen verschwindet das
#  Wasserzeichen also wieder.
# ============================================================
$WATERMARK_OFF = 0x72DE20
$WATERMARK = 'Patched with St0nys AIO WoW.exe Patcher by St0ny (Raz0r1337) - https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher'
# Erkannt wird nur dieser Anfang - der Rest (Link) darf sich zwischen Versionen aendern.
$WATERMARK_MARK = 'Patched with St0nys AIO WoW.exe Patcher'

function Add-Watermark {
    $b = [System.Text.Encoding]::ASCII.GetBytes($WATERMARK)
    for ($i = 0; $i -le $b.Length; $i++) {
        if ($script:f[$WATERMARK_OFF + $i] -ne 0) { throw ('Wasserzeichen: Bereich bei 0x{0:X} ist belegt.' -f ($WATERMARK_OFF + $i)) }
    }
    Patch $WATERMARK_OFF $b
}

# ============================================================
#  Patchstand aus der Exe ermitteln (Wasserzeichen + Original-Byte-Tabelle)
#  Ob eine Wow.exe mit diesem Patcher gepatcht wurde, zeigt das Wasserzeichen.
#  Passt der Hash aus patcher_state.ini, geht es ueber die Zustandsdatei
#  (schneller Weg). Sonst ermittelt der Patcher den Patchstand aus der Exe
#  selbst: Die Tabelle $ORIGINAL_TABLE (am Ende der Patch-Definitionen)
#  enthaelt fuer jeden Patch die Original-Bytes an allen Stellen, die er
#  beschreibt. Ein Patch gilt als eingespielt, wenn eine seiner eigenen
#  Stellen (die kein anderer Patch beschreibt) vom Original abweicht. Werte
#  (Sprunghoehe, Build-Datum ...) liest Decode des Patches aus der Exe. Fuer
#  das Original werden alle Stellen zurueckgeschrieben und angehaengte
#  Sektionen abgeschnitten; das Ergebnis muss exakt den Original-Hash haben.
# ============================================================
function Test-Watermark([byte[]]$data) {
    $b = [System.Text.Encoding]::ASCII.GetBytes($WATERMARK_MARK)
    if ($data.Length -lt $WATERMARK_OFF + $b.Length) { return $false }
    for ($i = 0; $i -lt $b.Length; $i++) { if ($data[$WATERMARK_OFF + $i] -ne $b[$i]) { return $false } }
    return $true
}

# Tabelle einmal einlesen: Zeilen "size;<Laenge>" und "<Id>;<Offset hex>;<Bytes hex>;<1 = nur dieser Patch>"
function Get-OriginalTable {
    if ($script:origTable) { return $script:origTable }
    $t = @{ Size = [int64]0; Entries = (New-Object System.Collections.Generic.List[object]) }
    foreach ($l in ($ORIGINAL_TABLE -split "`r?`n")) {
        if ($l -match '^size;(\d+)$') { $t.Size = [int64]$matches[1] }
        elseif ($l -match '^([A-Za-z0-9_]+);([0-9A-F]+);([0-9A-F]+);([01])$') {
            $t.Entries.Add(@{ Id = $matches[1]; Off = [Convert]::ToInt64($matches[2], 16); Bytes = (ConvertFrom-Hex $matches[3]); Own = ($matches[4] -eq '1') })
        }
    }
    $script:origTable = $t
    return $t
}

# Original aus einer gepatchten Exe zurueckgewinnen. $null, wenn das nicht exakt klappt.
function Restore-FromTable([byte[]]$data) {
    $t = Get-OriginalTable
    if ($t.Size -le 0 -or $data.Length -lt $t.Size) { return $null }
    $o = New-Object byte[] $t.Size
    [Array]::Copy($data, 0, $o, 0, $t.Size)
    foreach ($e in $t.Entries) { [Array]::Copy($e.Bytes, 0, $o, $e.Off, $e.Bytes.Length) }
    if ((Get-Sha256 $o) -ne $EXPECTED_HASH) { return $null }
    return , $o
}

# Ids der Patches, deren eigene Stellen vom Original abweichen (in Menue-Reihenfolge).
function Find-AppliedPatches([byte[]]$data) {
    $hit = @{}
    foreach ($e in (Get-OriginalTable).Entries) {
        if (-not $e.Own -or $hit.ContainsKey($e.Id)) { continue }
        for ($i = 0; $i -lt $e.Bytes.Length; $i++) {
            if ($data[$e.Off + $i] -ne $e.Bytes[$i]) { $hit[$e.Id] = $true; break }
        }
    }
    $ids = @()
    foreach ($p in $patches) { if ($hit.ContainsKey($p.Id)) { $ids += $p.Id } }
    return , $ids
}

# Hilfen fuer Decode: Text aus der Exe lesen, VA in Dateioffset umrechnen.
function Read-AsciiZ([int64]$off, [int]$max) {
    $s = ''
    for ($i = 0; $i -lt $max; $i++) { $b = $script:f[$off + $i]; if ($b -eq 0) { break }; $s += [char]$b }
    return $s
}
function Read-Utf16Z([int64]$off, [int]$max) {
    $s = ''
    for ($i = 0; $i + 1 -lt $max; $i += 2) { $c = RU16 $script:f ($off + $i); if ($c -eq 0) { break }; $s += [char]$c }
    return $s
}
function ConvertTo-FileOffset([int64]$va) {
    $e = RU32 $script:f 0x3C
    $nsec = RU16 $script:f ($e + 6)
    $IB = RU32 $script:f ($e + 24 + 28)
    $sectBase = $e + 24 + (RU16 $script:f ($e + 20))
    for ($i = 0; $i -lt $nsec; $i++) {
        $so = $sectBase + 40 * $i
        $rva = RU32 $script:f ($so + 12); $raw = RU32 $script:f ($so + 20); $rs = RU32 $script:f ($so + 16)
        if ($va -ge $IB + $rva -and $va -lt $IB + $rva + $rs) { return $raw + ($va - $IB - $rva) }
    }
    return -1
}
function Get-ClientDateFromExe {
    $t = [System.Text.Encoding]::ASCII.GetString($script:f, 0x5F39F4, 11)
    if ($t -notmatch '^([A-Za-z]{3}) (\d{2}) (\d{4})$') { return $null }
    $mon = $matches[1]; $day = $matches[2]; $year = $matches[3]   # vor dem naechsten -match sichern
    $en = @('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    $fr = @('Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec')
    $m = [array]::IndexOf($en, $mon); $suffix = ''
    if ($m -lt 0) { $m = [array]::IndexOf($fr, $mon); $suffix = ' FR' }
    if ($m -lt 0) { return $null }
    # Monate, die in beiden Sprachen gleich heissen (Jan, Mar, Jun, ...), verraten
    # die Sprache nicht - dann gilt die aus dem gemerkten Wert.
    if ($suffix -eq '' -and $fr[$m] -eq $en[$m] -and ((Get-SavedValues)['clientdate'] -match '\sFR\s*$')) { $suffix = ' FR' }
    $time = [System.Text.Encoding]::ASCII.GetString($script:f, 0x62F3FF, 8)
    if ($time -notmatch '^\d\d:\d\d:\d\d$') { $time = $CLIENT_TIME_ORIG }
    return (ConvertTo-ClientDate ('{0}-{1:00}-{2} {3}{4}' -f $year, ($m + 1), $day, $time, $suffix))
}
function Get-DoubleJumpFromExe {
    $hook = 0x98842A - 0x400C00
    if ($script:f[$hook] -ne 0xE9) { return $null }
    $cave = ConvertTo-FileOffset (0x98842A + 5 + [BitConverter]::ToInt32($script:f, $hook + 1))
    if ($cave -lt 0 -or $script:f[$cave + 11] -ne 0xC6) { return $null }
    return [string]$script:f[$cave + 17]
}

# ============================================================
#  Original-Byte-Tabelle erzeugen (Entwickler, Parameter -BuildTable)
#  Spielt auf Kopien der originalen Wow.exe alle Patches ein - alle
#  zusammen und jeden einzeln (Sektionsheader an der ersten freien Stelle) -
#  und merkt sich je
#  Patch alle Stellen im Original, die er beschreibt. Stellen, die nur ein
#  Patch beschreibt, bekommen die Markierung 1 (fuer die Erkennung).
#  Dazu kommt der Pseudo-Eintrag "pe": NumberOfSections, SizeOfImage, das
#  Security-Verzeichnis (Signatur-Verweis) und die
#  freien Sektionsheader-Slots. Welcher Patch seine Sektion in welchem Slot
#  anlegt, haengt von der Kombination ab - so werden alle Slots unabhaengig
#  davon zurueckgesetzt und gelten fuer keinen Patch als eigene Stelle.
#  Das Ergebnis ersetzt den Block $ORIGINAL_TABLE in diesem Skript.
# ============================================================
function Invoke-BuildTable {
    $orig = [System.IO.File]::ReadAllBytes($file)
    if ((Get-Sha256 $orig) -ne $EXPECTED_HASH) { Write-Host 'BuildTable: braucht die originale Wow.exe (-Path).'; exit 1 }
    $ranges = @{}
    $allIds = @($patches | ForEach-Object { $_.Id })
    $configs = New-Object System.Collections.Generic.List[object]
    $configs.Add($allIds)
    foreach ($id in $allIds) { $configs.Add(@($id)) }
    $n = 0
    foreach ($cfg in $configs) {
        $n++
        Write-Host ("  Konfiguration {0}/{1}" -f $n, $configs.Count)
        $script:f = [byte[]]$orig.Clone()
        $script:VALUES = @{}
        foreach ($p in $patches) { if ($p.Check) { $script:VALUES[$p.Id] = $p.Default } }
        $script:writes.Clear()
        foreach ($p in $patches) {
            if ($cfg -notcontains $p.Id) { continue }
            $start = $script:writes.Count
            & $p.Code
            Add-BuildRanges $ranges $p.Id $start $orig.Length
        }
        $start = $script:writes.Count
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
    $ranges['pe'].Add(@(($e + 24 + 96 + 4 * 8), ($e + 24 + 96 + 5 * 8)))   # Security-Verzeichnis (Signatur)
    $ranges['pe'].Add(@(($sectBase + 40 * $nsec), $firstRaw))
    # je Patch sortieren und zusammenfassen
    $merged = @{}
    foreach ($id in $ranges.Keys) {
        $list = @($ranges[$id] | Sort-Object { $_[0] })
        $out = New-Object System.Collections.Generic.List[object]
        foreach ($r in $list) {
            if ($out.Count -gt 0 -and $r[0] -le $out[$out.Count - 1][1]) {
                if ($r[1] -gt $out[$out.Count - 1][1]) { $out[$out.Count - 1][1] = $r[1] }
            } else { $out.Add(@($r[0], $r[1])) }
        }
        $merged[$id] = $out
    }
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("size;$($orig.Length)")
    foreach ($id in (@($allIds) + 'watermark' + 'pe')) {
        if (-not $merged.ContainsKey($id)) { continue }
        $own = 0
        foreach ($r in $merged[$id]) {
            $shared = $false
            foreach ($other in $merged.Keys) {
                if ($other -eq $id) { continue }
                foreach ($q in $merged[$other]) { if ($q[0] -lt $r[1] -and $r[0] -lt $q[1]) { $shared = $true; break } }
                if ($shared) { break }
            }
            $b = New-Object byte[] ($r[1] - $r[0])
            [Array]::Copy($orig, $r[0], $b, 0, $b.Length)
            $flag = 1; if ($shared) { $flag = 0 } else { $own++ }
            $lines.Add(('{0};{1:X};{2};{3}' -f $id, $r[0], ([BitConverter]::ToString($b)).Replace('-', ''), $flag))
        }
        if ($own -eq 0 -and $id -ne 'pe') { Write-Host "  WARNUNG: $id hat keine eigene Stelle und ist nicht erkennbar." }
    }
    $block = "# BEGIN ORIGINAL-BYTES`r`n`$ORIGINAL_TABLE = @'`r`n" + ($lines -join "`r`n") + "`r`n'@`r`n# END ORIGINAL-BYTES"
    $src = [System.IO.File]::ReadAllText($scriptPath)
    if ($src -match '[^\x00-\x7F]') { Write-Host 'BuildTable: Skript enthaelt Nicht-ASCII-Zeichen, Abbruch (es wird als ASCII zurueckgeschrieben).'; exit 1 }
    $a = $src.IndexOf('# BEGIN ORIGINAL-BYTES' + "`r`n")
    $z = -1; if ($a -ge 0) { $z = $src.IndexOf('# END ORIGINAL-BYTES', $a) }
    if ($a -lt 0 -or $z -lt 0) { Write-Host 'BuildTable: Markierungen nicht gefunden.'; exit 1 }
    $src = $src.Substring(0, $a) + $block + $src.Substring($z + '# END ORIGINAL-BYTES'.Length)
    [System.IO.File]::WriteAllText($scriptPath, $src, (New-Object System.Text.ASCIIEncoding))
    Write-Host ("  {0} Eintraege geschrieben." -f ($lines.Count - 1))
}

function Add-BuildRanges($ranges, [string]$id, [int]$start, [int64]$origLen) {
    if (-not $ranges.ContainsKey($id)) { $ranges[$id] = New-Object System.Collections.Generic.List[object] }
    for ($i = $start; $i -lt $script:writes.Count; $i += 2) {
        $off = $script:writes[$i]; $end = $off + $script:writes[$i + 1]
        if ($off -ge $origLen) { continue }
        if ($end -gt $origLen) { $end = $origLen }
        $ranges[$id].Add(@($off, $end))
    }
}

# ============================================================
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
#  Helfer fuer die Sprechblasen-Reichweite
#  Der Client zeigt Sprechblasen nur bis 25 Meter: Er vergleicht das Quadrat
#  des Abstands mit der float-Konstante 625.0 (VA 0xA104B0), die auch die
#  Fussspuren nutzen. Der Patch laesst die beiden Sprechblasen-Stellen auf
#  eine andere, schon vorhandene Konstante in .rdata zeigen - erlaubt sind
#  daher nur die Reichweiten, deren Quadrat es dort gibt (0 = unbegrenzt,
#  FLT_MAX). Schluessel = Meter, Wert = VA der Konstante.
# ============================================================
$BUBBLE_RANGES = [ordered]@{
    '50'  = 0xA12094    # 2500.0
    '100' = 0x9EA4C8    # 10000.0
    '150' = 0xA32904    # 22500.0
    '200' = 0xA4062C    # 40000.0
    '0'   = 0x9EA8FC    # FLT_MAX
}

function Test-BubbleRange([string]$v) {
    if ($BUBBLE_RANGES.Contains($v.Trim())) { return $null }
    return (L 'Erlaubt sind 50, 100, 150, 200 oder 0 (unbegrenzt).' 'Allowed are 50, 100, 150, 200 or 0 (unlimited).')
}

function Get-BubbleRangeFromExe {
    $va = [BitConverter]::ToUInt32($script:f, 0x31F4D0)
    foreach ($k in $BUBBLE_RANGES.Keys) { if ($BUBBLE_RANGES[$k] -eq $va) { return $k } }
    return $null
}

# ============================================================
#  Jahr-2038-Fix (St0ny): Datumsanzeige um N Jahre verschieben
#  Der Client speichert Daten gepackt mit 5-Bit-Jahr ab 2000 (bis 2031) und
#  32-Bit-Unix-Zeiten (bis 2038). Ein Servermodul schickt alle Daten um N
#  Jahre (Vielfaches von 28: gleiche Wochentage und Schaltjahre) in die
#  Vergangenheit; dieser Patch zaehlt sie fuer die Anzeige wieder dazu und
#  zieht sie bei Eingaben (Kalender-Termine) wieder ab. Intern bleibt alles
#  im Bereich 2000-2030, angezeigt wird 2000+N bis 2030+N.
#  - Jahresbasis 2000 (0x7D0) -> 2000+N an allen Lua-Schnittstellen:
#    Kalender (Datum, Grenzen, Monate, Termine, Antwortzeit, Sperren),
#    Kalender-Post (GetInboxText), /ginfo-Gruendungsdatum, Statistik-Daten.
#  - Kalender-Untergrenze 24.11.2004 -> 1.1.2000 (vier Stellen), damit
#    verschobene Daten vor 2004 gueltig sind.
#  - Erfolgsdaten rechnen mit zweistelligem Jahr: GetAchievementInfo,
#    GetAchievementComparisonInfo und der Erfolgs-Link (Tooltip) +N.
#  Die PC-Uhr (Lua date/time, Chat-Zeitstempel) bleibt unveraendert.
# ============================================================
$YEAR_SHIFTS = @(28, 56, 84)

function Test-YearShift([string]$v) {
    $n = 0
    if ([int]::TryParse($v.Trim(), [ref]$n) -and ($YEAR_SHIFTS -contains $n)) { return $null }
    return (L 'Erlaubt sind 28, 56 oder 84 (Vielfache von 28).' 'Allowed are 28, 56 or 84 (multiples of 28).')
}

function Get-YearShiftFromExe {
    $n = [BitConverter]::ToInt32($script:f, 0x1B75BE) - 2000
    if ($YEAR_SHIFTS -contains $n) { return [string]$n }
    return $null
}

function Set-YearShift([int]$N) {
    $base = [BitConverter]::GetBytes([int32](2000 + $N))
    # Jahresbasis 2000 -> 2000+N (imm32 von add/sub reg,0x7D0)
    $YEAR_SITES = @(
        0x1B75BE,  # VA 0x5B81BE add eax, 0x7d0: CalendarGetDate year
        0x1B767B,  # VA 0x5B827B add eax, 0x7d0: CalendarGetMinDate year
        0x1B7724,  # VA 0x5B8324 add eax, 0x7d0: CalendarGetMaxDate year
        0x1B77E9,  # VA 0x5B83E9 add ecx, 0x7d0: CalendarGetMinHistoryDate year
        0x1B7876,  # VA 0x5B8476 add ecx, 0x7d0: CalendarGetMaxCreateDate year
        0x1B8E60,  # VA 0x5B9A60 add edx, 0x7d0: CalendarGetMonth year
        0x1B8F93,  # VA 0x5B9B93 add edx, 0x7d0: CalendarGetAbsMonth year (out)
        0x1B9906,  # VA 0x5BA506 add ecx, 0x7d0: CalendarEventGetInviteResponseTime year
        0x1BCE53,  # VA 0x5BDA53 add edx, 0x7d0: CalendarGetEventInfo event year
        0x1BCEE5,  # VA 0x5BDAE5 add eax, 0x7d0: CalendarGetEventInfo lockout year
        0x1B72B4,  # VA 0x5B7EB4 add edx, 0x7d0: GetInboxText calendar mail FULLDATE year
        0x2CB8EF,  # VA 0x6CC4EF add eax, 0x7d0: SMSG_GUILD_INFO GUILD_INFO_TEMPLATE year
        0x36BF3D,  # VA 0x76CB3D add edx, 0x7d0: GetStatistic/GetAchievementCriteriaInfo date quantity "%02d/%02d/%d" (only caller 5B115D)
        0x1B8F4D,  # VA 0x5B9B4D sub edi, 0x7d0: CalendarGetAbsMonth year arg (in, sub)
        0x1BA952,  # VA 0x5BB552 sub eax, 0x7d0: CalendarEventSetDate year (in, sub)
        0x1BAB02,  # VA 0x5BB702 sub eax, 0x7d0: CalendarEventSetLockoutDate year (in, sub)
        0x1C383B   # VA 0x5C443B sub esi, 0x7d0: CalendarSetAbsMonth year arg (in, sub)
    )
    foreach ($o in $YEAR_SITES) {
        Assert-Bytes $o @(0xD0, 0x07, 0x00, 0x00) 'Jahr-2038-Fix'
        Patch $o $base
    }
    # Kalender-Untergrenze und Standardjahr: Konstanten auf 0 (1.1.2000)
    $ZERO_SITES = @(
        @(0x1B7609, @(0x0A, 0x00, 0x00, 0x00)),  # VA 0x5B8209 mov dword ptr [ebp - 0x14], 0xa: CalendarGetMinDate month 10->0
        @(0x1B7610, @(0x17, 0x00, 0x00, 0x00)),  # VA 0x5B8210 mov dword ptr [ebp - 0x18], 0x17: CalendarGetMinDate day 23->0
        @(0x1B7617, @(0x04, 0x00, 0x00, 0x00)),  # VA 0x5B8217 mov dword ptr [ebp - 0x10], 4: CalendarGetMinDate year 4->0
        @(0x1B6F5F, @(0x0A, 0x00, 0x00, 0x00)),  # VA 0x5B7B5F mov dword ptr [ebp - 0x10], 0xa: IsCalendarDateValid(5B7B30) min month
        @(0x1B6F66, @(0x17, 0x00, 0x00, 0x00)),  # VA 0x5B7B66 mov dword ptr [ebp - 0x14], 0x17: IsCalendarDateValid min day
        @(0x1B6F6D, @(0x04, 0x00, 0x00, 0x00)),  # VA 0x5B7B6D mov dword ptr [ebp - 0xc], 4: IsCalendarDateValid min year
        @(0x1B833E, @(0x04)),  # VA 0x5B8F3E cmp eax, 4: MonthOffset clamp (5B8EC0) cmp year,4
        @(0x1B8345, @(0x04, 0x00, 0x00, 0x00)),  # VA 0x5B8F45 mov dword ptr [esi], 4: 5B8EC0 year=4
        @(0x1B834D, @(0x0A)),  # VA 0x5B8F4D cmp eax, 0xa: 5B8EC0 cmp month,10
        @(0x1B8351, @(0x0A, 0x00, 0x00, 0x00)),  # VA 0x5B8F51 mov eax, 0xa: 5B8EC0 month=10
        @(0x1B83A5, @(0x04)),  # VA 0x5B8FA5 cmp eax, 4: AbsMonth clamp (5B8F70) cmp year,4
        @(0x1B83AC, @(0x04, 0x00, 0x00, 0x00)),  # VA 0x5B8FAC mov dword ptr [ecx], 4: 5B8F70 year=4
        @(0x1BF368, @(0x04)),  # VA 0x5BFF68 cmp eax, 4: Calendar init (5BFF30) cmp year,4
        @(0x1BF36D, @(0x0A)),  # VA 0x5BFF6D cmp ecx, 0xa: 5BFF30 cmp month,10
        @(0x1BF36F, @(0x04, 0x00, 0x00, 0x00)),  # VA 0x5BFF6F mov eax, 4: 5BFF30 year=4
        @(0x1BF37B, @(0x0A, 0x00, 0x00, 0x00)),  # VA 0x5BFF7B mov ecx, 0xa: 5BFF30 month=10
        @(0x1B8F20, @(0x04, 0x00, 0x00, 0x00)),  # VA 0x5B9B20 mov edi, 4: default year if no game time (GetAbsMonth)
        @(0x1C380E, @(0x04, 0x00, 0x00, 0x00)),  # VA 0x5C440E mov esi, 4: default year (SetAbsMonth)
        @(0x1BEFDC, @(0x04, 0x00, 0x00, 0x00))   # VA 0x5BFBDC mov eax, 4: default year (holiday expand)
    )
    foreach ($z in $ZERO_SITES) {
        Assert-Bytes $z[0] ([byte[]]$z[1]) 'Jahr-2038-Fix'
        Patch $z[0] (New-Object byte[] ($z[1].Length))
    }
    # GetAchievementInfo year +28 (2-digit): Monat/Tag per fild+fld1+faddp, damit Platz fuer mov eax,[edi+20h]; add eax,N
    Assert-Bytes 0x1B3A26 @(0x8B, 0x47, 0x1C, 0x83, 0xC0, 0x01, 0x89, 0x45, 0xF4, 0xDB, 0x45, 0xF4, 0xDD, 0x1C, 0x24, 0x53, 0xE8, 0x65, 0x9C, 0x29, 0x00, 0x8B, 0x4F, 0x18, 0x83, 0xC1, 0x01, 0x89, 0x4D, 0xF4, 0xDB, 0x45, 0xF4, 0x83, 0xC4, 0x04, 0xDD, 0x1C, 0x24, 0x53, 0xE8, 0x4D, 0x9C, 0x29, 0x00, 0xDB, 0x47, 0x20, 0x83, 0xC4, 0x04, 0xDD, 0x1C, 0x24, 0x53, 0xE8, 0x3E, 0x9C, 0x29, 0x00) 'Jahr-2038-Fix'
    $b = [byte[]]@(0xDB, 0x47, 0x1C, 0xD9, 0xE8, 0xDE, 0xC1, 0xDD, 0x1C, 0x24, 0x53, 0xE8, 0x6A, 0x9C, 0x29, 0x00, 0xDB, 0x47, 0x18, 0xD9, 0xE8, 0xDE, 0xC1, 0x83, 0xC4, 0x04, 0xDD, 0x1C, 0x24, 0x53, 0xE8, 0x57, 0x9C, 0x29, 0x00, 0x8B, 0x47, 0x20, 0x83, 0xC0, 0x1C, 0x89, 0x45, 0xF4, 0xDB, 0x45, 0xF4, 0x83, 0xC4, 0x04, 0xDD, 0x1C, 0x24, 0x53, 0xE8, 0x3F, 0x9C, 0x29, 0x00, 0x90)
    $b[40] = [byte]$N
    Patch 0x1B3A26 $b
    # GetAchievementComparisonInfo year +28 (2-digit): Monat/Tag per fild+fld1+faddp, damit Platz fuer mov eax,[edi+20h]; add eax,N
    Assert-Bytes 0x1B3BFD @(0x8B, 0x57, 0x1C, 0x83, 0xC2, 0x01, 0x89, 0x55, 0xF8, 0xDB, 0x45, 0xF8, 0xDD, 0x1C, 0x24, 0x56, 0xE8, 0x8E, 0x9A, 0x29, 0x00, 0x8B, 0x47, 0x18, 0x83, 0xC0, 0x01, 0x89, 0x45, 0xF8, 0xDB, 0x45, 0xF8, 0x83, 0xC4, 0x04, 0xDD, 0x1C, 0x24, 0x56, 0xE8, 0x76, 0x9A, 0x29, 0x00, 0xDB, 0x47, 0x20, 0x83, 0xC4, 0x04, 0xDD, 0x1C, 0x24, 0x56, 0xE8, 0x67, 0x9A, 0x29, 0x00) 'Jahr-2038-Fix'
    $b = [byte[]]@(0xDB, 0x47, 0x1C, 0xD9, 0xE8, 0xDE, 0xC1, 0xDD, 0x1C, 0x24, 0x56, 0xE8, 0x93, 0x9A, 0x29, 0x00, 0xDB, 0x47, 0x18, 0xD9, 0xE8, 0xDE, 0xC1, 0x83, 0xC4, 0x04, 0xDD, 0x1C, 0x24, 0x56, 0xE8, 0x80, 0x9A, 0x29, 0x00, 0x8B, 0x47, 0x20, 0x83, 0xC0, 0x1C, 0x89, 0x45, 0xF8, 0xDB, 0x45, 0xF8, 0x83, 0xC4, 0x04, 0xDD, 0x1C, 0x24, 0x56, 0xE8, 0x68, 0x9A, 0x29, 0x00, 0x90)
    $b[40] = [byte]$N
    Patch 0x1B3BFD $b
    # AchievementLinkParse year +28 (2-digit): inc esi; push esi; call atoi; add al,N; mov [ebp-30h],eax
    Assert-Bytes 0x22D2E9 @(0x83, 0xC6, 0x01, 0x56, 0xE8, 0xDE, 0x11, 0x14, 0x00, 0x89, 0x45, 0xD0) 'Jahr-2038-Fix'
    $b = [byte[]]@(0x46, 0x56, 0xE8, 0xE0, 0x11, 0x14, 0x00, 0x04, 0x1C, 0x89, 0x45, 0xD0)
    $b[8] = [byte]$N
    Patch 0x22D2E9 $b
}

# ============================================================
#  PATCH-DEFINITIONEN
#  Jeder Patch ist eine Hashtable:
#    Id    - interner Kurzname (fuer Abhaengigkeiten und patcher_selection.ini)
#    Cat   - Kategorie (siehe $CATEGORIES), Ueberschrift im Menue
#    De/En - Anzeigename je Sprache
#    On    - Teil des Presets "Billy's_Wow.exe" ($true) oder nicht ($false).
#            Die Standard-Auswahl ist das Preset "Reforged"
#            ($PRESET_REFORGED), das Preset "St0nys_Wow.exe" steht in
#            $PRESET_STONY - beide als Id-Listen hinter den Patches
#    NoteDe/NoteEn - optional: Hinweis in Klammern hinter dem Namen, z.B. was
#            zusaetzlich benoetigt wird
#    Url   - optional: Link zum Hinweis, wird im Menue unter dem Namen gezeigt
#    Author - optional: Urheber bzw. Quelle des Patches (nur zur Dokumentation)
#    Obsoletes - optional: Ids von Patches, die dieser ueberfluessig macht
#            (erzeugt nur einen Hinweis, wenn beide ausgewaehlt sind)
#    GrowsExe - optional: $true, wenn der Patch immer eine Sektion anhaengt und
#            die Wow.exe damit groesser macht (erzeugt einen Bann-Hinweis)
#    Warn-Codes - Patches ohne die drei folgenden Flags sind sicher (Code 1,
#            keine Warnung). Jedes Flag erzeugt eine Warnung in eckigen
#            Klammern hinter dem Namen und einen Hinweis vor dem Patchen:
#    BanRisk - optional: $true bei Bann-Gefahr (Code 2, roter Hinweis)
#    PublicUntested - optional: $true, wenn der Patch nicht auf oeffentlichen
#            Servern getestet ist - Vorsicht, kann zu Kick/Bann fuehren
#            (Code 3, gelber Hinweis)
#    GameUntested - optional: $true, wenn die Funktion im Spiel ungetestet
#            ist - moeglicherweise verbuggt (Code 4, gelber Hinweis)
#    Needs - optional: Ids von Patches, ohne die dieser nicht voll wirkt
#            (erzeugt nur einen Hinweis, keine Sperre)
#    PromptDe/PromptEn, Default, Check - optional, fuer Patches mit eigenem
#            Wert: der Patcher fragt ihn nach der Auswahl ab (Vorschlag =
#            gemerkter Wert oder Default), prueft ihn mit Check (liefert $null
#            oder eine Fehlermeldung) und legt ihn in $VALUES[Id] ab
#    Decode - optional: Scriptblock, der den eingespielten Wert aus der Exe
#            ($script:f) liest - fuer die Erkennung ueber das Wasserzeichen
#    Suggest - optional: Scriptblock, der den Vorschlag im Dialog aus dem
#            gemerkten Wert berechnet (z.B. heutiges Datum)
#    Normalize - optional: Scriptblock, der einen gueltigen Wert in eine
#            einheitliche Schreibweise bringt (z.B. Build-Datum mit Uhrzeit)
#    Code  - Scriptblock mit den Patch-Aufrufen
#  Die Reihenfolge hier ist die Reihenfolge im Menue und beim Einspielen,
#  Patches einer Kategorie stehen zusammen.
# ============================================================

$CATEGORIES = @{
    system   = @{ De = 'System & Leistung';                 En = 'System & performance' }
    security = @{ De = 'Sicherheit & Datenschutz';          En = 'Security & privacy' }
    login    = @{ De = 'Login & Verbindung';                En = 'Login & connection' }
    modding  = @{ De = 'Modding: Interface, MPQs & Addons'; En = 'Modding: interface, MPQs & addons' }
    dll      = @{ De = 'DLL-Loader';                        En = 'DLL loaders' }
    gameplay = @{ De = 'Gameplay-Fixes';                    En = 'Gameplay fixes' }
    graphics = @{ De = 'Grafik & Sichtweite';               En = 'Graphics & view distance' }
    ui       = @{ De = 'Interface & Komfort';               En = 'Interface & comfort' }
    window   = @{ De = 'Fenster, Maus & Kamera';            En = 'Window, mouse & camera' }
    sound    = @{ De = 'Sound';                             En = 'Sound' }
    client   = @{ De = 'Client-Infos: Version, Build, Titel, Datum, Icon'; En = 'Client info: version, build, title, date, icon' }
}

$patches = @(

    # --- System & Leistung ---

    @{ Id = 'laa'; Cat = 'system'; On = $true
       Author = 'Alastor StrixEfuartus / Kebabstorm / Robinsch'
       De = '4GB-Patch (Large Address Aware)'
       En = '4GB patch (Large Address Aware)'
       Code = {
        Patch 0x126 @(0x23)
    }}

    @{ Id = 'cache'; Cat = 'system'; On = $false
       Author = 'Alastor StrixEfuartus / Kebabstorm'
       De = 'CACHE-Ordner-Erstellung deaktivieren'
       En = 'Disable CACHE folder creation'
       Code = {
        Patch 0x61BE58 @(0x7C, 0x7C)
    }}

    @{ Id = 'itemcache'; Cat = 'system'; On = $true
       Author = 'Robinsch'
       De = 'Item-Cache sofort aktualisieren'
       En = 'Refresh item cache immediately'
       Code = {
        Patch 0x2689FD @(0x00, 0x00)
    }}

    @{ Id = 'worldcrash'; Cat = 'system'; On = $false; PublicUntested = $true
       Author = 'Alyst3r (0x539wowmod) (fixed by St0ny)'
       De = 'WorldFrame-Absturzfix (ungueltige Dreiecks-Indizes)'
       En = 'WorldFrame crash fix (invalid triangle indices)'
       Code = {
        # Code-Hoehle am Ende von .text, siehe Get-CodeCave / Add-WorldFrameCrashFix.
        Add-WorldFrameCrashFix
    }}

    @{ Id = 'timer'; Cat = 'system'; On = $false
       Author = 'St0ny'
       De = 'Genauen Timer immer nutzen (Ruckeln beim Drehen behoben)'
       En = 'Always use the precise timer (fixes turning stutter)'
       Code = {
        # Beim Start waehlt TimeManager (VA 0x86AB30) die Zeitquelle: QPC
        # (genau) oder GetTickCount (~16-ms-Schritte). Dazu vergleicht er 250 ms
        # lang QPC mit GetTickCount; weichen beide um 5 ms oder mehr ab (z.B.
        # wenn ein Treiber den Thread kurz aufhaelt), faellt er fuer die ganze
        # Sitzung auf GetTickCount zurueck (timingTestError 3). Mit dem groben
        # Timer ruckelt u.a. das Nachdrehen des Unterkoerpers beim Drehen.
        # jne -> jmp bei VA 0x86AC8E: der 250-ms-Vergleich entfaellt. Die
        # Pruefung, ob QPC ueber alle CPU-Kerne vorwaerts laeuft (Fehler 4),
        # und die CVar timingMethod bleiben erhalten.
        Patch 0x46A08E @(0xE9, 0x83, 0x00, 0x00, 0x00, 0x90)
    }}

    @{ Id = 'nothrottle'; Cat = 'system'; On = $false
       Author = 'tb (ported by St0ny)'
       De = 'Gegenstands- und Namensabfragen nicht drosseln'
       En = 'Do not throttle item and player name queries'
       Code = {
        # Die Datenbank-Caches des Clients (Items, Kreaturen, Quests, Namen ...)
        # koennen ihre Anfragen an den Server pro 30-Sekunden-Fenster begrenzen
        # ([Cache+48h] = "Anfragen pro Minute" aus dem Konstruktor / 2). Ist die
        # Grenze erreicht, kommt die Anfrage in eine Warteschlange (Pruefung bei
        # VA 0x67B711), 0 heisst unbegrenzt. Von den 15 Caches ist das nur bei
        # zweien gesetzt: itemcache (Gegenstands-Infos, 512 pro Minute) und
        # namecache (Spielernamen, 256 pro Minute) - alle anderen bekommen schon
        # im Original 0. In den beiden Konstruktoren wird statt des berechneten
        # Werts (edx) ecx gespeichert, das dort 0 ist:
        # mov [esi+48h],edx -> mov [esi+48h],ecx.
        Patch 0x27547E @(0x4E)   # VA 0x67607E, itemcache.wdb
        Patch 0x2756DE @(0x4E)   # VA 0x6762DE, namecache.wdb
    }}

    @{ Id = 'mirrorfix'; Cat = 'system'; On = $false
       Author = 'tb (ported by St0ny)'
       De = 'Mirror-Image-Absturzfix (Speicherleck bei Spiegelbildern)'
       En = 'Mirror Image crash fix (memory leak with mirror images)'
       Code = {
        # Blizzard-Fehler: Der Handler fuer SMSG_MIRRORIMAGE_DATA (VA 0x730290)
        # legt fuer das Aussehen einer Spiegelbild-Einheit eine neue
        # Charakter-Komponente an ([Einheit+B4Ch]), ohne eine noch vorhandene
        # alte freizugeben. Die alte bleibt mit ihrer Textur am Grafikgeraet
        # haengen; beim Beenden greift der Client dann auf schon freigegebenen
        # Speicher zu (Absturz). Haeufig bei Server-Kopien von Spielern (Eluna
        # "Mirror Image"-Kreaturen), die ihr Modell oft neu laden.
        # Beide Aufrufe des Allokators (VA 0x4F0980) im Handler gehen jetzt an
        # einen Stub, der eine alte Komponente erst mit der Original-Freigabe
        # (VA 0x4F16C0) loest und dann zum Allokator springt. Der Stub (29 Byte)
        # liegt in einer toten Funktion bei VA 0x86BF10 (nirgends aufgerufen
        # oder referenziert). Die Dateigroesse aendert sich nicht.
        Patch 0x46B310 @(
            0x8B, 0x86, 0x4C, 0x0B, 0x00, 0x00, 0x85, 0xC0, 0x74, 0x0E, 0x50, 0xE8, 0xA0, 0x57, 0xC8, 0xFF,
            0x59, 0x83, 0xA6, 0x4C, 0x0B, 0x00, 0x00, 0x00, 0xE9, 0x53, 0x4A, 0xC8, 0xFF, 0xCC, 0xCC, 0xCC
        )
        Patch 0x32F729 @(0xE8, 0xE2, 0xBB, 0x13, 0x00)
        Patch 0x32F8CA @(0xE8, 0x41, 0xBA, 0x13, 0x00)
    }}

    @{ Id = 'wmocube'; Cat = 'system'; On = $false
       Author = 'Alyst3r (ported by St0ny)'
       De = 'Fehlende WMO-Datei: Fehlerwuerfel statt ERROR #134'
       En = 'Missing WMO file: error cube instead of ERROR #134'
       Code = {
        # CMap::SafeOpen (VA 0x7BD480) oeffnet WMO-Dateien (Gebaeude, Dungeons).
        # Klappt das zehnmal nicht, bricht der Client mit "ERROR #134 Fatal
        # Condition: CMap::SafeOpen() failed" ab. Statt der Fehlermeldung oeffnet
        # der Fehlerausgang jetzt "Spells\ErrorCube.mdx" (der Text steht schon in
        # der Exe) und gibt dessen Ergebnis zurueck - wie in WotLK-Extensions:
        # push ebx / push "Spells\ErrorCube.mdx" / call SFile::Open / Epilog.
        Patch 0x3BC8AF @(0x53, 0x68, 0x60, 0x4B, 0xA3, 0x00, 0xE8, 0xC6, 0x7A, 0xC6, 0xFF, 0x5F, 0x5E, 0x5B, 0x5D, 0xC3)
    }}

    @{ Id = 'glyphfix'; Cat = 'system'; On = $false; GrowsExe = $true
       Author = 'tb (ported by St0ny)'
       De = 'Schrift-Glyphen-Fix (falsche oder kaputte Zeichen in Texten)'
       En = 'Font glyph fix (wrong or garbled characters in text)'
       Code = {
        # Eigene Sektion (.glyph) mit vier Hooks im Glyphen-Cache plus
        # CheckGeometry an Ort und Stelle neu, siehe Add-GlyphCacheFix.
        Add-GlyphCacheFix
    }}

    # --- Sicherheit & Datenschutz ---

    @{ Id = 'rce'; Cat = 'security'; On = $false; BanRisk = $true
       Author = 'Robinsch'
       De = 'Remote Code Execution Exploit Fix'
       En = 'Remote code execution exploit fix'
       Code = {
        Patch 0x2A7 @(0xC0)
        Patch 0x3D9D7C @(0x90, 0x90)
    }}

    @{ Id = 'wardenoff'; Cat = 'security'; On = $false; Obsoletes = @('rce'); BanRisk = $true
       Author = 'Robinsch'
       De = 'Warden komplett abschalten, RCE-Fix'
       En = 'Disable Warden completely, RCE fix'
       Code = {
        # Verwirft SMSG_WARDEN_DATA (Opcode 0x2E6) direkt am Eingang des
        # Paket-Handlers (VA 0x7DA850): je -> nop, der Handler kehrt sofort mit 0
        # zurueck. Damit kann der Server ueber Warden keinerlei Code mehr im
        # Client ausfuehren. Der Client antwortet aber auch nicht mehr auf
        # Warden - Server mit aktivem Warden koennen deshalb kicken.
        # Macht den RCE-Fix (rce) ueberfluessig, beide zusammen schaden nicht.
        Patch 0x3D9C5B @(0x90, 0x90)
    }}

    @{ Id = 'scandll'; Cat = 'security'; On = $false
       Author = 'Alastor StrixEfuartus'
       De = 'Scan.dll deaktivieren'
       En = 'Disable Scan.dll'
       Code = {
        # Macht aus ".\Scan.dll" und ".\Scan.dll.new" ".\||an.dll" usw. - '|' ist
        # in Dateinamen verboten, das Laden schlaegt damit garantiert fehl.
        Patch 0x5F4D56 @(0x7C, 0x7C)
        Patch 0x5F4D62 @(0x7C, 0x7C)
    }}

    @{ Id = 'noserverpatch'; Cat = 'security'; On = $false
       Author = 'Kebabstorm'
       De = 'Client-Patches vom Server verbieten'
       En = 'Disallow client patches from the server'
       Code = {
        Patch 0xDA2A8 @(0x90, 0x90, 0xEB)
    }}

    @{ Id = 'nosurvey'; Cat = 'security'; On = $false
       Author = 'Kebabstorm'
       De = 'Hardware-Umfragen vom Server verbieten'
       En = 'Disallow hardware surveys from the server'
       Code = {
        Patch 0xDA2BD @(0xE9, 0xEB, 0x0A, 0x00, 0x00)
    }}

    # --- Login & Verbindung ---

    @{ Id = 'skipbnet'; Cat = 'login'; On = $false
       Author = 'Kebabstorm'
       De = 'Battle.net-Login ueberspringen'
       En = 'Skip Battle.net login'
       Code = {
        Patch 0x2B1F48 @(0xEB)
    }}

    @{ Id = 'skiprdp'; Cat = 'login'; On = $false
       Author = 'Kebabstorm'
       De = 'Remote-Desktop-Pruefung ueberspringen'
       En = 'Skip Remote Desktop check'
       Code = {
        Patch 0x36AE40 @(0xEB)
    }}

    @{ Id = 'nohttp'; Cat = 'login'; On = $false
       Author = 'Kebabstorm'
       De = 'HTTP-Anfragen an Battle.net deaktivieren'
       En = 'Disable HTTP requests to Battle.net'
       Code = {
        # News, Hilfe-Artikel und Nutzungsbedingungen werden nicht mehr abgerufen.
        Patch 0x46F28F @(0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'afk'; Cat = 'login'; On = $false
       Author = 'St0ny'
       De = 'Idle-Kick nach Character-Autologin verhindern'
       En = 'Prevent the idle kick after character auto-login'
       NoteDe = 'wird fuer Character-Autologin benoetigt; AFK- und Idle-Timer bleiben aktiv'
       NoteEn = 'required for character auto-login; AFK and idle timers stay active'
       Url = 'https://discord.com/channels/858041817043042364/1515439916878663701'
       Code = {
        # Nach einem Autologin ohne jede Eingabe steht der Zeitstempel der
        # letzten Eingabe ([0xB499A4]) noch auf 0 - der Idle-Check haelt den
        # Spieler sofort fuer untaetig. Der Umweg bei VA 0x52B24C (Hoehle in der
        # int3-Luecke VA 0x94B902) setzt den Zeitstempel beim ersten Durchlauf
        # auf "jetzt", wenn er noch 0 ist. Dazu wird bei VA 0x52AFAF ein
        # Fatal-Error-Check entfernt, der dabei ausloesen kann. Die eigentlichen
        # Timer (AFK nach 5 Minuten, Logout nach 30 Minuten) bleiben.
        Patch 0x12A3AF @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
        Patch 0x12A64C @(0xE9, 0xB1, 0x06, 0x42, 0x00)
        Patch 0x54AD02 @(0xE8, 0x19, 0xF5, 0xF1, 0xFF, 0x83, 0x3D, 0xA4, 0x99, 0xB4, 0x00, 0x00, 0x75, 0x05, 0xA3, 0xA4, 0x99, 0xB4, 0x00, 0xE9, 0x37, 0xF9, 0xBD, 0xFF)
    }}

    # --- Modding: Interface, MPQs & Addons ---

    @{ Id = 'glue'; Cat = 'modding'; On = $true
       Author = 'Alastor StrixEfuartus / Kebabstorm (fixed by St0ny)'
       De = 'Custom Glue-XML erlauben'
       En = 'Allow custom GlueXML'
       Code = {
        # Signaturpruefung der Interface-Dateien (VA 0x8165E0, liefert 0 = keine
        # Signatur, 1 = kaputt, 2 = veraendert, 3 = gueltig) immer "gueltig"
        # melden; ausserdem (0x1F41BF) die lokalen Ordner Interface\GlueXML und
        # Interface\FrameXML nicht mehr in "*.old" umbenennen.
        # Die verbreitete Fassung dieses Patches (Alastor/Kebabstorm) macht aus
        # dem Sprung bei VA 0x816625 ein "jmp": Laesst sich die .sig-Datei
        # nicht laden (Addons ohne Signatur!), lief die Pruefung dann mit
        # uninitialisierten Variablen weiter und gab einen Zeiger in .rdata
        # frei (undefiniertes Verhalten). Hier stattdessen am Fehlerausgang
        # (VA 0x816627) direkt "3" zurueckgeben: mov al,3 / pop esi / leave / ret.
        # Gleiche Wirkung, ohne wilden Speicherzugriff.
        Patch 0x1F41BF @(0xEB)
        Patch 0x415A27 @(0xB0, 0x03, 0x5E, 0xC9, 0xC3)
        Patch 0x415A3F @(0x03)
        Patch 0x415A95 @(0x03)
        Patch 0x415B46 @(0xEB)
        Patch 0x415B5F @(0xB8, 0x03, 0x00, 0x00, 0x00, 0xEB, 0xED)
    }}

    @{ Id = 'mpqsig'; Cat = 'modding'; On = $false
       Author = 'Alastor StrixEfuartus'
       De = 'Falsch/Nicht signierte MPQs zulassen'
       En = 'Allow unsigned / incorrectly signed MPQs'
       Code = {
        # Die Signaturpruefung fuer MPQ-Archive (VA 0x421F50) meldet immer
        # "gueltig". Im Client wird sie nur fuer Archive aufgerufen, die der
        # Server schickt: wow-patch.mpq (PatchDownloadApply) und Cache\Survey.mpq.
        # Die normalen Data\*.MPQ laedt der Client ohne Signaturpruefung.
        Patch 0x021350 @(0x55, 0x8B, 0xEC, 0xB9, 0x05, 0x00, 0x00, 0x00, 0x8B, 0x45, 0x0C, 0x89, 0x08, 0xB8, 0x01, 0x00, 0x00, 0x00, 0x5D, 0xC2, 0x18, 0x00)
    }}

    @{ Id = 'mpqnames'; Cat = 'modding'; On = $true
       De = 'Erweiterte MPQ-Namen erlauben'
       En = 'Allow extended MPQ names'
       Code = {
        Patch 0x5E0F09 @(0x2A)
        Patch 0x5E0F16 @(0x2A)
    }}

    @{ Id = 'localdata'; Cat = 'modding'; On = $true
       Author = 'Alastor StrixEfuartus'
       De = 'Daten direkt aus dem Data-Ordner laden (ohne MPQ)'
       En = 'Load data directly from the Data folder (no MPQ)'
       Code = {
        # Z.B. Data\DBFilesClient\ItemDisplayInfo.dbc wird direkt aus dem Ordner gelesen.
        Patch 0x1F2A @(0x90, 0x90, 0x90, 0x90, 0x90, 0x6A, 0xFF)
    }}

    @{ Id = 'luaunlock'; Cat = 'modding'; On = $false; BanRisk = $true
       Author = 'Alastor StrixEfuartus'
       De = 'LUA Unlock (Zauber, Bewegung, Makros)'
       En = 'LUA unlock (spells, movement, macros)'
       Code = {
        # Die zentrale Schutzpruefung (VA 0x5191C0) meldet fuer die Schutzarten
        # 0-5, 16 und 17 immer "erlaubt": Bewegungsfunktionen (MoveForwardStart,
        # TurnLeftStart, ...), CastSpellByName / CastSpell / UseAction /
        # PetAttack, RunMacro / RunMacroText, GM-Ticket-Funktionen.
        # Nicht betroffen (eigene Pruefungen im Code): TargetUnit, FocusUnit,
        # InteractUnit, ReloadUI; AttackTarget meldet weiterhin einen Fehler.
        Patch 0x1185E7 @(0xB8, 0x01, 0x00, 0x00, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'luaunlockfull'; Cat = 'modding'; On = $false; Obsoletes = @('luaunlock'); BanRisk = $true
       Author = 'St0ny'
       De = 'LUA Unlock (vollstaendig): alle geschuetzten Funktionen freigeben'
       En = 'LUA unlock (complete): allow all protected functions'
       Code = {
        # Umfasst die Wirkung von "LUA Unlock (Zauber, Bewegung, Makros)" und
        # gibt zusaetzlich alle Funktionen frei, die eine eigene Pruefung haben.
        # 1) Zentrale Schutzpruefung (VA 0x5191C0): 24 Schutztypen in drei
        #    Klassen (immer verboten / nur nach Hardware-Ereignis / nur bei
        #    erlaubten Attribut-Aenderungen). Liefert sofort "erlaubt":
        #    mov eax,1 / ret (cdecl, der Aufrufer raeumt den Stack).
        #    Damit u.a. UseAction, Handel, Auktionshaus, Kalender, LFG,
        #    Raid-Untergruppen, Makros anlegen/aendern, Mouselook-Bindings.
        Patch 0x1185C0 @(0xB8, 0x01, 0x00, 0x00, 0x00, 0xC3)
        # 2) Eigene Pruefungen "cmp [Taint],0 / je erlaubt" -> "jmp erlaubt":
        Patch 0x1216E7 @(0xEB)   # ReloadUI (VA 0x5222E7)
        Patch 0x11F34A @(0xEB)   # FocusUnit, ClearFocus (VA 0x51FF4A)
        Patch 0x127389 @(0xEB)   # InteractUnit (VA 0x527F89)
        Patch 0x119BD6 @(0xEB)   # UninviteUnit (VA 0x51A7D6)
        Patch 0x11A097 @(0xEB)   # CancelLogout (VA 0x51AC97)
        Patch 0x11CD67 @(0xEB)   # UI-Neuladen-Helfer (VA 0x51D967)
        Patch 0x11F088 @(0xEB)   # Grafik-Einstellung mit UI-Neuladen (VA 0x51FC88)
        Patch 0x124076 @(0xEB)   # TargetUnit, AssistUnit, TargetLast*, TargetNearest*, TargetTotem (VA 0x524C76)
        Patch 0x1246E0 @(0xEB)   # TargetDirectionEnemy/Friend (VA 0x5252E0)
        Patch 0x40259C @(0xEB)   # Sperrliste fuer Zauber aus unsicherem Code (VA 0x80319C)
        # 3) AttackTarget, StartAttack, TargetNearest*, Pet-Befehle: "jne Fehler"
        #    (VA 0x524FD7, 6 Byte) wird zu nop - der Fehlerpfad entfaellt.
        Patch 0x1243D7 @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
        # Unangetastet bleiben die Frame-Schutzpruefung (SetAttribute, Show,
        # Hide auf geschuetzten Frames) und RegisterForSave - sie betreffen
        # keine Spielaktionen.
    }}

    @{ Id = 'keyprop'; Cat = 'modding'; On = $false; BanRisk = $true; GameUntested = $true
       Author = 'Alyst3r (0x539wowmod)'
       De = 'Alle Tastatur-Ereignisse an Addons weiterreichen (OnKeyDown)'
       En = 'Pass all keyboard events on to addons (OnKeyDown)'
       Code = {
        # CSimpleFrame::OnKeyDown (VA 0x48FB80) meldet nach dem OnKeyDown-Skript
        # eines Frames "erledigt" (mov eax, 1 bei VA 0x48FBD8). Mit 0 laeuft die
        # Taste danach weiter zu den Tastenbelegungen.
        Patch 0x8EFD9 @(0x00)
    }}

    @{ Id = 'globalsv'; Cat = 'modding'; On = $false; PublicUntested = $true; GameUntested = $true
       Author = 'St0ny (original by boredatom)'
       De = 'Addon-Daten aller Accounts zusammenlegen (SavedVariables)'
       En = 'Merge addon data of all accounts (SavedVariables)'
       NoteDe = 'gemeinsamer Ordner WTF\Account\global'
       NoteEn = 'shared folder WTF\Account\global'
       Code = {
        # Nach dem Login merkt sich die Funktion bei VA 0x5F9080 den Account-
        # Namen fuer die Addon-Pfade: WTF\Account\<Account>\SavedVariables,
        # ...\<Realm>\<Charakter>\SavedVariables und die AddOns.txt beider
        # Ebenen. Statt des Namens kopiert sie jetzt den Text "global", der
        # schon in der Exe steht (VA 0xA384A0). Makros, Tastenbelegungen und
        # Einstellungen (*-cache.*, layout-local.txt) nutzen einen eigenen
        # Puffer und bleiben je Account getrennt. Gleiche Wirkung wie der Patch
        # von boredatom, aber an Ort und Stelle statt die Funktion zu
        # verschieben: aus mov eax,[ebp+8] / push 0x500 / push eax wird
        # push 0x7F / push "global" / nop / nop. 0x7F ist nur die Hoechstlaenge
        # fuer SStrCopy und reicht fuer "global".
        Patch 0x1F8488 @(0x6A, 0x7F, 0x68, 0xA0, 0x84, 0xA3, 0x00, 0x90, 0x90)
    }}

    # --- DLL-Loader ---

    @{ Id = 'awesome'; Cat = 'dll'; On = $true; Needs = @('laa')
       Author = 'FrostAtom'
       De = 'AwesomeWotlkLib.dll Unterstuetzung aktivieren'
       En = 'Enable AwesomeWotlkLib.dll support'
       NoteDe = 'benoetigt awesome_wotlk'
       NoteEn = 'requires awesome_wotlk'
       Url = 'https://github.com/noname08662/awesome_wotlk'
       Code = {
        # Patch von FrostAtom (awesome_wotlk). Der Start der Haupt-Fiber (VA
        # 0x40B7D0, kurz vor WinMain) springt in einen Lader bei VA 0x4E5CB0,
        # der die DLL per LoadLibraryA laedt, das Scan.dll-Flag ("Pruefung
        # bestanden") setzt und den ueberschriebenen Prolog nachholt. Der Lader
        # ueberschreibt den Anfang der Scan.dll-Startfunktion, deren einziger
        # Aufrufer (Lua ScanDLLStart, VA 0x4DCCF0) deshalb zu "return 0" wird -
        # der Scan.dll-Mechanismus ist damit abgeschaltet (wie bei "Scan.dll
        # deaktivieren"). Fehlt die DLL, startet WoW normal weiter.
        Patch 0xABD0 @(0xE9, 0xDB, 0xA4, 0x0D, 0x00, 0x90, 0x90, 0x90)
        Patch 0xDC0F0 @(0xB8, 0x00, 0x00, 0x00, 0x00, 0xC3)
        Patch 0xE50B0 @(0xB8, 0x01, 0x00, 0x00, 0x00, 0xA3, 0x74, 0xB4, 0xB6, 0x00, 0x68, 0xE0, 0x5C, 0x4E, 0x00, 0xE8, 0x1C, 0x68, 0x38, 0x00, 0x83, 0xC4, 0x04, 0x55, 0x8B, 0xEC, 0xE8, 0xA1, 0x10, 0xF2, 0xFF, 0xE9, 0x04, 0x5B, 0xF2, 0xFF, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0x41, 0x77, 0x65, 0x73, 0x6F, 0x6D, 0x65, 0x57, 0x6F, 0x74, 0x6C, 0x6B, 0x4C, 0x69, 0x62, 0x2E, 0x64, 0x6C, 0x6C, 0x00)
    }}

    @{ Id = 'wotlkext'; Cat = 'dll'; On = $false; Needs = @('laa')
       Author = 'St0ny (original by Alyst3r)'
       De = 'WotLKExtensions.dll Unterstuetzung aktivieren'
       En = 'Enable WotLKExtensions.dll support'
       NoteDe = 'benoetigt WotLK-Extensions'
       NoteEn = 'requires WotLK-Extensions'
       Url = 'https://github.com/Alyst3r/WotLK-Extensions'
       Code = {
        # Laedt beim Start die WotLKExtensions.dll aus dem WoW-Ordner. Der
        # Original-Patcher von WotLK-Extensions haengt seinen Lader wie der
        # awesome-Lader an den Start der Haupt-Fiber (VA 0x40B7D0) - beide
        # zusammen gingen nicht. Dieser Lader sitzt stattdessen am Anfang der
        # Funktion, die die Haupt-Fiber dort aufruft (VA 0x406D70, einziger
        # Aufrufer): jmp -> Lader bei VA 0x4E5D00 im toten Teil der
        # Scan.dll-Startfunktion (hinter dem awesome-Lader) -> Scan.dll-Flag
        # "Pruefung bestanden" setzen (sonst blockiert DefaultServerLogin),
        # LoadLibraryA("WotLKExtensions.dll"), ersten Befehl (push 5EEB70h)
        # nachholen, zurueck. Lua ScanDLLStart (VA 0x4DCCF0) wird wie beim
        # awesome-Lader zu "return 0" (gleiche Bytes). Mit dem awesome-Lader
        # zusammen werden beide DLLs geladen. Fehlt die DLL, startet WoW normal.
        Patch 0x6170 @(0xE9, 0x8B, 0xEF, 0x0D, 0x00)
        Patch 0xDC0F0 @(0xB8, 0x00, 0x00, 0x00, 0x00, 0xC3)
        Patch 0xE5100 @(
            0xC6, 0x05, 0x74, 0xB4, 0xB6, 0x00, 0x01, 0x68, 0x1C, 0x5D, 0x4E, 0x00, 0xFF, 0x15, 0x48, 0xF2,
            0x9D, 0x00, 0x68, 0x70, 0xEB, 0x5E, 0x00, 0xE9, 0x59, 0x10, 0xF2, 0xFF, 0x57, 0x6F, 0x74, 0x4C,
            0x4B, 0x45, 0x78, 0x74, 0x65, 0x6E, 0x73, 0x69, 0x6F, 0x6E, 0x73, 0x2E, 0x64, 0x6C, 0x6C, 0x00
        )
    }}

    @{ Id = 'voicedll'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'voice.dll beim Start laden (mod-voicechat) [ALPHA]'
       En = 'Load voice.dll at startup (mod-voicechat) [ALPHA]'
       NoteDe = 'Modul noch unfertig'
       NoteEn = 'module not finished yet'
       Url = 'https://github.com/Raz0r1337/mod-voicechat'
       Code = {
        # ALPHA - das Modul mod-voicechat ist noch nicht fertig. Laedt
        # beim Start die voice.dll aus dem WoW-Ordner; fehlt sie,
        # startet WoW ganz normal. Dateigroesse und PE-Header bleiben gleich.
        Add-VoiceLoader 'voice.dll'
    }}

    # --- Gameplay-Fixes ---

    @{ Id = 'areatrigger'; Cat = 'gameplay'; On = $true
       Author = 'Robinsch'
       De = 'Area-Trigger-Timer genauer (50 ms statt 100 ms)'
       En = 'More precise area trigger timer (50 ms instead of 100 ms)'
       Code = {
        # push 64h -> push 32h: Intervall des Area-Trigger-Timers (VA 0x6DBE40)
        Patch 0x2DB241 @(0x32)
    }}

    @{ Id = 'swing'; Cat = 'gameplay'; On = $true
       Author = 'Robinsch'
       De = 'Nahkampf-Schwung bei Rechtsklick entfernt'
       En = 'Remove melee swing on right-click'
       Code = {
        Patch 0x2E1C67 @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'npcanim'; Cat = 'gameplay'; On = $true
       Author = 'Robinsch (fixed by St0ny)'
       De = 'NPC-Angriffsanimation beim Drehen unterdrueckt'
       En = 'Suppress NPC attack animation when turning'
       Code = {
        # Dreht sich eine Einheit auf der Stelle, startet der Client die
        # Schritt-Animation (ShuffleLeft/-Right) ueber "Animation neu
        # bestimmen" (VA 0x73AC30). Bei NPCs kam dabei die Angriffsanimation
        # heraus, deshalb schaltete Robinschs Patch (je -> jmp bei VA
        # 0x73E3C9) den Aufruf ab - aber fuer ALLE Einheiten, also auch fuer
        # Spieler: deren Beine machten beim Drehen keine Schritte mehr, nur der
        # Oberkoerper verdrehte sich. Der Block VA 0x73E385-0x73E3D5 ist hier
        # kompakter neu geschrieben (gleiche Logik) und prueft vor dem Aufruf
        # zusaetzlich TYPEMASK_PLAYER (Deskriptor-Feld OBJECT_FIELD_TYPE):
        # Spieler wie im Original, NPCs wie bei Robinsch.
        Patch 0x33D785 @(
            0x75, 0x28, 0x8B, 0x96, 0x38, 0x0A, 0x00, 0x00, 0xF6, 0xC6, 0x08, 0x75, 0x1D, 0xF6, 0xC1, 0x20,
            0x75, 0x13, 0xF6, 0xC6, 0x10, 0x75, 0x0E, 0x83, 0xF8, 0x0B, 0x74, 0x05, 0x83, 0xF8, 0x0C, 0x75,
            0x30, 0x33, 0xC9, 0xEB, 0x08, 0x6A, 0x0C, 0x59, 0xEB, 0x03, 0x6A, 0x0B, 0x59, 0x3B, 0xC1, 0x74,
            0x20, 0x8B, 0xCE, 0xE8, 0xD3, 0xFA, 0xFD, 0xFF, 0x85, 0xC0, 0x74, 0x15, 0x8B, 0x46, 0x08, 0xF6,
            0x40, 0x08, 0x10, 0x74, 0x0C, 0x6A, 0xFF, 0x6A, 0x00, 0x8B, 0xCE, 0xE8, 0x5B, 0xC8, 0xFF, 0xFF,
            0x90
        )
    }}

    @{ Id = 'spellanim'; Cat = 'gameplay'; On = $true
       Author = 'Robinsch'
       De = 'Zauber-Animation nach Abbruch repariert'
       En = 'Fix spell animation after cancelled channel'
       Code = {
        Patch 0x33E0D6 @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'ghostattack'; Cat = 'gameplay'; On = $true
       Author = 'Robinsch (fixed by St0ny)'
       De = '"Geister"-Angriff von NPCs beim Evade behoben'
       En = 'Fix "ghost" attack when NPCs evade from combat'
       Code = {
        # Vor jedem neuen Nahkampf-Ergebnis (SMSG_ATTACKERSTATEUPDATE) spielt
        # der Client den zuletzt gespeicherten Schlag noch einmal auf dem Ziel
        # ab (VA 0x7561BF in UnitCombat_C, Aufruf 0x755A60). Nach einem Evade
        # ist das ein veralteter Schlag - der "Geister"-Angriff. je -> jmp:
        # der gespeicherte Schlag wird nur noch geloescht, nicht abgespielt.
        # Robinschs Offset 0x355BF ist ein Tippfehler (eine 5 zu wenig) und
        # traf einen call in einer String-Hilfsfunktion (Endlosschleife).
        Patch 0x3555BF @(0xEB)
    }}

    @{ Id = 'naked'; Cat = 'gameplay'; On = $true
       Author = 'Robinsch (fixed by St0ny)'
       De = 'Nackter-Charakter-Bug behoben'
       En = 'Fix naked character bug'
       Code = {
        # Die Abfrage, ob der eigene Spieler die X-Ray-Aura hat (VA 0x6DE840,
        # Bit 1 von [Spieler+0xF42]), meldet immer "nein": je -> jmp bei
        # VA 0x6DE85D. Mit der Aura zeichnet der Client andere Einheiten ohne
        # Ausruestung. Robinsch hat mit der Basis 0x500C00 statt 0x400C00
        # gerechnet; sein Offset 0x1DDC5D traf ein push in GetTradeSkillTools.
        Patch 0x2DDC5D @(0xEB)
    }}

    @{ Id = 'forcereaction'; Cat = 'gameplay'; On = $true
       Author = 'Robinsch'
       De = 'Force-Reaction bei /reload erhalten'
       En = 'Keep force reaction on /reload'
       Code = {
        Patch 0x12811E @(0x90, 0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'mail'; Cat = 'gameplay'; On = $true
       Author = 'Robinsch'
       De = 'Neue Post ohne 60 Sekunden Wartezeit'
       En = 'New mail without the 60-second wait'
       Code = {
        Patch 0x16D899 @(0x05, 0x01, 0x00, 0x00, 0x00)
    }}

    @{ Id = 'deadchat'; Cat = 'gameplay'; On = $true
       Author = 'Robinsch'
       De = 'Chat-Befehle auch im Tod erlauben'
       En = 'Allow chat commands while dead'
       Code = {
        Patch 0x10CA41 @(0xEB)
    }}

    @{ Id = 'follow'; Cat = 'gameplay'; On = $false; PublicUntested = $true
       Author = 'St0ny (original by Alastor StrixEfuartus)'
       De = '/follow auch bei NPCs erlauben'
       En = 'Allow /follow on NPCs'
       Code = {
        # Portierung des /follow-Patches aus der 12th Generation EXE (Alastor
        # StrixEfuartus, hier aus patch-007-allow_follow.bat), angepasst von St0ny.
        # Vor dem Folgen ruft der Client eine Pruefung auf (call 0x729BD0 bei VA
        # 0x72B525) und bricht bei "nein" ab. Das Original lenkt den Aufruf in eine
        # Code-Hoehle um, die die Pruefung zwar ausfuehrt, ihr Ergebnis aber
        # ignoriert und immer zum Erfolgsweg 0x72B546 springt. Diese Hoehle laege
        # im .text-Padding bei 0x9DE3B8 - genau dort, wo WorldFrame-Absturzfix
        # und NPC-Ausblenden ihre Code-Hoehlen haben.
        # Gleiche Wirkung ohne Hoehle: den bedingten Sprung direkt hinter der
        # Pruefung (jne 0x72B546 bei VA 0x72B52C) unbedingt machen. Der Code am
        # Ziel setzt die Flags selbst neu, haengt also nicht davon ab.
        Patch 0x32A92C @(0xEB)
    }}

    @{ Id = 'level101'; Cat = 'gameplay'; On = $false; Needs = @('glue')
       Author = 'Alastor StrixEfuartus (fixed by St0ny)'
       De = 'Level 101+ Fix (Spielwert-Tabellen, Barbierstuhl, Grundwerte)'
       En = 'Level 101+ fix (game tables, barber chair, base stats)'
       Code = {
        # Die Spielwert-Tabellen (gtCombatRatings, gtBarberShopCostBase,
        # gtOCTRegenHP/MP, gtChanceToMeleeCrit, ... - elf Tabellen) sind je
        # Spalte 100 Zeilen lang, eine je Level. Der gemeinsame Zugriff (VA
        # 0x7F69B0, Zwilling 0x7F69E0 fuer den zweiten Wert eines Eintrags)
        # rechnet Index = Zeilen * Spalte + (Level - 1); ab Level 101 landet er
        # ausserhalb der Spalte - falsche Werte oder Absturz (Druiden-Grundwerte,
        # Barbierstuhl).
        # Die verbreitete Fassung (12th Generation EXE) entfernt dort einfach das
        # "+ Zeile" - damit ignorieren ALLE Abfragen das Level, auch unter 100
        # (Wertungen, Krit-Chance, Regeneration zeigen Level-1-Werte).
        # Hier wird die Zeile stattdessen auf die letzte Zeile der Spalte
        # begrenzt: Level 101+ bekommt die Werte fuer Level 100, alles darunter
        # bleibt unveraendert. Beide Funktionen werden neu geschrieben (48 bzw.
        # 23 Byte, der Zwilling ruft den ersten Zugriff auf und liest dessen
        # zweiten Wert), nichts springt in ihre Mitte.
        # Braucht laut Quelle den Patch "Custom Glue-XML erlauben" (glue).
        Patch 0x3F5DB0 @(0x55, 0x8B, 0xEC, 0x8B, 0xC1, 0x8B, 0x48, 0x0C, 0x8B, 0x40, 0x08, 0x8B, 0x40, 0x04, 0x8B, 0x55, 0x08, 0x3B, 0xD0, 0x72, 0x03, 0x8D, 0x50, 0xFF, 0x0F, 0xAF, 0x45, 0x0C, 0x03, 0xC2, 0x8B, 0x51, 0x18, 0x8B, 0x52, 0x04, 0x83, 0xC1, 0x18, 0x50, 0xFF, 0xD2, 0xD9, 0x00, 0x5D, 0xC2, 0x08, 0x00)
        Patch 0x3F5DE0 @(0x55, 0x8B, 0xEC, 0xFF, 0x75, 0x0C, 0xFF, 0x75, 0x08, 0xE8, 0xC2, 0xFF, 0xFF, 0xFF, 0xDD, 0xD8, 0xD9, 0x40, 0x04, 0x5D, 0xC2, 0x08, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC)
    }}

    @{ Id = 'raceclass'; Cat = 'gameplay'; On = $false; BanRisk = $true
       Author = 'Alastor StrixEfuartus / Robinsch'
       De = 'Charaktererstellung: mehr als 10 Klassen (Zufallsklasse)'
       En = 'Character creation: more than 10 classes (random class)'
       NoteDe = 'fuer eigene Klassen; Server muss es unterstuetzen'
       NoteEn = 'for custom classes; server must support it'
       Code = {
        # Die Zufallsauswahl der Klasse bei der Charaktererstellung (VA 0x4E0F50)
        # sammelt die erlaubten Klassen in einem Feld mit 10 Plaetzen auf dem
        # Stack. Mit eigenen Klassen (ChrClasses.dbc, mehr als 10) wuerde es
        # ueberlaufen. Das Feld wird auf 30 Plaetze vergroessert: Stackrahmen
        # 0x28 -> 0x78 und die drei Zugriffe [ebp-0x28] -> [ebp-0x78].
        # Welche Rasse welche Klasse darf, prueft weiterhin der Server.
        Patch 0xE0355 @(0x78)
        Patch 0xE038E @(0x88)
        Patch 0xE03A3 @(0x88)
        Patch 0xE03C3 @(0x88)
    }}

    @{ Id = 'namecheck'; Cat = 'gameplay'; On = $false; BanRisk = $true
       Author = 'Alyst3r (0x539wowmod) (fixed by St0ny)'
       De = 'Namenspruefung bei der Charaktererstellung abschalten (z.B. Zahlen im Namen)'
       En = 'Disable the name check in character creation (e.g. digits in names)'
       NoteDe = 'Server muss die Namen ebenfalls erlauben'
       NoteEn = 'server must allow the names as well'
       Code = {
        # Die Pruefung bei VA 0x6B0F90 (cdecl) liefert sofort 0x57 = Name gueltig:
        # mov eax, 57h / ret. Im Original (0x539wowmod) per Detour mit falscher
        # Aufrufkonvention (stdcall), hier direkt in der Funktion.
        Patch 0x2B0390 @(0xB8, 0x57, 0x00, 0x00, 0x00, 0xC3)
    }}

    @{ Id = 'maxchars'; Cat = 'gameplay'; On = $true
       Author = 'St0ny'
       De = 'Max. Charaktere pro Server auf 255 erhoeht'
       En = 'Max characters per realm raised to 255'
       Code = {
        Patch 0x6404F @(0xFF)
    }}

    @{ Id = 'customitem'; Cat = 'gameplay'; On = $false; Needs = @('cache'); PublicUntested = $true; GameUntested = $true
       Author = 'Kebabstorm (fixed by St0ny)'
       De = 'Custom Item Fix (BETA) v2'
       En = 'Custom Item Fix (BETA) v2'
       NoteDe = 'Custom-Items ohne DBC-Anpassung: Modell, Icon und Item-Typ aus den Serverdaten'
       NoteEn = 'custom items without DBC changes: model, icon and item type from the server data'
       Code = {
        # Im Spiel getestet. Viele Stellen im Client lesen Display-
        # ID, Inventartyp, Klasse, Unterklasse und Scheide eines Items nur aus der
        # Item.dbc. Custom-Items, die nur in der Datenbank des Servers stehen,
        # fehlen dort - kein Modell am Charakter, kein Icon. Die Wow.exe hat aber
        # schon Helfer, die zuerst im Item-Cache (Daten vom Server) und erst dann
        # in der Item.dbc suchen (thiscall, ecx = Zeiger auf die Item-ID):
        # 0x758DD0 Inventartyp, 0x758E50 Display-ID, 0x758F50 Scheide. Der Patch
        # leitet die reinen DBC-Zugriffe auf diese Helfer um.
        # Vorlage ist "Custom Item Fix (BETA) v1" aus Kebabstorms "WoW 3.3.5
        # Patcher (Custom Item Fix)" (wowmodding.net, Datei 283). Die Patch-Liste,
        # aus der er uebernommen wurde, hatte zwei Fehler, die den Client
        # abstuerzen lassen: Bei 0x35813C fehlte vorne das Byte 01 (der Klassen-
        # Helfer wurde zu Datenmuell), und 0x1AAAFA war eine Kopie der Zeile
        # 0x1AA9D0 (der call landete mitten in 0x758F50). Beides ist hier
        # korrigiert. Nicht uebernommen: die PE-Pruefsumme bei 0x168 (Windows
        # prueft sie bei Programmen nicht) und "Cache" -> "||che" bei 0x61BE58 -
        # das ist genau der Patch "CACHE-Ordner-Erstellung deaktivieren",
        # deshalb hier nur als Needs.
        #
        # Helfer Klasse (0x758D30) und Unterklasse (0x758D80) suchen bisher nur
        # im Cache. Bei einem Fehlschlag geht es jetzt mit der Item-ID weiter in
        # den DBC-Teil von CGItem::GetClass/GetSubClass (0x707226/0x707256).
        Patch 0x358136 @(0x56, 0x8B, 0x31, 0x89, 0xF0)
        Patch 0x35813C @(0x01, 0x99, 0x6A, 0x00, 0x68, 0x70, 0xEB, 0x5E, 0x00, 0x33, 0xC2, 0x8D, 0x4D, 0xF8, 0x51, 0x2B, 0xC2, 0x50, 0xB9, 0x28, 0xD8, 0xC5, 0x00, 0xC7, 0x45, 0xF8)
        Patch 0x358157 @(0x00, 0x00, 0x00, 0xC7, 0x45, 0xFC)
        Patch 0x35815E @(0x00, 0x00, 0x00, 0xE8, 0xCA, 0x3C, 0xF2, 0xFF, 0x85, 0xC0, 0x74, 0x08)
        Patch 0x35816B @(0x40, 0x04, 0x5E, 0x8B, 0xE5, 0x5D, 0xC3, 0x89, 0xF0, 0x5E, 0x89, 0xEC, 0x5D, 0xE9, 0xA9, 0xE4, 0xFA, 0xFF)
        Patch 0x358186 @(0x56, 0x8B, 0x31, 0x89, 0xF0)
        Patch 0x35818C @(0x01, 0x99, 0x6A, 0x00, 0x68, 0x70, 0xEB, 0x5E, 0x00, 0x33, 0xC2, 0x8D, 0x4D, 0xF8, 0x51, 0x2B, 0xC2, 0x50, 0xB9, 0x28, 0xD8, 0xC5, 0x00, 0xC7, 0x45, 0xF8)
        Patch 0x3581A7 @(0x00, 0x00, 0x00, 0xC7, 0x45, 0xFC)
        Patch 0x3581AE @(0x00, 0x00, 0x00, 0xE8, 0x7A, 0x3C, 0xF2, 0xFF, 0x85, 0xC0, 0x74)
        Patch 0x3581BB @(0x40, 0x08, 0x5E, 0x8B, 0xE5, 0x5D, 0xC3, 0x89, 0xF0, 0x5E, 0x89, 0xEC, 0x5D, 0xE9, 0x89, 0xE4, 0xFA, 0xFF)
        # CGItem::GetClass, GetSubClass, GetInventoryType, GetDisplayId, GetSheath
        # und das Item-Icon (0x707220 bis 0x70AA00) holen ihre Werte ueber die
        # Helfer. 0x707214, 0x70728C und 0x707298 sind kleine Stubs in frei
        # gewordenen Bytes, 0x707298 gehoert zur Aufrufstelle 0x5AB421.
        Patch 0x306614 @(0x8B, 0x41, 0x08, 0x8D, 0x48, 0x0C, 0xE9, 0x11, 0x1B, 0x05, 0x00)
        Patch 0x306620 @(0xEB, 0xF2, 0xCC, 0xCC, 0xCC, 0xCC)
        Patch 0x306650 @(0xEB, 0x3A, 0xCC, 0xCC, 0xCC, 0xCC)
        Patch 0x306683 @(0x8D, 0x48)
        Patch 0x306686 @(0xE9, 0x45, 0x1B, 0x05, 0x00, 0xCC, 0x8B, 0x41, 0x08, 0x8D, 0x48, 0x0C, 0xE9, 0xE9, 0x1A, 0x05, 0x00, 0xCC, 0x8D, 0x4D, 0x08, 0xE8, 0xB0, 0x1B, 0x05)
        Patch 0x3066A0 @(0xE9, 0x8C, 0x41, 0xEA, 0xFF, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC)
        Patch 0x306703 @(0x8D, 0x48)
        Patch 0x306706 @(0xE9, 0x45, 0x1B, 0x05, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC)
        Patch 0x306733 @(0x8D, 0x48)
        Patch 0x306736 @(0xE9, 0x15, 0x1C, 0x05, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC)
        Patch 0x309E03 @(0x8D, 0x48)
        Patch 0x309E06 @(0xE8, 0x45, 0xE4, 0x04, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
        # Aufrufstellen mit direktem Item.dbc-Zugriff: aus "mov ecx,0xAD3D64 /
        # call ItemDB::GetRecord" und spaeter "mov eax,[eax+0x14]" wird
        # "mov ecx,esp / call Helfer / add esp,4". 0x5A8906 (in der Zeile
        # 0x1A7CF5) ist ein Stub fuer 0x5ABC76: Inventartyp und Display-ID.
        Patch 0x11646D @(0x56, 0x89, 0xE1, 0xE8, 0xDB, 0x1D, 0x24, 0x00, 0x83, 0xC4, 0x04, 0x89, 0xC6, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
        Patch 0x1164AC @(0x89, 0xF1, 0x90)
        Patch 0x1223F7 @(0x56, 0x89, 0xE1, 0xE8, 0x51, 0x5E, 0x23, 0x00, 0x83, 0xC4, 0x04, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
        Patch 0x122419 @(0x89, 0xC7, 0x90)
        Patch 0x1A54EF @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x8D, 0x4D, 0xF4)
        Patch 0x1A54F9 @(0x53, 0x2D, 0x1B)
        Patch 0x1A5528 @(0x90, 0x90, 0x90)
        Patch 0x1A552C @(0x45, 0xF4)
        Patch 0x1A572E @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x89, 0xD9)
        Patch 0x1A5737 @(0x15, 0x2B, 0x1B)
        Patch 0x1A575C @(0x90, 0x90, 0x90)
        Patch 0x1A5760 @(0x4D, 0xF8)
        Patch 0x1A7CF5 @(0x83, 0xC4, 0x04, 0x56, 0x89, 0xE1, 0xE8, 0xD0, 0x04, 0x1B, 0x00, 0x83, 0xC4, 0x04, 0xEB, 0x17, 0xCC, 0x89, 0xC3, 0x89, 0xE1, 0xE8, 0x41, 0x05, 0x1B)
        Patch 0x1A7D0F @(0x83, 0xC4, 0x04, 0xE9, 0x6B, 0x33, 0x00, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0x85, 0xC0)
        Patch 0x1A8C8E @(0x89, 0xE1, 0xE8, 0xBB, 0xF5, 0x1A, 0x00, 0x83, 0xC4, 0x04)
        Patch 0x1A8C9C @(0x90, 0x90, 0x90)
        Patch 0x1AA6D4 @(0x89, 0xE1, 0xE8, 0x75, 0xDB, 0x1A, 0x00, 0x83, 0xC4, 0x04)
        Patch 0x1AA6E2 @(0x90, 0x90, 0x90)
        Patch 0x1AA821 @(0x90, 0x8D, 0x4D, 0x08, 0xE8, 0xA6, 0xD9, 0x1A)
        Patch 0x1AA82A @(0x8B, 0xF8, 0xE9, 0x67, 0xBE, 0x15, 0x00)
        Patch 0x1AA832 @(0xC0)
        Patch 0x1AA86C @(0x90, 0x89, 0xF8)
        Patch 0x1AA8A2 @(0x89, 0xE1, 0xE8, 0xA7, 0xD9, 0x1A, 0x00, 0x83, 0xC4, 0x04)
        Patch 0x1AA8B0 @(0x90, 0x90, 0x90)
        Patch 0x1AA9D0 @(0x89, 0xE1, 0xE8, 0x79, 0xD8, 0x1A, 0x00, 0x83, 0xC4, 0x04)
        Patch 0x1AA9DE @(0x90, 0x90, 0x90)
        Patch 0x1AAAFA @(0x89, 0xE1, 0xE8, 0x4F, 0xD7, 0x1A, 0x00, 0x83, 0xC4, 0x04)
        Patch 0x1AAB08 @(0x90, 0x90, 0x90)
        Patch 0x1AB076 @(0x89, 0xE1, 0xE8, 0x53, 0xD1, 0x1A, 0x00, 0xE9, 0x84, 0xCC, 0xFF, 0xFF)
        Patch 0x1AB083 @(0xC0)
        Patch 0x1AB0A9 @(0x90, 0x90, 0x85, 0xDB)
        Patch 0x1AB316 @(0x89, 0xE1, 0xE8, 0x33, 0xCF, 0x1A, 0x00, 0x83, 0xC4, 0x04)
        Patch 0x1AB324 @(0x90, 0x90, 0x90)
    }}

    @{ Id = 'climb'; Cat = 'gameplay'; On = $false; BanRisk = $true
       Author = 'Alastor StrixEfuartus'
       De = 'Steigwinkel-Begrenzung aufheben (jeden Hang hochlaufen)'
       En = 'Remove the climb angle limit (walk up any slope)'
       Code = {
        # Aus der 12th Generation EXE (Alastor StrixEfuartus). VA 0xA37F0C ist
        # der Kosinus des steilsten begehbaren Hangs, im Original 0.6427876 =
        # cos(50 Grad). Die Bewegungs-/Kollisionsroutinen vergleichen die
        # Neigung damit; 0.0 = cos(90 Grad) macht jeden Hang begehbar.
        Patch 0x63670C @(0x00, 0x00, 0x00, 0x00)
    }}

    @{ Id = 'jump'; Cat = 'gameplay'; On = $false; BanRisk = $true
       Author = 'Alastor StrixEfuartus'
       De = 'Sprunghoehe aendern (Original -7.9555473)'
       En = 'Change jump height (original -7.9555473)'
       PromptDe = 'Neuer Wert, negativ - je kleiner, desto hoeher (z.B. -11.25 = doppelte Hoehe)'
       PromptEn = 'New value, negative - the lower, the higher (e.g. -11.25 = double height)'
       Default = '-7.9555473'
       Check = { param($v) Test-JumpValue $v }
       Decode = { ([BitConverter]::ToSingle($script:f, 0x6A1BDC)).ToString('R', [System.Globalization.CultureInfo]::InvariantCulture) }
       Code = {
        # Aus der 12th Generation EXE (Alastor StrixEfuartus). VA 0xAA33DC ist
        # die Anfangsgeschwindigkeit des Sprungs (float, einzige Lesestelle
        # fld bei VA 0x98845C), im Original -7.9555473 = D8 93 FE C0.
        Patch 0x6A1BDC ([BitConverter]::GetBytes([float](ConvertTo-JumpValue $script:VALUES['jump'])))
    }}

    @{ Id = 'airforward'; Cat = 'gameplay'; On = $false; BanRisk = $true
       Author = 'Alyst3r (0x539wowmod) (ported by St0ny)'
       De = 'Im Sprung vorwaerts/rueckwaerts steuern'
       En = 'Steer forward/backward while jumping'
       Code = {
        # Nach 0x539wowmod. Dort ersetzt die DLL die Vorwaerts-Eingabe
        # (VA 0x988A20) durch eine eigene Funktion; die unterscheidet sich vom
        # Original nur in zwei Spruengen, die hier direkt geaendert werden:
        #  - VA 0x988A3D je -> jmp: in der Luft (Fall-Flag 0x1000) nicht mehr
        #    abbrechen, sondern die Richtung wie am Boden setzen
        #  - VA 0x988AD2 je -> jmp: Geschwindigkeit auch in der Luft neu berechnen
        # Dazu aus der DLL: VA 0x987EFD je -> jmp, die Bewegung wird auch in der
        # Luft aktualisiert.
        Patch 0x587E3D @(0xEB)
        Patch 0x587ED2 @(0xEB)
        Patch 0x5872FD @(0xEB)
    }}

    @{ Id = 'airlateral'; Cat = 'gameplay'; On = $false; BanRisk = $true
       Author = 'Alyst3r (0x539wowmod) (ported by St0ny)'
       De = 'Im Sprung seitwaerts steuern'
       En = 'Steer sideways while jumping'
       Code = {
        # Nach 0x539wowmod, wie oben fuer die Seitwaerts-Eingabe
        # (VA 0x988B00):
        #  - VA 0x988B25 je -> jmp: in der Luft nicht mehr abbrechen
        #  - VA 0x988B81 je -> jmp: Geschwindigkeit auch in der Luft neu berechnen
        # Dazu aus der DLL: VA 0x988BEF jne -> 6x NOP (Funktion bei VA 0x988BA0
        # bricht bei gesetztem Fall-Flag nicht mehr vor der Neuberechnung ab).
        Patch 0x587F25 @(0xEB)
        Patch 0x587F81 @(0xEB)
        Patch 0x587FEF @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'airturn'; Cat = 'gameplay'; On = $false; BanRisk = $true
       Author = 'Alyst3r (0x539wowmod) (ported by St0ny)'
       De = 'Im Sprung drehen aendert die Flugrichtung'
       En = 'Turning while jumping changes the flight direction'
       Code = {
        # Nach 0x539wowmod. Beim Drehen (VA 0x989B70) setzt der Client
        # die Bewegungsrichtung nur am Boden neu; in der Luft springt er bei
        # VA 0x989B97 (jne) daran vorbei. 2x NOP: auch in der Luft.
        Patch 0x588F97 @(0x90, 0x90)
    }}

    @{ Id = 'doublejump'; Cat = 'gameplay'; On = $false; GrowsExe = $true; BanRisk = $true
       Author = 'Alyst3r (0x539wowmod) (ported by St0ny)'
       De = 'Doppelsprung (weitere Spruenge in der Luft)'
       En = 'Double jump (more jumps in the air)'
       PromptDe = 'Anzahl zusaetzlicher Spruenge in der Luft, 1 bis 9 (1 = Doppelsprung)'
       PromptEn = 'Number of extra jumps in the air, 1 to 9 (1 = double jump)'
       Default = '1'
       Check = { param($v) Test-DoubleJump $v }
       Decode = { Get-DoubleJumpFromExe }
       Code = {
        # Eigene beschreibbare Sektion (.djump), siehe Add-DoubleJump.
        Add-DoubleJump ([int]$script:VALUES['doublejump'])
    }}

    @{ Id = 'noammo'; Cat = 'gameplay'; On = $false; PublicUntested = $true; GameUntested = $true
       Author = 'Alyst3r (ported by St0ny)'
       De = 'Fernkampf ohne Munition'
       En = 'Ranged attacks without ammo'
       NoteDe = 'Server muss mitspielen, sonst meldet er weiter "Keine Munition"'
       NoteEn = 'the server has to support it, otherwise it still reports "no ammo"'
       Code = {
        # Spell_C_HaveEquippedSpellItems (VA 0x8093D0): Bei Zaubern, die
        # Munition verlangen (Schiessen, Automatischer Schuss ...), prueft der
        # Client ab VA 0x809540 die Munition. Ein Sprung zum Erfolgsausgang
        # (VA 0x8095FF) laesst diese Pruefung weg. Der Server prueft selbst -
        # ohne Anpassung am Server bleibt es bei seiner Fehlermeldung.
        Patch 0x408940 @(0xE9, 0xBA, 0x00, 0x00, 0x00)
    }}

    # --- Grafik & Sichtweite ---

    @{ Id = 'farclip'; Cat = 'graphics'; On = $true
       Author = 'Alastor StrixEfuartus'
       De = 'CVar farclip unlock (max 10000)'
       En = 'CVar farclip unlock (max 10000)'
       Code = {
        # Beide Floats sind Obergrenzen derselben Klemme in ClampFarclip
        # (VA 0x780770), die den Wert beim Setzen des CVars kappt.
        # Normalfall 1583.33 Yards:
        Patch 0x63CF10 @(0x00, 0x40, 0x1C, 0x46)
        # Rueckfallwert 791.67 Yards - greift auf den alten Vanilla-Zonen
        # (mapId < 530 sowie 543 und 575) und bei <= 1 GB RAM, das prueft
        # die Funktion per GlobalMemoryStatusEx. Muss mit hoch, sonst faellt
        # die Sichtweite dort wieder auf 791 zurueck.
        Patch 0x63CF0C @(0x00, 0x40, 0x1C, 0x46)
    }}

    @{ Id = 'horizon'; Cat = 'graphics'; On = $true
       Author = 'St0ny'
       De = 'CVar horizonFarclipScale unlock (max 12)'
       En = 'CVar horizonFarclipScale unlock (max 12)'
       Code = {
        Patch 0x38CBDF @(0x7C, 0x04, 0xA1, 0x00)
    }}

    @{ Id = 'envdetail'; Cat = 'graphics'; On = $true
       Author = 'St0ny'
       De = 'CVar environmentDetail unlock (kein Limit statt 1.5)'
       En = 'CVar environmentDetail unlock (no limit instead of 1.5)'
       Code = {
        # Im Setz-Callback (VA 0x78DC60) wird der geklemmte Wert durch den
        # Rohwert ersetzt (fstp st(1) -> fstp st(0)). Der Ausgang ist fuer beide
        # Grenzen derselbe, es faellt also auch die Untergrenze 0.5 weg.
        Patch 0x38D08E @(0xD8)
    }}

    @{ Id = 'grounddist'; Cat = 'graphics'; On = $true
       De = 'CVar groundEffectDist unlock (max 3166 statt 140)'
       En = 'CVar groundEffectDist unlock (max 3166 instead of 140)'
       Code = {
        Patch 0x5E74FC @(0xAB, 0xEA, 0x45, 0x45)
    }}

    @{ Id = 'sliders'; Cat = 'graphics'; On = $false; Needs = @('farclip', 'envdetail', 'grounddist')
       Author = 'St0ny'
       De = 'Grafikoptionen: Slider-Maxima erweitern'
       En = 'Graphics options: extend slider maximums'
       Code = {
        # Hebt die Obergrenzen der Regler im Video-Menue an (Reiter "Effekte").
        # Die CVar-Sperren sind mit den Patches darueber laengst offen - die Regler
        # selbst blieben trotzdem auf Blizzards Werten stehen, weil sie ihr Maximum
        # woanders herholen.
        #
        # WO DAS MAXIMUM HERKOMMT
        # Interface\FrameXML\OptionsPanelTemplates.lua baut jeden Regler so auf:
        #     minValue = BlizzardOptionsPanel_GetCVarMinSafe(cvar) or entry.minValue
        #     maxValue = BlizzardOptionsPanel_GetCVarMaxSafe(cvar) or entry.maxValue
        # Also erst die EXE fragen, und nur wenn die nichts liefert, den in der Lua
        # hinterlegten Ersatzwert nehmen. GetCVarMax kennt aber nur zwei CVars:
        # "extShadowQuality" (zaehlt die verfuegbaren Schattenstufen aus) und
        # "farclip" (liefert den festen double 1277.0 aus 0x9F57D8). Fuer alles
        # andere kommt nil zurueck, und dann greifen die Konstanten aus
        # VideoOptionsPanels.lua: environmentDetail 1.5, groundEffectDist 140,
        # groundEffectDensity 64. Genau das sind die Werte, an denen die Regler
        # bisher endeten.
        #
        # ACHTUNG: GetCVarMax liegt ZWEIMAL in der EXE, einmal fuer den
        # Glue-Screen (VA 0x4DDF80) und einmal fuer das laufende Spiel
        # (VA 0x514E30). Beide sind bis auf die Registerbelegung gleich gebaut;
        # im Spiel haelt ebx den Lua-State, im Glue-Screen edi. Wer nur eine der
        # beiden patcht, sieht im Spiel keinerlei Wirkung. Dasselbe gilt fuer
        # GetCVarMin (0x4DDEA0 / 0x514D40), das hier aber unangetastet bleibt.
        #
        # WAS DER PATCH TUT
        # In beiden Funktionen wird der farclip-Vergleich durch einen Aufruf einer
        # gemeinsamen Such-Routine ersetzt, die eine Namensliste durchlaeuft.
        # Treffer -> zugehoeriges Maximum auf den FPU-Stack und weiter im
        # vorhandenen lua_pushnumber-Pfad. Kein Treffer -> in den vorhandenen
        # nil-Pfad, alle uebrigen CVars verhalten sich also unveraendert.
        # Die Dateigroesse bleibt gleich, und die Code-Hoehle am Ende von .text
        # bleibt frei fuer WorldFrame-Absturzfix und NPC-Ausblenden.
        #
        #   CVar                  vorher   nachher
        #   farclip               1277     2477
        #   environmentDetail      1.5      2.5
        #   groundEffectDist       140      250
        #   groundEffectDensity     64      256
        #
        # Die Untergrenzen bleiben unangetastet: GetCVarMin wird nicht angefasst,
        # gibt fuer diese drei weiter nil zurueck, und damit gelten die Lua-Minima
        # 0.5 / 70 / 16 (bei farclip die 177.0 aus der EXE, VA 0x9F5798).
        # Die Schrittweiten stehen ebenfalls in der Lua und gehen ohne Nacharbeit
        # glatt auf: environmentDetail 0.25 -> 8 Stufen, groundEffectDist 10 -> 18,
        # groundEffectDensity 8 -> 30. Bei farclip rechnet
        # VideoOptionsEffectsPanel_OnEvent die Schrittweite bei jedem
        # PLAYER_ENTERING_WORLD ohnehin als (max-min)/10 neu, hier also 230.
        #
        # ZWEI EINSCHRAENKUNGEN
        # 1. Der Regler setzt nur das CVar. Ohne die Unlock-Patches darueber klemmt
        #    der Client den Wert beim Setzen sofort wieder auf sein Original.
        # 2. Bei groundEffectDensity wirkt oberhalb von 64 nichts mehr: der
        #    Vertexbuffer der Detail-Doodads ist bei VA 0x7B2A9D auf
        #    density*64 <= 4096 geklemmt. Der Regler laeuft dann zwar bis 256,
        #    optisch aendert sich ab 64 aber nichts.

        # 1) Such-Routine in einer 19-Byte-int3-Luecke zwischen zwei Funktionen
        #    (VA 0x9296ED, Datei 0x528AED; nichts springt dorthin). 18 Byte.
        #    Eingang: ebx = CVar-Name (aus dem CVar-Objekt, [obj+0x14]),
        #    esi = Anfang der Namensliste. Ausgang: esi steht hinter dem
        #    gefundenen Namen bzw. hinter der Endmarke; die Stubs lesen
        #    [esi-4] (0 = Endmarke) und das Maximum bei [esi+16].
        #    Als Laengenlimit fuer SStrCmpI dient esi selbst - eine feste
        #    Adresse in .rdata, also immer unter 0x7FFFFFFF (die CRT lehnt
        #    groessere Werte ab) und weit laenger als jeder CVar-Name.
        #    SStrCmpI (stdcall, raeumt selbst auf) erhaelt ebx/esi/edi.
        #    L:lodsd                           eax = Namenszeiger, esi += 4
        #      test eax, eax / jz R            0x00000000 = Endmarke
        #      push esi / push eax / push ebx
        #      call SStrCmpI (0x76E780)
        #      test eax, eax / jnz L           0 = Treffer
        #    R:ret
        Patch 0x528AED @(0xAD, 0x85, 0xC0, 0x74, 0x0C, 0x56, 0x50, 0x53, 0xE8, 0x86, 0x50, 0xE4, 0xFF, 0x85, 0xC0, 0x75, 0xEF, 0xC3)

        # 2) Aufrufstelle im Glue-Screen: ersetzt den farclip-Vergleich bei
        #    0x4DE046 (26 Byte). esi (der Name) ist danach tot, ebx wird
        #    gesichert - im Spiel haelt es den Lua-State. eax/ecx/edx waren
        #    schon im Original durch den SStrCmpI-Aufruf verbraucht.
        #      push ebx / mov ebx, esi / mov esi, 0xAB5680 (Namensliste)
        #      call 0x9296ED / pop ebx
        #      cmp dword [esi-4], 0 / je 0x4DE07A (nil-Pfad)
        #      fld dword [esi+16] / 3x nop -> 0x4DE060 (lua_pushnumber-Pfad)
        Patch 0xDD446 @(0x53, 0x8B, 0xDE, 0xBE, 0x80, 0x56, 0xAB, 0x00, 0xE8, 0x9A, 0xB6, 0x44, 0x00, 0x5B, 0x83, 0x7E, 0xFC, 0x00, 0x74, 0x20, 0xD9, 0x46, 0x10, 0x90, 0x90, 0x90)

        # 3) Dieselbe Aufrufstelle im Spiel, bei 0x514EEA. Gleicher Stub, nur
        #    andere Ziele: nil-Pfad 0x514F1E, Fortsetzung 0x514F04.
        Patch 0x1142EA @(0x53, 0x8B, 0xDE, 0xBE, 0x80, 0x56, 0xAB, 0x00, 0xE8, 0xF6, 0x47, 0x41, 0x00, 0x5B, 0x83, 0x7E, 0xFC, 0x00, 0x74, 0x20, 0xD9, 0x46, 0x10, 0x90, 0x90, 0x90)

        # 4) Tabelle im .rdata-Padding (VA 0xAB5680, 384 freie Bytes ab 0x6B3E80,
        #    hinter der VirtualSize, aber innerhalb der Rohdaten - der Lader
        #    blendet die ganze Seite ein). Erst fuenf Namenszeiger (der letzte
        #    0x00000000 = Endmarke), dahinter die vier Maxima als float, in
        #    derselben Reihenfolge: Maximum i liegt 16 Byte hinter Name i+1.
        #    Als Namen dienen die CVar-Namen, die ohnehin in der EXE stehen:
        #      0x9F57A0 "farclip"              2477.0
        #      0xA3F3BC "environmentDetail"       2.5
        #      0xA3F438 "groundEffectDist"      250.0
        #      0xA3F460 "groundEffectDensity"   256.0
        Patch 0x6B3E80 @(0xA0, 0x57, 0x9F, 0x00, 0xBC, 0xF3, 0xA3, 0x00, 0x38, 0xF4, 0xA3, 0x00, 0x60, 0xF4, 0xA3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xD0, 0x1A, 0x45, 0x00, 0x00, 0x20, 0x40, 0x00, 0x00, 0x7A, 0x43, 0x00, 0x00, 0x80, 0x43)
    }}

    @{ Id = 'goscale'; Cat = 'graphics'; On = $false; Needs = @('envdetail')
       Author = 'St0ny'
       De = 'GameObject Sichtweite: Cat 0 und Cat 4 auf environmentDetail reagieren lassen'
       En = 'GameObject view distance: Cat 0 and Cat 4 scale with environmentDetail'
       Code = {
        # Ergaenzt einen im Client fehlenden Rechenschritt.
        #
        # Die Funktion bei VA 0x78F570 bildet aus den Basiswerten die Laufzeitwerte neu,
        # jedes Mal wenn environmentDetail gesetzt wird. Fuer Cat 1, 2 und 3 lautet sie
        #     Laufzeit-Sichtweite = Basiswert * environmentDetail
        # fuer Cat 0 und Cat 4 dagegen nur
        #     Laufzeit-Sichtweite = Basiswert
        # Dort fehlt die Multiplikation schlicht, der Regler erreicht diese beiden
        # Kategorien also gar nicht.
        #
        # Beide Bloecke beginnen mit einer Kopie der Groessen-Schwellen (Default nach
        # Runtime). Die beiden Tabellen sind byte-gleich und werden von nichts veraendert,
        # die Kopie ist damit wirkungslos. Ihre 12 Byte werden hier frei und reichen fuer
        # den fehlenden Schritt:
        #
        #   vorher (24 Byte)                 nachher (24 Byte)
        #   fld  [SizeThresh_def]   6        fld  [ebp+8]        3   Faktor laden
        #   fstp [SizeThresh_rt]    6        fmul [BaseDist]     6   damit multiplizieren
        #   fld  [BaseDist]         6        fst  [RuntimeDist]  6   Ergebnis ablegen
        #   fst  [RuntimeDist]      6        9x nop              9   Rest auffuellen
        #
        # Danach ist der FPU-Stack genauso belegt wie vorher (st0 = Laufzeit-Sichtweite),
        # der Folgecode ab "fld [FadeBand]" laeuft unveraendert weiter.
        #
        # WIRKUNG: die Sichtweiten-Tabellen bleiben auf den Blizzard-Werten
        # (30/100/200/750/1250), environmentDetail wird zum sauberen Gesamtregler:
        #   ED 1.0  ->   30 / 100 / 200 /  750 / 1250   = x1 gegenueber Blizzard
        #   ED 2.0  ->   60 / 200 / 400 / 1500 / 2500   = x2
        #   ED 2.4  ->   72 / 240 / 480 / 1800 / 3000   = x2.4
        # Alle fuenf Kategorien behalten dabei ihr Verhaeltnis zueinander. Werte ueber 1.5
        # brauchen zusaetzlich den Patch "CVar environmentDetail unlock".
        #
        # Der folgende Patch "Cat 0 von 30 auf 50 Yards" setzt zusaetzlich einen festen
        # Basiswert fuer Cat 0. Er wird nur gebraucht, wenn die Kategorien UNTERSCHIEDLICH
        # skaliert werden sollen - fuer gleichmaessiges Hoch- und Runterregeln reicht
        # dieser Patch hier allein.
        # Cat 0, VA 0x78F573
        Patch 0x38E973 @(0xD9, 0x45, 0x08, 0xD8, 0x0D, 0x64, 0xF3, 0xAD, 0x00, 0xD9, 0x15, 0xA0, 0xF3, 0xAD, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
        # Cat 4, VA 0x78F664
        Patch 0x38EA64 @(0xD9, 0x45, 0x08, 0xD8, 0x0D, 0x74, 0xF3, 0xAD, 0x00, 0xD9, 0x15, 0xB0, 0xF3, 0xAD, 0x00, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'cat0'; Cat = 'graphics'; On = $false
       Author = 'St0ny'
       De = 'GameObject Sichtweite: Cat 0 von 30 auf 50 Yards'
       En = 'GameObject view distance: Cat 0 from 30 to 50 yards'
       NoteDe = 'kostet Leistung, mehr Kleinkram sichtbar'
       NoteEn = 'costs performance, more small objects visible'
       Code = {
        # Hebt ausschliesslich die kleinste Objektkategorie an (Kerzen, Buecher, Saecke,
        # Werkzeug). Cat 1 bis 4 werden von diesem Patcher ohnehin nicht angefasst,
        # geregelt wird die Sichtweite ueber das CVar environmentDetail (Patch davor).
        # Cat 0 ist im Original mit 30 Yards so knapp bemessen, dass Kleinkram deutlich
        # frueher verschwindet als alles andere; 50 verbessert das Verhaeltnis zu Cat 1
        # von 1:3.3 auf 1:2, und der Regler zieht den Kleinkram proportional mit.
        #
        # Geschrieben werden nur die Cat-0-Felder, jeweils die ersten 4 Byte der Tabelle.
        # Beim Aendern muessen alle fuenf zusammenpassen:
        #   Basis == Laufzeit
        #   Sichtweite^2 == Basis * Basis        (darueber cullt die Engine, spart die Wurzel)
        #   Fade-Start   == Basis - Fade-Band    (Fade-Band Cat 0 = 5, bleibt unangetastet)
        #   Fade-Start^2 == Fade-Start * Fade-Start
        #
        #   hier:      Basis 50   Laufzeit 50   Quadrat 2500  Fade-Start 45  Fade-Quadrat 2025
        #   Blizzard:  Basis 30   Laufzeit 30   Quadrat  900  Fade-Start 25  Fade-Quadrat  625
        #
        # Der Client rechnet die vier abgeleiteten Werte zwar neu, sobald environmentDetail
        # gesetzt wird - steht das CVar aber gar nicht in der Config.wtf, bleiben die
        # Tabellenwerte stehen und muessen dann zur Basis passen.
        # Basis-Sichtweite Cat 0: 50
        Patch 0x6DD364 @(0x00, 0x00, 0x48, 0x42)
        # Laufzeit-Sichtweite Cat 0: 50
        Patch 0x6DD3A0 @(0x00, 0x00, 0x48, 0x42)
        # Sichtweite im Quadrat Cat 0: 2500
        Patch 0x6DD3B4 @(0x00, 0x40, 0x1C, 0x45)
        # Fade-Start Cat 0: 45 (= 50 minus Fade-Band 5)
        Patch 0x6DD3C8 @(0x00, 0x00, 0x34, 0x42)
        # Fade-Start im Quadrat Cat 0: 2025
        Patch 0x6DD3DC @(0x00, 0x20, 0xFD, 0x44)
    }}

    @{ Id = 'occluder'; Cat = 'graphics'; On = $false
       Author = 'Robinsch'
       De = 'Occluder Fix fuer Stormwind (Open Azeroth)'
       En = 'Occluder fix for Stormwind (Open Azeroth)'
       Code = {
        # VA 0xAF0040 ist der Karten-Schluessel (mapId 0 = Oestliche
        # Koenigreiche) des ersten Eintrags der fest eingebauten Occluder-Tabelle
        # (VA 0x7CDD31 vergleicht ihn mit der aktuellen Karte). 99999 passt zu
        # keiner Karte - die Stormwind-Occluder werden nie mehr angewendet.
        Patch 0x6EE040 @(0x9F, 0x86, 0x01, 0x00)
    }}

    @{ Id = 'bluemoon'; Cat = 'graphics'; On = $true
       Author = 'Robinsch'
       De = 'Blauer Mond am Nachthimmel reaktiviert'
       En = 'Re-enable the blue moon in the night sky'
       Code = {
        Patch 0x5CFBC0 @(0xC7, 0x05, 0x74, 0x8E, 0xD3, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xC3)
    }}

    @{ Id = 'notransparency'; Cat = 'graphics'; On = $true
       Author = 'Alastor StrixEfuartus'
       De = 'Keine Transparenz beim Heranzoomen'
       En = 'No character transparency when zooming in'
       Code = {
        Patch 0x336841 @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'nofade'; Cat = 'graphics'; On = $false; PublicUntested = $true; GameUntested = $true
       Author = 'Alyst3r (0x539wowmod) (ported by St0ny)'
       De = 'Kein Ausblenden fuer NPCs mit Flag DO_NOT_FADE_IN'
       En = 'No fade-out for NPCs with flag DO_NOT_FADE_IN'
       NoteDe = 'Server muss das Flag setzen'
       NoteEn = 'server must set the flag'
       Code = {
        # Code-Hoehle am Ende von .text, siehe Get-CodeCave / Add-NoFadeOutFlag.
        Add-NoFadeOutFlag
    }}

    @{ Id = 'hdportraits'; Cat = 'graphics'; On = $false; GrowsExe = $true
       Author = 'St0ny (original by Badgermilk0)'
       De = 'HD Unit-Frame Portraits: Renderaufloesung 256 statt 64 Pixel'
       En = 'HD unit frame portraits: render resolution 256 instead of 64 pixels'
       Code = {
        # Haengt die .hdp-Sektion an und biegt den Model-Render-Pfad auf 256px um.
        # Erzeugt keine neuen Portraits: Die Unit-Frames zeigen schon im Original
        # das 3D-Modell, nur die Textur, in die es gerendert wird, waechst von
        # 64x64 auf 256x256 Pixel. Die Groesse ist der einzige Parameter.
        Add-HdPortraits 256
    }}

    @{ Id = 'iconsnap'; Cat = 'graphics'; On = $false; GrowsExe = $true
       Author = 'tb (ported by St0ny)'
       De = 'Icons im Text pixelgenau (scharf statt verschwommen)'
       En = 'Pixel-exact icons in text (sharp instead of blurry)'
       Code = {
        # Eigene Sektion (.isnap) hinter ParseEmbeddedTexture, siehe Add-IconPixelSnap.
        Add-IconPixelSnap
    }}

    # --- Interface & Komfort ---

    @{ Id = 'tracker'; Cat = 'ui'; On = $false
       De = 'Quest-Tracker automatisch sortieren'
       En = 'Auto-sort quest tracker'
       Code = {
        Patch 0x11D4C5 @(0x64, 0x14, 0x9E, 0x00)
    }}

    @{ Id = 'worldmap'; Cat = 'ui'; On = $false
       De = 'Erweiterte Weltkarte standardmaessig aktiv'
       En = 'Advanced world map enabled by default'
       Code = {
        Patch 0x11D462 @(0x64, 0x14, 0x9E, 0x00)
    }}

    @{ Id = 'castbars'; Cat = 'ui'; On = $true
       Author = 'Kebabstorm'
       De = 'Cast Bars auf allen Frames'
       En = 'Cast bars on all frames'
       Code = {
        Patch 0x123676 @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'emblems'; Cat = 'ui'; On = $false; Needs = @('mpqnames'); PublicUntested = $true
       Author = 'MacWarrior'
       De = 'Retail-Gildenembleme: Auswahl von 170 auf 196 erweitert'
       En = 'Retail guild emblems: selection extended from 170 to 196'
       NoteDe = 'benoetigt Patch-G'
       NoteEn = 'requires Patch-G'
       Url = 'https://discord.com/channels/407664041016688662/1541873346608889936'
       Code = {
        # Entspricht dem Pattern-Replace "73 00 00 AA 00 00" -> "73 00 00 C4 00 00".
        # Das Muster kommt in der Original-EXE genau einmal vor, ab Datei-Offset
        # 0x613105: "73 00" ist das 's' samt Terminator des Lua-Namens
        # "InitializeTabardColors", das dritte Byte Ausrichtungs-Padding. Erst
        # danach faengt der eigentliche Wert an, gepatcht wird also 0x613108.
        #
        # DIE TABELLE (VA 0xA14908, Datei 0x613108) - fuenf DWORDs, je einer pro
        # Tabard-Kategorie:
        #   Idx  VA         Kategorie            Wert
        #    0   0xA14908   Embleme               170   <- dieser Patch
        #    1   0xA1490C   Emblemfarben           17
        #    2   0xA14910   Bordueren               6
        #    3   0xA14914   Borduerenfarben        17
        #    4   0xA14918   Hintergrundfarben      51
        #
        # Beide Stellen, die die Tabelle nutzen, lesen den Zaehler zur Laufzeit:
        #   VA 0x599481  mov edi,[esi*4+0xA14908]
        #                Durchschalten im Tabard-Designer (Lua-Seite:
        #                TabardModel:CycleVariation(Kategorie+1, Schritt), esi ist
        #                der auf 0..4 gepruefte Index). Der neue Index wird direkt
        #                danach per idiv gegen denselben Zaehler modulo genommen -
        #                alles ab 170 war damit gar nicht erst erreichbar.
        #   VA 0x599729  mov esi,0xA14908
        #                Zufalls-Tabard, zieht je Kategorie rand() * Zaehler. Die
        #                Schleife laeuft bis 0xA1491C, daher genau fuenf Eintraege.
        # Eine zweite, fest verdrahtete 170 gibt es im Emblem-Pfad nicht - der
        # Zaehler ist die einzige Stelle, die Grenze faellt also vollstaendig.
        #
        # 196 (0xC4) ist die Emblemzahl von Retail.
        #
        # VORAUSSETZUNG: ZUSAETZLICHES MPQ-PATCH-ARCHIV NOETIG
        # Dieser Patch hebt nur den Zaehler an, er bringt keine Grafiken mit. Die
        # 26 neuen Wappen (Index 170 bis 195) muessen als eigenes MPQ-Archiv im
        # Data-Ordner liegen. Fehlt es, sind die neuen Plaetze im Tabard-Designer
        # zwar anwaehlbar, bleiben aber leer.
        # Die Dateinamen baut der Client bei VA 0x4E8210 aus zwei Zahlen -
        # Emblem-Index und Farbindex, in dieser Reihenfolge:
        #   Textures\GuildEmblems\Emblem_<Index>_<Farbe>_TU_U   (obere Haelfte)
        #   Textures\GuildEmblems\Emblem_<Index>_<Farbe>_TL_U   (untere Haelfte)
        # So stehen die Formatstrings in der EXE, die Endung .blp haengt der
        # Texturlader an. Pro Wappen also 17 Farben x 2 Haelften = 34 Dateien,
        # fuer die 26 neuen Wappen zusammen 884.
        # Der Archivname ist frei waehlbar (patch-*.MPQ), dafuer sorgt der Patch
        # "Erweiterte MPQ-Namen erlauben" (mpqnames).
        Patch 0x613108 @(0xC4)
    }}

    @{ Id = 'flash'; Cat = 'ui'; On = $true
       Author = 'Kebabstorm'
       De = 'FlashWindow Patch'
       En = 'FlashWindow patch'
       NoteDe = 'benoetigt FlashWindow-Addon'
       NoteEn = 'requires the FlashWindow addon'
       Url = 'https://github.com/noname08662/awesome_wotlk/tree/main/addons/Flash'
       Code = {
        # Ersetzt die in 3.3.5a funktionslose Lua-Funktion BNRemoveFriend (VA
        # 0x534ED5, Datei 0x1342D5) durch FlashWindow(): GetModuleHandleA
        # ("user32.dll") / GetProcAddress("FlashWindow") / FlashWindow(hwnd,
        # FALSE) - genau wie die Fassung in der AwesomeWotlkLib.dll. Der Name
        # im Lua-Namenseintrag (VA 0xA086E4, Datei 0x606EE4) wird mit
        # "FlashWindow" ueberschrieben.
        Patch 0x1342D5 @(0x14, 0x68, 0xD8, 0x4C, 0x9E, 0x00, 0xFF, 0x15, 0xB0, 0xF1, 0x9D, 0x00, 0x68, 0xE4, 0x86, 0xA0, 0x00, 0x50, 0xE8, 0xCD, 0x7E, 0xEE, 0xFF, 0x6A, 0x00, 0xB9, 0x20, 0x16, 0xD4, 0x00, 0xFF, 0x31, 0xFF, 0xD0, 0xB8, 0x00, 0x00, 0x00, 0x00, 0xC9, 0xC3, 0xCC)
        Patch 0x606EE4 @(0x46, 0x6C, 0x61, 0x73, 0x68, 0x57, 0x69, 0x6E, 0x64, 0x6F, 0x77, 0x00, 0x00, 0x00)
    }}

    @{ Id = 'charrandom'; Cat = 'ui'; On = $false
       Author = 'Alyst3r (0x539wowmod)'
       De = 'Charaktererstellung: Aussehen nicht automatisch auswuerfeln'
       En = 'Character creation: do not randomize the appearance automatically'
       Code = {
        # VA 0x4E147B: je -> jmp, die automatischen Zufallsaufrufe beim Oeffnen
        # (ResetCharCustomize) bzw. Volk-/Geschlechtswechsel werden
        # uebersprungen. Der Zufall-Knopf
        # (RandomizeCharCustomization, VA 0x4E1B60) nutzt einen eigenen Weg.
        Patch 0xE087B @(0xEB)
    }}

    @{ Id = 'lootopen'; Cat = 'ui'; On = $false; PublicUntested = $true
       Author = 'tb (ported by St0ny)'
       De = 'Lootfenster bleibt beim Laufen offen'
       En = 'Loot window stays open while moving'
       Code = {
        # Zehn Bewegungs-Handler (Laufen, Seitwaerts, Drehen, Neigen ...) der
        # eigenen Figur schliessen das Lootfenster (Aufruf VA 0x523640). Das
        # "je" vor dem Aufruf wird zu "jmp", der Aufruf entfaellt.
        Patch 0x32A347 @(0xEB)   # VA 0x72AF47
        Patch 0x32C62E @(0xEB)   # VA 0x72D22E
        Patch 0x32DA4B @(0xEB)   # VA 0x72E64B
        Patch 0x32DAFB @(0xEB)   # VA 0x72E6FB
        Patch 0x32DBAB @(0xEB)   # VA 0x72E7AB
        Patch 0x32DCBD @(0xEB)   # VA 0x72E8BD
        Patch 0x32DD7B @(0xEB)   # VA 0x72E97B
        Patch 0x32DE2B @(0xEB)   # VA 0x72EA2B
        Patch 0x32DF4B @(0xEB)   # VA 0x72EB4B
        Patch 0x32DFCA @(0xEB)   # VA 0x72EBCA
    }}

    @{ Id = 'showlevel'; Cat = 'ui'; On = $false; PublicUntested = $true
       Author = 'tb (ported by St0ny)'
       De = 'Echtes Level statt "??" bei Gegnern ab 10 Level ueber dir'
       En = 'Real level instead of "??" for enemies 10+ levels above you'
       NoteDe = 'Bosse zeigen weiter "??" - dafuer Nr. 73'
       NoteEn = 'bosses still show "??" - see No. 73'
       Code = {
        # Lua UnitLevel (VA 0x60F9E0), Tooltip (VA 0x620EE0) und Namensplakette
        # (VA 0x98EF10) zeigen "??" (bzw. -1 / Totenkopf), wenn ein feindliches
        # Ziel 10 oder mehr Level ueber dir ist. Diese Pruefung ("jle") faellt
        # weg; die Boss-Pruefung direkt dahinter bleibt (die nimmt Nr. 73 raus).
        Patch 0x20EEB2 @(0x90, 0x90)
        Patch 0x220B66 @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
        Patch 0x58E3B9 @(0x90, 0x90)
    }}

    @{ Id = 'showlevelboss'; Cat = 'ui'; On = $false; Needs = @('showlevel'); PublicUntested = $true
       Author = 'St0ny'
       De = 'Echtes Level auch bei Bossen statt "??" (Erweiterung zu Nr. 72)'
       En = 'Real level for bosses too instead of "??" (extension to No. 72)'
       Code = {
        # Ist eine Kreatur als Boss markiert (Flag 0x4 in den Kreatur-Typflags,
        # Pruefung CGUnit_C::IsBossMob bei VA 0x715D70), zeigen UnitLevel,
        # Tooltip und Namensplakette immer "??" bzw. -1 / Totenkopf. Diese drei
        # Boss-Pruefungen fallen weg; die Beschriftung "Boss" im Tooltip und das
        # Elite-Symbol der Namensplakette bleiben. Gegner 10+ Level ueber dir
        # zeigen ihr Level erst zusammen mit Nr. 72.
        Patch 0x20EEBD @(0xEB)                                 # VA 0x60FABD UnitLevel: je -> jmp (kein -1)
        Patch 0x220B78 @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90)   # VA 0x621778 Tooltip: jne "??" -> nop
        Patch 0x58E358 @(0xEB)                                 # VA 0x98EF58 Namensplakette: je -> jmp (Level statt Totenkopf)
    }}

    @{ Id = 'holdrepeat'; Cat = 'ui'; On = $false; GrowsExe = $true; BanRisk = $true
       Author = 'tb (ported by St0ny)'
       De = 'Aktionstasten gedrueckt halten zum Wiederholen'
       En = 'Hold action buttons to repeat'
       Code = {
        # Eigene beschreibbare Sektion (.hrep) mit Hooks in ExecKey, UseAction
        # und OnWorldRender, siehe Add-HoldRepeat. Fest: 500 ms bis zur ersten
        # Wiederholung, danach hoechstens alle 100 ms, nur wenn die Aktion
        # bereit ist (keine Abklingzeit, kein laufender Zauber).
        Add-HoldRepeat
    }}


    # --- Fenster, Maus & Kamera ---

    @{ Id = 'bubblerange'; Cat = 'ui'; On = $false
       Author = 'St0ny'
       De = 'Sprechblasen-Reichweite erhoehen (Original 25 Meter)'
       En = 'Increase the chat bubble range (original 25 yards)'
       PromptDe = 'Reichweite in Metern: 50, 100, 150, 200 oder 0 = unbegrenzt'
       PromptEn = 'Range in yards: 50, 100, 150, 200 or 0 = unlimited'
       Default = '50'
       Check = { param($v) Test-BubbleRange $v }
       Decode = { Get-BubbleRangeFromExe }
       Code = {
        # Zwei Abstandspruefungen gegen 625.0 = 25 Meter im Quadrat:
        # fcomp [0xA104B0] bei VA 0x7200CE (neue Blase nur in Reichweite, gilt
        # fuer Sagen, Gruppe, Schreien und NPC-Sagen/-Schreien) und bei VA
        # 0x56C5E9 (vorhandene Blase ausblenden, wenn der Sprecher zu weit weg
        # ist). Beide lesen danach die gewaehlte Konstante, siehe $BUBBLE_RANGES.
        $va = [BitConverter]::GetBytes([uint32]$BUBBLE_RANGES[$script:VALUES['bubblerange'].Trim()])
        Patch 0x31F4D0 $va
        Patch 0x16B9EB $va
    }}

    @{ Id = 'window'; Cat = 'window'; On = $false
       Author = 'St0ny'
       De = 'Fenstermodus als Standard setzen'
       En = 'Windowed mode by default'
       NoteDe = 'startet als kleines Fenster mitten auf dem Desktop - maximiert nur zusammen mit Nr. 77'
       NoteEn = 'starts as a small window in the middle of the desktop - maximized only together with No. 77'
       Code = {
        Patch 0x369A7D @(0x64, 0x14, 0x9E)
    }}

    @{ Id = 'maximize'; Cat = 'window'; On = $false; Needs = @('window')
       Author = 'St0ny'
       De = 'Fenstermodus maximiert als Standard setzen'
       En = 'Maximized window by default'
       NoteDe = 'wirkt nur zusammen mit Nr. 76'
       NoteEn = 'only works together with No. 76'
       Code = {
        Patch 0x369AB2 @(0x64, 0x14, 0x9E)
    }}

    @{ Id = 'windowfix'; Cat = 'window'; On = $true
       Author = 'Robinsch'
       De = 'Kein schwarzer Bildschirm beim Wechsel in den Fenstermodus'
       En = 'No black screen when switching to windowed mode'
       Code = {
        Patch 0xE94 @(0xEB)
    }}

    @{ Id = 'mouse'; Cat = 'window'; On = $true
       Author = 'Robinsch'
       De = 'Mausflackern / Kameraspruenge Fix'
       En = 'Mouse flicker / camera jump fix'
       Code = {
        Patch 0x469A2C @(0xE9, 0x71, 0xF0, 0x0B, 0x00, 0xF8, 0x13, 0xD4, 0x00, 0x8B, 0x1D, 0xFC)
        Patch 0x528AA2 @(0x8D, 0x4D, 0xF0, 0x51, 0x57, 0xFF, 0x15, 0xDC, 0xF5, 0x9D, 0x00, 0x8B, 0x45, 0xF0, 0x8B, 0x15, 0xF8, 0x13, 0xD4, 0x00, 0xE9, 0x7A, 0x0F, 0xF4, 0xFF)
        Patch 0x4691B1 @(0x89, 0xE5, 0x8B, 0x05, 0xFC, 0x13, 0xD4, 0x00, 0x8B, 0x0D, 0xF8, 0x13, 0xD4, 0x00, 0xEB, 0xC2, 0x7D, 0x03, 0x83, 0xC1, 0x01, 0x83, 0xC0, 0x32, 0x83, 0xC1, 0x32, 0x3B, 0x0D, 0xEC, 0xBC, 0xCA, 0x00, 0x7E, 0x03, 0x83, 0xE9, 0x01, 0x3B, 0x05, 0xF0, 0xBC, 0xCA, 0x00, 0x7E, 0x03, 0x83, 0xE8, 0x01, 0x83, 0xE9, 0x32, 0x83, 0xE8, 0x32, 0x89, 0x0D, 0xF8, 0x13, 0xD4, 0x00, 0x89, 0x05, 0xFC, 0x13, 0xD4, 0x00, 0x89, 0xEC, 0x5D, 0xE9, 0xB4, 0xF7, 0xFF, 0xFF, 0xEC, 0x5D, 0xC3, 0xC3)
        Patch 0x469183 @(0x83, 0xF8, 0x32, 0x7D, 0x03, 0x83, 0xC0, 0x01, 0x83, 0xF9, 0x32, 0xEB, 0x31)
    }}

    @{ Id = 'camera'; Cat = 'window'; On = $false; GrowsExe = $true; PublicUntested = $true
       Author = 'Stormhand (fixed by St0ny)'
       De = 'CameraReforged [BETA]: Kamerahoehe und Zoom-Grenzen'
       En = 'CameraReforged [BETA]: camera height and zoom limits'
       NoteDe = 'Schulterversatz noch ohne Wirkung'
       NoteEn = 'shoulder offset has no effect yet'
       Code = {
        # BETA - funktioniert noch nicht zu 100 Prozent, hier fliesst noch Arbeit rein.
        #
        # Portierung von CameraReforged (Stormhand), mit seiner Erlaubnis eingebaut.
        # Der Original-Patcher ist ein eigenstaendiges Tool mit GUI; hier steckt
        # nur seine Patch-Logik, damit alles in einem Durchgang laeuft.
        #
        # WAS DER PATCH TUT
        # 1. Er registriert beim Start zwei neue CVars direkt im Client, die es
        #    in 3.3.5a gar nicht gibt. Bisher brauchte man dafuer ConsoleXP.dll
        #    samt Injector - das faellt damit weg.
        #      test_cameraHeight        Hoehe des Fokuspunkts in Yards. Der Client
        #                               zielt auf die Brust; der Wert hebt die
        #                               Kamera auf Kopfhoehe an. Bereich 0.0 - 3.0.
        #      test_cameraOverShoulder  Seitlicher Versatz in Yards, negativ =
        #                               links. Bereich -2.0 - 2.0. NOCH OHNE
        #                               WIRKUNG - die Lesestellen der Vorlage
        #                               waren falsch, siehe Add-CameraReforged.
        # 2. Er tauscht die Vorgabewerte zweier vorhandener CVars aus:
        #      cameraDistanceMaxFactor  max. Zoom-Faktor, Blizzard 1.0  -> 2.6
        #      cameraDistanceMoveSpeed  Zoom-Tempo,      Blizzard 8.33 -> 20.0
        #
        # Alle vier sind zur Laufzeit ueber /console <name> <wert> erreichbar und
        # wirken sofort, also auch aus Makros und Addons wie DynamicCam heraus.
        # Die hier gesetzten Werte sind die Startwerte; alle vier werden mit
        # Flag 0x10 registriert und landen damit in der Config.wtf, eine
        # Aenderung per /console ueberlebt also den Neustart.
        #
        # WERTE AENDERN
        # Einfach die vier Zahlen unten anpassen und neu patchen. Die Funktion
        # baut Texte, Zeiger und Sprungziele daraus neu auf und prueft die
        # Bereiche; ausserhalb bricht sie mit Meldung ab.
        #
        # WO DAS IM BINARY LANDET
        # Eine eigene, angehaengte Sektion ".camr" (RWX) mit Code und Daten,
        # Detours auf CVars_Initialize und den Kamera-Fokuspfad, dazu zwei
        # umgebogene Vorgabewerte. Details stehen bei Add-CameraReforged oben.
        #
        # EINE EINSCHRAENKUNG
        # Dieser Patch veraendert wie die HD-Portraits die
        # Dateigroesse und die PE-Struktur (etwa +1 KB), weil er eine Sektion
        # anhaengt. Das ist unvermeidbar: der Weg der Vorlage - Caves ins
        # .rdata-Padding und die Sektion dafuer ausfuehrbar machen - laesst
        # diesen Client beim Start mit R6002 abbrechen, nachgewiesen mit einem
        # Build, der nur dieses eine Header-Byte aenderte. Auf Servern, die den
        # Client auf Groesse oder Sektionsaufbau pruefen, kann das auffallen.
        # Die SHA256-Pruefung des Patchers betrifft nur die Eingabe und bleibt
        # davon unberuehrt.
        Add-CameraReforged -Height 0.5 -Shoulder 0.0 -MaxFactor 2.6 -ZoomSpeed 20.0
    }}

    # --- Sound ---

    @{ Id = 'sound'; Cat = 'sound'; On = $false
       Author = 'St0ny'
       De = 'Sound-Einstellungen optimieren'
       En = 'Optimize sound settings'
       NoteDe = 'benoetigt OpenAL, sonst wirken die Einstellungen nicht'
       NoteEn = 'requires OpenAL, otherwise the settings have no effect'
       Url = 'https://github.com/kcat/openal-soft'
       Code = {
        Patch 0x0C77C2 @(0xC7, 0x45, 0xF8, 0x7E, 0x00, 0x00, 0x00, 0x90, 0x90, 0x90)
        Patch 0x6B3F80 @(0x36, 0x34, 0x00)
        Patch 0x6B3F84 @(0x32, 0x00)
        Patch 0x0D0604 @(0x68, 0x84, 0x57, 0xAB, 0x00)
        Patch 0x0D0624 @(0x68, 0x80, 0x57, 0xAB, 0x00)
        Patch 0x0D064A @(0x68, 0x64, 0x14, 0x9E, 0x00)
        Patch 0x0D077F @(0x68, 0x64, 0x14, 0x9E, 0x00)
    }}


    # --- Client-Infos ---

    @{ Id = 'clientversion'; Cat = 'client'; On = $false; BanRisk = $true
       Author = 'MacWarrior'
       De = 'Client-Version aendern (Original 3.3.5)'
       En = 'Change client version (original 3.3.5)'
       PromptDe = 'Neue Client-Version, Format x.y.z, max. 7 Zeichen'
       PromptEn = 'New client version, format x.y.z, max. 7 characters'
       Default = '3.3.5'
       Check = { param($v) Test-ClientVersion $v }
       Decode = { Read-AsciiZ 0x5F3A08 8 }
       Code = {
        # Portierung von edit_version.py (MacWarrior): Version im Spiel, die
        # Versionsressource (FileVersion/ProductVersion) und VS_FIXEDFILEINFO.
        # Die Build-Nummer bleibt erhalten.
        Set-ClientVersion $script:VALUES['clientversion']
    }}

    @{ Id = 'clientbuild'; Cat = 'client'; On = $false; BanRisk = $true
       Author = 'MacWarrior'
       De = 'Build-Nummer aendern (Original 12340)'
       En = 'Change build number (original 12340)'
       PromptDe = 'Neue Build-Nummer, 6142 bis 65535'
       PromptEn = 'New build number, 6142 to 65535'
       Default = '12340'
       Check = { param($v) Test-ClientBuild $v }
       Decode = { [string](RU16 $script:f 0x4C99F0) }
       Code = {
        # Portierung von edit_revision.py (MacWarrior): interne und sichtbare
        # Build-Nummer sowie der vierte Teil der FileVersion.
        Set-ClientBuild $script:VALUES['clientbuild']
    }}

    @{ Id = 'clienttitle'; Cat = 'client'; On = $false; BanRisk = $true
       Author = 'MacWarrior (fixed by St0ny)'
       De = 'Programmtitel aendern (Dateieigenschaften und Fenstertitel)'
       En = 'Change program title (file properties and window title)'
       PromptDe = 'Neuer Titel, max. 17 Zeichen, nur ASCII'
       PromptEn = 'New title, max. 17 characters, ASCII only'
       Default = 'World of Warcraft'
       Check = { param($v) Test-ClientTitle $v }
       Decode = { Read-Utf16Z 0x7577C0 50 }
       Code = {
        # Portierung von edit_title.py (MacWarrior): FileDescription,
        # InternalName und ProductName der Versionsressource, dazu der
        # Fenstertitel des Spiels.
        Set-ClientTitle $script:VALUES['clienttitle']
    }}

    @{ Id = 'clientdate'; Cat = 'client'; On = $false; BanRisk = $true
       Author = 'St0ny (original by MacWarrior)'
       De = 'Build-Datum aendern (Original Jun 24 2010)'
       En = 'Change build date (original Jun 24 2010)'
       PromptDe = 'Neues Build-Datum mit Uhrzeit JJJJ-MM-TT HH:MM[:SS], optional mit FR fuer franzoesische Monatsnamen'
       PromptEn = 'New build date with time YYYY-MM-DD HH:MM[:SS], optionally followed by FR for French month names'
       Default = '2010-06-24 23:54:57'
       Suggest = { param($saved) Get-ClientDateSuggestion $saved }
       Check = { param($v) Test-ClientDate $v }
       Normalize = { param($v) ConvertTo-ClientDate $v }
       Decode = { Get-ClientDateFromExe }
       Code = {
        # Portierung von edit_date.py (MacWarrior): die drei Datumsfelder
        # ("Jun 24 2010") und das Jahr im LegalCopyright, dazu die Uhrzeit im
        # Build-Text und der Zeitstempel im PE-Kopf.
        Set-ClientDate $script:VALUES['clientdate']
    }}

    @{ Id = 'clienticon'; Cat = 'client'; On = $false; BanRisk = $true
       Author = 'St0ny (original by MacWarrior)'
       De = 'Programm-Icon aendern (Symbol der Wow.exe)'
       En = 'Change program icon (icon of Wow.exe)'
       PromptDe = 'Icon-Datei (.ico oder .png), Pfad absolut oder relativ zum WoW-Ordner'
       PromptEn = 'Icon file (.ico or .png), path absolute or relative to the WoW folder'
       Default = ''
       Check = { param($v) Test-ClientIcon $v }
       Decode = { Get-ClientIconFromExe }
       Code = {
        # Nach edit_icon.py (MacWarrior), hier ohne Windows-API: Die acht
        # Icon-Bitmaps (48/32/24/16 Pixel, zwei Sprachvarianten) werden an
        # Ort und Stelle ueberschrieben, siehe Set-ClientIcon.
        Set-ClientIcon $script:VALUES['clienticon']
    }}

    @{ Id = 'y38fix'; Cat = 'client'; On = $false; PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Jahr-2038-Fix: Daten um N Jahre verschoben anzeigen'
       En = 'Year 2038 fix: show dates shifted by N years'
       NoteDe = 'nur zusammen mit dem passenden Servermodul'
       NoteEn = 'only together with the matching server module'
       PromptDe = 'Verschiebung in Jahren: 28, 56 oder 84 (wie im Servermodul)'
       PromptEn = 'Shift in years: 28, 56 or 84 (as in the server module)'
       Default = '28'
       Check = { param($v) Test-YearShift $v }
       Decode = { Get-YearShiftFromExe }
       Code = {
        # Jahresbasis, Kalender-Untergrenze und Erfolgsjahre, siehe Set-YearShift.
        Set-YearShift ([int]$script:VALUES['y38fix'].Trim())
    }}
)

# Standard-Preset "Reforged" - das offizielle Preset des Projekts
# Project Reforged (https://projectreforged.github.io/wotlk/), zusammengestellt
# von Stormhand. Nur sichere Patches, alle von Stormhand mehrere Stunden auf
# Warmane getestet (Nr. 9, 63 und 64 vergroessern die Wow.exe). Im Menue mit R, ueber
# -Select reforged; gilt beim ersten Start und fuer neue Patches.
$PRESET_REFORGED = @(
    'laa', 'itemcache', 'timer', 'mirrorfix', 'wmocube', 'glyphfix',
    'scandll', 'noserverpatch', 'nosurvey', 'skipbnet', 'skiprdp', 'nohttp',
    'glue', 'mpqsig', 'mpqnames', 'localdata', 'awesome',
    'areatrigger', 'swing', 'npcanim', 'spellanim', 'ghostattack', 'naked',
    'forcereaction', 'mail', 'deadchat', 'level101',
    'farclip', 'horizon', 'envdetail', 'grounddist', 'sliders', 'goscale',
    'occluder', 'bluemoon', 'notransparency', 'hdportraits', 'iconsnap',
    'tracker', 'worldmap', 'castbars', 'charrandom', 'bubblerange',
    'window', 'maximize', 'windowfix', 'mouse', 'sound'
)

# Preset "St0nys_Wow.exe" - St0nys eigene Auswahl fuer eigene Server (enthaelt
# auch unsichere Patches wie Warden aus und die Sprungsteuerung). Im Menue
# mit S, ueber -Select stony. Ids, die hier fehlen oder unbekannt sind, bleiben aus.
$PRESET_STONY = @(
    'laa', 'itemcache', 'worldcrash', 'timer', 'nothrottle', 'mirrorfix',
    'wmocube', 'glyphfix', 'wardenoff', 'scandll', 'noserverpatch', 'nosurvey',
    'skipbnet', 'skiprdp', 'nohttp', 'afk', 'glue', 'mpqsig',
    'mpqnames', 'localdata', 'awesome', 'areatrigger', 'swing', 'npcanim',
    'spellanim', 'ghostattack', 'naked', 'forcereaction', 'mail', 'deadchat',
    'follow', 'level101', 'airforward', 'airlateral', 'airturn', 'doublejump',
    'farclip', 'horizon', 'envdetail', 'grounddist', 'sliders', 'goscale',
    'cat0', 'occluder', 'bluemoon', 'notransparency', 'iconsnap', 'tracker',
    'worldmap', 'castbars', 'emblems', 'flash', 'holdrepeat', 'bubblerange',
    'window', 'maximize', 'windowfix', 'mouse', 'sound'
)

# ============================================================
#  Original-Bytes je Patch - erzeugt mit -BuildTable, nicht von Hand aendern
# ============================================================
# BEGIN ORIGINAL-BYTES
$ORIGINAL_TABLE = @'
size;7704216
laa;126;03;1
cache;61BE58;4361;1
itemcache;2689FD;3075;1
worldcrash;210;B3D35D00;0
worldcrash;41C91B;0F834D010000;1
worldcrash;5DD7B3;0000000000000000000000000000000000000000000000000000000000000000000000000000;1
timer;46A08E;0F8582000000;1
nothrottle;27547E;56;1
nothrottle;2756DE;56;1
mirrorfix;32F729;E85206DCFF;1
mirrorfix;32F8CA;E8B104DCFF;1
mirrorfix;46B310;558BEC8B4508687026870050E89FFFFFFF83C4085DC3CCCCCCCCCCCCCCCCCCCC;1
wmocube;3BC8AF;56681802A400E8E655FBFF83C4085F5E;1
glyphfix;116;0600;0
glyphfix;160;00D09F00;0
glyphfix;1A8;007C750098120000;0
glyphfix;2F8;00000000000000000000000000000000000000000000000000000000000000000000000000000000;0
glyphfix;2C3ED0;558BEC83EC20;1
glyphfix;2C4520;558BEC83EC0C;1
glyphfix;2C5F90;56578BF16A00;1
glyphfix;2C6880;568BF1837E6400741E8B46488B4E4450E80BB5FFFF85C075078BCEE8F0F6FFFFC74664000000008BCEE86206000033C03986B0000000C786D4000000000000000F95C05EC3;1
glyphfix;2C9350;558BEC51837D0801;1
rce;2A7;E0;1
rce;3D9D7C;750A;1
wardenoff;3D9C5B;7406;1
scandll;5F4D56;5363;1
scandll;5F4D62;5363;1
noserverpatch;DA2A8;85C075;1
nosurvey;DA2BD;68FFFFFF7F;1
skipbnet;2B1F48;74;1
skiprdp;36AE40;74;1
nohttp;46F28F;85C07507;1
afk;12A3AF;0F85A4030000;1
afk;12A64C;E8CFFB3300;1
afk;54AD02;CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC;1
glue;1F41BF;74;1
glue;415A27;5E8BE55DC3;1
glue;415A3F;01;1
glue;415A95;01;1
glue;415B46;7F;1
glue;415B5F;83C0035E8BE55D;1
mpqsig;21350;558BEC8B451C8B4D188B55145368984F9E00508B4510;1
mpqnames;5E0F09;3F;1
mpqnames;5E0F16;3F;1
localdata;1F2A;E821EC01006A00;1
luaunlock;1185E7;33C05050E840A3FFFF83C40833C0;1
luaunlockfull;1185C0;558BEC833D9C;1
luaunlockfull;119BD6;74;1
luaunlockfull;11A097;74;1
luaunlockfull;11CD67;74;1
luaunlockfull;11F088;74;1
luaunlockfull;11F34A;74;1
luaunlockfull;1216E7;74;1
luaunlockfull;124076;74;1
luaunlockfull;1243D7;0F859B020000;1
luaunlockfull;1246E0;74;1
luaunlockfull;127389;74;1
luaunlockfull;40259C;74;1
keyprop;8EFD9;01;1
globalsv;1F8488;8B4508680005000050;1
awesome;ABD0;558BECE898B5FFFF;1
awesome;DC0F0;558BEC568B75;0
awesome;E50B0;558BEC5633F639356CB4B6000F85DB010000393568B4B6000F85CF01000033C0B968B4B6008701566A5468F8659F006A18E85A8828006860659F00A380B4B600E81BBEF7;1
wotlkext;6170;6870EB5E00;1
wotlkext;DC0F0;558BEC568B75;0
wotlkext;E5100;B6006A18526860659F00E881561D0083C40C84C074206854659F00E8C0BFF7FF6854659F006860659F00E841BFF7FF83;1
voicedll;406;91AA0000;1
voicedll;543F45;CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC;1
areatrigger;2DB241;64;1
swing;2E1C67;6AFF6A408BCEE8BE830500;1
npcanim;33D785;75308B96380A0000F7C2000800007522F6C1207516F7C200100000750E83F80B740583F80C752A33C9EB0CB90C000000EB05B90B0000003BC174168BCEE8C9FAFDFF85C0740B6AFF6A008BCEE85AC8FFFF;1
spellanim;33E0D6;6AFF6A008BCEE84FBFFFFF8D8D58FDFFFFE884FEEAFF;1
ghostattack;3555BF;74;1
naked;2DDC5D;74;1
forcereaction;12811E;E89D970A00;1
mail;16D899;0560EA0000;1
deadchat;10CA41;74;1
follow;32A92C;75;1
level101;3F5DB0;558BEC8BC18B480C8B40088B40040FAF450C0345088B51188B520483C11850FFD2D9005DC20800CCCCCCCCCCCCCCCCCC558BEC8BC18B480C8B40088B40040FAF450C0345088B51188B520483C11850FFD2D940045DC20800CCCCCCCCCCCCCC;1
raceclass;E0355;28;1
raceclass;E038E;D8;1
raceclass;E03A3;D8;1
raceclass;E03C3;D8;1
namecheck;2B0390;558BEC8B4508;1
maxchars;6404F;0A;1
customitem;11646D;A15C3DAD003BF07C773B35583DAD007F6F2BF0A16C3DAD008B34B0;1
customitem;1164AC;8B4E14;1
customitem;1223F7;A15C3DAD003BF07C1E3B35583DAD007F168B156C3DAD008BCE2BC88B048A;1
customitem;122419;8B7814;1
customitem;1A54EF;8B4DF451B9643DAD00;1
customitem;1A54F9;93610B;1
customitem;1A5528;8B55F4;1
customitem;1A552C;4214;1
customitem;1A572E;8B0350B9643DAD00;1
customitem;1A5737;555F0B;1
customitem;1A575C;8B45F8;1
customitem;1A5760;4814;1
customitem;1A7CF5;A15C3DAD0083C4043BF07C1F3B35583DAD007F178B156C3DAD;1
customitem;1A7D0F;8BCE2BC88B048A85C0740683781800;1
customitem;1A8C8E;B9643DAD00E8F8290B00;1
customitem;1A8C9C;8B4014;1
customitem;1AA6D4;B9643DAD00E8B20F0B00;1
customitem;1AA6E2;8B4014;1
customitem;1AA821;8B450850B9643DAD;1
customitem;1AA82A;E8610E0B008BF8;1
customitem;1AA832;FF;1
customitem;1AA86C;8B4718;1
customitem;1AA8A2;B9643DAD00E8E40D0B00;1
customitem;1AA8B0;8B4014;1
customitem;1AA9D0;B9643DAD00E8B60C0B00;1
customitem;1AA9DE;8B4014;1
customitem;1AAAFA;B9643DAD00E88C0B0B00;1
customitem;1AAB08;8B4014;1
customitem;1AB076;B9643DAD00E810060B008BD8;1
customitem;1AB083;DB;1
customitem;1AB0A9;837B1800;1
customitem;1AB316;B9643DAD00E870030B00;1
customitem;1AB324;8B4014;1
customitem;306614;CCCCCCCCCCCCCCCCCCCCCC;1
customitem;306620;8B41088B400C;1
customitem;306650;8B41088B400C;1
customitem;306683;8B40;1
customitem;306686;8B0D5C3DAD003BC17C1B3B05583DAD007F132BC18B0D6C3DAD;1
customitem;3066A0;8B048185C074048B4018C333C0C3;1
customitem;306703;8B40;1
customitem;306706;8B0D5C3DAD003BC17C1B3B05583DAD007F132BC18B0D6C3DAD008B048185C074048B4014C333C0C3;1
customitem;306733;8B40;1
customitem;306736;8B0D5C3DAD003BC17C1B3B05583DAD007F132BC18B0D6C3DAD008B048185C074048B401CC333C0C3;1
customitem;309E03;8B40;1
customitem;309E06;8B0D5C3DAD003BC17C243B05583DAD007F1C2BC18B0D6C3DAD008B048185C0740D8B4014;1
customitem;358136;8B016A0199;1
customitem;35813C;006870EB5E0033C28D4DF8512BC250B928D8C500C745F8000000;1
customitem;358157;C745FC000000;1
customitem;35815E;E8CD3CF2FF85C074078B4004;1
customitem;35816B;E55DC333C08BE55DC3CCCCCCCCCCCCCCCCCC;1
customitem;358186;8B016A0199;1
customitem;35818C;006870EB5E0033C28D4DF8512BC250B928D8C500C745F8000000;1
customitem;3581A7;C745FC000000;1
customitem;3581AE;E87D3CF2FF85C074078B40;1
customitem;3581BB;E55DC333C08BE55DC3CCCCCCCCCCCCCCCCCC;1
climb;63670C;BB8D243F;1
jump;6A1BDC;D893FEC0;1
airforward;5872FD;74;1
airforward;587E3D;74;1
airforward;587ED2;74;1
airlateral;587F25;74;1
airlateral;587F81;74;1
airlateral;587FEF;0F85AC010000;1
airturn;588F97;7512;1
doublejump;116;0600;0
doublejump;160;00D09F00;0
doublejump;1A8;007C750098120000;0
doublejump;2F8;0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000;0
doublejump;58782A;8B7E44F7C7001800027544;1
noammo;408940;F64710100F;1
farclip;63CF0C;ABEA4544ABEAC544;1
horizon;38CBDF;F88C9E00;1
envdetail;38D08E;D9;1
grounddist;5E74FC;00000C43;1
sliders;DD446;68FFFFFF7F68A0579F0056E82A07290085C07520DD05D8579F00;1
sliders;1142EA;68FFFFFF7F68A0579F0056E88698250085C07520DD05D8579F00;1
sliders;528AED;CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC;1
sliders;6B3E80;000000000000000000000000000000000000000000000000000000000000000000000000;1
goscale;38E973;D90550F3AD00D91D78F3AD00D90564F3AD00D915A0F3AD00;1
goscale;38EA64;D90560F3AD00D91D88F3AD00D90574F3AD00D915B0F3AD00;1
cat0;6DD364;0000F041;1
cat0;6DD3A0;0000F041;1
cat0;6DD3B4;00006144;1
cat0;6DD3C8;0000C841;1
cat0;6DD3DC;00401C44;1
occluder;6EE040;00000000;1
bluemoon;5CFBC0;C3CCCCCCCCCCCCCCCCCCCC;1
notransparency;336841;8896CB000000;1
nofade;210;B3D35D00;0
nofade;3431A3;8B068B5040;1
nofade;5DD7D9;00000000000000000000000000000000000000000000000000000000000000000000000000;1
hdportraits;116;0600;0
hdportraits;160;00D09F00;0
hdportraits;1A8;007C750098120000;0
hdportraits;2F8;00000000000000000000000000000000000000000000000000000000000000000000000000000000;0
hdportraits;348;00000000000000000000000000000000000000000000000000000000000000000000000000000000;0
hdportraits;21620A;40000000;1
hdportraits;216AA0;558BEC81EC04050000;1
hdportraits;2174E9;930BEAFF;1
hdportraits;218F73;89F6E9FF;1
hdportraits;2193AF;40000000;1
iconsnap;116;0600;0
iconsnap;160;00D09F00;0
iconsnap;1A8;007C750098120000;0
iconsnap;2F8;00000000000000000000000000000000000000000000000000000000000000000000000000000000;0
iconsnap;370;00000000000000000000000000000000000000000000000000000000000000000000000000000000;0
iconsnap;2C0280;558BEC83EC44;1
tracker;11D4C5;A0149E00;1
worldmap;11D462;A0149E00;1
castbars;123676;8BCEE8A3181F00;1
emblems;613108;AA;1
flash;1342D5;0C56E8B4BA17008BF085F60F84860000008B068B90C80000008BCEFFD283F80175758B068B90AC000000;1
flash;606EE4;424E52656D6F7665467269656E64;1
charrandom;E087B;74;1
lootopen;32A347;74;1
lootopen;32C62E;74;1
lootopen;32DA4B;74;1
lootopen;32DAFB;74;1
lootopen;32DBAB;74;1
lootopen;32DCBD;74;1
lootopen;32DD7B;74;1
lootopen;32DE2B;74;1
lootopen;32DF4B;74;1
lootopen;32DFCA;74;1
showlevel;20EEB2;7E0B;1
showlevel;220B66;0F8EDD000000;1
showlevel;58E3B9;7E9F;1
showlevelboss;20EEBD;74;1
showlevelboss;220B78;0F85CB000000;1
showlevelboss;58E358;74;1
holdrepeat;116;0600;0
holdrepeat;160;00D09F00;0
holdrepeat;1A8;007C750098120000;0
holdrepeat;2F8;00000000000000000000000000000000000000000000000000000000000000000000000000000000;0
holdrepeat;398;00000000000000000000000000000000000000000000000000000000000000000000000000000000;0
holdrepeat;F82A0;558BEC83EC34;1
holdrepeat;162550;558BEC81ECC4000000;1
holdrepeat;1AAFC0;558BEC83EC0C;1
bubblerange;16B9EB;B004A100;1
bubblerange;31F4D0;B004A100;1
window;369A7D;A0149E;1
maximize;369AB2;A0149E;1
windowfix;E94;74;1
mouse;469183;CCCCCCCCCCCCCCCCCCCCCCCCCC;1
mouse;4691B1;8BEC83EC108D45F0506A00E8DF28000083C40450FF150CF69D008B45F8992BC28BC88B45FC992BC2D1F8D1F95051890DEC13D400A3F013D400E881EEFFFF83C4088BE55DC3CCCCCCCCCCCCCCCCCCCC;1
mouse;469A2C;8B45F08B15EC13D4008B1DF0;1
mouse;528AA2;CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC;1
camera;116;0600;0
camera;160;00D09F00;0
camera;1A8;007C750098120000;0
camera;2F8;00000000000000000000000000000000000000000000000000000000000000000000000000000000;0
camera;3C0;00000000000000000000000000000000000000000000000000000000000000000000000000000000;0
camera;11CDB0;558BEC81EC80000000;1
camera;1FCE36;68E0E7A100;1
camera;1FD5B2;6840139E00;1
camera;2064CB;D90570169F00;1
sound;C77C2;85C074068B40308945F8;1
sound;D0604;6864149E00;1
sound;D0624;68DC219E00;1
sound;D064A;68A0149E00;1
sound;D077F;68A0149E00;1
sound;6B3F80;000000;1
sound;6B3F84;0000;1
clientversion;5F3A08;332E332E35000000;1
clientversion;7576C8;03000300;1
clientversion;7576CE;05000300030000000000;1
clientversion;7577F6;0F00;1
clientversion;757814;33002C00200033002C00200035002C002000310032003300340030000000;1
clientversion;757986;0C00;1
clientversion;7579A8;560065007200730069006F006E00200033002E0033000000;1
clientbuild;4C99F0;3430;1
clientbuild;5F3A00;313233343000;1
clientbuild;7576CC;3430;1
clienttitle;369519;E832251000;1
clienttitle;36A604;E847141000;1
clienttitle;5E0288;576F726C64206F66205761726372616674000000;1
clienttitle;75779A;1900;1
clienttitle;7577C0;57006F0072006C00640020006F0066002000570061007200630072006100660074002000520065007400610069006C000000;1
clienttitle;757836;1200;1
clienttitle;757854;57006F0072006C00640020006F0066002000570061007200630072006100660074000000;1
clienttitle;757942;1200;1
clienttitle;757960;57006F0072006C00640020006F0066002000570061007200630072006100660074000000;1
clientdate;118;FE52244C;1
clientdate;5F39F4;4A756E2032342032303130;1
clientdate;62F3F3;4A756E2032342032303130;1
clientdate;62F3FF;32333A35343A3537;1
clientdate;636F5F;4A756E2032342032303130;1
clientdate;7578B4;3200300030003400;1
clienticon;74ED84;28000000300000006000000001002000000000000000000000000000000000000000000000000000FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF0001000800010008000100080001000800000000000103070001040B00000000000000000000000200050208000402070002010700020108000201080001000700000005010100011D040000560101039506060BB3080F19C30E1E2BD9112B3DD8133446D9122D3DD50D2030BF081622AC05060E9902000063000001250400000405132B00071934000B17280007142100030E1700030C16000208120001000400010007000100080000000800060207000301080001000800010008000100080001000800010008000100080001000800000000000103070001040B00000000000000000000000200050208000402070002010700020108000101030A00000048030508A90D1F29FA17384CFF2A5F7CFF327799FF3588B2FF3EA2CCFF41AFD7FF4DC6E4FF51CBE6FF4DC3DFFF50C1D8FF47AFC7FF317C94FF23526CFA0C2034C6000A285C04102A070B16260007142100030E1700030C16000208120001000400010007000100080000000800060207000301080001000800010008000100080001000800010008000100080001000800000000000103070001040B000000000000000000000002000502080004020800010003040000006209151ED4174156FF256D8EFF2D8CB8FF2A8EC1FF2E93C9FF3096CEFF34A3DAFF3AB3E2FF3CBBE4FF4ACAEAFF54D5F0FF52D3EFFF4CCBE9FF50D0ECFF59E2F8FF6CEEFDFF6BDFF0FF499EB6FF1D4C68E004112973040B170C030E1600030D16000208120001000400010007000100080000000800060207000301080001000800010008000100080001000800010008000100080001000800000000000103070001040B000000000000000000000002000401060002000051070F18DB1B4A64FF2980A7FF2F9BCBFF339DD1FF2D9DD1FF2495CFFF268CC4FF2782B4FF2775A1FF2A759CFF29698CFF25617FFF2A6374FF3B7383FF3F8AA1FF42A6C4FF4DC8E1FF58E2F8FF6EF4FFFF87FDFFFF7DF1FCFF4CB0C6FF174458DF00060F5C02081100020812000100040001000700010008000000080006020700030108000100080001000800010008000100080001000800010008000100080000000104000003040000050400000004000000020000000801010480132F3EFE27698AFF297BA8FF298AB6FF2D9AC9FF2D90C1FF247097FF204D6BFF162E3FFF131B27FF12101AFF100B0FFF070409FF03030BFF0E0608FF170606FF1D1010FF201F24FF273439FF366570FF50A8B3FF69DEE8FF7EFAFFFF7EF8FFFF6BEAFAFF4092A6FF081320990000070C0001020000000000000002000000020005020500030108000100080001000800010008000100060001000600010006000000030D0B141ACB1C3641E1112633DD0B161CDD040709DC060D11E31E4A5CFF2D7290FF2A7399FF2978A2FF26749EFF184F6DFF0F2A3CFF090D18FF08050BFF0D0809FF110A09FF140D0CFF120E0AFF0E0F11FF090F13FF040D14FF010B15FF030E18FF05111BFF08111CFF0D111BFF15131AFF2A3439FF4192A1FF66E4F3FF7BF6FFFF87FCFFFF65C1D1FF0F2B3DDA1C2C36A31C303CA70A1A27A7122028A8090B10A6010003150100050001000500010005000000000000000000000000000000000F10273EEA64BFE7FF72CFE0FF5DAEC2FF193743FF255568FF2D6A80FF2B6985FF2D6B8AFF1F465FFF091523FF070407FF100804FF0F0907FF180F0AFF20130DFF241510FF231511FF231412FF231512FF1F1411FF121213FF0C1013FF040C14FF030F17FF04101BFF091625FF09192CFF0A1528FF091122FF1B465BFF4DBDD4FF7CF8FFFF91FFFFFF69D7E5FF36768DFF7CC4D4FF8DDDEBFF6CCEEDFF1A4160FD000000210000000000000000000000000000000000000000000000000000000F0B2336EA399DE1FF64A4C6FF325259FF254C5CFF2A5E76FF295E76FF255569FF172833FF110908FF110804FF1E110AFF21130FFF23130DFF241510FF241410FF291A15FF2B1D16FF291915FF271613FF261613FF211411FF1C1413FF141214FF0F1015FF050F17FF05111CFF0A1627FF09192FFF091A31FF081224FF0C2134FF33879EFF75F2FBFFA5FFFFFF89E3EDFF50828FFF6FB8D6FF4CC5FCFF173F5CFD000000210000000000000000000000000000000000000000000000000000000F102736EA389EE1FF173D62FF244552FF2E5C6EFF275871FF214457FF13151BFF120906FF1B120CFF261A14FF2B1C17FF24130DFF25140EFF23140DFF24140CFF28160EFF2D1E10FF2D1D11FF281714FF261614FF281511FF21120BFF17100AFF100C0AFF060B0EFF050D14FF07121FFF081323FF0B1C31FF081B36FF09192EFF071425FF236076FF8AECF4FFCCFFFFFF9AE5EAFF2A5D7BFF3BA8DDFF1C4C68FD000000210000000000000000000000000000000000000000000000000000000F0F2634EA256487FF1F4351FF2E5B6CFF28576CFF1D4053FF1A1415FF20140FFF211712FF32221BFF39251DFF342C29FF2A426DFF293A6FFF243B6EFF263B70FF2A3967FF2C3352FF313747FF1C1312FF1C110BFF25232FFF242F60FF253469FF23396EFF223567FF203164FF1D3A64FF132F48FF081421FF0B1C30FF0A2038FF091D35FF061328FF266076FF87EFFAFFB9FFFFFF97E0E4FF478AA7FF18415BFD000000210000040000000400000004000000000000000000000000000000000F020609EA173442FF2C596BFF274F5FFF203E4DFF140F0DFF26170FFF32231CFF422D25FF4C3329FF472E26FF3B2118FF35728BFF348CC6FF395B9DFF2E4B95FF2D4C91FF4081BFFF235882FF0D0809FF170C08FF1A252EFF2B80C2FF2A4899FF2C4592FF2E4E91FF305A9EFF3568B6FF163358FF060F1AFF0B1728FF0E2031FF0E2336FF0D2236FF0A1728FF296277FF8AF4FEFFA0FEFFFF7CDCE9FF142E3CFD0000002100000800000008000000080000000300000003000000030000000024070F14F5264C5EFF274C5CFF224454FF1B1512FF1D1008FF2B1D16FF443028FF533B30FF573F35FF523A2FFF391E15FF366870FF39D1F0FF4EB4D6FF4787BFFF347FBCFF32A3E7FF154974FF0A0000FF170801FF1D3134FF3AD0EEFF389CCDFF3F81B5FF407DB5FF346CBBFF2C6BC4FF0D2642FF050F19FF0A1626FF0A1728FF0D1F31FF0E2335FF0E2234FF0B1424FF3C8DA2FF86FAFFFF7DF6FFFF4898A4FF010003460603080006040900060409000306070003060700030606000204079D1E3F50FF274C5EFF24495CFF201F21FF2D1D13FF2F211AFF3D2A22FF553C31FF5C4638FF574337FF533C32FF391C13FF3A7984FF43D9F3FF4BCAE3FF366BC3FF4998D2FF41ADE4FF21609CFF0A0000FF170500FF26565DFF4ADEF4FF45B6DCFF2C93D1FF4795CDFF3161B9FF2973CBFF0F2D4AFF01070CFF08131FFF0B1627FF0B1929FF0E2334FF0E2335FF0E1E2EFF132232FF55C4D7FF6EF0FAFF63E7F8FF183842CA090000010D0606000D0606000001000000010000000000170B1B25EC26526CFF24516AFF1D303CFF27170EFF31231BFF372922FF4B372EFF5E4538FF624739FF584437FF503A2FFF39211AFF3D9BACFF47DCF3FF5DB9DEFF275BBCFF5AA9D8FF54B4E0FF2D73C3FF0A0810FF110000FF26747EFF4BE6FDFF35A6D4FF2C8CC8FF429EC8FF3167BAFF2A7BCDFF13375AFF010509FF0A1118FF0D1625FF121725FF0C1C2BFF0D2032FF0E2335FF0D1524FF255F77FF5CE5FAFF5CE4F9FF40A3BAFF04040C7D030006000402080000000000000000000000007F1A3D51FF27566DFF234D63FF221B19FF2F2017FF392922FF45332CFF594135FF664A3DFF5D4538FF553E33FF473128FF2F2723FF3BB7CEFF46DAEEFF4099D2FF245DBCFF49B2DEFF5DB6DFFF3380CEFF101328FF0E0100FF2D9BADFF3CD8F3FF30A1D8FF2C94CBFF4CBBD2FF3D7DC3FF2879D2FF194C7FFF020608FF0F1217FF171621FF191723FF101624FF0B1A2BFF0E2234FF0E2639FF0A1629FF3FACC7FF56DEF3FF4ECFEAFF194456EA00000017020007000000000000000000071119BD235573FF255773FF1F3C4EFF2C1C15FF392921FF4E382FFF574035FF61473DFF664A3FFF594236FF52382FFF40281FFF2B4243FF39CFE8FF42CEE6FF3896D3FF2B6FC6FF3DC1E3FF4FB7D9FF3685D4FF18264AFF12120DFF36C2DAFF37C8E9FF2D99D9FF32A5D8FF4DDAE9FF40A0D3FF2774CDFF2368AAFF040B10FF0E1117FF1C1723FF1B1722FF181723FF0B1626FF0D1F2EFF0F2538FF0C1E30FF1D5672FF49D5F0FF4BCCE7FF317F9BFF0200015603000300000001000000001B15354BF2245C83FF22577CFF1C2934FF38251DFF46322BFF553F35FF5C4538FF654A40FF674B42FF5A4438FF523B32FF3A2119FF2A5F67FF38DCF8FF47CCE7FF378ECEFF307BCBFF3DCFE9FF3BB2DAFF327FD4FF24407CFF102726FF39D6EEFF34BAE3FF2D91D6FF35BCE3FF40E2F1FF40B1DCFF2973C9FF287AC2FF06111CFF100D0FFF18151CFF1C1723FF131722FF0A1625FF0C1E26FF0E2334FF0F2335FF0E2338FF3CAFD3FF4AC2E2FF3D9CC3FF050E1A850000000500010500010206651D496AFF255D8BFF20527AFF241F20FF3F2B24FF4E382FFF564035FF554035FF5B4437FF60473CFF5B4538FF533B31FF311913FF31909DFF3BE4F9FF44BEE1FF3188D3FF2E81D0FF3AD0EBFF36BFDFFF3379CCFF2B4F96FF1C4E56FF3CDCF4FF33A5D8FF288DD5FF3ACEEAFF43E5F0FF48C5E4FF2A7DCAFF2989CFFF0A1927FF0F090AFF151316FF18151EFF14161FFF161724FF101824FF0C202AFF102436FF0D182AFF2777A2FF46B9E1FF46B0DCFF133344D6000000410000000B07111A94245C86FF26638EFF204D6EFF35251EFF49342CFF564136FF554135FF5A4338FF64483EFF5B4438FF574035FF4E372EFF27211FFF3AC3D7FF44E5F3FF38AFDDFF2A86D3FF2A7DC0FF3FC3DAFF41E0F0FF3480CAFF2F55AAFF2F92A7FF3AD4EEFF3391D1FF2B81C5FF3BBCCBFF54F7FDFF55E2F0FF348ED0FF2B8EDBFF0D273CFF100807FF131011FF111217FF19161FFF1B1620FF1A1723FF0D1926FF0D2334FF0C1C2DFF184A68FF41B0DBFF48B3DBFF1F4F66F607050B6F020409350F2537CD286892FF286898FF1F3F59FF442E22FF533A30FF564136FF594336FF64493FFF694D44FF554035FF36261FFF342118FF273537FF3CD5EAFF47E8F1FF34A8DBFF2A8EDEFF256197FF3993A1FF4DF9FEFF3792D1FF335EB9FF38BBDFFF38C2E1FF348AD2FF255F8BFF368E91FF75FFFFFF64F5FAFF349DD7FF2C8EDFFF164364FF190C06FF2B1E19FF151213FF141419FF18161DFF1C1721FF141723FF0B1E2EFF0D1F30FF123149FF3AA5D0FF44AED7FF21556FFF0206108706060B8E153347FF296896FF27659AFF1F3141FF50352AFF543A30FF574135FF634A3EFF695144FF6F5548FF48392FFF362C24FF341C16FF28545DFF41E8F8FF43DFECFF2F9BD6FF2B9DE3FF245177FF30616AFF65FFFFFF42ADDEFF335BBAFF38C2E6FF37B8DDFF358AD3FF203A54FF295D62FF7FFFFFFF70FAFDFF31AADEFF2A88D6FF205E8FFF25140BFF33241BFF211813FF181415FF19151BFF1A1721FF1A1723FF0F1724FF0E1F2EFF10273DFF3190BFFF3A9FCEFF245C7BFF0816249F05050B9F16384FFF296998FF246195FF292D34FF5D4234FF5A4338FF644C3FFF6A5145FF785A4DFF664B40FF342B23FF372A22FF2D1711FF33919FFF4DF4FEFF41D5EBFF2C95D7FF2C9DE0FF213748FF324E56FF81FFFFFF57D2EDFF3259B7FF38C0E3FF37A3D1FF347DC8FF1B2633FF233A3FFF7FFBFFFF82FFFFFF38B4E3FF2784D0FF2473B2FF251B17FF35251DFF302219FF291C16FF1D161BFF1A1721FF1B1721FF1A1621FF0F1D2BFF0C2032FF2E7FAAFF3B95C3FF2B678CFF0E21329F04050D9F183C59FF2A699DFF225E90FF343337FF674A3DFF654C40FF6A5145FF694F44FF584238FF513C32FF564037FF5B4237FF3B2F2CFF43CEDBFF5EF8FEFF43CEEBFF2998D8FF2C95D6FF23262EFF2B3743FF80EBF4FF79F5FDFF356AC1FF37B2DCFF3780BFFF305EA5FF1C1411FF263639FF75F0F6FFA2FFFFFF4FCDEDFF2584D0FF2781C8FF1C1D21FF3A271FFF372721FF302219FF2A1D17FF1B1721FF1A1620FF1C1721FF111724FF091926FF2C7198FF3A8CB6FF306A8CFF1122319F04060D9F193D5BFF2B6A9FFF215D8FFF393739FF6B5042FF705547FF765A4CFF725649FF775A4BFF856654FF7D5F52FF694A3EFF364044FF5BE8F2FF6DFDFFFF40C1E6FF2C8FD4FF2986CAFF28262AFF312932FF6BBECDFF8DFFFFFF3D78C7FF35AAD6FF365DB1FF2C457DFF221005FF2A2F2EFF6CE5EBFFAEFFFFFF6BE9F5FF298FD6FF2787D1FF19232CFF3D271EFF3C2923FF35261FFF2D221AFF241A1BFF1B1621FF1B1721FF1A1722FF0F1621FF296687FF357EA8FF2F6480FF11222F9F04050C9F163853FF296996FF215E8FFF333439FF6D5241FF75574BFF7E6053FF8F6C5AFF8D6A58FF876655FF816254FF68473CFF355860FF76FAFFFF7BFBFEFF369ED5FF2C7DCCFF266DA4FF292528FF37292EFF5A9BACFF80FFFFFF4495D3FF3492CCFF365AB3FF253A65FF241407FF2E211BFF51C8D2FF88FEFFFF6CF3FAFF2F9DD7FF2D84D4FF1C3249FF3D281CFF3D2C25FF372621FF32241CFF2A1B15FF20161BFF1A1722FF1C1722FF13131CFF275F7DFF347CA1FF25556FFF0C18249F06060B7F15344CFD286891FF246394FF2E353FFF755546FF7C5D50FF886757FF8F6C5AFF8C6B59FF8F6D5CFF7F6152FF5F3F34FF4E99A1FF90FFFFFF7BEFF9FF2F7DC3FF2E73CAFF27577FFF2D2322FF3C2A28FF497181FF6FFEFFFF4BB7E2FF326DB6FF3554B3FF242B3FFF2F1E13FF361C14FF439AA7FF58F8FFFF5FF7FBFF379BD6FF2C78D2FF1C4770FF341D11FF3E2B25FF382721FF362620FF2D1E16FF271A17FF1B1620FF1A151EFF12171DFF29627EFF2F739DFF1C4055FF07080E870100045610293CE82A6D98FF2A709CFF253D4FFF785748FF927161FF997665FF967260FF896858FF614A3FFF6E5345FF594139FF5BC3CDFF99FFFFFF69D8EFFF2D6AB6FF2E74C6FF2A4054FF2C2627FF3F3028FF464650FF62E0EAFF54DAF1FF334EA9FF34479CFF2F2623FF3A2C23FF46291FFF42777FFF4AF1FFFF5CF9FCFF3B97D1FF2E61BFFF25528DFF2C1E14FF413229FF3D2E26FF382721FF31231AFF291B16FF1E161EFF18131AFF111D25FF266388FF2D7094FF183547FC0201047D0100001D0C1C2AB22D739FFF337DAAFF285A78FF775849FF9A7666FFA27E6CFFA5806DFF715548FF523D34FF755748FF544C4BFF73DCE7FF9AFFFFFF55C6E5FF2F65B4FF2F70C1FF253844FF322E2CFF48342CFF4E3A3AFF5BB0BEFF60F3FEFF3253A9FF343678FF3A2D20FF3D2F27FF3D231AFF365B5EFF4AEBFEFF61FAFEFF3C9BCDFF2B4EADFF284B90FF251C16FF433228FF3F2E27FF33231DFF211713FF231A16FF231719FF191218FF132437FF245E8BFF27668FFF102432CE0200043707000000070509752B6D95FF388CB9FF2E79A1FF6A574FFFA87F6AFF7D5E4FFF7E6152FF694F44FF62483FFF775443FF556C73FF88F8FFFF94FFFFFF42A7D5FF3266B8FF2E6CB6FF273338FF3E3431FF4B3931FF553E38FF5C909DFF64F6FFFF3563C3FF3A326CFF3D2A1BFF33251EFF352018FF314A50FF4AE7FDFF63F5FBFF3FB2D5FF28459CFF264595FF211F20FF412F26FF352620FF251814FF1D1311FF17110FFF201515FF181010FF18364EFF245B83FF22557DFF060D188B00000108030005000100004A225979FF3F98C6FF4096C1FF445562FF785545FF735549FF76574DFF74564AFF6D5245FF7F5848FF619EA6FF8AFFFFFF76F0F9FF3782BCFF3468C0FF315B91FF362E2AFF4A3A33FF574237FF61453BFF595E63FF55D7EAFF365FC3FF3A304BFF312317FF3B2F27FF402B22FF2D353AFF41D2EFFF62F0F8FF43C9E2FF284491FF2D419AFF272736FF3D2A1FFF271A15FF291D17FF251815FF191210FF150E0EFF110D0EFF1D4868FF23587DFF183D60FF0300074C020004000100080000000008122A3CDC45A0CDFF46A8D3FF346C88FF6B493EFF7F5E53FF866453FF856354FF735548FF674A41FF57B8C7FF7FFAFFFF5CD9EDFF345CA9FF3466C4FF344A73FF47362EFF59453BFF674E42FF694E43FF604B41FF44AAC4FF3754AAFF352729FF3B2C23FF47342DFF44322AFF342825FF37B0D1FF4FE5F5FF3ECDE5FF26448AFF2E399BFF27274BFF312114FF2D2017FF2D1F17FF261A15FF191211FF150D0AFF101E2AFF20537AFF22557BFF132C43DB08000105090306000100080001000700000003963786A9FF48B5DDFF3EA6C7FF544C4CFF8D6957FF906E5DFF8A6857FF84614FFF4E484AFF55CBE1FF6EF5FCFF46C1DDFF3354A9FF3466C5FF404962FF564239FF674E43FF74574BFF74574BFF724F3EFF488FABFF34489CFF362621FF40332BFF4E3A33FF4B3830FF39231CFF3491B1FF43D8F5FF3BCBEBFF23437FFF2E3897FF252E64FF24170AFF2F2319FF2F2218FF281A15FF1C1312FF0F0805FF1A3B50FF235173FF1D486AFF060B139305000600050208000402080004020800000000221D485CF54CC6E5FF52D2ECFF40778BFF8E6A5AFFA88572FF94705FFF8A614DFF4E6A7AFF4DDEF4FF47DDEDFF2D8BC0FF3355B1FF336BC5FF524D51FF664C40FF76594DFF7F5F52FF825E51FF7B503EFF526E7FFF344889FF322114FF45362DFF564136FF513E34FF39271BFF32738BFF3DD0F3FF35BCE6FF204D8DFF293494FF29439AFF221C1FFF2F2119FF2E1F17FF261814FF180F0CFF0F1A23FF1D4969FF234F6DFF143044EE0000021E000008000000080002000700020007000100040003070EA640A8C6FF57D7F0FF4CC3E0FF64737AFFAC8C7CFFA4806DFF7A5645FF377092FF32A1D5FF43B2D9FF68A1CAFF3352A9FF2D5CB4FF5E4E4BFF765848FF866555FF8E6B59FF896553FF875D4BFF5C5152FF373C51FF3A2A1FFF513E35FF584438FF543D33FF442D21FF395C6FFF2CABE5FF2997D4FF569AC6FF3F519FFF253B9FFF222A52FF1D1109FF231613FF251613FF130E0EFF143A55FF1A4A6CFF214B69FF050E17A100000300010006000100060002040D0002040D0002040D0000000433194156FC5DDCF1FF6AEAF8FF4FB4CBFF857976FFA67F6BFF484750FF2A72ABFF59B4DDFFBEF4FCFFE8FFFFFF85C0DBFF3B64AAFF564A50FF856250FF96725FFF9A7664FF9E7967FF97725FFF4F372CFF3C2B22FF564037FF634941FF5A4842FF574439FF4B3326FF2C5069FF3FA8E8FF8FDCF3FFD3FFFFFFB8F0F8FF5695C9FF264381FF141010FF171110FF130E0EFF0F2433FF184A6CFF1C4B6DFF122C41FE0000033501000800010008000100080002060F0002060F0002060F0001040D0F010612EA3C8EA2FF79F6FFFF75EFFCFF55B0C4FF746C6EFF3F5161FF428EA0FF72C2C8FF9EC5C6FF87BDC0FF7BBFBFFF739FA8FF715F5DFF96725FFFA88572FFB48E79FFAC8874FF725548FF5E463CFF674F43FF684E43FF664A42FF614C45FF594943FF3E2A22FF306376FF62C2CEFF8BCFD5FF8BC0C6FF6DB9BFFF49ACB7FF326071FF12151EFF140E0FFF0F171FFF153E56FF1B4A69FF1A3F59FF040B13EA0000040F0100070001000700010007000100070001000700010007000000000F0E283DEA226491FF5DBDCCFFB2FFFFFF8AF6FFFF4BA9BFFF787577FFA88675FF906D5FFF896759FF987361FFA17866FFA4816DFFAC8C78FFB1917EFFBE9B85FFCBA58EFF9B7664FF7A594BFF7B5E50FF765C50FF6E5448FF6B5249FF675145FF614C44FF4E3E36FF372922FF2B1E18FF25201EFF1F1712FF1B0E0CFF180907FF17100CFF19141AFF101A24FF133A53FF1F4961FF1D435EFF14324AFF132F44EA0100000F0301080003010800030108000000000000000000000000000000000F0E2638EA318DD2FF185281FF9DD7E1FFE7FFFFFF98F6FFFF4BAEC5FF767C81FFC6AA99FFBDA392FFBEA18DFFC3A994FFCAB19CFFCDB09AFFD0B39CFFD6B59EFFCCA58EFF936D5BFF8E6A58FF8B6C59FF826C58FF7D6855FF795D50FF705548FF685245FF624B42FF543F36FF4B3930FF43342CFF342921FF31231CFF2D2321FF231E1FFF141C29FF153D57FF214C65FF234D65FF0A1F33FF255C93FF163855EA0200000F0502080005020800050208000000000000000000000000000000000F0B2133EA328DD6FF70A8D3FF608D9FFFC9ECF1FFEFFFFFFFB8FFFFFF6ABCCFFF5D747CFFC0A898FFEBCDB4FFE2C8B2FFE0C7B4FFE2C8B2FFE2C7B0FFE1C4ACFFC49D88FF9A7361FF926E59FF8E6A56FF8A6A57FF816754FF796552FF7C6553FF715B4BFF664D43FF5D4A42FF57453CFF4B3A33FF45362EFF392E27FF272225FF142738FF16405CFF1F4861FF244F67FF2B474FFF466C97FF2D6BB3FF112E4BEA0200000F0402070004020700040207000000000000000000000000000000000F092338EA8FDCF9FFEEFFFFFFB6E4EDFF5792AAFFB8EEF3FFD9FFFFFFB9FDFFFF75D9E7FF488798FF8C8884FFD8B9A3FFF0D2BAFFE6CCB6FFDAC0ABFFDAC0AAFFD8B9A0FFBB927CFFAF8770FFB5917AFFB7917DFF947362FF816856FF836C57FF796351FF6D5548FF665147FF5A473FFF4D382FFF3A2E2CFF212E36FF173D5AFF184668FF174460FF234E69FF1F4558FF61C0D0FF99FFFFFF71C8F0FF193961EA0000000F0301070003010700030107000100050001000500010005000000010D0F1B24CB3B6E79E1285C6FDD2D4F64DD162534DC1C465BF780D5E5FF98FAFFFF82F0FAFF69EAF8FF46B6CEFF4B8695FF838885FFBD9E8BFFD1AE95FFCFAE95FFD2B39AFFD9B9A0FFDCBCA4FFD9B59DFFD3AC93FFC9A38CFFA6846FFF7E6151FF78574AFF6D4F40FF503B33FF393331FF2C3B46FF1E4966FF21567CFF22557AFF1F4C70FF174463FF0C1E2BFA0D1F2ADE1F5265DD1D4D5DDD2D5869E1152332CB0000040D02000800020008000200080001000800010008000100080001000800000005040100000402000004010000040001030000040D39071F2FCF3E9AB0FF61E7F8FF6BF0F8FF6CEBF5FF61E1F5FF41BAD5FF4092A7FF5F8792FF6B7372FF7D7169FFA69485FFBCA28FFFBD9A84FFB48F79FFA78370FF836859FF4F443EFF393C3DFF314958FF26556FFF246386FF287098FF296A93FF25608BFF245A80FF193E5AFF050D13B00000003600000002000000040000000402000004080203040100080001000800010008000100080001000800010008000100080001000800010006000201070004020800030107000101090004101800020B13060006108918465BF544ADC1FF6AF0FDFF65EBFAFF54D4ECFF4BCEE6FF44C9E2FF3DB4D3FF389BBAFF3B91B1FF3F87A6FF43809BFF407C97FF3D7893FF387B9BFF3A80A1FF3984A5FF3688B0FF347EA8FF2E759CFF2D7097FF2A6B92FF215377FF0E2333E20102025D0000000000000000000000000000000000000300040208000904070001000800010008000100080001000800010008000100080001000800010008000100060002010700040208000301070001010900040F180004111A00020913000000002E00020696184656F43A96ABFF48BFDAFF4CCAE6FF4ED0E7FF4BCAE3FF48C0DEFF47B6D5FF43A6CFFF4298C0FF4299C0FF439AC1FF449AC1FF4590B3FF458FB0FF3B8CB2FF367FA8FF30769AFF21536EFF122A39D004090C650000020D000000000000000000000000000000000000000000000300040208000904070001000800010008000100080001000800010008000100080001000800010008000100060002010700040208000301070001010900040F180004111A00030B150001010700000000000000001E000005550B1D2CAC1F4E62E83787A2FF43A6C3FF46ACCBFF43A9CEFF47A4CAFF4A9FC5FF49A0C6FF479DC3FF4292B5FF4187A6FF3D809EFF29627EFC163446E409161F8802050837010002040205050001030700000000000000000000000000000000000000000000000300040208000904070001000800010008000100080001000800010008000100080001000800010008000100060002010700040208000301070001010900040F180004111A00030B150001010700000000000000010001010800000104000000060B00000937060B14880B1520B3102431DA1D3741D8234252D8214351D81B353ED80F1F27DB091317C8060A0C83000000280000000A0000020002060A00020305000206060001030600000000000000000000000000000000000000000000000300040208000904070001000800010008000100080001000800FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFFFFFFFF0000FFFF0000FFFF0000FFFC00003FFF0000FFF000000FFF0000FFE0000007FF0000F000000001FF0000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000030000C000000000030000C000000000010000C000000000010000800000000000000080000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000080000000000100008000000000010000C000000000030000C000000000030000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000F0800000000F0000FFC0000007FF0000FFF000000FFF0000FFFC00003FFF0000FFFF8001FFFF0000FFFFFFFFFFFF000028000000300000006000000001002000000000000000000000000000000000000000000000000000FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF0001000800010008000100080001000800000000000103070001040B00000000000000000000000200050208000402070002010700020108000201080001000700000005010100011D040000560101039506060BB3080F19C30E1E2BD9112B3DD8133446D9122D3DD50D2030BF081622AC05060E9902000063000001250400000405132B00071934000B17280007142100030E1700030C16000208120001000400010007000100080000000800060207000301080001000800010008000100080001000800010008000100080001000800000000000103070001040B00000000000000000000000200050208000402070002010700020108000101030A00000048030508A90D1F29FA17384CFF2A5F7CFF327799FF3588B2FF3EA2CCFF41AFD7FF4DC6E4FF51CBE6FF4DC3DFFF50C1D8FF47AFC7FF317C94FF23526CFA0C2034C6000A285C04102A070B16260007142100030E1700030C16000208120001000400010007000100080000000800060207000301080001000800010008000100080001000800010008000100080001000800000000000103070001040B000000000000000000000002000502080004020800010003040000006209151ED4174156FF256D8EFF2D8CB8FF2A8EC1FF2E93C9FF3096CEFF34A3DAFF3AB3E2FF3CBBE4FF4ACAEAFF54D5F0FF52D3EFFF4CCBE9FF50D0ECFF59E2F8FF6CEEFDFF6BDFF0FF499EB6FF1D4C68E004112973040B170C030E1600030D16000208120001000400010007000100080000000800060207000301080001000800010008000100080001000800010008000100080001000800000000000103070001040B000000000000000000000002000401060002000051070F18DB1B4A64FF2980A7FF2F9BCBFF339DD1FF2D9DD1FF2495CFFF268CC4FF2782B4FF2775A1FF2A759CFF29698CFF25617FFF2A6374FF3B7383FF3F8AA1FF42A6C4FF4DC8E1FF58E2F8FF6EF4FFFF87FDFFFF7DF1FCFF4CB0C6FF174458DF00060F5C02081100020812000100040001000700010008000000080006020700030108000100080001000800010008000100080001000800010008000100080000000104000003040000050400000004000000020000000801010480132F3EFE27698AFF297BA8FF298AB6FF2D9AC9FF2D90C1FF247097FF204D6BFF162E3FFF131B27FF12101AFF100B0FFF070409FF03030BFF0E0608FF170606FF1D1010FF201F24FF273439FF366570FF50A8B3FF69DEE8FF7EFAFFFF7EF8FFFF6BEAFAFF4092A6FF081320990000070C0001020000000000000002000000020005020500030108000100080001000800010008000100060001000600010006000000030D0B141ACB1C3641E1112633DD0B161CDD040709DC060D11E31E4A5CFF2D7290FF2A7399FF2978A2FF26749EFF184F6DFF0F2A3CFF090D18FF08050BFF0D0809FF110A09FF140D0CFF120E0AFF0E0F11FF090F13FF040D14FF010B15FF030E18FF05111BFF08111CFF0D111BFF15131AFF2A3439FF4192A1FF66E4F3FF7BF6FFFF87FCFFFF65C1D1FF0F2B3DDA1C2C36A31C303CA70A1A27A7122028A8090B10A6010003150100050001000500010005000000000000000000000000000000000F10273EEA64BFE7FF72CFE0FF5DAEC2FF193743FF255568FF2D6A80FF2B6985FF2D6B8AFF1F465FFF091523FF070407FF100804FF0F0907FF180F0AFF20130DFF241510FF231511FF231412FF231512FF1F1411FF121213FF0C1013FF040C14FF030F17FF04101BFF091625FF09192CFF0A1528FF091122FF1B465BFF4DBDD4FF7CF8FFFF91FFFFFF69D7E5FF36768DFF7CC4D4FF8DDDEBFF6CCEEDFF1A4160FD000000210000000000000000000000000000000000000000000000000000000F0B2336EA399DE1FF64A4C6FF325259FF254C5CFF2A5E76FF295E76FF255569FF172833FF110908FF110804FF1E110AFF21130FFF23130DFF241510FF241410FF291A15FF2B1D16FF291915FF271613FF261613FF211411FF1C1413FF141214FF0F1015FF050F17FF05111CFF0A1627FF09192FFF091A31FF081224FF0C2134FF33879EFF75F2FBFFA5FFFFFF89E3EDFF50828FFF6FB8D6FF4CC5FCFF173F5CFD000000210000000000000000000000000000000000000000000000000000000F102736EA389EE1FF173D62FF244552FF2E5C6EFF275871FF214457FF13151BFF120906FF1B120CFF261A14FF2B1C17FF24130DFF25140EFF23140DFF24140CFF28160EFF2D1E10FF2D1D11FF281714FF261614FF281511FF21120BFF17100AFF100C0AFF060B0EFF050D14FF07121FFF081323FF0B1C31FF081B36FF09192EFF071425FF236076FF8AECF4FFCCFFFFFF9AE5EAFF2A5D7BFF3BA8DDFF1C4C68FD000000210000000000000000000000000000000000000000000000000000000F0F2634EA256487FF1F4351FF2E5B6CFF28576CFF1D4053FF1A1415FF20140FFF211712FF32221BFF39251DFF342C29FF2A426DFF293A6FFF243B6EFF263B70FF2A3967FF2C3352FF313747FF1C1312FF1C110BFF25232FFF242F60FF253469FF23396EFF223567FF203164FF1D3A64FF132F48FF081421FF0B1C30FF0A2038FF091D35FF061328FF266076FF87EFFAFFB9FFFFFF97E0E4FF478AA7FF18415BFD000000210000040000000400000004000000000000000000000000000000000F020609EA173442FF2C596BFF274F5FFF203E4DFF140F0DFF26170FFF32231CFF422D25FF4C3329FF472E26FF3B2118FF35728BFF348CC6FF395B9DFF2E4B95FF2D4C91FF4081BFFF235882FF0D0809FF170C08FF1A252EFF2B80C2FF2A4899FF2C4592FF2E4E91FF305A9EFF3568B6FF163358FF060F1AFF0B1728FF0E2031FF0E2336FF0D2236FF0A1728FF296277FF8AF4FEFFA0FEFFFF7CDCE9FF142E3CFD0000002100000800000008000000080000000300000003000000030000000024070F14F5264C5EFF274C5CFF224454FF1B1512FF1D1008FF2B1D16FF443028FF533B30FF573F35FF523A2FFF391E15FF366870FF39D1F0FF4EB4D6FF4787BFFF347FBCFF32A3E7FF154974FF0A0000FF170801FF1D3134FF3AD0EEFF389CCDFF3F81B5FF407DB5FF346CBBFF2C6BC4FF0D2642FF050F19FF0A1626FF0A1728FF0D1F31FF0E2335FF0E2234FF0B1424FF3C8DA2FF86FAFFFF7DF6FFFF4898A4FF010003460603080006040900060409000306070003060700030606000204079D1E3F50FF274C5EFF24495CFF201F21FF2D1D13FF2F211AFF3D2A22FF553C31FF5C4638FF574337FF533C32FF391C13FF3A7984FF43D9F3FF4BCAE3FF366BC3FF4998D2FF41ADE4FF21609CFF0A0000FF170500FF26565DFF4ADEF4FF45B6DCFF2C93D1FF4795CDFF3161B9FF2973CBFF0F2D4AFF01070CFF08131FFF0B1627FF0B1929FF0E2334FF0E2335FF0E1E2EFF132232FF55C4D7FF6EF0FAFF63E7F8FF183842CA090000010D0606000D0606000001000000010000000000170B1B25EC26526CFF24516AFF1D303CFF27170EFF31231BFF372922FF4B372EFF5E4538FF624739FF584437FF503A2FFF39211AFF3D9BACFF47DCF3FF5DB9DEFF275BBCFF5AA9D8FF54B4E0FF2D73C3FF0A0810FF110000FF26747EFF4BE6FDFF35A6D4FF2C8CC8FF429EC8FF3167BAFF2A7BCDFF13375AFF010509FF0A1118FF0D1625FF121725FF0C1C2BFF0D2032FF0E2335FF0D1524FF255F77FF5CE5FAFF5CE4F9FF40A3BAFF04040C7D030006000402080000000000000000000000007F1A3D51FF27566DFF234D63FF221B19FF2F2017FF392922FF45332CFF594135FF664A3DFF5D4538FF553E33FF473128FF2F2723FF3BB7CEFF46DAEEFF4099D2FF245DBCFF49B2DEFF5DB6DFFF3380CEFF101328FF0E0100FF2D9BADFF3CD8F3FF30A1D8FF2C94CBFF4CBBD2FF3D7DC3FF2879D2FF194C7FFF020608FF0F1217FF171621FF191723FF101624FF0B1A2BFF0E2234FF0E2639FF0A1629FF3FACC7FF56DEF3FF4ECFEAFF194456EA00000017020007000000000000000000071119BD235573FF255773FF1F3C4EFF2C1C15FF392921FF4E382FFF574035FF61473DFF664A3FFF594236FF52382FFF40281FFF2B4243FF39CFE8FF42CEE6FF3896D3FF2B6FC6FF3DC1E3FF4FB7D9FF3685D4FF18264AFF12120DFF36C2DAFF37C8E9FF2D99D9FF32A5D8FF4DDAE9FF40A0D3FF2774CDFF2368AAFF040B10FF0E1117FF1C1723FF1B1722FF181723FF0B1626FF0D1F2EFF0F2538FF0C1E30FF1D5672FF49D5F0FF4BCCE7FF317F9BFF0200015603000300000001000000001B15354BF2245C83FF22577CFF1C2934FF38251DFF46322BFF553F35FF5C4538FF654A40FF674B42FF5A4438FF523B32FF3A2119FF2A5F67FF38DCF8FF47CCE7FF378ECEFF307BCBFF3DCFE9FF3BB2DAFF327FD4FF24407CFF102726FF39D6EEFF34BAE3FF2D91D6FF35BCE3FF40E2F1FF40B1DCFF2973C9FF287AC2FF06111CFF100D0FFF18151CFF1C1723FF131722FF0A1625FF0C1E26FF0E2334FF0F2335FF0E2338FF3CAFD3FF4AC2E2FF3D9CC3FF050E1A850000000500010500010206651D496AFF255D8BFF20527AFF241F20FF3F2B24FF4E382FFF564035FF554035FF5B4437FF60473CFF5B4538FF533B31FF311913FF31909DFF3BE4F9FF44BEE1FF3188D3FF2E81D0FF3AD0EBFF36BFDFFF3379CCFF2B4F96FF1C4E56FF3CDCF4FF33A5D8FF288DD5FF3ACEEAFF43E5F0FF48C5E4FF2A7DCAFF2989CFFF0A1927FF0F090AFF151316FF18151EFF14161FFF161724FF101824FF0C202AFF102436FF0D182AFF2777A2FF46B9E1FF46B0DCFF133344D6000000410000000B07111A94245C86FF26638EFF204D6EFF35251EFF49342CFF564136FF554135FF5A4338FF64483EFF5B4438FF574035FF4E372EFF27211FFF3AC3D7FF44E5F3FF38AFDDFF2A86D3FF2A7DC0FF3FC3DAFF41E0F0FF3480CAFF2F55AAFF2F92A7FF3AD4EEFF3391D1FF2B81C5FF3BBCCBFF54F7FDFF55E2F0FF348ED0FF2B8EDBFF0D273CFF100807FF131011FF111217FF19161FFF1B1620FF1A1723FF0D1926FF0D2334FF0C1C2DFF184A68FF41B0DBFF48B3DBFF1F4F66F607050B6F020409350F2537CD286892FF286898FF1F3F59FF442E22FF533A30FF564136FF594336FF64493FFF694D44FF554035FF36261FFF342118FF273537FF3CD5EAFF47E8F1FF34A8DBFF2A8EDEFF256197FF3993A1FF4DF9FEFF3792D1FF335EB9FF38BBDFFF38C2E1FF348AD2FF255F8BFF368E91FF75FFFFFF64F5FAFF349DD7FF2C8EDFFF164364FF190C06FF2B1E19FF151213FF141419FF18161DFF1C1721FF141723FF0B1E2EFF0D1F30FF123149FF3AA5D0FF44AED7FF21556FFF0206108706060B8E153347FF296896FF27659AFF1F3141FF50352AFF543A30FF574135FF634A3EFF695144FF6F5548FF48392FFF362C24FF341C16FF28545DFF41E8F8FF43DFECFF2F9BD6FF2B9DE3FF245177FF30616AFF65FFFFFF42ADDEFF335BBAFF38C2E6FF37B8DDFF358AD3FF203A54FF295D62FF7FFFFFFF70FAFDFF31AADEFF2A88D6FF205E8FFF25140BFF33241BFF211813FF181415FF19151BFF1A1721FF1A1723FF0F1724FF0E1F2EFF10273DFF3190BFFF3A9FCEFF245C7BFF0816249F05050B9F16384FFF296998FF246195FF292D34FF5D4234FF5A4338FF644C3FFF6A5145FF785A4DFF664B40FF342B23FF372A22FF2D1711FF33919FFF4DF4FEFF41D5EBFF2C95D7FF2C9DE0FF213748FF324E56FF81FFFFFF57D2EDFF3259B7FF38C0E3FF37A3D1FF347DC8FF1B2633FF233A3FFF7FFBFFFF82FFFFFF38B4E3FF2784D0FF2473B2FF251B17FF35251DFF302219FF291C16FF1D161BFF1A1721FF1B1721FF1A1621FF0F1D2BFF0C2032FF2E7FAAFF3B95C3FF2B678CFF0E21329F04050D9F183C59FF2A699DFF225E90FF343337FF674A3DFF654C40FF6A5145FF694F44FF584238FF513C32FF564037FF5B4237FF3B2F2CFF43CEDBFF5EF8FEFF43CEEBFF2998D8FF2C95D6FF23262EFF2B3743FF80EBF4FF79F5FDFF356AC1FF37B2DCFF3780BFFF305EA5FF1C1411FF263639FF75F0F6FFA2FFFFFF4FCDEDFF2584D0FF2781C8FF1C1D21FF3A271FFF372721FF302219FF2A1D17FF1B1721FF1A1620FF1C1721FF111724FF091926FF2C7198FF3A8CB6FF306A8CFF1122319F04060D9F193D5BFF2B6A9FFF215D8FFF393739FF6B5042FF705547FF765A4CFF725649FF775A4BFF856654FF7D5F52FF694A3EFF364044FF5BE8F2FF6DFDFFFF40C1E6FF2C8FD4FF2986CAFF28262AFF312932FF6BBECDFF8DFFFFFF3D78C7FF35AAD6FF365DB1FF2C457DFF221005FF2A2F2EFF6CE5EBFFAEFFFFFF6BE9F5FF298FD6FF2787D1FF19232CFF3D271EFF3C2923FF35261FFF2D221AFF241A1BFF1B1621FF1B1721FF1A1722FF0F1621FF296687FF357EA8FF2F6480FF11222F9F04050C9F163853FF296996FF215E8FFF333439FF6D5241FF75574BFF7E6053FF8F6C5AFF8D6A58FF876655FF816254FF68473CFF355860FF76FAFFFF7BFBFEFF369ED5FF2C7DCCFF266DA4FF292528FF37292EFF5A9BACFF80FFFFFF4495D3FF3492CCFF365AB3FF253A65FF241407FF2E211BFF51C8D2FF88FEFFFF6CF3FAFF2F9DD7FF2D84D4FF1C3249FF3D281CFF3D2C25FF372621FF32241CFF2A1B15FF20161BFF1A1722FF1C1722FF13131CFF275F7DFF347CA1FF25556FFF0C18249F06060B7F15344CFD286891FF246394FF2E353FFF755546FF7C5D50FF886757FF8F6C5AFF8C6B59FF8F6D5CFF7F6152FF5F3F34FF4E99A1FF90FFFFFF7BEFF9FF2F7DC3FF2E73CAFF27577FFF2D2322FF3C2A28FF497181FF6FFEFFFF4BB7E2FF326DB6FF3554B3FF242B3FFF2F1E13FF361C14FF439AA7FF58F8FFFF5FF7FBFF379BD6FF2C78D2FF1C4770FF341D11FF3E2B25FF382721FF362620FF2D1E16FF271A17FF1B1620FF1A151EFF12171DFF29627EFF2F739DFF1C4055FF07080E870100045610293CE82A6D98FF2A709CFF253D4FFF785748FF927161FF997665FF967260FF896858FF614A3FFF6E5345FF594139FF5BC3CDFF99FFFFFF69D8EFFF2D6AB6FF2E74C6FF2A4054FF2C2627FF3F3028FF464650FF62E0EAFF54DAF1FF334EA9FF34479CFF2F2623FF3A2C23FF46291FFF42777FFF4AF1FFFF5CF9FCFF3B97D1FF2E61BFFF25528DFF2C1E14FF413229FF3D2E26FF382721FF31231AFF291B16FF1E161EFF18131AFF111D25FF266388FF2D7094FF183547FC0201047D0100001D0C1C2AB22D739FFF337DAAFF285A78FF775849FF9A7666FFA27E6CFFA5806DFF715548FF523D34FF755748FF544C4BFF73DCE7FF9AFFFFFF55C6E5FF2F65B4FF2F70C1FF253844FF322E2CFF48342CFF4E3A3AFF5BB0BEFF60F3FEFF3253A9FF343678FF3A2D20FF3D2F27FF3D231AFF365B5EFF4AEBFEFF61FAFEFF3C9BCDFF2B4EADFF284B90FF251C16FF433228FF3F2E27FF33231DFF211713FF231A16FF231719FF191218FF132437FF245E8BFF27668FFF102432CE0200043707000000070509752B6D95FF388CB9FF2E79A1FF6A574FFFA87F6AFF7D5E4FFF7E6152FF694F44FF62483FFF775443FF556C73FF88F8FFFF94FFFFFF42A7D5FF3266B8FF2E6CB6FF273338FF3E3431FF4B3931FF553E38FF5C909DFF64F6FFFF3563C3FF3A326CFF3D2A1BFF33251EFF352018FF314A50FF4AE7FDFF63F5FBFF3FB2D5FF28459CFF264595FF211F20FF412F26FF352620FF251814FF1D1311FF17110FFF201515FF181010FF18364EFF245B83FF22557DFF060D188B00000108030005000100004A225979FF3F98C6FF4096C1FF445562FF785545FF735549FF76574DFF74564AFF6D5245FF7F5848FF619EA6FF8AFFFFFF76F0F9FF3782BCFF3468C0FF315B91FF362E2AFF4A3A33FF574237FF61453BFF595E63FF55D7EAFF365FC3FF3A304BFF312317FF3B2F27FF402B22FF2D353AFF41D2EFFF62F0F8FF43C9E2FF284491FF2D419AFF272736FF3D2A1FFF271A15FF291D17FF251815FF191210FF150E0EFF110D0EFF1D4868FF23587DFF183D60FF0300074C020004000100080000000008122A3CDC45A0CDFF46A8D3FF346C88FF6B493EFF7F5E53FF866453FF856354FF735548FF674A41FF57B8C7FF7FFAFFFF5CD9EDFF345CA9FF3466C4FF344A73FF47362EFF59453BFF674E42FF694E43FF604B41FF44AAC4FF3754AAFF352729FF3B2C23FF47342DFF44322AFF342825FF37B0D1FF4FE5F5FF3ECDE5FF26448AFF2E399BFF27274BFF312114FF2D2017FF2D1F17FF261A15FF191211FF150D0AFF101E2AFF20537AFF22557BFF132C43DB08000105090306000100080001000700000003963786A9FF48B5DDFF3EA6C7FF544C4CFF8D6957FF906E5DFF8A6857FF84614FFF4E484AFF55CBE1FF6EF5FCFF46C1DDFF3354A9FF3466C5FF404962FF564239FF674E43FF74574BFF74574BFF724F3EFF488FABFF34489CFF362621FF40332BFF4E3A33FF4B3830FF39231CFF3491B1FF43D8F5FF3BCBEBFF23437FFF2E3897FF252E64FF24170AFF2F2319FF2F2218FF281A15FF1C1312FF0F0805FF1A3B50FF235173FF1D486AFF060B139305000600050208000402080004020800000000221D485CF54CC6E5FF52D2ECFF40778BFF8E6A5AFFA88572FF94705FFF8A614DFF4E6A7AFF4DDEF4FF47DDEDFF2D8BC0FF3355B1FF336BC5FF524D51FF664C40FF76594DFF7F5F52FF825E51FF7B503EFF526E7FFF344889FF322114FF45362DFF564136FF513E34FF39271BFF32738BFF3DD0F3FF35BCE6FF204D8DFF293494FF29439AFF221C1FFF2F2119FF2E1F17FF261814FF180F0CFF0F1A23FF1D4969FF234F6DFF143044EE0000021E000008000000080002000700020007000100040003070EA640A8C6FF57D7F0FF4CC3E0FF64737AFFAC8C7CFFA4806DFF7A5645FF377092FF32A1D5FF43B2D9FF68A1CAFF3352A9FF2D5CB4FF5E4E4BFF765848FF866555FF8E6B59FF896553FF875D4BFF5C5152FF373C51FF3A2A1FFF513E35FF584438FF543D33FF442D21FF395C6FFF2CABE5FF2997D4FF569AC6FF3F519FFF253B9FFF222A52FF1D1109FF231613FF251613FF130E0EFF143A55FF1A4A6CFF214B69FF050E17A100000300010006000100060002040D0002040D0002040D0000000433194156FC5DDCF1FF6AEAF8FF4FB4CBFF857976FFA67F6BFF484750FF2A72ABFF59B4DDFFBEF4FCFFE8FFFFFF85C0DBFF3B64AAFF564A50FF856250FF96725FFF9A7664FF9E7967FF97725FFF4F372CFF3C2B22FF564037FF634941FF5A4842FF574439FF4B3326FF2C5069FF3FA8E8FF8FDCF3FFD3FFFFFFB8F0F8FF5695C9FF264381FF141010FF171110FF130E0EFF0F2433FF184A6CFF1C4B6DFF122C41FE0000033501000800010008000100080002060F0002060F0002060F0001040D0F010612EA3C8EA2FF79F6FFFF75EFFCFF55B0C4FF746C6EFF3F5161FF428EA0FF72C2C8FF9EC5C6FF87BDC0FF7BBFBFFF739FA8FF715F5DFF96725FFFA88572FFB48E79FFAC8874FF725548FF5E463CFF674F43FF684E43FF664A42FF614C45FF594943FF3E2A22FF306376FF62C2CEFF8BCFD5FF8BC0C6FF6DB9BFFF49ACB7FF326071FF12151EFF140E0FFF0F171FFF153E56FF1B4A69FF1A3F59FF040B13EA0000040F0100070001000700010007000100070001000700010007000000000F0E283DEA226491FF5DBDCCFFB2FFFFFF8AF6FFFF4BA9BFFF787577FFA88675FF906D5FFF896759FF987361FFA17866FFA4816DFFAC8C78FFB1917EFFBE9B85FFCBA58EFF9B7664FF7A594BFF7B5E50FF765C50FF6E5448FF6B5249FF675145FF614C44FF4E3E36FF372922FF2B1E18FF25201EFF1F1712FF1B0E0CFF180907FF17100CFF19141AFF101A24FF133A53FF1F4961FF1D435EFF14324AFF132F44EA0100000F0301080003010800030108000000000000000000000000000000000F0E2638EA318DD2FF185281FF9DD7E1FFE7FFFFFF98F6FFFF4BAEC5FF767C81FFC6AA99FFBDA392FFBEA18DFFC3A994FFCAB19CFFCDB09AFFD0B39CFFD6B59EFFCCA58EFF936D5BFF8E6A58FF8B6C59FF826C58FF7D6855FF795D50FF705548FF685245FF624B42FF543F36FF4B3930FF43342CFF342921FF31231CFF2D2321FF231E1FFF141C29FF153D57FF214C65FF234D65FF0A1F33FF255C93FF163855EA0200000F0502080005020800050208000000000000000000000000000000000F0B2133EA328DD6FF70A8D3FF608D9FFFC9ECF1FFEFFFFFFFB8FFFFFF6ABCCFFF5D747CFFC0A898FFEBCDB4FFE2C8B2FFE0C7B4FFE2C8B2FFE2C7B0FFE1C4ACFFC49D88FF9A7361FF926E59FF8E6A56FF8A6A57FF816754FF796552FF7C6553FF715B4BFF664D43FF5D4A42FF57453CFF4B3A33FF45362EFF392E27FF272225FF142738FF16405CFF1F4861FF244F67FF2B474FFF466C97FF2D6BB3FF112E4BEA0200000F0402070004020700040207000000000000000000000000000000000F092338EA8FDCF9FFEEFFFFFFB6E4EDFF5792AAFFB8EEF3FFD9FFFFFFB9FDFFFF75D9E7FF488798FF8C8884FFD8B9A3FFF0D2BAFFE6CCB6FFDAC0ABFFDAC0AAFFD8B9A0FFBB927CFFAF8770FFB5917AFFB7917DFF947362FF816856FF836C57FF796351FF6D5548FF665147FF5A473FFF4D382FFF3A2E2CFF212E36FF173D5AFF184668FF174460FF234E69FF1F4558FF61C0D0FF99FFFFFF71C8F0FF193961EA0000000F0301070003010700030107000100050001000500010005000000010D0F1B24CB3B6E79E1285C6FDD2D4F64DD162534DC1C465BF780D5E5FF98FAFFFF82F0FAFF69EAF8FF46B6CEFF4B8695FF838885FFBD9E8BFFD1AE95FFCFAE95FFD2B39AFFD9B9A0FFDCBCA4FFD9B59DFFD3AC93FFC9A38CFFA6846FFF7E6151FF78574AFF6D4F40FF503B33FF393331FF2C3B46FF1E4966FF21567CFF22557AFF1F4C70FF174463FF0C1E2BFA0D1F2ADE1F5265DD1D4D5DDD2D5869E1152332CB0000040D02000800020008000200080001000800010008000100080001000800000005040100000402000004010000040001030000040D39071F2FCF3E9AB0FF61E7F8FF6BF0F8FF6CEBF5FF61E1F5FF41BAD5FF4092A7FF5F8792FF6B7372FF7D7169FFA69485FFBCA28FFFBD9A84FFB48F79FFA78370FF836859FF4F443EFF393C3DFF314958FF26556FFF246386FF287098FF296A93FF25608BFF245A80FF193E5AFF050D13B00000003600000002000000040000000402000004080203040100080001000800010008000100080001000800010008000100080001000800010006000201070004020800030107000101090004101800020B13060006108918465BF544ADC1FF6AF0FDFF65EBFAFF54D4ECFF4BCEE6FF44C9E2FF3DB4D3FF389BBAFF3B91B1FF3F87A6FF43809BFF407C97FF3D7893FF387B9BFF3A80A1FF3984A5FF3688B0FF347EA8FF2E759CFF2D7097FF2A6B92FF215377FF0E2333E20102025D0000000000000000000000000000000000000300040208000904070001000800010008000100080001000800010008000100080001000800010008000100060002010700040208000301070001010900040F180004111A00020913000000002E00020696184656F43A96ABFF48BFDAFF4CCAE6FF4ED0E7FF4BCAE3FF48C0DEFF47B6D5FF43A6CFFF4298C0FF4299C0FF439AC1FF449AC1FF4590B3FF458FB0FF3B8CB2FF367FA8FF30769AFF21536EFF122A39D004090C650000020D000000000000000000000000000000000000000000000300040208000904070001000800010008000100080001000800010008000100080001000800010008000100060002010700040208000301070001010900040F180004111A00030B150001010700000000000000001E000005550B1D2CAC1F4E62E83787A2FF43A6C3FF46ACCBFF43A9CEFF47A4CAFF4A9FC5FF49A0C6FF479DC3FF4292B5FF4187A6FF3D809EFF29627EFC163446E409161F8802050837010002040205050001030700000000000000000000000000000000000000000000000300040208000904070001000800010008000100080001000800010008000100080001000800010008000100060002010700040208000301070001010900040F180004111A00030B150001010700000000000000010001010800000104000000060B00000937060B14880B1520B3102431DA1D3741D8234252D8214351D81B353ED80F1F27DB091317C8060A0C83000000280000000A0000020002060A00020305000206060001030600000000000000000000000000000000000000000000000300040208000904070001000800010008000100080001000800FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFF00FFFFFFFFFFFF0000FFFF0000FFFF0000FFFC00003FFF0000FFF000000FFF0000FFE0000007FF0000F000000001FF0000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000030000C000000000030000C000000000010000C000000000010000800000000000000080000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000080000000000100008000000000010000C000000000030000C000000000030000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000E000000000070000F0800000000F0000FFC0000007FF0000FFF000000FFF0000FFFC00003FFF0000FFFF8001FFFF0000FFFFFFFFFFFF000028000000200000004000000001002000000000000000000000000000000000000000000000000000010008000100080001000600010206000102080000000000010004000502080002010700030108000000030000000015020000440504096D09121C8E0F23339F122D3B9F0F202C8A070F1A690300064B0000001C010617000918300008152200030F170002091200010006000100080002010800040208000100080001000800010008000100080001000600010206000102080000000000010004000502080002000600010000020000004508121AA6142E3EDC214B63F72B6D8EFF368EB0FF41A5BEFF3D9AB3FF358298F6286072E2163244B003102851030D250407131F00030F170002091200010006000100080002010800040208000100080001000800010008000100080001000600010206000102080000000000010004000400030302020760112F3FCF236A8AFF2D90BDFF2B98D0FF309BD6FF33A1D6FF39A9D5FF43B4D3FF4EBFD8FF4EC8E6FF57E5FFFF68F0FFFF65CDDFFF35738AD7081A2C6200040C0702091200010006000100080002010800040208000100080001000800010008000100080001000601000000030000000300000003000000190B1720B7215A77FF2C8CBAFF30A0D3FF2A86B5FF1F6288FF1A425CFF142434FF0F1B28FF0D1521FF1B191CFF263037FF326574FF469BAAFF70E4EDFF85FFFFFF5FD0E1FF214D5DC50000061F0000000000000000000000000402080001000800010008000100040001000300020207482A5060E232606BE2172D34E2132D38F02C6C89FF2D79A0FF205F83FF113347FF0B1119FF0D0707FF160906FF180C09FF140D0CFF0C0D0FFF040B12FF020B13FF060A13FF0C101BFF1D2932FF3C8392FF6EECFAFF88FFFFFF3C7D8DEF274551C83A606BC8294B59C80304095901000400010004000000000000000000000102533F93C9FF66AFC9FF2D5663FF2A6179FF285D73FF1B303DFF0F0909FF180903FF1F0F08FF22120AFF281710FF2A1B14FF281713FF241512FF1A1311FF0F0F12FF050D15FF05121EFF071529FF050E24FF14394DFF51B9CAFF99FFFFFF70BBC9FF73BED5FF50B7E5FF02070D7500000000000000000000000000000000020405512975A8FF1E425DFF2C5768FF254F65FF171C21FF150A05FF281A12FF2B1F1FFF261A23FF231D23FF261C21FF2D1F1BFF281A15FF261613FF251619FF19161EFF0F1421FF0A1626FF0B1A2BFF091B31FF06152CFF071C31FF5EADBBFFBDFFFFFF5E9DB1FF3286B3FF040C1271000000000000000000000000000000000102034C173646FF2B5666FF23495BFF18191AFF2B1A13FF3D2A22FF462B21FF383B40FF3278AFFF315396FF2D4B8EFF346599FF151C23FF180C06FF24507EFF2B4B97FF2D4889FF2F569AFF1E416DFF08121EFF0C1E32FF0B1E33FF081E33FF60B1C0FFACFFFFFF5BA4B5FF00020A6C0000050000000700010204000102030002040777203F4DFF274D5FFF1F2122FF24140CFF453027FF584035FF543A2FFF39352FFF3BC5DDFF4AADD6FF3C88C8FF2E92D1FF0C1018FF150400FF329DB1FF3FAAD9FF4283BDFF336FC6FF163A67FF050D15FF0A1627FF0D2031FF0C1E30FF122A3CFF6CD9E6FF79F4FAFF19353F990400000008040900020302000102010C122733E627546DFF202D35FF2C1C12FF3B2B24FF5A4135FF60483AFF52382CFF3B4545FF46D7ECFF47A1D7FF488BCEFF4AA8E1FF0F1930FF15120CFF42C6D8FF37A7D9FF3D95C9FF3472C7FF194B7EFF03070BFF0C1523FF0F1928FF0D2132FF0C1727FF265B6FFF63F0FDFF42A4B8FB06040934060304000000000001030554204A61FF244B60FF271C15FF3B2A21FF503B32FF65493EFF5B4336FF492C21FF30595EFF45D9F1FF3887CDFF3D99D4FF51B1E4FF182C55FF162927FF39CEEBFF2E9CD6FF46BBD7FF3B8DD1FF1D5D9FFF070B0FFF18161FFF191723FF0D1828FF0E2335FF0A182BFF3AA1BBFF52DBF5FF143443B001000000000001000918229D255D82FF1F394BFF36231BFF4F3A30FF5F463BFF664B41FF594236FF42241BFF2E7E8AFF40D4F2FF3486CEFF39ADDDFF3EADE0FF22407BFF1C4E51FF38CDF2FF2E9DDBFF41D8ECFF3A9FD8FF236BB5FF091016FF18141AFF1B1723FF0E1724FF0C202DFF0D1E30FF1D546EFF4CD2F3FF276681E60000011B0001041915364FE424618FFF262C35FF473026FF553F35FF594337FF5F473BFF5C4437FF3B2721FF35B4C3FF40CAECFF2E81D0FF37B6E0FF39B6E2FF2B4F99FF298490FF36B5E7FF2E9BD4FF46EAF1FF44BDE3FF2881CCFF0E1B28FF120D0EFF16141CFF181622FF111A25FF0D202FFF102940FF3EA9D3FF388DB0FF080B125904090F441E4F71FE24608CFF392F2DFF543B30FF574336FF644A40FF5C443AFF3E2A21FF2D302FFF3FD7E6FF3AB9E3FF287ECBFF3694ADFF43D2ECFF315FB8FF37B8D6FF35A4DDFF296B91FF62EEEEFF56DDF1FF2A8DDBFF162F44FF20120CFF151316FF19161DFF191621FF0D1E2DFF0C1E31FF338CB3FF3D9DC3FF0C19258409101992245D84FF245984FF48352DFF583F33FF624A3EFF72574AFF4C3C33FF311E16FF2F5054FF44EBF8FF34AEE0FF2884C2FF315C69FF5FEDFBFF3671C4FF39C0E5FF3596D3FF1D3950FF6EDCDEFF67EFFBFF2892DCFF204362FF311D10FF231A15FF1A151AFF1B1721FF141724FF0C1929FF276E94FF3895C2FF11283AA00A1421A1266291FF265379FF574033FF664D40FF695044FF61483EFF503D33FF482B22FF39848BFF54F6FFFF30A8E2FF2779AFFF2C343BFF7EF3F8FF438CD0FF36A4D6FF3269ACFF1B191CFF68C7CCFF8BFEFFFF2E9EE0FF205784FF321D13FF36261EFF291C18FF1B1720FF1C1620FF0E131FFF205473FF3B8EB9FF142D409F0B1421A2276394FF265277FF5F473AFF74584AFF795B4EFF7F5F50FF826355FF5A3D35FF53B7BEFF63F1FEFF2D96DAFF276594FF2E2327FF77D7DDFF56AEE1FF348BCBFF2D4687FF210E06FF59ACB0FF9CFFFFFF3EB3E7FF20649FFF332118FF3D2A23FF31241CFF22191CFF1A1722FF16111BFF1F4761FF367FA6FF132939A10A111C8C235D85FF25567CFF634A3FFF806052FF8E6C5AFF8F6C5BFF836151FF564A45FF73E3E8FF68D6EFFF2974C9FF275072FF35201FFF5CA6AFFF58CAF1FF3365BDFF2A3765FF2E1204FF418389FF65FFFFFF44B9E5FF2465B2FF2E2522FF3F2C24FF362620FF2B1C16FF1E171FFF171118FF214960FF2E7095FF0D19248F04060F5423597DFF27678FFF645049FF9B7765FFA17C6AFF75594BFF66483BFF5A6765FF89FEFFFF56B5DCFF2A69BAFF273848FF3A2620FF52767DFF5BE3F9FF344EAEFF322F49FF3F2517FF41686AFF50FBFFFF48B9E1FF2A58B2FF29292FFF422F25FF3A2923FF2C1F17FF23171AFF161219FF205273FF276081FF080D147405010227204E6CF03287B6FF5D5D5FFF9D7460FF886858FF654C42FF6C4A3CFF62888DFF90FFFFFF439BD2FF2D62ADFF2A3237FF47342BFF555455FF60E3F0FF3760B3FF3A2B33FF372317FF33464AFF52EEFEFF4CC5E1FF284AA6FF252A3FFF3E2C21FF2E201AFF1C1310FF1F1513FF17171CFF21557BFF1B4463F70202083102000003122C3FBC42A2D1FF436D82FF745041FF78594DFF75574AFF725246FF6DC0C9FF78F4FCFF3677C0FF325896FF3E322DFF594339FF62483FFF51AFC3FF385CA6FF36241EFF402E25FF322E2EFF46CDE3FF4AD2E6FF2A4499FF292B54FF352417FF291C16FF211714FF150D0AFF15212CFF235A81FF12263CBB0501010400000400050812693F9CC3FF3F9CBCFF6A514AFF8E6A58FF896452FF605450FF60DBEAFF5AD6EBFF325DB8FF384F7DFF553F35FF6C5247FF734F3EFF4F7C91FF324781FF3C2A1FFF4D3931FF3A2720FF3AA5BEFF3FD3EFFF274591FF272C6AFF281B0EFF2F2219FF231814FF130A07FF1A3A50FF215176FF090E1765060203000502070002000011266076EC51D7F5FF4F7D8DFFA37C6BFF9A6E5AFF576B74FF40CFECFF389FCBFF2D56B8FF4E536CFF6F5141FF816153FF845A49FF606670FF323D61FF422F22FF574237FF422D21FF3687A2FF30BCEBFF28529CFF263898FF25202AFF2C1D13FF23140FFF121C24FF1F4D6EFF173349E70000030E0000070001020B000102060006101C8551C3D9FF5DDBF0FF7D888AFF916959FF2D648EFF5CB9E4FFBAECF9FF5C91CAFF4E4D64FF86614DFF977360FF9C7562FF634A41FF3C312EFF5B443BFF5A463EFF4C3325FF316F94FF62C8F6FFADEAFAFF5C91CCFF20335FFF180E07FF151113FF153E5AFF1B4A6BFF070E1988000004000100080002040D0002040C000001094C2C6B83FF7FF7FEFF70D5E3FF5B6C75FF5F7D84FF86A4A1FF99A9A3FF87A6A1FF7F726CFFA07B68FFB9947FFF9A7766FF664B3FFF695044FF684D44FF624D46FF47352DFF325761FF649294FF6A8C8CFF447F82FF233A46FF120D11FF122B3CFF1D4B6AFF153348FF02030A4D010007000100070000000200000001000204085120679EFF4489ACFFCCFFFFFF7BD5E3FF7A8487FFB8907DFFB8947FFFC09D87FFC9AA93FFCDAF99FFCDA891FF926D5BFF876856FF7E6855FF765E4FFF6D5447FF604B42FF493227FF37251CFF291810FF26120DFF1C1415FF142D40FF204D67FF122E47FF1D4A75FF090E18510402050005020800000000000000000000010153458DC1FF92C0DFFFA2CED9FFE6FFFFFF8BD7E3FF739298FFC6AD9CFFECCBB4FFE8CDB6FFE4C9B2FFD1AF98FF9F7763FF97735EFF91715EFF7D6653FF7C6553FF6C5448FF614C43FF523E34FF3F3028FF25282EFF15334AFF1E4B67FF2B5768FF5D97B0FF3B7BB5FF0407115302010500030107000100040000000300020105484A7382E271929CE2385464E25D93A2FFA9FFFFFF76EDFAFF53AEBFFF839A9AFFBFA897FFCEAC95FFD5B298FFD8B297FFD9B197FFD2A78EFFA8836DFF7D5E4CFF6C4E3FFF524139FF3A3B3EFF24445BFF1F5175FF1D4E71FF132F43FF1D4452E3478C96E23B6A7FE205051048020106000301070001000800010008000100070100000003000000030000000300040F3A1F5566E255D0E2FF6FFBFFFF57DBF2FF43ACC4FF5498A6FF64848BFF7A8585FF867F79FF7B726DFF666665FF445861FF345E73FF2A6585FF286E97FF296D99FF23557AFF0E2232C800000035000000030000000300000003040107010100080001000800010008000100080001000700020106000301080002020A000410180000010A1605111B852C6E7BE34BBACFFF4CCEE8FF4CD7F0FF44C4E4FF3DAAD1FF3991BAFF3990B7FF3D95BDFF4496BBFF3E94BCFF3580AAFF286485FF17384DCD050C12640000000700000000000000000000010006030700040108000100080001000800010008000100080001000700020106000301080002020A0004101900030C1500000000000000000C01040C4C14324293276176D3337D95F63885A3FF3F86A6FF3E87A6FF367793FF30647AFB1F4658CC0E212D8B04080C3800000000000103000000000000000000000000000000010006030700040108000100080001000800010008000100080001000700020106000301080002020A0004101900030C15000100050000000000000000000000050A02040F3909111B6A0F20289F172C359F162C369F0E1D249F0810147901010232000000060000000002030400010306000000000000000000000000000000010006030700040108000100080001000800FFE007FFFF8001FFFE00007FC000003FC0000003C0000003C0000003C0000003C00000038000000180000001800000000000000000000000000000000000000000000000000000000000000000000000000000008000000180000001C0000003C0000003C0000003C0000003C0000003C0000003FE00007FFF8003FFFFE007FF28000000200000004000000001002000000000000000000000000000000000000000000000000000010008000100080001000600010206000102080000000000010004000502080002010700030108000000030000000015020000440504096D09121C8E0F23339F122D3B9F0F202C8A070F1A690300064B0000001C010617000918300008152200030F170002091200010006000100080002010800040208000100080001000800010008000100080001000600010206000102080000000000010004000502080002000600010000020000004508121AA6142E3EDC214B63F72B6D8EFF368EB0FF41A5BEFF3D9AB3FF358298F6286072E2163244B003102851030D250407131F00030F170002091200010006000100080002010800040208000100080001000800010008000100080001000600010206000102080000000000010004000400030302020760112F3FCF236A8AFF2D90BDFF2B98D0FF309BD6FF33A1D6FF39A9D5FF43B4D3FF4EBFD8FF4EC8E6FF57E5FFFF68F0FFFF65CDDFFF35738AD7081A2C6200040C0702091200010006000100080002010800040208000100080001000800010008000100080001000601000000030000000300000003000000190B1720B7215A77FF2C8CBAFF30A0D3FF2A86B5FF1F6288FF1A425CFF142434FF0F1B28FF0D1521FF1B191CFF263037FF326574FF469BAAFF70E4EDFF85FFFFFF5FD0E1FF214D5DC50000061F0000000000000000000000000402080001000800010008000100040001000300020207482A5060E232606BE2172D34E2132D38F02C6C89FF2D79A0FF205F83FF113347FF0B1119FF0D0707FF160906FF180C09FF140D0CFF0C0D0FFF040B12FF020B13FF060A13FF0C101BFF1D2932FF3C8392FF6EECFAFF88FFFFFF3C7D8DEF274551C83A606BC8294B59C80304095901000400010004000000000000000000000102533F93C9FF66AFC9FF2D5663FF2A6179FF285D73FF1B303DFF0F0909FF180903FF1F0F08FF22120AFF281710FF2A1B14FF281713FF241512FF1A1311FF0F0F12FF050D15FF05121EFF071529FF050E24FF14394DFF51B9CAFF99FFFFFF70BBC9FF73BED5FF50B7E5FF02070D7500000000000000000000000000000000020405512975A8FF1E425DFF2C5768FF254F65FF171C21FF150A05FF281A12FF2B1F1FFF261A23FF231D23FF261C21FF2D1F1BFF281A15FF261613FF251619FF19161EFF0F1421FF0A1626FF0B1A2BFF091B31FF06152CFF071C31FF5EADBBFFBDFFFFFF5E9DB1FF3286B3FF040C1271000000000000000000000000000000000102034C173646FF2B5666FF23495BFF18191AFF2B1A13FF3D2A22FF462B21FF383B40FF3278AFFF315396FF2D4B8EFF346599FF151C23FF180C06FF24507EFF2B4B97FF2D4889FF2F569AFF1E416DFF08121EFF0C1E32FF0B1E33FF081E33FF60B1C0FFACFFFFFF5BA4B5FF00020A6C0000050000000700010204000102030002040777203F4DFF274D5FFF1F2122FF24140CFF453027FF584035FF543A2FFF39352FFF3BC5DDFF4AADD6FF3C88C8FF2E92D1FF0C1018FF150400FF329DB1FF3FAAD9FF4283BDFF336FC6FF163A67FF050D15FF0A1627FF0D2031FF0C1E30FF122A3CFF6CD9E6FF79F4FAFF19353F990400000008040900020302000102010C122733E627546DFF202D35FF2C1C12FF3B2B24FF5A4135FF60483AFF52382CFF3B4545FF46D7ECFF47A1D7FF488BCEFF4AA8E1FF0F1930FF15120CFF42C6D8FF37A7D9FF3D95C9FF3472C7FF194B7EFF03070BFF0C1523FF0F1928FF0D2132FF0C1727FF265B6FFF63F0FDFF42A4B8FB06040934060304000000000001030554204A61FF244B60FF271C15FF3B2A21FF503B32FF65493EFF5B4336FF492C21FF30595EFF45D9F1FF3887CDFF3D99D4FF51B1E4FF182C55FF162927FF39CEEBFF2E9CD6FF46BBD7FF3B8DD1FF1D5D9FFF070B0FFF18161FFF191723FF0D1828FF0E2335FF0A182BFF3AA1BBFF52DBF5FF143443B001000000000001000918229D255D82FF1F394BFF36231BFF4F3A30FF5F463BFF664B41FF594236FF42241BFF2E7E8AFF40D4F2FF3486CEFF39ADDDFF3EADE0FF22407BFF1C4E51FF38CDF2FF2E9DDBFF41D8ECFF3A9FD8FF236BB5FF091016FF18141AFF1B1723FF0E1724FF0C202DFF0D1E30FF1D546EFF4CD2F3FF276681E60000011B0001041915364FE424618FFF262C35FF473026FF553F35FF594337FF5F473BFF5C4437FF3B2721FF35B4C3FF40CAECFF2E81D0FF37B6E0FF39B6E2FF2B4F99FF298490FF36B5E7FF2E9BD4FF46EAF1FF44BDE3FF2881CCFF0E1B28FF120D0EFF16141CFF181622FF111A25FF0D202FFF102940FF3EA9D3FF388DB0FF080B125904090F441E4F71FE24608CFF392F2DFF543B30FF574336FF644A40FF5C443AFF3E2A21FF2D302FFF3FD7E6FF3AB9E3FF287ECBFF3694ADFF43D2ECFF315FB8FF37B8D6FF35A4DDFF296B91FF62EEEEFF56DDF1FF2A8DDBFF162F44FF20120CFF151316FF19161DFF191621FF0D1E2DFF0C1E31FF338CB3FF3D9DC3FF0C19258409101992245D84FF245984FF48352DFF583F33FF624A3EFF72574AFF4C3C33FF311E16FF2F5054FF44EBF8FF34AEE0FF2884C2FF315C69FF5FEDFBFF3671C4FF39C0E5FF3596D3FF1D3950FF6EDCDEFF67EFFBFF2892DCFF204362FF311D10FF231A15FF1A151AFF1B1721FF141724FF0C1929FF276E94FF3895C2FF11283AA00A1421A1266291FF265379FF574033FF664D40FF695044FF61483EFF503D33FF482B22FF39848BFF54F6FFFF30A8E2FF2779AFFF2C343BFF7EF3F8FF438CD0FF36A4D6FF3269ACFF1B191CFF68C7CCFF8BFEFFFF2E9EE0FF205784FF321D13FF36261EFF291C18FF1B1720FF1C1620FF0E131FFF205473FF3B8EB9FF142D409F0B1421A2276394FF265277FF5F473AFF74584AFF795B4EFF7F5F50FF826355FF5A3D35FF53B7BEFF63F1FEFF2D96DAFF276594FF2E2327FF77D7DDFF56AEE1FF348BCBFF2D4687FF210E06FF59ACB0FF9CFFFFFF3EB3E7FF20649FFF332118FF3D2A23FF31241CFF22191CFF1A1722FF16111BFF1F4761FF367FA6FF132939A10A111C8C235D85FF25567CFF634A3FFF806052FF8E6C5AFF8F6C5BFF836151FF564A45FF73E3E8FF68D6EFFF2974C9FF275072FF35201FFF5CA6AFFF58CAF1FF3365BDFF2A3765FF2E1204FF418389FF65FFFFFF44B9E5FF2465B2FF2E2522FF3F2C24FF362620FF2B1C16FF1E171FFF171118FF214960FF2E7095FF0D19248F04060F5423597DFF27678FFF645049FF9B7765FFA17C6AFF75594BFF66483BFF5A6765FF89FEFFFF56B5DCFF2A69BAFF273848FF3A2620FF52767DFF5BE3F9FF344EAEFF322F49FF3F2517FF41686AFF50FBFFFF48B9E1FF2A58B2FF29292FFF422F25FF3A2923FF2C1F17FF23171AFF161219FF205273FF276081FF080D147405010227204E6CF03287B6FF5D5D5FFF9D7460FF886858FF654C42FF6C4A3CFF62888DFF90FFFFFF439BD2FF2D62ADFF2A3237FF47342BFF555455FF60E3F0FF3760B3FF3A2B33FF372317FF33464AFF52EEFEFF4CC5E1FF284AA6FF252A3FFF3E2C21FF2E201AFF1C1310FF1F1513FF17171CFF21557BFF1B4463F70202083102000003122C3FBC42A2D1FF436D82FF745041FF78594DFF75574AFF725246FF6DC0C9FF78F4FCFF3677C0FF325896FF3E322DFF594339FF62483FFF51AFC3FF385CA6FF36241EFF402E25FF322E2EFF46CDE3FF4AD2E6FF2A4499FF292B54FF352417FF291C16FF211714FF150D0AFF15212CFF235A81FF12263CBB0501010400000400050812693F9CC3FF3F9CBCFF6A514AFF8E6A58FF896452FF605450FF60DBEAFF5AD6EBFF325DB8FF384F7DFF553F35FF6C5247FF734F3EFF4F7C91FF324781FF3C2A1FFF4D3931FF3A2720FF3AA5BEFF3FD3EFFF274591FF272C6AFF281B0EFF2F2219FF231814FF130A07FF1A3A50FF215176FF090E1765060203000502070002000011266076EC51D7F5FF4F7D8DFFA37C6BFF9A6E5AFF576B74FF40CFECFF389FCBFF2D56B8FF4E536CFF6F5141FF816153FF845A49FF606670FF323D61FF422F22FF574237FF422D21FF3687A2FF30BCEBFF28529CFF263898FF25202AFF2C1D13FF23140FFF121C24FF1F4D6EFF173349E70000030E0000070001020B000102060006101C8551C3D9FF5DDBF0FF7D888AFF916959FF2D648EFF5CB9E4FFBAECF9FF5C91CAFF4E4D64FF86614DFF977360FF9C7562FF634A41FF3C312EFF5B443BFF5A463EFF4C3325FF316F94FF62C8F6FFADEAFAFF5C91CCFF20335FFF180E07FF151113FF153E5AFF1B4A6BFF070E1988000004000100080002040D0002040C000001094C2C6B83FF7FF7FEFF70D5E3FF5B6C75FF5F7D84FF86A4A1FF99A9A3FF87A6A1FF7F726CFFA07B68FFB9947FFF9A7766FF664B3FFF695044FF684D44FF624D46FF47352DFF325761FF649294FF6A8C8CFF447F82FF233A46FF120D11FF122B3CFF1D4B6AFF153348FF02030A4D010007000100070000000200000001000204085120679EFF4489ACFFCCFFFFFF7BD5E3FF7A8487FFB8907DFFB8947FFFC09D87FFC9AA93FFCDAF99FFCDA891FF926D5BFF876856FF7E6855FF765E4FFF6D5447FF604B42FF493227FF37251CFF291810FF26120DFF1C1415FF142D40FF204D67FF122E47FF1D4A75FF090E18510402050005020800000000000000000000010153458DC1FF92C0DFFFA2CED9FFE6FFFFFF8BD7E3FF739298FFC6AD9CFFECCBB4FFE8CDB6FFE4C9B2FFD1AF98FF9F7763FF97735EFF91715EFF7D6653FF7C6553FF6C5448FF614C43FF523E34FF3F3028FF25282EFF15334AFF1E4B67FF2B5768FF5D97B0FF3B7BB5FF0407115302010500030107000100040000000300020105484A7382E271929CE2385464E25D93A2FFA9FFFFFF76EDFAFF53AEBFFF839A9AFFBFA897FFCEAC95FFD5B298FFD8B297FFD9B197FFD2A78EFFA8836DFF7D5E4CFF6C4E3FFF524139FF3A3B3EFF24445BFF1F5175FF1D4E71FF132F43FF1D4452E3478C96E23B6A7FE205051048020106000301070001000800010008000100070100000003000000030000000300040F3A1F5566E255D0E2FF6FFBFFFF57DBF2FF43ACC4FF5498A6FF64848BFF7A8585FF867F79FF7B726DFF666665FF445861FF345E73FF2A6585FF286E97FF296D99FF23557AFF0E2232C800000035000000030000000300000003040107010100080001000800010008000100080001000700020106000301080002020A000410180000010A1605111B852C6E7BE34BBACFFF4CCEE8FF4CD7F0FF44C4E4FF3DAAD1FF3991BAFF3990B7FF3D95BDFF4496BBFF3E94BCFF3580AAFF286485FF17384DCD050C12640000000700000000000000000000010006030700040108000100080001000800010008000100080001000700020106000301080002020A0004101900030C1500000000000000000C01040C4C14324293276176D3337D95F63885A3FF3F86A6FF3E87A6FF367793FF30647AFB1F4658CC0E212D8B04080C3800000000000103000000000000000000000000000000010006030700040108000100080001000800010008000100080001000700020106000301080002020A0004101900030C15000100050000000000000000000000050A02040F3909111B6A0F20289F172C359F162C369F0E1D249F0810147901010232000000060000000002030400010306000000000000000000000000000000010006030700040108000100080001000800FFE007FFFF8001FFFE00007FC000003FC0000003C0000003C0000003C0000003C00000038000000180000001800000000000000000000000000000000000000000000000000000000000000000000000000000008000000180000001C0000003C0000003C0000003C0000003C0000003C0000003FE00007FFF8003FFFFE007FF2800000018000000300000000100200000000000000000000000000000000000000000000000000001000800010007000101050001020500000001000502070002000700000000000000002E070A10660F1E2C8917394B9F1C48579E173846850D1B2469000007350109220008142200030E170001040B0000000700030108000201080001000800010008000100070001010500010205000000010004000400010001210A19248E194D65E727749CFF3392C2FF3DB2DEFF4ECDEBFF50CBE6FF49BDD7FF4498ACEE204B6596030E1E2500070F0001040B0000000700030108000201080001000800010008000100070100000008000000080000000C070D13741D516DF52D93C2FF2D93C5FF1F6993FF1B4967FF193D53FF1B3C4BFF2A4A54FF367485FF58C1CEFF7DF6FFFF56BAC9F414303D7C0000000400000000000000000201080001000800000003000000021225495DD53D707DE4142D36E728637CFF286A8DFF143A51FF10151BFF130805FF1A0A05FF180A07FF0E090AFF04050BFF040810FF0D111DFF224452FF56BDCBFF7DF2FAFF376D7BDB477583CF2A5062CA0100031B000003000000000000000014286994F43D7590FF2A5B6FFF204456FF151212FF1D0D06FF230F0BFF24140FFF2A1810FF2B1912FF261512FF1A0F0DFF090C11FF05101CFF051024FF04142CFF388192FFA2FCFFFF73BDD4FF2E7BA3FF00000022000000000000000000000010143243EE275468FF1E3A47FF201410FF37231AFF3C2B25FF2F5981FF2C4881FF2F4C7DFF202933FF1C1819FF26467CFF273C76FF26487FFF0F233BFF09182BFF031127FF447F90FFA0FBFFFF3C7387F90000001C0000060001030400020304311B3745FA243F4CFF231610FF412C22FF5B4336FF472D23FF3DA7B9FF459ED6FF3E98DCFF132D46FF1A2520FF3DB7DDFF3D84C3FF316CC1FF0B2036FF08121FFF0D1F31FF071526FF4D9FAEFF68DDE8FD0C141A4907020400000100000A171D9D25526BFF25211FFF3B2820FF5C4337FF5D4436FF40312AFF42BCCEFF3C8FD3FF52AEE5FF203F69FF1C4545FF3AC4ECFF3A9BCCFF337DCBFF0D2A45FF0E0E15FF121826FF0B1B2DFF133044FF55DCF3FF2C7183D5020000070000000A173C54E722485FFF37251DFF563F34FF654A40FF573A2FFF354444FF3BCAE5FF348CD1FF40B8E4FF28508AFF24737EFF32B7ECFF3CC3E4FF3697DBFF12385EFF130C0FFF191722FF0C1B29FF0A192BFF2D819EFF40ADCCFF03050E3C03090E45205882FF27394BFF4B3328FF584237FF5F463BFF513126FF32686DFF3DD3F3FF2F89D0FF3BC7E6FF2E67ADFF309FB8FF2F9CD8FF44DBE9FF41B8EAFF194D7CFF0F0704FF16141CFF161721FF0C1A27FF17415DFF44B2DEFF102533760D1D2A83246595FF38393FFF573D2FFF654C40FF5C463CFF321A13FF35929AFF3CCEF4FF266FACFF44B5BFFF3A8ED4FF38B9E4FF286A9CFF55BCBDFF53DBFCFF1F65A1FF24160FFF1A1515FF1A151EFF121724FF102A3FFF399CC8FF17394D9B0E2233A3246294FF473C3BFF664B3EFF6A5044FF543F34FF392B25FF45C9D1FF39C3F3FF21557FFF579798FF54B6E8FF359FD8FF21375DFF549391FF6FEEFFFF2177BAFF2C2320FF312118FF1F181CFF191520FF0E1D2CFF317FAAFF1D435CA10F2234A2236091FF4F4341FF795A4BFF806151FF84604FFF525351FF67EDF4FF36A4E1FF244162FF517376FF66D6F5FF3273C1FF231D35FF4A7873FF80FEFFFF298ED0FF2B2B33FF3C271EFF2B1E19FF1C151EFF151722FF2D6C8EFF1A3A4FA00C1B2B88236592FF524C4CFF936E5CFF916F5DFF755142FF5F817FFF7CF1FFFF2E77C3FF293446FF454C4CFF5AD2ECFF3254A8FF301F22FF405F5DFF56F8FFFF358CD5FF29354DFF3E2A1EFF33231BFF231719FF161924FF296789FF1125328E080C15522A76A3FF52636EFF9B725DFF7D5F51FF614135FF74AEB0FF71DFF7FF2A64AFFF2F3337FF4D3933FF5BC2D4FF38559BFF39221AFF374545FF54EFFBFF3884C7FF28305AFF3C291DFF271A16FF1E1310FF18222FFF235C85FF070F1A5E010000192C6C90F54486A6FF725043FF7B5A4CFF6F5448FF76D9DDFF54B5E0FF2F539BFF473A33FF634436FF548698FF374F80FF3C2719FF383433FF49D5E7FF3789C0FF292863FF2F2013FF261A15FF150C08FF193448FF1C4566F30502061901000000173647A947BDE0FF6E6A68FF9E705AFF6B625DFF4CD7E9FF3281C7FF3C4F89FF674B3DFF7D5747FF61646EFF313A57FF4A3527FF443028FF38ACC7FF2986C0FF222778FF2A1E1AFF2B1C14FF161213FF1F4B69FF0E2133A4010002000202080002050B3841A7BEFB62BDCDFF977566FF486377FF60C7EAFF74AFDDFF44557DFF85604CFF98725FFF6F574EFF3F3434FF594339FF4B362BFF358AB3FF76CEF2FF5E8DCAFF1E273FFF1B0C05FF152F41FF194260FC03040C360000060001020B00000001101B4B64EE7CEBF8FF6DB3BFFF607078FF959A92FF98A095FF8D837AFFAF8A76FFB08B77FF735547FF6C5245FF684F47FF503F37FF3D575AFF5A7472FF406262FF1C242BFF111F2BFF18435FFF102A3DEF01000411020008000000000000000014205987F47AB5D5FFCDFFFFFF87BDC6FFA38F84FFD8AF96FFDFC0A8FFDEC1AAFFB28C77FF8B6854FF826855FF775F4FFF6A5347FF543B30FF3D271BFF291814FF172533FF1F4B63FF325D79FF224E7AF404010214050207000000030000000212385A6CD57498A5E45A7E8CEEA6F4FCFF6CD3E1FF84A9ABFFBFAFA0FFD5B39BFFCFA88EFFCBA086FFBD9279FF8C6B56FF6E5142FF50413BFF353E47FF214765FF194768FF163445EF498A98E4305770D501000312020107000100080001000801000001080000000800000215113645964BB5C4FF5EEBFDFF4AC1D9FF56A2B2FF668F98FF7E8F94FF758184FF526975FF39677EFF2D6E92FF286F9AFF1D4C6EF508141D830000001600000008030000080200080101000800010008000100080002010700030007000209110000060F0000000236183D479D32849AE340B3CFFF40B2D5FF3E9DC7FF3E99C2FF4093B8FF3880A2FF22536EDC0F242F88010304220000000000000000000001000603070002000800010008000100080001000800020107000300070002091100040E1800000000000000000001020C260E202D62163341931F42539F1F41509F162B36990B171D5F0000021F0000000000010300000000000000000000000100060307000200080001000800FF00FF00FC003F0080000F0080000100800001008000010080000100800000000000000000000000000000000000000000000000000000000000000000000000800001008000010080000100800001008000010080000100FC003F00FF00FF002800000018000000300000000100200000000000000000000000000000000000000000000000000001000800010007000101050001020500000001000502070002000700000000000000002E070A10660F1E2C8917394B9F1C48579E173846850D1B2469000007350109220008142200030E170001040B0000000700030108000201080001000800010008000100070001010500010205000000010004000400010001210A19248E194D65E727749CFF3392C2FF3DB2DEFF4ECDEBFF50CBE6FF49BDD7FF4498ACEE204B6596030E1E2500070F0001040B0000000700030108000201080001000800010008000100070100000008000000080000000C070D13741D516DF52D93C2FF2D93C5FF1F6993FF1B4967FF193D53FF1B3C4BFF2A4A54FF367485FF58C1CEFF7DF6FFFF56BAC9F414303D7C0000000400000000000000000201080001000800000003000000021225495DD53D707DE4142D36E728637CFF286A8DFF143A51FF10151BFF130805FF1A0A05FF180A07FF0E090AFF04050BFF040810FF0D111DFF224452FF56BDCBFF7DF2FAFF376D7BDB477583CF2A5062CA0100031B000003000000000000000014286994F43D7590FF2A5B6FFF204456FF151212FF1D0D06FF230F0BFF24140FFF2A1810FF2B1912FF261512FF1A0F0DFF090C11FF05101CFF051024FF04142CFF388192FFA2FCFFFF73BDD4FF2E7BA3FF00000022000000000000000000000010143243EE275468FF1E3A47FF201410FF37231AFF3C2B25FF2F5981FF2C4881FF2F4C7DFF202933FF1C1819FF26467CFF273C76FF26487FFF0F233BFF09182BFF031127FF447F90FFA0FBFFFF3C7387F90000001C0000060001030400020304311B3745FA243F4CFF231610FF412C22FF5B4336FF472D23FF3DA7B9FF459ED6FF3E98DCFF132D46FF1A2520FF3DB7DDFF3D84C3FF316CC1FF0B2036FF08121FFF0D1F31FF071526FF4D9FAEFF68DDE8FD0C141A4907020400000100000A171D9D25526BFF25211FFF3B2820FF5C4337FF5D4436FF40312AFF42BCCEFF3C8FD3FF52AEE5FF203F69FF1C4545FF3AC4ECFF3A9BCCFF337DCBFF0D2A45FF0E0E15FF121826FF0B1B2DFF133044FF55DCF3FF2C7183D5020000070000000A173C54E722485FFF37251DFF563F34FF654A40FF573A2FFF354444FF3BCAE5FF348CD1FF40B8E4FF28508AFF24737EFF32B7ECFF3CC3E4FF3697DBFF12385EFF130C0FFF191722FF0C1B29FF0A192BFF2D819EFF40ADCCFF03050E3C03090E45205882FF27394BFF4B3328FF584237FF5F463BFF513126FF32686DFF3DD3F3FF2F89D0FF3BC7E6FF2E67ADFF309FB8FF2F9CD8FF44DBE9FF41B8EAFF194D7CFF0F0704FF16141CFF161721FF0C1A27FF17415DFF44B2DEFF102533760D1D2A83246595FF38393FFF573D2FFF654C40FF5C463CFF321A13FF35929AFF3CCEF4FF266FACFF44B5BFFF3A8ED4FF38B9E4FF286A9CFF55BCBDFF53DBFCFF1F65A1FF24160FFF1A1515FF1A151EFF121724FF102A3FFF399CC8FF17394D9B0E2233A3246294FF473C3BFF664B3EFF6A5044FF543F34FF392B25FF45C9D1FF39C3F3FF21557FFF579798FF54B6E8FF359FD8FF21375DFF549391FF6FEEFFFF2177BAFF2C2320FF312118FF1F181CFF191520FF0E1D2CFF317FAAFF1D435CA10F2234A2236091FF4F4341FF795A4BFF806151FF84604FFF525351FF67EDF4FF36A4E1FF244162FF517376FF66D6F5FF3273C1FF231D35FF4A7873FF80FEFFFF298ED0FF2B2B33FF3C271EFF2B1E19FF1C151EFF151722FF2D6C8EFF1A3A4FA00C1B2B88236592FF524C4CFF936E5CFF916F5DFF755142FF5F817FFF7CF1FFFF2E77C3FF293446FF454C4CFF5AD2ECFF3254A8FF301F22FF405F5DFF56F8FFFF358CD5FF29354DFF3E2A1EFF33231BFF231719FF161924FF296789FF1125328E080C15522A76A3FF52636EFF9B725DFF7D5F51FF614135FF74AEB0FF71DFF7FF2A64AFFF2F3337FF4D3933FF5BC2D4FF38559BFF39221AFF374545FF54EFFBFF3884C7FF28305AFF3C291DFF271A16FF1E1310FF18222FFF235C85FF070F1A5E010000192C6C90F54486A6FF725043FF7B5A4CFF6F5448FF76D9DDFF54B5E0FF2F539BFF473A33FF634436FF548698FF374F80FF3C2719FF383433FF49D5E7FF3789C0FF292863FF2F2013FF261A15FF150C08FF193448FF1C4566F30502061901000000173647A947BDE0FF6E6A68FF9E705AFF6B625DFF4CD7E9FF3281C7FF3C4F89FF674B3DFF7D5747FF61646EFF313A57FF4A3527FF443028FF38ACC7FF2986C0FF222778FF2A1E1AFF2B1C14FF161213FF1F4B69FF0E2133A4010002000202080002050B3841A7BEFB62BDCDFF977566FF486377FF60C7EAFF74AFDDFF44557DFF85604CFF98725FFF6F574EFF3F3434FF594339FF4B362BFF358AB3FF76CEF2FF5E8DCAFF1E273FFF1B0C05FF152F41FF194260FC03040C360000060001020B00000001101B4B64EE7CEBF8FF6DB3BFFF607078FF959A92FF98A095FF8D837AFFAF8A76FFB08B77FF735547FF6C5245FF684F47FF503F37FF3D575AFF5A7472FF406262FF1C242BFF111F2BFF18435FFF102A3DEF01000411020008000000000000000014205987F47AB5D5FFCDFFFFFF87BDC6FFA38F84FFD8AF96FFDFC0A8FFDEC1AAFFB28C77FF8B6854FF826855FF775F4FFF6A5347FF543B30FF3D271BFF291814FF172533FF1F4B63FF325D79FF224E7AF404010214050207000000030000000212385A6CD57498A5E45A7E8CEEA6F4FCFF6CD3E1FF84A9ABFFBFAFA0FFD5B39BFFCFA88EFFCBA086FFBD9279FF8C6B56FF6E5142FF50413BFF353E47FF214765FF194768FF163445EF498A98E4305770D501000312020107000100080001000801000001080000000800000215113645964BB5C4FF5EEBFDFF4AC1D9FF56A2B2FF668F98FF7E8F94FF758184FF526975FF39677EFF2D6E92FF286F9AFF1D4C6EF508141D830000001600000008030000080200080101000800010008000100080002010700030007000209110000060F0000000236183D479D32849AE340B3CFFF40B2D5FF3E9DC7FF3E99C2FF4093B8FF3880A2FF22536EDC0F242F88010304220000000000000000000001000603070002000800010008000100080001000800020107000300070002091100040E1800000000000000000001020C260E202D62163341931F42539F1F41509F162B36990B171D5F0000021F0000000000010300000000000000000000000100060307000200080001000800FF00FF00FC003F0080000F0080000100800001008000010080000100800000000000000000000000000000000000000000000000000000000000000000000000800001008000010080000100800001008000010080000100FC003F00FF00FF0028000000100000002000000001002000000000000000000000000000000000000000000000000000010008000101060000010300030003000100000004080F3D0F25347C1C4C649D2561769C1C43507D0D1E2F42030C1F000107100001000700030108000100080001000800000002050000000805070B3D194A64C82780ABFF24709BFF266685FF2F6E81FF3E8EA1FF5CC4D4FF4B9EADC90B1C2741000000030100030201000800000002001C3D509A356575EA205065FE1E4A62FF151A1FFF1A0900FF1E0902FF120503FF040103FF0D1A24FF397E8EFF67C9D6FE56909FDE1D3F509F0000020000000000122D3FA72B5B73FF202A30FF2F180CFF303745FF2D3F64FF262B35FF212028FF21345EFF162C50FF010A1FFF275062FF8CE6F4FF2A5668B80000000000010005152D39D2232F34FF402A1EFF583729FF408692FF47AAECFF234C72FF22565EFF40A5E2FF275799FF08101BFF061022FF346F80FF4EACBAE005030510030A0F3E1F455DFF392922FF61463BFF503529FF3897ABFF3EA9E8FF306A97FF25798FFF3CC2EFFF2C7CB7FF10111CFF141623FF091B2DFF3BA4C1FF13303E680D273B892B4962FF52382BFF604639FF403931FF37B5D3FF339FD5FF3591C6FF2F97C4FF42C0DAFF3BADDDFF141A27FF171216FF0E1320FF256788FF235871A9143956BF3D4E5FFF664839FF5C4034FF39524EFF3BCCF0FF307294FF53B3D8FF2D83BCFF4B8890FF56D0F7FF253346FF281812FF16111BFF1B445EFF266080C1123755BE475463FF85604EFF7F5747FF62908DFF47BBECFF2D4057FF5DB4CDFF2D5491FF415D5AFF5EE1FFFF294566FF3A2316FF211518FF1D3447FF214D66BE0F2E44934B6B80FF956C58FF6C4B3EFF76BDC0FF4090CBFF32292FFF569AABFF384B7CFF3A453CFF4AD2F1FF2C4373FF382418FF22130FFF1D384FFF122D42990914214A418BABFF7A594CFF776153FF5FCCE0FF3463A2FF563C32FF5D707BFF384360FF3D342BFF3DB9D6FF263C7BFF2E1D14FF1B110CFF1B3E58FF0A121E49010002072F7F95D77BA2A3FF6B6B6DFF57BDE4FF4C6490FF845E4BFF755E57FF43383AFF4C372DFF439EC2FF5389C5FF221C28FF192229FF13334BD60000040600000100143A51A882DFF3FF799DA5FFA69B8FFFAE9E8EFFBD9883FF886554FF6D5446FF5C483FFF4B5351FF485651FF182530FF1B425DFF0F253BA80200010000000100223D509A77A1B2EA93D6E0FF8AC3C6FFC5B9AAFFD4B199FFBD9278FFA37D65FF715646FF4C3E39FF273748FF163953FF386D81EA213E559A020001000100080002000605000000080A1F2B513992A0D54BBDD3FF58B0C3FF6C9CACFF63899AFF427892FF2B698DFF17415DC7040A0F47000000090502070501000800010008000200070003030A00010811000000000307151F3A143D4E7E245A72A024556BA1132E3A7E060E14340000000000000000010001000502080001000800F81F00008001000080010000800100000000000000000000000000000000000000000000000000000000000000000000800100008001000080010000F01F000028000000100000002000000001002000000000000000000000000000000000000000000000000000010008000101060000010300030003000100000004080F3D0F25347C1C4C649D2561769C1C43507D0D1E2F42030C1F000107100001000700030108000100080001000800000002050000000805070B3D194A64C82780ABFF24709BFF266685FF2F6E81FF3E8EA1FF5CC4D4FF4B9EADC90B1C2741000000030100030201000800000002001C3D509A356575EA205065FE1E4A62FF151A1FFF1A0900FF1E0902FF120503FF040103FF0D1A24FF397E8EFF67C9D6FE56909FDE1D3F509F0000020000000000122D3FA72B5B73FF202A30FF2F180CFF303745FF2D3F64FF262B35FF212028FF21345EFF162C50FF010A1FFF275062FF8CE6F4FF2A5668B80000000000010005152D39D2232F34FF402A1EFF583729FF408692FF47AAECFF234C72FF22565EFF40A5E2FF275799FF08101BFF061022FF346F80FF4EACBAE005030510030A0F3E1F455DFF392922FF61463BFF503529FF3897ABFF3EA9E8FF306A97FF25798FFF3CC2EFFF2C7CB7FF10111CFF141623FF091B2DFF3BA4C1FF13303E680D273B892B4962FF52382BFF604639FF403931FF37B5D3FF339FD5FF3591C6FF2F97C4FF42C0DAFF3BADDDFF141A27FF171216FF0E1320FF256788FF235871A9143956BF3D4E5FFF664839FF5C4034FF39524EFF3BCCF0FF307294FF53B3D8FF2D83BCFF4B8890FF56D0F7FF253346FF281812FF16111BFF1B445EFF266080C1123755BE475463FF85604EFF7F5747FF62908DFF47BBECFF2D4057FF5DB4CDFF2D5491FF415D5AFF5EE1FFFF294566FF3A2316FF211518FF1D3447FF214D66BE0F2E44934B6B80FF956C58FF6C4B3EFF76BDC0FF4090CBFF32292FFF569AABFF384B7CFF3A453CFF4AD2F1FF2C4373FF382418FF22130FFF1D384FFF122D42990914214A418BABFF7A594CFF776153FF5FCCE0FF3463A2FF563C32FF5D707BFF384360FF3D342BFF3DB9D6FF263C7BFF2E1D14FF1B110CFF1B3E58FF0A121E49010002072F7F95D77BA2A3FF6B6B6DFF57BDE4FF4C6490FF845E4BFF755E57FF43383AFF4C372DFF439EC2FF5389C5FF221C28FF192229FF13334BD60000040600000100143A51A882DFF3FF799DA5FFA69B8FFFAE9E8EFFBD9883FF886554FF6D5446FF5C483FFF4B5351FF485651FF182530FF1B425DFF0F253BA80200010000000100223D509A77A1B2EA93D6E0FF8AC3C6FFC5B9AAFFD4B199FFBD9278FFA37D65FF715646FF4C3E39FF273748FF163953FF386D81EA213E559A020001000100080002000605000000080A1F2B513992A0D54BBDD3FF58B0C3FF6C9CACFF63899AFF427892FF2B698DFF17415DC7040A0F47000000090502070501000800010008000200070003030A00010811000000000307151F3A143D4E7E245A72A024556BA1132E3A7E060E14340000000000000000010001000502080001000800F81F00008001000080010000800100000000000000000000000000000000000000000000000000000000000000000000800100008001000080010000F01F0000;1
y38fix;1B3A26;8B471C83C0018945F4DB45F4DD1C2453E8659C29008B4F1883C101894DF4DB45F483C404DD1C2453E84D9C2900DB472083C404DD1C2453E83E9C2900;1
y38fix;1B3BFD;8B571C83C2018955F8DB45F8DD1C2456E88E9A29008B471883C0018945F8DB45F883C404DD1C2456E8769A2900DB472083C404DD1C2456E8679A2900;1
y38fix;1B6F5F;0A000000;1
y38fix;1B6F66;17000000;1
y38fix;1B6F6D;04000000;1
y38fix;1B72B4;D0070000;1
y38fix;1B75BE;D0070000;1
y38fix;1B7609;0A000000;1
y38fix;1B7610;17000000;1
y38fix;1B7617;04000000;1
y38fix;1B767B;D0070000;1
y38fix;1B7724;D0070000;1
y38fix;1B77E9;D0070000;1
y38fix;1B7876;D0070000;1
y38fix;1B833E;04;1
y38fix;1B8345;04000000;1
y38fix;1B834D;0A;1
y38fix;1B8351;0A000000;1
y38fix;1B83A5;04;1
y38fix;1B83AC;04000000;1
y38fix;1B8E60;D0070000;1
y38fix;1B8F20;04000000;1
y38fix;1B8F4D;D0070000;1
y38fix;1B8F93;D0070000;1
y38fix;1B9906;D0070000;1
y38fix;1BA952;D0070000;1
y38fix;1BAB02;D0070000;1
y38fix;1BCE53;D0070000;1
y38fix;1BCEE5;D0070000;1
y38fix;1BEFDC;04000000;1
y38fix;1BF368;04;1
y38fix;1BF36D;0A;1
y38fix;1BF36F;04000000;1
y38fix;1BF37B;0A000000;1
y38fix;1C380E;04000000;1
y38fix;1C383B;D0070000;1
y38fix;22D2E9;83C60156E8DE1114008945D0;1
y38fix;2CB8EF;D0070000;1
y38fix;36BF3D;D0070000;1
watermark;72DE20;00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000;1
pe;116;0600;0
pe;160;00D09F00;0
pe;1A8;007C750098120000;0
pe;2F8;000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000;0
'@
# END ORIGINAL-BYTES

# ============================================================
#  Auswahl-Logik
# ============================================================

# Zerlegt "1,3 5-8" in Indizes (0-basiert). Liefert $null bei ungueltiger Eingabe.
function ConvertTo-Indices([string]$text, [int]$max) {
    $result = New-Object System.Collections.Generic.List[int]
    foreach ($tok in ($text -split '[\s,;]+')) {
        if ($tok -eq '') { continue }
        if ($tok -match '^(\d{1,6})-(\d{1,6})$') {
            $a = [int]$matches[1]; $b = [int]$matches[2]
            if ($a -gt $b) { $t = $a; $a = $b; $b = $t }
        } elseif ($tok -match '^\d{1,6}$') {
            $a = [int]$tok; $b = $a
        } else {
            return $null
        }
        if ($a -lt 1 -or $b -gt $max) { return $null }
        for ($i = $a; $i -le $b; $i++) { $result.Add($i - 1) }
    }
    if ($result.Count -eq 0) { return $null }
    return , $result.ToArray()
}

# Standard-Auswahl = Preset "Reforged"
function Get-DefaultSelection {
    $sel = New-Object bool[] $patches.Count
    for ($i = 0; $i -lt $patches.Count; $i++) { $sel[$i] = $PRESET_REFORGED -contains $patches[$i].Id }
    return , $sel
}

# Preset "Billy's_Wow.exe" aus den On-Eintraegen der Patches
function Get-BillySelection {
    $sel = New-Object bool[] $patches.Count
    for ($i = 0; $i -lt $patches.Count; $i++) { $sel[$i] = [bool]$patches[$i].On }
    return , $sel
}

# Preset "St0nys_Wow.exe" aus der Id-Liste $PRESET_STONY
function Get-StonySelection {
    $sel = New-Object bool[] $patches.Count
    for ($i = 0; $i -lt $patches.Count; $i++) { $sel[$i] = $PRESET_STONY -contains $patches[$i].Id }
    return , $sel
}

# Gespeicherte Auswahl aus patcher_selection.ini lesen. Liefert $null, wenn es
# keine gibt. Gespeichert wird pro Patch-Id, nicht pro Nummer: Patches, die in
# der Datei fehlen (z.B. in einer neueren Version hinzugekommen), bekommen
# ihren Standardwert (Preset Reforged), unbekannte Eintraege werden ignoriert.
function Get-SavedSelection {
    if (-not (Test-Path -LiteralPath $settingsFile -PathType Leaf)) { return $null }
    try { $lines = [System.IO.File]::ReadAllLines($settingsFile) } catch { return $null }
    $saved = @{}
    foreach ($l in $lines) {
        if ($l -match '^\s*([A-Za-z0-9_]+)\s*=\s*([01])\s*$') { $saved[$matches[1]] = ($matches[2] -eq '1') }
    }
    if ($saved.Count -eq 0) { return $null }
    $sel = Get-DefaultSelection
    for ($i = 0; $i -lt $patches.Count; $i++) {
        if ($saved.ContainsKey($patches[$i].Id)) { $sel[$i] = $saved[$patches[$i].Id] }
    }
    return , $sel
}

# Gemerkte Sprache (Zeile "language=de|en") aus patcher_selection.ini lesen.
function Get-SavedLanguage {
    if (-not (Test-Path -LiteralPath $settingsFile -PathType Leaf)) { return $null }
    try { $lines = [System.IO.File]::ReadAllLines($settingsFile) } catch { return $null }
    foreach ($l in $lines) {
        if ($l -match '^\s*language\s*=\s*(de|en)\s*$') { return $matches[1].ToLowerInvariant() }
    }
    return $null
}

# Nur die Sprache in patcher_selection.ini setzen, alles andere bleibt stehen.
# Fehler beim Schreiben sind hier unkritisch und werden ignoriert.
function Save-Language([string]$language) {
    try {
        $lines = New-Object System.Collections.Generic.List[string]
        if (Test-Path -LiteralPath $settingsFile -PathType Leaf) {
            foreach ($l in [System.IO.File]::ReadAllLines($settingsFile)) {
                if ($l -notmatch '^\s*language\s*=') { $lines.Add($l) }
            }
        }
        $lines.Add("language=$language")
        [System.IO.File]::WriteAllLines($settingsFile, $lines.ToArray())
    } catch { }
}

# Nur die Werte (value.<Id>=...) in patcher_selection.ini erneuern, die Auswahl
# bleibt stehen - fuer -Select, das die gespeicherte Auswahl nicht veraendern
# soll. Fehler beim Schreiben sind hier unkritisch und werden ignoriert.
function Save-Values($values) {
    if ($values.Count -eq 0) { return }
    try {
        $lines = New-Object System.Collections.Generic.List[string]
        if (Test-Path -LiteralPath $settingsFile -PathType Leaf) {
            foreach ($l in [System.IO.File]::ReadAllLines($settingsFile)) {
                if ($l -notmatch '^\s*value\.') { $lines.Add($l) }
            }
        }
        foreach ($k in ($values.Keys | Sort-Object)) { $lines.Add("value.$k=$($values[$k])") }
        [System.IO.File]::WriteAllLines($settingsFile, $lines.ToArray())
    } catch { }
}

# Gemerkte Werte (Zeilen "value.<Id>=<Wert>") aus patcher_selection.ini lesen.
function Get-SavedValues {
    $vals = @{}
    if (-not (Test-Path -LiteralPath $settingsFile -PathType Leaf)) { return $vals }
    try { $lines = [System.IO.File]::ReadAllLines($settingsFile) } catch { return $vals }
    foreach ($l in $lines) {
        if ($l -match '^\s*value\.([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$') { $vals[$matches[1]] = $matches[2] }
    }
    return $vals
}

# Auswahl und Werte in patcher_selection.ini schreiben. Liefert $null oder die Fehlermeldung.
function Save-Selection($sel, $values) {
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# St0nys-AIO-WoW-EXE-Patcher - gespeicherte Patch-Auswahl / saved patch selection")
    $lines.Add('# 1 = an / on, 0 = aus / off')
    $lines.Add('# Datei loeschen setzt die Auswahl zurueck / delete this file to reset the selection')
    for ($i = 0; $i -lt $patches.Count; $i++) {
        $v = 0; if ($sel[$i]) { $v = 1 }
        $lines.Add("$($patches[$i].Id)=$v")
    }
    foreach ($k in ($values.Keys | Sort-Object)) { $lines.Add("value.$k=$($values[$k])") }
    $lines.Add("language=$script:lang")
    try {
        [System.IO.File]::WriteAllLines($settingsFile, $lines.ToArray())
        return $null
    } catch {
        return $_.Exception.Message
    }
}

# ============================================================
#  Zustand der gepatchten Wow.exe (patcher_state.ini)
#  Nach jedem Patchen merkt sich der Patcher den SHA256 der erzeugten Datei,
#  die eingespielten Patches samt Werten, die Groesse des Originals und die
#  Original-Bytes an allen Stellen, die die Patches beschrieben haben. Passt
#  die Wow.exe beim naechsten Start zu diesem Hash, wird daraus das Original
#  rekonstruiert (und per SHA256 geprueft) und die neue Auswahl darauf
#  eingespielt. So lassen sich Patches beliebig dazu- und abwaehlen.
# ============================================================
function Get-Sha256([byte[]]$data) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($data))).Replace('-', '') } finally { $sha.Dispose() }
}

function ConvertFrom-Hex([string]$hex) {
    $b = New-Object byte[] ($hex.Length / 2)
    for ($i = 0; $i -lt $b.Length; $i++) { $b[$i] = [Convert]::ToByte($hex.Substring(2 * $i, 2), 16) }
    return , $b
}

# Liefert $null, wenn es keine lesbare Zustandsdatei gibt. Undo-Eintraege
# sind Paare @(Offset, Original-Bytes).
function Read-State {
    if (-not (Test-Path -LiteralPath $stateFile -PathType Leaf)) { return $null }
    try { $lines = [System.IO.File]::ReadAllLines($stateFile) } catch { return $null }
    $st = @{ Hash = $null; Size = [int64]-1; Ids = @(); Values = @{}; Undo = New-Object System.Collections.Generic.List[object] }
    foreach ($l in $lines) {
        if ($l -match '^hash=([0-9A-Fa-f]{64})$') { $st.Hash = $matches[1].ToUpperInvariant() }
        elseif ($l -match '^size=(\d+)$') { $st.Size = [int64]$matches[1] }
        elseif ($l -match '^patches=(.*)$') { $st.Ids = @($matches[1] -split ',' | Where-Object { $_ -ne '' }) }
        elseif ($l -match '^value\.([A-Za-z0-9_]+)=(.*)$') { $st.Values[$matches[1]] = $matches[2] }
        elseif ($l -match '^undo=0x([0-9A-Fa-f]+):((?:[0-9A-Fa-f]{2})+)$') {
            $st.Undo.Add(@([Convert]::ToInt64($matches[1], 16), (ConvertFrom-Hex $matches[2])))
        }
    }
    if ($st.Values.ContainsKey('clientdate')) { $st.Values['clientdate'] = ConvertTo-ClientDate $st.Values['clientdate'] }   # aeltere Versionen: ohne Uhrzeit
    if (-not $st.Hash -or $st.Size -le 0) { return $null }
    return $st
}

# Rekonstruiert aus einer gepatchten Datei das Original: auf die alte Groesse
# kuerzen (angehaengte Sektionen fallen weg), Original-Bytes zurueckschreiben.
# Liefert $null, wenn das Ergebnis nicht exakt die originale Wow.exe ist.
function Restore-Original([byte[]]$data, $st) {
    if ($st.Size -gt $data.Length) { return $null }
    $o = New-Object byte[] $st.Size
    [Array]::Copy($data, 0, $o, 0, $st.Size)
    foreach ($u in $st.Undo) {
        if ($u[0] + $u[1].Length -gt $o.Length) { return $null }
        [Array]::Copy($u[1], 0, $o, $u[0], $u[1].Length)
    }
    if ((Get-Sha256 $o) -ne $EXPECTED_HASH) { return $null }
    return , $o
}

# Original-Bytes zu allen Schreibzugriffen von Patch(), die im Original liegen.
function Get-UndoEntries([byte[]]$orig) {
    $undo = New-Object System.Collections.Generic.List[object]
    $seen = @{}
    for ($i = 0; $i -lt $script:writes.Count; $i += 2) {
        $off = $script:writes[$i]
        $end = $off + $script:writes[$i + 1]
        if ($off -ge $orig.Length) { continue }
        if ($end -gt $orig.Length) { $end = $orig.Length }
        if ($seen.ContainsKey("$off/$end")) { continue }
        $seen["$off/$end"] = $true
        $b = New-Object byte[] ($end - $off)
        [Array]::Copy($orig, $off, $b, 0, $b.Length)
        $undo.Add(@($off, $b))
    }
    return , $undo
}

# Zustandsdatei schreiben. Liefert $null oder die Fehlermeldung.
function Write-State([string]$path, [string]$hash, [int64]$size, $ids, $values, $undo) {
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add('# St0nys-AIO-WoW-EXE-Patcher - Zustand der gepatchten Wow.exe / state of the patched Wow.exe')
    $lines.Add('# Nicht von Hand aendern! Nur zur Beschleunigung - ohne diese Datei ermittelt der Patcher den Patchstand ueber das Wasserzeichen.')
    $lines.Add('# Do not edit! Only speeds things up - without this file the patcher determines the patch state via the watermark.')
    $lines.Add("hash=$hash")
    $lines.Add("size=$size")
    $lines.Add("patches=$($ids -join ',')")
    foreach ($k in ($values.Keys | Sort-Object)) { $lines.Add("value.$k=$($values[$k])") }
    foreach ($u in $undo) {
        $lines.Add(('undo=0x{0:X}:{1}' -f $u[0], ([BitConverter]::ToString($u[1])).Replace('-', '')))
    }
    try {
        [System.IO.File]::WriteAllLines($path, $lines.ToArray())
        return $null
    } catch {
        return $_.Exception.Message
    }
}

# Hinweis auf Wow.exe.ORI bzw. Wow.exe.BAK, wenn eine davon das Original enthaelt
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

function Get-PatchById([string]$id) {
    foreach ($q in $patches) { if ($q.Id -eq $id) { return $q } }
    return $null
}

# Anzeigename auch fuer Ids, die es in dieser Version nicht mehr gibt.
function Get-NameById([string]$id) {
    $q = Get-PatchById $id
    if ($q) { return PatchName $q -NoTags }
    return $id
}

# Vorschlag fuer einen Patch mit eigener Eingabe: der gemerkte Wert, sonst der
# Default; Patches mit Suggest berechnen ihren Vorschlag selbst (Build-Datum:
# heute). Ist der Patch schon in der Wow.exe, ist sein aktueller Wert der
# Vorschlag. Ohne Rueckfragen (-Unattended) gilt der gemerkte Wert - auch wenn
# der Patch schon mit einem anderen Wert drin ist, sonst liesse sich der Wert
# unbeaufsichtigt nie aendern.
function Test-ValueActive($p) {
    return ($script:patchedMode -and ($script:appliedIds -contains $p.Id) -and $script:state.Values.ContainsKey($p.Id))
}

function Get-ValueSuggestion($p) {
    $active = Test-ValueActive $p
    $saved = $script:savedValues[$p.Id]
    if ($active -and -not ($Unattended -and $saved)) { $saved = $script:state.Values[$p.Id] }
    $def = $saved
    if (-not $def) { $def = $p.Default }
    if ($p.Suggest -and -not $active -and -not ($Unattended -and $saved)) { $def = & $p.Suggest $saved }
    return $def
}

# Kommt der Vorschlag aus Suggest (Build-Datum: jetzt)? Dann gilt beim
# Uebernehmen der Zeitpunkt, an dem das Patchen mit J bestaetigt wird.
function Test-SuggestNow($p) {
    $saved = $script:savedValues[$p.Id]
    return [bool]($p.Suggest -and -not (Test-ValueActive $p) -and -not ($Unattended -and $saved))
}
# Wert fuer die Anzeige: bei "Zeitpunkt der Bestaetigung" dieser Text (mit FR).
function Get-ValueText($p) {
    $v = $script:VALUES[$p.Id]
    if ($script:atConfirm -contains $p.Id) {
        $t = T 'ValueAtYes'; if ($Unattended) { $t = T 'ValueAtStart' }
        if ($v -match '\sFR\s*$') { $t += ' FR' }
        return $t
    }
    return $v
}

function Get-SelectedCount($sel) {
    $n = 0
    foreach ($s in $sel) { if ($s) { $n++ } }
    return $n
}

function Show-Menu($sel, [string]$message) {
    Clear-Host
    $total = $patches.Count
    $width = ([string]$total).Length
    Write-Host ''
    Say (T 'MenuTitle' (Get-SelectedCount $sel) $total) 'Cyan'
    Say ('=' * 70) 'Cyan'
    $lastCat = ''
    for ($i = 0; $i -lt $total; $i++) {
        if ($patches[$i].Cat -ne $lastCat) {
            $lastCat = $patches[$i].Cat
            $c = $CATEGORIES[$lastCat]
            if ($script:lang -eq 'en') { $title = $c.En } else { $title = $c.De }
            Write-Host "   -- $title --" -ForegroundColor Yellow
        }
        $nr = ([string]($i + 1)).PadLeft($width)
        $was = $script:patchedMode -and ($script:appliedIds -contains $patches[$i].Id)
        $name = PatchName $patches[$i]
        if ($sel[$i]) {
            $mark = ''; if ($script:patchedMode -and -not $was) { $mark = ' ' + (T 'MarkNew') }
            Write-Host "   $nr  [X]  $name$mark" -ForegroundColor Green
        } elseif ($was) {
            Write-Host "   $nr  [ ]  $name $(T 'MarkRemove')" -ForegroundColor Yellow
        } else {
            Write-Host "   $nr  [ ]  $name" -ForegroundColor DarkGray
        }
        if ($patches[$i].Url) {
            Write-Host "$(' ' * ($width + 10))$($patches[$i].Url)" -ForegroundColor DarkCyan
        }
    }
    Say ('=' * 70) 'Cyan'
    Say (T 'MenuHelp1')
    Say (T 'MenuHelp2')
    Say (T 'MenuPresetR')
    Say (T 'MenuPresets')
    Say (T 'MenuHelp3')
    if ($message) {
        Write-Host ''
        Say $message 'Yellow'
    }
    Write-Host ''
}

# Interaktive Auswahl, beginnend mit $sel. Liefert das bool-Array oder $null
# bei Abbruch. Eine leere Auswahl gibt es nur fuer eine gepatchte Wow.exe -
# sie bedeutet: alle Patches zuruecknehmen.
function Select-Patches([bool[]]$sel, [string]$message) {
    while ($true) {
        Show-Menu $sel $message
        $message = ''
        $in = Ask "  $(T 'Prompt')"
        switch -regex ($in) {
            '^$' {
                if ((Get-SelectedCount $sel) -eq 0 -and -not $script:patchedMode) { $message = T 'NoneSelected'; break }
                return , $sel
            }
            '^[aA]$'   { for ($i = 0; $i -lt $sel.Length; $i++) { $sel[$i] = $true };  break }
            '^[nN]$'   { for ($i = 0; $i -lt $sel.Length; $i++) { $sel[$i] = $false }; break }
            '^[rR]$'   { $sel = Get-DefaultSelection; break }
            '^[bB]$'   { $sel = Get-BillySelection; break }
            '^[sS]$'   { $sel = Get-StonySelection; $message = T 'StonyWarning'; break }
            '^[lL]$'   {
                if ($script:lang -eq 'de') { $script:lang = 'en' } else { $script:lang = 'de' }
                Save-Language $script:lang
                break
            }
            '^[qQxX]$' { return $null }
            default {
                $idx = ConvertTo-Indices $in $sel.Length
                if ($null -eq $idx) { $message = T 'BadInput' $in; break }
                foreach ($i in $idx) { $sel[$i] = -not $sel[$i] }
            }
        }
    }
}

# Nicht-interaktive Auswahl ueber -Select. Liefert $null bei ungueltigem Wert.
function Get-SelectionFromParam([string]$value) {
    $v = $value.Trim().ToLowerInvariant()
    if ($v -eq 'reforged' -or $v -eq 'default' -or $v -eq 'standard') { return , (Get-DefaultSelection) }
    if ($v -eq 'billy') { return , (Get-BillySelection) }
    if ($v -eq 'stony' -or $v -eq 'st0ny') { return , (Get-StonySelection) }
    if ($v -eq 'saved' -or $v -eq 'gespeichert') {
        $sel = Get-SavedSelection
        if ($null -eq $sel) { $sel = Get-DefaultSelection }
        return , $sel
    }
    $sel = New-Object bool[] $patches.Count
    if ($v -eq 'none' -or $v -eq 'keine' -or $v -eq 'original') { return , $sel }
    if ($v -eq 'all' -or $v -eq 'alle') {
        for ($i = 0; $i -lt $sel.Length; $i++) { $sel[$i] = $true }
        return , $sel
    }
    $idx = ConvertTo-Indices $v $sel.Length
    if ($null -eq $idx) { return $null }
    foreach ($i in $idx) { $sel[$i] = $true }
    return , $sel
}

# ============================================================
#  Banner in der figlet-Schrift "big"
#  Einzeilig ist es 136 Zeichen breit, das Standard-Konsolenfenster hat aber
#  nur 120 Spalten. Ist das Fenster nicht breiter als das Banner (bei genau
#  136 Spalten wuerde die letzte Spalte schon umbrechen), kommt dieselbe
#  Schrift zweizeilig (max. 78 Zeichen), damit nichts umbricht.
#  Das Fenster wird bewusst NICHT per Skript verbreitert: Beim Start per
#  Doppelklick unter Windows 11 uebernimmt Windows Terminal das Fenster, die
#  Konsole meldet die neue Breite dann zwar, das Fenster bleibt aber schmal.
# ============================================================
$BANNER_WIDE = @'
  _____ _    ___                             _____ ____   __          ____          __               _____      _       _
 / ____| |  / _ \                      /\   |_   _/ __ \  \ \        / /\ \        / /              |  __ \    | |     | |
| (___ | |_| | | |_ __  _   _ ___     /  \    | || |  | |  \ \  /\  / /__\ \  /\  / / _____  _____  | |__) |_ _| |_ ___| |__   ___ _ __
 \___ \| __| | | | '_ \| | | / __|   / /\ \   | || |  | |   \ \/  \/ / _ \\ \/  \/ / / _ \ \/ / _ \ |  ___/ _` | __/ __| '_ \ / _ \ '__|
 ____) | |_| |_| | | | | |_| \__ \  / ____ \ _| || |__| |    \  /\  / (_) |\  /\  / |  __/>  <  __/ | |  | (_| | || (__| | | |  __/ |
|_____/ \__|\___/|_| |_|\__, |___/ /_/    \_\_____\____/      \/  \/ \___/  \/  \/ (_)___/_/\_\___| |_|   \__,_|\__\___|_| |_|\___|_|
                         __/ |
                        |___/
'@

$BANNER_NARROW = @'
  _____ _    ___                             _____ ____
 / ____| |  / _ \                      /\   |_   _/ __ \
| (___ | |_| | | |_ __  _   _ ___     /  \    | || |  | |
 \___ \| __| | | | '_ \| | | / __|   / /\ \   | || |  | |
 ____) | |_| |_| | | | | |_| \__ \  / ____ \ _| || |__| |
|_____/ \__|\___/|_| |_|\__, |___/ /_/    \_\_____\____/
                         __/ |
                        |___/

__          ____          __               _____      _       _
\ \        / /\ \        / /              |  __ \    | |     | |
 \ \  /\  / /__\ \  /\  / / _____  _____  | |__) |_ _| |_ ___| |__   ___ _ __
  \ \/  \/ / _ \\ \/  \/ / / _ \ \/ / _ \ |  ___/ _` | __/ __| '_ \ / _ \ '__|
   \  /\  / (_) |\  /\  / |  __/>  <  __/ | |  | (_| | || (__| | | |  __/ |
    \/  \/ \___/  \/  \/ (_)___/_/\_\___| |_|   \__,_|\__\___|_| |_|\___|_|
'@

function Show-Banner {
    $width = 0
    try { $width = [int]$Host.UI.RawUI.WindowSize.Width } catch { }
    if ($width -gt 0 -and $width -le 136) {
        Write-Host $BANNER_NARROW
    } else {
        Write-Host $BANNER_WIDE
    }
}

# ============================================================
#  ABLAUF
# ============================================================

if ($BuildTable) {
    Invoke-BuildTable
    exit 0
}

Write-Host ''
Show-Banner
Write-Host ''

# --- 1. Sprache ---
# -Language geht vor, sonst die gemerkte Sprache; nur ohne beides wird gefragt
# (bei -Unattended gilt dann Deutsch). Die Wahl wird gemerkt.
$lang = $Language
$langFromSettings = $false
if (-not $lang) {
    $lang = Get-SavedLanguage
    if ($lang) { $langFromSettings = $true }
}
if (-not $lang -and $Unattended) { $lang = 'de' }
$askedLanguage = -not $lang
while (-not $lang) {
    Say 'Sprache waehlen / Choose language:'
    Say '  1 = Deutsch'
    Say '  2 = English'
    $in = (Ask '  [1/2]').ToLowerInvariant()
    switch ($in) {
        { $_ -eq '1' -or $_ -eq 'd' -or $_ -eq 'de' } { $lang = 'de' }
        { $_ -eq '2' -or $_ -eq 'e' -or $_ -eq 'en' } { $lang = 'en' }
    }
    Write-Host ''
}
if ($askedLanguage) { Save-Language $lang }

if ($langFromSettings) {
    Say (T 'LangInfo') 'DarkGray'
    Write-Host ''
}
Say (T 'Welcome1')
Say (T 'Welcome2')
Say (T 'Welcome3')
Write-Host ''
Say (T 'Welcome4')
Say (T 'Welcome5')
Write-Host ''
Say (T 'StartWarn1') 'Yellow'
Say (T 'StartWarn2') 'Yellow'
Say (T 'StartWarn3') 'Yellow'
Say (T 'StartWarn4') 'Yellow'
Say (T 'StartWarn5') 'Yellow'
Say (T 'StartWarn6') 'Yellow'
Write-Host ''
Say (T 'Thanks') 'Magenta'
Write-Host ''
if (-not $Unattended) {
    [void](Read-Host "  $(T 'PressStart')")
    Write-Host ''
}

# --- 2. Wow.exe vorhanden und original oder mit diesem Patcher gepatcht? ---
# Beim ersten Start muss die Wow.exe original sein. Danach erkennt der
# Patcher eine von ihm gepatchte Exe am Wasserzeichen. Passt der Hash aus
# patcher_state.ini, wird das Original schnell aus der Zustandsdatei
# rekonstruiert, sonst ueber die Original-Byte-Tabelle (mit Erkennung der
# eingespielten Patches und ihrer Werte).
if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
    Say (T 'NotFound' $file) 'Red'
    Exit-Patcher 1
}

Say (T 'Checking')
$f = [System.IO.File]::ReadAllBytes($file)
$hash = Get-Sha256 $f
$state = $null
if ($hash -eq $EXPECTED_HASH) {
    Say (T 'HashOk') 'Green'
} else {
    $state = Read-State
    $orig = $null
    if ($null -ne $state -and $state.Hash -eq $hash) { $orig = Restore-Original $f $state }
    if ($null -ne $orig) {
        # schneller Weg ueber patcher_state.ini
        Say (T 'HashKnown' @($state.Ids).Count) 'Green'
        Say (T 'RevertOk') 'Green'
    } elseif (Test-Watermark $f) {
        # Patchstand aus der Exe selbst ermitteln
        Say (T 'Scanning')
        $ids = Find-AppliedPatches $f
        $vals = @{}
        foreach ($id in $ids) {
            $p = Get-PatchById $id
            if (-not $p.Decode) { continue }
            $v = $null
            try { $v = & $p.Decode } catch { }
            if ($v -and -not (& $p.Check $v)) { $vals[$id] = [string]$v }
        }
        $orig = Restore-FromTable $f
        if ($null -eq $orig) {
            Write-Host ''
            Say (T 'WmBroken1') 'Red'
            Say (T 'WmBroken2') 'Red'
            Show-BakHint
            Exit-Patcher 1
        }
        # Zustand wie nach dem Patchen: Original-Bytes aller erkannten Patches
        # aus der Tabelle. Gibt es nichts zu tun, wird er unten gespeichert,
        # damit der naechste Start wieder den schnellen Weg nehmen kann.
        $undo = New-Object System.Collections.Generic.List[object]
        foreach ($e in (Get-OriginalTable).Entries) {
            if ($ids -contains $e.Id -or $e.Id -eq 'watermark' -or $e.Id -eq 'pe') { $undo.Add(@($e.Off, $e.Bytes)) }
        }
        $state = @{ Hash = $hash; Size = (Get-OriginalTable).Size; Ids = $ids; Values = $vals; Undo = $undo; Scanned = $true }
        Say (T 'WmFound') 'Green'
        Say (T 'WmScanned' $ids.Count) 'Green'
    } else {
        Write-Host ''
        Say (T 'HashBad1') 'Red'
        Say (T 'HashBad2') 'Red'
        Write-Host ''
        Say (T 'Expected' $EXPECTED_HASH)
        Say (T 'Found' $hash)
        Write-Host ''
        Say (T 'HashBad3')
        Show-BakHint
        Exit-Patcher 1
    }
    $origPatched = $f      # die gepatchte Datei, wie sie auf der Platte liegt
    $f = $orig
    $patchedMode = $true
    $appliedIds = @($state.Ids)
}
Write-Host ''

# --- 3. Patches auswaehlen ---
$savedValues = Get-SavedValues
# Build-Datum aus aelteren Versionen ohne Uhrzeit: originale 23:54:57 ergaenzen
if ($savedValues.ContainsKey('clientdate')) { $savedValues['clientdate'] = ConvertTo-ClientDate $savedValues['clientdate'] }
$fromMenu = $false
if ($Select) {
    $selection = Get-SelectionFromParam $Select
    if ($null -eq $selection) {
        Say (T 'BadSelect' $Select) 'Red'
        Exit-Patcher 1
    }
} else {
    $message = ''
    if ($patchedMode) {
        $initial = New-Object bool[] $patches.Count
        for ($i = 0; $i -lt $patches.Count; $i++) { $initial[$i] = $appliedIds -contains $patches[$i].Id }
        $message = T 'AppliedLoaded'
    } else {
        $initial = Get-SavedSelection
        if ($null -eq $initial) { $initial = Get-DefaultSelection } else { $message = T 'SavedLoaded' }
    }
    $selection = Select-Patches $initial $message
    if ($null -eq $selection) {
        Write-Host ''
        Say (T 'Aborted') 'Yellow'
        Exit-Patcher 2
    }
    Clear-Host
    $fromMenu = $true
}

$chosen = @()
$chosenIds = @()
for ($i = 0; $i -lt $patches.Count; $i++) {
    if ($selection[$i]) { $chosen += , $patches[$i]; $chosenIds += $patches[$i].Id }
}
if ($chosen.Count -eq 0 -and -not $patchedMode) {
    Say (T 'AlreadyOrig') 'Green'
    Exit-Patcher 0
}

# --- 3b. Werte fuer Patches mit eigener Eingabe (Vorschlag: Get-ValueSuggestion) ---
$VALUES = @{}
$atConfirm = @()      # Ids, deren Wert erst beim Bestaetigen mit J feststeht (Build-Datum: jetzt)
$asked = $false
foreach ($p in $chosen) {
    if (-not $p.Check) { continue }
    $def = Get-ValueSuggestion $p
    $useNow = Test-SuggestNow $p
    if ($Unattended) {
        if ($useNow) { $atConfirm += $p.Id }
        $err = & $p.Check $def
        if ($err) {
            Say (T 'BadValue' (PatchName $p) $def) 'Red'
            Say $err 'Red'
            Exit-Patcher 1
        }
        if ($p.Normalize) { $def = & $p.Normalize $def }
        $VALUES[$p.Id] = $def
        continue
    }
    if (-not $asked) {
        Write-Host ''
        Say (T 'InputHead') 'Cyan'
        $asked = $true
    }
    # Vorschlag bzw. aktuellen Wert hinter den Namen mit dem Originalwert schreiben
    $label = 'ValueSuggest'; if (Test-ValueActive $p) { $label = 'ValueNow' }
    Write-Host ''
    $shown = $def
    if ($useNow) { $shown = T 'ValueAtYes'; if ($def -match '\sFR\s*$') { $shown += ' FR' } }
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
    if ($p.Normalize) { $v = & $p.Normalize $v }
    if ($takeNow) { $atConfirm += $p.Id }
    $VALUES[$p.Id] = $v
}

$allValues = @{}
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

# --- 4. Zusammenfassung, Hinweise, Bestaetigung ---
Write-Host ''
$added = @(); $changed = @(); $removed = @(); $kept = 0
if (-not $patchedMode) {
    Say (T 'Summary' $chosen.Count) 'Cyan'
    foreach ($p in $chosen) {
        if ($VALUES.ContainsKey($p.Id)) { Say "  - $(PatchName $p): $(Get-ValueText $p)" } else { Say "  - $(PatchName $p)" }
        if ($p.Url) { Say "    $($p.Url)" 'DarkCyan' }
    }
} else {
    foreach ($p in $chosen) {
        if ($appliedIds -notcontains $p.Id) { $added += , $p }
        elseif ($VALUES.ContainsKey($p.Id) -and $VALUES[$p.Id] -cne $state.Values[$p.Id]) { $changed += , $p }
        else { $kept++ }
    }
    foreach ($id in $appliedIds) { if ($chosenIds -notcontains $id) { $removed += $id } }
    if ($added.Count + $changed.Count + $removed.Count -eq 0 -and $chosen.Count -gt 0) {
        Say (T 'NoChange') 'Green'
        if ($state.Scanned -and $null -ne (Restore-Original $origPatched $state)) {
            # Patchstand kam ueber das Wasserzeichen - jetzt merken, dann geht es beim naechsten Mal schneller.
            if ($null -eq (Write-State $stateFile $state.Hash $state.Size $state.Ids $state.Values $state.Undo)) { Say (T 'StateSaved') 'DarkGray' }
        }
        Exit-Patcher 0
    }
    if ($added.Count -gt 0) {
        Say (T 'SumAdd' $added.Count) 'Cyan'
        foreach ($p in $added) {
            if ($VALUES.ContainsKey($p.Id)) { Say "  + $(PatchName $p): $(Get-ValueText $p)" 'Green' } else { Say "  + $(PatchName $p)" 'Green' }
            if ($p.Url) { Say "    $($p.Url)" 'DarkCyan' }
        }
    }
    if ($changed.Count -gt 0) {
        Say (T 'SumChange' $changed.Count) 'Cyan'
        foreach ($p in $changed) {
            $old = $state.Values[$p.Id]; if (-not $old) { $old = '?' }
            Say "  ~ $(PatchName $p): $old -> $(Get-ValueText $p)" 'Green'
        }
    }
    if ($removed.Count -gt 0) {
        Say (T 'SumRemove' $removed.Count) 'Cyan'
        foreach ($id in $removed) { Say "  - $(Get-NameById $id)" 'Yellow' }
    }
    Say (T 'SumKeep' $kept)
    if ($chosen.Count -eq 0) {
        Write-Host ''
        Say (T 'SumOriginal') 'Yellow'
    }
}

foreach ($p in $chosen) {
    if (-not $p.Needs) { continue }
    $missing = @()
    foreach ($id in $p.Needs) {
        if ($chosenIds -notcontains $id) {
            foreach ($q in $patches) { if ($q.Id -eq $id) { $missing += PatchRef $q } }
        }
    }
    if ($missing.Count -gt 0) {
        Write-Host ''
        Say (T 'HintHead' (PatchRef $p)) 'Yellow'
        Say (T 'Hint') 'Yellow'
        foreach ($m in $missing) { Say "  - $m" 'Yellow' }
    }
}
foreach ($p in $chosen) {
    if (-not $p.Obsoletes) { continue }
    $both = @()
    foreach ($id in $p.Obsoletes) {
        if ($chosenIds -contains $id) {
            foreach ($q in $patches) { if ($q.Id -eq $id) { $both += PatchRef $q } }
        }
    }
    if ($both.Count -gt 0) {
        Write-Host ''
        Say (T 'HintHead' (PatchRef $p)) 'Yellow'
        Say (T 'Obsolete') 'Yellow'
        foreach ($m in $both) { Say "  - $m" 'Yellow' }
    }
}
$cheat = @()
foreach ($p in $chosen) { if ($p.BanRisk) { $cheat += PatchRef $p } }
if ($cheat.Count -gt 0) {
    Write-Host ''
    Say (T 'CheatHead') 'Red'
    foreach ($m in $cheat) { Say "  - $m" 'Red' }
    Say (T 'CheatBan') 'Red'
}
$grow = @()
foreach ($p in $chosen) { if ($p.GrowsExe) { $grow += PatchRef $p } }
if ($grow.Count -gt 0) {
    Write-Host ''
    Say (T 'GrowHead') 'Yellow'
    foreach ($m in $grow) { Say "  - $m" 'Yellow' }
    Say (T 'GrowBan') 'Yellow'
}
$public = @()
foreach ($p in $chosen) { if ($p.PublicUntested) { $public += PatchRef $p } }
if ($public.Count -gt 0) {
    Write-Host ''
    Say (T 'PublicHead') 'Yellow'
    foreach ($m in $public) { Say "  - $m" 'Yellow' }
    Say (T 'PublicBan') 'Red'
}
$untested = @()
foreach ($p in $chosen) { if ($p.GameUntested) { $untested += PatchRef $p } }
if ($untested.Count -gt 0) {
    Write-Host ''
    Say (T 'UntestedHead') 'Yellow'
    foreach ($m in $untested) { Say "  - $m" 'Yellow' }
    Say (T 'UntestedWarn') 'Red'
}
Write-Host ''

if (-not $Unattended) {
    $answer = (Ask "  $(T 'Confirm')").ToUpperInvariant()
    if ($answer -ne (T 'Yes') -and $answer -ne 'Y' -and $answer -ne 'J') {
        Write-Host ''
        Say (T 'Aborted') 'Yellow'
        Exit-Patcher 2
    }
    Write-Host ''
}

# Werte "Zeitpunkt der Bestaetigung" jetzt festlegen (ohne Rueckfragen: beim
# Start des Patchens) und gemerkt ablegen.
if ($atConfirm.Count -gt 0) {
    foreach ($p in $chosen) {
        if ($atConfirm -notcontains $p.Id) { continue }
        $v = & $p.Suggest $VALUES[$p.Id]
        if ($p.Normalize) { $v = & $p.Normalize $v }
        $VALUES[$p.Id] = $v
        $allValues[$p.Id] = $v
    }
    Save-Values $allValues
}

# --- 5. Backup ---
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
Write-Host ''
Say (T 'Starting')
Write-Host ''

# --- 6. Patchen (im Speicher) ---
# $f ist hier immer das Original (gelesen oder rekonstruiert); abgewaehlte
# Patches sind damit schon zurueckgenommen, die Auswahl wird neu eingespielt.
$origBytes = [byte[]]$f.Clone()
$writes.Clear()
foreach ($id in $removed) { Say "[-] $(Get-NameById $id)" 'Yellow' }
$total = $chosen.Count
$width = ([string]$total).Length
$cur = 0
try {
    foreach ($p in $chosen) {
        $cur++
        Say "[+] $(([string]$cur).PadLeft($width))/$total - $(PatchName $p -NoTags)"
        & $p.Code
    }
    if ($total -gt 0) { Add-Watermark }
} catch {
    Write-Host ''
    Say (T 'PatchFail') 'Red'
    Say $_.Exception.Message 'Red'
    Say (T 'NotWritten') 'Red'
    Exit-Patcher 1
}

# --- 7. Zustand vorbereiten ---
# Erst die Original-Bytes sammeln und pruefen, dass sich das Ergebnis damit
# exakt zum Original zuruecknehmen laesst. Der neue Zustand geht zuerst in
# eine .tmp-Datei und ersetzt den alten erst, wenn die Wow.exe geschrieben ist.
$stateTmp = $stateFile + '.tmp'
$stateWarn = $null
if ($total -gt 0) {
    $undo = Get-UndoEntries $origBytes
    if ($null -eq (Restore-Original $f @{ Size = [int64]$origBytes.Length; Undo = $undo })) {
        Write-Host ''
        Say (T 'UndoFail') 'Red'
        Say (T 'NotWritten') 'Red'
        Exit-Patcher 1
    }
    if ($null -eq (Restore-FromTable $f)) { Write-Host ''; Say (T 'TableWarn') 'Yellow' }
    # Die Zustandsdatei ist nur eine Beschleunigung - ein Schreibfehler
    # verhindert das Patchen nicht (Hinweis am Ende).
    $stateWarn = Write-State $stateTmp (Get-Sha256 $f) $origBytes.Length $chosenIds $VALUES $undo
}

# --- 8. Datei einmal zurueckschreiben ---
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

# Download-Markierung (Zone.Identifier, "aus dem Internet") entfernen - wie das
# Haekchen "Zulassen" in den Dateieigenschaften. Ersetzen per File.Replace
# uebernimmt sie sonst von der alten Wow.exe. Nur unter Windows vorhanden.
if (Get-Command Unblock-File -ErrorAction SilentlyContinue) {
    try { Unblock-File -LiteralPath $file -ErrorAction Stop } catch { }
}

# --- 9. Zustand uebernehmen (ohne Patches ist die Wow.exe original, dann weg damit) ---
try {
    if ($total -gt 0 -and $stateWarn) {
        # .tmp konnte nicht geschrieben werden - alten Zustand nicht stehen lassen
        if (Test-Path -LiteralPath $stateFile -PathType Leaf) { [System.IO.File]::Delete($stateFile) }
    } elseif ($total -gt 0) {
        [System.IO.File]::Copy($stateTmp, $stateFile, $true)
        [System.IO.File]::Delete($stateTmp)
    } elseif (Test-Path -LiteralPath $stateFile -PathType Leaf) {
        [System.IO.File]::Delete($stateFile)
    }
    if ($total -eq 0 -and (Test-Path -LiteralPath $stateTmp -PathType Leaf)) { [System.IO.File]::Delete($stateTmp) }
} catch {
    $stateWarn = $_.Exception.Message
}

Write-Host ''
Say '============================================' 'Green'
if ($total -eq 0) {
    Say (T 'DoneOrig') 'Green'
} else {
    Say (T 'Done1') 'Green'
    if ($patchedMode) {
        Say (T 'Done3' $added.Count $changed.Count $removed.Count $total) 'Green'
    } else {
        Say (T 'Done2' $total) 'Green'
    }
}
Say '============================================' 'Green'
if ($stateWarn -and $total -gt 0) {
    Write-Host ''
    Say (T 'StateWarn1') 'Yellow'
    Say $stateWarn 'Yellow'
    Say (T 'StateWarn2') 'Yellow'
} elseif ($total -gt 0) {
    Write-Host ''
    Say (T 'StateSaved') 'DarkGray'
}
Exit-Patcher 0

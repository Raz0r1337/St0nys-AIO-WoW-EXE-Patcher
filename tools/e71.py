R('''function Test-ClientIcon([string]$v) {''','''# Fuer die Erkennung ueber das Wasserzeichen: Der Pfad selbst steht nicht in
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

function Test-ClientIcon([string]$v) {''')
R('''       Default = ''
       Check = { param($v) Test-ClientIcon $v }
       Code = {
        # Nach edit_icon.py (MacWarrior), hier ohne Windows-API: Die acht''','''       Default = ''
       Check = { param($v) Test-ClientIcon $v }
       Decode = { Get-ClientIconFromExe }
       Code = {
        # Nach edit_icon.py (MacWarrior), hier ohne Windows-API: Die acht''')

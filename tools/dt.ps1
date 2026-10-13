$f = [System.IO.File]::ReadAllBytes('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/bt/Wow.exe.BAK')
$t = [System.Text.Encoding]::ASCII.GetString($f, 0x5F39F4, 11)
"[$t]"
$script:f = $f
$settingsFile = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/bt/patcher_selection.ini'
function Get-SavedValues {
    $vals = @{}
    if (-not (Test-Path -LiteralPath $settingsFile -PathType Leaf)) { return $vals }
    try { $lines = [System.IO.File]::ReadAllLines($settingsFile) } catch { return $vals }
    foreach ($l in $lines) {
        if ($l -match '^\s*value\.([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$') { $vals[$matches[1]] = $matches[2] }
    }
    return $vals
}
function Get-ClientDateFromExe {
    $t = [System.Text.Encoding]::ASCII.GetString($script:f, 0x5F39F4, 11)
    if ($t -notmatch '^([A-Za-z]{3}) (\d{2}) (\d{4})$') { return $null }
    $en = @('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    $fr = @('Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec')
    $m = [array]::IndexOf($en, $matches[1]); $suffix = ''
    "m=$m matches1=$($matches[1])"
    if ($m -lt 0) { $m = [array]::IndexOf($fr, $matches[1]); $suffix = ' FR' }
    if ($m -lt 0) { return $null }
    "before saved: m=$m"
    $sv = (Get-SavedValues)['clientdate']
    "saved=[$sv]"
    if ($suffix -eq '' -and $fr[$m] -eq $en[$m] -and ($sv -match '\sFR\s*$')) { $suffix = ' FR' }
    "after: m=$m matches3=$($matches[3]) matches2=$($matches[2])"
    return ('{0}-{1:00}-{2}{3}' -f $matches[3], ($m + 1), $matches[2], $suffix)
}
Get-ClientDateFromExe

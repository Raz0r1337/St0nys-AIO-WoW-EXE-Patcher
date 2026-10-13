param([string]$f)
$t = $null; $e = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile($f, [ref]$t, [ref]$e)
foreach ($x in $e) { $x.Message + ' @ ' + $x.Extent.StartLineNumber }
'Parser-Fehler: ' + @($e).Count

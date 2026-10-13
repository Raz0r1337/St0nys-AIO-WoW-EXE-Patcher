$scriptDir = $PSScriptRoot
function RU32([byte[]]$a, [int]$o) { return [int64][BitConverter]::ToUInt32($a, $o) }
function RU16([byte[]]$a, [int]$o) { return [int][BitConverter]::ToUInt16($a, $o) }
function L([string]$de, [string]$en) { return $de }
function Patch($o,$b) { }
function Assert-Bytes { }
$script:f = New-Object byte[] 10
. ..\icon_helpers.ps1
$a = [byte[]](0x00,0x00,0x00,0x0D,0x49)
"BE32 test: $(BE32 $a 0) (expect 13)"
$d = [System.IO.File]::ReadAllBytes("$PSScriptRoot/test.png")
try { $img = Read-PngImage $d; "png ok $($img.W)x$($img.H) px0=$($img.Px[0]),$($img.Px[1]),$($img.Px[2]),$($img.Px[3])" } catch { "PNG ERR: $($_.Exception.Message) at $($_.InvocationInfo.ScriptLineNumber): $($_.InvocationInfo.Line.Trim())" }
try { $imgs = Read-IconFile "$PSScriptRoot/test.ico"; "ico ok: $($imgs.Count) images: " + (($imgs | ForEach-Object { "$($_.W)x$($_.H)" }) -join ' ') } catch { "ICO ERR: $($_.Exception.Message) at $($_.InvocationInfo.ScriptLineNumber): $($_.InvocationInfo.Line.Trim())" }
$script:f = [System.IO.File]::ReadAllBytes('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe')
function Patch([int64]$offset, [byte[]]$bytes) { "patch $offset len $($bytes.Length)" }
function Assert-Bytes([int64]$Off, [byte[]]$Expected, [string]$What) { }
try { Set-ClientIcon 'test.png'; 'set ok' } catch { "SET ERR: $($_.Exception.Message) at $($_.InvocationInfo.ScriptLineNumber): $($_.InvocationInfo.Line.Trim())" }

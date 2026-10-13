$ast = [System.Management.Automation.Language.Parser]::ParseFile("$PWD/apply_patches.ps1", [ref]$null, [ref]$null)
$want = 'RU32','RU16','ConvertTo-FileOffset','Get-IconDibLength','Get-IconResourceSlots'
foreach ($fd in $ast.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true)) {
    if ($want -contains $fd.Name) { . ([scriptblock]::Create($fd.Extent.Text)) }
}
$script:f = [System.IO.File]::ReadAllBytes('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe')
"orig: " + ((Get-IconResourceSlots) -join ' ')
# Groesse des ersten 48er-Eintrags im Datenverzeichnis-Blatt verfaelschen
$need = '{0}/{1}' -f 0x74ED84, 9640
$res = Get-IconResourceSlots; "contains 48/1024: " + $res.Contains($need)
# Blatt suchen: Data-Entry mit RVA des Slots
$rva = 0x74ED84 - 0x72E000 + 0x9D3000
for ($o = 0x72E000; $o -lt 0x757C00; $o += 4) { if ([BitConverter]::ToUInt32($script:f, $o) -eq $rva) { $leaf = $o; break } }
"leaf at 0x{0:X}" -f $leaf
[Array]::Copy([BitConverter]::GetBytes([uint32]9000), 0, $script:f, $leaf + 4, 4)
"after tamper contains: " + (Get-IconResourceSlots).Contains($need)

# ============================================================
#  mod-voicechat - Standalone voice.dll loader patcher
#  SPDX-License-Identifier: GPL-2.0-or-later
#
#  DE: Patcht Wow.exe im aktuellen Ordner (oder -Path), legt vorher
#      Wow.exe.voice.BAK an. Laeuft auf original oder bereits gepatchter EXE.
#  EN: Patches Wow.exe in the current folder (or -Path), creates
#      Wow.exe.voice.BAK first. Works on original or already patched EXEs.
# ============================================================
param(
    [string]$Path = 'Wow.exe',
    [string]$DllName = 'voice.dll'
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Add-VoiceLoader.ps1')

if (-not (Test-Path -LiteralPath $Path)) {
    Write-Host "  [FEHLER/ERROR] $Path nicht gefunden / not found."
    exit 1
}
$full = (Resolve-Path -LiteralPath $Path).Path

try {
    $bytes = [System.IO.File]::ReadAllBytes($full)
    if (-not (Add-VoiceLoader -Image $bytes -DllName $DllName)) { exit 0 }   # bereits gepatcht / already patched

    $bak = "$full.voice.BAK"
    if (-not (Test-Path -LiteralPath $bak)) { Copy-Item -LiteralPath $full -Destination $bak }
    [System.IO.File]::WriteAllBytes($full, $bytes)
    Write-Host "  [OK] $DllName wird beim Start geladen / is loaded at startup. Backup: $bak"
    exit 0
}
catch {
    Write-Host "  [FEHLER/ERROR] $($_.Exception.Message)"
    exit 1
}

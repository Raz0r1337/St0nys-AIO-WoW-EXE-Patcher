import sys
p=sys.argv[1]; raw=open(p,'rb').read()
assert b'\r\n' in raw and raw.count(b'\n')==raw.count(b'\r\n')
def rep(a,b):
    global raw
    a=a.replace(b'\n',b'\r\n'); b=b.replace(b'\n',b'\r\n')
    assert raw.count(a)==1,a[:60]; raw=raw.replace(a,b)
rep(b"""$scriptDir = Split-Path -Parent $scriptPath
if (-not $Path) {
    $Path = Join-Path $scriptDir 'Wow.exe'
} elseif""",b"""$scriptDir = Split-Path -Parent $scriptPath
$wowHits = @()
if (-not $Path) {
    $Path = Join-Path $scriptDir 'Wow.exe'
    # Linux unterscheidet Gross-/Kleinschreibung: dann auch WoW.exe, wow.exe
    # usw. finden. Unter Windows passt immer schon der Pfad oben. Liegen
    # mehrere Schreibweisen im Ordner, bricht der Patcher weiter unten ab.
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        $wowHits = @(Get-ChildItem -LiteralPath $scriptDir -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ieq 'Wow.exe' })
        if ($wowHits.Count -eq 1) { $Path = $wowHits[0].FullName }
    }
} elseif""")
rep(b"""        NotFound      = '[FEHLER] Keine Wow.exe gefunden: {0}'
""",b"""        NotFound      = '[FEHLER] Keine Wow.exe gefunden: {0}'
        WowMulti      = '[FEHLER] Mehrere Wow.exe in unterschiedlicher Schreibweise gefunden: {0} - bitte nur eine davon im Ordner lassen oder die richtige mit -Path angeben.'
""")
rep(b"""        NotFound      = '[ERROR] No Wow.exe found: {0}'
""",b"""        NotFound      = '[ERROR] No Wow.exe found: {0}'
        WowMulti      = '[ERROR] Several Wow.exe with different spelling found: {0} - please keep only one of them in the folder or pass the right one with -Path.'
""")
rep(b"""if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
    Say (T 'NotFound' $file) 'Red'
    Exit-Patcher 1
}
""",b"""if ($wowHits.Count -gt 1) {
    Say (T 'WowMulti' (($wowHits | ForEach-Object { $_.Name }) -join ', ')) 'Red'
    Exit-Patcher 1
}
if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
    Say (T 'NotFound' $file) 'Red'
    Exit-Patcher 1
}
""")
assert all(c<128 for c in raw)
open(p,'wb').write(raw); print('ok')

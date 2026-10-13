P='/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1'
s=open(P,newline='').read().replace('\r\n','\n')
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80])
    s=s.replace(a,b)
# --- StartWarn ---
rep("""        StartWarn1    = 'HINWEIS: Die meisten Patches sind im Spiel getestet. Solange keiner gewaehlt ist,'
        StartWarn2    = 'der als Bann-Gefahr markiert ist oder die Wow.exe vergroessert, sollte auch auf'
        StartWarn3    = 'oeffentlichen Servern nichts passieren - eine 100%-Garantie gibt es aber nicht.'
""","""        StartWarn1    = 'HINWEIS: Patches ohne Warnung in eckigen Klammern sind im Spiel getestet und sollten auch'
        StartWarn2    = 'auf oeffentlichen Servern unbedenklich sein - eine 100%-Garantie gibt es aber nicht.'
        StartWarn3    = 'Warnungen: [Bann-Gefahr], [auf oeffentlichen Servern ungetestet] (Vorsicht, kann zu Kick/Bann'
        StartWarn6    = 'fuehren), [im Spiel ungetestet] (moeglicherweise verbuggt), [Exe wird groesser] (Bann-Gefahr).'
""")
rep("""        StartWarn1    = 'NOTE: Most patches have been tested in game. As long as none is selected that'
        StartWarn2    = 'is marked as a ban risk or makes Wow.exe larger, nothing should happen on'
        StartWarn3    = 'public servers either - but there is no 100% guarantee.'
""","""        StartWarn1    = 'NOTE: Patches without a warning in square brackets have been tested in game and should be'
        StartWarn2    = 'harmless on public servers as well - but there is no 100% guarantee.'
        StartWarn3    = 'Warnings: [ban risk], [untested on public servers] (careful, may get you kicked/banned),'
        StartWarn6    = '[untested in game] (possibly buggy), [exe grows] (ban risk).'
""")
rep("""Say (T 'StartWarn3') 'Yellow'
""","""Say (T 'StartWarn3') 'Yellow'
Say (T 'StartWarn6') 'Yellow'
""")
# --- summary texts ---
rep("""        CheatHead     = 'HINWEIS: Diese Patches koennen von Servern mit Anti-Cheat als Cheat oder Botting gewertet werden:'
        DllHint       = 'HINWEIS: Der Patch selbst ist unkritisch. Erst die geladene DLL kann auf Servern mit Anti-Cheat auffallen - nur dort einsetzen, wo {0} erlaubt ist.'
        CheatBan      = 'Das kann zu einem Bann fuehren - nur auf Servern nutzen, die das erlauben!'
""","""        CheatHead     = 'ACHTUNG - Bann-Gefahr: Diese Patches koennen von Servern als Cheat oder Botting gewertet werden:'
        CheatBan      = 'Das kann zu einem Bann fuehren - nur auf Servern nutzen, die das erlauben!'
        PublicHead    = 'VORSICHT: Diese Patches sind nicht auf oeffentlichen Servern getestet - moegliche Bann-Gefahr:'
        PublicBan     = 'Sie koennen zu einem Kick oder Bann fuehren.'
        UntestedHead  = 'HINWEIS: Die Funktion dieser Patches ist im Spiel ungetestet - moeglicherweise verbuggt:'
        TagBan        = 'Bann-Gefahr'
        TagPublic     = 'auf oeffentlichen Servern ungetestet'
        TagGame       = 'im Spiel ungetestet'
        TagBoth       = 'auf oeffentlichen Servern und im Spiel ungetestet'
        TagGrow       = 'Exe wird groesser'
""")
rep("""        CheatHead     = 'NOTE: Servers with anti-cheat may treat these patches as cheating or botting:'
        DllHint       = 'NOTE: The patch itself is harmless. Only the loaded DLL may be noticed by servers with anti-cheat - use it only where {0} is allowed.'
        CheatBan      = 'This can lead to a ban - only use them on servers that allow it!'
""","""        CheatHead     = 'WARNING - ban risk: servers may treat these patches as cheating or botting:'
        CheatBan      = 'This can lead to a ban - only use them on servers that allow it!'
        PublicHead    = 'CAUTION: these patches have not been tested on public servers - possible ban risk:'
        PublicBan     = 'They may get you kicked or banned.'
        UntestedHead  = 'NOTE: these patches have not been tested in game - possibly buggy:'
        TagBan        = 'ban risk'
        TagPublic     = 'untested on public servers'
        TagGame       = 'untested in game'
        TagBoth       = 'untested on public servers and in game'
        TagGrow       = 'exe grows'
""")
# --- PatchName ---
rep("""    if ($note) { $n = "$n ($note)" }
    return $n
}
""","""    if ($note) { $n = "$n ($note)" }
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
""")
# --- field doc ---
rep("""#    GrowsExe - optional: $true, wenn der Patch immer eine Sektion anhaengt und
#            die Wow.exe damit groesser macht (erzeugt einen Bann-Hinweis)
#    BanRisk - optional: $true, wenn Server mit Anti-Cheat den Patch als Cheat
#            oder Botting werten koennen (erzeugt einen roten Bann-Hinweis)
#    DllHint - optional: Name des DLL-Projekts fuer den DLL-Loader - dezenter
#            gelber Hinweis, dass erst die geladene DLL auffallen kann
""","""#    GrowsExe - optional: $true, wenn der Patch immer eine Sektion anhaengt und
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
""")
# --- summary ---
rep("""foreach ($p in $chosen) {
    if ($p.DllHint) {
        Write-Host ''
        Say (T 'HintHead' (PatchRef $p)) 'Yellow'
        Say (T 'DllHint' $p.DllHint) 'Yellow'
    }
}
$cheat = @()
foreach ($p in $chosen) { if ($p.BanRisk) { $cheat += PatchRef $p } }
if ($cheat.Count -gt 0) {
    Write-Host ''
    Say (T 'CheatHead') 'Yellow'
    foreach ($m in $cheat) { Say "  - $m" 'Yellow' }
    Say (T 'CheatBan') 'Red'
}
""","""$untested = @()
foreach ($p in $chosen) { if ($p.GameUntested) { $untested += PatchRef $p } }
if ($untested.Count -gt 0) {
    Write-Host ''
    Say (T 'UntestedHead') 'Yellow'
    foreach ($m in $untested) { Say "  - $m" 'Yellow' }
}
$public = @()
foreach ($p in $chosen) { if ($p.PublicUntested) { $public += PatchRef $p } }
if ($public.Count -gt 0) {
    Write-Host ''
    Say (T 'PublicHead') 'Yellow'
    foreach ($m in $public) { Say "  - $m" 'Yellow' }
    Say (T 'PublicBan') 'Yellow'
}
$cheat = @()
foreach ($p in $chosen) { if ($p.BanRisk) { $cheat += PatchRef $p } }
if ($cheat.Count -gt 0) {
    Write-Host ''
    Say (T 'CheatHead') 'Red'
    foreach ($m in $cheat) { Say "  - $m" 'Red' }
    Say (T 'CheatBan') 'Red'
}
""")
open(P,'w',newline='').write(s.replace('\n','\r\n'))

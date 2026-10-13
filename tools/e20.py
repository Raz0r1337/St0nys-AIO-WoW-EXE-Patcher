R("""    @{ Id = 'awesome'; Cat = 'modding'; On = $true; Needs = @('laa'); BanRisk = $true
       Author = 'FrostAtom'
       De = 'AwesomeWotlkLib.dll Unterstuetzung aktivieren'
       En = 'Enable AwesomeWotlkLib.dll support'
       NoteDe = 'benoetigt awesome_wotlk - Bann-Gefahr'
       NoteEn = 'requires awesome_wotlk - ban risk'
""", """    @{ Id = 'awesome'; Cat = 'modding'; On = $true; Needs = @('laa'); DllHint = $true
       Author = 'FrostAtom'
       De = 'AwesomeWotlkLib.dll Unterstuetzung aktivieren'
       En = 'Enable AwesomeWotlkLib.dll support'
       NoteDe = 'benoetigt awesome_wotlk'
       NoteEn = 'requires awesome_wotlk'
""")
R("""        CheatHead     = 'HINWEIS: Diese Patches koennen von Servern mit Anti-Cheat als Cheat, Botting oder unerlaubte DLL gewertet werden:'
""", """        CheatHead     = 'HINWEIS: Diese Patches koennen von Servern mit Anti-Cheat als Cheat oder Botting gewertet werden:'
        DllHint       = 'HINWEIS: Der Patch selbst ist unkritisch. Erst die geladene DLL kann auf Servern mit Anti-Cheat auffallen - nur dort einsetzen, wo awesome_wotlk erlaubt ist.'
""")
R("""        CheatHead     = 'NOTE: Servers with anti-cheat may treat these patches as cheating, botting or an unauthorized DLL:'
""", """        CheatHead     = 'NOTE: Servers with anti-cheat may treat these patches as cheating or botting:'
        DllHint       = 'NOTE: The patch itself is harmless. Only the loaded DLL may be noticed by servers with anti-cheat - use it only where awesome_wotlk is allowed.'
""")
R("""#    BanRisk - optional: $true, wenn Server mit Anti-Cheat den Patch als Cheat
#            oder Botting werten koennen (erzeugt einen Bann-Hinweis)
""", """#    BanRisk - optional: $true, wenn Server mit Anti-Cheat den Patch als Cheat
#            oder Botting werten koennen (erzeugt einen roten Bann-Hinweis)
#    DllHint - optional: $true fuer den DLL-Loader - dezenter gelber Hinweis,
#            dass erst die geladene DLL auffallen kann
""")
R("""$cheat = @()
foreach ($p in $chosen) { if ($p.BanRisk) { $cheat += PatchName $p } }
""", """foreach ($p in $chosen) {
    if ($p.DllHint) {
        Write-Host ''
        Say (T 'HintHead' (PatchName $p)) 'Yellow'
        Say (T 'DllHint') 'Yellow'
    }
}
$cheat = @()
foreach ($p in $chosen) { if ($p.BanRisk) { $cheat += PatchName $p } }
""")

R("""    @{ Id = 'awesome'; Cat = 'modding'; On = $true; Needs = @('laa')
       Author = 'FrostAtom'
       De = 'AwesomeWotlkLib.dll Unterstuetzung aktivieren'
       En = 'Enable AwesomeWotlkLib.dll support'
       NoteDe = 'benoetigt awesome_wotlk'
       NoteEn = 'requires awesome_wotlk'
""", """    @{ Id = 'awesome'; Cat = 'modding'; On = $true; Needs = @('laa'); BanRisk = $true
       Author = 'FrostAtom'
       De = 'AwesomeWotlkLib.dll Unterstuetzung aktivieren'
       En = 'Enable AwesomeWotlkLib.dll support'
       NoteDe = 'benoetigt awesome_wotlk - Bann-Gefahr'
       NoteEn = 'requires awesome_wotlk - ban risk'
""")
R("""        CheatHead     = 'HINWEIS: Diese Patches koennen von Servern mit Anti-Cheat als Cheat oder Botting gewertet werden:'
""", """        CheatHead     = 'HINWEIS: Diese Patches koennen von Servern mit Anti-Cheat als Cheat, Botting oder unerlaubte DLL gewertet werden:'
""")
R("""        CheatHead     = 'NOTE: Servers with anti-cheat may treat these patches as cheating or botting:'
""", """        CheatHead     = 'NOTE: Servers with anti-cheat may treat these patches as cheating, botting or an unauthorized DLL:'
""")

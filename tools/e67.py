R('''        Welcome5      = 'Eingespielte Patches lassen sich spaeter wieder abwaehlen - bis zurueck zum Original.'
''','''        Welcome5      = 'Eingespielte Patches lassen sich spaeter wieder abwaehlen - bis zurueck zum Original.'
        StartWarn1    = 'ACHTUNG: Dieser Patcher ist ein Entwickler-Werkzeug fuer eigene Server, Modding und Tests.'
        StartWarn2    = 'Auf oeffentlichen Servern kann JEDER Patch gegen die Serverregeln verstossen und zu einem'
        StartWarn3    = 'BANN fuehren - auch Patches, die hier nicht als Bann-Gefahr markiert sind.'
        StartWarn4    = 'Pruefe die Richtlinien deines Servers, bevor du eine gepatchte Wow.exe dort benutzt.'
        StartWarn5    = 'Benutzung auf eigene Gefahr.'
''')
R('''        Welcome5      = 'Applied patches can be deselected later - all the way back to the original.'
''','''        Welcome5      = 'Applied patches can be deselected later - all the way back to the original.'
        StartWarn1    = 'WARNING: This patcher is a developer tool for your own servers, modding and testing.'
        StartWarn2    = 'On public servers ANY patch can violate the server rules and get you BANNED -'
        StartWarn3    = 'including patches that are not marked as a ban risk here.'
        StartWarn4    = 'Check the rules of your server before using a patched Wow.exe there.'
        StartWarn5    = 'Use at your own risk.'
''')
R('''Say (T 'Welcome4')
Say (T 'Welcome5')
Write-Host ''
Say (T 'Thanks') 'Magenta'
''','''Say (T 'Welcome4')
Say (T 'Welcome5')
Write-Host ''
Say (T 'StartWarn1') 'Red'
Say (T 'StartWarn2') 'Red'
Say (T 'StartWarn3') 'Red'
Say (T 'StartWarn4') 'Red'
Say (T 'StartWarn5') 'Red'
Write-Host ''
Say (T 'Thanks') 'Magenta'
''')

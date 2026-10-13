# Header: -Select
R('''#                             "saved" (gespeicherte Auswahl), "billy" (Preset
#                             Billy's_Wow.exe = Standard), "all", "none" (alle
#                             Patches zuruecknehmen) oder Nummern/Bereiche
#                             wie "1,3,5-8"''',
'''#                             "saved" (gespeicherte Auswahl), "billy" (Preset
#                             Billy's_Wow.exe = Standard), "stony" (Preset
#                             Billy's_Wow.exe (modded by St0ny)), "all", "none"
#                             (alle Patches zuruecknehmen) oder Nummern/Bereiche
#                             wie "1,3,5-8"''')
# Menu help DE
R('''        MenuHelp2     = 'A = alle an    N = alle aus    B = Preset Billy''s_Wow.exe    L = English    Q = abbrechen'
''',
'''        MenuHelp2     = 'A = alle an    N = alle aus    L = English    Q = abbrechen'
        MenuPresets   = 'B = Preset Billy''s_Wow.exe    S = Preset Billy''s_Wow.exe (modded by St0ny)'
''')
# Menu help EN
R('''        MenuHelp2     = 'A = all on    N = all off    B = preset Billy''s_Wow.exe    L = Deutsch    Q = quit'
''',
'''        MenuHelp2     = 'A = all on    N = all off    L = Deutsch    Q = quit'
        MenuPresets   = 'B = preset Billy''s_Wow.exe    S = preset Billy''s_Wow.exe (modded by St0ny)'
''')
# Field doc
R('''#    On    - Teil des Presets "Billy's_Wow.exe", das zugleich die Standard-
#            Auswahl ist: vorausgewaehlt ($true) oder nicht ($false)
''',
'''#    On    - Teil des Presets "Billy's_Wow.exe", das zugleich die Standard-
#            Auswahl ist: vorausgewaehlt ($true) oder nicht ($false). Das
#            zweite Preset "Billy's_Wow.exe (modded by St0ny)" steht als
#            Id-Liste in $PRESET_STONY hinter den Patches
''')
# Preset list after $patches
R('''    @{ Id = 'clientdate'; Cat = 'client'; On = $false
''', '''    @{ Id = 'clientdate'; Cat = 'client'; On = $false
''')

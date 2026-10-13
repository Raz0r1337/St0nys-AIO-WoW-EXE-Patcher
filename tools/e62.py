R('''        MenuPresets   = 'B = Preset Billy''s_Wow.exe    S = Preset Billy''s_Wow.exe (modded by St0ny)'
''','''        MenuPresets   = 'B = Preset Billy''s_Wow.exe    S = Preset Billy''s_Wow.exe (modded by St0ny) - noch ungetestet'
        StonyUntested = 'Achtung: Das Preset Billy''s_Wow.exe (modded by St0ny) ist noch ungetestet.'
''')
R('''        MenuPresets   = 'B = preset Billy''s_Wow.exe    S = preset Billy''s_Wow.exe (modded by St0ny)'
''','''        MenuPresets   = 'B = preset Billy''s_Wow.exe    S = preset Billy''s_Wow.exe (modded by St0ny) - not tested yet'
        StonyUntested = 'Warning: the preset Billy''s_Wow.exe (modded by St0ny) has not been tested yet.'
''')
R('''            '^[sS]$'   { $sel = Get-StonySelection; break }
''','''            '^[sS]$'   { $sel = Get-StonySelection; $message = T 'StonyUntested'; break }
''')

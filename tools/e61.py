R('''        Set-ClientDate $script:VALUES['clientdate']
    }}
)

# ============================================================
#  Original-Bytes je Patch''',
'''        Set-ClientDate $script:VALUES['clientdate']
    }}
)

# Zweites Preset "Billy's_Wow.exe (modded by St0ny)" - Billys Patch-Set plus
# RCE-Fix, Sicherheits- und Login-Patches, MPQ-Signatur, /follow, Level 101,
# Objektgroesse, Tracker, Weltkarte und Fenstermodus. Im Menue mit S, ueber
# -Select stony. Ids, die hier fehlen oder unbekannt sind, bleiben aus.
$PRESET_STONY = @(
    'laa', 'itemcache',
    'rce', 'scandll', 'noserverpatch', 'nosurvey',
    'skipbnet', 'skiprdp', 'nohttp',
    'glue', 'mpqsig', 'mpqnames', 'localdata', 'awesome',
    'areatrigger', 'swing', 'npcanim', 'spellanim', 'ghostattack', 'naked',
    'forcereaction', 'mail', 'deadchat', 'follow', 'level101', 'maxchars',
    'farclip', 'horizon', 'envdetail', 'grounddist', 'goscale',
    'bluemoon', 'notransparency',
    'tracker', 'worldmap', 'castbars', 'flash',
    'window', 'maximize', 'windowfix', 'mouse'
)

# ============================================================
#  Original-Bytes je Patch''')
R('''function Get-DefaultSelection {
    $sel = New-Object bool[] $patches.Count
    for ($i = 0; $i -lt $patches.Count; $i++) { $sel[$i] = [bool]$patches[$i].On }
    return , $sel
}
''',
'''function Get-DefaultSelection {
    $sel = New-Object bool[] $patches.Count
    for ($i = 0; $i -lt $patches.Count; $i++) { $sel[$i] = [bool]$patches[$i].On }
    return , $sel
}

# Preset "Billy's_Wow.exe (modded by St0ny)" aus der Id-Liste $PRESET_STONY
function Get-StonySelection {
    $sel = New-Object bool[] $patches.Count
    for ($i = 0; $i -lt $patches.Count; $i++) { $sel[$i] = $PRESET_STONY -contains $patches[$i].Id }
    return , $sel
}
''')
R('''    Say (T 'MenuHelp2')
    Say (T 'MenuHelp3')
''', '''    Say (T 'MenuHelp2')
    Say (T 'MenuPresets')
    Say (T 'MenuHelp3')
''')
R('''            '^[bB]$'   { $sel = Get-DefaultSelection; break }
''', '''            '^[bB]$'   { $sel = Get-DefaultSelection; break }
            '^[sS]$'   { $sel = Get-StonySelection; break }
''')
R('''    if ($v -eq 'billy' -or $v -eq 'default' -or $v -eq 'standard') { return , (Get-DefaultSelection) }
''', '''    if ($v -eq 'billy' -or $v -eq 'default' -or $v -eq 'standard') { return , (Get-DefaultSelection) }
    if ($v -eq 'stony' -or $v -eq 'st0ny') { return , (Get-StonySelection) }
''')

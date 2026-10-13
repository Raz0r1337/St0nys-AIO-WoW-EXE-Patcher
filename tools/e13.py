R("""function Add-CodeSection([string]$Name, [int]$Size) {""", """function Add-CodeSection([string]$Name, [int]$Size, [switch]$Writable) {""")
R("""    [Array]::Copy([byte[]](0x20, 0x00, 0x00, 0x60), 0, $sh, 36, 4)     # 0x60000020 = Code | ausfuehrbar | lesbar
""", """    if ($Writable) {
        [Array]::Copy([byte[]](0x20, 0x00, 0x00, 0xE0), 0, $sh, 36, 4) # 0xE0000020 = Code | ausfuehrbar | lesbar | schreibbar
    } else {
        [Array]::Copy([byte[]](0x20, 0x00, 0x00, 0x60), 0, $sh, 36, 4) # 0x60000020 = Code | ausfuehrbar | lesbar
    }
""")
R("""# ============================================================
#  Helfer fuer den Sprunghoehen-Patch
""", r"""# ============================================================
#  Doppelsprung (nach 0x539wowmod, Alyst3r)
#  Die Sprungfunktion (VA 0x9883F0) lehnt bei VA 0x98842A jeden Sprung ab,
#  solange eines der Flags ROOT (0x800), FALLING (0x1000) oder FLYING
#  (0x2000000) gesetzt ist. 0x539wowmod ersetzt sie per DLL und zaehlt
#  Sprungladungen mit. Hier dasselbe als Code-Hoehle: Beim Sprung vom Boden
#  wird der Zaehler auf N gesetzt, in der Luft ist ein Sprung erlaubt,
#  solange der Zaehler > 0 ist (dann -1). ROOT und FLYING sperren weiter.
#  Der Zaehler ist ein Byte in derselben Sektion, die darum beschreibbar
#  sein muss - deshalb eine eigene Sektion (.djump) statt der Luecke in .text.
# ============================================================
function Add-DoubleJump([int]$Extra) {
    $HOOK_VA = 0x98842A; $OK_VA = 0x988435; $FAIL_VA = 0x988479
    Assert-Bytes ($HOOK_VA - 0x400C00) @(0x8B, 0x7E, 0x44, 0xF7, 0xC7, 0x00, 0x18, 0x00, 0x02, 0x75, 0x44) 'Doppelsprung'
    $loc = Add-CodeSection '.djump' 0x44 -Writable
    $CAVE = $loc[0]; $DATA = $CAVE + 0x40
    $c = New-Object System.Collections.Generic.List[byte]
    AddRaw $c @(0x8B, 0x7E, 0x44)                                  # mov edi, [esi+44h]      (Original)
    AddRaw $c @(0xF7, 0xC7, 0x00, 0x10, 0x00, 0x00)                # test edi, 1000h         (in der Luft?)
    AddRaw $c @(0x75, 0x14)                                        # jnz Luft
    AddRaw $c @(0xC6, 0x05); AddLE32 $c $DATA; AddRaw $c @([byte]$Extra)   # mov byte [Zaehler], N
    AddRaw $c @(0xF7, 0xC7, 0x00, 0x18, 0x00, 0x02)                # test edi, 2001800h      (Original)
    AddRaw $c @(0x75, 0x21)                                        # jnz Abbruch
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $OK_VA)        # jmp weiter
    # Luft:
    AddRaw $c @(0xF7, 0xC7, 0x00, 0x08, 0x00, 0x02)                # test edi, 2000800h      (ROOT/FLYING)
    AddRaw $c @(0x75, 0x14)                                        # jnz Abbruch
    AddRaw $c @(0x80, 0x3D); AddLE32 $c $DATA; AddRaw $c @(0x00)   # cmp byte [Zaehler], 0
    AddRaw $c @(0x74, 0x0B)                                        # je Abbruch
    AddRaw $c @(0xFE, 0x0D); AddLE32 $c $DATA                      # dec byte [Zaehler]
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $OK_VA)        # jmp weiter
    # Abbruch:
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $FAIL_VA)      # jmp Sprung ablehnen
    if ($c.Count -ne 0x40) { throw 'Doppelsprung: Hoehle hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    $hook = (Get-Rel32 @(0xE9) $HOOK_VA $CAVE) + [byte[]](0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    Patch ($HOOK_VA - 0x400C00) ([byte[]]$hook)
}

function Test-DoubleJump([string]$v) {
    if ($v -notmatch '^[1-9]$') { return (L 'Eine Zahl von 1 bis 9.' 'A number from 1 to 9.') }
    return $null
}

# ============================================================
#  Helfer fuer den Sprunghoehen-Patch
""")
i=s.index("    @{ Id = 'airturn';"); j=s.index("    }}\n", i)+len("    }}\n")
s=s[:j]+"""
    @{ Id = 'doublejump'; Cat = 'gameplay'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Doppelsprung (weitere Spruenge in der Luft) [TEST]'
       En = 'Double jump (more jumps in the air) [TEST]'
       NoteDe = 'kann vom Server als Cheat erkannt werden'
       NoteEn = 'may be detected as cheating by the server'
       PromptDe = 'Anzahl zusaetzlicher Spruenge in der Luft, 1 bis 9 (1 = Doppelsprung)'
       PromptEn = 'Number of extra jumps in the air, 1 to 9 (1 = double jump)'
       Default = '1'
       Check = { param($v) Test-DoubleJump $v }
       Code = {
        # Eigene beschreibbare Sektion (.djump), siehe Add-DoubleJump.
        Add-DoubleJump ([int]$script:VALUES['doublejump'])
    }}
"""+s[j:]

# ============================================================
#  Icons im Text pixelgenau (Hour of Twilight, ported by St0ny)
#  Texte koennen Icons enthalten (|T...|t, z.B. Raidmarker, Waehrungen,
#  Questsymbole). Ihre Groesse und Lage rechnet der Client in Pixeln mit
#  Nachkommastellen aus - bei skalierten Schriften landen die Icons dann
#  zwischen zwei Pixeln und werden unscharf oder um einen Pixel verzerrt.
#  Der Hook hinter ParseEmbeddedTexture (VA 0x6C0E80, cdecl: Text, Info,
#  Hoehe, Skalierung, Schrifthoehe) rundet - wenn das Parsen geklappt hat
#  und die Hoehe von der Schrifthoehe abweicht - Hoehe [Info+18h] und
#  Breite [Info+1Ch] auf ganze Pixel (mindestens 1) und den Versatz
#  [Info+20h] / [Info+24h] auf ganze Pixel. Gerundet wird wie im Fork mit
#  floor(x + 0,5): Rundungsmodus der FPU kurz auf "abrunden", danach wieder
#  zurueck. Eigene Sektion (.isnap), nur ausfuehrbar.
# ============================================================
function Add-IconPixelSnap {
    $PARSE = 0x6C0E80
    Assert-Bytes ($PARSE - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x44) 'Icons pixelgenau'
    $loc = Add-CodeSection '.isnap' 0xB3
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
    # snap:  Original aufrufen (Argumente neu ablegen), danach runden
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xFF, 0x74, 0x24, 0x18)                        # push dword ptr [esp+0x18]
    AddRaw $c @(0xE8, 0x8E, 0x00, 0x00, 0x00)                  # call tramp
    AddRaw $c @(0x83, 0xC4, 0x14)                              # add esp,0x14
    AddRaw $c @(0x84, 0xC0)                                    # test al,al
    AddRaw $c @(0x0F, 0x84, 0x81, 0x00, 0x00, 0x00)            # jz out
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xD9, 0x44, 0x24, 0x14)                        # fld dword ptr [esp+0x14]
    AddRaw $c @(0xD8, 0x5C, 0x24, 0x1C)                        # fcomp dword ptr [esp+0x1C]
    AddRaw $c @(0xDF, 0xE0)                                    # fnstsw ax
    AddRaw $c @(0x80, 0xE4, 0x45)                              # and ah,0x45
    AddRaw $c @(0x80, 0xFC, 0x40)                              # cmp ah,0x40
    AddRaw $c @(0x74, 0x6D)                                    # je out_pop
    AddRaw $c @(0x8B, 0x74, 0x24, 0x10)                        # mov esi,[esp+0x10]
    AddRaw $c @(0x83, 0xEC, 0x08)                              # sub esp,8
    AddRaw $c @(0xD9, 0x3C, 0x24)                              # fnstcw word ptr [esp]
    AddRaw $c @(0x66, 0x8B, 0x04, 0x24)                        # mov ax,word ptr [esp]
    AddRaw $c @(0x66, 0x25, 0xFF, 0xF3)                        # and ax,0xF3FF
    AddRaw $c @(0x66, 0x0D, 0x00, 0x04)                        # or ax,0x400
    AddRaw $c @(0x66, 0x89, 0x44, 0x24, 0x02)                  # mov word ptr [esp+2],ax
    AddRaw $c @(0xC7, 0x44, 0x24, 0x04, 0x00, 0x00, 0x00, 0x3F) # mov dword ptr [esp+4],0x3F000000
    AddRaw $c @(0xD9, 0x6C, 0x24, 0x02)                        # fldcw word ptr [esp+2]
    AddRaw $c @(0xD9, 0x46, 0x18)                              # fld dword ptr [esi+0x18]
    AddRaw $c @(0xD8, 0x44, 0x24, 0x04)                        # fadd dword ptr [esp+4]
    AddRaw $c @(0xD9, 0xFC)                                    # frndint
    AddRaw $c @(0xD9, 0xE8)                                    # fld1
    AddRaw $c @(0xDB, 0xF1)                                    # fcomi st(0),st(1)
    AddRaw $c @(0xDA, 0xD1)                                    # fcmovbe st(0),st(1)
    AddRaw $c @(0xD9, 0x5E, 0x18)                              # fstp dword ptr [esi+0x18]
    AddRaw $c @(0xDD, 0xD8)                                    # fstp st(0)
    AddRaw $c @(0xD9, 0x46, 0x1C)                              # fld dword ptr [esi+0x1C]
    AddRaw $c @(0xD8, 0x44, 0x24, 0x04)                        # fadd dword ptr [esp+4]
    AddRaw $c @(0xD9, 0xFC)                                    # frndint
    AddRaw $c @(0xD9, 0xE8)                                    # fld1
    AddRaw $c @(0xDB, 0xF1)                                    # fcomi st(0),st(1)
    AddRaw $c @(0xDA, 0xD1)                                    # fcmovbe st(0),st(1)
    AddRaw $c @(0xD9, 0x5E, 0x1C)                              # fstp dword ptr [esi+0x1C]
    AddRaw $c @(0xDD, 0xD8)                                    # fstp st(0)
    AddRaw $c @(0xD9, 0x46, 0x20)                              # fld dword ptr [esi+0x20]
    AddRaw $c @(0xD8, 0x44, 0x24, 0x04)                        # fadd dword ptr [esp+4]
    AddRaw $c @(0xD9, 0xFC)                                    # frndint
    AddRaw $c @(0xD9, 0x5E, 0x20)                              # fstp dword ptr [esi+0x20]
    AddRaw $c @(0xD9, 0x46, 0x24)                              # fld dword ptr [esi+0x24]
    AddRaw $c @(0xD8, 0x44, 0x24, 0x04)                        # fadd dword ptr [esp+4]
    AddRaw $c @(0xD9, 0xFC)                                    # frndint
    AddRaw $c @(0xD9, 0x5E, 0x24)                              # fstp dword ptr [esi+0x24]
    AddRaw $c @(0xD9, 0x2C, 0x24)                              # fldcw word ptr [esp]
    AddRaw $c @(0x83, 0xC4, 0x08)                              # add esp,8
    # out_pop:
    AddRaw $c @(0x58)                                          # pop eax
    # out:
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0xC3)                                          # ret
    # tramp: ueberschriebene Befehle, weiter im Original
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x44)                              # sub esp,0x44
    AddRaw $c @(0xE9); AddLE32 $c (0x6C0E86 - ($CAVE + 0xB3))  # jmp 0x6C0E86  (ParseEmbeddedTexture+6)
    if ($c.Count -ne 0xB3) { throw 'Icons pixelgenau: Sektion hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    Patch ($PARSE - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $PARSE ($CAVE + 0x0)) + [byte[]](0x90)))
}

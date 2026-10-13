# ============================================================
#  Schrift-Glyphen-Fix (Hour of Twilight, ported by St0ny)
#  Blizzard-Fehler im Glyphen-Cache: Texte (vor allem Zahlen, Schaden,
#  Chat) zeigen zeitweise falsche, abgeschnittene oder fremde Zeichen.
#  Der Cache legt die gerenderten Zeichen auf 256 Pixel breiten Zeilen
#  von Textur-Seiten ab und verdraengt alte, wenn er voll ist. Dabei
#  passieren mehrere Fehler, die WotLK-Extensions (Hour of Twilight)
#  per DLL behebt - hier dasselbe in einer eigenen Sektion (.glyph):
#  - CreateNewDesc (VA 0x6C5120): Der Merker "breiteste freie Luecke"
#    einer Zeile ([Zeile+0]) wird nie aktualisiert. Der Hook rechnet ihn
#    vor jedem Einfuegen aus der Zeichenliste der Zeile neu aus
#    (Knoten: Start +30h, Ende +34h, naechster [Knoten+Linkoffset+4]).
#  - ClearInstanceData (VA 0x6C6B90): Die Merker "benutzte Seiten" (+60h)
#    und "Seite verdraengt" (+64h) des Strings bleiben stehen - werden
#    jetzt mit geloescht. Die Original-Funktion liest beide nicht.
#  - CheckGeometry (VA 0x6C7480, an Ort und Stelle neu geschrieben): Ist
#    eine Seite des Strings verdraengt worden, wird er immer komplett
#    geloescht und neu aufgebaut (das Original prueft vorher noch die
#    Schrift und baut dann mit alten Daten weiter).
#  - RenderBatch (VA 0x6C4AD0): Vor dem Zeichnen werden alle Strings des
#    Batches neu aufgebaut; verdraengt das einen anderen String, folgen
#    bis zu drei weitere Durchgaenge nur fuer die verdraengten.
#  - TextureCallback (VA 0x6C9F50): Beim Hochladen einer Seite (Befehl 1)
#    wird der Upload-Puffer (VA 0xC7D328, 128 KB) erst geleert, sonst
#    landen Reste alter Zeichen auf der neuen Seite.
#  Code-Sprungadressen werden beim Patchen aus der Lage der Sektion
#  berechnet ($CAVE). Die Sektion ist nur ausfuehrbar, nicht beschreibbar.
# ============================================================
function Add-GlyphCacheFix {
    $NEWDESC = 0x6C5120; $CLEAR = 0x6C6B90; $CHECK = 0x6C7480; $RENDER = 0x6C4AD0; $TEXCB = 0x6C9F50
    Assert-Bytes ($NEWDESC - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C) 'Glyphen-Fix'
    Assert-Bytes ($CLEAR - 0x400C00) @(0x56, 0x57, 0x8B, 0xF1, 0x6A, 0x00) 'Glyphen-Fix'
    Assert-Bytes ($CHECK - 0x400C00) @(0x56, 0x8B, 0xF1, 0x83, 0x7E, 0x64, 0x00, 0x74, 0x1E, 0x8B, 0x46, 0x48, 0x8B, 0x4E, 0x44, 0x50, 0xE8, 0x0B, 0xB5, 0xFF, 0xFF, 0x85, 0xC0, 0x75, 0x07, 0x8B, 0xCE, 0xE8, 0xF0, 0xF6, 0xFF, 0xFF, 0xC7, 0x46, 0x64, 0x00, 0x00, 0x00, 0x00, 0x8B, 0xCE, 0xE8, 0x62, 0x06, 0x00, 0x00, 0x33, 0xC0, 0x39, 0x86, 0xB0, 0x00, 0x00, 0x00, 0xC7, 0x86, 0xD4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x95, 0xC0, 0x5E, 0xC3) 'Glyphen-Fix'
    Assert-Bytes ($RENDER - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x20) 'Glyphen-Fix'
    Assert-Bytes ($TEXCB - 0x400C00) @(0x55, 0x8B, 0xEC, 0x51, 0x83, 0x7D, 0x08, 0x01) 'Glyphen-Fix'
    $loc = Add-CodeSection '.glyph' 0xDF
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]

    # --- CreateNewDesc (VA 0x6C5120), ecx = Zeile: breiteste freie Luecke neu berechnen ---
    # newdesc:
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0x31, 0xD2)                                    # xor edx,edx
    AddRaw $c @(0x8B, 0x71, 0x0C)                              # mov esi,[ecx+0xC]
    AddRaw $c @(0x8B, 0x79, 0x04)                              # mov edi,[ecx+4]
    # nd_loop:
    AddRaw $c @(0x85, 0xF6)                                    # test esi,esi
    AddRaw $c @(0x74, 0x21)                                    # jz nd_end
    AddRaw $c @(0xF7, 0xC6, 0x01, 0x00, 0x00, 0x00)            # test esi,1
    AddRaw $c @(0x75, 0x19)                                    # jnz nd_end
    AddRaw $c @(0x8B, 0x5E, 0x30)                              # mov ebx,[esi+0x30]
    AddRaw $c @(0x39, 0xD3)                                    # cmp ebx,edx
    AddRaw $c @(0x76, 0x08)                                    # jbe nd_skip
    AddRaw $c @(0x29, 0xD3)                                    # sub ebx,edx
    AddRaw $c @(0x39, 0xC3)                                    # cmp ebx,eax
    AddRaw $c @(0x76, 0x02)                                    # jbe nd_skip
    AddRaw $c @(0x89, 0xD8)                                    # mov eax,ebx
    # nd_skip:
    AddRaw $c @(0x8B, 0x56, 0x34)                              # mov edx,[esi+0x34]
    AddRaw $c @(0x42)                                          # inc edx
    AddRaw $c @(0x8B, 0x74, 0x3E, 0x04)                        # mov esi,[esi+edi+4]
    AddRaw $c @(0xEB, 0xDB)                                    # jmp nd_loop
    # nd_end:
    AddRaw $c @(0xBB, 0x00, 0x01, 0x00, 0x00)                  # mov ebx,0x100
    AddRaw $c @(0x39, 0xD3)                                    # cmp ebx,edx
    AddRaw $c @(0x76, 0x08)                                    # jbe nd_store
    AddRaw $c @(0x29, 0xD3)                                    # sub ebx,edx
    AddRaw $c @(0x39, 0xC3)                                    # cmp ebx,eax
    AddRaw $c @(0x76, 0x02)                                    # jbe nd_store
    AddRaw $c @(0x89, 0xD8)                                    # mov eax,ebx
    # nd_store:
    AddRaw $c @(0x89, 0x01)                                    # mov [ecx],eax
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x0C)                              # sub esp,0xC
    AddRaw $c @(0xE9); AddLE32 $c (0x6C5126 - ($CAVE + 0x53))  # jmp 0x6C5126  (CreateNewDesc+6)
    # --- ClearInstanceData (VA 0x6C6B90), ecx = String: Seiten-Merker loeschen ---
    # clear:
    AddRaw $c @(0x83, 0x61, 0x60, 0x00)                        # and dword ptr [ecx+0x60],0
    AddRaw $c @(0x83, 0x61, 0x64, 0x00)                        # and dword ptr [ecx+0x64],0
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x89, 0xCE)                                    # mov esi,ecx
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0xE9); AddLE32 $c (0x6C6B96 - ($CAVE + 0x66))  # jmp 0x6C6B96  (ClearInstanceData+6)
    # --- RenderBatch (VA 0x6C4AD0), ecx = Batch: Geometrie vor dem Zeichnen neu aufbauen ---
    # render:
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xCB)                                    # mov ebx,ecx
    AddRaw $c @(0x31, 0xED)                                    # xor ebp,ebp
    # rb_pass:
    AddRaw $c @(0x31, 0xFF)                                    # xor edi,edi
    AddRaw $c @(0x8B, 0x73, 0x24)                              # mov esi,[ebx+0x24]
    # rb_str:
    AddRaw $c @(0x85, 0xF6)                                    # test esi,esi
    AddRaw $c @(0x74, 0x25)                                    # jz rb_end
    AddRaw $c @(0xF7, 0xC6, 0x01, 0x00, 0x00, 0x00)            # test esi,1
    AddRaw $c @(0x75, 0x1D)                                    # jnz rb_end
    AddRaw $c @(0x8B, 0x46, 0x64)                              # mov eax,[esi+0x64]
    AddRaw $c @(0x85, 0xED)                                    # test ebp,ebp
    AddRaw $c @(0x74, 0x04)                                    # jz rb_do
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x74, 0x09)                                    # jz rb_next
    # rb_do:
    AddRaw $c @(0x09, 0xC7)                                    # or edi,eax
    AddRaw $c @(0x89, 0xF1)                                    # mov ecx,esi
    AddRaw $c @(0xE8); AddLE32 $c (0x6C7480 - ($CAVE + 0x93))  # call 0x6C7480  (CheckGeometry)
    # rb_next:
    AddRaw $c @(0x8B, 0x43, 0x1C)                              # mov eax,[ebx+0x1C]
    AddRaw $c @(0x8B, 0x74, 0x06, 0x04)                        # mov esi,[esi+eax+4]
    AddRaw $c @(0xEB, 0xD7)                                    # jmp rb_str
    # rb_end:
    AddRaw $c @(0x85, 0xFF)                                    # test edi,edi
    AddRaw $c @(0x74, 0x06)                                    # jz rb_out
    AddRaw $c @(0x45)                                          # inc ebp
    AddRaw $c @(0x83, 0xFD, 0x04)                              # cmp ebp,4
    AddRaw $c @(0x72, 0xC8)                                    # jb rb_pass
    # rb_out:
    AddRaw $c @(0x89, 0xD9)                                    # mov ecx,ebx
    AddRaw $c @(0x5D)                                          # pop ebp
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x20)                              # sub esp,0x20
    AddRaw $c @(0xE9); AddLE32 $c (0x6C4AD6 - ($CAVE + 0xB7))  # jmp 0x6C4AD6  (RenderBatch+6)
    # --- TextureCallback (VA 0x6C9F50, cdecl): Upload-Puffer vor dem Fuellen leeren ---
    # tex:
    AddRaw $c @(0x83, 0x7C, 0x24, 0x04, 0x01)                  # cmp dword ptr [esp+4],1
    AddRaw $c @(0x75, 0x14)                                    # jne tx_go
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x51)                                          # push ecx
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xBF, 0x28, 0xD3, 0xC7, 0x00)                  # mov edi,0xC7D328  (Glyphen-Upload-Puffer)
    AddRaw $c @(0xB9, 0x00, 0x80, 0x00, 0x00)                  # mov ecx,0x8000
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0xF3, 0xAB)                                    # rep stosd
    AddRaw $c @(0x58)                                          # pop eax
    AddRaw $c @(0x59)                                          # pop ecx
    AddRaw $c @(0x5F)                                          # pop edi
    # tx_go:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x51)                                          # push ecx
    AddRaw $c @(0x83, 0x7D, 0x08, 0x01)                        # cmp dword ptr [ebp+8],1
    AddRaw $c @(0xE9); AddLE32 $c (0x6C9F58 - ($CAVE + 0xDF))  # jmp 0x6C9F58  (TextureCallback+8)
    if ($c.Count -ne 0xDF) { throw 'Glyphen-Fix: Sektion hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    # Einspruenge: jmp in die Sektion, Rest der ueberschriebenen Befehle mit nop
    Patch ($NEWDESC - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $NEWDESC ($CAVE + 0x0)) + [byte[]](0x90)))
    Patch ($CLEAR - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $CLEAR ($CAVE + 0x53)) + [byte[]](0x90)))
    Patch ($RENDER - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $RENDER ($CAVE + 0x66)) + [byte[]](0x90)))
    Patch ($TEXCB - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $TEXCB ($CAVE + 0xB7)) + [byte[]](0x90, 0x90, 0x90)))
    # CheckGeometry neu (45 statt 69 Byte, Rest int3). Der Aufruf von
    # ClearInstanceData laeuft ueber den Hook oben und loescht +60h/+64h mit.
    $k = New-Object System.Collections.Generic.List[byte]

    AddRaw $k @(0x56)                                          # push esi
    AddRaw $k @(0x89, 0xCE)                                    # mov esi,ecx
    AddRaw $k @(0x83, 0x7E, 0x64, 0x00)                        # cmp dword ptr [esi+0x64],0
    AddRaw $k @(0x74, 0x07)                                    # je L
    AddRaw $k @(0x89, 0xF1)                                    # mov ecx,esi
    AddRaw $k @(0xE8, 0x00, 0xF7, 0xFF, 0xFF)                  # call 0x6C6B90  (ClearInstanceData)
    # L:
    AddRaw $k @(0x89, 0xF1)                                    # mov ecx,esi
    AddRaw $k @(0xE8, 0x79, 0x06, 0x00, 0x00)                  # call 0x6C7B10  (CreateGeometry)
    AddRaw $k @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $k @(0x89, 0x46, 0x64)                              # mov [esi+0x64],eax
    AddRaw $k @(0x89, 0x86, 0xD4, 0x00, 0x00, 0x00)            # mov [esi+0xD4],eax
    AddRaw $k @(0x39, 0x86, 0xB0, 0x00, 0x00, 0x00)            # cmp [esi+0xB0],eax
    AddRaw $k @(0x0F, 0x95, 0xC0)                              # setne al
    AddRaw $k @(0x5E)                                          # pop esi
    AddRaw $k @(0xC3)                                          # ret
    while ($k.Count -lt 69) { $k.Add([byte]0xCC) }
    Patch ($CHECK - 0x400C00) $k.ToArray()
}

# ============================================================
#  Aktionstasten gedrueckt halten zum Wiederholen (Hour of Twilight, ported by St0ny)
#  Haelt man die Taste einer Aktionsleisten-Belegung (ACTIONBUTTON1-12,
#  die Hauptleiste mit Seiten- und Bonusleisten-Wechsel wie im Fork),
#  loest der Client die Aktion wiederholt aus - wie in WotLK-Extensions
#  (Hour of Twilight) mit actionButtonHoldRepeat = 2 (dauerhaft):
#  - ExecKey (VA 0x563150): Beim Druecken merkt sich der Hook Taste,
#    Aktions-Slot und Zeit (bis 8 Tasten gleichzeitig). Beim Loslassen
#    wird der Eintrag geloescht; hat er schon wiederholt, unterdrueckt er
#    das normale Ausloesen beim Loslassen (UseAction-Hook).
#  - OnWorldRender (VA 0x4F8EA0): Nach jedem Bild prueft der Hook jede
#    gehaltene Taste: fruehestens 500 ms nach dem Druecken, nicht waehrend
#    eines Zaubers, nicht waehrend der Abklingzeit (GetCooldown, auch
#    globale), erst 100 ms nachdem die Aktion wieder bereit ist und
#    hoechstens alle 100 ms ruft er UseAction auf.
#  - Fokus-Ereignis (EventRegisterEx, Ereignis 2, beim ersten Druck
#    angemeldet): Verliert das Fenster den Fokus, werden alle gehaltenen
#    Tasten vergessen (sonst wiederholt es ohne Loslassen ewig).
#  Die Zustaende stehen in derselben Sektion (.hrep), die darum
#    beschreibbar sein muss: +0 acht Eintraege zu 32 Byte (Taste, Slot,
#  Druckzeit, letzte Wiederholung, bereit seit, wiederholt, aktiv),
#  +100h Unterdrueck-Merker, +104h Ereignis angemeldet, +108h GUID (0),
#  +110h leerer Text, +114h "ACTIONBUTTON". Code ab +120h.
# ============================================================
function Add-HoldRepeat {
    $EXEC = 0x563150; $USE = 0x5ABBC0; $RENDER = 0x4F8EA0
    Assert-Bytes ($EXEC - 0x400C00) @(0x55, 0x8B, 0xEC, 0x81, 0xEC, 0xC4, 0x00, 0x00, 0x00) 'Gedrueckt halten'
    Assert-Bytes ($USE - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C) 'Gedrueckt halten'
    Assert-Bytes ($RENDER - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x34) 'Gedrueckt halten'
    $loc = Add-CodeSection '.hrep' 0x473 -Writable
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
    for ($i = 0; $i -lt 0x114; $i++) { $c.Add([byte]0) }                 # Zustaende, beginnen bei 0
    AddRaw $c ([System.Text.Encoding]::ASCII.GetBytes('ACTIONBUTTON'))  # +114h, ohne Null

    # --- ExecKey (VA 0x563150, thiscall: mods, slot, isDown, argC, keyMode) ---
    # exec:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x81, 0xEC, 0x04, 0x01, 0x00, 0x00)            # sub esp,0x104
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x89, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov [ebp-0x104],ecx
    AddRaw $c @(0xC6, 0x85, 0x00, 0xFF, 0xFF, 0xFF, 0x00)      # mov byte ptr [ebp-0x100],0
    AddRaw $c @(0x68, 0x80, 0x00, 0x00, 0x00)                  # push 0x80
    AddRaw $c @(0x8D, 0x85, 0x00, 0xFF, 0xFF, 0xFF)            # lea eax,[ebp-0x100]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xFF, 0x75, 0x0C)                              # push dword ptr [ebp+0xC]
    AddRaw $c @(0xFF, 0x75, 0x18)                              # push dword ptr [ebp+0x18]
    AddRaw $c @(0xE8); AddLE32 $c (0x5622E0 - ($CAVE + 0x150)) # call 0x5622E0  (GetReducedKeyBinding)
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0x47, 0x01, 0x00, 0x00)            # jz ex_orig
    AddRaw $c @(0xFF, 0x75, 0x18)                              # push dword ptr [ebp+0x18]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0x8B, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov ecx,[ebp-0x104]
    AddRaw $c @(0xE8); AddLE32 $c (0x55E470 - ($CAVE + 0x167)) # call 0x55E470  (GetCommandForBinding)
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0x30, 0x01, 0x00, 0x00)            # jz ex_orig
    AddRaw $c @(0x89, 0xC6)                                    # mov esi,eax
    AddRaw $c @(0xBF); AddLE32 $c ($CAVE + 0x114)              # mov edi,strab
    AddRaw $c @(0xB9, 0x0C, 0x00, 0x00, 0x00)                  # mov ecx,12
    # ex_cmp:
    AddRaw $c @(0x8A, 0x06)                                    # mov al,[esi]
    AddRaw $c @(0x3C, 0x61)                                    # cmp al,0x61
    AddRaw $c @(0x72, 0x06)                                    # jb ex_c1
    AddRaw $c @(0x3C, 0x7A)                                    # cmp al,0x7A
    AddRaw $c @(0x77, 0x02)                                    # ja ex_c1
    AddRaw $c @(0x2C, 0x20)                                    # sub al,0x20
    # ex_c1:
    AddRaw $c @(0x3A, 0x07)                                    # cmp al,[edi]
    AddRaw $c @(0x0F, 0x85, 0x10, 0x01, 0x00, 0x00)            # jne ex_orig
    AddRaw $c @(0x46)                                          # inc esi
    AddRaw $c @(0x47)                                          # inc edi
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xE7)                                    # jnz ex_cmp
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    # ex_dig:
    AddRaw $c @(0x0F, 0xB6, 0x16)                              # movzx edx,byte ptr [esi]
    AddRaw $c @(0x83, 0xEA, 0x30)                              # sub edx,0x30
    AddRaw $c @(0x83, 0xFA, 0x09)                              # cmp edx,9
    AddRaw $c @(0x77, 0x11)                                    # ja ex_num
    AddRaw $c @(0x6B, 0xC0, 0x0A)                              # imul eax,eax,10
    AddRaw $c @(0x01, 0xD0)                                    # add eax,edx
    AddRaw $c @(0x83, 0xF8, 0x0C)                              # cmp eax,12
    AddRaw $c @(0x0F, 0x87, 0xF0, 0x00, 0x00, 0x00)            # ja ex_orig
    AddRaw $c @(0x46)                                          # inc esi
    AddRaw $c @(0xEB, 0xE4)                                    # jmp ex_dig
    # ex_num:
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0xE5, 0x00, 0x00, 0x00)            # jz ex_orig
    AddRaw $c @(0x8D, 0x58, 0xFF)                              # lea ebx,[eax-1]
    AddRaw $c @(0x83, 0x3D, 0xA0, 0xE5, 0xC1, 0x00, 0x00)      # cmp dword ptr [0xC1E5A0],0  (Seitenwechsel aktiv)
    AddRaw $c @(0x74, 0x07)                                    # je ex_p1
    AddRaw $c @(0xBA, 0x01, 0x00, 0x00, 0x00)                  # mov edx,1
    AddRaw $c @(0xEB, 0x07)                                    # jmp ex_p2
    # ex_p1:
    AddRaw $c @(0x8B, 0x15, 0x98, 0xE5, 0xC1, 0x00)            # mov edx,dword ptr [0xC1E598]  (aktuelle Seite)
    AddRaw $c @(0x42)                                          # inc edx
    # ex_p2:
    AddRaw $c @(0x83, 0xFA, 0x01)                              # cmp edx,1
    AddRaw $c @(0x75, 0x0D)                                    # jne ex_p3
    AddRaw $c @(0x8B, 0x0D, 0x9C, 0xE5, 0xC1, 0x00)            # mov ecx,dword ptr [0xC1E59C]  (Bonusleiste)
    AddRaw $c @(0x85, 0xC9)                                    # test ecx,ecx
    AddRaw $c @(0x74, 0x03)                                    # jz ex_p3
    AddRaw $c @(0x8D, 0x51, 0x06)                              # lea edx,[ecx+6]
    # ex_p3:
    AddRaw $c @(0x4A)                                          # dec edx
    AddRaw $c @(0x6B, 0xD2, 0x0C)                              # imul edx,edx,12
    AddRaw $c @(0x01, 0xD3)                                    # add ebx,edx
    AddRaw $c @(0x8B, 0x55, 0x0C)                              # mov edx,[ebp+0xC]
    AddRaw $c @(0xE8, 0xC5, 0x00, 0x00, 0x00)                  # call find
    AddRaw $c @(0x83, 0x7D, 0x10, 0x00)                        # cmp dword ptr [ebp+0x10],0
    AddRaw $c @(0x74, 0x5D)                                    # je ex_up
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x75, 0x0D)                                    # jnz ex_init
    AddRaw $c @(0xE8, 0xD3, 0x00, 0x00, 0x00)                  # call findfree
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x0F, 0x84, 0x94, 0x00, 0x00, 0x00)            # jz ex_orig
    # ex_init:
    AddRaw $c @(0x89, 0xC6)                                    # mov esi,eax
    AddRaw $c @(0x89, 0x5E, 0x04)                              # mov [esi+4],ebx
    AddRaw $c @(0xE8); AddLE32 $c (0x86AE20 - ($CAVE + 0x215)) # call 0x86AE20  (OsGetAsyncTimeMs)
    AddRaw $c @(0x89, 0x46, 0x08)                              # mov [esi+8],eax
    AddRaw $c @(0x89, 0x46, 0x0C)                              # mov [esi+12],eax
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0x89, 0x46, 0x10)                              # mov [esi+16],eax
    AddRaw $c @(0x89, 0x46, 0x14)                              # mov [esi+20],eax
    AddRaw $c @(0x8B, 0x55, 0x0C)                              # mov edx,[ebp+0xC]
    AddRaw $c @(0x89, 0x16)                                    # mov [esi],edx
    AddRaw $c @(0xC7, 0x46, 0x18, 0x01, 0x00, 0x00, 0x00)      # mov dword ptr [esi+24],1
    AddRaw $c @(0x83, 0x3D); AddLE32 $c ($CAVE + 0x104); AddRaw $c @(0x00) # cmp dword ptr [evreg],0
    AddRaw $c @(0x75, 0x67)                                    # jne ex_orig
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x104); AddRaw $c @(0x01, 0x00, 0x00, 0x00) # mov dword ptr [evreg],1
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0x68); AddLE32 $c ($CAVE + 0x2EF)              # push focus
    AddRaw $c @(0x6A, 0x02)                                    # push 2
    AddRaw $c @(0xE8); AddLE32 $c (0x47D3C0 - ($CAVE + 0x252)) # call 0x47D3C0  (EventRegisterEx)
    AddRaw $c @(0x83, 0xC4, 0x10)                              # add esp,16
    AddRaw $c @(0xEB, 0x48)                                    # jmp ex_orig
    # ex_up:
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x74, 0x44)                                    # jz ex_orig
    AddRaw $c @(0xC7, 0x40, 0x18, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [eax+24],0
    AddRaw $c @(0x83, 0x78, 0x14, 0x00)                        # cmp dword ptr [eax+20],0
    AddRaw $c @(0x74, 0x37)                                    # je ex_orig
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x01, 0x00, 0x00, 0x00) # mov dword ptr [suppress],1
    AddRaw $c @(0xFF, 0x75, 0x18)                              # push dword ptr [ebp+0x18]
    AddRaw $c @(0xFF, 0x75, 0x14)                              # push dword ptr [ebp+0x14]
    AddRaw $c @(0xFF, 0x75, 0x10)                              # push dword ptr [ebp+0x10]
    AddRaw $c @(0xFF, 0x75, 0x0C)                              # push dword ptr [ebp+0xC]
    AddRaw $c @(0xFF, 0x75, 0x08)                              # push dword ptr [ebp+8]
    AddRaw $c @(0x8B, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov ecx,[ebp-0x104]
    AddRaw $c @(0xE8, 0x1F, 0x00, 0x00, 0x00)                  # call exec_tramp
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x00, 0x00, 0x00, 0x00) # mov dword ptr [suppress],0
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x89, 0xEC)                                    # mov esp,ebp
    AddRaw $c @(0x5D)                                          # pop ebp
    AddRaw $c @(0xC2, 0x14, 0x00)                              # ret 0x14
    # ex_orig:
    AddRaw $c @(0x8B, 0x8D, 0xFC, 0xFE, 0xFF, 0xFF)            # mov ecx,[ebp-0x104]
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0x89, 0xEC)                                    # mov esp,ebp
    AddRaw $c @(0x5D)                                          # pop ebp
    # exec_tramp:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x81, 0xEC, 0xC4, 0x00, 0x00, 0x00)            # sub esp,0xC4
    AddRaw $c @(0xE9); AddLE32 $c (0x563159 - ($CAVE + 0x2B9)) # jmp 0x563159  (ExecKey+9)
    # --- Hilfsfunktionen: Eintrag zu edx (Taste) / freien Eintrag suchen ---
    # find:
    AddRaw $c @(0xB8); AddLE32 $c ($CAVE + 0x0)                # mov eax,held
    AddRaw $c @(0xB9, 0x08, 0x00, 0x00, 0x00)                  # mov ecx,8
    # f_l:
    AddRaw $c @(0x83, 0x78, 0x18, 0x00)                        # cmp dword ptr [eax+24],0
    AddRaw $c @(0x74, 0x04)                                    # je f_n
    AddRaw $c @(0x39, 0x10)                                    # cmp [eax],edx
    AddRaw $c @(0x74, 0x08)                                    # je f_r
    # f_n:
    AddRaw $c @(0x83, 0xC0, 0x20)                              # add eax,32
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xF0)                                    # jnz f_l
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    # f_r:
    AddRaw $c @(0xC3)                                          # ret
    # findfree:
    AddRaw $c @(0xB8); AddLE32 $c ($CAVE + 0x0)                # mov eax,held
    AddRaw $c @(0xB9, 0x08, 0x00, 0x00, 0x00)                  # mov ecx,8
    # ff_l:
    AddRaw $c @(0x83, 0x78, 0x18, 0x00)                        # cmp dword ptr [eax+24],0
    AddRaw $c @(0x74, 0x08)                                    # je ff_r
    AddRaw $c @(0x83, 0xC0, 0x20)                              # add eax,32
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xF4)                                    # jnz ff_l
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    # ff_r:
    AddRaw $c @(0xC3)                                          # ret
    # --- Fokus-Ereignis (cdecl): alle gehaltenen Tasten vergessen ---
    # focus:
    AddRaw $c @(0xB8); AddLE32 $c ($CAVE + 0x0)                # mov eax,held
    AddRaw $c @(0xB9, 0x08, 0x00, 0x00, 0x00)                  # mov ecx,8
    # fo_l:
    AddRaw $c @(0xC7, 0x40, 0x18, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [eax+24],0
    AddRaw $c @(0x83, 0xC0, 0x20)                              # add eax,32
    AddRaw $c @(0x49)                                          # dec ecx
    AddRaw $c @(0x75, 0xF3)                                    # jnz fo_l
    AddRaw $c @(0xB8, 0x01, 0x00, 0x00, 0x00)                  # mov eax,1
    AddRaw $c @(0xC3)                                          # ret
    # --- UseAction (VA 0x5ABBC0, cdecl: slot, guid*, button) ---
    # use:
    AddRaw $c @(0x83, 0x3D); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x00) # cmp dword ptr [suppress],0
    AddRaw $c @(0x74, 0x0B)                                    # je use_tramp
    AddRaw $c @(0xC7, 0x05); AddLE32 $c ($CAVE + 0x100); AddRaw $c @(0x00, 0x00, 0x00, 0x00) # mov dword ptr [suppress],0
    AddRaw $c @(0xC3)                                          # ret
    # use_tramp:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x0C)                              # sub esp,0xC
    AddRaw $c @(0xE9); AddLE32 $c (0x5ABBC6 - ($CAVE + 0x32B)) # jmp 0x5ABBC6  (UseAction+6)
    # --- OnWorldRender (VA 0x4F8EA0, thiscall): Original, danach Wiederholung pruefen ---
    # render:
    AddRaw $c @(0xE8, 0x08, 0x00, 0x00, 0x00)                  # call render_tramp
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xE8, 0x0D, 0x00, 0x00, 0x00)                  # call update
    AddRaw $c @(0x58)                                          # pop eax
    AddRaw $c @(0xC3)                                          # ret
    # render_tramp:
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x89, 0xE5)                                    # mov ebp,esp
    AddRaw $c @(0x83, 0xEC, 0x34)                              # sub esp,0x34
    AddRaw $c @(0xE9); AddLE32 $c (0x4F8EA6 - ($CAVE + 0x343)) # jmp 0x4F8EA6  (OnWorldRender+6)
    # --- Wiederholung: jede gehaltene Taste pruefen ---
    # update:
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0x56)                                          # push esi
    AddRaw $c @(0x57)                                          # push edi
    AddRaw $c @(0x55)                                          # push ebp
    AddRaw $c @(0x83, 0xEC, 0x10)                              # sub esp,16
    AddRaw $c @(0x89, 0xE3)                                    # mov ebx,esp
    AddRaw $c @(0xE8); AddLE32 $c (0x86AE20 - ($CAVE + 0x351)) # call 0x86AE20  (OsGetAsyncTimeMs)
    AddRaw $c @(0x89, 0xC5)                                    # mov ebp,eax
    AddRaw $c @(0xE8); AddLE32 $c (0x4D3790 - ($CAVE + 0x358)) # call 0x4D3790
    AddRaw $c @(0x6A, 0x00)                                    # push 0
    AddRaw $c @(0x68, 0xD4, 0x2C, 0xA2, 0x00)                  # push 0xA22CD4
    AddRaw $c @(0x6A, 0x10)                                    # push 0x10
    AddRaw $c @(0x52)                                          # push edx
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0xE8); AddLE32 $c (0x4D4DB0 - ($CAVE + 0x368)) # call 0x4D4DB0
    AddRaw $c @(0x83, 0xC4, 0x14)                              # add esp,0x14
    AddRaw $c @(0xB9, 0x01, 0x00, 0x00, 0x00)                  # mov ecx,1
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x74, 0x28)                                    # jz cast_done
    AddRaw $c @(0x83, 0xB8, 0x6C, 0x0A, 0x00, 0x00, 0x00)      # cmp dword ptr [eax+0xA6C],0
    AddRaw $c @(0x74, 0x0A)                                    # je cast_chan
    AddRaw $c @(0x89, 0xEA)                                    # mov edx,ebp
    AddRaw $c @(0x2B, 0x90, 0x7C, 0x0A, 0x00, 0x00)            # sub edx,[eax+0xA7C]
    AddRaw $c @(0x78, 0x15)                                    # js cast_done
    # cast_chan:
    AddRaw $c @(0x83, 0xB8, 0x80, 0x0A, 0x00, 0x00, 0x00)      # cmp dword ptr [eax+0xA80],0
    AddRaw $c @(0x74, 0x0A)                                    # je cast_no
    AddRaw $c @(0x89, 0xEA)                                    # mov edx,ebp
    AddRaw $c @(0x2B, 0x90, 0x88, 0x0A, 0x00, 0x00)            # sub edx,[eax+0xA88]
    AddRaw $c @(0x78, 0x02)                                    # js cast_done
    # cast_no:
    AddRaw $c @(0x31, 0xC9)                                    # xor ecx,ecx
    # cast_done:
    AddRaw $c @(0x89, 0x4B, 0x0C)                              # mov [ebx+12],ecx
    AddRaw $c @(0xBE); AddLE32 $c ($CAVE + 0x0)                # mov esi,held
    AddRaw $c @(0xBF, 0x08, 0x00, 0x00, 0x00)                  # mov edi,8
    # up_l:
    AddRaw $c @(0x83, 0x7E, 0x18, 0x00)                        # cmp dword ptr [esi+24],0
    AddRaw $c @(0x0F, 0x84, 0xAE, 0x00, 0x00, 0x00)            # je up_n
    AddRaw $c @(0x89, 0xE8)                                    # mov eax,ebp
    AddRaw $c @(0x2B, 0x46, 0x08)                              # sub eax,[esi+8]
    AddRaw $c @(0x3D, 0xF4, 0x01, 0x00, 0x00)                  # cmp eax,500
    AddRaw $c @(0x0F, 0x82, 0x9E, 0x00, 0x00, 0x00)            # jb up_n
    AddRaw $c @(0x83, 0x3D, 0xE4, 0xF4, 0xD3, 0x00, 0x00)      # cmp dword ptr [0xD3F4E4],0  (laufender Zauber)
    AddRaw $c @(0x75, 0x06)                                    # jne up_busy
    AddRaw $c @(0x83, 0x7B, 0x0C, 0x00)                        # cmp dword ptr [ebx+12],0
    AddRaw $c @(0x74, 0x0C)                                    # je up_nc
    # up_busy:
    AddRaw $c @(0xC7, 0x46, 0x10, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [esi+16],0
    AddRaw $c @(0xE9, 0x83, 0x00, 0x00, 0x00)                  # jmp up_n
    # up_nc:
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0x89, 0x03)                                    # mov [ebx],eax
    AddRaw $c @(0x89, 0x43, 0x04)                              # mov [ebx+4],eax
    AddRaw $c @(0x89, 0x43, 0x08)                              # mov [ebx+8],eax
    AddRaw $c @(0x8D, 0x43, 0x08)                              # lea eax,[ebx+8]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0x8D, 0x43, 0x04)                              # lea eax,[ebx+4]
    AddRaw $c @(0x50)                                          # push eax
    AddRaw $c @(0x53)                                          # push ebx
    AddRaw $c @(0xFF, 0x76, 0x04)                              # push dword ptr [esi+4]
    AddRaw $c @(0xE8); AddLE32 $c (0x5A8E40 - ($CAVE + 0x3F9)) # call 0x5A8E40  (GetCooldown)
    AddRaw $c @(0x83, 0xC4, 0x10)                              # add esp,16
    AddRaw $c @(0x8B, 0x43, 0x04)                              # mov eax,[ebx+4]
    AddRaw $c @(0x85, 0xC0)                                    # test eax,eax
    AddRaw $c @(0x7E, 0x11)                                    # jle up_ready
    AddRaw $c @(0x89, 0xE9)                                    # mov ecx,ebp
    AddRaw $c @(0x2B, 0x0B)                                    # sub ecx,[ebx]
    AddRaw $c @(0x39, 0xC1)                                    # cmp ecx,eax
    AddRaw $c @(0x73, 0x09)                                    # jae up_ready
    AddRaw $c @(0xC7, 0x46, 0x10, 0x00, 0x00, 0x00, 0x00)      # mov dword ptr [esi+16],0
    AddRaw $c @(0xEB, 0x4D)                                    # jmp up_n
    # up_ready:
    AddRaw $c @(0x83, 0x7E, 0x10, 0x00)                        # cmp dword ptr [esi+16],0
    AddRaw $c @(0x75, 0x03)                                    # jne up_r2
    AddRaw $c @(0x89, 0x6E, 0x10)                              # mov [esi+16],ebp
    # up_r2:
    AddRaw $c @(0x89, 0xE8)                                    # mov eax,ebp
    AddRaw $c @(0x2B, 0x46, 0x10)                              # sub eax,[esi+16]
    AddRaw $c @(0x83, 0xF8, 0x64)                              # cmp eax,100
    AddRaw $c @(0x72, 0x3A)                                    # jb up_n
    AddRaw $c @(0x89, 0xE8)                                    # mov eax,ebp
    AddRaw $c @(0x2B, 0x46, 0x0C)                              # sub eax,[esi+12]
    AddRaw $c @(0x83, 0xF8, 0x64)                              # cmp eax,100
    AddRaw $c @(0x72, 0x30)                                    # jb up_n
    AddRaw $c @(0x31, 0xC0)                                    # xor eax,eax
    AddRaw $c @(0xA3); AddLE32 $c ($CAVE + 0x108)              # mov dword ptr [guid],eax
    AddRaw $c @(0xA3); AddLE32 $c ($CAVE + 0x10C)              # mov dword ptr [guid+4],eax
    AddRaw $c @(0xA3); AddLE32 $c ($CAVE + 0x110)              # mov dword ptr [btn],eax
    AddRaw $c @(0x68); AddLE32 $c ($CAVE + 0x110)              # push btn
    AddRaw $c @(0x68); AddLE32 $c ($CAVE + 0x108)              # push guid
    AddRaw $c @(0xFF, 0x76, 0x04)                              # push dword ptr [esi+4]
    AddRaw $c @(0xE8, 0xCC, 0xFE, 0xFF, 0xFF)                  # call use_tramp
    AddRaw $c @(0x83, 0xC4, 0x0C)                              # add esp,12
    AddRaw $c @(0x89, 0x6E, 0x0C)                              # mov [esi+12],ebp
    AddRaw $c @(0xC7, 0x46, 0x14, 0x01, 0x00, 0x00, 0x00)      # mov dword ptr [esi+20],1
    # up_n:
    AddRaw $c @(0x83, 0xC6, 0x20)                              # add esi,32
    AddRaw $c @(0x4F)                                          # dec edi
    AddRaw $c @(0x0F, 0x85, 0x3E, 0xFF, 0xFF, 0xFF)            # jnz up_l
    AddRaw $c @(0x83, 0xC4, 0x10)                              # add esp,16
    AddRaw $c @(0x5D)                                          # pop ebp
    AddRaw $c @(0x5F)                                          # pop edi
    AddRaw $c @(0x5E)                                          # pop esi
    AddRaw $c @(0x5B)                                          # pop ebx
    AddRaw $c @(0xC3)                                          # ret
    if ($c.Count -ne 0x473) { throw 'Gedrueckt halten: Sektion hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    Patch ($EXEC - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $EXEC ($CAVE + 0x120)) + [byte[]](0x90, 0x90, 0x90, 0x90)))
    Patch ($USE - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $USE ($CAVE + 0x30C)) + [byte[]](0x90)))
    Patch ($RENDER - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $RENDER ($CAVE + 0x32B)) + [byte[]](0x90)))
}

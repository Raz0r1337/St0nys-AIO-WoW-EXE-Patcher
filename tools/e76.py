R("""       De = 'Geister-Angriff von NPCs beim Evade behoben'""", """       De = '"Geister"-Angriff von NPCs beim Evade behoben'""")
R("""        $state = @{ Hash = $hash; Ids = $ids; Values = $vals }
        Say (T 'WmFound') 'Green'
        Say (T 'WmScanned' $ids.Count) 'Green'
""", """        # Zustand wie nach dem Patchen: Original-Bytes aller erkannten Patches
        # aus der Tabelle. Gibt es nichts zu tun, wird er unten gespeichert,
        # damit der naechste Start wieder den schnellen Weg nehmen kann.
        $undo = New-Object System.Collections.Generic.List[object]
        foreach ($e in (Get-OriginalTable).Entries) {
            if ($ids -contains $e.Id -or $e.Id -eq 'watermark' -or $e.Id -eq 'pe') { $undo.Add(@($e.Off, $e.Bytes)) }
        }
        $state = @{ Hash = $hash; Size = (Get-OriginalTable).Size; Ids = $ids; Values = $vals; Undo = $undo; Scanned = $true }
        Say (T 'WmFound') 'Green'
        Say (T 'WmScanned' $ids.Count) 'Green'
""")
R("""    if ($added.Count + $changed.Count + $removed.Count -eq 0 -and $chosen.Count -gt 0) {
        Say (T 'NoChange') 'Green'
        Exit-Patcher 0
    }
""", """    if ($added.Count + $changed.Count + $removed.Count -eq 0 -and $chosen.Count -gt 0) {
        Say (T 'NoChange') 'Green'
        if ($state.Scanned -and $null -ne (Restore-Original $origPatched $state)) {
            # Patchstand kam ueber das Wasserzeichen - jetzt merken, dann geht es beim naechsten Mal schneller.
            if ($null -eq (Write-State $stateFile $state.Hash $state.Size $state.Ids $state.Values $state.Undo)) { Say (T 'StateSaved') 'DarkGray' }
        }
        Exit-Patcher 0
    }
""")
R("""    $f = $orig
    $patchedMode = $true
    $appliedIds = @($state.Ids)
}
""", """    $origPatched = $f      # die gepatchte Datei, wie sie auf der Platte liegt
    $f = $orig
    $patchedMode = $true
    $appliedIds = @($state.Ids)
}
""")

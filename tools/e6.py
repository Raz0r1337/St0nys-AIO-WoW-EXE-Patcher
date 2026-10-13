R("""        MenuHelp4     = 'O = Original wiederherstellen (alle Patches zuruecknehmen)'
""", "")
R("""        MenuHelp4     = 'O = restore original (remove all patches)'
""", "")
R("""    if ($script:patchedMode) { Say (T 'MenuHelp4') }
""", "")
R("""            '^[oO]$' {
                if (-not $script:patchedMode) { $message = T 'BadInput' $in; break }
                for ($i = 0; $i -lt $sel.Length; $i++) { $sel[$i] = $false }
                return , $sel
            }
""", "")

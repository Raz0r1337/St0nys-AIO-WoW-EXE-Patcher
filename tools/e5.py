R("""        # Patches mit eigener Eingabe: Vorschlag bzw. aktuellen Wert hinter den
        # Namen schreiben, wenn er vom Original abweicht (Build-Datum: immer).
        $name = PatchName $patches[$i]
        if ($patches[$i].Check) {
            $v = Get-ValueSuggestion $patches[$i]
            if ($v -cne $patches[$i].Default) {
                if (Test-ValueActive $patches[$i]) { $name += ' ' + (T 'ValueNow' $v) } else { $name += ' ' + (T 'ValueSuggest' $v) }
            }
        }
""", """        $name = PatchName $patches[$i]
""")
R("""    Write-Host ''
    Say (PatchName $p)
    while ($true) {""", """    # Vorschlag bzw. aktuellen Wert hinter den Namen mit dem Originalwert schreiben
    $label = 'ValueSuggest'; if (Test-ValueActive $p) { $label = 'ValueNow' }
    Write-Host ''
    Say "$(PatchName $p) $(T $label $def)"
    while ($true) {""")

R('''    $label = 'ValueSuggest'; if (Test-ValueActive $p) { $label = 'ValueNow' }
    Write-Host ''
    Say "$(PatchName $p) $(T $label $def)"
    while ($true) {
        $v = Ask "  $(L $p.PromptDe $p.PromptEn) [$def]"
''','''    $label = 'ValueSuggest'; if (Test-ValueActive $p) { $label = 'ValueNow' }
    Write-Host ''
    if ($def -ne '') { Say "$(PatchName $p) $(T $label $def)" } else { Say (PatchName $p) }
    while ($true) {
        $hint = ''; if ($def -ne '') { $hint = " [$def]" }
        $v = Ask "  $(L $p.PromptDe $p.PromptEn)$hint"
''')

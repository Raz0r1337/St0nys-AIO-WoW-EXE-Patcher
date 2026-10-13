R("""        MarkRemove    = '(wird zurueckgenommen)'
""", """        MarkRemove    = '(wird zurueckgenommen)'
        ValueSuggest  = '-> Vorschlag: {0}'
        ValueNow      = '-> aktuell: {0}'
""")
R("""        MarkRemove    = '(will be removed)'
""", """        MarkRemove    = '(will be removed)'
        ValueSuggest  = '-> suggestion: {0}'
        ValueNow      = '-> current: {0}'
""")
R("""function Get-SelectedCount($sel) {""", """# Vorschlag fuer einen Patch mit eigener Eingabe: der gemerkte Wert, sonst der
# Default; Patches mit Suggest berechnen ihren Vorschlag selbst (Build-Datum:
# heute). Ohne Rueckfragen (-Unattended) gilt der gemerkte Wert. Ist der Patch
# schon in der Wow.exe, ist sein aktueller Wert der Vorschlag.
function Test-ValueActive($p) {
    return ($script:patchedMode -and ($script:appliedIds -contains $p.Id) -and $script:state.Values.ContainsKey($p.Id))
}

function Get-ValueSuggestion($p) {
    $active = Test-ValueActive $p
    $saved = $script:savedValues[$p.Id]
    if ($active) { $saved = $script:state.Values[$p.Id] }
    $def = $saved
    if (-not $def) { $def = $p.Default }
    if ($p.Suggest -and -not $active -and -not ($Unattended -and $saved)) { $def = & $p.Suggest $saved }
    return $def
}

function Get-SelectedCount($sel) {""")
R("""        $was = $script:patchedMode -and ($script:appliedIds -contains $patches[$i].Id)
        if ($sel[$i]) {
            $mark = ''; if ($script:patchedMode -and -not $was) { $mark = ' ' + (T 'MarkNew') }
            Write-Host "   $nr  [X]  $(PatchName $patches[$i])$mark" -ForegroundColor Green
        } elseif ($was) {
            Write-Host "   $nr  [ ]  $(PatchName $patches[$i]) $(T 'MarkRemove')" -ForegroundColor Yellow
        } else {
            Write-Host "   $nr  [ ]  $(PatchName $patches[$i])" -ForegroundColor DarkGray
        }
""", """        $was = $script:patchedMode -and ($script:appliedIds -contains $patches[$i].Id)
        # Patches mit eigener Eingabe: Vorschlag bzw. aktuellen Wert hinter den
        # Namen schreiben, wenn er vom Original abweicht (Build-Datum: immer).
        $name = PatchName $patches[$i]
        if ($patches[$i].Check) {
            $v = Get-ValueSuggestion $patches[$i]
            if ($v -cne $patches[$i].Default) {
                if (Test-ValueActive $patches[$i]) { $name += ' ' + (T 'ValueNow' $v) } else { $name += ' ' + (T 'ValueSuggest' $v) }
            }
        }
        if ($sel[$i]) {
            $mark = ''; if ($script:patchedMode -and -not $was) { $mark = ' ' + (T 'MarkNew') }
            Write-Host "   $nr  [X]  $name$mark" -ForegroundColor Green
        } elseif ($was) {
            Write-Host "   $nr  [ ]  $name $(T 'MarkRemove')" -ForegroundColor Yellow
        } else {
            Write-Host "   $nr  [ ]  $name" -ForegroundColor DarkGray
        }
""")
R("""# --- 3. Patches auswaehlen ---
""", """# --- 3. Patches auswaehlen ---
$savedValues = Get-SavedValues
""")
R("""# --- 3b. Werte fuer Patches mit eigener Eingabe ---
# Vorschlag ist der gemerkte Wert, sonst der Default; Patches mit Suggest
# berechnen ihren Vorschlag selbst (Build-Datum: heute). Ohne Rueckfragen
# (-Unattended) gilt der gemerkte Wert, sonst der Vorschlag. Ist der Patch
# schon in der Wow.exe, ist sein aktueller Wert der Vorschlag.
$VALUES = @{}
$savedValues = Get-SavedValues
$asked = $false
foreach ($p in $chosen) {
    if (-not $p.Check) { continue }
    $active = $patchedMode -and ($appliedIds -contains $p.Id) -and $state.Values.ContainsKey($p.Id)
    $saved = $savedValues[$p.Id]
    if ($active) { $saved = $state.Values[$p.Id] }
    $def = $saved
    if (-not $def) { $def = $p.Default }
    if ($p.Suggest -and -not $active -and -not ($Unattended -and $saved)) { $def = & $p.Suggest $saved }
""", """# --- 3b. Werte fuer Patches mit eigener Eingabe (Vorschlag: Get-ValueSuggestion) ---
$VALUES = @{}
$asked = $false
foreach ($p in $chosen) {
    if (-not $p.Check) { continue }
    $def = Get-ValueSuggestion $p
""")

R("""    $m = [array]::IndexOf($en, $matches[1]); $suffix = ''
    if ($m -lt 0) { $m = [array]::IndexOf($fr, $matches[1]); $suffix = ' FR' }
    if ($m -lt 0) { return $null }
    return ('{0}-{1:00}-{2}{3}' -f $matches[3], ($m + 1), $matches[2], $suffix)""",
  """    $m = [array]::IndexOf($en, $matches[1]); $suffix = ''
    if ($m -lt 0) { $m = [array]::IndexOf($fr, $matches[1]); $suffix = ' FR' }
    if ($m -lt 0) { return $null }
    # Monate, die in beiden Sprachen gleich heissen (Jan, Mar, Jun, ...), verraten
    # die Sprache nicht - dann gilt die aus dem gemerkten Wert.
    if ($suffix -eq '' -and $fr[$m] -eq $en[$m] -and ((Get-SavedValues)['clientdate'] -match '\\sFR\\s*$')) { $suffix = ' FR' }
    return ('{0}-{1:00}-{2}{3}' -f $matches[3], ($m + 1), $matches[2], $suffix)""")

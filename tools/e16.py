R("""    $src = [regex]::Replace($src, '(?s)# BEGIN ORIGINAL-BYTES.*?# END ORIGINAL-BYTES', { param($m) $block })
""", """    $a = $src.IndexOf('# BEGIN ORIGINAL-BYTES' + "`r`n")
    $z = $src.IndexOf('# END ORIGINAL-BYTES', $a)
    if ($a -lt 0 -or $z -lt 0) { Write-Host 'BuildTable: Markierungen nicht gefunden.'; exit 1 }
    $src = $src.Substring(0, $a) + $block + $src.Substring($z + '# END ORIGINAL-BYTES'.Length)
""")

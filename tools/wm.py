R("""# ============================================================
#  Helfer fuer den Sprunghoehen-Patch
""", r"""# ============================================================
#  Wasserzeichen
#  Jede gepatchte Wow.exe bekommt einen Text, an dem man spaeter erkennt,
#  dass sie mit diesem Patcher erstellt wurde. Er steht im Fuellbereich
#  hinter der .tls-Sektion (Datei 0x72DE19-0x72DFFF, 487 Byte Nullen):
#  ausserhalb der VirtualSize, wird also nie geladen, und kein Patch nutzt
#  diesen Bereich. Die Dateigroesse bleibt gleich. Geschrieben wird ueber
#  Patch(), beim Zuruecknehmen verschwindet das Wasserzeichen also wieder.
# ============================================================
$WATERMARK_OFF = 0x72DE20
$WATERMARK = 'Patched with St0nys AIO WoW.exe Patcher by St0ny (Raz0r1337) - https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher'

function Add-Watermark {
    $b = [System.Text.Encoding]::ASCII.GetBytes($WATERMARK)
    for ($i = 0; $i -le $b.Length; $i++) {
        if ($script:f[$WATERMARK_OFF + $i] -ne 0) { throw ('Wasserzeichen: Bereich bei 0x{0:X} ist belegt.' -f ($WATERMARK_OFF + $i)) }
    }
    Patch $WATERMARK_OFF $b
}

# ============================================================
#  Helfer fuer den Sprunghoehen-Patch
""")
R("""try {
    foreach ($p in $chosen) {
        $cur++
        Say "[+] $(([string]$cur).PadLeft($width))/$total - $(PatchName $p)"
        & $p.Code
    }
} catch {""", """try {
    foreach ($p in $chosen) {
        $cur++
        Say "[+] $(([string]$cur).PadLeft($width))/$total - $(PatchName $p)"
        & $p.Code
    }
    if ($total -gt 0) { Add-Watermark }
} catch {""")

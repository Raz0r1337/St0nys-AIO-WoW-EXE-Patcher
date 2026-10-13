# P im Startmenue: unter Linux/Mac Backslash-Escapes vom Hineinziehen ins Terminal entfernen.
# Aufruf: path_escape.py <apply_patches.ps1>
import sys
path = sys.argv[1]
raw = open(path, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
a = """        $in = $in.Trim('"', "'").Trim()
        if ($in -eq '') {
            Save-WowPath ''"""
b = """        $in = $in.Trim('"', "'").Trim()
        # Linux/Mac: Manche Terminals setzen beim Hineinziehen einen Backslash
        # vor Leerzeichen und Sonderzeichen ("My\\ Games") - den entfernen.
        if ([System.IO.Path]::DirectorySeparatorChar -eq '/' -and $in.Contains('\\') -and -not (Test-Path -LiteralPath $in)) {
            $in = [regex]::Replace($in, '\\\\(.)', '$1')
        }
        if ($in -eq '') {
            Save-WowPath ''"""
assert s.count(a) == 1
s = s.replace(a, b)
open(path, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')

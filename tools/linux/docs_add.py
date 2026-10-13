# Linux-Abschnitt: Hinweis auf Microsofts Paketquelle und "Getestet mit Ubuntu 24.04".
# Aufruf: python3 docs_add.py <worktree>
import sys
wt = sys.argv[1]
def once(s, a, b, label):
    n = s.count(a); assert n == 1, '%s: %d Treffer' % (label, n); return s.replace(a, b)
for fn, pairs in (
  ('docs/README.de.md', [
    ("mit PowerShell 7 (`pwsh`) – Wine wird dafür nicht gebraucht.\n",
     "mit PowerShell 7 (`pwsh`) – Wine wird dafür nicht gebraucht. Getestet mit\nUbuntu 24.04.\n"),
    ("   [Debian](https://learn.microsoft.com/powershell/scripting/install/install-debian) oder [RHEL](https://learn.microsoft.com/powershell/scripting/install/install-rhel).\n",
     "   [Debian](https://learn.microsoft.com/powershell/scripting/install/install-debian) oder [RHEL](https://learn.microsoft.com/powershell/scripting/install/install-rhel).\n"
     "   PowerShell liegt nicht in den normalen Paketquellen; die verlinkten\n"
     "   Anleitungen richten deshalb zuerst die Paketquelle von Microsoft ein,\n"
     "   sonst findet z. B. `apt` das Paket `powershell` nicht.\n")]),
  ('docs/README.md', [
    ("PowerShell 7 (`pwsh`) – no Wine needed.\n",
     "PowerShell 7 (`pwsh`) – no Wine needed. Tested on Ubuntu 24.04.\n"),
    ("   [Debian](https://learn.microsoft.com/powershell/scripting/install/install-debian) or [RHEL](https://learn.microsoft.com/powershell/scripting/install/install-rhel).\n",
     "   [Debian](https://learn.microsoft.com/powershell/scripting/install/install-debian) or [RHEL](https://learn.microsoft.com/powershell/scripting/install/install-rhel).\n"
     "   PowerShell is not in the default package sources; the linked\n"
     "   instructions therefore first add Microsoft's package source, otherwise\n"
     "   e.g. `apt` will not find the `powershell` package.\n")])):
    p = wt + '/' + fn
    s = open(p, encoding='utf-8', newline='').read(); assert '\r' not in s
    for a, b in pairs: s = once(s, a, b, fn)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
print(wt.split('/')[-1], 'docs OK')

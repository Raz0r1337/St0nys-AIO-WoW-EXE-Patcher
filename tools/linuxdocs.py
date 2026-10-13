import sys
d=sys.argv[1]
def edit(fn,pairs):
    p=d+'/'+fn; t=open(p,encoding='utf-8').read()
    assert '\r\n' not in t
    for a,b in pairs:
        assert t.count(a)==1,(fn,a[:60],t.count(a)); t=t.replace(a,b)
    open(p,'w',encoding='utf-8',newline='\n').write(t); print(fn,'ok')
U='https://learn.microsoft.com/powershell/scripting/install/'
edit('patcher.sh',[('    echo "  Installation: README.de.md / README.md (Linux)"\n','    echo "  Installation: docs/README.de.md / docs/README.md (Linux)"\n')])
edit('docs/README.de.md',[
 ("- [Benutzung](#benutzung)\n","- [Benutzung](#benutzung)\n  - [Unter Linux](#unter-linux)\n"),
 ("- Windows mit PowerShell (Windows PowerShell 5.1 ist ab Windows 10 vorinstalliert)\n",
  "- Windows mit PowerShell (Windows PowerShell 5.1 ist ab Windows 10 vorinstalliert) –\n  Linux: siehe [Unter Linux](#unter-linux)\n"),
 ("> [Hinweise](#hinweise).\n\n## Ablauf\n","""> [Hinweise](#hinweise).

### Unter Linux

Der Patcher ist für Windows geschrieben, läuft aber auch unter Linux direkt
mit PowerShell 7 (`pwsh`) – Wine wird dafür nicht gebraucht.

1. PowerShell 7 installieren, z. B. für [Ubuntu](%sinstall-ubuntu),
   [Debian](%sinstall-debian) oder [RHEL](%sinstall-rhel).
   Für andere Distributionen gibt es Snap und ein Archiv zum Entpacken
   ([Anleitung](%sinstall-other-linux)), für Arch das Paket im AUR.
2. `patcher.sh` und `apply_patches.ps1` in den WoW-Ordner kopieren. Wie die
   `Wow.exe` geschrieben ist (`WoW.exe`, `wow.exe` …), spielt keine Rolle.
3. WoW beenden, falls es noch läuft.
4. Im Terminal im WoW-Ordner `./patcher.sh` starten.

Alles Weitere funktioniert wie unter Windows: Wo in dieser Anleitung
`patcher.bat` steht, nimmst du `./patcher.sh`. Auf einem Mac kann der
Patcher mit PowerShell 7 ebenfalls funktionieren, das ist aber ungetestet.

## Ablauf
""" % (U,U,U,U)),
 ("| `patcher.bat`       | Startdatei, ruft `apply_patches.ps1` auf |\n",
  "| `patcher.bat`       | Startdatei, ruft `apply_patches.ps1` auf |\n| `patcher.sh`        | Startdatei für Linux |\n")])
edit('docs/README.md',[
 ("- [Usage](#usage)\n","- [Usage](#usage)\n  - [On Linux](#on-linux)\n"),
 ("- Windows with PowerShell (Windows PowerShell 5.1 ships with Windows 10 and later)\n",
  "- Windows with PowerShell (Windows PowerShell 5.1 ships with Windows 10 and later) –\n  Linux: see [On Linux](#on-linux)\n"),
 ("> [Notes](#notes).\n\n## Workflow\n","""> [Notes](#notes).

### On Linux

The patcher is written for Windows, but it also runs on Linux directly with
PowerShell 7 (`pwsh`) – no Wine needed.

1. Install PowerShell 7, e.g. for [Ubuntu](%sinstall-ubuntu),
   [Debian](%sinstall-debian) or [RHEL](%sinstall-rhel).
   Other distributions can use Snap or an archive to unpack
   ([instructions](%sinstall-other-linux)), Arch the package from the AUR.
2. Copy `patcher.sh` and `apply_patches.ps1` into your WoW folder. How
   `Wow.exe` is spelled (`WoW.exe`, `wow.exe` …) does not matter.
3. Close WoW if it is still running.
4. In a terminal in the WoW folder, run `./patcher.sh`.

Everything else works as on Windows: wherever this guide says `patcher.bat`,
use `./patcher.sh`. On a Mac the patcher may also work with PowerShell 7, but
this is untested.

## Workflow
""" % (U,U,U,U)),
 ("| `patcher.bat`       | Launcher, calls `apply_patches.ps1` |\n",
  "| `patcher.bat`       | Launcher, calls `apply_patches.ps1` |\n| `patcher.sh`        | Launcher for Linux |\n")])

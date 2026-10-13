# Startdateien umbenennen (patcher-win.bat / patcher-lin.sh) und Linux-Teil der README.
# Aufruf: python3 rename.py main|dev|side <worktree> [<dev-worktree>]
import re, sys, os, subprocess
mode, wt = sys.argv[1], sys.argv[2]
def once(s, a, b, label=''):
    n = s.count(a); assert n == 1, '%s: %d Treffer fuer %r' % (label, n, a[:90]); return s.replace(a, b)
def git(*a): subprocess.run(['git', '-C', wt] + list(a), check=True)
rd = lambda p: open(wt + '/' + p, encoding='utf-8', newline='').read()
def wr(p, s): open(wt + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

# ---- Startdateien
git('mv', 'patcher.bat', 'patcher-win.bat')
b = open(wt + '/patcher-win.bat', 'rb').read().decode('ascii')
b = once(b, 'REM  St0nys-AIO-WoW-EXE-Patcher - Startdatei / Launcher\r\n', 'REM  St0nys-AIO-WoW-EXE-Patcher - Startdatei fuer Windows / Launcher\r\n', 'bat Kopf')
b = once(b, 'REM    patcher.bat -Language en -Select default\r\n', 'REM    patcher-win.bat -Language en -Select default\r\n', 'bat REM')
open(wt + '/patcher-win.bat', 'wb').write(b.encode('ascii'))
if mode == 'dev':
    git('mv', 'patcher.sh', 'patcher-lin.sh')
if mode in ('dev', 'main'):
    if mode == 'main':
        src = open(sys.argv[3] + '/patcher.sh', encoding='ascii', newline='').read()
        open(wt + '/patcher-lin.sh', 'w', encoding='ascii', newline='\n').write(src)
        os.chmod(wt + '/patcher-lin.sh', 0o755)
        git('add', 'patcher-lin.sh'); git('update-index', '--chmod=+x', 'patcher-lin.sh')
        open(wt + '/.gitattributes', 'w', encoding='ascii', newline='\n').write(open(sys.argv[3] + '/.gitattributes', encoding='ascii', newline='').read())
    sh = rd('patcher-lin.sh')
    sh = once(sh, '#    ./patcher.sh -Language en -Select default\n', '#    ./patcher-lin.sh -Language en -Select default\n', 'sh usage')
    wr('patcher-lin.sh', sh)

# ---- README
LINUX = {
 'de': ("### Unter Linux\n\n"
        "Der Patcher ist für Windows geschrieben, läuft aber auch unter Linux direkt\n"
        "mit PowerShell 7 (`pwsh`) – Wine wird dafür nicht gebraucht.\n\n"
        "1. PowerShell 7 installieren, z. B. für [Ubuntu](https://learn.microsoft.com/powershell/scripting/install/install-ubuntu),\n"
        "   [Debian](https://learn.microsoft.com/powershell/scripting/install/install-debian) oder [RHEL](https://learn.microsoft.com/powershell/scripting/install/install-rhel).\n"
        "   Für andere Distributionen gibt es Snap und ein Archiv zum Entpacken\n"
        "   ([Anleitung](https://learn.microsoft.com/powershell/scripting/install/install-other-linux)), für Arch das Paket im AUR.\n"
        "2. Das ZIP entpacken und die originale `Wow.exe` in den Ordner\n"
        "   `St0nys-AIO-WoW-EXE-Patcher` kopieren – wie unter Windows. Wie die\n"
        "   `Wow.exe` geschrieben ist (`WoW.exe`, `wow.exe` …), spielt keine Rolle.\n"
        "3. Im Terminal in diesem Ordner `./patcher.sh` starten. Falls das nicht\n"
        "   startet (z. B. weil beim Entpacken das Ausführungsrecht verloren ging):\n"
        "   `sh patcher.sh`.\n"
        "4. WoW beenden und die gepatchte `Wow.exe` zurück in den WoW-Ordner kopieren.\n\n"
        "Alles Weitere funktioniert wie unter Windows: Wo in dieser Anleitung\n"
        "`patcher.bat` steht, nimmst du `./patcher.sh`. Auf einem Mac kann der\n"
        "Patcher mit PowerShell 7 ebenfalls funktionieren, das ist aber ungetestet.\n\n"),
 'en': ("### On Linux\n\n"
        "The patcher is written for Windows, but it also runs on Linux directly with\n"
        "PowerShell 7 (`pwsh`) – no Wine needed.\n\n"
        "1. Install PowerShell 7, e.g. for [Ubuntu](https://learn.microsoft.com/powershell/scripting/install/install-ubuntu),\n"
        "   [Debian](https://learn.microsoft.com/powershell/scripting/install/install-debian) or [RHEL](https://learn.microsoft.com/powershell/scripting/install/install-rhel).\n"
        "   Other distributions can use Snap or an archive to unpack\n"
        "   ([instructions](https://learn.microsoft.com/powershell/scripting/install/install-other-linux)), Arch the package from the AUR.\n"
        "2. Unpack the ZIP and copy your original `Wow.exe` into the folder\n"
        "   `St0nys-AIO-WoW-EXE-Patcher` – just like on Windows. How `Wow.exe` is\n"
        "   spelled (`WoW.exe`, `wow.exe` …) does not matter.\n"
        "3. In a terminal in that folder, run `./patcher.sh`. If that does not start\n"
        "   (e.g. because unpacking lost the execute permission), use `sh patcher.sh`.\n"
        "4. Close WoW and copy the patched `Wow.exe` back into your WoW folder.\n\n"
        "Everything else works as on Windows: wherever this guide says `patcher.bat`,\n"
        "use `./patcher.sh`. On a Mac the patcher may also work with PowerShell 7, but\n"
        "this is untested.\n\n")}
for fn, lang in (('docs/README.de.md', 'de'), ('docs/README.md', 'en')):
    s = rd(fn); assert '\r' not in s
    if mode == 'main':
        if lang == 'de':
            s = once(s, "- [Benutzung](#benutzung)\n", "- [Benutzung](#benutzung)\n  - [Unter Linux](#unter-linux)\n", 'TOC')
            s = once(s, "- Windows mit PowerShell (Windows PowerShell 5.1 ist ab Windows 10 vorinstalliert)\n",
                        "- Windows mit PowerShell (Windows PowerShell 5.1 ist ab Windows 10 vorinstalliert) –\n  Linux: siehe [Unter Linux](#unter-linux)\n", 'Voraussetzungen')
            s = once(s, "> [Hinweise](#hinweise).\n\n## Ablauf\n", "> [Hinweise](#hinweise).\n\n" + LINUX['de'] + "## Ablauf\n", 'Abschnitt')
            s = once(s, "| `patcher.bat`       | Startdatei, ruft `apply_patches.ps1` auf |\n",
                        "| `patcher.bat`       | Startdatei, ruft `apply_patches.ps1` auf |\n| `patcher.sh`        | Startdatei für Linux |\n", 'Dateien')
        else:
            s = once(s, "- [Usage](#usage)\n", "- [Usage](#usage)\n  - [On Linux](#on-linux)\n", 'TOC')
            s = once(s, "- Windows with PowerShell (Windows PowerShell 5.1 ships with Windows 10 and later)\n",
                        "- Windows with PowerShell (Windows PowerShell 5.1 ships with Windows 10 and later) –\n  Linux: see [On Linux](#on-linux)\n", 'Requirements')
            s = once(s, "> [Notes](#notes).\n\n## Workflow\n", "> [Notes](#notes).\n\n" + LINUX['en'] + "## Workflow\n", 'section')
            s = once(s, "| `patcher.bat`       | Launcher, calls `apply_patches.ps1` |\n",
                        "| `patcher.bat`       | Launcher, calls `apply_patches.ps1` |\n| `patcher.sh`        | Launcher for Linux |\n", 'files')
    # Dateiliste: Windows ausdruecklich nennen, Spaltenbreite halten
    if lang == 'de':
        s = once(s, "| `patcher.bat`       | Startdatei, ruft `apply_patches.ps1` auf |\n", "| `patcher-win.bat`   | Startdatei für Windows, ruft `apply_patches.ps1` auf |\n", 'Dateien bat')
        if mode in ('dev', 'main'): s = once(s, "| `patcher.sh`        | Startdatei für Linux |\n", "| `patcher-lin.sh`    | Startdatei für Linux |\n", 'Dateien sh')
    else:
        s = once(s, "| `patcher.bat`       | Launcher, calls `apply_patches.ps1` |\n", "| `patcher-win.bat`   | Launcher for Windows, calls `apply_patches.ps1` |\n", 'files bat')
        if mode in ('dev', 'main'): s = once(s, "| `patcher.sh`        | Launcher for Linux |\n", "| `patcher-lin.sh`    | Launcher for Linux |\n", 'files sh')
    s = s.replace('patcher.bat', 'patcher-win.bat').replace('patcher.sh', 'patcher-lin.sh')
    assert 'patcher.bat' not in s and 'patcher.sh' not in s
    wr(fn, s)

# ---- Release-Workflow (nur main)
if mode == 'main':
    p = '.github/workflows/release.yml'; s = rd(p)
    s = once(s, "double-click `patcher.bat`. Then copy the", "double-click `patcher-win.bat`. Then copy the", 'wf bat')
    s = once(s, "if [ -f patcher.sh ]; then", "if [ -f patcher-lin.sh ]; then", 'wf if')
    s = once(s, "Linux: `./patcher.sh` with PowerShell 7", "Linux: `./patcher-lin.sh` with PowerShell 7", 'wf sh')
    wr(p, s)
print(mode, 'OK')

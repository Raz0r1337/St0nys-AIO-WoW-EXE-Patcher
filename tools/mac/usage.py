# README (dev): Benutzung in Windows / Linux / Mac gliedern, Mac-Anleitung.
import sys
wt = sys.argv[1]
def once(s, a, b, label):
    n = s.count(a); assert n == 1, '%s: %d Treffer' % (label, n); return s.replace(a, b)
ISSUES = 'https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/issues'
MACDOC = 'https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-macos'
MAC_DE = ("### Auf dem Mac\n\n"
 "> [!NOTE]\n"
 "> Ich habe keinen Mac und kann den Patcher dort nicht testen. Die Anleitung\n"
 "> sollte funktionieren, weil es PowerShell 7 auch für macOS gibt – eine\n"
 "> Garantie gibt es aber nicht. Wenn du es ausprobierst, freue ich mich über\n"
 "> eine Rückmeldung als [Issue](" + ISSUES + ").\n\n"
 "Der Patcher verändert die Windows-`Wow.exe`. Auf dem Mac ist das die `Wow.exe`,\n"
 "die du z. B. mit CrossOver oder Wine startest – den Mac-Client selbst kann er\n"
 "nicht patchen.\n\n"
 "1. PowerShell 7 installieren, z. B. mit [Homebrew](https://brew.sh):\n"
 "   `brew install --cask powershell`. Alternativ gibt es ein\n"
 "   Installationspaket von Microsoft ([Anleitung](" + MACDOC + ")).\n"
 "2. Das ZIP entpacken und die originale `Wow.exe` in den Ordner\n"
 "   `St0nys-AIO-WoW-EXE-Patcher` kopieren – wie unter Windows.\n"
 "3. Das Terminal öffnen und in diesen Ordner wechseln, z. B. `cd ` eingeben und\n"
 "   den Ordner ins Terminal-Fenster ziehen. Dann `sh patcher-lin.sh` starten –\n"
 "   die Linux-Startdatei funktioniert auch auf dem Mac.\n"
 "4. WoW beenden und die gepatchte `Wow.exe` zurück in den WoW-Ordner kopieren.\n\n"
 "Alles Weitere funktioniert wie unter Windows: Wo in dieser Anleitung\n"
 "`patcher-win.bat` steht, nimmst du `sh patcher-lin.sh`.\n\n")
MAC_EN = ("### On a Mac\n\n"
 "> [!NOTE]\n"
 "> I don't have a Mac and cannot test the patcher there. The steps should work\n"
 "> because PowerShell 7 is also available for macOS – but there is no\n"
 "> guarantee. If you try it, I'd be glad about feedback as an\n"
 "> [issue](" + ISSUES + ").\n\n"
 "The patcher modifies the Windows `Wow.exe`. On a Mac that is the `Wow.exe` you\n"
 "run e.g. with CrossOver or Wine – it cannot patch the Mac client itself.\n\n"
 "1. Install PowerShell 7, e.g. with [Homebrew](https://brew.sh):\n"
 "   `brew install --cask powershell`. Microsoft also offers an installer\n"
 "   package ([instructions](" + MACDOC + ")).\n"
 "2. Unpack the ZIP and copy your original `Wow.exe` into the folder\n"
 "   `St0nys-AIO-WoW-EXE-Patcher` – just like on Windows.\n"
 "3. Open Terminal and change to that folder, e.g. type `cd ` and drag the\n"
 "   folder into the Terminal window. Then run `sh patcher-lin.sh` – the Linux\n"
 "   start file works on a Mac as well.\n"
 "4. Close WoW and copy the patched `Wow.exe` back into your WoW folder.\n\n"
 "Everything else works as on Windows: wherever this guide says\n"
 "`patcher-win.bat`, use `sh patcher-lin.sh`.\n\n")
# ---- Deutsch
p = wt + '/docs/README.de.md'; s = open(p, encoding='utf-8', newline='').read(); assert '\r' not in s
s = once(s, "- [Benutzung](#benutzung)\n  - [Unter Linux](#unter-linux)\n",
            "- [Benutzung](#benutzung)\n  - [Unter Windows](#unter-windows)\n  - [Unter Linux](#unter-linux)\n  - [Auf dem Mac](#auf-dem-mac)\n", 'de TOC')
s = once(s, "- Windows mit PowerShell (Windows PowerShell 5.1 ist ab Windows 10 vorinstalliert) –\n  Linux: siehe [Unter Linux](#unter-linux)\n",
            "- Windows mit PowerShell (Windows PowerShell 5.1 ist ab Windows 10 vorinstalliert),\n  Linux oder Mac mit PowerShell 7 – siehe [Unter Linux](#unter-linux) und\n  [Auf dem Mac](#auf-dem-mac)\n", 'de Voraussetzungen')
s = once(s, "## Benutzung\n\n1. Das ZIP", "## Benutzung\n\n### Unter Windows\n\n1. Das ZIP", 'de Windows')
s = once(s, "Alles Weitere funktioniert wie unter Windows: Wo in dieser Anleitung\n"
            "`patcher-win.bat` steht, nimmst du `./patcher-lin.sh`. Auf einem Mac kann der\n"
            "Patcher mit PowerShell 7 ebenfalls funktionieren, das ist aber ungetestet.\n\n",
            "Alles Weitere funktioniert wie unter Windows: Wo in dieser Anleitung\n"
            "`patcher-win.bat` steht, nimmst du `./patcher-lin.sh`.\n\n" + MAC_DE, 'de Mac')
s = once(s, "| `patcher-lin.sh`    | Startdatei für Linux |\n", "| `patcher-lin.sh`    | Startdatei für Linux, auch für den Mac |\n", 'de Dateien')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
# ---- Englisch
p = wt + '/docs/README.md'; s = open(p, encoding='utf-8', newline='').read(); assert '\r' not in s
s = once(s, "- [Usage](#usage)\n  - [On Linux](#on-linux)\n",
            "- [Usage](#usage)\n  - [On Windows](#on-windows)\n  - [On Linux](#on-linux)\n  - [On a Mac](#on-a-mac)\n", 'en TOC')
s = once(s, "- Windows with PowerShell (Windows PowerShell 5.1 ships with Windows 10 and later) –\n  Linux: see [On Linux](#on-linux)\n",
            "- Windows with PowerShell (Windows PowerShell 5.1 ships with Windows 10 and later),\n  Linux or Mac with PowerShell 7 – see [On Linux](#on-linux) and\n  [On a Mac](#on-a-mac)\n", 'en Requirements')
s = once(s, "## Usage\n\n1. Download", "## Usage\n\n### On Windows\n\n1. Download", 'en Windows')
s = once(s, "Everything else works as on Windows: wherever this guide says `patcher-win.bat`,\n"
            "use `./patcher-lin.sh`. On a Mac the patcher may also work with PowerShell 7, but\n"
            "this is untested.\n\n",
            "Everything else works as on Windows: wherever this guide says `patcher-win.bat`,\n"
            "use `./patcher-lin.sh`.\n\n" + MAC_EN, 'en Mac')
s = once(s, "| `patcher-lin.sh`    | Launcher for Linux |\n", "| `patcher-lin.sh`    | Launcher for Linux, also for a Mac |\n", 'en files')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('usage OK')

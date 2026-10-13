# README (dev): Formulierungen im Mac- und Linux-Abschnitt nach St0nys Vorgaben.
import sys
wt = sys.argv[1]
def once(s, a, b, label):
    n = s.count(a); assert n == 1, '%s: %d Treffer' % (label, n); return s.replace(a, b)
def rep_n(s, a, b, n, label):
    c = s.count(a); assert c == n, '%s: %d Treffer statt %d' % (label, c, n); return s.replace(a, b)
p = wt + '/docs/README.de.md'; s = open(p, encoding='utf-8', newline='').read(); assert '\r' not in s
s = once(s, "Der Patcher verändert die Windows-`Wow.exe`. Auf dem Mac ist das die `Wow.exe`,\n"
            "die du z. B. mit CrossOver oder Wine startest – den Mac-Client selbst kann er\n"
            "nicht patchen.\n",
            "Der Patcher verändert die Windows-`Wow.exe`, den Mac-Client selbst kann er\n"
            "nicht patchen. Auf dem Mac ist das die `Wow.exe`, die du z. B. mit CrossOver\n"
            "oder Wine startest.\n", 'de Mac-Client')
s = once(s, "   den Ordner ins Terminal-Fenster ziehen. Dann `sh patcher-lin.sh` starten –\n"
            "   die Linux-Startdatei funktioniert auch auf dem Mac.\n",
            "   den Ordner ins Terminal-Fenster ziehen. Dann `sh patcher-lin.sh` starten –\n"
            "   die Linux-Startdatei sollte auch auf dem Mac funktionieren.\n", 'de Startdatei')
s = rep_n(s, "4. WoW beenden und die gepatchte `Wow.exe` zurück in den WoW-Ordner kopieren.\n",
             "4. Sollte WoW laufen, beende es und kopiere die gepatchte `Wow.exe` zurück in\n"
             "   den WoW-Ordner.\n", 2, 'de Schritt 4 (Linux+Mac)')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
p = wt + '/docs/README.md'; s = open(p, encoding='utf-8', newline='').read(); assert '\r' not in s
s = once(s, "The patcher modifies the Windows `Wow.exe`. On a Mac that is the `Wow.exe` you\n"
            "run e.g. with CrossOver or Wine – it cannot patch the Mac client itself.\n",
            "The patcher modifies the Windows `Wow.exe`, it cannot patch the Mac client\n"
            "itself. On a Mac that is the `Wow.exe` you run e.g. with CrossOver or Wine.\n", 'en Mac client')
s = once(s, "   folder into the Terminal window. Then run `sh patcher-lin.sh` – the Linux\n"
            "   start file works on a Mac as well.\n",
            "   folder into the Terminal window. Then run `sh patcher-lin.sh` – the Linux\n"
            "   start file should work on a Mac as well.\n", 'en start file')
s = rep_n(s, "4. Close WoW and copy the patched `Wow.exe` back into your WoW folder.\n",
             "4. If WoW is running, close it and copy the patched `Wow.exe` back into your\n"
             "   WoW folder.\n", 2, 'en step 4 (Linux+Mac)')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('wording OK')

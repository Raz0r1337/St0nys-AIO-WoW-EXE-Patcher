# README DE/EN: Benutzung mit P (Pfad zum WoW-Ordner) als Hauptweg, Kopieren als zweiter Weg.
# Aufruf: docs_usage_path.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

edit('docs/README.de.md', [
("""2. Die originale `Wow.exe` aus dem WoW-Ordner in diesen Ordner kopieren.
3. `patcher-win.bat` per Doppelklick starten.
4. Sprache wählen (nur beim ersten Start), im [Startmenü](#startmenü) `1` für das
   Patch-Menü, Patches auswählen, bestätigen.
5. Sollte WoW laufen, beende es und kopiere die gepatchte `Wow.exe` zurück in
   den WoW-Ordner, dort ersetzt sie die alte.

Patches **ändern oder zurücknehmen:** `patcher-win.bat` im Patcher-Ordner einfach
erneut starten und die `Wow.exe` danach wieder in den WoW-Ordner kopieren,
siehe [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen).

> [!TIP]
> **Ohne Kopieren:** Statt die `Wow.exe` hin und her zu kopieren, kannst du im
> [Startmenü](#startmenü) mit `P` den Pfad zur `Wow.exe` in deinem WoW-Ordner
> angeben. Der Patcher merkt sich den Pfad und patcht die Exe dann direkt dort;
> die Sicherungen bleiben im Patcher-Ordner. WoW muss dabei beendet sein.""",
"""2. WoW beenden und `patcher-win.bat` per Doppelklick starten.
3. Sprache wählen (nur beim ersten Start). Im [Startmenü](#startmenü) `P`
   drücken und den Pfad zu deinem WoW-Ordner eingeben – oder den Ordner bzw.
   die `Wow.exe` einfach ins Fenster ziehen – und ENTER drücken. Das ist nur
   einmal nötig, der Patcher merkt sich den Pfad.
4. Im Startmenü `1` für das Patch-Menü, Patches auswählen, bestätigen. Der
   Patcher patcht die `Wow.exe` direkt in deinem WoW-Ordner; die Sicherungen
   (`Wow.exe.ORI`, `Wow.exe.BAK`) legt er in seinem eigenen Ordner an.

Patches **ändern oder zurücknehmen:** `patcher-win.bat` einfach erneut starten,
siehe [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen).

> [!TIP]
> **Kopieren statt Pfad:** Soll der Patcher die `Wow.exe` im WoW-Ordner nicht
> direkt verändern, kopiere die originale `Wow.exe` vor dem Start in den
> Patcher-Ordner und lass `P` weg. Nach dem Patchen kopierst du die gepatchte
> `Wow.exe` zurück in den WoW-Ordner – nach jeder Änderung erneut."""),
("""2. Das ZIP entpacken und die originale `Wow.exe` in den Ordner
   `St0nys-AIO-WoW-EXE-Patcher` kopieren – wie unter Windows. Wie die
   `Wow.exe` geschrieben ist (`WoW.exe`, `wow.exe` …), spielt keine Rolle.
3. Im Terminal in diesem Ordner `./patcher-lin.sh` starten. Falls das nicht
   startet (z. B. weil beim Entpacken das Ausführungsrecht verloren ging):
   `sh patcher-lin.sh`.
4. Sollte WoW laufen, beende es und kopiere die gepatchte `Wow.exe` zurück in
   den WoW-Ordner.

Alles Weitere funktioniert wie unter Windows: Wo in dieser Anleitung
`patcher-win.bat` steht, nimmst du `./patcher-lin.sh`.""",
"""2. Das ZIP entpacken.
3. Im Terminal in diesem Ordner `./patcher-lin.sh` starten. Falls das nicht
   startet (z. B. weil beim Entpacken das Ausführungsrecht verloren ging):
   `sh patcher-lin.sh`.
4. Im Startmenü `P` drücken und den Pfad zu deinem WoW-Ordner angeben –
   eintippen oder den Ordner ins Terminal ziehen –, dann `1` und Patches
   wählen, wie unter Windows. WoW muss dabei beendet sein. Wie die `Wow.exe`
   geschrieben ist (`WoW.exe`, `wow.exe` …), spielt keine Rolle.

Statt mit `P` kannst du die `Wow.exe` auch wie unter Windows in den
Patcher-Ordner kopieren und nach dem Patchen zurückkopieren. Alles Weitere
funktioniert wie unter Windows: Wo in dieser Anleitung `patcher-win.bat`
steht, nimmst du `./patcher-lin.sh`."""),
("""2. Das ZIP entpacken und die originale `Wow.exe` in den Ordner
   `St0nys-AIO-WoW-EXE-Patcher` kopieren – wie unter Windows.
3. Das Terminal öffnen und in diesen Ordner wechseln, z. B. `cd ` eingeben und
   den Ordner ins Terminal-Fenster ziehen. Dann `sh patcher-lin.sh` starten –
   die Linux-Startdatei sollte auch auf dem Mac funktionieren.
4. Sollte WoW laufen, beende es und kopiere die gepatchte `Wow.exe` zurück in
   den WoW-Ordner.

Alles Weitere funktioniert wie unter Windows: Wo in dieser Anleitung
`patcher-win.bat` steht, nimmst du `sh patcher-lin.sh`.""",
"""2. Das ZIP entpacken.
3. Das Terminal öffnen und in diesen Ordner wechseln, z. B. `cd ` eingeben und
   den Ordner ins Terminal-Fenster ziehen. Dann `sh patcher-lin.sh` starten –
   die Linux-Startdatei sollte auch auf dem Mac funktionieren.
4. Im Startmenü `P` drücken und den Pfad zu der `Wow.exe` angeben, die du mit
   CrossOver oder Wine startest – eintippen oder ins Terminal ziehen –, dann
   `1` und Patches wählen, wie unter Windows. WoW muss dabei beendet sein.

Statt mit `P` kannst du die `Wow.exe` auch wie unter Windows in den
Patcher-Ordner kopieren und nach dem Patchen zurückkopieren. Alles Weitere
funktioniert wie unter Windows: Wo in dieser Anleitung `patcher-win.bat`
steht, nimmst du `sh patcher-lin.sh`."""),
("""Client-Infos). Mit `N` und ENTER nimmst du alle Patches zurück – danach ist die
`Wow.exe` wieder **byte-genau das Original**. Danach kopierst du die `Wow.exe`
wieder in deinen WoW-Ordner.""",
"""Client-Infos). Mit `N` und ENTER nimmst du alle Patches zurück – danach ist die
`Wow.exe` wieder **byte-genau das Original**. Hast du die `Wow.exe` in den
Patcher-Ordner kopiert, statt mit `P` den Pfad anzugeben, kopierst du sie
danach wieder in deinen WoW-Ordner."""),
])

edit('docs/README.md', [
("""2. Copy your original `Wow.exe` from your WoW folder into that folder.
3. Double-click `patcher-win.bat`.
4. Choose the language (first start only), `1` in the [start menu](#start-menu)
   for the patch menu, select patches, confirm.
5. If WoW is running, close it and copy the patched `Wow.exe` back into your
   WoW folder, replacing the old one.

To **change or remove** patches just run `patcher-win.bat` in the patcher folder
again and copy `Wow.exe` back into your WoW folder afterwards, see
[Changing or removing patches](#changing-or-removing-patches).

> [!TIP]
> **Without copying:** instead of copying `Wow.exe` back and forth, you can set
> the path to the `Wow.exe` in your WoW folder with `P` in the
> [start menu](#start-menu). The patcher remembers the path and then patches the
> exe right there; the backups stay in the patcher folder. WoW has to be closed.""",
"""2. Close WoW and double-click `patcher-win.bat`.
3. Choose the language (first start only). In the [start menu](#start-menu)
   press `P` and enter the path to your WoW folder – or just drag the folder
   or the `Wow.exe` into the window – and press ENTER. This is only needed
   once, the patcher remembers the path.
4. `1` in the start menu for the patch menu, select patches, confirm. The
   patcher patches the `Wow.exe` right in your WoW folder; it keeps the
   backups (`Wow.exe.ORI`, `Wow.exe.BAK`) in its own folder.

To **change or remove** patches just run `patcher-win.bat` again, see
[Changing or removing patches](#changing-or-removing-patches).

> [!TIP]
> **Copying instead of a path:** if the patcher should not change the
> `Wow.exe` in your WoW folder directly, copy your original `Wow.exe` into the
> patcher folder before starting and skip `P`. After patching, copy the
> patched `Wow.exe` back into your WoW folder – again after every change."""),
("""2. Unpack the ZIP and copy your original `Wow.exe` into the folder
   `St0nys-AIO-WoW-EXE-Patcher` – just like on Windows. How `Wow.exe` is
   spelled (`WoW.exe`, `wow.exe` …) does not matter.
3. In a terminal in that folder, run `./patcher-lin.sh`. If that does not start
   (e.g. because unpacking lost the execute permission), use `sh patcher-lin.sh`.
4. If WoW is running, close it and copy the patched `Wow.exe` back into your
   WoW folder.

Everything else works as on Windows: wherever this guide says `patcher-win.bat`,
use `./patcher-lin.sh`.""",
"""2. Unpack the ZIP.
3. In a terminal in that folder, run `./patcher-lin.sh`. If that does not start
   (e.g. because unpacking lost the execute permission), use `sh patcher-lin.sh`.
4. In the start menu press `P` and enter the path to your WoW folder – type
   it or drag the folder into the terminal –, then `1` and select patches,
   just like on Windows. WoW has to be closed. How `Wow.exe` is spelled
   (`WoW.exe`, `wow.exe` …) does not matter.

Instead of using `P` you can also copy `Wow.exe` into the patcher folder and
back after patching, just like on Windows. Everything else works as on
Windows: wherever this guide says `patcher-win.bat`, use `./patcher-lin.sh`."""),
("""2. Unpack the ZIP and copy your original `Wow.exe` into the folder
   `St0nys-AIO-WoW-EXE-Patcher` – just like on Windows.
3. Open Terminal and change to that folder, e.g. type `cd ` and drag the
   folder into the Terminal window. Then run `sh patcher-lin.sh` – the Linux
   start file should work on a Mac as well.
4. If WoW is running, close it and copy the patched `Wow.exe` back into your
   WoW folder.

Everything else works as on Windows: wherever this guide says
`patcher-win.bat`, use `sh patcher-lin.sh`.""",
"""2. Unpack the ZIP.
3. Open Terminal and change to that folder, e.g. type `cd ` and drag the
   folder into the Terminal window. Then run `sh patcher-lin.sh` – the Linux
   start file should work on a Mac as well.
4. In the start menu press `P` and enter the path to the `Wow.exe` you run
   with CrossOver or Wine – type it or drag it into the terminal –, then `1`
   and select patches, just like on Windows. WoW has to be closed.

Instead of using `P` you can also copy `Wow.exe` into the patcher folder and
back after patching, just like on Windows. Everything else works as on
Windows: wherever this guide says `patcher-win.bat`, use `sh patcher-lin.sh`."""),
("""every patch – afterwards `Wow.exe` is **byte-for-byte the original** again.
Afterwards copy `Wow.exe` back into your WoW folder.""",
"""every patch – afterwards `Wow.exe` is **byte-for-byte the original** again.
If you copied `Wow.exe` into the patcher folder instead of setting the path
with `P`, copy it back into your WoW folder afterwards."""),
])
print('ok')

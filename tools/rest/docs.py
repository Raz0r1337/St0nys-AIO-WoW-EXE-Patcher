import sys
wt = sys.argv[1]
def once(s, a, b, label):
    n = s.count(a); assert n == 1, '%s: %d Treffer' % (label, n); return s.replace(a, b)
SEC_DE = ("### Wenn die Wow.exe fehlt\n\n"
"Liegt im Patcher-Ordner keine `Wow.exe` mehr, aber noch die Sicherungen\n"
"`Wow.exe.ORI` und/oder `Wow.exe.BAK` – etwa weil du die gepatchte Exe in den\n"
"WoW-Ordner verschoben statt kopiert hast –, bietet der Patcher beim Start an:\n\n"
"1. **Neue Wow.exe aus dem Original bauen:** Das Menü startet mit den Patches\n"
"   und Werten, die zuletzt eingespielt waren. Du kannst sie übernehmen, ändern\n"
"   oder mit `R`, `B` oder `S` ein Preset laden. Ohne Änderung entsteht genau die\n"
"   zuletzt gepatchte `Wow.exe` neu.\n"
"2. **Vorherige Wow.exe wiederherstellen:** Der Patcher kopiert `Wow.exe.BAK`\n"
"   zurück, also den Stand vor dem letzten Patchen.\n"
"3. **Original wiederherstellen:** Der Patcher kopiert `Wow.exe.ORI` zurück.\n\n"
"`Q` bricht ab. Die Sicherungen bleiben in jedem Fall erhalten. Angeboten wird\n"
"nur, was sich verwenden lässt: Das Original muss laut SHA256 wirklich das\n"
"Original sein, das Backup original oder mit diesem Patcher gepatcht. Mit\n"
"`-Unattended` gibt es kein Menü; der Patcher bricht dann ab und weist auf die\n"
"Sicherungen hin.\n\n")
SEC_EN = ("### If Wow.exe is missing\n\n"
"If there is no `Wow.exe` in the patcher folder any more, but the backups\n"
"`Wow.exe.ORI` and/or `Wow.exe.BAK` are still there – e.g. because you moved the\n"
"patched exe into your WoW folder instead of copying it –, the patcher offers at\n"
"startup:\n\n"
"1. **Build a new Wow.exe from the original:** the menu starts with the patches\n"
"   and values applied last time. You can keep them, change them or load a\n"
"   preset with `R`, `B` or `S`. Without changes you get exactly the last\n"
"   patched `Wow.exe` again.\n"
"2. **Restore the previous Wow.exe:** the patcher copies `Wow.exe.BAK` back,\n"
"   i.e. the state before the last patching.\n"
"3. **Restore the original:** the patcher copies `Wow.exe.ORI` back.\n\n"
"`Q` cancels. The backups are kept in every case. Only usable options are\n"
"offered: the original must really be the original according to SHA256, the\n"
"backup original or patched with this patcher. With `-Unattended` there is no\n"
"menu; the patcher then aborts and points to the backups.\n\n")
p = wt + '/docs/README.de.md'; s = open(p, encoding='utf-8', newline='').read(); assert '\r' not in s
s = once(s, "4. Prüfung, ob eine `Wow.exe` im Ordner vorhanden ist.\n",
            "4. Prüfung, ob eine `Wow.exe` im Ordner vorhanden ist. Fehlt sie, liegen aber\n"
            "   noch Sicherungen im Ordner, bietet der Patcher an, sie neu zu bauen oder\n"
            "   wiederherzustellen (siehe [Wenn die Wow.exe fehlt](#wenn-die-wowexe-fehlt)).\n", 'de Ablauf')
s = once(s, "## Parameter für den unbeaufsichtigten Betrieb\n", SEC_DE + "## Parameter für den unbeaufsichtigten Betrieb\n", 'de Abschnitt')
s = once(s, "  oder ohne `patcher_state.ini`. Alternativ gepatchte `Wow.exe` löschen und\n"
            "  `Wow.exe.ORI` in `Wow.exe` umbenennen. `Wow.exe.BAK` ist dagegen die `Wow.exe`\n"
            "  von vor dem letzten Lauf.\n",
            "  oder ohne `patcher_state.ini`. Alternativ die gepatchte `Wow.exe` löschen und\n"
            "  den Patcher starten: Er bietet dann an, das Original wiederherzustellen\n"
            "  (siehe [Wenn die Wow.exe fehlt](#wenn-die-wowexe-fehlt)). `Wow.exe.BAK` ist\n"
            "  dagegen die `Wow.exe` von vor dem letzten Lauf.\n", 'de Hinweise')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
p = wt + '/docs/README.md'; s = open(p, encoding='utf-8', newline='').read(); assert '\r' not in s
s = once(s, "4. Check that a `Wow.exe` exists in the folder.\n",
            "4. Check that a `Wow.exe` exists in the folder. If it is missing but backups\n"
            "   are still there, the patcher offers to rebuild or restore it (see\n"
            "   [If Wow.exe is missing](#if-wowexe-is-missing)).\n", 'en workflow')
s = once(s, "## Parameters for unattended use\n", SEC_EN + "## Parameters for unattended use\n", 'en section')
s = once(s, "  without `patcher_state.ini`. Alternatively delete the patched `Wow.exe` and\n"
            "  rename `Wow.exe.ORI` to `Wow.exe`. `Wow.exe.BAK`, on the other hand, is the\n"
            "  `Wow.exe` from before the last run.\n",
            "  without `patcher_state.ini`. Alternatively delete the patched `Wow.exe` and\n"
            "  start the patcher: it then offers to restore the original (see\n"
            "  [If Wow.exe is missing](#if-wowexe-is-missing)). `Wow.exe.BAK`, on the other\n"
            "  hand, is the `Wow.exe` from before the last run.\n", 'en notes')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('Doku OK')

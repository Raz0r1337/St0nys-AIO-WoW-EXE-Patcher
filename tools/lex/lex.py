# Lexara-Lader und wow_optimize-Lader: getestet, [sicher - DLL riskant], ohne BETA.
# Aufruf: python3 lex.py dev|lights|main <worktree>
import re, sys
mode, wt = sys.argv[1], sys.argv[2]

def once(s, a, b, label=''):
    n = s.count(a)
    assert n == 1, '%s: %d Treffer fuer %r' % (label, n, a[:100])
    return s.replace(a, b)

def rd_ps():
    raw = open(wt + '/apply_patches.ps1', 'rb').read().decode('ascii')
    assert raw.count('\r\n') == raw.count('\n')
    return raw.replace('\r\n', '\n')
def wr_ps(s):
    open(wt + '/apply_patches.ps1', 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
def rd_md(fn):
    s = open(wt + '/docs/' + fn, encoding='utf-8', newline='').read(); assert '\r' not in s; return s
def wr_md(fn, s):
    open(wt + '/docs/' + fn, 'w', encoding='utf-8', newline='\n').write(s)

def section(s, anchor):
    """Start/Ende eines PATCHES-Abschnitts (bis zum naechsten Anker oder ##)."""
    a = s.index('<a id="patch-%s"></a>' % anchor)
    nx = [k for k in (s.find('\n<a id="', a + 1), s.find('\n## ', a + 1)) if k != -1]
    return a, min(nx) + 1

BETA_DE = ("> [!WARNING]\n> **BETA** – dieser Patch ist noch in der Testphase und deshalb vorerst nur in\n"
           "> den dev-Zweigen, nicht in `st0ny-main`.\n")
BETA_EN = ("> [!WARNING]\n> **BETA** – this patch is still being tested and is therefore only in the dev\n"
           "> branches for now, not in `st0ny-main`.\n")
DLLBOX_DE = ("> [!WARNING]\n> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten\n"
             "> ist. Die geladene `Lexara.dll` kann aber auf öffentlichen Servern erkannt\n"
             "> oder blockiert werden – also nur dort einsetzen, wo Lexara erlaubt ist.\n")
DLLBOX_EN = ("> [!WARNING]\n> The patch itself is safe, it only loads a DLL that is not included here.\n"
             "> The loaded `Lexara.dll`, however, may be detected or blocked on public\n"
             "> servers – so use it only where Lexara is allowed.\n")

# ---------------------------------------------------------------- Skript
LEX_HEAD_OLD = "    @{ Id = 'lexara'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true\n"
LEX_HEAD_NEW = "    @{ Id = 'lexara'; Cat = 'dll'; On = $false; DllRisky = $true\n"
LEX_DE = ("       De = 'Lexara.dll beim Start laden (HD-Schriften von Stormhand) [BETA]'\n",
          "       De = 'Lexara.dll beim Start laden (HD-Schriften von Stormhand)'\n")
LEX_EN = ("       En = 'Load Lexara.dll at startup (HD fonts by Stormhand) [BETA]'\n",
          "       En = 'Load Lexara.dll at startup (HD fonts by Stormhand)'\n")
WO_DE = ("       De = 'wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST) [BETA]'\n",
         "       De = 'wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST)'\n")
WO_EN = ("       En = 'Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST) [BETA]'\n",
         "       En = 'Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST)'\n")

def status_script(s, rf_old, rf_new, has_wo):
    s = once(s, LEX_HEAD_OLD, LEX_HEAD_NEW, 'lexara-Kopf')
    s = once(s, *LEX_DE, label='lexara De'); s = once(s, *LEX_EN, label='lexara En')
    if has_wo:
        s = once(s, *WO_DE, label='wo De'); s = once(s, *WO_EN, label='wo En')
    s = once(s, rf_old, rf_new, 'Reforged-Kommentar')
    return s

# ---------------------------------------------------------------- Doku (Status)
def status_rows(s, lang, has_wo):
    if lang == 'de':
        s = once(s, 'Lexara.dll beim Start laden (HD-Schriften von Stormhand) [BETA] *(', 'Lexara.dll beim Start laden (HD-Schriften von Stormhand) *(', 'Zeile lexara')
        m = re.search(r'(?m)^(\| \[\d+\]\(PATCHES\.de\.md#patch-lexara\) .*\| )🟠 \*\*\[ungetestet\]\*\*( \|.*)$', s); assert m
        s = s[:m.start()] + m.group(1) + '🟡 **[sicher - DLL riskant]**' + m.group(2) + s[m.end():]
        if has_wo: s = once(s, 'wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST) [BETA] *(', 'wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST) *(', 'Zeile wo')
    else:
        s = once(s, 'Load Lexara.dll at startup (HD fonts by Stormhand) [BETA] *(', 'Load Lexara.dll at startup (HD fonts by Stormhand) *(', 'row lexara')
        m = re.search(r'(?m)^(\| \[\d+\]\(PATCHES\.en\.md#patch-lexara\) .*\| )🟠 \*\*\[untested\]\*\*( \|.*)$', s); assert m
        s = s[:m.start()] + m.group(1) + '🟡 **[safe - DLL risky]**' + m.group(2) + s[m.end():]
        if has_wo: s = once(s, 'Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST) [BETA] *(', 'Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST) *(', 'row wo')
    return s

def status_patches(s, lang, has_wo, keep_voice=True):
    beta, box = (BETA_DE, DLLBOX_DE) if lang == 'de' else (BETA_EN, DLLBOX_EN)
    a, b = section(s, 'lexara'); sec = s[a:b]
    if lang == 'de':
        sec = once(sec, '**Lexara.dll beim Start laden (HD-Schriften von Stormhand) [BETA]**', '**Lexara.dll beim Start laden (HD-Schriften von Stormhand)**', 'H lexara')
        sec = once(sec, ', Autor: St0ny)* 🟠 **[ungetestet]**\n', ', Autor: St0ny)* 🟡 **[sicher - DLL riskant]**\n', 'Badge lexara')
    else:
        sec = once(sec, '**Load Lexara.dll at startup (HD fonts by Stormhand) [BETA]**', '**Load Lexara.dll at startup (HD fonts by Stormhand)**', 'H lexara')
        sec = once(sec, ', Author: St0ny)* 🟠 **[untested]**\n', ', Author: St0ny)* 🟡 **[safe - DLL risky]**\n', 'badge lexara')
    sec = once(sec, beta, box, 'BETA-Kasten lexara')
    s = s[:a] + sec + s[b:]
    if has_wo:
        a, b = section(s, 'wowoptimize'); sec = s[a:b]
        if lang == 'de':
            sec = once(sec, '**wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST) [BETA]**', '**wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST)**', 'H wo')
        else:
            sec = once(sec, '**Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST) [BETA]**', '**Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST)**', 'H wo')
        sec = once(sec, beta + '\n', '', 'BETA-Kasten wo')
        s = s[:a] + sec + s[b:]
    return s

# ---------------------------------------------------------------- Zweig-Texte
RF = {}
RF['dev'] = dict(
 ps=("# Warmane getestet (Nr. 9, 65 und 66 vergroessern die Wow.exe); dazu der noch\n# ungetestete Lexara-Lader (Nr. 30). Im Menue mit R, ueber\n",
     "# Warmane getestet (Nr. 9, 65 und 66 vergroessern die Wow.exe); dazu der\n# Lexara-Lader (Nr. 30, Patch sicher, DLL riskant). Im Menue mit R, ueber\n"),
 de=("Dazu kommt der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften. Er ist noch\nungetestet; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts. Welche Patches\ndazugehören, zeigt die Spalte „Reforged“ in der\n",
     "Dazu kommt der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften. Der Patch\nselbst ist sicher, die `Lexara.dll` kann auf öffentlichen Servern aber erkannt\noder blockiert werden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts.\nWelche Patches dazugehören, zeigt die Spalte „Reforged“ in der\n"),
 en=("(No. 30) for Stormhand's HD fonts. It is still untested; without `Lexara.dll`\nin the WoW folder it does nothing. The \"Reforged\" column in the\n",
     "(No. 30) for Stormhand's HD fonts. The patch itself is safe, but `Lexara.dll`\nmay be detected or blocked on public servers; without `Lexara.dll` in the WoW\nfolder it does nothing. The \"Reforged\" column in the\n"),
 leg_de=[("kann zu Kick/Bann führen: Nr. 26, 30, 31, 41,", "kann zu Kick/Bann führen: Nr. 26, 31, 41,"),
         ("möglicherweise verbuggt: Nr. 25, 26, 30, 31, 46, 53 und 64 (orange Warnung).", "möglicherweise verbuggt: Nr. 25, 26, 31, 46, 53 und 64 (orange Warnung)."),
         ("erkannt oder blockiert werden kann: Nr. 27–29\n", "erkannt oder blockiert werden kann: Nr. 27–30\n")],
 leg_en=[("you kicked or banned: No. 26, 30, 31, 41,", "you kicked or banned: No. 26, 31, 41,"),
         ("possibly buggy: No. 25, 26, 30, 31, 46, 53 and 64 (orange warning).", "possibly buggy: No. 25, 26, 31, 46, 53 and 64 (orange warning)."),
         ("detected or blocked on public servers: No. 27–29 (yellow note).", "detected or blocked on public servers: No. 27–30 (yellow note).")],
 wo=True)
RF['lights'] = dict(
 ps=("# Warmane getestet (Nr. 9, 64 und 65 vergroessern die Wow.exe); dazu der noch\n# ungetestete Lexara-Lader (Nr. 29) und die noch ungetesteten Licht-Patches\n# Nr. 66 und 67. Im Menue mit R, ueber\n",
     "# Warmane getestet (Nr. 9, 64 und 65 vergroessern die Wow.exe); dazu der\n# Lexara-Lader (Nr. 29, Patch sicher, DLL riskant) und die noch ungetesteten\n# Licht-Patches Nr. 66 und 67. Im Menue mit R, ueber\n"),
 de=("Licht-Patches Nr. 66 und 67. Sie sind noch ungetestet; ohne `Lexara.dll` im\nWoW-Ordner bewirkt Nr. 29 nichts. Welche Patches\ndazugehören, zeigt die Spalte „Reforged“ in der\n",
     "Licht-Patches Nr. 66 und 67. Beim Lexara-Lader ist der Patch selbst sicher,\ndie `Lexara.dll` kann auf öffentlichen Servern aber erkannt oder blockiert\nwerden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts. Die Licht-Patches\nsind noch ungetestet. Welche Patches dazugehören, zeigt die Spalte „Reforged“\nin der\n"),
 en=("No. 66 and 67. They are still untested; without `Lexara.dll` in the WoW folder\nNo. 29 does nothing. The \"Reforged\" column in the\n",
     "No. 66 and 67. For the Lexara loader the patch itself is safe, but\n`Lexara.dll` may be detected or blocked on public servers; without\n`Lexara.dll` in the WoW folder it does nothing. The light patches are still\nuntested. The \"Reforged\" column in the\n"),
 leg_de=[("kann zu Kick/Bann führen: Nr. 26, 29, 30, 40,", "kann zu Kick/Bann führen: Nr. 26, 30, 40,"),
         ("möglicherweise verbuggt: Nr. 25, 26, 29, 30, 45, 52, 63, 66 und 67 (orange Warnung).", "möglicherweise verbuggt: Nr. 25, 26, 30, 45, 52, 63, 66 und 67 (orange Warnung)."),
         ("erkannt oder blockiert werden kann: Nr. 27 und 28\n", "erkannt oder blockiert werden kann: Nr. 27–29\n")],
 leg_en=[("you kicked or banned: No. 26, 29, 30, 40,", "you kicked or banned: No. 26, 30, 40,"),
         ("possibly buggy: No. 25, 26, 29, 30, 45, 52, 63, 66 and 67 (orange warning).", "possibly buggy: No. 25, 26, 30, 45, 52, 63, 66 and 67 (orange warning)."),
         ("detected or blocked on public servers: No. 27 and 28 (yellow note).", "detected or blocked on public servers: No. 27–29 (yellow note).")],
 wo=False)

def run_status(cfg):
    s = rd_ps(); s = status_script(s, cfg['ps'][0], cfg['ps'][1], cfg['wo']); wr_ps(s)
    for fn, lang, key, leg in (('README.de.md', 'de', 'de', 'leg_de'), ('README.md', 'en', 'en', 'leg_en')):
        s = rd_md(fn); s = status_rows(s, lang, cfg['wo'])
        s = once(s, cfg[key][0], cfg[key][1], 'Reforged ' + lang)
        for a, b in cfg[leg]: s = once(s, a, b, 'Legende ' + lang)
        wr_md(fn, s)
    for fn, lang in (('PATCHES.de.md', 'de'), ('PATCHES.en.md', 'en')):
        s = rd_md(fn); s = status_patches(s, lang, cfg['wo']); wr_md(fn, s)

# ---------------------------------------------------------------- main
def mp(n): n = int(n); return n if n < 29 else n + 1
def refs(s):
    def f(m):
        out = '%s %s' % (m.group(1), mp(m.group(2)))
        if m.group(3): out += m.group(3) + str(mp(m.group(4)))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?', f, s)

def run_main(devwt):
    # --- Skript: Eintrag aus dev holen, anpassen, vor den Gameplay-Fixes einfuegen
    dev = open(devwt + '/apply_patches.ps1', 'rb').read().decode('ascii').replace('\r\n', '\n')
    a = dev.index("    @{ Id = 'lexara'"); b = dev.index("    @{ Id = 'voicedll'")
    entry = dev[a:b]; assert entry.endswith('    }}\n\n') and 'Nr.' not in entry
    entry = once(entry, LEX_HEAD_OLD, LEX_HEAD_NEW, 'lexara-Kopf')
    entry = once(entry, *LEX_DE, label='lexara De'); entry = once(entry, *LEX_EN, label='lexara En')
    entry = once(entry, "        # wird ebenfalls vor dem Einstiegspunkt geladen, der Zeitpunkt passt.\n"
                        "        # Vertraegt sich mit dem voice.dll-Lader (der aendert nur den Sprung\n"
                        "        # danach). Fehlt die DLL, startet WoW ganz normal.\n",
                        "        # wird ebenfalls vor dem Einstiegspunkt geladen, der Zeitpunkt passt.\n"
                        "        # Fehlt die DLL, startet WoW ganz normal.\n", 'voice-Satz')
    s = rd_ps()
    assert "Id = 'lexara'" not in s
    s = once(s, "    # --- Gameplay-Fixes ---\n", entry + "    # --- Gameplay-Fixes ---\n", 'Einfuegen')
    out = []
    for x in s.split('\n'):
        if re.match(r'^[a-z0-9]+;', x) or 'Name mit Patch-Nummer davor' in x or x.startswith('# Warmane getestet (Nr. 9, 62 und 63'):
            out.append(x)
        else:
            out.append(refs(x))
    s = '\n'.join(out)
    s = once(s, "# von Stormhand. Nur sichere Patches, alle von Stormhand mehrere Stunden auf\n"
                "# Warmane getestet (Nr. 9, 62 und 63 vergroessern die Wow.exe). Im Menue mit R, ueber\n",
                "# von Stormhand. Sichere Patches, alle von Stormhand mehrere Stunden auf\n"
                "# Warmane getestet (Nr. 9, 63 und 64 vergroessern die Wow.exe); dazu der\n"
                "# Lexara-Lader (Nr. 29, Patch sicher, DLL riskant). Im Menue mit R, ueber\n", 'Reforged-Kommentar')
    i = s.index('$PRESET_REFORGED = @(')
    s = s[:i] + once(s[i:i + 600], "    'glue',\n", "    'glue', 'lexara',\n", 'Preset') + s[i + 600:]
    wr_ps(s)
    # --- README
    ROW = {'de': "| [29](PATCHES.de.md#patch-lexara) | Lexara.dll beim Start laden (HD-Schriften von Stormhand) *(benötigt [Lexara](https://github.com/Stormhand-dev/Lexara---HD-Font-Renderer-for-WoW-3.3.5) – `dinput8.dll` in `Lexara.dll` umbenennen)* | 🟡 **[sicher - DLL riskant]** | St0ny | ✅ | – | – |\n",
           'en': "| [29](PATCHES.en.md#patch-lexara) | Load Lexara.dll at startup (HD fonts by Stormhand) *(requires [Lexara](https://github.com/Stormhand-dev/Lexara---HD-Font-Renderer-for-WoW-3.3.5) – rename `dinput8.dll` to `Lexara.dll`)* | 🟡 **[safe - DLL risky]** | St0ny | ✅ | – | – |\n"}
    LEG = {'de': [("Nr. 4, 10,\n    11, 23–25, 40, 41, 44–49, 73 und 80–84 (rote Warnung).", "Nr. 4, 10,\n    11, 23–25, 41, 42, 45–50, 74 und 81–85 (rote Warnung)."),
                  ("Nr. 26, 38, 43, 50, 61, 67 und 70–72 (orange Warnung).", "Nr. 26, 39, 44, 51, 62, 68 und 71–73 (orange Warnung)."),
                  ("Nr. 25, 26, 43, 50 und 61 (orange Warnung).", "Nr. 25, 26, 44, 51 und 62 (orange Warnung)."),
                  ("Nr. 9, 49, 62, 63 und 73. Das ist", "Nr. 9, 50, 63, 64 und 74. Das ist"),
                  ("erkannt oder blockiert werden kann: Nr. 27 und 28\n", "erkannt oder blockiert werden kann: Nr. 27–29\n"),
                  ("(Nr. 9, 49, 62, 63 und 73), entfernen", "(Nr. 9, 50, 63, 64 und 74), entfernen"),
                  ("zusammengestellt von Stormhand, und die Standard-Auswahl. Es enthält nur\n", "zusammengestellt von Stormhand, und die Standard-Auswahl. Es enthält\n"),
                  ("verwendet werden. Drei davon (Nr. 9, 62 und 63) vergrößern die `Wow.exe`; auf\n"
                   "Warmane war das kein Problem, andere Server können die Dateigröße aber prüfen. Welche Patches\n"
                   "dazugehören, zeigt die Spalte „Reforged“ in der\n",
                   "verwendet werden. Drei davon (Nr. 9, 63 und 64) vergrößern die `Wow.exe`; auf\n"
                   "Warmane war das kein Problem, andere Server können die Dateigröße aber prüfen.\n"
                   "Dazu kommt der Lexara-Lader (Nr. 29) für Stormhands HD-Schriften. Der Patch\n"
                   "selbst ist sicher, die `Lexara.dll` kann auf öffentlichen Servern aber erkannt\n"
                   "oder blockiert werden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts.\n"
                   "Welche Patches dazugehören, zeigt die Spalte „Reforged“ in der\n")],
           'en': [("No. 4, 10, 11, 23–25,\n    40, 41, 44–49, 73 and 80–84 (red warning).", "No. 4, 10, 11, 23–25,\n    41, 42, 45–50, 74 and 81–85 (red warning)."),
                  ("No. 26, 38, 43, 50, 61, 67 and 70–72 (orange warning).", "No. 26, 39, 44, 51, 62, 68 and 71–73 (orange warning)."),
                  ("No. 25, 26, 43, 50 and 61 (orange warning).", "No. 25, 26, 44, 51 and 62 (orange warning)."),
                  ("No. 9, 49,\n    62, 63 and 73. This does not", "No. 9, 50,\n    63, 64 and 74. This does not"),
                  ("detected or blocked on public servers: No. 27 and 28 (yellow note).", "detected or blocked on public servers: No. 27–29 (yellow note)."),
                  ("(No. 9, 49, 62, 63 and 73) also remove", "(No. 9, 50, 63, 64 and 74) also remove"),
                  ("together by Stormhand, and the default selection. It contains only patches\n", "together by Stormhand, and the default selection. It contains patches\n"),
                  ("(No. 9, 62 and 63) make `Wow.exe` larger; that was no problem on Warmane, but\n"
                   "other servers may check the file size. The \"Reforged\" column in the\n",
                   "(No. 9, 63 and 64) make `Wow.exe` larger; that was no problem on Warmane, but\n"
                   "other servers may check the file size. On top of that comes the Lexara loader\n"
                   "(No. 29) for Stormhand's HD fonts. The patch itself is safe, but `Lexara.dll`\n"
                   "may be detected or blocked on public servers; without `Lexara.dll` in the WoW\n"
                   "folder it does nothing. The \"Reforged\" column in the\n")]}
    for fn, md, lang in (('README.de.md', 'PATCHES.de.md', 'de'), ('README.md', 'PATCHES.en.md', 'en')):
        s = rd_md(fn)
        s = refs(s)
        s = re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(md), lambda m: '| [%d](%s#' % (mp(m.group(1)), md), s)
        m = re.search(r'(?m)^\| \[28\]\(%s#patch-wotlkext\).*\n' % re.escape(md), s); assert m
        s = s[:m.end()] + ROW[lang] + s[m.end():]
        for x, y in LEG[lang]: s = once(s, x, y, 'README ' + lang)
        wr_md(fn, s)
    # --- PATCHES: Abschnitt aus dev holen, anpassen, hinter wotlkext einfuegen
    for fn, lang in (('PATCHES.de.md', 'de'), ('PATCHES.en.md', 'en')):
        d = open(devwt + '/docs/' + fn, encoding='utf-8', newline='').read()
        a, b = section(d, 'lexara'); sec = d[a:b]
        if lang == 'de':
            sec = once(sec, '**Lexara.dll beim Start laden (HD-Schriften von Stormhand) [BETA]** *(Nr. 30, Autor: St0ny)* 🟠 **[ungetestet]**\n',
                            '**Lexara.dll beim Start laden (HD-Schriften von Stormhand)** *(Nr. 29, Autor: St0ny)* 🟡 **[sicher - DLL riskant]**\n', 'H')
            sec = once(sec, "Einstiegspunkt geladen, der Zeitpunkt passt also. Der Patch verträgt sich mit\n"
                            "dem voice.dll-Lader (Nr. 31), der nur den Sprung direkt danach ändert.\n",
                            "Einstiegspunkt geladen, der Zeitpunkt passt also.\n", 'voice-Satz')
            sec = once(sec, BETA_DE, DLLBOX_DE, 'Kasten')
        else:
            sec = once(sec, '**Load Lexara.dll at startup (HD fonts by Stormhand) [BETA]** *(No. 30, Author: St0ny)* 🟠 **[untested]**\n',
                            '**Load Lexara.dll at startup (HD fonts by Stormhand)** *(No. 29, Author: St0ny)* 🟡 **[safe - DLL risky]**\n', 'H')
            sec = once(sec, "proxy DLL is loaded before the entry point as well, so the timing matches. The\n"
                            "patch works together with the voice.dll loader (No. 31), which only changes\n"
                            "the jump right after it.\n",
                            "proxy DLL is loaded before the entry point as well, so the timing matches.\n", 'voice-Satz')
            sec = once(sec, BETA_EN, DLLBOX_EN, 'box')
        assert 'Nr. 3' not in sec.replace('Nr. 29', '') and 'No. 3' not in sec.replace('No. 29', '')
        s = rd_md(fn)
        s = refs(s)
        a, b = section(s, 'wotlkext')
        s = s[:b] + sec + s[b:]
        wr_md(fn, s)

if mode in ('dev', 'lights'):
    run_status(RF[mode])
elif mode == 'main':
    run_main(sys.argv[3])
print(mode, 'OK')

# Neue Kennzeichnung "DLL riskant" / "DLL risky" fuer awesome + wotlkext.
# Aufruf: python3 apply_dll.py <worktree>
# Jede Ersetzung muss genau einmal passen (assert), sonst Abbruch ohne Schreiben.
import re, sys

wt = sys.argv[1]
PS = wt + '/apply_patches.ps1'
D = wt + '/docs/'

def rep(s, old, new, label):
    n = s.count(old)
    assert n == 1, '%s: %d Treffer' % (label, n)
    return s.replace(old, new)

# ---------------- apply_patches.ps1 (ASCII, CRLF bleibt erhalten) ----------------
raw = open(PS, encoding='ascii', newline='').read()
assert '\r\n' in raw and raw.count('\r\n') == raw.count('\n'), 'ps1 nicht durchgehend CRLF'
assert raw.count('\r\r') == 0
assert not re.search(r'\$dll\b', raw), '$dll schon vorhanden'
assert 'DllRisky' not in raw and 'TagDll' not in raw
s = raw.replace('\r\n', '\n')

s = rep(s,
"        StartWarn4    = '[ingame ungetestet] (moeglicherweise verbuggt), [ungetestet], [Exe wird groesser] (Bann-Risiko).'\n"
"        StartWarn5    = 'Im Zweifel pruefe die Richtlinien deines Servers, bevor du eine gepatchte Wow.exe dort benutzt.'\n"
"        StartWarn6    = 'Benutzung auf eigene Gefahr.'\n",
"        StartWarn4    = '[ingame ungetestet] (moeglicherweise verbuggt), [ungetestet], [Exe wird groesser] (Bann-Risiko),'\n"
"        StartWarn5    = '[DLL riskant] (Patch sicher, die DLL kann auf oeffentlichen Servern erkannt/blockiert werden).'\n"
"        StartWarn6    = 'Im Zweifel pruefe die Richtlinien deines Servers, bevor du eine gepatchte Wow.exe dort benutzt.'\n"
"        StartWarn7    = 'Benutzung auf eigene Gefahr.'\n", 'StartWarn DE')

s = rep(s,
"        StartWarn4    = '[untested ingame] (possibly buggy), [untested], [exe grows] (possible ban risk).'\n"
"        StartWarn5    = 'If in doubt, check the rules of your server before using a patched Wow.exe there.'\n"
"        StartWarn6    = 'Use at your own risk.'\n",
"        StartWarn4    = '[untested ingame] (possibly buggy), [untested], [exe grows] (possible ban risk),'\n"
"        StartWarn5    = '[DLL risky] (the patch is safe, but the DLL may be detected/blocked on public servers).'\n"
"        StartWarn6    = 'If in doubt, check the rules of your server before using a patched Wow.exe there.'\n"
"        StartWarn7    = 'Use at your own risk.'\n", 'StartWarn EN')

s = rep(s,
"Say (T 'StartWarn6') 'Yellow'\n",
"Say (T 'StartWarn6') 'Yellow'\n"
"Say (T 'StartWarn7') 'Yellow'\n", 'Say StartWarn7')

s = rep(s,
"        GrowBan       = 'Das ist keine sichere Bann-Gefahr, aber ein Risiko: Manche Server pruefen die Groesse der Wow.exe.'\n",
"        GrowBan       = 'Das ist keine sichere Bann-Gefahr, aber ein Risiko: Manche Server pruefen die Groesse der Wow.exe.'\n"
"        DllHead       = 'HINWEIS: Diese Patches laden eine DLL, die auf oeffentlichen Servern erkannt oder blockiert werden kann:'\n"
"        DllWarn       = 'Der Patch selbst ist sicher - die DLL nur auf Servern nutzen, die sie erlauben.'\n", 'Dll DE')

s = rep(s,
"        GrowBan       = 'This does not mean a certain ban, but it is a risk: some servers check the size of Wow.exe.'\n",
"        GrowBan       = 'This does not mean a certain ban, but it is a risk: some servers check the size of Wow.exe.'\n"
"        DllHead       = 'NOTE: These patches load a DLL that may be detected or blocked on public servers:'\n"
"        DllWarn       = 'The patch itself is safe - only use the DLL on servers that allow it.'\n", 'Dll EN')

s = rep(s,
"        TagGrow       = 'Exe wird groesser'\n",
"        TagGrow       = 'Exe wird groesser'\n"
"        TagDll        = 'DLL riskant'\n", 'TagDll DE')

s = rep(s,
"        TagGrow       = 'exe grows'\n",
"        TagGrow       = 'exe grows'\n"
"        TagDll        = 'DLL risky'\n", 'TagDll EN')

s = rep(s,
"# GameUntested = Funktion im Spiel ungetestet (4), dazu GrowsExe.\n",
"# GameUntested = Funktion im Spiel ungetestet (4), dazu GrowsExe und DllRisky.\n", 'PatchTags Kommentar')

s = rep(s,
"    if ($p.GrowsExe) { $tags += T 'TagGrow' }\n",
"    if ($p.GrowsExe) { $tags += T 'TagGrow' }\n"
"    if ($p.DllRisky) { $tags += T 'TagDll' }\n", 'PatchTags')

s = rep(s,
"#    GrowsExe - optional: $true, wenn der Patch immer eine Sektion anhaengt und\n"
"#            die Wow.exe damit groesser macht (erzeugt einen Bann-Hinweis)\n",
"#    GrowsExe - optional: $true, wenn der Patch immer eine Sektion anhaengt und\n"
"#            die Wow.exe damit groesser macht (erzeugt einen Bann-Hinweis)\n"
"#    DllRisky - optional: $true bei DLL-Ladern, deren DLL auf oeffentlichen\n"
"#            Servern erkannt oder blockiert werden kann - der Patch selbst ist\n"
"#            sicher (erzeugt einen gelben Hinweis)\n", 'Flag-Doku')

s = rep(s,
"    Say (T 'GrowBan') 'Yellow'\n"
"}\n",
"    Say (T 'GrowBan') 'Yellow'\n"
"}\n"
"$dll = @()\n"
"foreach ($p in $chosen) { if ($p.DllRisky) { $dll += PatchRef $p } }\n"
"if ($dll.Count -gt 0) {\n"
"    Write-Host ''\n"
"    Say (T 'DllHead') 'Yellow'\n"
"    foreach ($m in $dll) { Say \"  - $m\" 'Yellow' }\n"
"    Say (T 'DllWarn') 'Yellow'\n"
"}\n", 'Warnblock')

s = rep(s,
"    @{ Id = 'awesome'; Cat = 'dll'; On = $true; Needs = @('laa')\n",
"    @{ Id = 'awesome'; Cat = 'dll'; On = $true; Needs = @('laa'); DllRisky = $true\n", 'awesome Flag')

s = rep(s,
"    @{ Id = 'wotlkext'; Cat = 'dll'; On = $false; Needs = @('laa')\n",
"    @{ Id = 'wotlkext'; Cat = 'dll'; On = $false; Needs = @('laa'); DllRisky = $true\n", 'wotlkext Flag')

s.encode('ascii')
open(PS, 'w', encoding='ascii', newline='').write(s.replace('\n', '\r\n'))

# Nummern der DllRisky-Patches (1-basiert) fuer die README-Liste
ids = re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$", s)
nums = [i + 1 for i, (_, h) in enumerate(ids) if 'DllRisky = $true' in h]
assert len(nums) == 2 and [ids[n - 1][0] for n in nums] == ['awesome', 'wotlkext'], nums
nde = 'Nr. %d und %d' % tuple(nums)
nen = 'No. %d and %d' % tuple(nums)

# ---------------- Docs (UTF-8, LF) ----------------
def rd(fn):
    t = open(D + fn, encoding='utf-8', newline='').read()
    assert '\r' not in t, fn + ' hat CR'
    return t

def wr(fn, t):
    open(D + fn, 'w', encoding='utf-8', newline='').write(t)

def row(t, md, pid, old, new, label):
    lines = t.split('\n')
    hit = [i for i, l in enumerate(lines) if l.startswith('| [') and '(%s#patch-%s)' % (md, pid) in l]
    assert len(hit) == 1, label
    l = lines[hit[0]]
    assert l.count(old) == 1, label + ' Badge'
    lines[hit[0]] = l.replace(old, new)
    return '\n'.join(lines)

def head(t, pid, old, new, label):
    a = '<a id="patch-%s"></a>\n' % pid
    assert t.count(a) == 1, label
    i = t.index(a) + len(a)
    j = t.index('\n', i)
    h = t[i:j]
    assert h.endswith(' ' + old), label + ' Badge: ' + h
    return t[:i] + h[:-len(old)] + new + t[j:]

# README.de.md
t = rd('README.de.md')
t = row(t, 'PATCHES.de.md', 'awesome', '| 🟢 **[sicher]** |', '| 🟡 **[sicher - DLL riskant]** |', 'de awesome')
t = row(t, 'PATCHES.de.md', 'wotlkext', '| 🟢 **[sicher]** |', '| 🟡 **[sicher - DLL riskant]** |', 'de wotlkext')
t = rep(t,
"| 🟡 **[Exe wird größer]** | Der Patch hängt eine Sektion an die `Wow.exe` an. Keine sichere Bann-Gefahr, aber ein Risiko: Manche Server prüfen die Dateigröße. | gelber Hinweis |\n",
"| 🟡 **[Exe wird größer]** | Der Patch hängt eine Sektion an die `Wow.exe` an. Keine sichere Bann-Gefahr, aber ein Risiko: Manche Server prüfen die Dateigröße. | gelber Hinweis |\n"
"| 🟡 **[DLL riskant]** | Der Patch selbst ist sicher, er lädt aber eine DLL, die auf öffentlichen Servern erkannt oder blockiert werden kann. Nur dort einsetzen, wo die DLL erlaubt ist. | gelber Hinweis |\n", 'de Legende Tabelle')
t = rep(t,
"Orange vor Gelb), ein grüner Punkt wird gelb, wenn die Exe größer wird. Zum\n"
"Beispiel 🟡 **[sicher - Exe wird größer]**, 🔴 **[unsicher - Exe wird größer]**,\n"
"🟠 **[ungetestet - Exe wird größer]** oder 🔴 **[unsicher - ingame ungetestet]**.\n",
"Orange vor Gelb), ein grüner Punkt wird gelb, wenn die Exe größer wird oder\n"
"die DLL riskant ist. Zum Beispiel 🟡 **[sicher - Exe wird größer]**,\n"
"🟡 **[sicher - DLL riskant]**, 🔴 **[unsicher - Exe wird größer]**,\n"
"🟠 **[ungetestet - Exe wird größer]** oder 🔴 **[unsicher - ingame ungetestet]**.\n", 'de Legende Absatz')
t = rep(t,
"    aber ein Risiko: Manche Server prüfen die Dateigröße (gelber Hinweis). Alle\n"
"    anderen Patches ändern die Dateigröße nicht.\n",
"    aber ein Risiko: Manche Server prüfen die Dateigröße (gelber Hinweis). Alle\n"
"    anderen Patches ändern die Dateigröße nicht.\n"
"  - 🟡 **DLL riskant** – der Patch selbst ist sicher, er lädt aber eine DLL, die\n"
"    auf öffentlichen Servern erkannt oder blockiert werden kann: %s\n"
"    (gelber Hinweis). Nur dort einsetzen, wo die DLL erlaubt ist.\n" % nde, 'de Hinweise')
wr('README.de.md', t)

# README.md
t = rd('README.md')
t = row(t, 'PATCHES.en.md', 'awesome', '| 🟢 **[safe]** |', '| 🟡 **[safe - DLL risky]** |', 'en awesome')
t = row(t, 'PATCHES.en.md', 'wotlkext', '| 🟢 **[safe]** |', '| 🟡 **[safe - DLL risky]** |', 'en wotlkext')
t = rep(t,
"| 🟡 **[exe grows]** | The patch appends a section to `Wow.exe`. Not a certain ban, but a risk: some servers check the file size. | yellow note |\n",
"| 🟡 **[exe grows]** | The patch appends a section to `Wow.exe`. Not a certain ban, but a risk: some servers check the file size. | yellow note |\n"
"| 🟡 **[DLL risky]** | The patch itself is safe, but it loads a DLL that may be detected or blocked on public servers. Only use it where the DLL is allowed. | yellow note |\n", 'en Legende Tabelle')
t = rep(t,
"yellow), and a green dot turns yellow when the exe grows. For example\n"
"🟡 **[safe - exe grows]**, 🔴 **[unsafe - exe grows]**,\n"
"🟠 **[untested - exe grows]** or 🔴 **[unsafe - untested ingame]**.\n",
"yellow), and a green dot turns yellow when the exe grows or the DLL is\n"
"risky. For example 🟡 **[safe - exe grows]**, 🟡 **[safe - DLL risky]**,\n"
"🔴 **[unsafe - exe grows]**, 🟠 **[untested - exe grows]** or\n"
"🔴 **[unsafe - untested ingame]**.\n", 'en Legende Absatz')
t = rep(t,
"    servers check the file size (yellow note). All other patches do not change\n"
"    the file size.\n",
"    servers check the file size (yellow note). All other patches do not change\n"
"    the file size.\n"
"  - 🟡 **DLL risky** – the patch itself is safe, but it loads a DLL that may be\n"
"    detected or blocked on public servers: %s (yellow note). Only\n"
"    use it where the DLL is allowed.\n" % nen, 'en Hinweise')
wr('README.md', t)

# PATCHES.de.md
t = rd('PATCHES.de.md')
t = head(t, 'awesome', '🟢 **[sicher]**', '🟡 **[sicher - DLL riskant]**', 'de awesome Kopf')
t = head(t, 'wotlkext', '🟢 **[sicher]**', '🟡 **[sicher - DLL riskant]**', 'de wotlkext Kopf')
t = rep(t,
"> [!NOTE]\n"
"> Der Patch selbst ist unkritisch, er lädt nur eine DLL, die hier nicht\n"
"> enthalten ist. Erst die geladene `AwesomeWotlkLib.dll` kann auf Servern mit\n"
"> Anti-Cheat auffallen – also nur dort einsetzen, wo awesome_wotlk erlaubt ist.\n",
"> [!WARNING]\n"
"> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten\n"
"> ist. Die geladene `AwesomeWotlkLib.dll` kann aber auf öffentlichen Servern\n"
"> erkannt oder blockiert werden – also nur dort einsetzen, wo awesome_wotlk\n"
"> erlaubt ist.\n", 'de awesome Box')
t = rep(t,
"> [!NOTE]\n"
"> Der Patch selbst ist unkritisch, er lädt nur eine DLL, die hier nicht\n"
"> enthalten ist. WotLK-Extensions ist für eigene Server-Projekte gedacht; laut\n"
"> dem Projekt können manche Server Aufrufe seiner Lua-Funktionen erkennen. Nur\n"
"> dort einsetzen, wo WotLK-Extensions erlaubt ist.\n",
"> [!WARNING]\n"
"> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten\n"
"> ist. Die geladene `WotLKExtensions.dll` kann aber auf öffentlichen Servern\n"
"> erkannt oder blockiert werden; laut dem Projekt können manche Server Aufrufe\n"
"> seiner Lua-Funktionen erkennen. WotLK-Extensions ist für eigene\n"
"> Server-Projekte gedacht – nur dort einsetzen, wo es erlaubt ist.\n", 'de wotlkext Box')
wr('PATCHES.de.md', t)

# PATCHES.en.md
t = rd('PATCHES.en.md')
t = head(t, 'awesome', '🟢 **[safe]**', '🟡 **[safe - DLL risky]**', 'en awesome Kopf')
t = head(t, 'wotlkext', '🟢 **[safe]**', '🟡 **[safe - DLL risky]**', 'en wotlkext Kopf')
t = rep(t,
"> [!NOTE]\n"
"> The patch itself is harmless, it only loads a DLL that is not included here.\n"
"> Only the loaded `AwesomeWotlkLib.dll` may be noticed by servers with\n"
"> anti-cheat – so use it only where awesome_wotlk is allowed.\n",
"> [!WARNING]\n"
"> The patch itself is safe, it only loads a DLL that is not included here.\n"
"> The loaded `AwesomeWotlkLib.dll`, however, may be detected or blocked on\n"
"> public servers – so use it only where awesome_wotlk is allowed.\n", 'en awesome Box')
t = rep(t,
"> [!NOTE]\n"
"> The patch itself is harmless, it only loads a DLL that is not included here.\n"
"> WotLK-Extensions is meant for your own server projects; according to the\n"
"> project, some servers can detect calls to its Lua functions. Only use it\n"
"> where WotLK-Extensions is allowed.\n",
"> [!WARNING]\n"
"> The patch itself is safe, it only loads a DLL that is not included here.\n"
"> The loaded `WotLKExtensions.dll`, however, may be detected or blocked on\n"
"> public servers; according to the project, some servers can detect calls to\n"
"> its Lua functions. WotLK-Extensions is meant for your own server projects –\n"
"> only use it where it is allowed.\n", 'en wotlkext Box')
wr('PATCHES.en.md', t)

print(wt.split('/')[-1], 'OK', nde, '/', nen)

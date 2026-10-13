#!/usr/bin/env python3
# Neue orange Kennzeichnung "riskant" (Blocked): wird auf manchen Servern geblockt. Nr. 10 bekommt sie statt BanRisk.
# Aufruf: edit_blocked.py <Ordner mit apply_patches.ps1 und docs/>
import sys, os
root = sys.argv[1]
def edit_ps1(p, pairs):
    s = open(p, 'rb').read().decode('ascii').replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70], s.count(a)); s = s.replace(a, b)
    s.encode('ascii'); open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
def edit_md(p, pairs):
    s = open(p, encoding='utf-8').read(); assert '\r' not in s
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:70], s.count(a)); s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

edit_ps1(os.path.join(root, 'apply_patches.ps1'), [
("""        CheatBan      = 'Das kann zu einem Bann fuehren - nur auf Servern nutzen, die das erlauben!'
""", """        CheatBan      = 'Das kann zu einem Bann fuehren - nur auf Servern nutzen, die das erlauben!'
        BlockedHead   = 'VORSICHT - riskant: Diese Patches werden auf manchen Servern geblockt:'
        BlockedWarn   = 'Im Zweifel die Regeln deines Servers pruefen.'
"""),
("""        CheatBan      = 'This can lead to a ban - only use them on servers that allow it!'
""", """        CheatBan      = 'This can lead to a ban - only use them on servers that allow it!'
        BlockedHead   = 'CAUTION - risky: these patches get blocked on some servers:'
        BlockedWarn   = 'If in doubt, check the rules of your server.'
"""),
("""        TagBan        = 'unsicher'
""", """        TagBan        = 'unsicher'
        TagBlocked    = 'riskant'
"""),
("""        TagBan        = 'unsafe'
""", """        TagBan        = 'unsafe'
        TagBlocked    = 'risky'
"""),
("""# GameUntested = Funktion im Spiel ungetestet (4), dazu GrowsExe und DllRisky.
""", """# GameUntested = Funktion im Spiel ungetestet (4), Blocked = riskant, wird auf
# manchen Servern geblockt (5), dazu GrowsExe und DllRisky.
"""),
("""    if ($p.BanRisk) { $tags += T 'TagBan' }
""", """    if ($p.BanRisk) { $tags += T 'TagBan' }
    if ($p.Blocked) { $tags += T 'TagBlocked' }
"""),
("""#    Warn-Codes - Patches ohne die drei folgenden Flags sind sicher (Code 1,
""", """#    Warn-Codes - Patches ohne die vier folgenden Flags sind sicher (Code 1,
"""),
("""#    GameUntested - optional: $true, wenn die Funktion im Spiel ungetestet
#            ist - moeglicherweise verbuggt (Code 4, oranger Hinweis)
""", """#    GameUntested - optional: $true, wenn die Funktion im Spiel ungetestet
#            ist - moeglicherweise verbuggt (Code 4, oranger Hinweis)
#    Blocked - optional: $true, wenn der Patch auf manchen Servern geblockt
#            wird - riskant (Code 5, oranger Hinweis)
"""),
("""    @{ Id = 'rce'; Cat = 'security'; On = $false; BanRisk = $true; GameUntested = $true
""", """    @{ Id = 'rce'; Cat = 'security'; On = $false; Blocked = $true; GameUntested = $true
"""),
("""    Say (T 'CheatBan') 'Red'
}
""", """    Say (T 'CheatBan') 'Red'
}
$blocked = @()
foreach ($p in $chosen) { if ($p.Blocked) { $blocked += PatchRef $p } }
if ($blocked.Count -gt 0) {
    Write-Host ''
    Say (T 'BlockedHead') 'DarkYellow'
    foreach ($m in $blocked) { Say "  - $m" 'DarkYellow' }
    Say (T 'BlockedWarn') 'DarkYellow'
}
"""),
])

edit_md(os.path.join(root, 'docs', 'README.de.md'), [
("""| 🔴 **[unsicher]** | Bestätigte Bann-Gefahr: kann auf vielen Servern zu einem Bann führen. Nur auf Servern nutzen, die das erlauben. | rote Warnung |
""", """| 🔴 **[unsicher]** | Bestätigte Bann-Gefahr: kann auf vielen Servern zu einem Bann führen. Nur auf Servern nutzen, die das erlauben. | rote Warnung |
| 🟠 **[riskant]** | Wird auf manchen Servern geblockt. Im Zweifel die Regeln deines Servers prüfen. | orange Warnung |
"""),
("""| Remote Code Execution Exploit Fix v2 [BETA] | 🔴 **[unsicher - ingame ungetestet]** |""",
 """| Remote Code Execution Exploit Fix v2 [BETA] | 🟠 **[riskant - ingame ungetestet]** |"""),
("""  - 🔴 **unsicher** – Bann-Gefahr, kann auf vielen Servern zu einem Bann führen: Nr. 4, 10,
    11, 23–25, 44, 45, 48–53, 79 und 87–91 (rote Warnung).
""", """  - 🔴 **unsicher** – Bann-Gefahr, kann auf vielen Servern zu einem Bann führen: Nr. 4,
    11, 23–25, 44, 45, 48–53, 79 und 87–91 (rote Warnung).
  - 🟠 **riskant** – wird auf manchen Servern geblockt: Nr. 10 (orange Warnung).
"""),
])
edit_md(os.path.join(root, 'docs', 'README.md'), [
("""| 🔴 **[unsafe]** | Confirmed ban risk: can lead to a ban on many servers. Only use it on servers that allow it. | red warning |
""", """| 🔴 **[unsafe]** | Confirmed ban risk: can lead to a ban on many servers. Only use it on servers that allow it. | red warning |
| 🟠 **[risky]** | Gets blocked on some servers. If in doubt, check the rules of your server. | orange warning |
"""),
("""| Remote code execution exploit fix v2 [BETA] | 🔴 **[unsafe - untested ingame]** |""",
 """| Remote code execution exploit fix v2 [BETA] | 🟠 **[risky - untested ingame]** |"""),
("""  - 🔴 **unsafe** – ban risk, can lead to a ban on many servers: No. 4, 10, 11, 23–25,
    44, 45, 48–53, 79 and 87–91 (red warning).
""", """  - 🔴 **unsafe** – ban risk, can lead to a ban on many servers: No. 4, 11, 23–25,
    44, 45, 48–53, 79 and 87–91 (red warning).
  - 🟠 **risky** – gets blocked on some servers: No. 10 (orange warning).
"""),
])
edit_md(os.path.join(root, 'docs', 'PATCHES.de.md'), [
("""*(Nr. 10, Autor: Brady Russell (original by stoneharry / Robinsch))* 🔴 **[unsicher - ingame ungetestet]**""",
 """*(Nr. 10, Autor: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[riskant - ingame ungetestet]**"""),
("""> Öffentliche Server können die Änderung über Warden erkennen – auf
> öffentlichen Servern besteht Bann-Gefahr.
""", """> Riskant: Auf manchen Servern wird dieser Patch geblockt. Im Zweifel die
> Regeln deines Servers prüfen.
"""),
])
edit_md(os.path.join(root, 'docs', 'PATCHES.en.md'), [
("""*(No. 10, Author: Brady Russell (original by stoneharry / Robinsch))* 🔴 **[unsafe - untested ingame]**""",
 """*(No. 10, Author: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[risky - untested ingame]**"""),
("""> Public servers can detect the change through Warden – there is a risk of a
> ban on public servers.
""", """> Risky: some servers block this patch. If in doubt, check the rules of your
> server.
"""),
])
print('edits ok')

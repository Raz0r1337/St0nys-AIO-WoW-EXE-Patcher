import sys
def ed(p,pairs,crlf=False):
    s=open(p,encoding='utf-8',newline='').read()
    if crlf: s=s.replace('\r\n','\n')
    for o,n in pairs:
        if s.count(o)!=1: sys.exit(p+': '+o[:80])
        s=s.replace(o,n)
    if crlf: s=s.replace('\n','\r\n')
    open(p,'w',encoding='utf-8',newline='').write(s)
ed('apply_patches.ps1',[
("""    if ($v -notmatch '^\\d{1,5}$' -or [int]$v -gt 65535) { return (L 'Eine Zahl von 0 bis 65535.' 'A number from 0 to 65535.') }
""","""    # Server (AzerothCore, TrinityCore) behandeln Builds bis 6141 als Classic-
    # Client (Pre-BC) mit anderem Login-Protokoll - damit kaeme ein 3.3.5-Client
    # nicht mehr auf den Server. Darum erst ab 6142.
    if ($v -notmatch '^\\d{1,5}$' -or [int]$v -lt 6142 -or [int]$v -gt 65535) {
        return (L 'Eine Zahl von 6142 bis 65535 (bis 6141 halten Server den Client fuer einen Classic-Client).' 'A number from 6142 to 65535 (up to 6141 servers treat the client as a Classic client).')
    }
"""),
("       PromptDe = 'Neue Build-Nummer, 0 bis 65535'\n       PromptEn = 'New build number, 0 to 65535'\n",
 "       PromptDe = 'Neue Build-Nummer, 6142 bis 65535'\n       PromptEn = 'New build number, 6142 to 65535'\n"),
],crlf=True)
ed('README.md',[("""Setzt eine neue Build-Nummer (0 bis 65535, Original `12340`): die interne
Build-Nummer, die sichtbare Build-Nummer und den vierten Teil der FileVersion.
""","""Setzt eine neue Build-Nummer (6142 bis 65535, Original `12340`): die interne
Build-Nummer, die sichtbare Build-Nummer und den vierten Teil der FileVersion.
Builds bis 6141 lässt der Patcher nicht zu: Server wie AzerothCore oder
TrinityCore halten den Client dann für einen Classic-Client (Pre-BC) und
verwenden ein anderes Login-Protokoll – ein 3.3.5-Client kommt so nicht mehr auf
den Server.

> [!TIP]
> **AzerothCore:** Der Authserver lässt nur Builds zu, die in der Tabelle
> `build_info` der Auth-Datenbank stehen. Für einen eigenen Build, z. B. `12341`:
>
> ```sql
> INSERT INTO build_info (majorVersion, minorVersion, bugfixVersion, hotfixVersion, build, winChecksumSeed, macChecksumSeed)
> VALUES (3, 3, 5, 'a', 12341, NULL, NULL);
> UPDATE realmlist SET gamebuild = 12341 WHERE id = 1;
> ```
>
> `winChecksumSeed` leer lassen (wird nur mit `StrictVersionCheck = 1` in der
> `authserver.conf` geprüft und passt zu einer gepatchten Exe ohnehin nicht).
> Major/Minor/Bugfix sind nur Anzeige in der Realmliste. Danach den Authserver
> neu starten – er liest `build_info` nur beim Start. Ein Realm nimmt nur den
> Build aus `realmlist.gamebuild` an; Spieler mit älterem Client sehen ihn als
> offline.
""")])
ed('README.en.md',[("""Sets a new build number (0 to 65535, original `12340`): the internal build
number, the visible build number and the fourth part of the FileVersion.
""","""Sets a new build number (6142 to 65535, original `12340`): the internal build
number, the visible build number and the fourth part of the FileVersion. The
patcher does not allow builds up to 6141: servers like AzerothCore or
TrinityCore then treat the client as a Classic client (pre-BC) and use a
different login protocol – a 3.3.5 client can no longer get onto the server.

> [!TIP]
> **AzerothCore:** the authserver only accepts builds listed in the `build_info`
> table of the auth database. For a build of your own, e.g. `12341`:
>
> ```sql
> INSERT INTO build_info (majorVersion, minorVersion, bugfixVersion, hotfixVersion, build, winChecksumSeed, macChecksumSeed)
> VALUES (3, 3, 5, 'a', 12341, NULL, NULL);
> UPDATE realmlist SET gamebuild = 12341 WHERE id = 1;
> ```
>
> Leave `winChecksumSeed` empty (it is only checked with `StrictVersionCheck = 1`
> in `authserver.conf` and would not match a patched exe anyway).
> Major/minor/bugfix are only displayed in the realm list. Restart the
> authserver afterwards – it reads `build_info` only at startup. A realm only
> accepts the build in `realmlist.gamebuild`; players with an older client see
> it as offline.
""")])
print('ok')

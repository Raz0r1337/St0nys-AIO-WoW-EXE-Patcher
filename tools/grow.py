import sys,re
def ed(p,pairs,crlf=False):
    s=open(p,encoding='utf-8',newline='').read()
    if crlf: s=s.replace('\r\n','\n')
    for o,n in pairs:
        if s.count(o)!=1: sys.exit(p+': '+o)
        s=s.replace(o,n)
    if crlf: s=s.replace('\n','\r\n')
    open(p,'w',encoding='utf-8',newline='').write(s)
ed('apply_patches.ps1',[
("    @{ Id = 'hdportraits'; Cat = 'graphics'; On = $false\n","    @{ Id = 'hdportraits'; Cat = 'graphics'; On = $false; GrowsExe = $true\n"),
("       De = 'HD Unit-Frame Portraits: 256x256 (live 3D-Portraits)'\n       En = 'HD unit frame portraits: 256x256 (live 3D portraits)'\n",
 "       De = 'HD Unit-Frame Portraits: 256x256 (live 3D-Portraits)'\n       En = 'HD unit frame portraits: 256x256 (live 3D portraits)'\n       NoteDe = 'Exe wird groesser - Bann-Gefahr'\n       NoteEn = 'exe grows - ban risk'\n"),
("    @{ Id = 'camera'; Cat = 'window'; On = $false\n","    @{ Id = 'camera'; Cat = 'window'; On = $false; GrowsExe = $true\n"),
("       NoteDe = 'noch nicht 100% fertig'\n       NoteEn = 'not 100% finished yet'\n","       NoteDe = 'noch nicht 100% fertig; Exe wird groesser - Bann-Gefahr'\n       NoteEn = 'not 100% finished yet; exe grows - ban risk'\n"),
("    @{ Id = 'doublejump'; Cat = 'gameplay'; On = $false\n","    @{ Id = 'doublejump'; Cat = 'gameplay'; On = $false; GrowsExe = $true\n"),
("       De = 'Doppelsprung (weitere Spruenge in der Luft)'\n       En = 'Double jump (more jumps in the air)'\n       NoteDe = 'kann vom Server als Cheat erkannt werden'\n       NoteEn = 'may be detected as cheating by the server'\n",
 "       De = 'Doppelsprung (weitere Spruenge in der Luft)'\n       En = 'Double jump (more jumps in the air)'\n       NoteDe = 'kann vom Server als Cheat erkannt werden; Exe wird groesser - Bann-Gefahr'\n       NoteEn = 'may be detected as cheating by the server; exe grows - ban risk'\n"),
("#    Needs - optional: Ids von Patches, ohne die dieser nicht voll wirkt\n",
 "#    GrowsExe - optional: $true, wenn der Patch immer eine Sektion anhaengt und\n#            die Wow.exe damit groesser macht (erzeugt einen Bann-Hinweis)\n#    Needs - optional: Ids von Patches, ohne die dieser nicht voll wirkt\n"),
("        ConflictBan   = 'Zusammen funktionieren sie, aber viele Server tolerieren eine veraenderte Groesse der Wow.exe nicht - das kann zu einem Bann fuehren!'\n",
 "        ConflictBan   = 'Zusammen funktionieren sie, aber viele Server tolerieren eine veraenderte Groesse der Wow.exe nicht - das kann zu einem Bann fuehren!'\n        GrowHead      = 'HINWEIS: Diese Patches haengen eine Sektion an und machen die Wow.exe groesser:'\n        GrowBan       = 'Viele Server tolerieren eine veraenderte Groesse der Wow.exe nicht - das kann zu einem Bann fuehren!'\n"),
("        ConflictBan   = 'They work together, but many servers do not tolerate a changed size of Wow.exe - this can lead to a ban!'\n",
 "        ConflictBan   = 'They work together, but many servers do not tolerate a changed size of Wow.exe - this can lead to a ban!'\n        GrowHead      = 'NOTE: These patches append a section and make Wow.exe larger:'\n        GrowBan       = 'Many servers do not tolerate a changed size of Wow.exe - this can lead to a ban!'\n"),
("        Say (T 'ConflictBan') 'Red'\n    }\n}\n",
 "        Say (T 'ConflictBan') 'Red'\n    }\n}\n$grow = @()\nforeach ($p in $chosen) { if ($p.GrowsExe) { $grow += PatchName $p } }\nif ($grow.Count -gt 0) {\n    Write-Host ''\n    Say (T 'GrowHead') 'Yellow'\n    foreach ($m in $grow) { Say \"  - $m\" 'Yellow' }\n    Say (T 'GrowBan') 'Red'\n}\n"),
],crlf=True)

def readme(p,lang):
    s=open(p,encoding='utf-8',newline='').read()
    if lang=='de':
        rows=[("| HD Unit-Frame Portraits: 256x256 (live 3D-Portraits) |","| HD Unit-Frame Portraits: 256x256 (live 3D-Portraits) *(Exe wird größer – Bann-Gefahr)* |"),
              ("*(noch nicht 100 % fertig)* |","*(noch nicht 100 % fertig; Exe wird größer – Bann-Gefahr)* |"),
              ("*(fragt den Wert ab, kann vom Server als Cheat erkannt werden)* | Alyst3r","*(fragt den Wert ab, kann vom Server als Cheat erkannt werden; Exe wird größer – Bann-Gefahr)* | Alyst3r")]
        heads=[r'\*\*HD Unit-Frame Portraits: 256x256 statt 64x64\*\*',r'\*\*CameraReforged \[BETA\][^\n]*\*\*',r'\*\*Doppelsprung \(weitere Sprünge in der Luft\)\*\*']
        box="> [!WARNING]\n> Dieser Patch hängt eine eigene Sektion an, die `Wow.exe` wird dadurch größer.\n> **Viele Server tolerieren eine veränderte Dateigröße der `Wow.exe` nicht – das\n> kann zu einem Bann führen.**\n\n"
    else:
        rows=[("| HD unit frame portraits: 256x256 (live 3D portraits) |","| HD unit frame portraits: 256x256 (live 3D portraits) *(exe grows – ban risk)* |"),
              ("*(not 100% finished yet)* |","*(not 100% finished yet; exe grows – ban risk)* |"),
              ("*(asks for the value, may be detected as cheating by the server)* | Alyst3r","*(asks for the value, may be detected as cheating by the server; exe grows – ban risk)* | Alyst3r")]
        heads=[r'\*\*HD unit frame portraits[^\n]*\*\*',r'\*\*CameraReforged \[BETA\][^\n]*\*\*',r'\*\*Double jump \(more jumps in the air\)\*\*']
        box="> [!WARNING]\n> This patch appends a section of its own, which makes `Wow.exe` larger. **Many\n> servers do not tolerate a changed file size of `Wow.exe` – this can lead to a\n> ban.**\n\n"
    for o,n in rows:
        if s.count(o)!=1: sys.exit(p+' row '+o)
        s=s.replace(o,n)
    for h in heads:
        m=list(re.finditer(r'(?m)^'+h+r' \*\(', s))
        if len(m)!=1: sys.exit(p+' head '+h+str(len(m)))
        k=m[0].end()
        nxt=re.search(r'(?m)^(\*\*[^\n]*\*\((?:Nr|No)\. \d+[,)]|### |## |---)', s[k:])
        pos=k+nxt.start()
        s=s[:pos]+box+s[pos:]
    open(p,'w',encoding='utf-8',newline='').write(s)
readme('README.md','de'); readme('README.en.md','en')
print('ok')

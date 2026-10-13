import sys
def ed(p,pairs,crlf=False):
    s=open(p,encoding='utf-8',newline='').read()
    if crlf: s=s.replace('\r\n','\n')
    for o,n in pairs:
        if s.count(o)!=1: sys.exit(p+': '+o)
        s=s.replace(o,n)
    if crlf: s=s.replace('\n','\r\n')
    open(p,'w',encoding='utf-8',newline='').write(s)
ed('apply_patches.ps1',[
("       De = 'Remote Code Execution Exploit Fix'\n       En = 'Remote code execution exploit fix'\n",
 "       De = 'Remote Code Execution Exploit Fix'\n       En = 'Remote code execution exploit fix'\n       NoteDe = 'nur einen der beiden RCE-Patches aktivieren'\n       NoteEn = 'enable only one of the two RCE patches'\n"),
("       NoteDe = 'Kick-Gefahr bei aktivem Warden'\n       NoteEn = 'may get you kicked if Warden is active'\n",
 "       NoteDe = 'Kick-Gefahr bei aktivem Warden; nur einen der beiden RCE-Patches aktivieren'\n       NoteEn = 'may get you kicked if Warden is active; enable only one of the two RCE patches'\n"),
],crlf=True)
ed('README.md',[
("| Remote Code Execution Exploit Fix | Robinsch |","| Remote Code Execution Exploit Fix *(nur einen der beiden RCE-Patches aktivieren)* | Robinsch |"),
("*(Kick-Gefahr bei aktivem Warden)*","*(Kick-Gefahr bei aktivem Warden; nur einen der beiden RCE-Patches aktivieren)*"),
("läuft weiter, auf Servern mit aktivem Warden gibt es also keine Probleme.\n",
 "läuft weiter, auf Servern mit aktivem Warden gibt es also keine Probleme.\n\n> [!NOTE]\n> Nur einen der beiden RCE-Patches aktivieren: entweder diesen (Warden läuft\n> weiter) oder „Warden komplett abschalten“ (Nr. 6), der die Lücke ebenfalls\n> schließt. Beide zusammen bringen nichts zusätzlich.\n"),
("Macht den RCE-Fix (Nr. 5) überflüssig; beide zusammen schaden aber nicht,\nder Patcher weist dann nur darauf hin.\n",
 "Macht den RCE-Fix (Nr. 5) überflüssig, es ist also nur sinnvoll, einen der\nbeiden zu aktivieren. Beide zusammen schaden aber nicht, der Patcher weist dann\nnur darauf hin.\n"),
])
ed('README.en.md',[
("| Remote code execution exploit fix | Robinsch |","| Remote code execution exploit fix *(enable only one of the two RCE patches)* | Robinsch |"),
("*(may get you kicked if Warden is active)*","*(may get you kicked if Warden is active; enable only one of the two RCE patches)*"),
("servers with active Warden are not a problem.\n",
 "servers with active Warden are not a problem.\n\n> [!NOTE]\n> Enable only one of the two RCE patches: either this one (Warden keeps running)\n> or \"Disable Warden completely\" (No. 6), which closes the hole as well. Both\n> together add nothing.\n"),
("Makes the RCE fix\n(No. 5) unnecessary; both together do no harm, the patcher just points it\nout.\n",
 "Makes the RCE fix\n(No. 5) unnecessary, so it only makes sense to enable one of the two. Both\ntogether do no harm, the patcher just points it out.\n"),
])
print('ok')

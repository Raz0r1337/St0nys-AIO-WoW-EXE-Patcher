import sys
d=sys.argv[1]
def rep(fn,pairs,enc='utf-8'):
    p=d+'/'+fn
    s=open(p,'rb').read().decode(enc)
    for a,b in pairs:
        assert s.count(a)==1,(fn,a[:60],s.count(a)); s=s.replace(a,b)
    open(p,'wb').write(s.encode(enc))
rep('apply_patches.ps1',[("Id = 'worldcrash'; Cat = 'system'; On = $false; PublicUntested = $true","Id = 'worldcrash'; Cat = 'system'; On = $false; BanRisk = $true")],'ascii')
rep('README.de.md',[
 ("| WorldFrame-Absturzfix (ungültige Dreiecks-Indizes) | 🟠 **[online ungetestet]** |","| WorldFrame-Absturzfix (ungültige Dreiecks-Indizes) | 🔴 **[unsicher]** |"),
 ("Bann führen: Nr. 10,\n","Bann führen: Nr. 4, 10,\n"),
 ("Kick/Bann führen: Nr. 4, 26,","Kick/Bann führen: Nr. 26,")])
rep('README.md',[
 ("| WorldFrame crash fix (invalid triangle indices) | 🟠 **[untested online]** |","| WorldFrame crash fix (invalid triangle indices) | 🔴 **[unsafe]** |"),
 ("many servers: No. 10, 11,","many servers: No. 4, 10, 11,"),
 ("banned: No. 4, 26,","banned: No. 26,")])
rep('PATCHES.de.md',[("(fixed by St0ny))* 🟠 **[online ungetestet]**\n\n> [!WARNING]\n> **Online ungetestet** – nicht auf öffentlichen Servern getestet, mögliche Bann-Gefahr. Vorsicht, kann zu Kick/Bann führen.\n",
 "(fixed by St0ny))* 🔴 **[unsicher]**\n\n> [!CAUTION]\n> **Unsicher** – Bann-Gefahr, kann auf vielen Servern zu einem Bann führen. Nur auf Servern nutzen, die das erlauben.\n")])
rep('PATCHES.en.md',[("(fixed by St0ny))* 🟠 **[untested online]**\n\n> [!WARNING]\n> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.\n",
 "(fixed by St0ny))* 🔴 **[unsafe]**\n\n> [!CAUTION]\n> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.\n")])
print('ok',d)

import re,sys
d=sys.argv[1]; S=sys.argv[2]
sys.path.insert(0,S+'/al'); sys.path.insert(0,S+'/wo')
import beta, gen_wowopt as g
once=beta.once
sh=lambda n: str(int(n)+1 if int(n)>=27 else int(n))
def refs(s):
    def f(m):
        out='%s %s'%(m.group(1),sh(m.group(2)))
        if m.group(3): out+=m.group(3)+sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?',f,s)
def hx(b): return '@(' + ', '.join('0x%02X'%x for x in b) + ')'
# ---------------- Skript ----------------
p=d+'/apply_patches.ps1'; s=open(p,'rb').read().decode('ascii')
s=beta.script(s,['lexara'])
out=[]
for x in s.split('\r\n'):
    if re.match(r'^[a-z0-9]+;',x) or 'Name mit Patch-Nummer davor' in x: out.append(x)
    else: out.append(refs(x))
s='\r\n'.join(out)
s=once(s,'# Warmane getestet (Nr. 9, 64 und 65 vergroessern die Wow.exe); dazu der noch\r\n# ungetestete Lexara-Lader (Nr. 30).',
         '# Warmane getestet (Nr. 9, 65 und 66 vergroessern die Wow.exe); dazu der noch\r\n# ungetestete Lexara-Lader (Nr. 30).')
caves=[]
for nm,(va,code) in g.PIECES:
    caves.append('            @(0x%X, %s)   # %s, VA 0x%X'%(va-g.BASE,hx(code),nm,va))
entry='''    @{ Id = 'wowoptimize'; Cat = 'dll'; On = $false; BanRisk = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST) [BETA]'
       En = 'Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST) [BETA]'
       NoteDe = 'benoetigt wow_optimize - nur wow_optimize.dll, ohne version.dll'
       NoteEn = 'requires wow_optimize - only wow_optimize.dll, without version.dll'
       Url = 'https://github.com/suprepupre/wow-optimize'
       Code = {
        # Laedt wow_optimize.dll (Performance-Optimierung von SUPREMATIST) aus
        # dem WoW-Ordner - genau wie die Proxy-version.dll von wow_optimize:
        # Beim Start legt die Exe einen eigenen Thread an, der 3 Sekunden
        # wartet und dann LoadLibraryA("wow_optimize.dll") aufruft. Fehlt die
        # DLL, startet WoW ganz normal. Laut wow_optimize bannt Warmane dafuer.
        # Eingehaengt ist das in den einmaligen Aufruf call 0x7755F0 bei VA
        # 0x76E490, den nur der Einstiegspunkt erreicht (nach dem Lexara-Lader,
        # vor dem Sprung, den der voice.dll-Lader umbiegt). Der Code steht in
        # acht freien Luecken zwischen Funktionen, den DLL-Namen baut der Thread
        # auf dem Stack. Dateigroesse und PE-Header bleiben unveraendert.
        #   A1-A3: CreateThread(NULL, 0, B1, NULL, 0, NULL) / CloseHandle / jmp 0x7755F0
        #   B1-B5: Sleep(3000) / LoadLibraryA("wow_optimize.dll") / return 0
        $caves = @(
%s
        )
        Assert-Bytes 0x%X %s 'wow_optimize-Lader'
        foreach ($c in $caves) { Assert-Bytes $c[0] (@(0xCC) * $c[1].Count) 'wow_optimize-Lader' }
        Patch 0x%X %s                   # call 0x7755F0 -> call A1
        foreach ($c in $caves) { Patch $c[0] $c[1] }
    }}

'''%('\n'.join(caves),g.HOOK-g.BASE,hx(g.HOOK_ORIG),g.HOOK-g.BASE,hx(g.HOOKP[1]))
entry=entry.replace('\n','\r\n')
s=once(s,"    @{ Id = 'awesome';",entry+"    @{ Id = 'awesome';")
s=once(s,"    'mpqnames', 'localdata', 'awesome', 'areatrigger', 'swing', 'npcanim',\r\n",
         "    'mpqnames', 'localdata', 'wowoptimize', 'awesome', 'areatrigger', 'swing',\r\n    'npcanim',")
s=once(s,"    'npcanim',    'spellanim', 'ghostattack',","    'npcanim', 'spellanim', 'ghostattack',")
open(p,'wb').write(s.encode('ascii'))
# ---------------- README ----------------
ROW={'de':"| [27](PATCHES.de.md#patch-wowoptimize) | wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST) [BETA] *(benötigt [wow_optimize](https://github.com/suprepupre/wow-optimize) – nur `wow_optimize.dll`, ohne `version.dll`)* | 🔴 **[unsicher - ingame ungetestet]** | St0ny | – | – | ✅ |\n",
     'en':"| [27](PATCHES.en.md#patch-wowoptimize) | Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST) [BETA] *(requires [wow_optimize](https://github.com/suprepupre/wow-optimize) – only `wow_optimize.dll`, without `version.dll`)* | 🔴 **[unsafe - untested ingame]** | St0ny | – | – | ✅ |\n"}
LEG={'de':[("Nr. 4, 10,\n    11, 23–25, 42, 43, 46–51, 75 und 83–87 (rote Warnung).","Nr. 4, 10,\n    11, 23–25, 27, 43, 44, 47–52, 76 und 84–88 (rote Warnung)."),
           ("Nr. 26, 29, 30, 40, 45, 52, 63, 69, 72–74 und 81\n    (orange Warnung).","Nr. 26, 30, 31, 41, 46, 53, 64, 70, 73–75 und 82\n    (orange Warnung)."),
           ("Nr. 25, 26, 29, 30, 45, 52 und 63 (orange Warnung).","Nr. 25–27, 30, 31, 46, 53 und 64 (orange Warnung)."),
           ("Nr. 9, 51, 64, 65, 75 und 81. Das ist","Nr. 9, 52, 65, 66, 76 und 82. Das ist"),
           ("(Nr. 9, 51, 64, 65, 75 und 81), entfernen","(Nr. 9, 52, 65, 66, 76 und 82), entfernen"),
           ("Drei davon (Nr. 9, 64 und 65) vergrößern","Drei davon (Nr. 9, 65 und 66) vergrößern")],
     'en':[("No. 4, 10, 11, 23–25,\n    42, 43, 46–51, 75 and 83–87 (red warning).","No. 4, 10, 11, 23–25,\n    27, 43, 44, 47–52, 76 and 84–88 (red warning)."),
           ("No. 26, 29, 30, 40, 45, 52, 63, 69, 72–74 and 81\n    (orange warning).","No. 26, 30, 31, 41, 46, 53, 64, 70, 73–75 and 82\n    (orange warning)."),
           ("No. 25, 26, 29, 30, 45, 52 and 63 (orange warning).","No. 25–27, 30, 31, 46, 53 and 64 (orange warning)."),
           ("No. 9, 51,\n    64, 65, 75 and 81. This does not","No. 9, 52,\n    65, 66, 76 and 82. This does not"),
           ("(No. 9, 51, 64, 65, 75 and 81) also remove","(No. 9, 52, 65, 66, 76 and 82) also remove"),
           ("(No. 9, 64 and 65) make `Wow.exe` larger","(No. 9, 65 and 66) make `Wow.exe` larger")]}
for fn,md,lang in (('docs/README.de.md','PATCHES.de.md','de'),('docs/README.md','PATCHES.en.md','en')):
    p=d+'/'+fn; s=open(p,encoding='utf-8',newline='').read(); assert '\r' not in s
    s=beta.readme(s,md,['lexara'])
    for a,b in LEG[lang]: s=once(s,a,b)
    s=re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(sh(m.group(1)),md), s)
    s=refs(s)
    s=once(s,'| [28](%s#patch-awesome)'%md, ROW[lang]+'| [28](%s#patch-awesome)'%md)
    open(p,'w',encoding='utf-8',newline='\n').write(s)
# ---------------- PATCHES ----------------
SEC={'de':open(S+'/al/wo_sec_de.md',encoding='utf-8').read(),'en':open(S+'/al/wo_sec_en.md',encoding='utf-8').read()}
for fn,lang in (('docs/PATCHES.de.md','de'),('docs/PATCHES.en.md','en')):
    p=d+'/'+fn; s=open(p,encoding='utf-8',newline='').read(); assert '\r' not in s
    s=beta.patches(s,lang,['lexara'])
    s=refs(s)
    s=once(s,'<a id="patch-awesome"></a>\n',SEC[lang]+'\n<a id="patch-awesome"></a>\n')
    open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

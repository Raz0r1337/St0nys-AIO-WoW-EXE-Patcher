import re,sys
L=sys.argv[1]; DEV=sys.argv[2]
sys.path.insert(0,sys.argv[3]); 
def once(s,a,b):
    assert s.count(a)==1,(a[:90],s.count(a)); return s.replace(a,b)
sh=lambda n: str(int(n)+1 if int(n)>=29 else int(n))
def refs(s):
    def f(m):
        out='%s %s'%(m.group(1),sh(m.group(2)))
        if m.group(3): out+=m.group(3)+sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?',f,s)
# ---------- script ----------
dev=open(DEV,'rb').read().decode('ascii')
a=dev.index("    @{ Id = 'lexara'"); b=dev.index("    @{ Id = 'voicedll'")
entry=dev[a:b]; assert entry.endswith('    }}\r\n\r\n'),repr(entry[-20:])
s=open(L+'/apply_patches.ps1','rb').read().decode('ascii')
i=s.index("    @{ Id = 'voicedll'"); assert s.count("    @{ Id = 'voicedll'")==1
s=s[:i]+entry+s[i:]
lines=s.split('\r\n'); out=[]
for x in lines:
    if re.match(r'^[a-z0-9]+;',x) or 'Name mit Patch-Nummer davor' in x or x.startswith('# Warmane getestet (Nr. 9, 63 und 64') or x.startswith('# ungetesteten Licht-Patches'):
        out.append(x)
    else:
        out.append(refs(x))
s='\r\n'.join(out)
s=once(s,"# von Stormhand. Sichere Patches, alle von Stormhand mehrere Stunden auf\r\n# Warmane getestet (Nr. 9, 63 und 64 vergroessern die Wow.exe); dazu die noch\r\n# ungetesteten Licht-Patches Nr. 65 und 66. Im Menue mit R, ueber\r\n",
         "# von Stormhand. Sichere Patches, alle von Stormhand mehrere Stunden auf\r\n# Warmane getestet (Nr. 9, 64 und 65 vergroessern die Wow.exe); dazu der noch\r\n# ungetestete Lexara-Lader (Nr. 29) und die noch ungetesteten Licht-Patches\r\n# Nr. 66 und 67. Im Menue mit R, ueber\r\n")
s=once(s,"    'glue', 'awesome',\r\n","    'glue', 'awesome', 'lexara',\r\n")
open(L+'/apply_patches.ps1','wb').write(s.encode('ascii'))
# ---------- docs ----------
import importlib.util
spec=importlib.util.spec_from_file_location('r29',sys.argv[3]+'/renum29_texts.py'); r29=importlib.util.module_from_spec(spec); spec.loader.exec_module(r29)
ROW,SEC=r29.ROW,r29.SEC
LEG={'de':[("Nr. 4, 10,\n    11, 23–25, 41, 42, 45–50, 76 und 84–88 (rote Warnung).","Nr. 4, 10,\n    11, 23–25, 42, 43, 46–51, 77 und 85–89 (rote Warnung)."),
           ("Nr. 26, 29, 39, 44, 51, 62, 65, 66, 70, 73–75\n    und 82 (rote Warnung).","Nr. 26, 29, 30, 40, 45, 52, 63, 66, 67, 71,\n    74–76 und 83 (rote Warnung)."),
           ("Nr. 25, 26, 29, 44, 51, 62, 65 und 66 (rote Warnung).","Nr. 25, 26, 29, 30, 45, 52, 63, 66 und 67 (rote\n    Warnung)."),
           ("Nr. 9, 50, 63–65, 76 und 82. Das ist","Nr. 9, 51, 64–66, 77 und 83. Das ist"),
           ("(Nr. 9, 50, 63–65, 76 und 82), entfernen","(Nr. 9, 51, 64–66, 77 und 83), entfernen"),
           ("Es enthält nur\nsichere Patches (🟢), die Stormhand alle mehrere Stunden auf Warmane getestet\nhat – **das Preset ist sicher** und kann auch auf öffentlichen Servern\nverwendet werden. Drei davon (Nr. 9, 63 und 64) vergrößern die `Wow.exe`; auf\nWarmane war das kein Problem, andere Server können die Dateigröße aber prüfen.\nDazu kommen die Licht-Patches Nr. 65 und 66 für Stormhands Grafik-Overhaul. Sie\nsind noch ungetestet, Nr. 65 vergrößert die `Wow.exe` ebenfalls. Welche Patches\n",
            "Es enthält\nsichere Patches (🟢), die Stormhand alle mehrere Stunden auf Warmane getestet\nhat – **das Preset ist sicher** und kann auch auf öffentlichen Servern\nverwendet werden. Drei davon (Nr. 9, 64 und 65) vergrößern die `Wow.exe`; auf\nWarmane war das kein Problem, andere Server können die Dateigröße aber prüfen.\nDazu kommen der Lexara-Lader (Nr. 29) für Stormhands HD-Schriften und die\nLicht-Patches Nr. 66 und 67 für den Grafik-Overhaul. Sie sind noch ungetestet;\nNr. 66 vergrößert die `Wow.exe` ebenfalls, und ohne `Lexara.dll` im WoW-Ordner\nbewirkt Nr. 29 nichts. Welche Patches\n")],
     'en':[("No. 4, 10, 11, 23–25,\n    41, 42, 45–50, 76 and 84–88 (red warning).","No. 4, 10, 11, 23–25,\n    42, 43, 46–51, 77 and 85–89 (red warning)."),
           ("No. 26, 29, 39, 44, 51, 62, 65, 66, 70, 73–75\n    and 82 (red warning).","No. 26, 29, 30, 40, 45, 52, 63, 66, 67, 71,\n    74–76 and 83 (red warning)."),
           ("No. 25, 26, 29, 44, 51, 62, 65 and 66 (red warning).","No. 25, 26, 29, 30, 45, 52, 63, 66 and 67 (red\n    warning)."),
           ("No. 9, 50,\n    63–65, 76 and 82. This does not","No. 9, 51,\n    64–66, 77 and 83. This does not"),
           ("(No. 9, 50, 63–65, 76 and 82) also remove","(No. 9, 51, 64–66, 77 and 83) also remove"),
           ("It contains only patches\nrated safe (🟢), all tested by Stormhand for several hours on Warmane – **the\npreset is safe** and can be used on public servers as well. Three of them\n(No. 9, 63 and 64) make `Wow.exe` larger; that was no problem on Warmane, but\nother servers may check the file size. On top of that come the light patches\nNo. 65 and 66 for Stormhand's graphics overhaul. They are still untested, and\nNo. 65 makes `Wow.exe` larger as well. The \"Reforged\" column in the\n",
            "It contains patches\nrated safe (🟢), all tested by Stormhand for several hours on Warmane – **the\npreset is safe** and can be used on public servers as well. Three of them\n(No. 9, 64 and 65) make `Wow.exe` larger; that was no problem on Warmane, but\nother servers may check the file size. On top of that come the Lexara loader\n(No. 29) for Stormhand's HD fonts and the light patches No. 66 and 67 for the\ngraphics overhaul. They are still untested; No. 66 makes `Wow.exe` larger as\nwell, and without `Lexara.dll` in the WoW folder No. 29 does nothing. The\n\"Reforged\" column in the\n")]}
for fn,md,lang in (('README.de.md','PATCHES.de.md','de'),('README.md','PATCHES.en.md','en')):
    p=L+'/'+fn; s=open(p,encoding='utf-8',newline='').read(); assert '\r' not in s
    for x,y in LEG[lang]: s=once(s,x,y)
    s=re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(sh(m.group(1)),md), s)
    s=re.sub(r'(?m)^\| \[\d+\]\(.*$',lambda m: refs(m.group(0)),s)
    m=re.search(r'(?m)^\| \[28\]\(%s#patch-wotlkext\).*\n'%re.escape(md),s); assert m
    s=s[:m.end()]+ROW[lang]+s[m.end():]
    open(p,'w',encoding='utf-8',newline='\n').write(s)
for fn,lang in (('PATCHES.de.md','de'),('PATCHES.en.md','en')):
    p=L+'/'+fn; s=open(p,encoding='utf-8',newline='').read(); assert '\r' not in s
    s=refs(s)
    a=s.index('<a id="patch-voicedll"></a>')
    s=s[:a]+SEC[lang]+s[a:]
    open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

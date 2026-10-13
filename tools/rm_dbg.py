import re,sys
d=sys.argv[1]
def once(s,a,b):
    assert s.count(a)==1,(a[:90],s.count(a)); return s.replace(a,b)
def mp(n):
    n=int(n); assert n not in (29,80),('stale ref',n)
    return str(n if n<29 else (n-1 if n<80 else n-2))
def refs(s):
    def f(m):
        out='%s %s'%(m.group(1),mp(m.group(2)))
        if m.group(3): out+=m.group(3)+mp(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?',f,s)
def cut(s,a,b):
    i=s.index(a); assert s.count(a)==1; j=s.index(b,i); return s[:i]+s[j:]
SEP='# ============================================================\r\n'
# ---------- apply_patches.ps1 ----------
p=d+'/apply_patches.ps1'; s=open(p,'rb').read().decode('ascii')
s=cut(s,SEP+'#  Helfer fuer den CameraReforged-Patch\r\n',SEP+'#  Helfer fuer die Client-Info-Patches')
s=cut(s,SEP+'#  Helfer fuer den voice.dll-Loader',SEP+'#  Eigene Code-Sektion fuer kleine Code-Hoehlen')
for pid in ('voicedll','camera'):
    a="    @{ Id = '%s';"%pid; i=s.index(a); assert s.count(a)==1
    j=s.index('    }}\r\n\r\n',i)+len('    }}\r\n\r\n')
    assert "@{ Id = '" not in s[i+10:j]
    s=s[:i]+s[j:]
s=once(s,'#  Wie CameraReforged veraendert dieser Patch die Dateigroesse/PE-Struktur.\r\n','#  Dieser Patch veraendert die Dateigroesse/PE-Struktur.\r\n')
s=once(s,'#  Wie HD-Portraits und CameraReforged: Padding bis FileAlignment, Sektion\r\n','#  Wie HD-Portraits: Padding bis FileAlignment, Sektion\r\n')
s=once(s,'# Warmane getestet (Nr. 9, 63 und 64 vergroessern die Wow.exe).','# Warmane getestet (Nr. 9, 62 und 63 vergroessern die Wow.exe).')
out=[]
for x in s.split('\r\n'):
    if re.match(r'^[a-z0-9]+;',x) or 'Name mit Patch-Nummer davor' in x or x.startswith('# Warmane getestet (Nr. 9, 62 und 63'): out.append(x)
    else: out.append(refs(x))
s='\r\n'.join(out)
import re as _r
for _m in _r.finditer(r'(?i).{0,60}(camerareforged|voice).{0,60}',s): print(repr(_m.group(0)))
sys.exit(0)
open(p,'wb').write(s.encode('ascii'))
# ---------- README ----------
LEG={'de':[("Nr. 4, 10,\n    11, 23–25, 41, 42, 45–50, 74 und 82–86 (rote Warnung).","Nr. 4, 10,\n    11, 23–25, 40, 41, 44–49, 73 und 80–84 (rote Warnung)."),
           ("kann zu Kick/Bann führen: Nr. 26, 29, 39, 44, 51, 62, 68, 71–73 und 80 (orange\n    Warnung).","kann zu Kick/Bann führen: Nr. 26, 38, 43, 50, 61, 67 und 70–72 (orange Warnung)."),
           ("Nr. 25, 26, 29, 44, 51 und 62 (orange Warnung).","Nr. 25, 26, 43, 50 und 61 (orange Warnung)."),
           ("Nr. 9, 50, 63, 64, 74 und 80. Das ist","Nr. 9, 49, 62, 63 und 73. Das ist"),
           ("(Nr. 9, 50, 63, 64, 74 und 80), entfernen","(Nr. 9, 49, 62, 63 und 73), entfernen"),
           ("Drei davon (Nr. 9, 63 und 64) vergrößern","Drei davon (Nr. 9, 62 und 63) vergrößern")],
     'en':[("No. 4, 10, 11, 23–25,\n    41, 42, 45–50, 74 and 82–86 (red warning).","No. 4, 10, 11, 23–25,\n    40, 41, 44–49, 73 and 80–84 (red warning)."),
           ("you kicked or banned: No. 26, 29, 39, 44, 51, 62, 68, 71–73 and 80 (orange\n    warning).","you kicked or banned: No. 26, 38, 43, 50, 61, 67 and 70–72 (orange warning)."),
           ("No. 25, 26, 29, 44, 51 and 62 (orange warning).","No. 25, 26, 43, 50 and 61 (orange warning)."),
           ("No. 9, 50,\n    63, 64, 74 and 80. This does not","No. 9, 49,\n    62, 63 and 73. This does not"),
           ("(No. 9, 50, 63, 64, 74 and 80) also remove","(No. 9, 49, 62, 63 and 73) also remove"),
           ("(No. 9, 63 and 64) make `Wow.exe` larger","(No. 9, 62 and 63) make `Wow.exe` larger")]}
for fn,md,lang in (('docs/README.de.md','PATCHES.de.md','de'),('docs/README.md','PATCHES.en.md','en')):
    p=d+'/'+fn; s=open(p,encoding='utf-8',newline='').read(); assert '\r' not in s
    for a,b in LEG[lang]: s=once(s,a,b)
    for anc in ('voicedll','camera'):
        m=re.search(r'(?m)^\| \[\d+\]\(%s#patch-%s\).*\n'%(re.escape(md),anc),s); assert m
        s=s[:m.start()]+s[m.end():]
    s=re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(mp(m.group(1)),md), s)
    s=refs(s)
    open(p,'w',encoding='utf-8',newline='\n').write(s)
# ---------- PATCHES ----------
for fn in ('docs/PATCHES.de.md','docs/PATCHES.en.md'):
    p=d+'/'+fn; s=open(p,encoding='utf-8',newline='').read(); assert '\r' not in s
    for anc in ('voicedll','camera'):
        a='<a id="patch-%s"></a>'%anc; i=s.index(a)
        nx=[k for k in (s.find('\n<a id="',i+1),s.find('\n## ',i+1)) if k!=-1]; j=min(nx)+1
        s=s[:i]+s[j:]
    s=refs(s)
    open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

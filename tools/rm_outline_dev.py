import difflib,re,sys
d=sys.argv[1]; MAIN=sys.argv[2]
def once(s,a,b):
    assert s.count(a)==1,(a[:90],s.count(a)); return s.replace(a,b)
sh=lambda n: str(int(n)-1 if int(n)>=67 else int(n))
def refs(s):
    def f(m):
        out='%s %s'%(m.group(1),sh(m.group(2)))
        if m.group(3): out+=m.group(3)+sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?',f,s)
# ---------- apply_patches.ps1 (ASCII, CRLF) ----------
D=open(d+'/apply_patches.ps1','rb').read().decode('ascii').split('\r\n')
M=open(MAIN,'rb').read().decode('ascii').split('\r\n')
tab=lambda L:[('#TABLE#' if re.match(r'^[a-z0-9]+;',x) else x) for x in L]
ops=difflib.SequenceMatcher(None,tab(M),tab(D),autojunk=False).get_opcodes()
out=[]; k=-1; reverted=[]
for op,a1,a2,b1,b2 in ops:
    if op=='equal': out+=D[b1:b2]; continue
    k+=1
    dv='\n'.join(D[b1:b2]); mv='\n'.join(M[a1:a2])
    outl=('Add-Outline' in dv) or ('Umrandung fuer Ziel' in dv)
    sect=('Add-SectionBlock' in dv) or ("kein Platz im PE-Header" in mv) or ('$opt = RU16' in mv) or ('$sectBase = $e + 24 + $opt' in mv)
    if outl or sect:
        out+=M[a1:a2]; reverted.append(k)
    else:
        out+=D[b1:b2]
print('reverted hunks',reverted)
assert reverted==[4,5,6,7,8,9,10,11,13],reverted
s='\r\n'.join(out)
body,sep,rest=s.partition("#  Original-Bytes je Patch")
body=refs(body)
s=body+sep+rest
assert 'outline' not in body.lower().replace('outlines','') or True
open(d+'/apply_patches.ps1','wb').write(s.encode('ascii'))
# ---------- README (UTF-8, LF) ----------
LEG={'de':[("11, 23–25, 42, 43, 46–51, 76 und 84–88 (rote Warnung).","11, 23–25, 42, 43, 46–51, 75 und 83–87 (rote Warnung)."),
           ("Nr. 26, 29, 30, 40, 45, 52, 63, 66, 70, 73–75 und 82\n    (orange Warnung).","Nr. 26, 29, 30, 40, 45, 52, 63, 69, 72–74 und 81\n    (orange Warnung)."),
           ("Nr. 9, 51, 64–66, 76 und 82. Das ist","Nr. 9, 51, 64, 65, 75 und 81. Das ist"),
           ("(Nr. 9, 51, 64–66, 76 und 82), entfernen","(Nr. 9, 51, 64, 65, 75 und 81), entfernen")],
     'en':[("42, 43, 46–51, 76 and 84–88 (red warning).","42, 43, 46–51, 75 and 83–87 (red warning)."),
           ("No. 26, 29, 30, 40, 45, 52, 63, 66, 70, 73–75 and 82\n    (orange warning).","No. 26, 29, 30, 40, 45, 52, 63, 69, 72–74 and 81\n    (orange warning)."),
           ("No. 9, 51,\n    64–66, 76 and 82. This does not","No. 9, 51,\n    64, 65, 75 and 81. This does not"),
           ("(No. 9, 51, 64–66, 76 and 82) also remove","(No. 9, 51, 64, 65, 75 and 81) also remove")]}
for fn,md,lang in (('docs/README.de.md','PATCHES.de.md','de'),('docs/README.md','PATCHES.en.md','en')):
    s=open(d+'/'+fn,encoding='utf-8',newline='').read(); assert '\r' not in s
    for a,b in LEG[lang]: s=once(s,a,b)
    row=re.search(r'(?m)^\| \[66\]\(%s#patch-outline\).*\n'%re.escape(md),s); assert row
    s=s[:row.start()]+s[row.end():]
    s=re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(sh(m.group(1)),md), s)
    s=refs(s)
    open(d+'/'+fn,'w',encoding='utf-8',newline='\n').write(s)
# ---------- PATCHES (UTF-8, LF) ----------
for fn,head in (('docs/PATCHES.de.md','## Interface & Komfort'),('docs/PATCHES.en.md','## Interface & comfort')):
    s=open(d+'/'+fn,encoding='utf-8',newline='').read(); assert '\r' not in s
    a=s.index('<a id="patch-outline"></a>'); assert s.count(head)==1; b=s.index(head)
    assert a<b
    s=s[:a]+s[b:]
    s=refs(s)
    open(d+'/'+fn,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

import re,subprocess,sys
d=sys.argv[1]
def show(ref,fn): return subprocess.run(['git','-C',d,'show','%s:%s'%(ref,fn)],capture_output=True,check=True).stdout.decode('utf-8')
OUT='origin/st0ny-dev-outline'
sh=lambda n: str(int(n)+1 if int(n)>=66 else int(n))
def once(s,a,b):
    assert s.count(a)==1,(a[:90],s.count(a)); return s.replace(a,b)
def refs(s):
    def f(m):
        out='%s %s'%(m.group(1),sh(m.group(2)))
        if m.group(3): out+=m.group(3)+sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?',f,s)
def table(s,md): return re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(sh(m.group(1)),md), s)
def rowrefs(s): return re.sub(r'(?m)^\| \[\d+\]\(.*$',lambda m: refs(m.group(0)),s)
LEG={'de':[("Nr. 4, 10,\n    11, 23–25, 42, 43, 46–51, 75 und 83–87 (rote Warnung).","Nr. 4, 10,\n    11, 23–25, 42, 43, 46–51, 76 und 84–88 (rote Warnung)."),
           ("Nr. 26, 29, 30, 40, 45, 52, 63, 69, 72–74 und 81 (rote\n    Warnung).","Nr. 26, 29, 30, 40, 45, 52, 63, 66, 70, 73–75 und 82\n    (rote Warnung)."),
           ("Nr. 9, 51, 64, 65, 75 und 81. Das ist","Nr. 9, 51, 64–66, 76 und 82. Das ist"),
           ("(Nr. 9, 51, 64, 65, 75 und 81), entfernen","(Nr. 9, 51, 64–66, 76 und 82), entfernen")],
     'en':[("42, 43, 46–51, 75 and 83–87 (red warning).","42, 43, 46–51, 76 and 84–88 (red warning)."),
           ("No. 26, 29, 30, 40, 45, 52, 63, 69, 72–74 and 81 (red\n    warning).","No. 26, 29, 30, 40, 45, 52, 63, 66, 70, 73–75 and 82\n    (red warning)."),
           ("No. 9, 51,\n    64, 65, 75 and 81. This does not","No. 9, 51,\n    64–66, 76 and 82. This does not"),
           ("(No. 9, 51, 64, 65, 75 and 81) also remove","(No. 9, 51, 64–66, 76 and 82) also remove")]}
for fn,md,lang,ex in (('README.de.md','PATCHES.de.md','de',('🟠 **[online ungetestet]**<br>🟡 **[Exe wird größer]**','🟠 **[online ungetestet]**<br>**[Exe wird größer]**')),
                      ('README.md','PATCHES.en.md','en',('🟠 **[untested online]**<br>🟡 **[exe grows]**','🟠 **[untested online]**<br>**[exe grows]**'))):
    s=show('HEAD',fn); o=show(OUT,fn)
    for a,b in LEG[lang]: s=once(s,a,b)
    s=table(s,md); s=rowrefs(s)
    row=re.search(r'(?m)^\| \[65\]\(%s#patch-outline\).*\n'%re.escape(md),o).group(0)
    row=once(row.replace('| [65](','| [66]('),*ex)
    m=re.search(r'(?m)^\| \[65\]\(%s#patch-iconsnap\).*\n'%re.escape(md),s); assert m
    s=s[:m.end()]+row+s[m.end():]
    open(d+'/'+fn,'w',encoding='utf-8',newline='\n').write(s)
for fn,head,nr in (('PATCHES.de.md','## Interface & Komfort','(Nr. 65, Autor'),('PATCHES.en.md','## Interface & comfort','(No. 65, Author')):
    s=show('HEAD',fn); o=show(OUT,fn)
    s=refs(s)
    a=o.index('<a id="patch-outline"></a>'); b=o.index(head,a)
    sec=once(o[a:b],nr,nr.replace('65','66'))
    i=s.index(head); assert s.count(head)==1
    s=s[:i]+sec+s[i:]
    open(d+'/'+fn,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

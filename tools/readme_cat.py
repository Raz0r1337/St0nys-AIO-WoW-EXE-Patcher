import re, json
SP='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/'
old=json.load(open(SP+'old_order.json')); CATS=json.load(open(SP+'cats.json'))
ps=open('apply_patches.ps1').read()
E=re.findall(r"@\{ Id = '(\w+)'; Cat = '(\w+)'; On = \$(true|false)[^\n]*\n(?:\s+Author = '([^']*)'\s*\n)?",ps)
new=[e[0] for e in E]; on={e[0]:e[2]=='true' for e in E}; auth={e[0]:e[3] for e in E}
assert new==[i for c in CATS for i in c[3]] and len(new)==51
N={i:n+1 for n,i in enumerate(new)}; O={n+1:i for n,i in enumerate(old)}
CFG={'README.md':dict(word='Nr.',head='| Nr. | Patch | Autor | Standard |',desc='## Patch-Beschreibungen',title=1,
      ren={'cache':'CACHE-Ordner-Erstellung deaktivieren','scandll':'Scan.dll deaktivieren','afk':None,'wardenoff':None,
           'areatrigger':'Area-Trigger-Timer genauer (50 ms statt 250 ms)','maxchars':'Max. Charaktere pro Server auf 255 erhöht'},
      tre=[('| AFK Timer IDLE Check deaktiviert ','| AFK-Timer / IDLE-Check deaktivieren '),('| Warden komplett abschalten (RCE-Fix) ','| Warden komplett abschalten, RCE-Fix ')],
      hre=[('**Scan-DLL deaktivieren**','**Scan.dll deaktivieren**')],
      sel=("""`[ ]` = wird übersprungen. Vorausgewählt ist die empfohlene Standard-Auswahl""","""`[ ]` = wird übersprungen. Das Menü ist in Kategorien gegliedert (dieselben wie
in der [Patch-Übersicht](#patch-übersicht)). Vorausgewählt ist die empfohlene Standard-Auswahl""")),
     'README.en.md':dict(word='No.',head='| No. | Patch | Author | Default |',desc='## Patch descriptions',title=2,
      ren={'scandll':'Disable Scan.dll','areatrigger':'More precise area trigger timer (50 ms instead of 250 ms)'},
      tre=[('| Disable Warden completely (RCE fix) ','| Disable Warden completely, RCE fix ')],
      hre=[('**Disable scan DLL**','**Disable Scan.dll**')],
      sel=("""`[ ]` = will be skipped. The recommended default selection is preselected""","""`[ ]` = will be skipped. The menu is grouped into categories (the same as in the
[patch overview](#patch-overview)). The recommended default selection is preselected"""))}
for p,c in CFG.items():
    s=open(p).read(); w=re.escape(c['word'])
    # 1) renumber everywhere old -> new
    s=re.sub(r'(%s )(\d+)'%w, lambda m: m.group(1)+str(N[O[int(m.group(2))]]), s)
    # 2) table with category rows
    lines=s.split('\n'); i=lines.index(c['head']); j=i+2; rows={}
    while lines[j].startswith('|'):
        m=re.match(r'^\| (\d+)\s*\| (.*) \| (.*?) \| (✅|–) \|$',lines[j]); assert m, lines[j]
        rows[O[int(m.group(1))]]=m.group(2); j+=1
    assert len(rows)==51
    for k,v in c['ren'].items():
        if v: rows[k]=v
    out=[]
    for cat in CATS:
        out.append('|    | **%s** |  |  |'%cat[c['title']])
        for x in cat[3]:
            out.append('| %-2d | %s | %s | %s |'%(N[x],rows[x],auth[x],'✅' if on[x] else '–'))
    lines[i+2:j]=out; s='\n'.join(lines)
    for o_,n_ in c['tre']:
        assert s.count(o_)==1,(p,o_); s=s.replace(o_,n_)
    for o_,n_ in c['hre']:
        assert s.count(o_)==1,(p,o_); s=s.replace(o_,n_)
    assert s.count(c['sel'][0])==1; s=s.replace(c['sel'][0],c['sel'][1])
    # 3) descriptions regrouped
    a=s.index('\n'+c['desc']+'\n')+len(c['desc'])+2; b=s.index('\n---\n',a)
    part=s[a:b]
    blocks={}
    for sec in re.split(r'\n(?=### )','\n'+part)[1:]:
        body=sec.split('\n',1)[1]
        heads=list(re.finditer(r'^\*\*.+?\*\* \*\(%s (\d+)'%w,body,re.M))
        for k,h in enumerate(heads):
            e=heads[k+1].start() if k+1<len(heads) else len(body)
            blocks[new[int(h.group(1))-1]]=body[h.start():e].strip('\n')
    assert len(blocks)==51,(p,len(blocks))
    newpart='\n'
    for cat in CATS:
        newpart+='### %s\n\n'%cat[c['title']]+'\n\n'.join(blocks[x] for x in cat[3])+'\n\n'
    s=s[:a]+newpart.rstrip('\n')+'\n'+s[b:]
    open(p,'w').write(s)
print('ok')

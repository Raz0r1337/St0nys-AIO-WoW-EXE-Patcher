import re
ps=open('apply_patches.ps1').read()
entries=re.findall(r"@\{ Id = '(\w+)'; On = \$(true|false)[^\n]*\n(?:\s+Author = '([^']*)'\s*\n)?",ps)
ids=[e[0] for e in entries]; on={e[0]:e[1]=='true' for e in entries}; auth={e[0]:e[2] for e in entries}
assert len(ids)==38 and ids[13:15]==['ghostattack','level101']
num={i:n+1 for n,i in enumerate(ids)}
L={
 'README.md':dict(word='Nr.',head='| Nr. | Patch | Autor | Standard |',autor='Autor',
   rows={'ghostattack':'„Geister“-Angriff von NPCs beim Evade behoben','level101':'Level 101+ Fix (Druiden-Grundwerte und Barbierstuhl)'},
   anchor_desc='**Zaubervorbereitungs-Animation nach Abbruch kanalisierter Spells repariert**',
   desc="""**„Geister“-Angriff von NPCs beim Evade behoben** *(Nr. 14, Autor: Robinsch)*
Behebt den „Geister“-Angriff, den NPCs ausführen, wenn sie aus dem Kampf
evaden.

**Level 101+ Fix für Druiden-Grundwerte und Barbierstuhl** *(Nr. 15, standardmäßig aus, Autor: Robinsch)*
Druiden ab Level 101 können ihre Grundwerte wieder ansehen, und der
Barbierstuhl funktioniert für alle Charaktere ab Level 101.
Hinweis des Autors: *„Use XML MD5“*.
"""),
 'README.en.md':dict(word='No.',head='| No. | Patch | Author | Default |',autor='Author',
   rows={'ghostattack':'Fix "ghost" attack when NPCs evade from combat','level101':'Level 101+ fix (druid base stats and barber chair)'},
   anchor_desc='**Fix spell preparation animation after cancelling channelled spells**',
   desc="""**Fix "ghost" attack when NPCs evade from combat** *(No. 14, Author: Robinsch)*
Fixes the "ghost" attack NPCs perform when they evade from combat.

**Level 101+ fix for druid base stats and barber chair** *(No. 15, off by default, Author: Robinsch)*
Druids at level 101 and above can view their base stats again, and the
barber chair works for all characters at level 101 and above.
Author's note: *"Use XML MD5"*.
"""),
}
for p,c in L.items():
    s=open(p).read()
    s=re.sub(r'(%s )(\d+)'%re.escape(c['word']), lambda m: m.group(1)+str(int(m.group(2))+2 if int(m.group(2))>=14 else int(m.group(2))), s)
    lines=s.split('\n'); i=lines.index(c['head']); j=i+2
    rows=[]
    while lines[j].startswith('|'):
        m=re.match(r'^\| (\d+)\s*\| (.*) \| (.*?) \| (✅|–) \|$',lines[j]); assert m, lines[j]
        rows.append(m.group(2)); j+=1
    assert len(rows)==36
    names=rows[:13]+[c['rows']['ghostattack'],c['rows']['level101']]+rows[13:]
    lines[i+2:j]=['| %-2d | %s | %s | %s |'%(n+1,names[n],auth[ids[n]],'✅' if on[ids[n]] else '–') for n in range(38)]
    s='\n'.join(lines)
    for i_,a in auth.items():
        if not a or i_ in ('ghostattack','level101'): continue
        n=num[i_]
        pat=re.compile(r'\*\(%s %d(, [^)]*?)?\)\*'%(re.escape(c['word']),n))
        ms=pat.findall(s); assert len(ms)==1,(p,i_,n,ms)
        if c['autor']+':' in (ms[0] or ''): continue
        s=pat.sub(lambda m:'*(%s %d%s, %s: %s)*'%(c['word'],n,m.group(1) or '',c['autor'],a),s)
    k=s.index(c['anchor_desc']); k=s.index('\n\n',k)+2
    s=s[:k]+c['desc']+'\n'+s[k:]
    assert s.count('`4gb=1`')==1; s=s.replace('`4gb=1`','`laa=1`')
    open(p,'w').write(s)
print('ok')

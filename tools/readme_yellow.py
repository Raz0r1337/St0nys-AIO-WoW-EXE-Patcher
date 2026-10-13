import sys
root=sys.argv[1]
def fix(fn,pairs,old_sent,new_sent,exp):
    p=root+'/'+fn
    raw=open(p,'rb').read()
    crlf=b'\r\n' in raw
    t=raw.decode('utf-8')
    if crlf: t=t.replace('\r\n','\n')
    a,b,c=pairs
    n1=t.count(a); t=t.replace(a,b)
    n2=t.count(c[0]); t=t.replace(c[0],c[1])
    assert t.count(old_sent)==1,(fn,'sent'); t=t.replace(old_sent,new_sent)
    assert (n1,n2)==exp,(fn,n1,n2)
    if crlf: t=t.replace('\n','\r\n')
    open(p,'wb').write(t.encode('utf-8'))
    print(fn,n1,n2,'crlf' if crlf else 'lf')
fix('README.de.md',
    ('🟢 **[sicher]**<br>🟡 **[Exe wird größer]**','🟡 **[sicher]**<br>**[Exe wird größer]**',
     ('<br>🟡 **[Exe wird größer]**','<br>**[Exe wird größer]**')),
    'Ein Patch kann mehrere Kennzeichnungen tragen, z. B. 🟢 **[sicher]** und\n🟡 **[Exe wird größer]**. Im Patcher',
    'Ein Patch kann mehrere Kennzeichnungen tragen, z. B. **[sicher]** und\n**[Exe wird größer]**. In der Übersicht hat jeder Patch nur einen Punkt: Bei\nsicheren Patches, die die Exe vergrößern, wird der grüne Punkt gelb\n(🟡 **[sicher]** **[Exe wird größer]**), rote und orange Punkte bleiben. Im Patcher',
    (3,3))
fix('README.md',
    ('🟢 **[safe]**<br>🟡 **[exe grows]**','🟡 **[safe]**<br>**[exe grows]**',
     ('<br>🟡 **[exe grows]**','<br>**[exe grows]**')),
    'A patch can carry several ratings, e.g. 🟢 **[safe]** and 🟡 **[exe grows]**.\n',
    'A patch can carry several ratings, e.g. **[safe]** and **[exe grows]**.\nIn the overview each patch has only one dot: for safe patches that grow\nthe exe the green dot turns yellow (🟡 **[safe]** **[exe grows]**); red\nand orange dots stay.\n',
    (3,3))

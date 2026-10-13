p='README.de.md'
t=open(p,encoding='utf-8').read()
old='''(🟡 **[sicher]** **[Exe wird größer]**), rote und orange Punkte bleiben. Im Patcher stehen die Warnungen in eckigen
Klammern hinter dem Namen, vor dem Patchen listet er sie noch einmal auf.'''
new='''(🟡 **[sicher]** **[Exe wird größer]**), rote und orange Punkte bleiben.
Im Patcher stehen die Warnungen in eckigen Klammern hinter dem Namen, vor
dem Patchen listet er sie noch einmal auf.'''
assert t.count(old)==1
open(p,'w',encoding='utf-8',newline='\n').write(t.replace(old,new))

import sys,re
sys.path.insert(0,sys.argv[1]+'/al'); import beta
S=sys.argv[1]; wt=sys.argv[2]; beta_ids=sys.argv[3].split(',') if len(sys.argv)>3 and sys.argv[3] else []
p=wt+'/apply_patches.ps1'; s=open(p,'rb').read().decode('ascii')
def once(a,b):
    global s; assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
# 1 bracket separator
once("$n = \"$n [$($tags -join ', ')]\"","$n = \"$n [$($tags -join ' - ')]\"")
# 2 orange warnings
once("    Say (T 'PublicHead') 'Yellow'\r\n    foreach ($m in $public) { Say \"  - $m\" 'Yellow' }\r\n    Say (T 'PublicBan') 'Red'",
     "    Say (T 'PublicHead') 'DarkYellow'\r\n    foreach ($m in $public) { Say \"  - $m\" 'DarkYellow' }\r\n    Say (T 'PublicBan') 'DarkYellow'")
once("    Say (T 'UntestedHead') 'Yellow'\r\n    foreach ($m in $untested) { Say \"  - $m\" 'Yellow' }\r\n    Say (T 'UntestedWarn') 'Red'",
     "    Say (T 'UntestedHead') 'DarkYellow'\r\n    foreach ($m in $untested) { Say \"  - $m\" 'DarkYellow' }\r\n    Say (T 'UntestedWarn') 'DarkYellow'")
# 3 comment colour words
once('#            (Code 3, gelber Hinweis)','#            (Code 3, oranger Hinweis)')
once('#            ist - moeglicherweise verbuggt (Code 4, gelber Hinweis)','#            ist - moeglicherweise verbuggt (Code 4, oranger Hinweis)')
# 4 icon prompt text
once("PromptDe = 'Icon-Datei (.ico oder .png), Pfad absolut oder relativ zum WoW-Ordner'","PromptDe = 'Icon-Datei (.ico oder .png), Pfad absolut oder relativ zum Ordner der Wow.exe'")
once("PromptEn = 'Icon file (.ico or .png), path absolute or relative to the WoW folder'","PromptEn = 'Icon file (.ico or .png), path absolute or relative to the folder of Wow.exe'")
# 5 No.40 rename to dev version
once("       De = 'Level 101+ Fix (Spielwert-Tabellen, Barbierstuhl, Grundwerte)'","       De = 'Level 101+ Druid Fix (Druiden-Werte im Charakterfenster, Barbierstuhl fuer alle)'")
once("       En = 'Level 101+ fix (game tables, barber chair, base stats)'","       En = 'Level 101+ Druid fix (druid stats in the character window, barber shop for everyone)'")
open(p,'wb').write(s.encode('ascii'))
# 6 BETA names
if beta_ids:
    s2=open(p,'rb').read().decode('ascii'); s2=beta.script(s2,beta_ids); open(p,'wb').write(s2.encode('ascii'))
print('patcher delta ok for',wt.split('/')[-1],'beta:',beta_ids)

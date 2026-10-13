import sys,re
wt=sys.argv[1]
def repl(path,pairs,enc,nl):
    s=open(path,encoding=enc,newline='').read()
    for a,b in pairs:
        c=s.count(a); assert c==1,('COUNT %d'%c,path.split('/')[-1],a[:70])
        s=s.replace(a,b)
    open(path,'w',encoding=enc,newline=nl).write(s)
# ---- name changes: (id, script_de_old, script_de_new, en_old, en_new, docs_de_old, docs_de_new)
N=[
 ('timer',
  'Genauen Timer immer nutzen (Ruckeln beim Drehen behoben)','Precise Timer Fix (behebt das Ruckeln beim Drehen des Charakters)',
  'Always use the precise timer (fixes turning stutter)','Precise timer fix (fixes the character turning stutter bug)',
  'Genauen Timer immer nutzen (Ruckeln beim Drehen behoben)','Precise Timer Fix (behebt das Ruckeln beim Drehen des Charakters)'),
 ('afk',
  'Idle-Kick nach Character-Autologin verhindern','CharAutoLogin Idle-Kick Fix',
  'Prevent the idle kick after character auto-login','CharAutoLogin idle-kick fix',
  'Idle-Kick nach Character-Autologin verhindern','CharAutoLogin Idle-Kick Fix'),
 ('awesome',
  'AwesomeWotlkLib.dll Unterstuetzung aktivieren','AwesomeWotlkLib.dll Unterstuetzung aktivieren (Client-Erweiterungen von noname08662)',
  'Enable AwesomeWotlkLib.dll support','Enable AwesomeWotlkLib.dll support (client extensions by noname08662)',
  'AwesomeWotlkLib.dll Unterstützung aktivieren','AwesomeWotlkLib.dll Unterstützung aktivieren (Client-Erweiterungen von noname08662)'),
 ('wotlkext',
  'WotLKExtensions.dll Unterstuetzung aktivieren','WotLKExtensions.dll Unterstuetzung aktivieren (Client-Erweiterungen von Alyst3r)',
  'Enable WotLKExtensions.dll support','Enable WotLKExtensions.dll support (client extensions by Alyst3r)',
  'WotLKExtensions.dll Unterstützung aktivieren','WotLKExtensions.dll Unterstützung aktivieren (Client-Erweiterungen von Alyst3r)'),
]
AUTH_OLD='Kebabstorm (fixed by St0ny)'; AUTH_NEW='St0ny (original by Kebabstorm)'
# ---- script (ASCII, CRLF) ----
sp=[]; 
for id_,sdo,sdn,eo,en,_,_ in N:
    sp.append(("De = '%s'"%sdo,"De = '%s'"%sdn)); sp.append(("En = '%s'"%eo,"En = '%s'"%en))
sp.append(("Author = '%s'"%AUTH_OLD,"Author = '%s'"%AUTH_NEW))
repl(wt+'/apply_patches.ps1',sp,'ascii','')
# ---- docs ----
for fn,md,lang in ((wt+'/docs/README.de.md','PATCHES.de.md','de'),(wt+'/docs/README.md','PATCHES.en.md','en')):
    pairs=[]
    for id_,sdo,sdn,eo,en,ddo,ddn in N:
        if lang=='de': pairs.append(('#patch-%s) | %s'%(id_,ddo),'#patch-%s) | %s'%(id_,ddn)))
        else: pairs.append(('#patch-%s) | %s'%(id_,eo),'#patch-%s) | %s'%(id_,en)))
    pairs.append(('| %s |'%AUTH_OLD,'| %s |'%AUTH_NEW))
    repl(fn,pairs,'utf-8','\n')
for fn,lang in ((wt+'/docs/PATCHES.de.md','de'),(wt+'/docs/PATCHES.en.md','en')):
    pairs=[]
    for id_,sdo,sdn,eo,en,ddo,ddn in N:
        if lang=='de': pairs.append(('**%s**'%ddo,'**%s**'%ddn))
        else: pairs.append(('**%s**'%eo,'**%s**'%en))
    word='Autor' if lang=='de' else 'Author'
    pairs.append(('%s: %s)'%(word,AUTH_OLD),'%s: %s)'%(word,AUTH_NEW)))
    repl(fn,pairs,'utf-8','\n')
print('renames applied:',wt.split('/')[-1])

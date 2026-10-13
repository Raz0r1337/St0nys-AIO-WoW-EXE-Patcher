# Prueft: Status-Spalte jeder README-Zeile und Badge jeder PATCHES-Ueberschrift
# passt zu den Flags im Skript (BanRisk, PublicUntested, GameUntested, GrowsExe, DllRisky).
import re,sys
d=sys.argv[1]; P='docs/'
src=open(d+'/apply_patches.ps1',encoding='ascii').read()
heads=re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$",src)
TXT={'de':dict(ban='unsicher',both='ungetestet',pub='online ungetestet',game='ingame ungetestet',grow='Exe wird größer',dll='DLL riskant',safe='sicher'),
     'en':dict(ban='unsafe',both='untested',pub='untested online',game='untested ingame',grow='exe grows',dll='DLL risky',safe='safe')}
def badge(h,lang):
    t=TXT[lang]; f=lambda k:(k+' = $true') in h
    tags=[]
    if f('BanRisk'): tags.append(t['ban'])
    if f('PublicUntested') and f('GameUntested'): tags.append(t['both'])
    elif f('PublicUntested'): tags.append(t['pub'])
    elif f('GameUntested'): tags.append(t['game'])
    base_unsafe=bool(tags)
    if f('GrowsExe'): tags.append(t['grow'])
    if f('DllRisky'): tags.append(t['dll'])
    if not base_unsafe: tags.insert(0,t['safe'])
    if f('BanRisk'): dot='🔴'
    elif f('PublicUntested') or f('GameUntested'): dot='🟠'
    elif f('GrowsExe') or f('DllRisky'): dot='🟡'
    else: dot='🟢'
    return '%s **[%s]**'%(dot,' - '.join(tags))
bad=0
for lang,fn,md in (('de','README.de.md','PATCHES.de.md'),('en','README.md','PATCHES.en.md')):
    s=open(d+'/'+P+fn,encoding='utf-8').read()
    rows=dict(re.findall(r'(?m)^\| \[\d+\]\(%s#patch-([^)]+)\) \|.*?\| ([🟢🟡🟠🔴] \*\*\[[^\]]+\]\*\*) \|'%re.escape(md),s))
    p=open(d+'/'+P+md,encoding='utf-8').read()
    secs=dict(re.findall(r'<a id="patch-([^"]+)"></a>\n\*\*[^\n]*?\*\* \*\([^\n]*?\)\* ([🟢🟡🟠🔴] \*\*\[[^\]]+\]\*\*)',p))
    n=0
    for i,(pid,h) in enumerate(heads):
        exp=badge(h,lang)
        for where,got in (('README',rows.get(pid)),('PATCHES',secs.get(pid))):
            if got!=exp: print('  MISMATCH',lang,where,i+1,pid,'got',got,'exp',exp); bad=1
            else: n+=1
    print(d.split('/')[-1],lang,'checked',n)
print('BADGES BAD' if bad else 'BADGES OK')

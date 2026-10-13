import sys,re,os
sys.path.insert(0,sys.argv[1]+'/al'); import portdocs as P
S=sys.argv[1]; which=sys.argv[2]
CFG={
 'y38':dict(wt=S+'/wt-y38w',remove=['wowoptimize','lexara'],add=[('y38fix','clienticon')],variant='base'),
 'out':dict(wt=S+'/wt-out',remove=['wowoptimize','lexara'],add=[('outline','iconsnap')],variant='base'),
 'lg':dict(wt=S+'/wt-lg',remove=['wowoptimize'],add=[('lights','iconsnap'),('lightstay','lights')],variant='lights'),
}
MID={'base':{'de':'Drei davon (Nr. 9, 63 und 64) vergrößern die `Wow.exe`; auf\nWarmane war das kein Problem, andere Server können die Dateigröße aber prüfen.',
             'en':'Three of them (No. 9, 63 and 64) make `Wow.exe` larger; that was no problem\non Warmane, but other servers may check the file size.'},
 'lights':{'de':'Vier davon (Nr. 9, 64, 65 und 66) vergrößern die `Wow.exe`; auf\nWarmane war das kein Problem, andere Server können die Dateigröße aber prüfen.\nDazu kommen der Lexara-Lader (Nr. 29) für Stormhands HD-Schriften und die\nLicht-Patches Nr. 66 und 67. Sie sind noch ungetestet; ohne `Lexara.dll` im\nWoW-Ordner bewirkt Nr. 29 nichts.',
           'en':'Four of them (No. 9, 64, 65 and 66) make `Wow.exe` larger; that was no\nproblem on Warmane, but other servers may check the file size. On top of that\ncome the Lexara loader (No. 29) for Stormhand’s HD fonts and the light patches\nNo. 66 and 67. They are still untested; without `Lexara.dll` in the WoW folder\nNo. 29 does nothing.'}}
c=CFG[which]; wt=c['wt']
order,cat,flags,pres=P.meta(wt+'/apply_patches.ps1')
def blank(R,lang):
    regions=[]
    if lang=='de':
        pats=[('BAN',r'(zu einem Bann führen: )Nr\. [0-9,\s–und]+?( \(rote)'),
              ('PUB',r'(kann zu Kick/Bann führen: )Nr\. [0-9,\s–und]+?(\s*\(orange)'),
              ('GAME',r'(möglicherweise verbuggt: )Nr\. [0-9,\s–und]+?( \(orange)'),
              ('GROW',r'(hängen eine Sektion an die `Wow\.exe` an:\n\s*)Nr\. [0-9,\s–und]+?(\. Das ist)'),
              ('SIG',r'(die eine Sektion anhängen \()Nr\. [0-9,\s–und]+?(\), entfernen)'),
              ('REF',r'(verwendet werden\. ).*?( Welche Patches\ndazugehören)')]
    else:
        pats=[('BAN',r'(can lead to a ban on many servers: )No\. [0-9,\s–and]+?( \(red)'),
              ('PUB',r'(may get\s*you kicked or banned: )No\. [0-9,\s–and]+?(\s*\(orange)'),
              ('GAME',r'(possibly buggy: )No\. [0-9,\s–and]+?( \(orange)'),
              ('GROW',r'(append a section to `Wow\.exe`: )No\. [0-9,\s–and]+?(\. This does not)'),
              ('SIG',r'(that append a section\s*\()No\. [0-9,\s–and]+?(\) also remove)'),
              ('REF',r'(public servers as well\. ).*?( The "Reforged" column)')]
    for key,pat in pats:
        nn=len(re.findall(pat,R,re.S)); assert nn==1,(lang,key,nn)
        R=re.sub(pat, lambda m,k=key:m.group(1)+('@@%s@@'%k)+m.group(2), R, count=1, flags=re.S)
    return R
def fill(R,lang):
    pos=lambda fl: sorted(order.index(i)+1 for i in order if fl in flags[i])
    w='und' if lang=='de' else 'and'
    vals={'BAN':'Nr. '+P.joinlist(pos('BanRisk'),w) if lang=='de' else 'No. '+P.joinlist(pos('BanRisk'),w),
          'PUB':('Nr. ' if lang=='de' else 'No. ')+P.joinlist(pos('PublicUntested'),w),
          'GAME':('Nr. ' if lang=='de' else 'No. ')+P.joinlist(pos('GameUntested'),w),
          'GROW':('Nr. ' if lang=='de' else 'No. ')+P.joinlist(pos('GrowsExe'),w),
          'SIG':('Nr. ' if lang=='de' else 'No. ')+P.joinlist(pos('GrowsExe'),w),
          'REF':MID[c['variant']][lang]}
    for k,v in vals.items(): R=R.replace('@@%s@@'%k,v)
    return R
for lang,md,devR,devP,oldR,oldP,outR,outP in (
   ('de','PATCHES.de.md',S+'/wt-dev2/docs/README.de.md',S+'/wt-dev2/docs/PATCHES.de.md',wt+'/README.de.md',wt+'/PATCHES.de.md',wt+'/docs/README.de.md',wt+'/docs/PATCHES.de.md'),
   ('en','PATCHES.en.md',S+'/wt-dev2/docs/README.md',S+'/wt-dev2/docs/PATCHES.en.md',wt+'/README.md',wt+'/PATCHES.en.md',wt+'/docs/README.md',wt+'/docs/PATCHES.en.md')):
    R=open(devR,encoding='utf-8').read(); Pt=open(devP,encoding='utf-8').read()
    oR=open(oldR,encoding='utf-8').read(); oP=open(oldP,encoding='utf-8').read()
    n2id=P.dev_num2id(R,md)
    for rid in c['remove']:
        row=P.get_row(R,md,rid); assert row,(rid,'row'); R=R.replace(row+'\n','',1)
        sec=P.get_section(Pt,rid); Pt=Pt.replace(sec,'',1)
    for aid,pred in c['add']:
        oldrow=P.get_row(oR,md,aid); nr=P.new_row(oldrow,aid,lang)
        predrow=P.get_row(R,md,pred); R=P.insert_after(R,predrow+'\n',nr+'\n')
        oldsec=P.get_section(oP,aid); nsec=P.new_section(oldsec,aid,lang)
        predsec=P.get_section(Pt,pred); Pt=P.insert_after(Pt,predsec,nsec)
    R=blank(R,lang)
    R=P.renum_readme(R,md,order); R=P.remap_cross(R,n2id,order)
    Pt=P.renum_sections(Pt,order); Pt=P.remap_cross(Pt,n2id,order)
    R=fill(R,lang)
    os.makedirs(wt+'/docs',exist_ok=True)
    open(outR,'w',encoding='utf-8',newline='\n').write(R)
    open(outP,'w',encoding='utf-8',newline='\n').write(Pt)
    ov=re.findall(r'(?m)^\| \[(\d+)\]\(%s#patch-([a-z0-9]+)\)'%re.escape(md),R)
    assert [x[1] for x in ov]==order,'order README '+lang
    assert [int(x[0]) for x in ov]==list(range(1,len(order)+1)),'num README '+lang
    anc=re.findall(r'<a id="patch-([a-z0-9]+)"></a>\n\*\*.*?\*\* \*\((?:Nr\.|No\.) (\d+)[,)]',Pt,re.S)
    assert [a for a,_ in anc]==order,'order PATCHES '+lang
    assert [int(b) for _,b in anc]==list(range(1,len(order)+1)),'num PATCHES '+lang
    assert '@@' not in R and '@@' not in Pt,'leftover sentinel'
print(which,'OK',len(order),'patches')

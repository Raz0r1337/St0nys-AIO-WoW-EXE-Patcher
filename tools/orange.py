import re,sys
d=sys.argv[1]
def rd(fn): 
    raw=open(d+'/'+fn,'rb').read(); assert b'\r\n' not in raw; return raw.decode('utf-8')
def wr(fn,t): open(d+'/'+fn,'w',encoding='utf-8',newline='\n').write(t)
def once(t,a,b,fn):
    assert t.count(a)==1,(fn,a[:60],t.count(a)); return t.replace(a,b)
CFG={'README.de.md':dict(
        intro=('''Warnung tragen – mit roter Warnung bei Bann-Gefahr und bei Patches, die auf
öffentlichen Servern oder im Spiel noch ungetestet sind, gelb bei vergrößerter
`Wow.exe` (siehe [Hinweise](#hinweise)).''','''Warnung tragen – rot bei Bann-Gefahr, orange bei Patches, die auf öffentlichen
Servern oder im Spiel noch ungetestet sind, und gelb bei vergrößerter
`Wow.exe` (siehe [Hinweise](#hinweise)).'''),
        old='rote',new='orange',cell=('| rote Warnung |','| orange Warnung |')),
     'README.md':dict(
        intro=('''with a red warning for ban risk and for patches that are still untested on
public servers or in game, yellow for a larger `Wow.exe` (see [Notes](#notes)).''','''red for ban risk, orange for patches that are still untested on public
servers or in game, and yellow for a larger `Wow.exe` (see [Notes](#notes)).'''),
        old='red',new='orange',cell=('| red warning |','| orange warning |'))}
for fn,c in CFG.items():
    t=rd(fn)
    t=once(t,*c['intro'],fn)
    # Legende: die drei orangen Zeilen
    n=[0]
    def row(m):
        n[0]+=1; return m.group(0).replace(*c['cell'])
    t=re.sub(r'(?m)^\| 🟠 \*\*\[[^\]]+\]\*\* \|.*'+re.escape(c['cell'][0])+r'$',row,t)
    assert n[0]==3,(fn,n[0])
    # Hinweise: orange Aufzaehlungspunkte
    k=[0]
    def bullet(m):
        s=m.group(0); r=re.sub(r'\(%s(\s+)(Warnung|warning)\)'%c['old'],lambda x:'(%s%s%s)'%(c['new'],x.group(1),x.group(2)),s)
        if r!=s: k[0]+=1
        return r
    t=re.sub(r'(?m)^  - 🟠 .*(?:\n    .*)*',bullet,t)
    assert k[0]==2,(fn,k[0])
    wr(fn,t); print(fn,'ok')
p=d+'/apply_patches.ps1'; raw=open(p,'rb').read()
for a,b in ((b"    Say (T 'PublicHead') 'Yellow'",b"    Say (T 'PublicHead') 'DarkYellow'"),
            (b"    foreach ($m in $public) { Say \"  - $m\" 'Yellow' }",b"    foreach ($m in $public) { Say \"  - $m\" 'DarkYellow' }"),
            (b"    Say (T 'PublicBan') 'Red'",b"    Say (T 'PublicBan') 'DarkYellow'"),
            (b"    Say (T 'UntestedHead') 'Yellow'",b"    Say (T 'UntestedHead') 'DarkYellow'"),
            (b"    foreach ($m in $untested) { Say \"  - $m\" 'Yellow' }",b"    foreach ($m in $untested) { Say \"  - $m\" 'DarkYellow' }"),
            (b"    Say (T 'UntestedWarn') 'Red'",b"    Say (T 'UntestedWarn') 'DarkYellow'"),
            (b"#            (Code 3, gelber Hinweis)",b"#            (Code 3, oranger Hinweis)"),
            (b"ist - moeglicherweise verbuggt (Code 4, gelber Hinweis)",b"ist - moeglicherweise verbuggt (Code 4, oranger Hinweis)")):
    assert raw.count(a)==1,a; raw=raw.replace(a,b)
open(p,'wb').write(raw); print('ps1 ok')

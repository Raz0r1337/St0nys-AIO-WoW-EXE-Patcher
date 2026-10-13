import re,os,json
os.chdir('/home/user/St0nys-WoW-EXE-Patcher')
mp={int(k):v for k,v in json.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/tm/renum3.json')).items()}
sh=lambda n: str(mp[int(n)])
def refs(s):
    pat=re.compile(r'(Nr\.|No\.) (\d+)((?:, \d+)*)((?: (?:und|and) (?:Nr\. |No\. )?)(\d+))?')
    def f(m):
        out=m.group(1)+' '+sh(m.group(2))
        if m.group(3): out+=re.sub(r'\d+',lambda x: sh(x.group(0)),m.group(3))
        if m.group(4): out+=m.group(4)[:-len(m.group(5))]+sh(m.group(5))
        return out
    return pat.sub(f,s)
def table(s,md): return re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(sh(m.group(1)),md), s)
def once(s,old,new):
    assert s.count(old)==1,(old[:80],s.count(old)); return s.replace(old,new)
def after_row(s,anchor_id,md,rows):
    i=s.index('](%s#patch-%s)'%(md,anchor_id)); j=s.index('\n',i)+1
    return s[:j]+rows+s[j:]
R={'de':'| [10](PATCHES.md#patch-glyphfix) | Schrift-Glyphen-Fix (falsche oder kaputte Zeichen in Texten) – ungetestet *(Exe wird größer – Bann-Gefahr)* | Hour of Twilight (ported by St0ny) | – | – | – |\n',
   'en':'| [10](PATCHES.en.md#patch-glyphfix) | Font glyph fix (wrong or garbled characters in text) – untested *(exe grows – ban risk)* | Hour of Twilight (ported by St0ny) | – | – | – |\n'}
for p,md,lang in (('README.md','PATCHES.md','de'),('README.en.md','PATCHES.en.md','en')):
    s=open(p,encoding='utf-8').read()
    s=table(s,md); s=refs(s)
    s=after_row(s,'wmocube',md,R[lang])
    if lang=='de':
        s=s.replace('Nr. 10, 51, 64 und 77','Nr. 10, 51, 64 und 77')  # check below
    open(p,'w',encoding='utf-8',newline='\n').write(s)

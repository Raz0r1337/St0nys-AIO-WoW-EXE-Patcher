import re,sys,subprocess,importlib.util
S=sys.argv[1]; DEV=S+'/wt-dev2'
def meta(path):
    s=open(path,encoding='ascii').read()
    order=re.findall(r"(?m)^    @\{ Id = '([^']+)'",s)
    cat={}; flags={}
    for m in re.finditer(r"(?ms)^    @\{ Id = '([^']+)';([^\n]*).*?\n    \}\}",s):
        i=m.group(1); cat[i]=re.search(r"Cat = '([^']+)'",m.group(0)).group(1)
        flags[i]=set(k for k in ('BanRisk','PublicUntested','GameUntested','GrowsExe') if k+' = $true' in m.group(2))
    pres={}
    for nm in ('REFORGED','BILLY','STONY'):
        mm=re.search(r'\$PRESET_%s = @\((.*?)\)'%nm,s,re.S); pres[nm]=set(re.findall(r"'([^']+)'",mm.group(1))) if mm else set()
    return order,cat,flags,pres
def rng(L):
    out=[];i=0
    while i<len(L):
        j=i
        while j+1<len(L) and L[j+1]==L[j]+1: j+=1
        out+=([str(L[i])] if j==i else ([str(L[i]),str(L[j])] if j==i+1 else ['%d–%d'%(L[i],L[j])])); i=j+1
    return out
def joinlist(L,word): r=rng(L); return (', '.join(r[:-1])+' '+word+' '+r[-1]) if len(r)>1 else r[0]
def renum_readme(s,md,order):
    # own numbers in links
    def f(m): return '| [%d](%s#patch-%s)'%(order.index(m.group(2))+1,md,m.group(2))
    return re.sub(r'\| \[(\d+)\]\(%s#patch-([a-z0-9]+)\)'%re.escape(md),f,s)
def renum_sections(s,order):
    def f(m):
        return '<a id="patch-%s"></a>\n%s*(%s %d%s'%(m.group(1),m.group(2),m.group(3),order.index(m.group(1))+1,m.group(4))
    return re.sub(r'<a id="patch-([a-z0-9]+)"></a>\n(\*\*.*?\*\* )\*\((Nr\.|No\.) \d+([,)])',f,s,flags=re.S)
def remap_cross(s,dev_n2id,order):
    # bare cross-refs: (Nr.|No.) N not preceded by '*(' ; also 'N und/and M'
    def one(n):
        n=int(n); 
        if n not in dev_n2id: return None
        i=dev_n2id[n]
        return order.index(i)+1 if i in order else None
    def f(m):
        a=one(m.group(2))
        if a is None: raise SystemExit('dangling crossref %s -> %s'%(m.group(2),dev_n2id.get(int(m.group(2)))))
        out='%s %d'%(m.group(1),a)
        if m.group(3):
            b=one(m.group(4)); assert b is not None
            out+=m.group(3)+str(b)
        return out
    return re.sub(r'(?<!\*\()(Nr\.|No\.) (\d+)(?!\d)(?:( (?:und|and) )(\d+)(?!\d))?',f,s)

BADGE={'outline':{'de':'🟠 **[online ungetestet - Exe wird größer]**','en':'🟠 **[untested online - exe grows]**'},
 'lights':{'de':'🟠 **[ungetestet - Exe wird größer]**','en':'🟠 **[untested - exe grows]**'},
 'lightstay':{'de':'🟠 **[ungetestet]**','en':'🟠 **[untested]**'},
 'y38fix':{'de':'🟠 **[ungetestet]**','en':'🟠 **[untested]**'}}
BETABOX={'de':'> [!WARNING]\n> **BETA** – dieser Patch ist noch in der Testphase und deshalb vorerst nur in\n> den dev-Zweigen, nicht in `st0ny-main`.\n',
         'en':'> [!WARNING]\n> **BETA** – this patch is still being tested and is therefore only in the dev\n> branches for now, not in `st0ny-main`.\n'}
def get_row(doc,md,id): 
    m=re.search(r'(?m)^\| \[\d+\]\(%s#patch-%s\) \|.*$'%(re.escape(md),id),doc); return m.group(0) if m else None
def get_section(doc,id):
    a=doc.index('<a id="patch-%s"></a>'%id)
    nx=[k for k in (doc.find('\n<a id="',a+1),doc.find('\n## ',a+1)) if k!=-1]
    b=min(nx) if nx else len(doc)-1
    return doc[a:b+1]
def new_row(oldrow,id,lang):
    # replace status cell (3rd column) and add [BETA] to name
    parts=oldrow.split(' | ')
    # parts[0]='| [N](..) ', parts[1]=name(+note), parts[2]=status, rest...
    name=parts[1]
    if ' *(' in name: name=name.replace(' *(',' [BETA] *(',1)
    else: name=name+' [BETA]'
    parts[1]=name; parts[2]=BADGE[id][lang]
    return ' | '.join(parts)
def new_section(oldsec,id,lang):
    lines=oldsec.split('\n')
    h=lines[1]
    m=re.match(r'(\*\*.*?)\*\*( \*\(.*?\)\*) ',h); assert m,h
    lines[1]='%s [BETA]**%s %s'%(m.group(1),m.group(2),BADGE[id][lang])
    # drop the first blockquote box if it is the online/ingame-untested warning
    out=[]; i=0
    dropped=False
    while i<len(lines):
        if (not dropped and lines[i].startswith('> [!WARNING]')):
            j=i; blk=[]
            while j<len(lines) and (lines[j].startswith('>') or lines[j]=='>'):
                blk.append(lines[j]); j+=1
            txt=' '.join(blk).lower()
            if ('ungetestet' in txt or 'untested' in txt) and 'beta' not in txt and 'alpha' not in txt:
                # also eat one trailing blank line
                if j<len(lines) and lines[j]=='': j+=1
                dropped=True; i=j; continue
        out.append(lines[i]); i+=1
    sec='\n'.join(out)
    hl=sec.index('\n',sec.index('**'))
    p2=sec.index('\n\n',hl+1)+1
    sec=sec[:p2]+'\n'+BETABOX[lang]+sec[p2:]
    return sec

def insert_after(doc,anchor_block,new_block):
    i=doc.index(anchor_block)+len(anchor_block)
    return doc[:i]+new_block+doc[i:]

def dev_num2id(devreadme,md):
    d={}
    for m in re.finditer(r'\| \[(\d+)\]\(%s#patch-([a-z0-9]+)\)'%re.escape(md),devreadme):
        d[int(m.group(1))]=m.group(2)
    return d
def legends_readme(R,order,flags):
    def poslist(flagset_pred):
        return sorted(order.index(i)+1 for i in order if flagset_pred(flags[i]))
    ban=poslist(lambda f:'BanRisk' in f)
    pub=poslist(lambda f:'PublicUntested' in f)
    game=poslist(lambda f:'GameUntested' in f)
    grow=poslist(lambda f:'GrowsExe' in f)
    def sub(pat,repl): 
        nonlocal R
        n=len(re.findall(pat,R,re.S)); assert n==1,(pat,n); R=re.sub(pat,lambda m:repl,R,flags=re.S)
    return R,ban,pub,game,grow

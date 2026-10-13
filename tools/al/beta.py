# [BETA]-Kennzeichnung fuer Patches, die (noch) nicht in st0ny-main sind.
import re
BOX={'de':"> [!WARNING]\n> **BETA** – dieser Patch ist noch in der Testphase und deshalb vorerst nur in\n> den dev-Zweigen, nicht in `st0ny-main`.\n",
     'en':"> [!WARNING]\n> **BETA** – this patch is still being tested and is therefore only in the dev\n> branches for now, not in `st0ny-main`.\n"}
def once(s,a,b):
    assert s.count(a)==1,(a[:90],s.count(a)); return s.replace(a,b)
def script(s,ids):
    """s: Skripttext mit CRLF. Haengt ' [BETA]' an De/En der Eintraege an."""
    for pid in ids:
        i=s.index("    @{ Id = '%s';"%pid); j=s.index('    }}\r\n',i)
        ent=s[i:j]
        for k in ('De','En'):
            m=re.search(r"(?m)^       %s = '([^']*)'\r$"%k,ent); assert m,(pid,k)
            assert '[BETA]' not in m.group(1)
            ent=ent[:m.start(1)]+m.group(1)+' [BETA]'+ent[m.end(1):]
        s=s[:i]+ent+s[j:]
    return s
def readme(s,md,ids):
    for pid in ids:
        m=re.search(r'(?m)^(\| \[\d+\]\(%s#patch-%s\) \| )([^|]*?)( \*\(.*?\)\*)? \|'%(re.escape(md),re.escape(pid)),s); assert m,pid
        assert '[BETA]' not in m.group(2)
        s=s[:m.end(2)]+' [BETA]'+s[m.end(2):]
    return s
def patches(s,lang,ids):
    for pid in ids:
        a='<a id="patch-%s"></a>\n'%pid; i=s.index(a)+len(a)
        m=re.match(r'\*\*(.*?)\*\*',s[i:]); assert m,pid
        assert '[BETA]' not in m.group(1)
        s=s[:i+m.end(1)]+' [BETA]'+s[i+m.end(1):]
        # BETA-Kasten hinter den ersten Absatz
        h=s.index('\n',i)+1; assert s[h]=='\n',(pid,'blank after heading')
        p=s.index('\n\n',h+1)+1
        s=s[:p]+'\n'+BOX[lang]+s[p:]
    return s

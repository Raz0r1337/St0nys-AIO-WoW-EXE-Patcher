import re,sys
d=sys.argv[1]; P=sys.argv[2] if len(sys.argv)>2 else 'docs/'
src=open(d+'/apply_patches.ps1',encoding='ascii').read()
ids=re.findall(r"(?m)^    @\{ Id = '([^']+)'",src)
print('script patches',len(ids))
bad=0
for fn,md,nr in ((P+'README.de.md','PATCHES.de.md','Nr.'),(P+'README.md','PATCHES.en.md','No.')):
    s=open(d+'/'+fn,encoding='utf-8').read()
    rows=re.findall(r'(?m)^\| \[(\d+)\]\(%s#patch-([^)]+)\)'%re.escape(md),s)
    nums=[int(n) for n,_ in rows]; aid=[a for _,a in rows]
    ok=nums==list(range(1,len(ids)+1)) and aid==ids
    print(fn,'rows',len(rows),'OK' if ok else 'MISMATCH'); bad|=not ok
    if not ok:
        for i,(n,a) in enumerate(rows):
            if n!=str(i+1) or i>=len(ids) or a!=ids[i]: print('  ',i+1,n,a,ids[i] if i<len(ids) else None); break
for fn,nr in ((P+'PATCHES.de.md','Nr.'),(P+'PATCHES.en.md','No.')):
    s=open(d+'/'+fn,encoding='utf-8').read()
    secs=re.findall(r'<a id="patch-([^"]+)"></a>\n\*\*[^\n]*?\*\* \*\(%s (\d+)[,)]'%re.escape(nr),s)
    anchors=re.findall(r'<a id="patch-([^"]+)"></a>',s)
    ok=[a for a,_ in secs]==ids and [int(n) for _,n in secs]==list(range(1,len(ids)+1)) and len(anchors)==len(ids)
    print(fn,'sections',len(secs),'anchors',len(anchors),'OK' if ok else 'MISMATCH'); bad|=not ok
    if not ok:
        for i,(a,n) in enumerate(secs):
            if i>=len(ids) or a!=ids[i] or int(n)!=i+1: print('  ',i+1,a,n,ids[i] if i<len(ids) else None); break
print('BAD' if bad else 'ALL OK')

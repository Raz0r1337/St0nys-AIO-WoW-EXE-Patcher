import sys,re
d=sys.argv[1]
p=d+'/apply_patches.ps1'; s=open(p,'rb').read().decode('ascii')
old="    'glue', 'mpqsig', 'mpqnames', 'localdata', 'awesome',\r\n"
assert s.count(old)==1; s=s.replace(old,"    'glue', 'awesome',\r\n")
open(p,'wb').write(s.encode('ascii'))
for fn,lk in (('README.md','PATCHES.en.md'),('README.de.md','PATCHES.de.md')):
    p=d+'/'+fn; s=open(p,encoding='utf-8').read()
    for n,a in ((20,'mpqsig'),(21,'mpqnames'),(22,'localdata')):
        m=re.search(r'^\| \[%d\]\(%s#patch-%s\) \|.*$'%(n,re.escape(lk),a),s,re.M); assert m,(fn,n)
        cells=m.group(0).split(' | ')
        assert cells[4]=='✅',(fn,n,cells)
        cells[4]='–'; s=s[:m.start()]+' | '.join(cells)+s[m.end():]
    open(p,'w',encoding='utf-8').write(s)
print('ok',d)

import re,sys,json
ids=lambda p: re.findall(r"(?m)^    @\{ Id = '([a-z0-9]+)'", open(p,encoding='utf-8').read())
old=ids(sys.argv[1]); new=ids(sys.argv[2])
m={i+1:new.index(x)+1 for i,x in enumerate(old)}
spec=json.load(open(sys.argv[3],encoding='utf-8'))
for p,lang in (('README.md','de'),('README.en.md','en')):
    s=open(p,encoding='utf-8',newline='').read()
    head='| Nr. | Patch | Autor | Standard |' if lang=='de' else '| No. | Patch | Author | Default |'
    i=s.index(head); j=s.index('\n\n',i); tbl=s[i:j]
    tbl=re.sub(r'(?m)^\| (\d+) +\|', lambda mm: f"| {m[int(mm.group(1))]:<2} |", tbl)
    s=s[:i]+tbl+s[j:]
    s=re.sub(r'(Nr\.|No\.) (\d+)', lambda mm: f"{mm.group(1)} {m[int(mm.group(2))]}" if int(mm.group(2)) in m else mm.group(0), s)
    s=re.sub(r'((?:Nr\.|No\.) \d+ (?:und|and) )(\d+)', lambda mm: f"{mm.group(1)}{m[int(mm.group(2))]}", s)
    for e in spec:
        n=new.index(e['id'])+1; prev=new.index(e['id'])  # predecessor number
        row=f"| {n:<2} | {e[lang]['row']} |\n"
        i=s.index(head); j=s.index('\n\n',i); tbl=s[i:j]
        a=re.search(rf'(?m)^\| {prev} +\|.*\n', tbl)
        tbl=tbl[:a.end()]+row+tbl[a.end():]
        s=s[:i]+tbl+s[j:]
        # description after predecessor's block
        k=re.search(rf'\*\((?:Nr|No)\. {prev}[,)]', s).start()
        nxt=re.search(r'(?m)^(\*\*[^\n]*\*\((?:Nr|No)\. \d+[,)]|### |## |---)', s[k+5:])
        pos=k+5+nxt.start()
        s=s[:pos]+e[lang]['desc'].replace('{N}',str(n))+'\n'+s[pos:]
    open(p,'w',encoding='utf-8',newline='').write(s)
print('ok')

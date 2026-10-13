import re,sys
ids=lambda p: re.findall(r"(?m)^    @\{ Id = '([a-z0-9]+)'", open(p,encoding='utf-8').read())
old=ids(sys.argv[1]); new=ids(sys.argv[2])
m={i+1:new.index(x)+1 for i,x in enumerate(old) if x in new}
removed=[i+1 for i,x in enumerate(old) if x not in new]
print('removed old numbers:',removed)
def rep(s,pairs,p):
    for o,n in pairs:
        c=s.count(o)
        if c!=1: sys.exit(f'{p}: count {c} for {o[:100]!r}')
        s=s.replace(o,n)
    return s
for p,lang in (('README.md','de'),('README.en.md','en')):
    s=open(p,encoding='utf-8',newline='').read()
    lab='Nr' if lang=='de' else 'No'
    head='| Nr. | Patch | Autor | Standard |' if lang=='de' else '| No. | Patch | Author | Default |'
    # remove table rows and description blocks of removed patches
    for r in removed:
        s,k=re.subn(r'(?m)^\| %d +\|.*\n'%r,'',s); assert k==1,(p,r,'row')
        mm=re.search(r'(?m)^\*\*[^\n]*\*\* \*\(%s\. %d[,)][^\n]*\n'%(lab,r),s); assert mm,(p,r,'block')
        nxt=re.search(r'(?m)^(\*\*[^\n]*\*\* \*\(%s\. \d+[,)]|### |## )'%lab,s[mm.end():])
        s=s[:mm.start()]+s[mm.end()+nxt.start():]
    # renumber table rows
    i=s.index(head); j=s.index('\n\n',i); tbl=s[i:j]
    tbl=re.sub(r'(?m)^\| (\d+) +\|', lambda mm: f"| {m[int(mm.group(1))]:<2} |", tbl)
    s=s[:i]+tbl+s[j:]
    # renumber references "Nr. X" / "No. X" and "Nr. X und Y"
    s=re.sub(r'(Nr\.|No\.) (\d+)', lambda mm: f"{mm.group(1)} {m[int(mm.group(2))]}" if int(mm.group(2)) in m else mm.group(0), s)
    s=re.sub(r'((?:Nr\.|No\.) \d+ (?:und|and) )(\d+)', lambda mm: f"{mm.group(1)}{m[int(mm.group(2))]}" if int(mm.group(2)) in m else mm.group(0), s)
    # bare-number lists in the ban-risk note
    if lang=='de':
        s=rep(s,[("Steigwinkel (38), Sprunghöhe (39), die\n  Sprungsteuerung (40–42) und der Doppelsprung (43).","Steigwinkel (36), Sprunghöhe (37), die\n  Sprungsteuerung (38–40) und der Doppelsprung (41)."),
                 ("Nr. 41,\n  55 und 66 –","Nr. 41,\n  53 und 64 –")],p)
    else:
        s=rep(s,[("climb angle (38), jump height (39), the air steering (40–42)\n  and the double jump (41).".replace("(41)","(43)"),"climb angle (36), jump height (37), the air steering (38–40)\n  and the double jump (41)."),
                 ("No. 41, 55 and 66","No. 41, 53 and 64")],p)
    open(p,'w',encoding='utf-8',newline='').write(s)
    print(p,'ok')

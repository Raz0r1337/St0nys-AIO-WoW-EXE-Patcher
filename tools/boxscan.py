import re,sys
fn=sys.argv[1]
t=open(fn,encoding='utf-8').read()
secs=re.split(r'(?m)^(?=<a id="patch-)',t)
STD=re.compile(r'^> \*\*(Unsicher|Online ungetestet|Ingame ungetestet|Unsafe|Untested online|Untested ingame)\*\* –')
GROW=re.compile(r'(wird größer|grows|larger)')
tot={'std':0,'stdonly_boxes':0,'mixed_boxes':0,'grow_boxes':0}
for s in secs[1:]:
    aid=re.match(r'<a id="patch-([^"]+)"',s).group(1)
    head=s.split('\n')[1]
    tags=re.findall(r'\*\*\[([^\]]+)\]\*\*',head[head.rfind('*)')+2:] if '*)' in head else head)
    boxes=re.findall(r'(?m)((?:^>.*\n?)+)',s)
    out=[]
    for b in boxes:
        lines=[l for l in b.split('\n') if l.strip()]
        kind=lines[0][4:-1] if lines[0].startswith('> [!') else '?'
        body=[l for l in lines[1:] if l.strip()!='>']
        std=[l for l in body if STD.match(l)]
        other=[l for l in body if not STD.match(l)]
        g=any(GROW.search(l) for l in other) and any(('Sektion' in l or 'section' in l) for l in other)
        tot['std']+=len(std)
        if std and not other: tot['stdonly_boxes']+=1; out.append('%s:STD%d'%(kind,len(std)))
        elif std and other: tot['mixed_boxes']+=1; out.append('%s:STD%d+%dlines'%(kind,len(std),len(other)))
        elif g: tot['grow_boxes']+=1; out.append('%s:GROW(%d)'%(kind,len(other)))
    if out or len(tags)>1: print(aid.ljust(16),'/'.join(tags).ljust(45),' '.join(out))
print(tot)

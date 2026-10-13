import re,sys
src=open('/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1',encoding='ascii',newline='').read()
b=src.index("# BEGIN ORIGINAL-BYTES\n$ORIGINAL_TABLE") if "# BEGIN ORIGINAL-BYTES\n$ORIGINAL_TABLE" in src else src.index("# BEGIN ORIGINAL-BYTES\r\n$ORIGINAL_TABLE")
tab=src[b:src.index("# END ORIGINAL-BYTES",b)]
ents=[]
for l in tab.replace("\r","").split("\n"):
    m=re.match(r'^([A-Za-z0-9_]+);([0-9A-F]+);([0-9A-F]+);([01])$',l.strip())
    if m: ents.append((m.group(1),int(m.group(2),16),len(m.group(3))//2))
F=lambda va: va-0x400C00
plan={
 'time':[(F(0x76CA1B),1),(F(0x5BFB0F),0x5BFB30-0x5BFB0F),(F(0x5BFB4B),3),(F(0x5B82C0),1),(F(0x5B7A83),0x5B7AC4-0x5B7A83),
         (F(0x5B8F33),1),(F(0x5B8F38),1),(F(0x5B8F9B),1),(F(0x5B8F9F),1),(F(0x5BFF46),1),(F(0x5BFF5B),1),(F(0x5C01FB),1),(F(0x5C04C1),1),(F(0x5C2683),1),(F(0x5C2893),1)],
 'wext':[(F(0x406D70),5),(F(0x4E5D00),0x30),(F(0x4DCCF0),6)],
}
for pid,rs in plan.items():
    for (o,n) in rs:
        for (eid,eo,en) in ents:
            if eo<o+n and o<eo+en:
                print('OVERLAP %s %X+%d with %s %X+%d'%(pid,o,n,eid,eo,en))
print('entries',len(ents))
# also print entries near the regions of interest
for (eid,eo,en) in ents:
    if 0xE5000<=eo<0xE5400 or 0xDC000<=eo<0xDC200 or 0x6000<=eo<0x6300 or 0x1B6000<=eo<0x1C2000 or 0x36B000<=eo<0x36D000:
        print('near',eid,hex(eo),en)

import re,json
src=open('/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1',encoding='ascii',newline='').read()
b=src.index("# BEGIN ORIGINAL-BYTES\r\n$ORIGINAL"); tab=src[b:src.index("# END ORIGINAL-BYTES",b)]
ents=[]
for l in tab.replace("\r","").split("\n"):
    m=re.match(r'^([A-Za-z0-9_]+);([0-9A-F]+);([0-9A-F]+);([01])$',l.strip())
    if m: ents.append((m.group(1),int(m.group(2),16),len(m.group(3))//2))
sites=[(0x6C0E80,6)]
dw=json.load(open('dllwrites.json'))
for va,n in sites:
    o=va-0x400C00
    for e,eo,en in ents:
        if eo<o+n and o<eo+en: print('TABLE overlap',hex(va),e)
    for wva,wn,f in dw:
        if wva<va+n and va<wva+wn: print('DLL overlap',hex(va),hex(wva),f)
print('ok',len(ents),len(dw))

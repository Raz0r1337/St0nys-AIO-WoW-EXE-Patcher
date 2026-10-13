import json,re
w=json.load(open('tm/dllwrites.json'))
w=[(a,n,f) for a,n,f in w]
def add(lst,minus4,src):
    for a in lst: w.append((a-4 if minus4 else a,4,src))
add([0x61DDB7,0x625590,0x62572F,0x6258BC,0x625B20,0x625C9A,0x62643A,0x6264C7,0x626687,0x626F0C,0x626F4A,0x62DC3D,0x62DCC5,0x62E9FD,0x62EA9F,0x62EC90,0x630F95,0x630FC4,0x63136D],True,'CGTooltip setSpell')
add([0x626708,0x62C412,0x62DBC1,0x62E1C8,0x62E376,0x62E4BE,0x62E649,0x62E767,0x62E8D4,0x62EA72,0x62EC56,0x62ED52,0x62EE50,0x62EFCC,0x62F1C1,0x62F3FB,0x62F6C7,0x62F98C,0x62FBE0,0x62FCB1,0x62FEF7,0x630092,0x630190,0x63023B,0x63035B,0x630495,0x630600,0x630780,0x6307D2,0x630930,0x630982,0x630A74,0x630B70,0x630C5D,0x630EBD,0x630EFB,0x6312B5,0x6312E5,0x631915,0x6319C4,0x631B11],True,'CGTooltip setItem')
add([0x702AAF,0x702AFC,0x7033E0,0x72E1D4,0x80282A],True,'CMissile')
add([0x510440,0x510460,0x52B2BC,0x6B204C,0x6B21F9],True,'Misc logout')
add([0x4E157D,0x4E16A3,0x4E15B5,0x4E20EE,0x4E222A,0x4E2127,0x4E1E94,0x4E1C3A],False,'CGPlayer race')
add([0x552948,0x553B7D,0x553B94,0x553DE7,0x554922],False,'CGPlayer lfd')
src=open('/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1',encoding='ascii',newline='').read()
b=src.index("# BEGIN ORIGINAL-BYTES\r\n$ORIGINAL_TABLE")
tab=src[b:src.index("# END ORIGINAL-BYTES",b)]
ents=[]
for l in tab.replace('\r','').split('\n'):
    m=re.match(r'^([A-Za-z0-9_]+);([0-9A-F]+);([0-9A-F]+);([01])$',l.strip())
    if m:
        o=int(m.group(2),16); n=len(m.group(3))//2
        if 0x400<=o<0x5DD800: va=o+0x400C00
        elif 0x5DD800<=o<0x6B4000: va=o-0x5DD800+0x9DF000
        elif 0x6B4000<=o<0x757C00: va=o-0x6B4000+0xAB6000
        else: va=None
        ents.append((m.group(1),o,va,n))
# planned new patches (VA ranges)
plan=[('time',0x76CA1B,1),('time',0x5BFB0F,0x21),('time',0x5BFB4B,3),('time',0x5B82C0,1),('time',0x5B7A83,0x41),('time',0x5B8F33,1),('time',0x5B8F38,1),('time',0x5B8F9B,1),('time',0x5B8F9F,1),('time',0x5BFF46,1),('time',0x5BFF5B,1),('time',0x5C01FB,1),('time',0x5C04C1,1),('time',0x5C2683,1),('time',0x5C2893,1),
      ('wext',0x406D70,5),('wext',0x4E5D00,0x30),('wext',0x4DCCF0,6)]
allp=[(e[0],e[2],e[3]) for e in ents if e[2]]+plan
cnt=0
for a,n,f in w:
    if n is None: n=8
    for pid,va,pn in allp:
        if va<a+n and a<va+pn:
            print('DLL %s %08X+%d  <->  patch %s %08X+%d'%(f,a,n,pid,va,pn)); cnt+=1
print('overlaps:',cnt,'dll writes:',len(w))

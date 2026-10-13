import re,sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
pat=re.compile(sys.argv[1].encode(),re.I)
for m in re.finditer(rb'[\x20-\x7e]{3,}',d):
    s=m.group()
    if pat.search(s):
        o=m.start()
        va = o+0x400C00 if o<0x5DD800 else (o-0x5DD800+0x9DF000 if o<0x6B4000 else o-0x6B4000+0xAB6000)
        print(hex(va),s.decode())

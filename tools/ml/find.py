import re,struct
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
def f2va(o):
    if 0x400<=o<0x5DD800: return o+0x400C00
    if 0x5DD800<=o<0x6B4000: return o-0x5DD800+0x9DF000
    if 0x6B4000<=o: return o-0x6B4000+0xAB6000
for m in re.finditer(rb'(?i)maxlight|light[a-z]*\0',d):
    s=d[m.start():d.find(b'\0',m.start())]
    if b'ight' in s.lower():
        pass
for m in re.finditer(rb'(?i)[a-z_ ]*light[a-z_ ]*\0',d):
    o=m.start()
    print(hex(o),hex(f2va(o)),d[o:m.end()-1])

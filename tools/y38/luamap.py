from common import *
import json
res={}
# scan .rdata and .data for pairs (strptr,funcptr)
for base,end in ((0x5DD800,0x6B4000),(0x6B4000,0x6B4000+0x78E00)):
    for o in range(base,end-8,4):
        s,f=struct.unpack_from('<II',d,o)
        if 0x401000<=f<0x9DF000 and 0x9DF000<=s<0xAB6000+0x78E00:
            n=cstr(s,60)
            if n and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',n):
                res.setdefault(hex(f),[]).append((n,hex(fo2va(o))))
json.dump(res,open('luamap.json','w'))
print(len(res))

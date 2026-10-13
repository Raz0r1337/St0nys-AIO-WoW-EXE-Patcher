import sys,struct,re,bisect; sys.path.insert(0,'ml')
from h import *
T0=0x400; TN=0x400+0x5DD3B3
t=d[T0:TN]
# function starts: 55 8B EC preceded by CC/C3/C2xxxx/90
starts=[]
for m in re.finditer(rb'\x55\x8b\xec',t):
    i=m.start()
    if i>0 and t[i-1] in (0xCC,0xC3,0x90): starts.append(i+0x401000)
print('starts',len(starts))
# all rel targets
tg=set()
for i in range(len(t)-5):
    b=t[i]
    if b in (0xE8,0xE9):
        tg.add(i+0x401000+5+struct.unpack_from('<i',t,i+1)[0])
    elif b==0x0F and 0x80<=t[i+1]<=0x8F:
        tg.add(i+0x401000+6+struct.unpack_from('<i',t,i+2)[0])
# all abs dword values anywhere in file
absv=set()
for off in range(0,len(d)-3):
    v=struct.unpack_from('<I',d,off)[0]
    if 0x401000<=v<0x9DE400: absv.add(v)
dead=[]
for k,s in enumerate(starts):
    if s in tg or s in absv: continue
    e=starts[k+1] if k+1<len(starts) else 0x9DE3B3
    # also nothing references inside (s..e)
    dead.append((e-s,s,e))
dead.sort(reverse=True)
print('dead candidates',len(dead))
for sz,s,e in dead[:40]: print(hex(s),hex(e),sz)
import json; json.dump(dead,open('tm/dead.json','w'))

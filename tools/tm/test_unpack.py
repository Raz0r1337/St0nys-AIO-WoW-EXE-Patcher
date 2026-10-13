from emu import *
def pack(mi,hr,wd,md,mo,yr,fl=0):
    return (mi&63)|((hr&31)<<6)|((wd&7)<<11)|((md&63)<<14)|((mo&15)<<20)|((yr&31)<<24)|((fl&3)<<29)
res={}
for tag,data in (('orig',ORIG),('patched',PATCHED)):
    E=Emu(data); out=[]
    for yr in list(range(0,32)):
        for (mi,hr,wd,md,mo,fl) in ((0,0,0,0,0,0),(59,23,6,30,11,2),(63,31,7,63,15,3)):
            p=pack(mi,hr,wd,md,mo,yr,fl)
            st=0x30000000
            for i in range(8): E.w32(st+4*i,0xAAAAAAAA)
            E.call(0x76CAB0,(p,st))            # Unpack(packed, WoWTime*) cdecl
            out.append((yr,mi,tuple(E.s32(st+4*i) for i in range(8))))
    res[tag]=out
diff=[(a,b) for a,b in zip(res['orig'],res['patched']) if a!=b]
print('cases',len(res['orig']),'diffs',len(diff))
for a,b in diff[:6]: print(' orig',a,'\n patch',b)
# erwartung: nur Jahr 31 unterscheidet sich (orig -1, patched 31), alle anderen Felder identisch
ok=all(a[0]==31 and a[2][5]==-1 and b[2][5]==31 and a[2][:5]==b[2][:5] and a[2][6:]==b[2][6:] for a,b in diff) and len(diff)==3
print('UNPACK OK' if ok else 'UNPACK FAIL')

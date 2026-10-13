import ix, wx, re, sys
def fend(s):
    k=ix.idx(s)
    while k<len(ix.I)-1:
        k+=1
        a,_,t=ix.I[k]
        if t.startswith('push ebp') and ix.I[k-1][2].startswith(('int3','ret','nop')): return a
    return s+0x1000
for a in sys.argv[1:]:
    s=int(a,16); e=fend(s)
    out=set()
    for x in ix.I[ix.idx(s):ix.idx(e)]:
        for m in re.finditer(r'0x([0-9a-f]{6,7})', x[2]):
            v=int(m.group(1),16)
            if 0x9d0000<=v<0xad0000:
                try:
                    st=wx.cstr(v)
                    if len(st)>3 and all(32<=c<127 for c in st): out.add((hex(v),st[:70]))
                except Exception: pass
    print(a, hex(e), sorted(out))

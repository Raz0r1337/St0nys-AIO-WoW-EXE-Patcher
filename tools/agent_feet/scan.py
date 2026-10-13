import sys, struct, wx
D = wx.D
lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
t = [s for s in wx.SECS if s[0] == '.text'][0]
res = {}
for o in range(t[3], t[3] + t[4] - 4):
    v = struct.unpack_from('<I', D, o)[0]
    if lo <= v < hi:
        va = o - t[3] + t[1]
        res.setdefault(v, []).append(va)
for v in sorted(res): print(hex(v), ' '.join(hex(x) for x in res[v][:30]), '...' if len(res[v]) > 30 else '')

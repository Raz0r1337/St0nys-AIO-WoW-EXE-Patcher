import sys, struct, wx
D = wx.D
t = [s for s in wx.SECS if s[0] == '.text'][0]
def callers(tgt):
    hits = []
    for o in range(t[3], t[3] + t[4] - 5):
        if D[o] in (0xE8, 0xE9):
            rel = struct.unpack_from('<i', D, o + 1)[0]
            va = o - t[3] + t[1]
            if va + 5 + rel == tgt: hits.append((va, D[o]))
    return hits
if __name__ == '__main__':
    for a in sys.argv[1:]:
        print(a, ' '.join('%X%s' % (v, '' if b == 0xE8 else 'j') for v, b in callers(int(a, 16))))

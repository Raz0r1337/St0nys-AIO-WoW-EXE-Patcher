import wx, pickle, capstone
t = [s for s in wx.SECS if s[0] == '.text'][0]
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); md.skipdata = True
code = wx.D[t[3]:t[3] + t[2]]
out = []
for a, sz, m, o in md.disasm_lite(code, t[1]):
    out.append((a, sz, m + ' ' + o))
pickle.dump(out, open('insns.pkl', 'wb'), protocol=4)
print(len(out))

import wx, struct, ix
# scan .rdata for vtables: runs of >=20 pointers into .text
t=[s for s in wx.SECS if s[0]=='.text'][0]; rd=[s for s in wx.SECS if s[0]=='.rdata'][0]
lo,hi=t[1],t[1]+t[2]
D=wx.D; base=rd[3]; va0=rd[1]
vts=[]
i=0; n=rd[4]//4
while i<n:
    j=i
    while j<n and lo<=struct.unpack_from('<I',D,base+4*j)[0]<hi: j+=1
    if j-i>=20: vts.append((va0+4*i, j-i))
    i=j+1
import pickle; pickle.dump(vts,open('vtables.pkl','wb'))
print(len(vts))

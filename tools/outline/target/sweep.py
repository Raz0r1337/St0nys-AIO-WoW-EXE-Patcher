from w import *
import pickle
md2=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
md2.skipdata=True
out=[]
o=TEXT0
code=d[TEXT0:TEXT1]
for i in md2.disasm_lite(code, 0x401000):
    out.append(i)
pickle.dump(out,open('sweep.pkl','wb'))
print(len(out))

from common import *
import pickle
# linear sweep of .text, resync on failure
start=0x400; end=0x5DD800
ins=[]
o=start
code=d[start:end]
md.skipdata=True
for i in md.disasm_lite(code,start+0x400C00):
    ins.append(i)
pickle.dump(ins,open('ins.pkl','wb'))
print(len(ins))

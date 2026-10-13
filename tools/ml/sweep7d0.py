import h,json,capstone,struct
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.skipdata=True
d=h.d; lua={int(k,16):v for k,v in json.load(open('../tm/luafuncs.json')).items()}
starts=sorted(lua)
import bisect
def owner(va):
    i=bisect.bisect_right(starts,va)-1
    return (starts[i],lua[starts[i]]) if i>=0 and va-starts[i]<0x1000 else (None,'')
res=[]
for i in md.disasm(d[0x400:0x5DD800],0x401000):
    if i.id==0: continue
    if '0x7d0' in i.op_str and i.mnemonic in ('add','sub','cmp','lea','mov','push') and not ('[' in i.op_str and '+ 0x7d0]' in i.op_str):
        res.append((i.address,i.mnemonic+' '+i.op_str))
for a,t in res:
    f,n=owner(a); print(hex(a),t,'|',n)

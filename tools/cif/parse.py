import re,sys
W='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
d=open(W,'rb').read()
def entries():
    out=[]
    for ln in open(sys.path[0]+'/list.txt'):
        ln=ln.strip()
        if not ln: continue
        m=re.match(r'0[xX]([0-9A-Fa-f]+)\s+(.*?)\s*->\s*(.*)$',ln)
        off=int(m.group(1),16); old=bytes.fromhex(m.group(2)); new=bytes.fromhex(m.group(3))
        out.append((off,old,new))
    return out
if __name__=='__main__':
    E=entries(); bad=0
    for off,old,new in E:
        ok_len=len(old)==len(new); ok_old=d[off:off+len(old)]==old
        if not (ok_len and ok_old):
            bad+=1; print('PROBLEM 0x%X len %d/%d old_match=%s actual=%s'%(off,len(old),len(new),ok_old,d[off:off+len(old)].hex(' ')))
    # overlaps between entries
    E2=sorted(E)
    for (a,o1,n1),(b,o2,n2) in zip(E2,E2[1:]):
        if a+len(o1)>b: print('OVERLAP between 0x%X and 0x%X'%(a,b))
    print('entries:',len(E),'problems:',bad,'total bytes:',sum(len(o) for _,o,_ in E),'changed bytes:',sum(sum(1 for x,y in zip(o,n) if x!=y) for _,o,n in E))

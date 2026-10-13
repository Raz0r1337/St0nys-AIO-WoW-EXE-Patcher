import sys
p='apply_patches.ps1'
s=open(p,newline='').read().replace('\r\n','\n')
def R(old,new,cnt=1):
    global s
    c=s.count(old)
    if c!=cnt: sys.exit(f"count {c} for: {old[:80]!r}")
    s=s.replace(old,new)
exec(open(sys.argv[1]).read())
open(p,'w',newline='').write(s.replace('\n','\r\n'))

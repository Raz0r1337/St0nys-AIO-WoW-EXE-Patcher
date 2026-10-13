import re
from codes import *
P='/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1'
src=open(P,newline='').read()
lines=src.split('\r\n')
hdr=[i for i,l in enumerate(lines) if re.match(r"    @\{ Id = '",l)]
assert len(hdr)==85,len(hdr)
# notes to drop entirely / rewrite
drop_notes={9,10,11,23,24,45,46,47,48,49,50,63,64,74}
for n,i in enumerate(hdr,1):
    l=lines[i]
    l=re.sub(r"; BanRisk = \$true","",l)
    l=re.sub(r"; DllHint = '[^']*'","",l)
    add=[]
    if n in C2: add.append("BanRisk = $true")
    if n in C3: add.append("PublicUntested = $true")
    if n in C4: add.append("GameUntested = $true")
    if add:
        if l.endswith(';'): l=l+' '+'; '.join(add)
        else: l=l+'; '+'; '.join(add)
    lines[i]=l
    end=hdr[n] if n<85 else len(lines)
    for j in range(i+1,end):
        s=lines[j]
        if re.match(r"\s+(De|En) = '",s):
            s=s.replace(" - ungetestet'","'").replace(" - untested'","'")
        if n in drop_notes and re.match(r"\s+Note(De|En) = '",s):
            s=None
        elif n==79 and re.match(r"\s+NoteDe = ",s):
            s="       NoteDe = 'Schulterversatz noch ohne Wirkung'"
        elif n==79 and re.match(r"\s+NoteEn = ",s):
            s="       NoteEn = 'shoulder offset has no effect yet'"
        lines[j]=s
lines=[l for l in lines if l is not None]
open(P,'w',newline='').write('\r\n'.join(lines))

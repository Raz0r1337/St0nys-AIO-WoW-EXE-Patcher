import sys
ORIG='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
OUT='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/rev/out'
o=open(ORIG,'rb').read()
for n in range(19,37):
    p=open(f'{OUT}/{n}.exe','rb').read()
    print(f'== {n}: size orig {len(o)} patched {len(p)}')
    if len(p)!=len(o): print('  SIZE DIFFERS')
    m=min(len(o),len(p))
    i=0; ranges=[]
    while i<m:
        if o[i]!=p[i]:
            j=i
            while j<m and o[j]!=p[j]: j+=1
            ranges.append((i,j))
            i=j
        else: i+=1
    for a,b in ranges:
        print(f'  file 0x{a:X}-0x{b-1:X} len {b-a}: {o[a:b].hex()} -> {p[a:b].hex()}')
    # ini undo lines
    for line in open(f'{OUT}/{n}.ini',encoding='utf-8',errors='replace'):
        if line.startswith('undo=') or line.startswith('patches=') or line.startswith('ids='):
            print('  ini:',line.strip()[:200])

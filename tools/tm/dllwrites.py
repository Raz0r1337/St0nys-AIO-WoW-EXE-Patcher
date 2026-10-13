import re,os,glob,sys
root='wext/repo/WotLKExtensions/src'
writes=[]
for f in glob.glob(root+'/**/*.cpp',recursive=True)+glob.glob(root+'/**/*.hpp',recursive=True):
    s=open(f,encoding='utf-8',errors='replace').read()
    # strip // comments
    s2=re.sub(r'//[^\n]*','',s)
    arrays={}
    for m in re.finditer(r'uint8_t\s+(\w+)\s*\[\s*\]\s*=\s*\{([^}]*)\}',s2):
        arrays[m.group(1)]=len([x for x in m.group(2).split(',') if x.strip()])
    for m in re.finditer(r'Util::(OverwriteUInt32AtAddress|SetByteAtAddress|OverwriteBytesAtAddress)\s*\(([^;]*)\)\s*;',s2):
        fn,args=m.group(1),m.group(2)
        a=re.search(r'0x([0-9A-Fa-f]+)',args)
        if not a: 
            print('?? no addr',f,args[:80]); continue
        addr=int(a.group(1),16)
        if fn=='OverwriteUInt32AtAddress': n=4
        elif fn=='SetByteAtAddress': n=1
        else:
            parts=[p.strip() for p in args.split(',')]
            if len(parts)==3 and parts[1] in arrays: n=arrays[parts[1]]
            elif len(parts)==3 and re.match(r'^(0x[0-9A-Fa-f]+|\d+)$',parts[2]): n=int(parts[2],0)
            else:
                n=None; print('?? size',f,args[:100])
        writes.append((addr,n,os.path.relpath(f,root)))
writes.sort()
for a,n,f in writes: print('%08X %s %s'%(a,n,f))
import json; json.dump(writes,open('tm/dllwrites.json','w'))

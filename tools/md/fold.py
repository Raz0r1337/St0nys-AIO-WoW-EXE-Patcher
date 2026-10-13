import re, html
src=open('apply_patches.ps1').read()
ids=re.findall(r"(?m)^    @\{ Id = '([a-z0-9]+)'",src)
cfg={'README.md':dict(nr='Nr',head='| Nr. | Patch | Autor | Standard | St0ny |',ov='## Patch-Übersicht',desc='## Patch-Beschreibungen',
        tsum='Übersicht aller Patches mit Autor und Preset-Zuordnung anzeigen',
        tint='Ein Klick auf einen Patchnamen springt zu seiner Beschreibung.',
        dint='Jede Beschreibung ist eingeklappt – ein Klick auf den Patchnamen klappt sie auf.'),
     'README.en.md':dict(nr='No',head='| No. | Patch | Author | Default | St0ny |',ov='## Patch overview',desc='## Patch descriptions',
        tsum='Show all patches with author and preset assignment',
        tint='Click a patch name to jump to its description.',
        dint='Each description is collapsed – click the patch name to expand it.')}
for fn,c in cfg.items():
    s=open(fn,encoding='utf-8').read()
    s=s.replace('<a id="patch-21"></a>\n','')
    s=s.replace('(#patch-21)','(#patch-globalsv)')
    # --- descriptions
    lines=s.split('\n'); out=[]; i=0
    hdr=re.compile(r'^\*\*(.+?)\*\* \*\((%s\. (\d+).*)\)\*$'%c['nr'])
    stop=re.compile(r'^(### |## |---$)')
    n_desc=0
    while i<len(lines):
        m=hdr.match(lines[i])
        if not m: out.append(lines[i]); i+=1; continue
        n=int(m.group(3)); pid=ids[n-1]
        j=i+1
        while j<len(lines) and not hdr.match(lines[j]) and not stop.match(lines[j]): j+=1
        body=lines[i+1:j]
        while body and body[0]=='': body.pop(0)
        while body and body[-1]=='': body.pop()
        out+=['<a id="patch-%s"></a>'%pid,'<details>',
              '<summary><b>%s</b> <i>(%s)</i></summary>'%(html.escape(m.group(1),quote=False),html.escape(m.group(2),quote=False)),
              '']+body+['','</details>','']
        n_desc+=1; i=j
    s='\n'.join(out)
    # --- table rows: link names
    a=s.index(c['head']); b=s.index('\n\n',a); tbl=s[a:b]
    def link(m):
        n=int(m.group(1)); cell=m.group(2)
        k=cell.find(' *(')
        name,rest=(cell,'') if k<0 else (cell[:k],cell[k:])
        name=name.replace('[','\\[').replace(']','\\]')
        return '| %s | [%s](#patch-%s)%s |'%(m.group(1).ljust(2),name,ids[n-1],rest)
    tbl2,cnt=re.subn(r'(?m)^\| (\d+) +\| (.*?) \|(?= .* \| (?:✅|–) \| (?:✅|–) \|$)',link,tbl)
    s=s[:a]+c['tint']+'\n\n<details>\n<summary><b>'+c['tsum']+'</b></summary>\n\n'+tbl2+'\n\n</details>'+s[b:]
    # --- intro line for descriptions
    s=s.replace(c['desc']+'\n\n',c['desc']+'\n\n'+c['dint']+'\n\n',1)
    open(fn,'w',encoding='utf-8').write(s)
    print(fn,'descriptions',n_desc,'rows',cnt)

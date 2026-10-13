import re,sys
ids="laa cache itemcache worldcrash rce wardenoff scandll noserverpatch nosurvey skipbnet skiprdp nohttp afk glue mpqsig mpqnames localdata luaunlock awesome voicedll keyprop areatrigger swing npcanim spellanim ghostattack naked forcereaction mail deadchat follow level101 raceclass namecheck maxchars climb jump airforward airlateral airturn doublejump farclip horizon envdetail grounddist sliders goscale cat0 occluder bluemoon notransparency nofade hdportraits tracker worldmap castbars emblems flash charrandom window maximize windowfix mouse camera sound clientversion clientbuild clienttitle clientdate".split()
stony=set("laa itemcache rce scandll noserverpatch nosurvey skipbnet skiprdp nohttp glue mpqsig mpqnames localdata awesome areatrigger swing npcanim spellanim ghostattack naked forcereaction mail deadchat follow level101 maxchars farclip horizon envdetail grounddist goscale bluemoon notransparency tracker worldmap castbars flash window maximize windowfix mouse".split())
assert len(ids)==69 and len(stony)==41
def R(s,old,new,cnt=1):
    c=s.count(old)
    if c!=cnt: sys.exit(f"count {c} for: {old[:70]!r}")
    return s.replace(old,new)
def table(s,hdr,sep):
    lines=s.split('\n'); out=[]; inside=False; n=0
    for l in lines:
        if l==hdr: l=hdr+' St0ny |'; inside=True
        elif inside and l==sep: l=sep+':-----:|'
        elif inside and re.match(r'^\|\s*\| \*\*.*\*\* \|  \|  \|$',l): l=l+'  |'
        elif inside:
            m=re.match(r'^\| *(\d+) *\|.*\| (✅|–) \|$',l)
            if m:
                nr=int(m.group(1)); n+=1
                l=l+(' ✅ |' if ids[nr-1] in stony else ' – |')
            elif l.strip()=='' : inside=False
            else: sys.exit('unexpected table line: '+l)
        out.append(l)
    assert n==69, n
    return '\n'.join(out)

# ---------- DE ----------
p='README.md'; s=open(p,encoding='utf-8').read()
s=R(s,'''die [Patch-Übersicht](#patch-übersicht). Beim ersten Start ist das
**Preset „Billy's_Wow.exe“** vorausgewählt (Spalte „Standard“ in der Übersicht),
danach die gespeicherte Auswahl bzw. die Patches, die gerade in der `Wow.exe`
stecken.''','''die [Patch-Übersicht](#patch-übersicht). Beim ersten Start ist das
**Preset „Billy's_Wow.exe“** vorausgewählt (Spalte „Standard“ in der Übersicht),
danach die gespeicherte Auswahl bzw. die Patches, die gerade in der `Wow.exe`
stecken. Mit `S` lädst du das zweite Preset **„Billy's_Wow.exe (modded by
St0ny)“** (Spalte „St0ny“).''')
s=R(s,'''| `B`                | Preset „Billy's_Wow.exe“ laden (= Standard) |
''','''| `B`                | Preset „Billy's_Wow.exe“ laden (= Standard) |
| `S`                | Preset „Billy's_Wow.exe (modded by St0ny)“ laden |
''')
s=R(s,'''- **Zurücksetzen:** im Menü `B` drücken oder `patcher_selection.ini` löschen –
  dann gilt wieder das Preset „Billy's_Wow.exe“.

Das Preset „Billy's_Wow.exe“ ist das Patch-Set von Billy Hoyle und zugleich die
Standard-Auswahl. Es ist in `apply_patches.ps1` festgelegt: Jeder Patch hat dort
einen Eintrag `On = $true` (im Preset) bzw. `On = $false` (nicht im Preset).
''','''- **Zurücksetzen:** im Menü `B` drücken oder `patcher_selection.ini` löschen –
  dann gilt wieder das Preset „Billy's_Wow.exe“.

Das Preset „Billy's_Wow.exe“ ist das Patch-Set von Billy Hoyle und zugleich die
Standard-Auswahl. Es ist in `apply_patches.ps1` festgelegt: Jeder Patch hat dort
einen Eintrag `On = $true` (im Preset) bzw. `On = $false` (nicht im Preset).

Das zweite Preset „Billy's_Wow.exe (modded by St0ny)“ (Taste `S`) ist Billys
Patch-Set plus RCE-Fix, Sicherheits- und Login-Patches, MPQ-Signaturprüfung
aus, `/follow`-Fix, Level 101, Objektgröße, Tracker, Weltkarte und
Fenstermodus. Die Liste steht in `apply_patches.ps1` unter `$PRESET_STONY`,
in der Übersicht ist es die Spalte „St0ny“.
''')
s=R(s,'''`billy` (Preset „Billy's_Wow.exe“, auch `default`), `all`,''','''`billy` (Preset „Billy's_Wow.exe“, auch `default`), `stony` (Preset „Billy's_Wow.exe (modded by St0ny)“), `all`,''')
s=table(s,'| Nr. | Patch | Autor | Standard |','|----:|-------|-------|:--------:|')
open(p,'w',encoding='utf-8').write(s)

# ---------- EN ----------
p='README.en.md'; s=open(p,encoding='utf-8').read()
s=R(s,'''**preset "Billy's_Wow.exe"** is preselected (see the "Default" column in the
overview), after that the saved selection or the patches currently in
`Wow.exe`.''','''**preset "Billy's_Wow.exe"** is preselected (see the "Default" column in the
overview), after that the saved selection or the patches currently in
`Wow.exe`. `S` loads the second preset **"Billy's_Wow.exe (modded by St0ny)"**
(column "St0ny").''')
s=R(s,'''| `B`                | load preset "Billy's_Wow.exe" (= default)  |
''','''| `B`                | load preset "Billy's_Wow.exe" (= default)  |
| `S`                | load preset "Billy's_Wow.exe (modded by St0ny)" |
''')
s=R(s,'''The preset "Billy's_Wow.exe" is Billy Hoyle's patch set and also the default
selection. It is defined in `apply_patches.ps1`: every patch has an entry
`On = $true` (in the preset) or `On = $false` (not in the preset).
''','''The preset "Billy's_Wow.exe" is Billy Hoyle's patch set and also the default
selection. It is defined in `apply_patches.ps1`: every patch has an entry
`On = $true` (in the preset) or `On = $false` (not in the preset).

The second preset "Billy's_Wow.exe (modded by St0ny)" (key `S`) is Billy's
patch set plus the RCE fix, the security and login patches, MPQ signature
check off, the `/follow` fix, level 101, object scale, tracker, world map and
windowed mode. The list is in `apply_patches.ps1` under `$PRESET_STONY`; in
the overview it is the "St0ny" column.
''')
s=R(s,'''`billy` (preset "Billy's_Wow.exe", also `default`), `all`,''','''`billy` (preset "Billy's_Wow.exe", also `default`), `stony` (preset "Billy's_Wow.exe (modded by St0ny)"), `all`,''')
s=table(s,'| No. | Patch | Author | Default |','|----:|-------|-------|:--------:|')
open(p,'w',encoding='utf-8').write(s)
print('OK')

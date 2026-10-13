import re, json
SP='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/'
CATS=[('system','System & Leistung','System & performance',['laa','cache','itemcache']),
 ('security','Sicherheit & Datenschutz','Security & privacy',['rce','wardenoff','scandll','noserverpatch','nosurvey']),
 ('login','Login & Verbindung','Login & connection',['skipbnet','skiprdp','nohttp','afk']),
 ('modding','Modding: Interface, MPQs & Addons','Modding: interface, MPQs & addons',['glue','mpqsig','mpqnames','localdata','luaunlock','awesome']),
 ('gameplay','Gameplay-Fixes','Gameplay fixes',['areatrigger','swing','npcanim','spellanim','ghostattack','naked','forcereaction','mail','deadchat','level101','raceclass','maxchars']),
 ('graphics','Grafik & Sichtweite','Graphics & view distance',['farclip','horizon','envdetail','grounddist','sliders','goscale','cat0','occluder','bluemoon','notransparency','hdportraits']),
 ('ui','Interface & Komfort','Interface & comfort',['tracker','worldmap','castbars','emblems','flash']),
 ('window','Fenster & Maus','Window & mouse',['window','maximize','windowfix','mouse']),
 ('sound','Sound','Sound',['sound'])]
json.dump(CATS,open(SP+'cats.json','w'))
p='apply_patches.ps1'; s=open(p,newline='').read().replace('\r\n','\n')
def rep(o,n,cnt=1):
    global s
    assert s.count(o)==cnt,(o[:70],s.count(o)); s=s.replace(o,n)
start=s.index("$patches = @(\n")+len("$patches = @(\n"); end=s.index("\n)\n",start)
blocks={}; old=[]
for m in re.finditer(r"    @\{ Id = '(\w+)';.*?\n    \}\}\n",s[start:end],re.S):
    blocks[m.group(1)]=m.group(0); old.append(m.group(1))
json.dump(old,open(SP+'old_order.json','w'))
new=[i for c in CATS for i in c[3]]
assert sorted(new)==sorted(old) and len(new)==51
cat={i:c[0] for c in CATS for i in c[3]}
for i in new:
    blocks[i]=blocks[i].replace("    @{ Id = '%s'; "%i,"    @{ Id = '%s'; Cat = '%s'; "%(i,cat[i]),1)
# einzelne Korrekturen in Bloecken
b=blocks['scandll']
b=b.replace("""       Code = {
        Patch 0x5F4D56 @(0xC7, 0xC7)
        Patch 0x5F4D62 @(0xC7, 0xC7)""","""       Code = {
        # Macht aus ".\\Scan.dll" und ".\\Scan.dll.new" ".\\||an.dll" usw. - '|' ist
        # in Dateinamen verboten, das Laden schlaegt damit garantiert fehl.
        Patch 0x5F4D56 @(0x7C, 0x7C)
        Patch 0x5F4D62 @(0x7C, 0x7C)"""); assert b!=blocks['scandll']; blocks['scandll']=b
b=blocks['awesome']; nb=b.replace("; On = $false\n","; On = $false; Needs = @('laa')\n",1); assert nb!=b; blocks['awesome']=nb
b=blocks['emblems']; nb=b.replace("""        # Der Archivname ist frei waehlbar (patch-*.MPQ), dafuer sorgt der Patch
        # "Erweiterte MPQ-Namen erlauben" weiter oben.""","""        # Der Archivname ist frei waehlbar (patch-*.MPQ), dafuer sorgt der Patch
        # "Erweiterte MPQ-Namen erlauben" (mpqnames)."""); assert nb!=b; blocks['emblems']=nb
body=''
for c in CATS:
    body+='\n    # --- %s ---\n\n'%c[1].replace('ä','ae')
    body+='\n'.join(blocks[i] for i in c[3])
s=s[:start]+body+s[end:]
# Doku der Felder
rep("#    Id    - interner Kurzname (fuer Abhaengigkeiten)\n","#    Id    - interner Kurzname (fuer Abhaengigkeiten und patcher_selection.ini)\n#    Cat   - Kategorie (siehe $CATEGORIES), Ueberschrift im Menue\n")
rep("#  Die Reihenfolge hier ist die Reihenfolge im Menue und beim Einspielen.\n# ============================================================\n",
"""#  Die Reihenfolge hier ist die Reihenfolge im Menue und beim Einspielen,
#  Patches einer Kategorie stehen zusammen.
# ============================================================

$CATEGORIES = @{
    system   = @{ De = 'System & Leistung';                 En = 'System & performance' }
    security = @{ De = 'Sicherheit & Datenschutz';          En = 'Security & privacy' }
    login    = @{ De = 'Login & Verbindung';                En = 'Login & connection' }
    modding  = @{ De = 'Modding: Interface, MPQs & Addons'; En = 'Modding: interface, MPQs & addons' }
    gameplay = @{ De = 'Gameplay-Fixes';                    En = 'Gameplay fixes' }
    graphics = @{ De = 'Grafik & Sichtweite';               En = 'Graphics & view distance' }
    ui       = @{ De = 'Interface & Komfort';               En = 'Interface & comfort' }
    window   = @{ De = 'Fenster & Maus';                    En = 'Window & mouse' }
    sound    = @{ De = 'Sound';                             En = 'Sound' }
}
""")
# Menue: Kategorie-Ueberschriften
rep("""    for ($i = 0; $i -lt $total; $i++) {
        $nr = ([string]($i + 1)).PadLeft($width)
""","""    $lastCat = ''
    for ($i = 0; $i -lt $total; $i++) {
        if ($patches[$i].Cat -ne $lastCat) {
            $lastCat = $patches[$i].Cat
            $c = $CATEGORIES[$lastCat]
            if ($script:lang -eq 'en') { $title = $c.En } else { $title = $c.De }
            Write-Host "   -- $title --" -ForegroundColor Yellow
        }
        $nr = ([string]($i + 1)).PadLeft($width)
""")
# Eingaben robust gegen $null (Strg+Z / geschlossene Eingabe)
rep("""function Exit-Patcher([int]$code) {""","""# Read-Host liefert bei Strg+Z bzw. geschlossener Eingabe $null.
function Ask([string]$prompt) {
    $r = Read-Host $prompt
    if ($null -eq $r) { return '' }
    return ([string]$r).Trim()
}

function Exit-Patcher([int]$code) {""")
rep("""        $in = (Read-Host "  $(T 'Prompt')").Trim()""","""        $in = Ask "  $(T 'Prompt')\"""")
rep("""    $in = (Read-Host '  [1/2]').Trim().ToLowerInvariant()""","""    $in = (Ask '  [1/2]').ToLowerInvariant()""")
rep("""    $answer = (Read-Host "  $(T 'Confirm')").Trim().ToUpperInvariant()""","""    $answer = (Ask "  $(T 'Confirm')").ToUpperInvariant()""")
# -Unattended: keine Rueckfragen -> Sprache und Auswahl vorbelegen
rep("""$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Path) { $Path = Join-Path $scriptDir 'Wow.exe' }
""","""$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Path) {
    $Path = Join-Path $scriptDir 'Wow.exe'
} elseif (-not [System.IO.Path]::IsPathRooted($Path)) {
    # .NET loest relative Pfade gegen das Prozessverzeichnis auf, nicht gegen
    # das aktuelle PowerShell-Verzeichnis - daher selbst absolut machen.
    $Path = Join-Path (Get-Location).ProviderPath $Path
}

# -Unattended stellt keine Rueckfragen: ohne -Language Deutsch, ohne -Select
# die gespeicherte Auswahl (bzw. die Standard-Auswahl, wenn es keine gibt).
if ($Unattended) {
    if (-not $Language) { $Language = 'de' }
    if (-not $Select) { $Select = 'saved' }
}
""")
rep("""#    -Unattended              Keine Rueckfragen und keine Pausen
""","""#    -Unattended              Keine Rueckfragen und keine Pausen. Ohne
#                             -Language gilt Deutsch, ohne -Select die
#                             gespeicherte bzw. die Standard-Auswahl
""")
open(p,'w',newline='').write(s.replace('\n','\r\n'))
print('ok')

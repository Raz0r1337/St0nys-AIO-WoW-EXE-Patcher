import re,glyph,holdrep
from emitps import *
from asmgen import B1
NAMES={0x5622E0:'GetReducedKeyBinding',0x55E470:'GetCommandForBinding',0x86AE20:'OsGetAsyncTimeMs',0x47D3C0:'EventRegisterEx',
 0x563159:'ExecKey+9',0x5ABBC6:'UseAction+6',0x4F8EA6:'OnWorldRender+6',0x5A8E40:'GetCooldown',0xC1E5A0:'Seitenwechsel aktiv',
 0xC1E598:'aktuelle Seite',0xC1E59C:'Bonusleiste',0xD3F4E4:'laufender Zauber',0x6C5126:'CreateNewDesc+6',0x6C6B96:'ClearInstanceData+6',
 0x6C7480:'CheckGeometry',0x6C4AD6:'RenderBatch+6',0x6C9F58:'TextureCallback+8',0xC7D328:'Glyphen-Upload-Puffer',0x6C6B90:'ClearInstanceData',0x6C7B10:'CreateGeometry'}
def name(lines):
    out=[]
    for l in lines:
        if '#' in l:
            code,cm=l.split('# ',1)
            for a,n in NAMES.items():
                if re.search(r'0x%X\b'%a,cm): cm=cm+'  (%s)'%n; break
            l=code+'# '+cm
        out.append(l)
    return out
g=name(emit(glyph.tpl,0,glyph.SRC,glyph.absf,glyph.relf))
h=name(emit(holdrep.code,holdrep.CODE_OFF,holdrep.src(B1),holdrep.absf,holdrep.relf,comment_src=holdrep.src0(None)))
srcl=[l.strip() for l in glyph.CHECK.strip().split('\n') if l.strip()]
from asmgen import md
ins=list(md.disasm(glyph.chk,0x6C7480)); k=0; ck=[]
for t in srcl:
    if t.endswith(':'): ck.append('    # %s'%t); continue
    i=ins[k]; k+=1
    ck.append('    %-58s # %s'%('AddRaw $k @(%s)'%hx(bytes(i.bytes)),' '.join(t.split())))
ck=name(ck)
# insert block headers before labels
def hdr(lines,heads):
    out=[]
    for l in lines:
        m=re.match(r'    # (\w+):$',l)
        if m and m.group(1) in heads:
            out.append('    # --- %s ---'%heads[m.group(1)])
        out.append(l)
    return out
g=hdr(g,{'newdesc':'CreateNewDesc (VA 0x6C5120), ecx = Zeile: breiteste freie Luecke neu berechnen',
         'clear':'ClearInstanceData (VA 0x6C6B90), ecx = String: Seiten-Merker loeschen',
         'render':'RenderBatch (VA 0x6C4AD0), ecx = Batch: Geometrie vor dem Zeichnen neu aufbauen',
         'tex':'TextureCallback (VA 0x6C9F50, cdecl): Upload-Puffer vor dem Fuellen leeren'})
h=hdr(h,{'exec':'ExecKey (VA 0x563150, thiscall: mods, slot, isDown, argC, keyMode)',
         'find':'Hilfsfunktionen: Eintrag zu edx (Taste) / freien Eintrag suchen',
         'focus':'Fokus-Ereignis (cdecl): alle gehaltenen Tasten vergessen',
         'use':'UseAction (VA 0x5ABBC0, cdecl: slot, guid*, button)',
         'render':'OnWorldRender (VA 0x4F8EA0, thiscall): Original, danach Wiederholung pruefen',
         'update':'Wiederholung: jede gehaltene Taste pruefen'})
GL=glyph.LAB; HL=holdrep.LAB
G_SIZE=len(glyph.tpl); H_SIZE=len(holdrep.TPL)
f=[]
f.append('''# ============================================================
#  Schrift-Glyphen-Fix (Hour of Twilight, ported by St0ny)
#  Blizzard-Fehler im Glyphen-Cache: Texte (vor allem Zahlen, Schaden,
#  Chat) zeigen zeitweise falsche, abgeschnittene oder fremde Zeichen.
#  Der Cache legt die gerenderten Zeichen auf 256 Pixel breiten Zeilen
#  von Textur-Seiten ab und verdraengt alte, wenn er voll ist. Dabei
#  passieren mehrere Fehler, die WotLK-Extensions (Hour of Twilight)
#  per DLL behebt - hier dasselbe in einer eigenen Sektion (.glyph):
#  - CreateNewDesc (VA 0x6C5120): Der Merker "breiteste freie Luecke"
#    einer Zeile ([Zeile+0]) wird nie aktualisiert. Der Hook rechnet ihn
#    vor jedem Einfuegen aus der Zeichenliste der Zeile neu aus
#    (Knoten: Start +30h, Ende +34h, naechster [Knoten+Linkoffset+4]).
#  - ClearInstanceData (VA 0x6C6B90): Die Merker "benutzte Seiten" (+60h)
#    und "Seite verdraengt" (+64h) des Strings bleiben stehen - werden
#    jetzt mit geloescht. Die Original-Funktion liest beide nicht.
#  - CheckGeometry (VA 0x6C7480, an Ort und Stelle neu geschrieben): Ist
#    eine Seite des Strings verdraengt worden, wird er immer komplett
#    geloescht und neu aufgebaut (das Original prueft vorher noch die
#    Schrift und baut dann mit alten Daten weiter).
#  - RenderBatch (VA 0x6C4AD0): Vor dem Zeichnen werden alle Strings des
#    Batches neu aufgebaut; verdraengt das einen anderen String, folgen
#    bis zu drei weitere Durchgaenge nur fuer die verdraengten.
#  - TextureCallback (VA 0x6C9F50): Beim Hochladen einer Seite (Befehl 1)
#    wird der Upload-Puffer (VA 0xC7D328, 128 KB) erst geleert, sonst
#    landen Reste alter Zeichen auf der neuen Seite.
#  Code-Sprungadressen werden beim Patchen aus der Lage der Sektion
#  berechnet ($CAVE). Die Sektion ist nur ausfuehrbar, nicht beschreibbar.
# ============================================================
function Add-GlyphCacheFix {
    $NEWDESC = 0x6C5120; $CLEAR = 0x6C6B90; $CHECK = 0x6C7480; $RENDER = 0x6C4AD0; $TEXCB = 0x6C9F50
    Assert-Bytes ($NEWDESC - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C) 'Glyphen-Fix'
    Assert-Bytes ($CLEAR - 0x400C00) @(0x56, 0x57, 0x8B, 0xF1, 0x6A, 0x00) 'Glyphen-Fix'
    Assert-Bytes ($CHECK - 0x400C00) @(%s) 'Glyphen-Fix'
    Assert-Bytes ($RENDER - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x20) 'Glyphen-Fix'
    Assert-Bytes ($TEXCB - 0x400C00) @(0x55, 0x8B, 0xEC, 0x51, 0x83, 0x7D, 0x08, 0x01) 'Glyphen-Fix'
    $loc = Add-CodeSection '.glyph' 0x%X
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
''' % (hx(glyph.__dict__['h_orig_check']) if 'h_orig_check' in glyph.__dict__ else '%CHECKORIG%', G_SIZE))
f+= g
f.append('''    if ($c.Count -ne 0x%X) { throw 'Glyphen-Fix: Sektion hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    # Einspruenge: jmp in die Sektion, Rest der ueberschriebenen Befehle mit nop
    Patch ($NEWDESC - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $NEWDESC ($CAVE + 0x%X)) + [byte[]](0x90)))
    Patch ($CLEAR - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $CLEAR ($CAVE + 0x%X)) + [byte[]](0x90)))
    Patch ($RENDER - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $RENDER ($CAVE + 0x%X)) + [byte[]](0x90)))
    Patch ($TEXCB - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $TEXCB ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90)))
    # CheckGeometry neu (%d statt 69 Byte, Rest int3). Der Aufruf von
    # ClearInstanceData laeuft ueber den Hook oben und loescht +60h/+64h mit.
    $k = New-Object System.Collections.Generic.List[byte]
''' % (G_SIZE, GL['newdesc'], GL['clear'], GL['render'], GL['tex'], len(glyph.chk)))
f+= ck
f.append('''    while ($k.Count -lt 69) { $k.Add([byte]0xCC) }
    Patch ($CHECK - 0x400C00) $k.ToArray()
}

# ============================================================
#  Aktionstasten gedrueckt halten zum Wiederholen (Hour of Twilight, ported by St0ny)
#  Haelt man die Taste einer Aktionsleisten-Belegung (ACTIONBUTTON1-12,
#  die Hauptleiste mit Seiten- und Bonusleisten-Wechsel wie im Fork),
#  loest der Client die Aktion wiederholt aus - wie in WotLK-Extensions
#  (Hour of Twilight) mit actionButtonHoldRepeat = 2 (dauerhaft):
#  - ExecKey (VA 0x563150): Beim Druecken merkt sich der Hook Taste,
#    Aktions-Slot und Zeit (bis 8 Tasten gleichzeitig). Beim Loslassen
#    wird der Eintrag geloescht; hat er schon wiederholt, unterdrueckt er
#    das normale Ausloesen beim Loslassen (UseAction-Hook).
#  - OnWorldRender (VA 0x4F8EA0): Nach jedem Bild prueft der Hook jede
#    gehaltene Taste: fruehestens 500 ms nach dem Druecken, nicht waehrend
#    eines Zaubers, nicht waehrend der Abklingzeit (GetCooldown, auch
#    globale), erst 100 ms nachdem die Aktion wieder bereit ist und
#    hoechstens alle 100 ms ruft er UseAction auf.
#  - Fokus-Ereignis (EventRegisterEx, Ereignis 2, beim ersten Druck
#    angemeldet): Verliert das Fenster den Fokus, werden alle gehaltenen
#    Tasten vergessen (sonst wiederholt es ohne Loslassen ewig).
#  Die Zustaende stehen in derselben Sektion (.hrep), die darum
#    beschreibbar sein muss: +0 acht Eintraege zu 32 Byte (Taste, Slot,
#  Druckzeit, letzte Wiederholung, bereit seit, wiederholt, aktiv),
#  +100h Unterdrueck-Merker, +104h Ereignis angemeldet, +108h GUID (0),
#  +110h leerer Text, +114h "ACTIONBUTTON". Code ab +120h.
# ============================================================
function Add-HoldRepeat {
    $EXEC = 0x563150; $USE = 0x5ABBC0; $RENDER = 0x4F8EA0
    Assert-Bytes ($EXEC - 0x400C00) @(0x55, 0x8B, 0xEC, 0x81, 0xEC, 0xC4, 0x00, 0x00, 0x00) 'Gedrueckt halten'
    Assert-Bytes ($USE - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C) 'Gedrueckt halten'
    Assert-Bytes ($RENDER - 0x400C00) @(0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x34) 'Gedrueckt halten'
    $loc = Add-CodeSection '.hrep' 0x%X -Writable
    $CAVE = $loc[0]
    $c = New-Object System.Collections.Generic.List[byte]
    for ($i = 0; $i -lt 0x114; $i++) { $c.Add([byte]0) }                 # Zustaende, beginnen bei 0
    AddRaw $c ([System.Text.Encoding]::ASCII.GetBytes('ACTIONBUTTON'))  # +114h, ohne Null
''' % H_SIZE)
f+= h
f.append('''    if ($c.Count -ne 0x%X) { throw 'Gedrueckt halten: Sektion hat die falsche Groesse.' }
    Patch $loc[1] $c.ToArray()
    Patch ($EXEC - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $EXEC ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90, 0x90)))
    Patch ($USE - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $USE ($CAVE + 0x%X)) + [byte[]](0x90)))
    Patch ($RENDER - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $RENDER ($CAVE + 0x%X)) + [byte[]](0x90)))
}
''' % (H_SIZE, HL['exec'], HL['use'], HL['render']))
txt='\n'.join(f)
import sys; sys.path.insert(0,'../ml'); import h as H
orig=H.d[H.v2f(0x6C7480):H.v2f(0x6C7480)+69]
txt=txt.replace('%CHECKORIG%',hx(orig))
open('funcs.ps1','w').write(txt)
print(len(txt.split('\n')))

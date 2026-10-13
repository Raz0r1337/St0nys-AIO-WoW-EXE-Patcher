import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from patches2 import P
PS='/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1'
s=open(PS,encoding='ascii',newline='').read().replace('\r\n','\n')
def once(old,new):
    global s
    assert s.count(old)==1,(old[:80],s.count(old)); s=s.replace(old,new)
def pl(off,bs,cm=''):
    it=['0x%02X'%b for b in bs]
    c=('   # '+cm) if cm else ''
    if len(it)<=16: return '        Patch 0x%X @(%s)%s\n'%(off,', '.join(it),c)
    lines=[', '.join(it[i:i+16]) for i in range(0,len(it),16)]
    return '        Patch 0x%X @(\n            %s\n        )\n'%(off,',\n            '.join(lines))
VA=lambda o:o+0x400C00
sysblk = """
    @{ Id = 'nothrottle'; Cat = 'system'; On = $false
       Author = 'Hour of Twilight (ported by St0ny)'
       De = 'Server-Abfragen nicht drosseln (Item- und Quest-Infos schneller) - ungetestet'
       En = 'Do not throttle server queries (item and quest info loads faster) - untested'
       Code = {
        # Die 15 Datenbank-Caches (Items, Kreaturen, Quests, Namen ...) begrenzen
        # die Anfragen an den Server pro 30-Sekunden-Fenster ([Cache+48h], aus
        # "Anfragen pro Minute" im Konstruktor berechnet). 0 heisst unbegrenzt
        # (Pruefung "test eax,eax / je"). Im Konstruktor wird statt des
        # berechneten Werts (edx) ecx gespeichert, das dort 0 ist:
        # mov [esi+48h],edx -> mov [esi+48h],ecx. Je ein Byte in allen 15.
""" + ''.join(pl(o,b,'VA 0x%X'%VA(o)) for o,b in P['nothrottle']) + """    }}

    @{ Id = 'mirrorfix'; Cat = 'system'; On = $false
       Author = 'Hour of Twilight (ported by St0ny)'
       De = 'Mirror-Image-Absturzfix (Speicherleck bei Spiegelbildern) - ungetestet'
       En = 'Mirror Image crash fix (memory leak with mirror images) - untested'
       Code = {
        # Blizzard-Fehler: Der Handler fuer SMSG_MIRRORIMAGE_DATA (VA 0x730290)
        # legt fuer das Aussehen einer Spiegelbild-Einheit eine neue
        # Charakter-Komponente an ([Einheit+B4Ch]), ohne eine noch vorhandene
        # alte freizugeben. Die alte bleibt mit ihrer Textur am Grafikgeraet
        # haengen; beim Beenden greift der Client dann auf schon freigegebenen
        # Speicher zu (Absturz). Haeufig bei Server-Kopien von Spielern (Eluna
        # "Mirror Image"-Kreaturen), die ihr Modell oft neu laden.
        # Beide Aufrufe des Allokators (VA 0x4F0980) im Handler gehen jetzt an
        # einen Stub, der eine alte Komponente erst mit der Original-Freigabe
        # (VA 0x4F16C0) loest und dann zum Allokator springt. Der Stub (29 Byte)
        # liegt in einer toten Funktion bei VA 0x86BF10 (nirgends aufgerufen
        # oder referenziert). Die Dateigroesse aendert sich nicht.
""" + ''.join(pl(o,b) for o,b in P['mirrorfix']) + """    }}

    @{ Id = 'wmocube'; Cat = 'system'; On = $false
       Author = 'Alyst3r (ported by St0ny)'
       De = 'Fehlende WMO-Datei: Fehlerwuerfel statt ERROR #134 - ungetestet'
       En = 'Missing WMO file: error cube instead of ERROR #134 - untested'
       Code = {
        # CMap::SafeOpen (VA 0x7BD480) oeffnet WMO-Dateien (Gebaeude, Dungeons).
        # Klappt das zehnmal nicht, bricht der Client mit "ERROR #134 Fatal
        # Condition: CMap::SafeOpen() failed" ab. Statt der Fehlermeldung oeffnet
        # der Fehlerausgang jetzt "Spells\\ErrorCube.mdx" (der Text steht schon in
        # der Exe) und gibt dessen Ergebnis zurueck - wie in WotLK-Extensions:
        # push ebx / push "Spells\\ErrorCube.mdx" / call SFile::Open / Epilog.
""" + ''.join(pl(o,b) for o,b in P['wmocube']) + """    }}
"""
anchor_sys="""        Patch 0x1C1C93 @(0x20)
    }}
"""
once(anchor_sys, anchor_sys+sysblk)
gp = """
    @{ Id = 'noammo'; Cat = 'gameplay'; On = $false
       Author = 'Alyst3r (ported by St0ny)'
       De = 'Fernkampf ohne Munition - ungetestet'
       En = 'Ranged attacks without ammo - untested'
       NoteDe = 'Server muss mitspielen, sonst meldet er weiter "Keine Munition"'
       NoteEn = 'the server has to support it, otherwise it still reports "no ammo"'
       Code = {
        # Spell_C_HaveEquippedSpellItems (VA 0x8093D0): Bei Zaubern, die
        # Munition verlangen (Schiessen, Automatischer Schuss ...), prueft der
        # Client ab VA 0x809540 die Munition. Ein Sprung zum Erfolgsausgang
        # (VA 0x8095FF) laesst diese Pruefung weg. Der Server prueft selbst -
        # ohne Anpassung am Server bleibt es bei seiner Fehlermeldung.
""" + ''.join(pl(o,b) for o,b in P['noammo']) + """    }}
"""
i=s.index("    @{ Id = 'doublejump';"); j=s.index("\n    }}\n",i)+len("\n    }}\n")
s=s[:j]+gp+s[j:]
ui = """
    @{ Id = 'lootopen'; Cat = 'ui'; On = $false
       Author = 'Hour of Twilight (ported by St0ny)'
       De = 'Lootfenster bleibt beim Laufen offen - ungetestet'
       En = 'Loot window stays open while moving - untested'
       Code = {
        # Zehn Bewegungs-Handler (Laufen, Seitwaerts, Drehen, Neigen ...) der
        # eigenen Figur schliessen das Lootfenster (Aufruf VA 0x523640). Das
        # "je" vor dem Aufruf wird zu "jmp", der Aufruf entfaellt.
""" + ''.join(pl(o,b,'VA 0x%X'%VA(o)) for o,b in P['lootopen']) + """    }}

    @{ Id = 'showlevel'; Cat = 'ui'; On = $false
       Author = 'Hour of Twilight (ported by St0ny)'
       De = 'Echtes Level statt "??" bei Gegnern ab 10 Level ueber dir - ungetestet'
       En = 'Real level instead of "??" for enemies 10+ levels above you - untested'
       NoteDe = 'Bosse zeigen weiter "??"'
       NoteEn = 'bosses still show "??"'
       Code = {
        # Lua UnitLevel (VA 0x60F9E0), Tooltip (VA 0x620EE0) und Namensplakette
        # (VA 0x98EF10) zeigen "??" (bzw. -1 / Totenkopf), wenn ein feindliches
        # Ziel 10 oder mehr Level ueber dir ist. Diese Pruefung ("jle") faellt
        # weg; die Boss-Pruefung direkt dahinter bleibt.
""" + ''.join(pl(o,b) for o,b in P['showlevel']) + """    }}
"""
i=s.index("    @{ Id = 'charrandom';"); j=s.index("\n    }}\n",i)+len("\n    }}\n")
s=s[:j]+ui+s[j:]
# Nr. 6 und Nr. 26 ebenfalls als ungetestet markieren
once("De = 'Jahr-2031-Fix (Datum und Kalender bis Ende 2031)'","De = 'Jahr-2031-Fix (Datum und Kalender bis Ende 2031) - ungetestet'")
once("En = 'Year 2031 fix (date and calendar until the end of 2031)'","En = 'Year 2031 fix (date and calendar until the end of 2031) - untested'")
once("De = 'WotLKExtensions.dll Unterstuetzung aktivieren'","De = 'WotLKExtensions.dll Unterstuetzung aktivieren - ungetestet'")
once("En = 'Enable WotLKExtensions.dll support'","En = 'Enable WotLKExtensions.dll support - untested'")
s=s.replace('\n','\r\n')
assert all(ord(c)<128 for c in s)
open(PS,'w',encoding='ascii',newline='').write(s)
print('ok')

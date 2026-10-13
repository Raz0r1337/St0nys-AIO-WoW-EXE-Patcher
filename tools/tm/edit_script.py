import sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__))))
from patches import YEAR2031, WOTLKEXT
P='/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1'
s=open(P,encoding='ascii',newline='').read()
assert '\r\n' in s
s=s.replace('\r\n','\n')
def once(old,new):
    global s
    assert s.count(old)==1,(old[:70],s.count(old)); s=s.replace(old,new)
def bl(bs, per=16, ind='            '):
    items=['0x%02X'%b for b in bs]
    if len(items)<=per: return ', '.join(items)
    lines=[', '.join(items[i:i+per]) for i in range(0,len(items),per)]
    return (',\n'+ind).join(lines)
def pl(off, bs, comment=''):
    body=bl(bs)
    c=('   # '+comment) if comment else ''
    return '        Patch 0x%X @(%s)%s\n'%(off,body,c)
Y=dict(YEAR2031) if False else None
yl=YEAR2031
# Reihenfolge in YEAR2031: unpack, holiday, holiday-jmp, maxdate, maxcreate, 6 Klemmen, 4 Schleifen
assert len(yl)==15
year = """
    @{ Id = 'year2031'; Cat = 'system'; On = $false
       Author = 'St0ny (original by Alyst3r)'
       De = 'Jahr-2031-Fix (Datum und Kalender bis Ende 2031)'
       En = 'Year 2031 fix (date and calendar until the end of 2031)'
       Url = 'https://github.com/Alyst3r/WotLK-Extensions'
       Code = {
        # WoW packt Datumswerte in 32 Bit, das Jahr in 5 Bit (2000 + 0..31).
        # Der Wert 31 heisst im Original "nicht gesetzt". Ab dem 1.1.2031
        # schickt der Server aber genau 31: Der Client haelt das Datum fuer
        # ungesetzt, Kalender und Datumsanzeigen laufen falsch (laut
        # WotLK-Extensions bis hin zu Abstuerzen). Idee aus WotLK-Extensions
        # (Alyst3r, dort Teil der DLL) - hier direkt in der Exe, ohne neuen
        # Platz und mit zwei Korrekturen (siehe 2 und 3).
        # 1) Entpacker (VA 0x76C970): Jahr 31 bleibt 2031 (jne -> jmp).
""" + pl(yl[0][0],yl[0][1]) + """        # 2) Feiertage: In Holidays.dbc (und den Feiertagsdaten vom Server)
        #    heisst Jahr 31 weiter "jedes Jahr", ein Wochentag ohne Datum
        #    "jede Woche". Die Feiertags-Auswertung (VA 0x5BFAB0) setzt Jahr 31
        #    nach dem Entpacken deshalb wieder auf "nicht gesetzt". Platz dafuer
        #    schafft ein kuerzerer Schleifen-Prolog (imul statt shl/sub/add),
        #    "add esp,8" nach dem Entpacken springt in den Stub (pop ecx x2,
        #    cmp [ebx+14h],1Fh / jne / or [ebx+14h],-1). In WotLK-Extensions
        #    fehlt das - dort fallen jaehrliche und woechentliche Feiertage aus
        #    dem Kalender.
""" + pl(yl[1][0],yl[1][1]) + pl(yl[2][0],yl[2][1]) + """        # 3) Kalendergrenzen von Ende 2030 auf Ende 2031 (2032 passt nicht mehr
        #    in die 5 Bit des Protokolls). CalendarGetMaxDate (VA 0x5B82BD):
        #    1.1.2032 minus 1 Tag. Spaetestes Datum fuer neue Termine (VA
        #    0x5B7A80): "Monatsende in 12 Monaten", aber hoechstens 31.12.2031 -
        #    das Original klemmt nur das Jahr und liesse 2031 nur noch den
        #    laufenden Monat zu, WotLK-Extensions laesst Termine bis 2032 zu.
""" + pl(yl[3][0],yl[3][1]) + pl(yl[4][0],yl[4][1]) + """        #    Jahres-Klemmen beim Blaettern (VA 0x5B8EC0, 0x5B8F70, 0x5BFF30):
        #    hoechstens 2031 statt 2030.
""" + ''.join(pl(o,b) for o,b in yl[5:11]) + """        #    Schleifen ueber Monate und Feiertage (VA 0x5C01F9, 0x5C04BF,
        #    0x5C2680, 0x5C2890): laufen bis Ende 2031 statt Ende 2030.
        #    (0x5C2680 ist die Schleife der woechentlichen Feiertage - auch die
        #    fehlt in WotLK-Extensions.)
""" + ''.join(pl(o,b) for o,b in yl[11:15]) + """    }}
"""
anchor="""        Patch 0x46A08E @(0xE9, 0x83, 0x00, 0x00, 0x00, 0x90)
    }}
"""
once(anchor, anchor+year)
wl=WOTLKEXT
wext = """
    @{ Id = 'wotlkext'; Cat = 'dll'; On = $false; Needs = @('laa'); DllHint = 'WotLK-Extensions'
       Author = 'St0ny (original by Alyst3r)'
       De = 'WotLKExtensions.dll Unterstuetzung aktivieren'
       En = 'Enable WotLKExtensions.dll support'
       NoteDe = 'benoetigt WotLK-Extensions'
       NoteEn = 'requires WotLK-Extensions'
       Url = 'https://github.com/Alyst3r/WotLK-Extensions'
       Code = {
        # Laedt beim Start die WotLKExtensions.dll aus dem WoW-Ordner. Der
        # Original-Patcher von WotLK-Extensions haengt seinen Lader wie der
        # awesome-Lader an den Start der Haupt-Fiber (VA 0x40B7D0) - beide
        # zusammen gingen nicht. Dieser Lader sitzt stattdessen am Anfang der
        # Funktion, die die Haupt-Fiber dort aufruft (VA 0x406D70, einziger
        # Aufrufer): jmp -> Lader bei VA 0x4E5D00 im toten Teil der
        # Scan.dll-Startfunktion (hinter dem awesome-Lader) -> Scan.dll-Flag
        # "Pruefung bestanden" setzen (sonst blockiert DefaultServerLogin),
        # LoadLibraryA("WotLKExtensions.dll"), ersten Befehl (push 5EEB70h)
        # nachholen, zurueck. Lua ScanDLLStart (VA 0x4DCCF0) wird wie beim
        # awesome-Lader zu "return 0" (gleiche Bytes). Mit dem awesome-Lader
        # zusammen werden beide DLLs geladen. Fehlt die DLL, startet WoW normal.
""" + pl(wl[0][0],wl[0][1]) + pl(wl[1][0],wl[1][1]) + pl(wl[2][0],wl[2][1]) + """    }}
"""
anchor2="""        Add-VoiceLoader 'voice.dll'
    }}
"""
once(anchor2, anchor2+wext)
# DllHint mit DLL-Namen
once("""        DllHint       = 'HINWEIS: Der Patch selbst ist unkritisch. Erst die geladene DLL kann auf Servern mit Anti-Cheat auffallen - nur dort einsetzen, wo awesome_wotlk erlaubt ist.'""",
     """        DllHint       = 'HINWEIS: Der Patch selbst ist unkritisch. Erst die geladene DLL kann auf Servern mit Anti-Cheat auffallen - nur dort einsetzen, wo {0} erlaubt ist.'""")
once("""        DllHint       = 'NOTE: The patch itself is harmless. Only the loaded DLL may be noticed by servers with anti-cheat - use it only where awesome_wotlk is allowed.'""",
     """        DllHint       = 'NOTE: The patch itself is harmless. Only the loaded DLL may be noticed by servers with anti-cheat - use it only where {0} is allowed.'""")
once("""        Say (T 'DllHint') 'Yellow'""","""        Say (T 'DllHint' $p.DllHint) 'Yellow'""")
once("""    @{ Id = 'awesome'; Cat = 'dll'; On = $true; Needs = @('laa'); DllHint = $true""","""    @{ Id = 'awesome'; Cat = 'dll'; On = $true; Needs = @('laa'); DllHint = 'awesome_wotlk'""")
once("""#    DllHint - optional: $true fuer den DLL-Loader - dezenter gelber Hinweis,
#            dass erst die geladene DLL auffallen kann""","""#    DllHint - optional: Name des DLL-Projekts fuer den DLL-Loader - dezenter
#            gelber Hinweis, dass erst die geladene DLL auffallen kann""")
# statische Nummern (window 64->66, maximize 65->67)
once("maximiert nur zusammen mit Nr. 65'","maximiert nur zusammen mit Nr. 67'")
once("maximized only together with No. 65'","maximized only together with No. 67'")
once("NoteDe = 'wirkt nur zusammen mit Nr. 64'","NoteDe = 'wirkt nur zusammen mit Nr. 66'")
once("NoteEn = 'only works together with No. 64'","NoteEn = 'only works together with No. 66'")
s=s.replace('\n','\r\n')
assert all(ord(c)<128 for c in s)
open(P,'w',encoding='ascii',newline='').write(s)
print('ok')

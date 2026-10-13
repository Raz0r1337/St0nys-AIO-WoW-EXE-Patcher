import re,sys
d=sys.argv[1]
sh=lambda n: str(int(n)+1 if 29<=int(n)<=86 else int(n))
def once(s,a,b):
    assert s.count(a)==1,(a[:90],s.count(a)); return s.replace(a,b)
def table(s,md): return re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(sh(m.group(1)),md), s)
def refs(s):
    def f(m):
        out='%s %s'%(m.group(1),sh(m.group(2)))
        if m.group(3): out+=m.group(3)+sh(m.group(4))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?![\d.])(?:( (?:und|and) )(\d+)(?!\d))?',f,s)
def rowrefs(s): return re.sub(r'(?m)^\| \[\d+\]\(.*$',lambda m: refs(m.group(0)),s)
URL='https://github.com/Stormhand-dev/Lexara---HD-Font-Renderer-for-WoW-3.3.5'
ROW={'de':'| [29](PATCHES.de.md#patch-lexara) | Lexara.dll beim Start laden (HD-Schriften von Stormhand) *(benötigt [Lexara](%s) – `dinput8.dll` in `Lexara.dll` umbenennen)* | 🟠 **[ungetestet]** | St0ny | ✅ | – | – |\n'%URL,
     'en':'| [29](PATCHES.en.md#patch-lexara) | Load Lexara.dll at startup (HD fonts by Stormhand) *(requires [Lexara](%s) – rename `dinput8.dll` to `Lexara.dll`)* | 🟠 **[untested]** | St0ny | ✅ | – | – |\n'%URL}
SEC={'de':"""<a id="patch-lexara"></a>
**Lexara.dll beim Start laden (HD-Schriften von Stormhand)** *(Nr. 29, Autor: St0ny)* 🟠 **[ungetestet]**

> [!WARNING]
> **Online ungetestet** – nicht auf öffentlichen Servern getestet, mögliche Bann-Gefahr. Vorsicht, kann zu Kick/Bann führen.
>
> **Ingame ungetestet** – die Funktion ist im Spiel noch nicht geprüft, möglicherweise verbuggt.

Lädt beim Start die `Lexara.dll` aus dem WoW-Ordner –
[Lexara](%s) von Stormhand ersetzt die Schriftdarstellung
des Clients durch scharfe HD-Schriften (MSDF). Bisher lief Lexara als
`dinput8.dll` neben der Exe und kam sich dabei mit anderen Mods in die Quere,
die denselben Dateinamen benutzen. Mit diesem Patch lädt die Exe Lexara selbst.
Fehlt die DLL, startet WoW ganz normal.

So wird es eingerichtet: Die `dinput8.dll` aus dem Lexara-Download in
`Lexara.dll` umbenennen und zusammen mit `skia.dll` in den WoW-Ordner legen.
Keine zusätzliche `dinput8.dll` von Lexara liegen lassen, sonst wird Lexara
doppelt geladen.

Dateigröße und PE-Header bleiben unverändert: Der Einstiegspunkt (VA
`0x401000`) ruft zuerst `__security_init_cookie` auf. Dieser Aufruf zeigt jetzt
auf eine freie 16-Byte-Lücke (VA `0x6DC8C0`) mit `push "Lexara.dll"` →
`call [LoadLibraryA]` → Sprung zu `__security_init_cookie`. Der Name steht in
einer zweiten Lücke (VA `0x6DC0E0`). Eine Proxy-DLL wird ebenfalls vor dem
Einstiegspunkt geladen, der Zeitpunkt passt also. Der Patch verträgt sich mit
dem voice.dll-Lader (Nr. 30), der nur den Sprung direkt danach ändert.

"""%URL,'en':"""<a id="patch-lexara"></a>
**Load Lexara.dll at startup (HD fonts by Stormhand)** *(No. 29, Author: St0ny)* 🟠 **[untested]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

Loads `Lexara.dll` from the WoW folder at startup –
[Lexara](%s) by Stormhand replaces the client's font
rendering with sharp HD fonts (MSDF). So far Lexara ran as `dinput8.dll` next
to the exe and got in the way of other mods that use the same file name. With
this patch the exe loads Lexara itself. If the DLL is missing, WoW starts
normally.

Setup: rename `dinput8.dll` from the Lexara download to `Lexara.dll` and put it
into the WoW folder together with `skia.dll`. Do not leave an additional Lexara
`dinput8.dll` there, otherwise Lexara is loaded twice.

File size and PE header stay unchanged: the entry point (VA `0x401000`) first
calls `__security_init_cookie`. This call now points to a free 16-byte gap
(VA `0x6DC8C0`) with `push "Lexara.dll"` → `call [LoadLibraryA]` → jump to
`__security_init_cookie`. The name sits in a second gap (VA `0x6DC0E0`). A
proxy DLL is loaded before the entry point as well, so the timing matches. The
patch works together with the voice.dll loader (No. 30), which only changes
the jump right after it.

"""%URL}
LEG={'de':[("Nr. 4, 10,\n    11, 23–25, 41, 42, 45–50, 74 und 82–86 (rote Warnung).","Nr. 4, 10,\n    11, 23–25, 42, 43, 46–51, 75 und 83–87 (rote Warnung)."),
           ("Nr. 26, 29, 39, 44, 51, 62, 68, 71–73 und 80 (rote\n    Warnung).","Nr. 26, 29, 30, 40, 45, 52, 63, 69, 72–74 und 81 (rote\n    Warnung)."),
           ("Nr. 25, 26, 29, 44, 51 und 62 (rote Warnung).","Nr. 25, 26, 29, 30, 45, 52 und 63 (rote Warnung)."),
           ("Nr. 9, 50, 63, 64, 74 und 80. Das ist","Nr. 9, 51, 64, 65, 75 und 81. Das ist"),
           ("(Nr. 9, 50, 63, 64, 74 und 80), entfernen","(Nr. 9, 51, 64, 65, 75 und 81), entfernen"),
           ("Es enthält nur\nsichere Patches (🟢), die Stormhand alle mehrere Stunden auf Warmane getestet\nhat – **das Preset ist sicher** und kann auch auf öffentlichen Servern\nverwendet werden. Drei davon (Nr. 9, 63 und 64) vergrößern die `Wow.exe`; auf\nWarmane war das kein Problem, andere Server können die Dateigröße aber prüfen. Welche Patches",
            "Es enthält\nsichere Patches (🟢), die Stormhand alle mehrere Stunden auf Warmane getestet\nhat – **das Preset ist sicher** und kann auch auf öffentlichen Servern\nverwendet werden. Drei davon (Nr. 9, 64 und 65) vergrößern die `Wow.exe`; auf\nWarmane war das kein Problem, andere Server können die Dateigröße aber prüfen.\nDazu kommt der Lexara-Lader (Nr. 29) für Stormhands HD-Schriften. Er ist noch\nungetestet; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts. Welche Patches")],
     'en':[("No. 4, 10, 11, 23–25,\n    41, 42, 45–50, 74 and 82–86 (red warning).","No. 4, 10, 11, 23–25,\n    42, 43, 46–51, 75 and 83–87 (red warning)."),
           ("No. 26, 29, 39, 44, 51, 62, 68, 71–73 and 80 (red\n    warning).","No. 26, 29, 30, 40, 45, 52, 63, 69, 72–74 and 81 (red\n    warning)."),
           ("No. 25, 26, 29, 44, 51 and 62 (red warning).","No. 25, 26, 29, 30, 45, 52 and 63 (red warning)."),
           ("No. 9, 50,\n    63, 64, 74 and 80. This does not","No. 9, 51,\n    64, 65, 75 and 81. This does not"),
           ("(No. 9, 50, 63, 64, 74 and 80) also remove","(No. 9, 51, 64, 65, 75 and 81) also remove"),
           ("It contains only patches\nrated safe (🟢), all tested by Stormhand for several hours on Warmane – **the\npreset is safe** and can be used on public servers as well. Three of them\n(No. 9, 63 and 64) make `Wow.exe` larger; that was no problem on Warmane, but\nother servers may check the file size. The",
            "It contains patches\nrated safe (🟢), all tested by Stormhand for several hours on Warmane – **the\npreset is safe** and can be used on public servers as well. Three of them\n(No. 9, 64 and 65) make `Wow.exe` larger; that was no problem on Warmane, but\nother servers may check the file size. On top of that comes the Lexara loader\n(No. 29) for Stormhand's HD fonts. It is still untested; without `Lexara.dll`\nin the WoW folder it does nothing. The")]}
for fn,md,lang in (('README.de.md','PATCHES.de.md','de'),('README.md','PATCHES.en.md','en')):
    p=d+'/'+fn; s=open(p,encoding='utf-8').read()
    for a,b in LEG[lang]: s=once(s,a,b)
    s=table(s,md); s=rowrefs(s)
    m=re.search(r'(?m)^\| \[28\]\(%s#patch-wotlkext\).*\n'%re.escape(md),s); assert m
    s=s[:m.end()]+ROW[lang]+s[m.end():]
    open(p,'w',encoding='utf-8').write(s)
for fn,lang in (('PATCHES.de.md','de'),('PATCHES.en.md','en')):
    p=d+'/'+fn; s=open(p,encoding='utf-8').read()
    s=refs(s)
    a=s.index('<a id="patch-voicedll"></a>')
    s=s[:a]+SEC[lang]+s[a:]
    open(p,'w',encoding='utf-8').write(s)
print('ok')

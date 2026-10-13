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

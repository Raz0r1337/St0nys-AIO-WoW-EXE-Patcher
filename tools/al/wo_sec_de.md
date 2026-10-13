<a id="patch-wowoptimize"></a>
**wow_optimize.dll beim Start laden (Performance-Optimierung von SUPREMATIST) [BETA]** *(Nr. 27, Autor: St0ny)* 🔴 **[unsicher - ingame ungetestet]**

Lädt beim Start die `wow_optimize.dll` aus dem WoW-Ordner –
[wow_optimize](https://github.com/suprepupre/wow-optimize) von SUPREMATIST
optimiert den Client auf Engine-Ebene: Speicherverwaltung, Lua-VM, Timer sowie
Datei- und Netzwerkzugriffe. Bisher wurde die DLL über die mitgelieferte
`version.dll` (Proxy) oder einen Injector geladen. Mit diesem Patch lädt die
Exe sie selbst. Fehlt die DLL, startet WoW ganz normal.

> [!WARNING]
> **BETA** – dieser Patch ist noch in der Testphase und deshalb vorerst nur in
> den dev-Zweigen, nicht in `st0ny-main`.

> [!CAUTION]
> Laut dem Autor von wow_optimize wertet **Warmane** die DLL als verbotene
> Software – die Folge ist ein **dauerhafter Bann**. Auf **WoW Circle** führt
> sie zum Disconnect. Nur auf Servern verwenden, die das erlauben.

So wird es eingerichtet: Nur die `wow_optimize.dll` aus dem
wow_optimize-Download in den WoW-Ordner legen. Die `version.dll` von
wow_optimize wird nicht gebraucht; liegt sie noch im Ordner, wird die DLL
trotzdem nur einmal geladen. Ihre Einstellungen liest wow_optimize aus der
`wow_opt.ini`, ohne diese Datei gelten die Standardwerte.

Dateigröße und PE-Header bleiben unverändert: Wie die Proxy-`version.dll` legt
die Exe beim Start einen eigenen Thread an, der 3 Sekunden wartet und dann
`LoadLibraryA("wow_optimize.dll")` aufruft. Eingehängt ist das in den
einmaligen Aufruf bei VA `0x76E490`, den der Einstiegspunkt gleich zu Beginn
ausführt. Der Code verteilt sich auf acht freie Lücken zwischen Funktionen,
den DLL-Namen legt der Thread auf dem Stack ab. Der Patch verträgt sich mit dem
Lexara-Lader (Nr. 30) und dem voice.dll-Lader (Nr. 31).

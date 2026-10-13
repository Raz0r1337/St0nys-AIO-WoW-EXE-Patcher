<a id="patch-wowoptimize"></a>
**Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST) [BETA]** *(No. 27, Author: St0ny)* 🔴 **[unsafe - untested ingame]**

Loads `wow_optimize.dll` from the WoW folder at startup –
[wow_optimize](https://github.com/suprepupre/wow-optimize) by SUPREMATIST
optimizes the client at engine level: memory allocation, the Lua VM, timers,
file and network access. So far the DLL was loaded through the bundled
`version.dll` (proxy) or an injector. With this patch the exe loads it itself.
If the DLL is missing, WoW starts normally.

> [!WARNING]
> **BETA** – this patch is still being tested and is therefore only in the dev
> branches for now, not in `st0ny-main`.

> [!CAUTION]
> According to the author of wow_optimize, **Warmane** treats the DLL as
> prohibited software – the result is a **permanent ban**. On **WoW Circle** it
> gets you disconnected. Only use it on servers that allow it.

Setup: put only `wow_optimize.dll` from the wow_optimize download into the WoW
folder. The `version.dll` of wow_optimize is not needed; if it is still there,
the DLL is loaded only once anyway. wow_optimize reads its settings from
`wow_opt.ini`; without that file the defaults apply.

File size and PE header stay unchanged: like the proxy `version.dll`, the exe
starts a thread of its own at startup that waits 3 seconds and then calls
`LoadLibraryA("wow_optimize.dll")`. It hooks into the one-time call at VA
`0x76E490` that the entry point runs right at the start. The code is spread
over eight free gaps between functions, and the thread builds the DLL name on
the stack. The patch works together with the Lexara loader (No. 30) and the
voice.dll loader (No. 31).

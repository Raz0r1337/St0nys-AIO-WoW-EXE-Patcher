# Patch descriptions

[🇩🇪 Deutsch](PATCHES.de.md) | 🇬🇧 English

Detailed descriptions of all patches of the
[St0nys-AIO-WoW-EXE-Patcher](README.md). The overview with authors and
preset assignment is in the [README](README.md#patch-overview).

- [System & performance](#system--performance)
- [Security & privacy](#security--privacy)
- [Login & connection](#login--connection)
- [Modding: interface, MPQs & addons](#modding-interface-mpqs--addons)
- [DLL loaders](#dll-loaders)
- [Gameplay fixes](#gameplay-fixes)
- [Graphics & view distance](#graphics--view-distance)
- [Interface & comfort](#interface--comfort)
- [Window, mouse & camera](#window-mouse--camera)
- [Sound](#sound)
- [Client info: version, build, title, date, icon](#client-info-version-build-title-date-icon)

## System & performance

<a id="patch-laa"></a>
**4GB patch (Large Address Aware)** *(No. 1, Author: Alastor StrixEfuartus / Kebabstorm / Robinsch)* 🟢 **[safe]**

Lets `Wow.exe` use up to 4 GB of RAM instead of the default 2 GB limit for
32-bit applications.

<a id="patch-cache"></a>
**Disable CACHE folder creation** *(No. 2, Author: Alastor StrixEfuartus / Kebabstorm)* 🟢 **[safe]**

Prevents the client from creating a `CACHE` folder automatically.

<a id="patch-itemcache"></a>
**Refresh item cache immediately** *(No. 3, Author: Robinsch)* 🟢 **[safe]**

Removes the 30-second delay when refreshing the item cache. Item changes
become visible immediately.

<a id="patch-worldcrash"></a>
**WorldFrame crash fix (invalid triangle indices)** *(No. 4, Author: Alyst3r (0x539wowmod) (fixed by St0ny))* 🟠 **[untested online]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.

Prevents a crash in a world rendering function (VA `0x81D510`). It walks over
triangles made of three vertex indices each and turns "index minus base" into a
memory address. If an index is smaller than the base, the address points before
the buffer and the client crashes. The patch checks the three indices of the
first triangle beforehand and skips the function in that case. Compared to the
original, the three jump distances have been corrected and the code is shorter.

> [!NOTE]
> The code lives in the free gap at the end of `.text`, which No. 62 uses as
> well. Both fit in there together, the file size does not change.

> [!NOTE]
> A heuristic fix, as the author himself calls it: only the first triangle of
> each call is checked. It does no harm when everything is fine, but does not
> catch every conceivable case.

<a id="patch-timer"></a>
**Always use the precise timer (fixes turning stutter)** *(No. 5, Author: St0ny)* 🟢 **[safe]**

Fixes an old Blizzard bug: when you turn your character, the lower body jerks
into the new direction instead of following smoothly – sometimes right after
starting the game, sometimes not at all.

At startup the client picks its time source. To do so, it compares the precise
timer (QueryPerformanceCounter) with the coarse Windows timer (GetTickCount) for
250 ms. If the two differ by 5 ms or more – a driver briefly holding up the
thread is enough – the client uses GetTickCount for the whole session, which
only counts in steps of about 16 ms.

When turning, the client first twists the upper body and the head and then
pulls the lower body along. How far depends on the time since the last change
of direction – usually only a few milliseconds. With the coarse timer this time
is almost always 0 and then jumps to 16 ms: the lower body stands still and
then jumps a large step ahead.

The patch drops the 250 ms comparison (conditional jump → fixed jump at VA
`0x86AC8E`), so the client always uses the precise timer when it is available.
The check whether the precise timer runs forward on all CPU cores and the CVar
`timingMethod` are kept: with `SET timingMethod "1"` in `Config.wtf` you still
get GetTickCount. As a side effect the client starts about a quarter of a second
faster.

> [!TIP]
> In game, `/run print(GetCVar("timingTestError"))` shows whether the coarse
> timer is active: `3` means the test failed at startup. Without the patch,
> `SET timingMethod "2"` in `Config.wtf` helps as well.

<a id="patch-nothrottle"></a>
**Do not throttle item and player name queries** *(No. 6, Author: tb (ported by St0ny))* 🟢 **[safe]**

When the client does not know an item, creature, quest or name yet, it asks the
server. The client itself limits two of these queries: item info to 512 and
player names to 256 per minute. Once the limit is reached, further queries wait
in a queue – which is why, for example, the first time you open full bags, the
bank or the auction house you see "Retrieving item information" or empty
tooltips for a while, and in busy cities or large raids names briefly show
"Unknown". The patch lifts these two limits (0 = unlimited, one byte each in the
constructors of `itemcache` and `namecache`), so the information arrives right
away. All other queries (creatures, quests, guilds …) are already unlimited in
the original – so with the patch all 15 database queries of the client are
unthrottled.

> [!NOTE]
> The client sends more queries at once this way. Servers with flood
> protection could object – test it first on public servers.

<a id="patch-mirrorfix"></a>
**Mirror Image crash fix (memory leak with mirror images)** *(No. 7, Author: tb (ported by St0ny))* 🟢 **[safe]**

Fixes a Blizzard bug: when a unit that copies a player's appearance (mirror
images, on some servers also player copies as creatures) receives new
appearance data, the client creates a new character component without freeing
the old one. The old one stays attached to the graphics device with its
texture – when exiting, the client then accesses memory that has already been
freed and crashes.

The patch frees a remaining old component first, using the original function.
The small extra code (29 bytes) sits in an unused function of the exe – the
file size does not change.

<a id="patch-wmocube"></a>
**Missing WMO file: error cube instead of ERROR #134** *(No. 8, Author: Alyst3r (ported by St0ny))* 🟢 **[safe]**

If a WMO file is missing (large world objects such as buildings or dungeons,
e.g. in custom MPQs), the client aborts with "ERROR #134 Fatal Condition:
CMap::SafeOpen() failed". With the patch it loads the error cube
`Spells\ErrorCube.mdx` instead – as in WotLK-Extensions, where this is built
into the DLL. The change fits into the original function, the file size does
not change.

<a id="patch-glyphfix"></a>
**Font glyph fix (wrong or garbled characters in text)** *(No. 9, Author: tb (ported by St0ny))* 🟢 **[safe]** 🟡 **[exe grows]**

Fixes Blizzard bugs in the glyph cache, which stores the rendered font
characters on texture pages: otherwise texts (especially numbers, damage and
chat) occasionally show wrong, clipped or foreign characters, especially when
many different characters and font sizes are on screen at the same time.

- When a character is inserted, the widest free gap of a row is recalculated –
  the original never updates this value.
- When a page is evicted, the affected texts remember it and are fully rebuilt
  before drawing (up to four passes, in case the rebuild evicts other texts).
- When a text is cleared, its page markers are cleared too.
- Before a new page is uploaded, the upload buffer is cleared so that no
  leftovers of old characters come along.

This matches the glyph fix from WotLK-Extensions (fork by tb), which does
it in its DLL. Here the four hooks live in a section of their own (`.glyph`,
223 bytes), and one function is rewritten in place.

> [!WARNING]
> The patch appends a section – `Wow.exe` gets larger. This does not mean a certain
> ban, but it is a risk: some servers check the file size.

> [!NOTE]
> Compatible with awesome_wotlk: its MSDF fonts hook other places in the same
> functions or build on top of the rewritten function.

## Security & privacy

<a id="patch-rce"></a>
**Remote code execution exploit fix** *(No. 10, Author: Robinsch)* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Closes a vulnerability that could allow remote code execution through crafted
packets: the `.zdata` section loses its execute permission and Warden modules
are no longer loaded from the local cache. Warden itself keeps working.

> [!WARNING]
> Public servers can detect the change through Warden – there is a risk of a
> ban on public servers.

> [!NOTE]
> "Disable Warden completely" (No. 11) closes the hole as well and makes this
> patch unnecessary. If you select both, the patcher points it out; together
> they do no harm.

<a id="patch-wardenoff"></a>
**Disable Warden completely, RCE fix** *(No. 11, Author: Robinsch)* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

The client drops all Warden packets from the server (`SMSG_WARDEN_DATA`).
Warden modules are code the server has the client execute – with this patch
that is no longer possible at all, including future tricks. Makes the RCE fix
(No. 10) unnecessary; both together do no harm, the patcher just points it out.

> [!WARNING]
> The client no longer answers Warden. Servers with active Warden (e.g.
> AzerothCore or TrinityCore with default settings) may therefore kick you. On
> public servers there is also a risk of a ban.

<a id="patch-scandll"></a>
**Disable Scan.dll** *(No. 12, Author: Alastor StrixEfuartus)* 🟢 **[safe]**

Prevents loading of `Scan.dll`, which the login server can push with its
"Scan" command (a check module of the login server, independent of Warden):
`.\Scan.dll` and `.\Scan.dll.new` become `.\||an.dll` – `|` is not allowed in
file names, so loading is guaranteed to fail.

<a id="patch-noserverpatch"></a>
**Disallow client patches from the server** *(No. 13, Author: Kebabstorm)* 🟢 **[safe]**

The server can no longer send patch files to the client and have them
installed.

<a id="patch-nosurvey"></a>
**Disallow hardware surveys from the server** *(No. 14, Author: Kebabstorm)* 🟢 **[safe]**

The server can no longer request a hardware survey (information about your PC)
from the client.

## Login & connection

<a id="patch-skipbnet"></a>
**Skip Battle.net login** *(No. 15, Author: Kebabstorm)* 🟢 **[safe]**

The client skips the Battle.net login step and goes straight to the classic
login.

<a id="patch-skiprdp"></a>
**Skip Remote Desktop check** *(No. 16, Author: Kebabstorm)* 🟢 **[safe]**

The client no longer checks whether it runs over a Remote Desktop connection –
so WoW can be played via RDP, for example.

<a id="patch-nohttp"></a>
**Disable HTTP requests to Battle.net** *(No. 17, Author: Kebabstorm)* 🟢 **[safe]**

The client no longer fetches news, help articles and terms of use from
Blizzard's servers – they no longer exist for 3.3.5 anyway.

<a id="patch-afk"></a>
**Prevent the idle kick after character auto-login** *(No. 18, Author: St0ny)* 🟢 **[safe]**

After an auto-login without any keyboard or mouse input the timestamp of the
last input is still 0 – the client immediately considers the player idle and
kicks them (CharAutoLogin bug). The patch sets the timestamp to "now" on the
first pass if it is still empty and removes a fatal-error check that can
trigger there. The actual timers stay unchanged: AFK status after 5 minutes,
logout after 30 minutes without input.
**Required for character auto-login** – details on [Discord](https://discord.com/channels/858041817043042364/1515439916878663701).

## Modding: interface, MPQs & addons

<a id="patch-glue"></a>
**Allow custom GlueXML** *(No. 19, Author: Alastor StrixEfuartus / Kebabstorm (fixed by St0ny))* 🟢 **[safe]**

Allows modifying the login and character selection screens with your own
XML/Lua files (glue screen modding): the signature check of the interface files
always reports "valid", and local `Interface\GlueXML` and `Interface\FrameXML`
folders are no longer renamed to `*.old`.

> [!NOTE]
> Side effect that every version of this patch has: addons without a signature
> file are treated as "secure" (like Blizzard code) as well and may call
> protected functions – similar in effect to the LUA unlock (No. 23). Servers
> with anti-cheat may judge it the same way.

The widespread version (Alastor/Kebabstorm) continues with uninitialised
variables when the signature file is missing and frees a dangling pointer on
the way (undefined behaviour). Here the error exit returns "valid" directly
instead – same effect, without the wild memory access.

<a id="patch-mpqsig"></a>
**Allow unsigned / incorrectly signed MPQs** *(No. 20, Author: Alastor StrixEfuartus)* 🟢 **[safe]**

The signature check for MPQ archives always reports "valid". The client only
checks archives sent by the server with it: `wow-patch.mpq` (client patch from
the server) and `Cache\Survey.mpq` (hardware survey). The regular `Data\*.MPQ`
are loaded without any signature check anyway – so this patch is not needed for
your own patch MPQs. Together with No. 13 and No. 14 it has no effect any more,
because neither path runs then.

<a id="patch-mpqnames"></a>
**Allow extended MPQ names** *(No. 21)* 🟢 **[safe]**

Allows wildcard names for MPQ archives (`patch-*.MPQ` and
`patch-locale-*.MPQ`).

<a id="patch-localdata"></a>
**Load data directly from the Data folder (no MPQ)** *(No. 22, Author: Alastor StrixEfuartus)* 🟢 **[safe]**

The client reads files directly from the Data folder without packing them into
an MPQ – e.g. `Data\DBFilesClient\ItemDisplayInfo.dbc`. Handy for modders.

<a id="patch-luaunlock"></a>
**LUA unlock (spells, movement, macros)** *(No. 23, Author: Alastor StrixEfuartus)* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Addons and macros may call protected functions: movement functions
(`MoveForwardStart`, `TurnLeftStart`, …), `CastSpellByName`, `CastSpell`,
`UseAction`, `PetAttack`, `RunMacro`/`RunMacroText` and the GM ticket
functions. Not unlocked, because they have their own checks in the code:
`TargetUnit`, `FocusUnit`, `InteractUnit`, `ReloadUI`; `AttackTarget` still
prints an error. No. 24 unlocks these and all others.

> [!WARNING]
> This enables automation. Servers with anti-cheat may treat it as botting –
> this can lead to a ban.

<a id="patch-luaunlockfull"></a>
**LUA unlock (complete): allow all protected functions** *(No. 24, Author: St0ny)* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Extends No. 23 to all protected functions. The client's central protection
check knows 24 protection types in three classes (always forbidden, allowed only
after a hardware event, allowed only while attribute changes are permitted) –
with this patch it reports "allowed" for all of them. In addition, the own
checks of the functions that do not go through this central check are bypassed:
`TargetUnit`, `AssistUnit`, `TargetLastTarget`, `TargetNearest…`,
`TargetDirection…`, `AttackTarget`, `StartAttack`, `FocusUnit`, `ClearFocus`,
`InteractUnit`, `ReloadUI`, `UninviteUnit`, `CancelLogout`, the pet commands
(`PetAttack`, `PetFollow`, …) as well as `UseAction`, trading, the auction
house, the calendar, LFG, raid subgroups and creating or editing macros. The
block list for spells cast from insecure code is no longer checked either.

Left untouched are the frame protection check (`SetAttribute`, `Show`, `Hide`
on protected frames) and `RegisterForSave` – they do not concern game actions.
Makes No. 23 unnecessary; both together do no harm, the patcher only points it
out.

> [!WARNING]
> This enables automation to the full extent. Servers with anti-cheat may treat
> it as botting – this can lead to a ban.

<a id="patch-keyprop"></a>
**Pass all keyboard events on to addons (OnKeyDown)** *(No. 25, Author: Alyst3r (0x539wowmod))* 🔴 **[unsafe]** 🟠 **[untested ingame]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

If a frame has an OnKeyDown script, the client reports the key as handled
afterwards – it no longer reaches the key bindings. With the patch every key
continues to the key bindings after the OnKeyDown script. This lets addons see
all key presses without blocking the normal controls.

> [!NOTE]
> Addons that rely on OnKeyDown "swallowing" a key will additionally trigger the
> bound action.

<a id="patch-globalsv"></a>
**Merge addon data of all accounts (SavedVariables)** *(No. 26, Author: St0ny (original by boredatom))* 🟠 **[untested]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

WoW normally stores addon data per account under `WTF\Account\<ACCOUNT>\`. With
this patch all accounts use the shared folder `WTF\Account\global\` instead – if
you play several accounts, you only have to set up your addons once. The
following are merged:

- the account-wide addon data (`SavedVariables\*.lua`),
- the per-character addon data (`<Realm>\<Character>\SavedVariables\*.lua`),
- the list of enabled addons (`AddOns.txt`, account-wide and per character).

Macros, key bindings as well as chat and game settings stay separate per
account as before.

> [!NOTE]
> The patch does not move existing addon data. To keep it, copy the contents of
> `WTF\Account\<ACCOUNT>\` to `WTF\Account\global\` before the first start. If
> the patch is reverted, WoW uses the folders of the individual accounts again;
> `global` is simply left as it is.

Technically the patch changes 9 bytes in the function that stores the account
name for the addon paths after login (VA `0x5F9080`): instead of the
name it copies the text `global`, which is already in `Wow.exe`. The original by
boredatom (`patch_globalvariables.exe`) moves the rest of the function by 4 bytes
for this; here everything stays in place. The advertising that the original
additionally writes into `Wow.exe` (a Telegram notice on the login screen) is
not included.

## DLL loaders

<a id="patch-awesome"></a>
**Enable AwesomeWotlkLib.dll support** *(No. 27, Author: FrostAtom)* 🟢 **[safe]**

Allows `AwesomeWotlkLib.dll` to be loaded on client start. This DLL extends
the client with additional features and improvements for private servers.
**Requires** `AwesomeWotlkLib.dll` from [awesome_wotlk](https://github.com/noname08662/awesome_wotlk).
Belongs together with the 4GB patch (No. 1): if that one is not selected, the
patcher points it out.

The loader sits at the start of the client's main fiber (right before
`WinMain`) and overwrites the beginning of the Scan.dll start function for
that; the Lua function `ScanDLLStart` becomes a no-op and the Scan.dll flag is
set to "passed". As a side effect the patch disables the Scan.dll mechanism
(like No. 12). If the DLL is missing, WoW simply starts normally.

> [!NOTE]
> The patch itself is harmless, it only loads a DLL that is not included here.
> Only the loaded `AwesomeWotlkLib.dll` may be noticed by servers with
> anti-cheat – so use it only where awesome_wotlk is allowed.

> [!NOTE]
> If No. 63 (HD portraits) is applied as well, awesome_wotlk's CVar
> `portraitResolution` has no effect – the resolution of the exe patch always
> wins.

<a id="patch-wotlkext"></a>
**Enable WotLKExtensions.dll support** *(No. 28, Author: St0ny (original by Alyst3r))* 🟢 **[safe]**

Loads `WotLKExtensions.dll` from the WoW folder when the client starts. The DLL
from [WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions) by Alyst3r
extends the client for your own server projects, e.g. with custom DBC files,
custom packets and new Lua functions.
**Requires** `WotLKExtensions.dll` from WotLK-Extensions. Belongs together with
the 4GB patch (No. 1): if that one is not selected, the patcher points it out.

The original patcher of WotLK-Extensions puts its loader at the same place as
No. 27 – the two could not be combined. Instead, this loader hooks the first
function the client calls from there, and it sits in the unused part of the
Scan.dll start function behind the loader of No. 27. This way No. 27 and No. 28
can be applied alone or together; together, the client loads both DLLs. As with
No. 27, the Lua function `ScanDLLStart` becomes a no-op and the Scan.dll flag is
set to "passed" – which also disables the Scan.dll mechanism (like No. 12). If
the DLL is missing, WoW simply starts as usual. The file size does not change.

> [!NOTE]
> The patch itself is harmless, it only loads a DLL that is not included here.
> WotLK-Extensions is meant for your own server projects; according to the
> project, some servers can detect calls to its Lua functions. Only use it
> where WotLK-Extensions is allowed.

> [!NOTE]
> At startup the DLL applies some patches in memory itself, always including
> its own year 2031 fix. None of them collides with the patches of this
> patcher: where the DLL changes the same places (its LUA unlock like No. 24,
> its GlueXML unlock like No. 19), no broken code results, and with the DLL its
> version applies. Its time fix, however, makes yearly holidays with a fixed
> date and weekly holidays disappear from the calendar.

<a id="patch-voicedll"></a>
**Load voice.dll at startup (mod-voicechat) [ALPHA]** *(No. 29, Author: St0ny)* 🟠 **[untested]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

Loads `voice.dll` from the WoW folder at startup – the client part of
[mod-voicechat](https://github.com/Raz0r1337/mod-voicechat), a voice chat
module for AzerothCore. If the DLL is missing, WoW starts normally.

> [!CAUTION]
> **ALPHA** – the mod-voicechat module is not finished yet. That is why this
> patch is deselected by default.

File size and PE header stay unchanged: the jump at the entry point (VA
`0x401005`) is redirected into a free 27-byte gap between two functions (VA
`0x944B45`), which holds `push "voice.dll"` → `call [LoadLibraryA]` → jump to the
original target. Before writing, the patcher checks the entry point, the gap and
the `LoadLibraryA` import.

## Gameplay fixes

<a id="patch-areatrigger"></a>
**More precise area trigger timer (50 ms instead of 100 ms)** *(No. 30, Author: Robinsch)* 🟢 **[safe]**

Increases the area trigger check frequency from 100 ms to 50 ms, so zone
transitions and triggers are detected more precisely.

<a id="patch-swing"></a>
**Remove melee swing on right-click** *(No. 31, Author: Robinsch)* 🟢 **[safe]**

Prevents the faulty auto-attack swing that was triggered when right-clicking
a target.

<a id="patch-npcanim"></a>
**Suppress NPC attack animation when turning** *(No. 32, Author: Robinsch (fixed by St0ny))* 🟢 **[safe]**

Suppresses the NPC attack animation when turning if no actual attack takes
place.

When a unit turns on the spot, the client first twists the upper body and the
head; the legs follow with the step animation (ShuffleLeft/-Right). The client
starts this animation by re-evaluating the unit's animation – for NPCs this
produced the attack animation. Robinsch's patch (conditional jump → fixed jump
at VA `0x73E3C9`) disabled that call for **all** units, including players: when
turning, their legs no longer took steps and only the upper body twisted
oddly.

Here the block at VA `0x73E385`–`0x73E3D5` is rewritten more compactly (same
logic) and additionally checks whether the unit is a player: players turn as in
the original, NPCs behave as with Robinsch's patch.

<a id="patch-spellanim"></a>
**Fix spell animation after cancelled channel** *(No. 33, Author: Robinsch)* 🟢 **[safe]**

Fixes a bug where the preparation animation got stuck after cancelling a
channelled spell.

<a id="patch-ghostattack"></a>
**Fix "ghost" attack when NPCs evade from combat** *(No. 34, Author: Robinsch (fixed by St0ny))* 🟢 **[safe]**

Before the client shows a new melee result, it plays the last stored swing on
the target once more. If an NPC has evaded from combat in the meantime, that is
a stale swing – the "ghost" attack. With the patch the stored swing is only
discarded, no longer played (conditional jump → unconditional jump at VA
`0x7561BF` in `UnitCombat_C`).

Robinsch's list has the offset `0x355BF` – a 5 is missing. It hit a `call` in a
string helper function and would have turned it into an endless loop. Here it
is corrected to `0x3555BF`.

<a id="patch-naked"></a>
**Fix naked character bug** *(No. 35, Author: Robinsch (fixed by St0ny))* 🟢 **[safe]**

Fixes characters shown naked, as happens on private servers when new items are
only distributed via `ItemDisplayInfo`. The patch disables `SPELL_AURA_X_RAY`:
the check whether the own player has this aura (VA `0x6DE840`) always reports
"no". With the aura the client draws other units without equipment.

For this patch Robinsch calculated with the base address `0x500C00` instead of
`0x400C00` (as noted in his source code). His offset `0x1DDC5D` therefore hit a
`push 0` in the Lua function `GetTradeSkillTools`. Here it is corrected to
`0x2DDC5D`.

<a id="patch-forcereaction"></a>
**Keep force reaction on /reload** *(No. 36, Author: Robinsch)* 🟢 **[safe]**

Prevents force reaction values (e.g. faction standing) from being reset when
reloading the UI. Important for custom servers.

<a id="patch-mail"></a>
**New mail without the 60-second wait** *(No. 37, Author: Robinsch)* 🟢 **[safe]**

The client checks for new mail immediately – no more 60-second wait and no
relog needed to receive new mail.

<a id="patch-deadchat"></a>
**Allow chat commands while dead** *(No. 38, Author: Robinsch)* 🟢 **[safe]**

Slash commands also work while the character is dead.

<a id="patch-follow"></a>
**Allow /follow on NPCs** *(No. 39, Author: St0ny (original by Alastor StrixEfuartus))* 🟠 **[untested online]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.

`/follow` also works on NPCs, not just players. Based on the `/follow` patch
from Alastor StrixEfuartus' 12th Generation EXE, ported and adjusted by St0ny:
the original redirects the check into a code cave that ignores its result.
That cave, however, would sit exactly in the gap at the end of `.text` that
No. 4 and No. 62 use. Here the conditional jump after the check is made
unconditional instead – a single byte, same effect, and the patches work
together.

<a id="patch-level101"></a>
**Level 101+ fix (game tables, barber chair, base stats)** *(No. 40, Author: Alastor StrixEfuartus (fixed by St0ny))* 🟢 **[safe]**

The client's game tables (`gtCombatRatings`, `gtBarberShopCostBase`,
`gtOCTRegenHP`/`MP`, `gtChanceToMeleeCrit` … – eleven tables) have 100 rows per
column, one per level. From level 101 on the client reads outside the column –
druids no longer see their base stats, the barber chair does not work, in the
worst case the client crashes. The patch clamps the row to the last one of the
column: level 101+ gets the values for level 100, everything below stays
unchanged.

> [!NOTE]
> The widespread version from the 12th Generation EXE removes the level from
> the calculation entirely instead – so *all* characters show the values for
> level 1 (ratings, critical strike chance, regeneration …). Here the two
> accessor functions (VA `0x7F69B0` and `0x7F69E0`) are rewritten for this.

**Requires** the patch "Allow custom GlueXML" (No. 19) according to the
source. There it is called "Disable XML SIG MD5", hence the note "Use XML MD5".

<a id="patch-raceclass"></a>
**Character creation: more than 10 classes (random class)** *(No. 41, Author: Alastor StrixEfuartus / Robinsch)* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

The random class selection in character creation collects the allowed classes
in an array with 10 slots. With custom classes (`ChrClasses.dbc` with more than
10 entries) it would overflow; the patch enlarges it to 30 slots. Which race may
pick which class is still checked by the server – this patch does nothing more.

<a id="patch-namecheck"></a>
**Disable the name check in character creation (e.g. digits in names)** *(No. 42, Author: Alyst3r (0x539wowmod) (fixed by St0ny))* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Disables the complete client-side name check in character creation: the check
function (VA `0x6B0F90`) always reports "name valid". This allows e.g. digits in
names – but all other client rules (length, allowed characters etc.) are gone as
well. The original (0x539wowmod) uses a detour with the wrong calling
convention, here it is done directly in the function (`mov eax, 57h` / `ret`).

**Required for [mod-two-names](https://github.com/lightninjay/mod-two-names)**
(AzerothCore module for first and last names, e.g. "Arthas Menethil"): without
this patch the client rejects names containing a space. The project ships the
same exe patch itself (`tools/patch_wow_safe.py`, same bytes at the same
place). It also needs the server module and the project's GlueXML files as a
patch MPQ, and for the changed interface files "Allow custom GlueXML" (No. 19).

> [!WARNING]
> The server still checks names itself and has to allow them as well, otherwise
> it rejects the character.

<a id="patch-maxchars"></a>
**Max characters per realm raised to 255** *(No. 43, Author: St0ny)* 🟢 **[safe]**

Raises the client-side limit from 10 to 255 characters per realm. The server
has to support this as well. Additional interface changes (GlueXML) are
required for the character selection screen to show more than 10 slots.

<a id="patch-customitem"></a>
**Custom Item Fix (BETA) v2** *(No. 44, Author: Kebabstorm (fixed by St0ny))* 🟠 **[untested]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

Makes custom items possible without changing the client's `Item.dbc`. Many
places in the client read the display ID, inventory type, class, subclass and
sheath of an item only from `Item.dbc`. Items that only exist in the server's
database are missing there – the client then shows e.g. no model on the
character and no icon. But `Wow.exe` already has helper functions that look
these values up in the item cache first (the data the server sends for every
item) and only then in `Item.dbc`. The patch redirects the plain DBC lookups to
these helper functions. If an item is in both, the server's values apply. On
the server, an entry in `item_template` is then all a custom item needs; with
TrinityCore, `DBC.EnforceItemAttributes = 0` must be set in `worldserver.conf`.
Only the material (the sound when moving the item in the inventory) still comes
from `Item.dbc` alone.

The basis is the "Custom Item Fix (BETA) v1" from Kebabstorm's
[WoW 3.3.5 Patcher (Custom Item Fix)](https://www.wowmodding.net/files/file/283-wow-335-patcher-custom-item-fix/).

**Recommended** together with "Disable CACHE folder creation" (No. 2): then WoW
does not store the item cache on disk and fetches changed custom items fresh
from the server at every start. If No. 2 is not selected, the patcher points
this out.

> [!NOTE]
> The v1 patch list this patch was taken from contained two errors that would
> have crashed the client: one line was missing a byte (turning the function
> for the item class into garbage), another was a copy of the line before it
> (a call landed in the middle of an unrelated function). v2 fixes both. All rebuilt places were checked by emulation with
> test items: only in the cache, only in `Item.dbc`, in both and in neither.

Not taken over from v1: the PE checksum (Windows does not check it for
programs) and the change `Cache` → `||che` – that is exactly patch No. 2.

<a id="patch-climb"></a>
**Remove the climb angle limit (walk up any slope)** *(No. 45, Author: Alastor StrixEfuartus)* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

The character can walk up any slope, no matter how steep. The original stops at
50°: the client compares the slope with the cosine of that angle (`0.6427876`
at VA `0xA37F0C`). The patch sets it to `0.0` = cos 90°.

> [!WARNING]
> Servers with anti-cheat may detect this as a climb hack – this can lead to a
> ban.

<a id="patch-jump"></a>
**Change jump height (original -7.9555473)** *(No. 46, Author: Alastor StrixEfuartus)* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Changes the initial velocity of a jump (VA `0xAA33DC`, original `-7.9555473`).
The patcher asks for the value after the selection: a negative number from
`-100` to just below `0`, with comma or dot as decimal separator. The lower the
value, the higher the jump; the height grows with the square, i.e. `-11.25`
gives about double and `-15.91` about four times the jump height. The value is
remembered like those of the client info patches.

> [!WARNING]
> Servers with anti-cheat may detect this as a jump hack – this can lead to a
> ban.

<a id="patch-airforward"></a>
**Steer forward/backward while jumping** *(No. 47, Author: Alyst3r (0x539wowmod) (ported by St0ny))* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Normally the client ignores forward and backward input while the character is
jumping or falling. With the patch the direction can be changed in the air as
well, even to the opposite direction. 0x539wowmod replaces the client's forward
input with a DLL for this; that version differs from the original only in two
jumps (do not stop in the air, recalculate the speed), which are changed directly
in the EXE here – without DLL and without a code cave. Added to this is the
byte patch from 0x539wowmod that updates the movement in the air.

> [!WARNING]
> Servers with anti-cheat may detect changed movement in the air – this can
> lead to a ban.

<a id="patch-airlateral"></a>
**Steer sideways while jumping** *(No. 48, Author: Alyst3r (0x539wowmod) (ported by St0ny))* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Like the previous patch, but for sideways movement (strafing): two jumps in the
client's sideways input plus the byte patch from 0x539wowmod that no longer stops
the movement early while the falling flag is set.

> [!WARNING]
> Servers with anti-cheat may detect changed movement in the air – this can
> lead to a ban.

<a id="patch-airturn"></a>
**Turning while jumping changes the flight direction** *(No. 49, Author: Alyst3r (0x539wowmod) (ported by St0ny))* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

If you turn while jumping (mouse or keys), the character keeps its flight
direction in the original. With the patch the client sets the movement direction
in the air as well, like the 0x539wowmod DLL does. Works best together with the
two previous patches.

> [!WARNING]
> Servers with anti-cheat may detect changed movement in the air – this can
> lead to a ban.

<a id="patch-doublejump"></a>
**Double jump (more jumps in the air)** *(No. 50, Author: Alyst3r (0x539wowmod) (ported by St0ny))* 🔴 **[unsafe]** 🟡 **[exe grows]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Allows more jumps while the character is in the air. After the selection the
patcher asks how many extra jumps there should be (1 to 9, `1` = double jump);
the value is remembered like those of the client info patches.

The client's jump function (VA `0x9883F0`) rejects every jump while the
character is falling. 0x539wowmod replaces it with a DLL and counts jump
charges. Here the same happens in a small code cave: a jump from the ground
sets a counter to the selected number, and in the air a jump is allowed as long
as the counter is not 0. Rooted or flying still blocks jumping. Every air jump
uses the same jump height as a normal jump (so also the value from "Change jump
height", No. 46). The separate second jump height of 0x539wowmod's double jump
is not included. The counter is only reset by the next jump from the ground,
not on landing: if you land after a jump and then walk off a ledge, you have the
chosen number of jumps in the air again.

The counter is a byte the client has to write. That is why the patch gets a small
section `.djump` of its own at the end of the file (the gap in `.text` is not
writable); this makes `Wow.exe` slightly larger.

> [!WARNING]
> Servers with anti-cheat may detect jumps in the air – this can lead to a ban.
>
> This patch appends a section of its own, which makes `Wow.exe` larger.
> This does not mean a certain ban, but it is a risk: some servers check the file size
> of `Wow.exe`.

<a id="patch-noammo"></a>
**Ranged attacks without ammo** *(No. 51, Author: Alyst3r (ported by St0ny))* 🟠 **[untested]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

For Shoot, Auto Shot and other abilities that need ammo, the client checks
whether arrows or bullets are present. The patch skips this check in the
client (jump to the success exit at VA `0x809540`).

> [!IMPORTANT]
> The server checks on its own. Ranged attacks without ammo only work if the
> server is changed so that it does not require ammo – otherwise it still
> reports "no ammo". Without adjusted visuals the projectiles are invisible.

## Graphics & view distance

<a id="patch-farclip"></a>
**CVar farclip unlock (max 10000)** *(No. 52, Author: Alastor StrixEfuartus)* 🟢 **[safe]**

Unlocks the maximum view distance (farclip) to 10000 yards. The client clamps
the value when it is set, in a single function (VA `0x780770`), and has two
upper limits for it: 1583 yards normally and 791 yards as a fallback. The 791
applies in the old vanilla zones and on machines with at most 1 GB of RAM –
the client really does query the RAM size there. The patch raises both limits
to 10000, otherwise the view distance drops back to 791 depending on the zone.
The lower limit of 183 yards stays untouched, and there is no separate input
limit for the CVar – this clamp is the limit.
Not to be confused with the 1277 from the video menu: that is the maximum of
the view distance slider and a completely different location in the EXE (see
patch No. 56 "Graphics options: extend slider maximums").

<a id="patch-horizon"></a>
**CVar horizonFarclipScale unlock (max 12)** *(No. 53, Author: St0ny)* 🟢 **[safe]**

Unlocks the CVar `horizonFarclipScale` and sets its maximum to 12. Noticeably
increases the horizon view distance.

<a id="patch-envdetail"></a>
**CVar environmentDetail unlock (no limit instead of 1.5)** *(No. 54, Author: St0ny)* 🟢 **[safe]**

Removes the upper limit of the CVar `environmentDetail` entirely. Originally
the value is clamped to the range 0.5 to 1.5; the patch replaces the clamped
value with the raw value at the shared exit of the check – so the lower limit
0.5 goes away as well, any value is passed through (sensible values start at
0.5).
Important: this CVar does nothing but multiply the GameObject view distances
(see patch No. 57) – in the original only for categories 1 to 3, with patch
No. 57 for all five. That makes it the most convenient FPS lever for object
rendering, since it works in-game without re-patching.

<a id="patch-grounddist"></a>
**CVar groundEffectDist unlock (max 3166 instead of 140)** *(No. 55)* 🟢 **[safe]**

Raises the maximum view distance for ground effects (grass, flowers, ground
clutter) from 140 to 3166 yards.

<a id="patch-sliders"></a>
**Graphics options: extend slider maximums** *(No. 56, Author: St0ny)* 🟢 **[safe]**

Raises the maximums of four sliders in the video menu, "Effects" tab. The
CVars themselves have long been unlocked by the unlock patches – but the
sliders stayed at Blizzard's values because they don't take their maximum
from the CVar limit.

| CVar                  | Slider before | Slider after |
|-----------------------|--------------:|-------------:|
| `farclip`             | 1277          | 2477         |
| `environmentDetail`   | 1.5           | 2.5          |
| `groundEffectDist`    | 140           | 250          |
| `groundEffectDensity` | 64            | 256          |

The minimums stay unchanged (177 / 0.5 / 70 / 16), as do the step sizes from
the interface. They divide evenly: 8 steps for `environmentDetail`, 18 for
`groundEffectDist`, 30 for `groundEffectDensity`. For the view distance slider
the interface calculates the step size itself as (max−min)/10, so 230 yards
per notch here.

<details>
<summary><b>Background: why the sliders didn't grow with the unlocks before</b></summary>

The interface builds every slider using this pattern:

```lua
minValue = GetCVarMin(cvar)  -- or fallback value from the Lua
maxValue = GetCVarMax(cvar)  -- or fallback value from the Lua
```

So it asks the EXE first and only uses the fallback from
`VideoOptionsPanels.lua` if the EXE returns nothing. In the original,
`GetCVarMax` only knows two CVars: `extShadowQuality` and `farclip`. For
everything else it returns nothing, and then the hard-coded Lua values
1.5 / 140 / 64 apply. For `farclip` it returned a fixed 1277 – likewise
regardless of how far the CVar is unlocked.

The patch replaces the fixed farclip comparison with a call to a small lookup
routine that walks a list of CVar names. If a CVar is listed, the interface
gets the matching maximum; if not, everything works as before. The routine
(18 bytes) lives in a free gap between two functions of the code section, the
list with the maximums in the unused rest of `.rdata` – the file does not grow.

Important: `GetCVarMax` exists twice in the EXE – once for the login/character
screens and once for the running game. Both call the same lookup routine. If
only one of them is patched, the sliders in-game stay at 1277 / 1.5 / 140 / 64
without any visible sign.

</details>

**Two limitations**

- The slider only sets the CVar. Without the unlock patches the client clamps
  the value back to its original immediately – so the patches "CVar farclip
  unlock" (No. 52), "CVar environmentDetail unlock" (No. 54) and "CVar
  groundEffectDist unlock" (No. 55) belong with it. If they are missing from
  the selection, the patcher points this out.
- For `groundEffectDensity` nothing changes above 64: the vertex buffer for
  ground clutter is hard-clamped in the client to density × 64 ≤ 4096. The
  slider goes up to 256, but visually nothing changes above 64.

**The Ultra preset stays at Blizzard's values**

The master "Graphics quality" slider still sets 1277 / 1.5 / 140 / 64 on
Ultra, not the new maximums. This cannot be changed from the EXE: the preset
values are plain Lua constants in
`Interface\FrameXML\GraphicsQualityLevels.lua` and are written directly into
the sliders from there. The only link from the EXE into this path is
`VideoOptionsEffectsPanel_FixupQualityLevels`, and that function can only
clamp – values above the maximum down, values below the minimum up. Both apply
per CVar to all six quality levels at once; a single level cannot be
addressed.

> [!CAUTION]
> Tempting dead end: you could pull Ultra up via the minimum
> (`GetCVarMin("farclip")` is the double at `0x9F5798`, originally 177.0), but
> then ALL six levels are pulled to that value – Low just like Ultra – and the
> slider ends up with minimum above maximum, sticks to the end stop and gets a
> negative step size. Exactly that happened in an earlier attempt and caused
> startup crashes via `Config.wtf`. Leave the minimum double alone.

If you really want Ultra at the new maximums, you need the interface side, i.e.
an MPQ with a modified `GraphicsQualityLevels.lua` – then the values are fixed
in the client instead of being set afterwards by an addon. This is
deliberately not part of this patcher: it remains a pure EXE patcher that
touches nothing but `Wow.exe`.

**No slider for horizonFarclipScale**

There is no slider for this CVar in the video menu at all – it doesn't appear
anywhere in the interface. An EXE patch cannot raise anything here because
there is nothing to raise. The value can still only be set via `Config.wtf`,
`/console horizonFarclipScale 12` or a CVar addon (it is unlocked up to 12,
see above).

> [!NOTE]
> The file size does not change: the small search routine lives in a free gap
> between two functions, the table with the maximums in the unused rest of
> `.rdata`. There is no overlap with No. 4 and No. 62.

<a id="patch-goscale"></a>
**GameObject view distance: Cat 0 and Cat 4 scale with environmentDetail** *(No. 57, Author: St0ny)* 🟢 **[safe]**

Fixes an omission in the client: the function that calculates the runtime view
distances from the base values only multiplies Cat 1 to 3 by the CVar
`environmentDetail`. Cat 0 (small clutter) and Cat 4 (huge buildings) take
their base value unchanged – the slider simply doesn't affect them.
The patch adds the missing multiplication in both blocks. The space for it
comes from dropping a redundant copy of the size thresholds (both tables are
identical and never modified). Afterwards `environmentDetail` scales all five
categories evenly – the slider becomes a true master slider. The base view
distances stay at Blizzard's values; everything is controlled via the CVar:

| environmentDetail | Cat 0 | Cat 1 | Cat 2 | Cat 3 | Cat 4 |
|------------------:|------:|------:|------:|------:|------:|
| 1.0               | 30    | 100   | 200   | 750   | 1250  |
| 2.0               | 60    | 200   | 400   | 1500  | 2500  |
| 10 | 300   | 1000  | 2000  | 7500  | 12500 |

With patch No. 58, Cat 0 is at 50 instead of 30 yards (so 50 / 100 / 500 in
the table above). Values above 1.5 require the patch "CVar environmentDetail
unlock" (No. 54).

<a id="patch-cat0"></a>
**GameObject view distance: Cat 0 from 30 to 50 yards** *(No. 58, Author: St0ny)* 🟢 **[safe]**

The patch costs performance: noticeably more small clutter is visible at the
same time, and the number of drawn objects is the performance lever. If you
want to keep view distances entirely at Blizzard's values, leave it out. It
only raises the smallest object category: candles, books, sacks,
tools. In the original, Cat 0 is so tight at 30 yards that small clutter
disappears much earlier than everything else; 50 improves the ratio to Cat 1
from 1:3.3 to 1:2, and the `environmentDetail` slider scales it
proportionally. Cat 1 to 4 are not touched – the view distance is controlled
via the CVar, which, together with the code patch No. 57, stretches all five
categories evenly.

Five related values are changed:

| Value                   | Blizzard | Patch |
|-------------------------|---------:|------:|
| Base view distance      | 30       | 50    |
| Runtime view distance   | 30       | 50    |
| View distance squared   | 900      | 2500  |
| Fade start              | 25       | 45    |
| Fade start squared      | 625      | 2025  |

The runtime value must match the base value, the squares are the squares of
those, and the fade start is view distance minus fade band. The fade band stays
at Blizzard's 5 yards.

<details>
<summary><b>Background: how the categories are determined</b></summary>

The client takes an object's bounding box, determines the **longest edge**
(not the radius, not the volume) and looks for the first threshold that is
greater than or equal to that edge:

| Category | Longest edge      | Examples                                  |
|----------|-------------------|-------------------------------------------|
| Cat 0    | up to 1 yard      | candles, books, sacks, tools              |
| Cat 1    | 1 to 4 yards      | crates, barrels, cabinets, fire bowls     |
| Cat 2    | 4 to 15 yards     | large tables, banners, cannons            |
| Cat 3    | 15 to 100 yards   | gates, cages, thrones, raid doors         |
| Cat 4    | 100 yards and up  | zeppelins, floating platforms             |

The thresholds are a separate table in the EXE and are NOT touched by this
patch. The examples come from the client's `GameObjectDisplayInfo.dbc`.
Note: the fully transformed box is classified, so an upscaled object can end
up one category higher than its model suggests.

**Interaction with the CVar environmentDetail**

The values in this patch are base values. The client recalculates them every
time `environmentDetail` is set:

```
view distance = base value * environmentDetail
```

In the original this ONLY applies to Cat 1, 2 and 3 – for Cat 0 and Cat 4 the
multiplication is missing from the code. The patch "Cat 0 and Cat 4 scale with
environmentDetail" adds it, so all five categories grow evenly.

Important when doing the math: the two factors **multiply**. Base value ×2 at
CVar 1.5 results in ×3, not ×2. To reach a target factor Z at CVar value E,
enter Z/E as the base value.
Without patch No. 57 this only applies to Cat 1–3, and the categories drift
apart at high CVar values: Cat 3 would eventually overtake Cat 4, so
medium-sized objects would be visible further away than huge ones.

Note: if a category distance is above the CVar `farclip`, the general view
distance cuts off first and the category has no visible effect anymore. At
farclip 1100, Cat 4 is effectively capped at 1100 – higher values only take
effect once farclip grows accordingly.

**Derived tables**

View distance and fade band are one table each in the EXE, plus four more that
the client calculates from them – every time `environmentDetail` is set:

```
runtime view distance = base value * environmentDetail
fade start            = runtime view distance - fade band
squared tables        = the square of each
                        (the engine culls using the squares, saving the sqrt)
```

So the only real inputs are the base view distances and the fade bands.
Anyone writing the four derived tables anyway has to keep them consistent,
otherwise the values jump on the first recalculation.

**Fade bands**

The fade band widths are at Blizzard's original values (5/10/15/20/50) and are
not scaled. The band is the distance over which an object fades out before
the cull limit – narrow bands keep objects opaque until shortly before,
instead of letting them fade out semi-transparently over many yards.
The fade start is always view distance minus band and moves with
`environmentDetail`: at 1.0 it is 25/90/185/730/1200, at 2.0 it is
55/190/385/1480/2450. Because the band stays the same, the fade start grows
slightly faster than the view distance itself.

Note: the view distance determines how many objects are drawn at the same
time and is therefore the performance lever. The fade bands cost practically
no FPS – if you find pop-in more annoying than losing a few frames per second,
you can widen them independently of the distances.

</details>

<a id="patch-occluder"></a>
**Occluder fix for Stormwind (Open Azeroth)** *(No. 59, Author: Robinsch)* 🟢 **[safe]**

Disables the occluders (view blockers) for Stormwind that are hard-coded in the
client: the map key of the table entry for the Eastern Kingdoms is set to
99999, so it no longer matches any map. This way no buildings and objects are
hidden incorrectly on custom servers with a rebuilt Stormwind.

<a id="patch-bluemoon"></a>
**Re-enable the blue moon in the night sky** *(No. 60, Author: Robinsch)* 🟢 **[safe]**

Restores a removed legacy feature: the blue moon that used to be visible in
the night sky.

<a id="patch-notransparency"></a>
**No character transparency when zooming in** *(No. 61, Author: Alastor StrixEfuartus)* 🟢 **[safe]**

Your own character no longer becomes transparent when the camera is zoomed in
close. The patch removes the transparency assignment for the normal case; if
the character sits in a vehicle or is attached to another object, it can still
become transparent when zooming in (same as in the original patch).

<a id="patch-nofade"></a>
**No fade-out for NPCs with flag DO_NOT_FADE_IN** *(No. 62, Author: Alyst3r (0x539wowmod) (ported by St0ny))* 🟠 **[untested]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

When an NPC is removed (e.g. despawn), the client normally fades the model out
slowly. With the patch, NPCs for which the server sets the flag
`UNIT_FLAG2_DO_NOT_FADE_IN` (`0x20`) in `UNIT_FIELD_FLAGS_2` disappear instantly –
matching the missing fade-in. Players and NPCs without the flag behave as
before.

> [!IMPORTANT]
> Only takes effect if the server sets the flag. Without server support nothing
> changes.
>
> As with No. 4, the code lives in the free gap at the end of `.text`. Both fit
> in there together, the file size does not change.

<a id="patch-hdportraits"></a>
**HD unit frame portraits: render resolution 256 instead of 64 pixels** *(No. 63, Author: St0ny (original by Badgermilk0))* 🟢 **[safe]** 🟡 **[exe grows]**

The unit frames (player, target, party, bosses etc.) already show the 3D model
of the respective character in the unmodified client. So the patch creates
**no new portraits, no images and no animations** – it changes a single
number: the client renders this model into a texture for the frame, and that
texture is 64×64 pixels in the original. The patch raises exactly this render
resolution to 256×256 pixels, hard-wired via the call `Add-HdPortraits 256` in
`apply_patches.ps1`. Badgermilk0's original allows up to 4096×4096; 256 was
chosen here deliberately, because more only costs memory without looking
visibly better. Framing, tilt and zoom stay the same, the portraits just
become much sharper.
Only the 3D model path is raised; the icon/file path (fixed 64×64 images for
item/spell icons) deliberately stays at 64, because its copy loop would
otherwise read past the source.

> [!WARNING]
> This patch appends a new PE section `.hdp` to `Wow.exe` (generated 256px alpha
> mask + code caves + detour of the mask builder), the file grows by about
> 69 KB. This does not mean a certain ban, but it is a risk: some servers check the
> file size of `Wow.exe`.

> [!NOTE]
> **Together with awesome_wotlk (No. 27):** `AwesomeWotlkLib.dll` brings its own
> setting for the portrait resolution, the CVar `portraitResolution`. With
> No. 63 applied, this awesome_wotlk feature is blocked – the resolution of the
> exe patch (256) always wins, whatever `portraitResolution` is set to.

<a id="patch-iconsnap"></a>
**Pixel-exact icons in text (sharp instead of blurry)** *(No. 64, Author: tb (ported by St0ny))* 🟢 **[safe]** 🟡 **[exe grows]**

Texts can contain icons (`|T…|t`, e.g. raid target markers, currencies or quest
symbols in chat, tooltips and addons). The client computes their size and
position in pixels with decimals – with scaled fonts the icons then end up
between two pixels and become blurry or distorted by one pixel. The patch
rounds the height and width (at least 1 pixel) and the offset of the icons to
whole pixels, like the pixel snap from WotLK-Extensions (fork by tb),
which does it in its DLL. Icons at the font's original size stay unchanged.

> [!WARNING]
> The patch appends a small section (`.isnap`, 179 bytes) – `Wow.exe` gets
> larger. This does not mean a certain ban, but it is a risk: some servers check the
> file size.

<a id="patch-lights"></a>
**More lights: 8 instead of 4 point lights (groundwork for new shaders)** *(No. 65, Author: St0ny)* 🟠 **[untested]** 🟡 **[exe grows]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.
>
> **Untested ingame** – the function has not been checked in game yet, possibly buggy.

In the original, every model and every building gets the sun plus at most
the 4 nearest point lights (torches, spells, lights on models). The patch
makes the game collect the 8 nearest and pass them on to the graphics. It is
the exe groundwork for new shaders that show more lights.

How it works:
- The 4 nearest lights stay where they were; the game and the original
  shaders keep working with them unchanged. Lights 5–8 go to an extra list
  (320 KB of memory, allocated once when first needed).
- **Shader path (default):** for models and buildings the exe also sends
  lights 5–8 to the vertex shader registers c236–c246, in the same format the
  original uses for lights 1–4 in c17–c27. The original shaders do not read
  these registers – you only see a difference with new shaders.
- **Path without shaders** (`/console fixedFunction 1`, then restart): the
  graphics device gets 8 instead of 4 light slots. Models, buildings, ground
  and water are lit by the sun and up to 7 point lights. This lets you try
  the patch without new shaders; the game looks plainer overall in this mode
  (no pixel shaders).
- Fixes a bug of the original in the path without shaders along the way:
  with 4 lights, the nearest one of all was dropped.
- Code and data live in a section of their own (`.lght`, 0x590 bytes).

Register layout for shader authors (vertex shaders, models and buildings):

| Register | Content |
|---|---|
| c17–c20 / c236–c239 | color of light 1–4 / 5–8 (rgb, w = 1; free slot = 0) |
| c21–c24 / c240–c243 | position of light 1–4 / 5–8 in view space (xyz, w = 1) |
| c25 / c244 | attenuation 0 of light 1–4 / 5–8 (x = first … w = fourth light) |
| c26 / c245 | attenuation 1, same split |
| c27 / c246 | attenuation 2, same split |

> [!NOTE]
> Shader selection stays unchanged: from 4 lights on, the game uses the
> "4 lights" variants (in every `Diffuse_*.bls` the variants 9, 19, …, 89).
> Only these need the extra code for c236–c246; number and order of the
> variants stay the same. The extra lights are only sent if the graphics card
> has at least 247 vertex shader registers (every shader model 2 or 3 card
> has 256).

> [!NOTE]
> On the shader path, ground and water stay at 3 lights. They have shaders
> and a data path of their own; that follows in a later stage.

> [!NOTE]
> If all patches with a section of their own are active at the same time,
> there is no room left in the PE header for another section entry. Then the
> patcher extends the last appended section instead of adding a new one.

## Interface & comfort

<a id="patch-tracker"></a>
**Auto-sort quest tracker** *(No. 66)* 🟢 **[safe]**

Sets the CVar `trackerSorting` to 1 by default. Quests in the tracker are
sorted automatically.

<a id="patch-worldmap"></a>
**Advanced world map enabled by default** *(No. 67)* 🟢 **[safe]**

Sets the CVar `advancedWorldMap` to 1 by default. The advanced map view is
enabled from the start.

<a id="patch-castbars"></a>
**Cast bars on all frames** *(No. 68, Author: Kebabstorm)* 🟢 **[safe]**

Shows cast bars on all unit frames (party, arena, boss etc.), not just target
and focus, as well as on all default nameplates. Matches the behavior from
Cataclysm onwards.

<a id="patch-emblems"></a>
**Retail guild emblems: selection extended from 170 to 196** *(No. 69, Author: MacWarrior)* 🟠 **[untested online]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.

The client keeps the number of selectable tabard variants in a small table
(VA `0xA14908`, file offset `0x613108`): 170 emblems, 17 emblem colors,
6 borders, 17 border colors, 51 background colors. The tabard designer cycles
with "index modulo count", the random tabard picks "rand() times count" – both
read the value at runtime, and there is no second hard-coded 170 anywhere. The
patch raises the emblem count to retail's 196, which removes the limit
completely.

> [!WARNING]
> **Additional MPQ patch archive required.** This patch only raises the counter
> in the EXE, it does not ship any graphics. The 26 new emblems (index 170 to
> 195) have to be provided as a separate MPQ archive in the `Data` folder.
> Without it, the new slots in the tabard designer can be selected but stay
> empty.
>
> The matching archive is **Patch-G**: [Discord](https://discord.com/channels/407664041016688662/1541873346608889936)

The client builds the file names from the emblem index and color index, in
this order:

```
Textures\GuildEmblems\Emblem_<Index>_<Color>_TU_U   (upper half)
Textures\GuildEmblems\Emblem_<Index>_<Color>_TL_U   (lower half)
```

The texture loader appends the `.blp` extension. That is 17 colors × 2 halves
= 34 files per emblem, 884 files for all 26 new emblems. The archive name is
up to you (`patch-*.MPQ`), thanks to the patch "Allow extended MPQ names"
(No. 21).

<a id="patch-flash"></a>
**FlashWindow patch** *(No. 70, Author: Kebabstorm)* 🟢 **[safe]**

Makes the WoW window flash in the taskbar when a relevant event occurs while
the game is in the background. For this the Lua function `BNRemoveFriend`,
which has no function in 3.3.5a, is replaced by `FlashWindow()`, which addons
can call (Windows API `FlashWindow(hwnd, FALSE)`, exactly like the version in
`AwesomeWotlkLib.dll`).
**Requires** an addon that calls `FlashWindow()`, e.g. the
[Flash addon](https://github.com/noname08662/awesome_wotlk/tree/main/addons/Flash) from awesome_wotlk –
which additionally needs `IsWindowFocused()` from `AwesomeWotlkLib.dll`
(No. 27).

<a id="patch-charrandom"></a>
**Character creation: do not randomize the appearance automatically** *(No. 71, Author: Alyst3r (0x539wowmod))* 🟢 **[safe]**

When opening character creation (clicking "Create New Character") and when
changing race or gender, the client no longer randomizes face, skin, hair style
etc. automatically; you start with the default appearance. The randomize button
keeps working – it uses a separate path in the client.

<a id="patch-lootopen"></a>
**Loot window stays open while moving** *(No. 72, Author: tb (ported by St0ny))* 🟠 **[untested online]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.

In the original the loot window closes as soon as you walk, strafe or turn.
With the patch it stays open. The ten places in the movement handlers that
close the window are skipped (one byte each).

<a id="patch-showlevel"></a>
**Real level instead of "??" for enemies 10+ levels above you** *(No. 73, Author: tb (ported by St0ny))* 🟠 **[untested online]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.

If a hostile target is 10 or more levels above you, the client shows "??"
instead of the level (or a skull on the nameplate, `UnitLevel` returns -1).
With the patch, tooltip, nameplate and `UnitLevel` show the real level. Bosses
still show "??" – that check is kept; No. 74 removes it.

<a id="patch-showlevelboss"></a>
**Real level for bosses too instead of "??" (extension to No. 73)** *(No. 74, Author: St0ny)* 🟠 **[untested online]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.

Creatures marked as boss (a flag in the creature data, e.g. raid and dungeon
bosses) always show "??" in the original – in the tooltip, on the nameplate
(skull) and through `UnitLevel` (-1), no matter how high your own level is. The
patch removes these three boss checks, so the level the server sends for the
boss is shown. The "Boss" label in the tooltip and the elite icon on the
nameplate stay.

> [!NOTE]
> If a boss is 10 or more levels above you, the level check applies as well –
> No. 73 removes its "??". For all bosses, apply it together with No. 73; the
> patcher points it out if No. 73 is missing.

<a id="patch-holdrepeat"></a>
**Hold action buttons to repeat** *(No. 75, Author: tb (ported by St0ny))* 🔴 **[unsafe]** 🟡 **[exe grows]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

When you hold the key of an action bar binding (the main bar,
`ACTIONBUTTON1`–`12`, with page, stance and form bars), the client triggers the
action repeatedly – like the "Press and Hold Casting" option that retail WoW
has had since Dragonflight.

- The first repeat comes 500 ms after pressing at the earliest.
- It only repeats when the action is ready: no cooldown (including the global
  cooldown), no cast bar or channel running, no spell waiting for its target,
  and only 100 ms after it became ready again. After that at most every 100 ms.
- If the key has already repeated, releasing it does not trigger the action
  once more. A short press behaves like the original.
- If the WoW window loses focus (e.g. Alt+Tab), all held keys are forgotten.

This matches `actionButtonHoldRepeat = 2` (continuous) from WotLK-Extensions
(fork by tb), which does it in its DLL with adjustable timings. Here the
timings are fixed, and the code and its state live in a writable section of
their own (`.hrep`). Up to 8 keys can be held at the same time.

> [!WARNING]
> Servers with anti-cheat may treat this as automation (botting), and many
> servers forbid "one key press = several actions". In addition, the patch
> appends a section – `Wow.exe` gets larger (ban risk).

<a id="patch-bubblerange"></a>
**Increase the chat bubble range (original 25 yards)** *(No. 76, Author: St0ny)* 🟢 **[safe]**

The client shows chat bubbles (say, party, yell, NPC say and NPC yell) only for
speakers up to 25 yards away. If the server sends a yell from 100 yards, for
example, it only appears in the chat. The patch raises this limit; the patcher
asks for the range: 50 (suggestion), 100, 150, 200 or 0 = unlimited.

The client compares the squared distance with the constant 625.0 (= 25²) in
two places: when the message arrives (VA `0x7200CE`, otherwise no bubble is
created) and when the bubble is updated (VA `0x56C5E9`, otherwise it is
hidden). The footprints use the same constant, so it stays unchanged: the patch
only points the two chat bubble places to another constant that already exists
in the exe (2500, 10000, 22500, 40000 or the largest float value). That is why
there are only these fixed steps; the file size and the PE header stay
unchanged.

> [!NOTE]
> A bubble only appears if the server sends the message and the speaker is
> visible to you – the view distance is set by the server (often around 100
> yards). The server limits say to 25 yards anyway, nothing changes there.
> Party bubbles, however, also appear above party members further away.

## Window, mouse & camera

<a id="patch-window"></a>
**Windowed mode by default** *(No. 77, Author: St0ny)* 🟢 **[safe]**

Sets the CVar `gxWindow` to 1 by default. The game starts in windowed mode
instead of fullscreen.

> [!TIP]
> **No. 77 and No. 78 belong together:** No. 77 enables windowed mode, No. 78
> maximizes the window.
> - **Both selected:** WoW starts as a maximized window covering the whole
>   screen.
> - **Only No. 77:** WoW starts as a small window in the middle of the desktop.
> - **Only No. 78:** no effect, WoW starts in fullscreen. The option "Maximize
>   window" is active, but greyed out.

<a id="patch-maximize"></a>
**Maximized window by default** *(No. 78, Author: St0ny)* 🟢 **[safe]**

Sets the CVar `gxMaximize` to 1 by default. The window is maximized on start.

> [!TIP]
> **No. 77 and No. 78 belong together:** No. 77 enables windowed mode, No. 78
> maximizes the window.
> - **Both selected:** WoW starts as a maximized window covering the whole
>   screen.
> - **Only No. 77:** WoW starts as a small window in the middle of the desktop.
> - **Only No. 78:** no effect, WoW starts in fullscreen. The option "Maximize
>   window" is active, but greyed out.

<a id="patch-windowfix"></a>
**No black screen when switching to windowed mode** *(No. 79, Author: Robinsch)* 🟢 **[safe]**

Switching to windowed mode while in-game no longer results in a black
screen. Technically the callback of the CVar `DesktopGamma` always takes the
game-gamma path; the desktop-gamma path and with it the CVar `DesktopGamma`
have no effect.

<a id="patch-mouse"></a>
**Mouse flicker / camera jump fix** *(No. 80, Author: Robinsch)* 🟢 **[safe]**

A larger patch (4 parts) that fixes problems with mice using a high polling
rate. Prevents cursor flicker and uncontrolled camera movement.

<a id="patch-camera"></a>
**CameraReforged [BETA]: camera height and zoom limits** *(No. 81, Author: Stormhand (fixed by St0ny))* 🟠 **[untested online]** 🟡 **[exe grows]**

> [!WARNING]
> **Untested online** – not tested on public servers, possible ban risk. Careful, it may get you kicked or banned.

Port of [CameraReforged](https://github.com/Zendevve/CameraReforged) by
**Stormhand** into this patcher, so everything
runs in one pass – included with his explicit permission ("Of course! Take
whatever you need. I appreciate your work."). The port and its adjustments were
made by St0ny. The client gets two brand-new CVars and new default values for
two existing ones.

> [!WARNING]
> **BETA** – this patch does not work 100% yet, more work is going into it.
> That is why it is deselected by default. The shoulder offset
> (`test_cameraOverShoulder`) currently has no effect: the four read sites the
> original redirects for it do not belong to the camera but to the chat frame
> (display time of messages). They are left untouched here.

| CVar                      | Blizzard  | here  | Range         |
|---------------------------|-----------|-------|---------------|
| `test_cameraHeight`       | (missing) | 0.50  | 0.0 to 3.0    |
| `test_cameraOverShoulder` | (missing) | 0.00  | -2.0 to 2.0 (no effect) |
| `cameraDistanceMaxFactor` | 1.0       | 2.60  | 1.0 to 5.0    |
| `cameraDistanceMoveSpeed` | 8.33      | 20.00 | 1.0 to 100.0  |

- `test_cameraHeight` raises the point the camera aims at. The client puts it
  at chest height; 0.5 yards brings it to head height.
- `test_cameraOverShoulder` is meant to shift the camera sideways, negative
  values to the left – currently without effect (see above).
- `cameraDistanceMaxFactor` is the factor by which you can zoom out beyond the
  normal limit, `cameraDistanceMoveSpeed` the zoom speed.

In 3.3.5a both new CVars were previously only available through
`ConsoleXP.dll` plus an injector – the patch registers them directly in the
EXE. All four are reachable via the console in-game and take effect
immediately, so they also work from macros and addons such as DynamicCam, e.g.
`/console test_cameraHeight 0.8`. They are registered with flag `0x10` and
saved to `Config.wtf`, so changes survive a restart. The default values can be
changed in the call
`Add-CameraReforged -Height 0.5 -Shoulder 0.0 -MaxFactor 2.6 -ZoomSpeed 20.0`
in `apply_patches.ps1`; values outside the ranges are rejected.

<details>
<summary><b>Background: how the patch is wired in</b></summary>

The patch appends its own section `.camr` to the EXE (about +1 KB,
read/write/execute) with code and data. It is wired up via a detour on
`CVars_Initialize` (where the new CVars are registered), a detour on the camera
focus path (where the height is added) and two redirected default-value
pointers.

Two deviations from the original tool, both necessary:

1. *Own section instead of `.rdata` padding.* The original puts code and data
   into the `.rdata` padding and makes that section executable – exactly that
   makes this client abort on start with runtime error R6002.
2. *Pointer instead of callback.* The original's callback is a validation
   callback that runs before the new value is stored, so the value lags behind
   every change. Here the init hook stores the pointer to the CVar object and
   the camera hook reads the value fresh every frame.

Do not run `CameraReforged.exe` in addition: it brings back the R6002 crash and
overwrites the table of the slider patch.

</details>

> [!WARNING]
> Like the HD portraits, this patch appends a section of its own (about +1 KB),
> which makes `Wow.exe` larger. This does not mean a certain ban, but it is a risk: some
> servers check the file size of `Wow.exe`.

## Sound

<a id="patch-sound"></a>
**Optimize sound settings** *(No. 82, Author: St0ny)* 🟢 **[safe]**

Includes the following changes:

- Sound channel hardware limit raised to 126
- `Sound_OutputQuality` set to maximum (2)
- `Sound_NumChannels` raised from 32 to 64
- `Sound_EnableReverb` enabled (reverb effect)
- `Sound_EnableHardware` enabled (hardware audio acceleration)

The channel limit of 126 is hard-coded in the initialisation code; the default
of 64 for `Sound_NumChannels` only applies at the second place where the client
reads the CVar.

> [!IMPORTANT]
> **OpenAL** is required for these settings to take effect at all, e.g.
> [OpenAL Soft](https://github.com/kcat/openal-soft).

## Client info: version, build, title, date, icon

These five patches by MacWarrior (ported from his Python scripts
`edit_version.py`, `edit_revision.py`, `edit_title.py`, `edit_date.py` and
`edit_icon.py`) change how the client identifies itself. When selected, **the
patcher asks for the desired values after the selection**. A suggestion is
shown in square brackets, ENTER accepts it. Invalid input is rejected with a
message and asked for again, and all values are checked before anything is
written. The patcher remembers the values in `patcher_selection.ini`
(`value.<Id>=…`); with `-Unattended` the remembered values are used, otherwise
the original values – exceptions: build date (current time) and icon (the
patcher aborts), see No. 86 and 87. If a patch is already in `Wow.exe`, its
current value is the suggestion. When asking, it is also shown after the patch
name (`-> suggestion: …`, or `-> current: …` for an already applied patch).

> [!NOTE]
> Servers may check the client version or build number, so a changed value has
> to match the server.

<a id="patch-clientversion"></a>
**Change client version (original 3.3.5)** *(No. 83, Author: MacWarrior)* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Sets a new version in the format `x.y.z` (e.g. `3.3.6` or `3.3.123`, at most 7
characters). Changes the version the client shows in-game, the FileVersion and
ProductVersion (`Version x.y`) of the version resource and `VS_FIXEDFILEINFO`.
The build number in `VS_FIXEDFILEINFO` is kept; the FileVersion text
(`3, 3, 5, 12340`) becomes the plain version (`3.3.6`). Major and minor version
together must fit into the ProductVersion field (e.g. `3.3`).

<a id="patch-clientbuild"></a>
**Change build number (original 12340)** *(No. 84, Author: MacWarrior)* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Sets a new build number (6142 to 65535, original `12340`): the internal build
number, the visible build number and the fourth part of the FileVersion in
`VS_FIXEDFILEINFO`. The texts `3, 3, 5, 12340` (FileVersion text) and
`WoW [Release] Build 12340 (…)` stay unchanged. The
patcher does not allow builds up to 6141: servers like AzerothCore or
TrinityCore then treat the client as a Classic client (pre-BC) and use a
different login protocol – a 3.3.5 client can no longer get onto the server.

> [!TIP]
> **AzerothCore:** the authserver only accepts builds listed in the `build_info`
> table of the auth database. For a build of your own, e.g. `12341`:
>
> ```sql
> INSERT INTO build_info (majorVersion, minorVersion, bugfixVersion, hotfixVersion, build, winChecksumSeed, macChecksumSeed)
> VALUES (3, 3, 5, 'a', 12341, NULL, NULL);
> UPDATE realmlist SET gamebuild = 12341 WHERE id = 1;
> ```
>
> Leave `winChecksumSeed` empty (it is only checked with `StrictVersionCheck = 1`
> in `authserver.conf` and would not match a patched exe anyway).
> Major/minor/bugfix are only displayed in the realm list. Restart the
> authserver afterwards – it reads `build_info` only at startup. A realm only
> accepts the build in `realmlist.gamebuild`; players with an older client see
> it as offline.

<a id="patch-clienttitle"></a>
**Change program title (file properties and window title)** *(No. 85, Author: MacWarrior (fixed by St0ny))* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Sets FileDescription, InternalName and ProductName of the version resource,
i.e. what Windows shows in the file properties and the Task Manager. At most 17
characters, ASCII only.

The patch also changes the title of the game window: WoW creates its window
with the text "World of Warcraft" (file offset `0x5E0288`) and then sets the
title twice more (calls at VA `0x76A119` and `0x76B204`). The patch writes the
custom title to the first place and disables the two calls so that it stays.

> [!NOTE]
> The text at `0x5E0288` is also used elsewhere in the client, e.g. probably
> as the title of error messages – the custom title appears there as well.

<a id="patch-clientdate"></a>
**Change build date (original Jun 24 2010)** *(No. 86, Author: St0ny (original by MacWarrior))* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Sets the build date (original `Jun 24 2010`) at all three places in the EXE and
the year in the copyright notice, plus the time. The time is stored in two
places: in the build text `WoW [Release] Build 12340 (Jun 24 2010 23:54:57)` and
as the timestamp in the program header, which analysis tools show as the build
time of `Wow.exe` (original 2010-06-25 06:55:58 UTC). Date and time are taken
as local time of the computer you patch on.

Input as `YYYY-MM-DD HH:MM:SS`, optionally followed by `FR` for French month
names (e.g. `2026-09-28 14:30:15 FR` → `Sep 28 2026 14:30:15`). Without seconds
(`14:30`) the patcher uses `00`. The suggestion in brackets is **"time of
confirming with Y"** (with `FR` if you chose it last time): if you accept it
with ENTER, the patcher uses the computer's date and time at the moment you
confirm patching with `Y`. With `-Unattended` the remembered value is used, or
the time of patching if nothing is remembered. If the patch is already applied,
the current date and time of `Wow.exe` are suggested.

<a id="patch-clienticon"></a>
**Change program icon (icon of Wow.exe)** *(No. 87, Author: St0ny (original by MacWarrior))* 🔴 **[unsafe]**

> [!CAUTION]
> **Unsafe** – ban risk, can lead to a ban on many servers. Only use it on servers that allow it.

Replaces the icon Windows shows for `Wow.exe` (Explorer, taskbar, shortcuts).
The patcher asks for the path of an `.ico` or `.png` file, absolute or
relative to the WoW folder. From that file it builds the four sizes stored in
`Wow.exe` (48, 32, 24 and 16 pixels, each 32-bit with alpha channel): if a size
is present in the ICO it is used as is, otherwise the next larger image is
downscaled by area averaging (or, as a last resort, the largest one is
upscaled). A PNG provides all four sizes by scaling. Transparency is kept.

MacWarrior's `edit_icon.py` swaps the resources via the Windows API, which
rewrites the `.rsrc` section. Here only the image data of the eight existing
icon bitmaps (four sizes in two language variants) is overwritten in place –
same size, same bit depth, same space. Resource directory, offsets and file
size stay unchanged, and the patch can be removed like any other. The other
patches are not shifted by it, not even those that append a section: they land
after the end of the file, while the icon images lie before it. Before writing,
the patcher checks in the resource directory that each of the eight places
really holds an icon image of exactly this size. If not, it aborts without
writing anything. The patcher reads ICO images in BMP form (1, 4, 8, 16, 24
or 32 bit) and PNG (not
interlaced) by itself, without extra modules. The path is remembered in
`patcher_selection.ini`; with `-Unattended` it has to be there, otherwise the
patcher aborts with a message.

> [!NOTE]
> If Explorer still shows the old icon afterwards, that is the Windows icon
> cache: rename `Wow.exe` briefly or copy it to another folder, recreate
> shortcuts or restart Explorer. The icon in the game itself (window title)
> comes from these resources as well.

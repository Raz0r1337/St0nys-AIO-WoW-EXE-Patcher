import re,sys
def rep(s,o,n,p):
    c=s.count(o)
    if c!=1: sys.exit(f'{p}: count {c} for {o[:100]!r}')
    return s.replace(o,n)
def row(s,num,new,p):
    s2,k=re.subn(r'(?m)^\| %d +\|.*$'%num,lambda m_: new,s)
    if k!=1: sys.exit(f'{p}: row {num} count {k}')
    return s2
DISC='https://discord.com/channels/858041817043042364/1515439916878663701'
p='README.en.md'; s=open(p,encoding='utf-8',newline='').read()
s=rep(s,"Disables the Warden scan DLL mechanism in the client.\n",
"""Prevents loading of `Scan.dll`, which the login server can push with its
"Scan" command (a check module of the login server, independent of Warden):
`.\\Scan.dll` and `.\\Scan.dll.new` become `.\\||an.dll` – `|` is not allowed in
file names, so loading is guaranteed to fail.
""",p)
s=rep(s,"**Disable AFK timer idle check** *(No. 13, off by default, Author: St0ny)*",
        "**Prevent the idle kick after character auto-login** *(No. 13, off by default, Author: St0ny)*",p)
s=rep(s,"""Disables the idle login check but keeps the automatic AFK disconnect timer
active. Also prevents the CharAutoLogin bug.
""","""After an auto-login without any keyboard or mouse input the timestamp of the
last input is still 0 – the client immediately considers the player idle and
kicks them (CharAutoLogin bug). The patch sets the timestamp to "now" on the
first pass if it is still empty and removes a fatal-error check that can
trigger there. The actual timers stay unchanged: AFK status after 5 minutes,
logout after 30 minutes without input.
""",p)
s=row(s,13,"| 13 | Prevent the idle kick after character auto-login *(required for character auto-login; AFK and idle timers stay active, [Discord](%s))* | St0ny | – | – |"%DISC,p)
s=rep(s,"""Allows modifying the login and character selection screens with your own
XML/Lua files (glue screen modding).
""","""Allows modifying the login and character selection screens with your own
XML/Lua files (glue screen modding): the signature check of the interface files
always reports "valid", and local `Interface\\GlueXML` and `Interface\\FrameXML`
folders are no longer renamed to `*.old`.

> [!NOTE]
> Side effect that every version of this patch has: addons without a signature
> file are treated as "secure" (like Blizzard code) as well and may call
> protected functions – similar in effect to the LUA unlock (No. 18). Servers
> with anti-cheat may judge it the same way.

The widespread version (Alastor/Kebabstorm) continues with uninitialised
variables when the signature file is missing and frees a dangling pointer on
the way (undefined behaviour). Here the error exit returns "valid" directly
instead – same effect, without the wild memory access.
""",p)
s=rep(s,"""Allows loading MPQ archives without a valid signature. Required for custom
content on private servers.
""","""The signature check for MPQ archives always reports "valid". The client only
checks archives sent by the server with it: `wow-patch.mpq` (client patch from
the server) and `Cache\\Survey.mpq` (hardware survey). The regular `Data\\*.MPQ`
are loaded without any signature check anyway – so this patch is not needed for
your own patch MPQs. Together with No. 8 and No. 9 it has no effect any more,
because neither path runs then.
""",p)
s=rep(s,"""Addons and macros may call protected functions, e.g. `CastSpellByName`,
`CastSpellByID`, `TargetUnit`, `FocusUnit`, `InteractUnit`, movement functions
or `ReloadUI`. `AttackTarget` still prints an error.
""","""Addons and macros may call protected functions: movement functions
(`MoveForwardStart`, `TurnLeftStart`, …), `CastSpellByName`, `CastSpell`,
`UseAction`, `PetAttack`, `RunMacro`/`RunMacroText` and the GM ticket
functions. Not unlocked, because they have their own checks in the code:
`TargetUnit`, `FocusUnit`, `InteractUnit`, `ReloadUI`; `AttackTarget` still
prints an error.
""",p)
s=rep(s,"""Belongs together with the 4GB patch (No. 1): if that one is not selected, the
patcher points it out.
""","""Belongs together with the 4GB patch (No. 1): if that one is not selected, the
patcher points it out.

The loader sits at the start of the client's main fiber (right before
`WinMain`) and overwrites the beginning of the Scan.dll start function for
that; the Lua function `ScanDLLStart` becomes a no-op and the Scan.dll flag is
set to "passed". As a side effect the patch disables the Scan.dll mechanism
(like No. 7). If the DLL is missing, WoW simply starts normally.
""",p)
s=rep(s,"**Level 101+ fix (druid base stats and barber chair)** *(No. 31, off by default, Author: Alastor StrixEfuartus)*",
        "**Level 101+ fix (game tables, barber chair, base stats)** *(No. 31, off by default, Author: Alastor StrixEfuartus / St0ny)*",p)
s=rep(s,"""Druids at level 101 and above can view their base stats again, and the
barber chair works for all characters at level 101 and above.
**Requires** the patch "Allow custom GlueXML" (No. 14). In the source it is
called "Disable XML SIG MD5", hence the note "Use XML MD5" there.
""","""The client's game tables (`gtCombatRatings`, `gtBarberShopCostBase`,
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

**Requires** the patch "Allow custom GlueXML" (No. 14) according to the
source. There it is called "Disable XML SIG MD5", hence the note "Use XML MD5".
""",p)
s=row(s,31,"| 31 | Level 101+ fix (game tables, barber chair, base stats) | Alastor StrixEfuartus / St0ny | – | ✅ |",p)
s=rep(s,"**Unlimited race/class combinations** *(No. 32, off by default, Author: Alastor StrixEfuartus / Robinsch)*",
        "**Character creation: more than 10 classes (random class)** *(No. 32, off by default, Author: Alastor StrixEfuartus / Robinsch)*",p)
s=rep(s,"""Character creation allows every race with every class. The server has to
support this as well.
""","""The random class selection in character creation collects the allowed classes
in an array with 10 slots. With custom classes (`ChrClasses.dbc` with more than
10 entries) it would overflow; the patch enlarges it to 30 slots. Which race may
pick which class is still checked by the server – this patch does nothing more.
""",p)
s=row(s,32,"| 32 | Character creation: more than 10 classes (random class) *(for custom classes; server must support it)* | Alastor StrixEfuartus / Robinsch | – | – |",p)
s=rep(s,"""height", No. 37). The separate second jump height of 0x539wowmod's double jump
is not included.
""","""height", No. 37). The separate second jump height of 0x539wowmod's double jump
is not included. The counter is only reset by the next jump from the ground,
not on landing: if you land after a jump and then walk off a ledge, you have the
chosen number of jumps in the air again.
""",p)
s=rep(s,"""Removes the upper limit of the CVar `environmentDetail` entirely. Originally
the value is clamped to the range 0.5 to 1.5; the patch disables the upper
clamp so arbitrarily high values are passed through.
""","""Removes the upper limit of the CVar `environmentDetail` entirely. Originally
the value is clamped to the range 0.5 to 1.5; the patch replaces the clamped
value with the raw value at the shared exit of the check – so the lower limit
0.5 goes away as well, any value is passed through (sensible values start at
0.5).
""",p)
s=rep(s,"""Raises the occluder threshold for Stormwind so buildings and objects are not
hidden incorrectly. Fixes graphical glitches on custom servers with a rebuilt
Stormwind.
""","""Disables the occluders (view blockers) for Stormwind that are hard-coded in the
client: the map key of the table entry for the Eastern Kingdoms is set to
99999, so it no longer matches any map. This way no buildings and objects are
hidden incorrectly on custom servers with a rebuilt Stormwind.
""",p)
s=rep(s,"""Your own character no longer becomes transparent when the camera is zoomed in
close.
""","""Your own character no longer becomes transparent when the camera is zoomed in
close. The patch removes the transparency assignment for the normal case; if
the character sits in a vehicle or is attached to another object, it can still
become transparent when zooming in (same as in the original patch).
""",p)
s=rep(s,"""FlashWindow: makes the WoW window flash in the taskbar when a relevant event
occurs while the game is in the background. The function can be called from
addons.
**Requires** the [FlashWindow addon](https://github.com/noname08662/awesome_wotlk/tree/main/addons/Flash) from awesome_wotlk.
""","""Makes the WoW window flash in the taskbar when a relevant event occurs while
the game is in the background. For this the Lua function `BNRemoveFriend`,
which has no function in 3.3.5a, is replaced by `FlashWindow()`, which addons
can call (Windows API `FlashWindow(hwnd, FALSE)`, exactly like the version in
`AwesomeWotlkLib.dll`).
**Requires** an addon that calls `FlashWindow()`, e.g. the
[Flash addon](https://github.com/noname08662/awesome_wotlk/tree/main/addons/Flash) from awesome_wotlk –
which additionally needs `IsWindowFocused()` from `AwesomeWotlkLib.dll`
(No. 21).
""",p)
s=rep(s,"""Switching to windowed mode while in-game no longer results in a black
screen.
""","""Switching to windowed mode while in-game no longer results in a black
screen. Technically the callback of the CVar `DesktopGamma` always takes the
game-gamma path; the desktop-gamma path and with it the CVar `DesktopGamma`
have no effect.
""",p)
s=rep(s,"**CameraReforged [BETA]: camera height, shoulder offset, zoom limits** *(No. 64, off by default, Author: Stormhand / St0ny)*",
        "**CameraReforged [BETA]: camera height and zoom limits** *(No. 64, off by default, Author: Stormhand / St0ny)*",p)
s=row(s,64,"| 64 | CameraReforged [BETA]: camera height and zoom limits *(shoulder offset has no effect yet; exe grows – ban risk)* | Stormhand / St0ny | – | – |",p)
s=rep(s,"""> **BETA** – this patch does not work 100% yet, more work is going into it.
> That is why it is deselected by default.
""","""> **BETA** – this patch does not work 100% yet, more work is going into it.
> That is why it is deselected by default. The shoulder offset
> (`test_cameraOverShoulder`) currently has no effect: the four read sites the
> original redirects for it do not belong to the camera but to the chat frame
> (display time of messages). They are left untouched here.
""",p)
s=rep(s,"| `test_cameraOverShoulder` | (missing) | 0.00  | -2.0 to 2.0   |",
        "| `test_cameraOverShoulder` | (missing) | 0.00  | -2.0 to 2.0 (no effect) |",p)
s=rep(s,"""- `test_cameraOverShoulder` shifts the camera sideways, negative values to the
  left. 0 keeps it centered, anything else gives an over-the-shoulder view.
""","""- `test_cameraOverShoulder` is meant to shift the camera sideways, negative
  values to the left – currently without effect (see above).
""",p)
s=rep(s,"""focus path (where the height is added), two redirected default-value pointers
and four redirected read sites for the shoulder offset.
""","""focus path (where the height is added) and two redirected default-value
pointers.
""",p)
s=rep(s,"""- `Sound_EnableHardware` enabled (hardware audio acceleration)
""","""- `Sound_EnableHardware` enabled (hardware audio acceleration)

The channel limit of 126 is hard-coded in the initialisation code; the default
of 64 for `Sound_NumChannels` only applies at the second place where the client
reads the CVar.
""",p)
s=rep(s,"""ProductVersion (`Version x.y`) of the version resource and `VS_FIXEDFILEINFO`.
The build number is kept. Major and minor version together must fit into the
ProductVersion field (e.g. `3.3`).
""","""ProductVersion (`Version x.y`) of the version resource and `VS_FIXEDFILEINFO`.
The build number in `VS_FIXEDFILEINFO` is kept; the FileVersion text
(`3, 3, 5, 12340`) becomes the plain version (`3.3.6`). Major and minor version
together must fit into the ProductVersion field (e.g. `3.3`).
""",p)
s=rep(s,"""Sets a new build number (6142 to 65535, original `12340`): the internal build
number, the visible build number and the fourth part of the FileVersion. The
""","""Sets a new build number (6142 to 65535, original `12340`): the internal build
number, the visible build number and the fourth part of the FileVersion in
`VS_FIXEDFILEINFO`. The texts `3, 3, 5, 12340` (FileVersion text) and
`WoW [Release] Build 12340 (…)` stay unchanged. The
""",p)
s=rep(s,"## Acknowledgements\n","""## Removed patches

Two patches from Robinsch's collection that earlier versions of this patcher
contained were removed after the code review – their offsets do not match this
`Wow.exe`:

- **Fix "ghost" attack when NPCs evade from combat** (`0x355BF`: `E8` → `EB`).
  The byte turns a `call` in a string helper function (VA `0x4361BF`) into a
  jump back by 5 bytes – an endless loop that pushes 4 bytes onto the stack per
  iteration until the client crashes. The function is rarely called, which is
  why this went unnoticed in game.
- **Fix naked character bug** (`0x1DDC5D`: `00` → `EB`). The byte is the
  argument of a `push 0` in the Lua function `GetTradeSkillTools`
  (VA `0x5DE85C`) and turns it into `push -21` – it only corrupts a parameter of
  the profession tool check and has nothing to do with `SPELL_AURA_X_RAY`.

A `Wow.exe` that was still created with these two patches is no longer
recognized by the patcher without `patcher_state.ini`: copy `Wow.exe.ORI` back
and patch again.

## Acknowledgements
""",p)
open(p,'w',encoding='utf-8',newline='').write(s); print('en ok')

# St0nys-AIO-WoW-EXE-Patcher

[🇩🇪 Deutsch](README.de.md) | 🇬🇧 English

An all-in-one (AIO) patcher for the `Wow.exe` of **World of Warcraft 3.3.5a
(build 12340)**. It applies bug fixes, performance optimizations, extended view
distances, improved sound settings and a few quality-of-life features directly
to the executable – in a single pass, without extra tools or DLL injectors.

On start you choose the **language** (Deutsch / English) and then pick
**which patches** to apply from a menu. Applied patches can be **deselected or
extended** at any time later – all the way back to the original `Wow.exe`.

> [!IMPORTANT]
> This repository does **not** contain a `Wow.exe` or any other Blizzard files.
> You need your own unmodified `Wow.exe` 3.3.5a (12340).

> [!WARNING]
> **Use at your own risk.** Patches rated safe (🟢) have been tested in game and
> should be harmless on public servers as well – but there is no 100 %
> guarantee: what is detected and tolerated on a server is up to its operator
> and may change from time to time. All other patches carry a uniform warning in the
> overview and in the patcher (see [Notes](#notes)). If in doubt, check the
> rules of your server before using a patched `Wow.exe` there. The patcher
> also shows this note on every start.

---

## Contents

- [Requirements](#requirements)
- [Usage on Windows](#usage-on-windows)
  - [On Linux](#on-linux)
  - [On a Mac](#on-a-mac)
- [Workflow](#workflow)
- [Patch selection](#patch-selection)
- [Changing or removing patches](#changing-or-removing-patches)
- [Parameters for unattended use](#parameters-for-unattended-use)
- [Files](#files)
- [Patch overview](#patch-overview)
- [Patch descriptions](#patch-descriptions)
- [Notes](#notes)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## Requirements

- Windows with PowerShell (Windows PowerShell 5.1 ships with Windows 10 and later),
  Linux or Mac with PowerShell 7 – see [On Linux](#on-linux) and
  [On a Mac](#on-a-mac)
- An **original, unmodified** `Wow.exe` 3.3.5a, build 12340 with
  SHA256 `AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8`
  (only on the first start; after that a `Wow.exe` patched with this patcher is
  enough)

## Usage on Windows

1. Download the ZIP from the [latest release](https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/releases/latest) and unpack it. It
   contains the folder `St0nys-AIO-WoW-EXE-Patcher`.
2. Copy your original `Wow.exe` from your WoW folder into that folder.
3. Double-click `patcher-win.bat`.
4. Choose the language (first start only), select patches, confirm.
5. If WoW is running, close it and copy the patched `Wow.exe` back into your
   WoW folder, replacing the old one.

To **change or remove** patches just run `patcher-win.bat` in the patcher folder
again and copy `Wow.exe` back into your WoW folder afterwards, see
[Changing or removing patches](#changing-or-removing-patches).

> [!NOTE]
> Windows will probably warn about an unsigned, potentially harmful app when
> you start the patched `Wow.exe`. This happens with every modified `Wow.exe`:
> any change invalidates Blizzard's digital signature, and a new signature that
> Windows accepts cannot be created for a modified Blizzard file. It still
> starts, e.g. via "More info" → "Run anyway". More on this under
> [Notes](#notes).

### On Linux

The patcher is written for Windows, but it also runs on Linux directly with
PowerShell 7 (`pwsh`) – no Wine needed. Tested on Ubuntu 24.04.

1. Install PowerShell 7, e.g. for [Ubuntu](https://learn.microsoft.com/powershell/scripting/install/install-ubuntu),
   [Debian](https://learn.microsoft.com/powershell/scripting/install/install-debian) or [RHEL](https://learn.microsoft.com/powershell/scripting/install/install-rhel).
   PowerShell is not in the default package sources; the linked
   instructions therefore first add Microsoft's package source, otherwise
   e.g. `apt` will not find the `powershell` package.
   Other distributions can use Snap or an archive to unpack
   ([instructions](https://learn.microsoft.com/powershell/scripting/install/install-other-linux)), Arch the package from the AUR.
2. Unpack the ZIP and copy your original `Wow.exe` into the folder
   `St0nys-AIO-WoW-EXE-Patcher` – just like on Windows. How `Wow.exe` is
   spelled (`WoW.exe`, `wow.exe` …) does not matter.
3. In a terminal in that folder, run `./patcher-lin.sh`. If that does not start
   (e.g. because unpacking lost the execute permission), use `sh patcher-lin.sh`.
4. If WoW is running, close it and copy the patched `Wow.exe` back into your
   WoW folder.

Everything else works as on Windows: wherever this guide says `patcher-win.bat`,
use `./patcher-lin.sh`.

### On a Mac

> [!NOTE]
> I don't have a Mac and cannot test the patcher there. The steps should work
> because PowerShell 7 is also available for macOS – but there is no
> guarantee. If you try it, I'd be glad about feedback as an
> [issue](https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/issues).

The patcher modifies the Windows `Wow.exe`, it cannot patch the Mac client
itself. On a Mac that is the `Wow.exe` you run e.g. with CrossOver or Wine.

1. Install PowerShell 7, e.g. with [Homebrew](https://brew.sh):
   `brew install --cask powershell`. Microsoft also offers an installer
   package ([instructions](https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-macos)).
2. Unpack the ZIP and copy your original `Wow.exe` into the folder
   `St0nys-AIO-WoW-EXE-Patcher` – just like on Windows.
3. Open Terminal and change to that folder, e.g. type `cd ` and drag the
   folder into the Terminal window. Then run `sh patcher-lin.sh` – the Linux
   start file should work on a Mac as well.
4. If WoW is running, close it and copy the patched `Wow.exe` back into your
   WoW folder.

Everything else works as on Windows: wherever this guide says
`patcher-win.bat`, use `sh patcher-lin.sh`.

## Workflow

1. The ASCII banner is shown.
2. **Language selection:** `1` = Deutsch, `2` = English. First start only – after
   that the language is remembered and can be switched with `L` in the menu.
3. Welcome message, press ENTER to start.
4. Check that a `Wow.exe` exists in the folder.
5. Checking `Wow.exe`: on the first start it must be original and unmodified
   (SHA256). After that the patcher recognizes a `Wow.exe` it patched itself
   by the watermark and determines which patches are in it. Anything else
   aborts.
6. **Patch selection** menu (see below). Your selection from last time is
   preselected, or for a patched `Wow.exe` the patches currently in it.
7. For patches with their own value (jump height, double jump, client info) the
   patcher asks for the values; then it saves the selection.
8. Summary of the selected patches (for a patched `Wow.exe`: what is added and
   what is removed), notes (missing or redundant companion patches, warnings)
   and a confirmation prompt (Y/N).
9. Backup: on the first patch run the original is saved as `Wow.exe.ORI`, on
   every later run the previous `Wow.exe` is saved as `Wow.exe.BAK`.
10. All selected patches are applied in memory (with progress output) and
    `Wow.exe` is written back **once**. If anything fails, `Wow.exe` stays
    untouched.
11. The patcher remembers the hash of the new `Wow.exe` together with the
    original bytes in `patcher_state.ini` (for a faster next start) and shows a
    final message.

## Patch selection

The menu lists every patch with a number. `[X]` = will be applied,
`[ ]` = will be skipped. The menu is grouped into the same categories as the
[patch overview](#patch-overview). On the first start the
**preset "Reforged"** is preselected (see the "Reforged" column in the
overview), after that the saved selection or the patches currently in
`Wow.exe`. `B` loads the preset **"Billy's_Wow.exe"** (column "Billy"), `S` the
preset **"St0nys_Wow.exe"** (column "St0ny").
Patches that need something additional say so in parentheses
after their name, with the link right below.

| Input              | Effect                                     |
|--------------------|--------------------------------------------|
| `5`                | toggle patch 5                             |
| `3 7 12` / `3,7,12` | toggle several patches                    |
| `10-15`            | toggle a range                             |
| `A`                | all patches on                             |
| `N`                | all patches off (patched `Wow.exe` + ENTER: restore the original) |
| `L`                | switch language (Deutsch ↔ English)        |
| `R`                | load preset "Reforged" (= default) (**Safe** – official preset of [Project Reforged](https://projectreforged.github.io/wotlk/)) |
| `B`                | load preset "Billy's_Wow.exe" (**Safe** – based on Billy's proven exe) |
| `S`                | load preset "St0nys_Wow.exe" (**Not safe**, use only on your own servers) |
| `Q`                | quit, `Wow.exe` stays unmodified           |
| `ENTER`            | accept the selection and continue          |

Before the confirmation prompt the patcher shows **notes** – nothing is blocked:
when a companion patch is missing (e.g. the extended slider maximums need the
CVar unlocks), when one patch makes another unnecessary (disabling Warden
completely replaces the RCE fix) and when selected patches carry a warning –
red for ban risk, orange for patches that are still untested on public
servers or in game, and yellow for a larger `Wow.exe` (see [Notes](#notes)).

### The selection is remembered

As soon as you accept the selection with ENTER, the patcher saves it to
`patcher_selection.ini` next to the script. On the next start exactly this
selection is preselected again – even if you cancelled at the confirmation
prompt.

- The selection is stored per patch (by an internal ID), not by number. If a
  newer version adds patches, your selection stays correct and the new patches
  start with their default setting.
- The file is plain text (`laa=1`, `cache=0`, …) and can also be edited by
  hand. It also holds the entered values of the value patches – client info,
  jump height, double jump (`value.clientversion=3.3.6` etc.).
- The language is remembered there as well (`language=de` or `en`).
- **Reset:** press `R` in the menu or delete `patcher_selection.ini` – then
  the preset "Reforged" applies again (deleting the file also forgets the
  language and the remembered values, they are asked for again).

The preset "Reforged" (key `R`) is the official preset of the
[Project Reforged](https://projectreforged.github.io/wotlk/) project, put
together by Stormhand, and the default selection. It contains patches
rated safe (🟢), all tested by Stormhand for several hours on Warmane – **the
preset is safe** and can be used on public servers as well. Three of them
(No. 9, 65 and 66) make `Wow.exe` larger; that was no problem on Warmane, but
other servers may check the file size. On top of that comes the Lexara loader
(No. 30) for Stormhand's HD fonts. The patch itself is safe, but `Lexara.dll`
may be detected or blocked on public servers; without `Lexara.dll` in the WoW
folder it does nothing. The "Reforged" column in the
[patch overview](#patch-overview) shows which patches belong to it; in the
script the list is `$PRESET_REFORGED`.

The preset "Billy's_Wow.exe" (key `B`) is Billy Hoyle's patch set. It is
defined in `apply_patches.ps1`: every patch has an entry
`On = $true` (in the preset) or `On = $false` (not in the preset).

It is based on Billy's `Wow.exe`, which was in use on public servers for a long
time. Some of its patches have since been fixed because they could crash the
client or break animations. In the overview you can recognize them by the
addition "fixed by St0ny" to the author. The fixed patches have been tested in
game and work – **the preset is safe**.

If you still run into problems, please let me know via an
[issue](https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/issues/new/choose).
If you have a patch that should be part of this patcher, you can send it to me
via an issue as well.

The second preset "St0nys_Wow.exe" (key `S`) is St0ny's own selection for
private servers. It also contains patches with a ban risk and patches that make
`Wow.exe` larger – **use it only on your own servers**. The "St0ny" column in
the [patch overview](#patch-overview) shows which patches belong to it; in the
script the list is `$PRESET_STONY`. **Warning: this preset should never be used on
public servers under any circumstances – it will most likely get you banned!**
The patcher shows this as a yellow note when you load it with `S`.

## Changing or removing patches

Applied patches are not final. Just run `patcher-win.bat` again: the menu then has
exactly the patches checked that are currently in `Wow.exe`. Newly checked
patches are marked **(new)**, deselected ones **(will be removed)**. This way
you can add patches, deselect them or change values (jump height, double
jump, client info) as you like. `N` plus ENTER removes every patch – afterwards
`Wow.exe` is **byte-for-byte the original** again. Afterwards copy `Wow.exe`
back into your WoW folder.

How it works:

- **First start:** `Wow.exe` must be original (SHA256 check), otherwise the
  patcher aborts. Patching saves the original as `Wow.exe.ORI`, and every
  patched `Wow.exe` gets a [watermark](#notes).
- **Every later start:** the patcher recognizes a `Wow.exe` it patched itself
  by the watermark. If it is missing (and the file is not original), it aborts
  – e.g. for an exe patched with another tool.
- **Determining the patch state:** if the hash in `patcher_state.ini` matches
  (the patcher stores hash, patches, values and original bytes there after
  every run), it uses that file – the fast way. Otherwise, e.g. if the file is
  missing or the `Wow.exe` comes from another computer, the patcher checks all
  patch locations in the exe itself: which patches are in it, and with which
  values (jump height, build date etc.)? For this the script contains a small
  table with the original bytes at all patch locations. If there is nothing to
  do afterwards, the patcher still recreates `patcher_state.ini` so that the
  next start takes the fast way again.
- **Restoring the original:** from the patched exe the patcher rebuilds the
  original in memory, verifies it by SHA256 and applies the new selection on
  top. If that does not work exactly – e.g. because the exe was changed in
  some other way after patching – it aborts.
- Before writing, the patcher also checks that the new result can be reverted
  cleanly to the original.
- `Wow.exe.ORI` is not touched on later runs and is always the original. If
  it is missing, the patcher recreates it from the reconstructed original. In
  addition, every later run saves the previous `Wow.exe` as `Wow.exe.BAK`, so
  one step back is always possible.

> [!NOTE]
> A patch with a value exactly matching the original (e.g. the jump height
> `-7.9555473`) changes no bytes and is therefore not detected as applied when
> the exe is checked – it has no effect then anyway.

## Parameters for unattended use

All parameters are optional and are passed through from `patcher-win.bat` to
`apply_patches.ps1`.

| Parameter              | Meaning                                                                    |
|------------------------|----------------------------------------------------------------------------|
| `-Language de\|en`     | set the language for this run. Together with `-Select` the remembered language stays unchanged; if you accept a selection in the menu with ENTER, it is saved along with it. |
| `-Select <selection>`  | skip the selection menu: `saved` (saved selection), `reforged` (preset "Reforged", also `default`), `billy` (preset "Billy's_Wow.exe"), `stony` (preset "St0nys_Wow.exe"), `all`, `none` (remove all patches, restore the original) or numbers/ranges like `"1,3,5-8"`. The selection completely replaces the patches in `Wow.exe`. Using `-Select` does not change the saved selection. |
| `-Unattended`          | no prompts and no pauses. Without `-Language` the remembered language or German is used, without `-Select` the saved selection or the preset "Reforged". |
| `-Path <file>`         | patch a `Wow.exe` other than the one next to the script                    |

Example:

```bat
patcher-win.bat -Language en -Select saved -Unattended
```

Exit codes: `0` = success (or nothing to do), `1` = error, `2` = cancelled (by
the user or because no more input is possible).

## Files

| File                | Purpose |
|---------------------|---------|
| `patcher-win.bat`   | Launcher for Windows, calls `apply_patches.ps1` |
| `patcher-lin.sh`    | Launcher for Linux, also for a Mac |
| `apply_patches.ps1` | Patch engine: language selection, checks, selection menu, backup; reads the EXE once, patches in memory, writes it back once |
| `docs/README.md`    | This file |
| `docs/README.de.md` | German documentation |
| `docs/PATCHES.de.md` | Detailed patch descriptions in German |
| `docs/PATCHES.en.md` | Detailed descriptions of all patches |
| `patcher_selection.ini` | Created on the first start (remembered language), stores the accepted selection and the entered values |
| `patcher_state.ini` | Created when patching: hash of the patched `Wow.exe`, applied patches, values and original bytes – speeds up the next start, but is not strictly required |
| `Wow.exe.ORI`       | Backup of the original `Wow.exe`, created on the first patch run |
| `Wow.exe.BAK`       | Backup of the previous `Wow.exe` from before the last run |
| `LICENSE`           | MIT license |

---

## Patch overview

Click the number of a patch to jump to its description.

<details>
<summary><b>Show all patches with author and preset assignment</b></summary>

#### What the ratings mean

| Rating | Meaning | In the patcher |
|--------|---------|----------------|
| 🟢 **[safe]** | Tested in game and safe to use. | no warning |
| 🔴 **[unsafe]** | Confirmed ban risk: can lead to a ban on many servers. Only use it on servers that allow it. | red warning |
| 🟠 **[untested online]** | Not tested on public servers, possible ban risk: nobody can predict how the server will react. Careful, it may get you kicked or banned. | orange warning |
| 🟠 **[untested ingame]** | The function has not been checked in game yet: nobody can predict how the game will react, possibly buggy. | orange warning |
| 🟠 **[untested]** | Neither tested online nor ingame. | orange warning |
| 🟡 **[exe grows]** | The patch appends a section to `Wow.exe`. Not a certain ban, but a risk: some servers check the file size. | yellow note |
| 🟡 **[DLL risky]** | The patch itself is safe, but it loads a DLL that may be detected or blocked on public servers. Only use it where the DLL is allowed. | yellow note |

A patch can carry several ratings. They then share one pair of brackets
with a single dot in front: the stricter one wins (red before orange before
yellow), and a green dot turns yellow when the exe grows or the DLL is
risky. For example 🟡 **[safe - exe grows]**, 🟡 **[safe - DLL risky]**,
🔴 **[unsafe - exe grows]**, 🟠 **[untested - exe grows]** or
🔴 **[unsafe - untested ingame]**.
In the patcher the warnings are shown in square brackets after the
name, and before patching it lists them once more.

#### System & performance

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [1](PATCHES.en.md#patch-laa) | 4GB patch (Large Address Aware) | 🟢 **[safe]** | Alastor StrixEfuartus / Kebabstorm / Robinsch | ✅ | ✅ | ✅ |
| [2](PATCHES.en.md#patch-cache) | Disable CACHE folder creation | 🟢 **[safe]** | Alastor StrixEfuartus / Kebabstorm | – | – | – |
| [3](PATCHES.en.md#patch-itemcache) | Refresh item cache immediately | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [4](PATCHES.en.md#patch-worldcrash) | WorldFrame crash fix (invalid triangle indices) | 🔴 **[unsafe]** | Alyst3r (0x539wowmod) (fixed by St0ny) | – | – | ✅ |
| [5](PATCHES.en.md#patch-timer) | Precise timer fix (fixes the character turning stutter bug) | 🟢 **[safe]** | St0ny | ✅ | – | ✅ |
| [6](PATCHES.en.md#patch-nothrottle) | Do not throttle item and player name queries | 🟢 **[safe]** | tb (ported by St0ny) | – | – | ✅ |
| [7](PATCHES.en.md#patch-mirrorfix) | Mirror Image crash fix (memory leak with mirror images) | 🟢 **[safe]** | tb (ported by St0ny) | ✅ | – | ✅ |
| [8](PATCHES.en.md#patch-wmocube) | Missing WMO file: error cube instead of ERROR #134 | 🟢 **[safe]** | Alyst3r (ported by St0ny) | ✅ | – | ✅ |
| [9](PATCHES.en.md#patch-glyphfix) | Font glyph fix (wrong or garbled characters in text) | 🟡 **[safe - exe grows]** | tb (ported by St0ny) | ✅ | – | ✅ |

#### Security & privacy

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [10](PATCHES.en.md#patch-rce) | Remote code execution exploit fix | 🔴 **[unsafe]** | Robinsch | – | – | – |
| [11](PATCHES.en.md#patch-wardenoff) | Disable Warden completely, RCE fix | 🔴 **[unsafe]** | Robinsch | – | – | ✅ |
| [12](PATCHES.en.md#patch-scandll) | Disable Scan.dll | 🟢 **[safe]** | Alastor StrixEfuartus | ✅ | – | ✅ |
| [13](PATCHES.en.md#patch-noserverpatch) | Disallow client patches from the server | 🟢 **[safe]** | Kebabstorm | ✅ | – | ✅ |
| [14](PATCHES.en.md#patch-nosurvey) | Disallow hardware surveys from the server | 🟢 **[safe]** | Kebabstorm | ✅ | – | ✅ |

#### Login & connection

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [15](PATCHES.en.md#patch-skipbnet) | Skip Battle.net login | 🟢 **[safe]** | Kebabstorm | ✅ | – | ✅ |
| [16](PATCHES.en.md#patch-skiprdp) | Skip Remote Desktop check | 🟢 **[safe]** | Kebabstorm | ✅ | – | ✅ |
| [17](PATCHES.en.md#patch-nohttp) | Disable HTTP requests to Battle.net | 🟢 **[safe]** | Kebabstorm | ✅ | – | ✅ |
| [18](PATCHES.en.md#patch-afk) | CharAutoLogin idle-kick fix *(required for character auto-login; AFK and idle timers stay active, [Discord](https://discord.com/channels/858041817043042364/1515439916878663701))* | 🟢 **[safe]** | St0ny | – | – | ✅ |

#### Modding: interface, MPQs & addons

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [19](PATCHES.en.md#patch-glue) | Allow custom GlueXML | 🟢 **[safe]** | Alastor StrixEfuartus / Kebabstorm (fixed by St0ny) | ✅ | ✅ | ✅ |
| [20](PATCHES.en.md#patch-mpqsig) | Allow unsigned / incorrectly signed MPQs | 🟢 **[safe]** | Alastor StrixEfuartus | – | – | ✅ |
| [21](PATCHES.en.md#patch-mpqnames) | Allow extended MPQ names | 🟢 **[safe]** | unknown | – | ✅ | ✅ |
| [22](PATCHES.en.md#patch-localdata) | Load data directly from the Data folder (no MPQ) | 🟢 **[safe]** | Alastor StrixEfuartus | – | ✅ | ✅ |
| [23](PATCHES.en.md#patch-luaunlock) | LUA unlock (spells, movement, macros) | 🔴 **[unsafe]** | Alastor StrixEfuartus | – | – | – |
| [24](PATCHES.en.md#patch-luaunlockfull) | LUA unlock (complete): allow all protected functions | 🔴 **[unsafe]** | St0ny | – | – | – |
| [25](PATCHES.en.md#patch-keyprop) | Pass all keyboard events on to addons (OnKeyDown) | 🔴 **[unsafe - untested ingame]** | Alyst3r (0x539wowmod) | – | – | – |
| [26](PATCHES.en.md#patch-globalsv) | Merge addon data of all accounts (SavedVariables) *(shared folder `WTF\Account\global`)* | 🟠 **[untested]** | St0ny (original by boredatom) | – | – | – |

#### DLL loaders

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [27](PATCHES.en.md#patch-wowoptimize) | Load wow_optimize.dll at startup (performance optimizer by SUPREMATIST) *(requires [wow_optimize](https://github.com/suprepupre/wow-optimize) – only `wow_optimize.dll`, without `version.dll`)* | 🟡 **[safe - DLL risky]** | St0ny | – | – | ✅ |
| [28](PATCHES.en.md#patch-awesome) | Enable AwesomeWotlkLib.dll support (client extensions by noname08662) *(requires [awesome_wotlk](https://github.com/noname08662/awesome_wotlk))* | 🟡 **[safe - DLL risky]** | FrostAtom | – | ✅ | ✅ |
| [29](PATCHES.en.md#patch-wotlkext) | Enable WotLKExtensions.dll support (client extensions by Alyst3r) *(requires [WotLK-Extensions](https://github.com/Alyst3r/WotLK-Extensions))* | 🟡 **[safe - DLL risky]** | St0ny (original by Alyst3r) | – | – | – |
| [30](PATCHES.en.md#patch-lexara) | Load Lexara.dll at startup (HD fonts by Stormhand) *(requires [Lexara](https://github.com/Stormhand-dev/Lexara---HD-Font-Renderer-for-WoW-3.3.5) – rename `dinput8.dll` to `Lexara.dll`)* | 🟡 **[safe - DLL risky]** | St0ny | ✅ | – | – |
| [31](PATCHES.en.md#patch-voicedll) | Load voice.dll at startup (mod-voicechat) [ALPHA] *(module not finished yet, [mod-voicechat](https://github.com/Raz0r1337/mod-voicechat))* | 🟠 **[untested]** | St0ny | – | – | – |

#### Gameplay fixes

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [32](PATCHES.en.md#patch-areatrigger) | More precise area trigger timer (50 ms instead of 100 ms) | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [33](PATCHES.en.md#patch-swing) | Remove melee swing on right-click | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [34](PATCHES.en.md#patch-npcanim) | Suppress NPC attack animation when turning | 🟢 **[safe]** | Robinsch (fixed by St0ny) | ✅ | ✅ | ✅ |
| [35](PATCHES.en.md#patch-spellanim) | Fix spell animation after cancelled channel | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [36](PATCHES.en.md#patch-ghostattack) | Fix "ghost" attack when NPCs evade from combat | 🟢 **[safe]** | Robinsch (fixed by St0ny) | ✅ | ✅ | ✅ |
| [37](PATCHES.en.md#patch-naked) | Fix naked character bug | 🟢 **[safe]** | Robinsch (fixed by St0ny) | ✅ | ✅ | ✅ |
| [38](PATCHES.en.md#patch-forcereaction) | Keep force reaction on /reload | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [39](PATCHES.en.md#patch-mail) | New mail without the 60-second wait | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [40](PATCHES.en.md#patch-deadchat) | Allow chat commands while dead | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [41](PATCHES.en.md#patch-follow) | Allow /follow on NPCs | 🟠 **[untested online]** | St0ny (original by Alastor StrixEfuartus) | – | – | ✅ |
| [42](PATCHES.en.md#patch-level101) | Level 101+ Druid fix (druid stats in the character window, barber shop for everyone) | 🟢 **[safe]** | Alastor StrixEfuartus (fixed by St0ny) | ✅ | – | ✅ |
| [43](PATCHES.en.md#patch-raceclass) | Character creation: more than 10 classes (random class) *(for custom classes; server must support it)* | 🔴 **[unsafe]** | Alastor StrixEfuartus / Robinsch | – | – | – |
| [44](PATCHES.en.md#patch-namecheck) | Disable the name check in character creation (e.g. digits in names) *(server must allow the names as well)* | 🔴 **[unsafe]** | Alyst3r (0x539wowmod) (fixed by St0ny) | – | – | – |
| [45](PATCHES.en.md#patch-maxchars) | Max characters per realm raised to 255 | 🟢 **[safe]** | St0ny | – | ✅ | – |
| [46](PATCHES.en.md#patch-customitem) | Custom Item Fix (BETA) v2 *(custom items without DBC changes: model, icon and item type from the server data)* | 🟠 **[untested]** | St0ny (original by Kebabstorm) | – | – | – |
| [47](PATCHES.en.md#patch-climb) | Remove the climb angle limit (walk up any slope) | 🔴 **[unsafe]** | Alastor StrixEfuartus | – | – | – |
| [48](PATCHES.en.md#patch-jump) | Change jump height (original -7.9555473) *(asks for the value)* | 🔴 **[unsafe]** | Alastor StrixEfuartus | – | – | – |
| [49](PATCHES.en.md#patch-airforward) | Steer forward/backward while jumping | 🔴 **[unsafe]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | ✅ |
| [50](PATCHES.en.md#patch-airlateral) | Steer sideways while jumping | 🔴 **[unsafe]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | ✅ |
| [51](PATCHES.en.md#patch-airturn) | Turning while jumping changes the flight direction | 🔴 **[unsafe]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | ✅ |
| [52](PATCHES.en.md#patch-doublejump) | Double jump (more jumps in the air) *(asks for the value)* | 🔴 **[unsafe - exe grows]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | ✅ |
| [53](PATCHES.en.md#patch-noammo) | Ranged attacks without ammo *(the server has to support it, otherwise it still reports "no ammo")* | 🟠 **[untested]** | Alyst3r (ported by St0ny) | – | – | – |

#### Graphics & view distance

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [54](PATCHES.en.md#patch-farclip) | CVar farclip unlock (max 10000) | 🟢 **[safe]** | Alastor StrixEfuartus | ✅ | ✅ | ✅ |
| [55](PATCHES.en.md#patch-horizon) | CVar horizonFarclipScale unlock (max 12) | 🟢 **[safe]** | St0ny | ✅ | ✅ | ✅ |
| [56](PATCHES.en.md#patch-envdetail) | CVar environmentDetail unlock (no limit instead of 1.5) | 🟢 **[safe]** | St0ny | ✅ | ✅ | ✅ |
| [57](PATCHES.en.md#patch-grounddist) | CVar groundEffectDist unlock (max 3166 instead of 140) | 🟢 **[safe]** | unknown | ✅ | ✅ | ✅ |
| [58](PATCHES.en.md#patch-sliders) | Graphics options: extend slider maximums | 🟢 **[safe]** | St0ny | ✅ | – | ✅ |
| [59](PATCHES.en.md#patch-goscale) | GameObject view distance: Cat 0 and Cat 4 scale with environmentDetail | 🟢 **[safe]** | St0ny | ✅ | – | ✅ |
| [60](PATCHES.en.md#patch-cat0) | GameObject view distance: Cat 0 from 30 to 50 yards *(costs performance, more small objects visible)* | 🟢 **[safe]** | St0ny | – | – | ✅ |
| [61](PATCHES.en.md#patch-occluder) | Occluder fix for Stormwind (Open Azeroth) | 🟢 **[safe]** | Robinsch | ✅ | – | ✅ |
| [62](PATCHES.en.md#patch-bluemoon) | Re-enable the blue moon in the night sky | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [63](PATCHES.en.md#patch-notransparency) | No character transparency when zooming in | 🟢 **[safe]** | Alastor StrixEfuartus | ✅ | ✅ | ✅ |
| [64](PATCHES.en.md#patch-nofade) | No fade-out for NPCs with flag DO_NOT_FADE_IN *(server must set the flag)* | 🟠 **[untested]** | Alyst3r (0x539wowmod) (ported by St0ny) | – | – | – |
| [65](PATCHES.en.md#patch-hdportraits) | HD unit frame portraits: render resolution 256 instead of 64 pixels | 🟡 **[safe - exe grows]** | St0ny (original by Badgermilk0) | ✅ | – | – |
| [66](PATCHES.en.md#patch-iconsnap) | Pixel-exact icons in text (sharp instead of blurry) | 🟡 **[safe - exe grows]** | tb (ported by St0ny) | ✅ | – | ✅ |

#### Interface & comfort

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [67](PATCHES.en.md#patch-tracker) | Auto-sort quest tracker | 🟢 **[safe]** | unknown | ✅ | – | ✅ |
| [68](PATCHES.en.md#patch-worldmap) | Advanced world map enabled by default | 🟢 **[safe]** | unknown | ✅ | – | ✅ |
| [69](PATCHES.en.md#patch-castbars) | Cast bars on all frames | 🟢 **[safe]** | Kebabstorm | ✅ | ✅ | ✅ |
| [70](PATCHES.en.md#patch-emblems) | Retail guild emblems: selection extended from 170 to 196 *(requires [Patch-G](https://discord.com/channels/407664041016688662/1541873346608889936))* | 🟠 **[untested online]** | MacWarrior | – | – | ✅ |
| [71](PATCHES.en.md#patch-flash) | FlashWindow patch *(requires the [FlashWindow addon](https://github.com/noname08662/awesome_wotlk/tree/main/addons/Flash))* | 🟢 **[safe]** | Kebabstorm | – | ✅ | ✅ |
| [72](PATCHES.en.md#patch-charrandom) | Character creation: do not randomize the appearance automatically | 🟢 **[safe]** | Alyst3r (0x539wowmod) | ✅ | – | – |
| [73](PATCHES.en.md#patch-lootopen) | Loot window stays open while moving | 🟠 **[untested online]** | tb (ported by St0ny) | – | – | – |
| [74](PATCHES.en.md#patch-showlevel) | Real level instead of "??" for enemies 10+ levels above you *(bosses still show "??" – see No. 75)* | 🟠 **[untested online]** | tb (ported by St0ny) | – | – | – |
| [75](PATCHES.en.md#patch-showlevelboss) | Real level for bosses too instead of "??" (extension to No. 74) | 🟠 **[untested online]** | St0ny | – | – | – |
| [76](PATCHES.en.md#patch-holdrepeat) | Hold action buttons to repeat | 🔴 **[unsafe - exe grows]** | tb (ported by St0ny) | – | – | ✅ |
| [77](PATCHES.en.md#patch-bubblerange) | Increase the chat bubble range (original 25 yards) *(asks for the value)* | 🟢 **[safe]** | St0ny | ✅ | – | ✅ |

#### Window, mouse & camera

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [78](PATCHES.en.md#patch-window) | Windowed mode by default *(starts as a small window in the middle of the desktop – maximized only together with No. 79)* | 🟢 **[safe]** | St0ny | ✅ | – | ✅ |
| [79](PATCHES.en.md#patch-maximize) | Maximized window by default *(only works together with No. 78)* | 🟢 **[safe]** | St0ny | ✅ | – | ✅ |
| [80](PATCHES.en.md#patch-windowfix) | No black screen when switching to windowed mode | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [81](PATCHES.en.md#patch-mouse) | Mouse flicker / camera jump fix | 🟢 **[safe]** | Robinsch | ✅ | ✅ | ✅ |
| [82](PATCHES.en.md#patch-camera) | CameraReforged [BETA]: camera height and zoom limits *(shoulder offset has no effect yet)* | 🟠 **[untested online - exe grows]** | Stormhand (fixed by St0ny) | – | – | – |

#### Sound

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [83](PATCHES.en.md#patch-sound) | Optimize sound settings *(requires [OpenAL](https://github.com/kcat/openal-soft), otherwise the settings have no effect)* | 🟢 **[safe]** | St0ny | ✅ | – | ✅ |

#### Client info: version, build, title, date, icon

| No. | Patch | Status | Author | Reforged | Billy | St0ny |
|----:|-------|--------|-------|:--------:|:-----:|:-----:|
| [84](PATCHES.en.md#patch-clientversion) | Change client version (original 3.3.5) *(asks for the value)* | 🔴 **[unsafe]** | MacWarrior | – | – | – |
| [85](PATCHES.en.md#patch-clientbuild) | Change build number (original 12340) *(asks for the value)* | 🔴 **[unsafe]** | MacWarrior | – | – | – |
| [86](PATCHES.en.md#patch-clienttitle) | Change program title (file properties and window title) *(asks for the value)* | 🔴 **[unsafe]** | MacWarrior (fixed by St0ny) | – | – | – |
| [87](PATCHES.en.md#patch-clientdate) | Change build date (original Jun 24 2010) *(asks for the value)* | 🔴 **[unsafe]** | St0ny (original by MacWarrior) | – | – | – |
| [88](PATCHES.en.md#patch-clienticon) | Change program icon (icon of Wow.exe) *(asks for the value)* | 🔴 **[unsafe]** | St0ny (original by MacWarrior) | – | – | – |

</details>

> [!NOTE]
> **Authors wanted:** For patches without an entry in the "Author" column, the
> author is not known yet. If you know who made one of these patches, please
> open an [issue](https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/issues) – it will be added.

---

## Patch descriptions

The detailed descriptions of all patches are in a separate file:
**[PATCHES.en.md](PATCHES.en.md)**. In the [patch overview](#patch-overview),
clicking the number of a patch takes you straight to its description.

---

## Notes

- **Warnings:** every patch has a uniform rating. In the
  [patch overview](#patch-overview) it is shown in the "Status" column, in the patcher
  in square brackets, and before the confirmation prompt the patcher lists the
  selected patches with a warning once more:
  - 🟢 **safe** – tested in game, no warning in the patcher.
  - 🔴 **unsafe** – ban risk, can lead to a ban on many servers: No. 4, 10, 11, 23–25,
    43, 44, 47–52, 76 and 84–88 (red warning).
  - 🟠 **untested online** – not tested on public servers, possible ban risk, careful, may get
    you kicked or banned: No. 26, 31, 41, 46, 53, 64, 70, 73–75 and 82
    (orange warning).
  - 🟠 **untested ingame** – the function has not been checked in game yet,
    possibly buggy: No. 25, 26, 31, 46, 53 and 64 (orange warning).
  - 🟡 **exe grows** – these patches append a section to `Wow.exe`: No. 9, 52,
    65, 66, 76 and 82. This does not mean a certain ban, but it is a risk: some
    servers check the file size (yellow note). All other patches do not change
    the file size.
  - 🟡 **DLL risky** – the patch itself is safe, but it loads a DLL that may be
    detected or blocked on public servers: No. 27–30 (yellow note). Only
    use it where the DLL is allowed.
- **Signature:** the original `Wow.exe` is digitally signed by Blizzard. Every
  patch invalidates this signature. Windows will therefore probably warn about
  an unsigned, potentially harmful app when it starts; with "More info" → "Run
  anyway" WoW starts normally. A new signature that Windows trusts is only
  issued by certificate authorities with identity verification – you cannot
  get one for a modified Blizzard file. The patches that append a section
  (No. 9, 52, 65, 66, 76 and 82) also remove the reference to the
  signature from the header: the new section lies behind the signature, and
  some tools would otherwise report the file as damaged. The signature bytes
  themselves stay untouched, and removing the patches restores the original
  including its signature. On Windows the patcher removes a download mark
  ("This file came from another computer") from `Wow.exe` after writing it,
  like the "Unblock" checkbox in the file properties.
- **Watermark:** every patched `Wow.exe` contains the text
  `Patched with St0nys AIO WoW.exe Patcher by St0ny (Raz0r1337) - https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher`.
  This is how the patcher identifies a `Wow.exe` unambiguously as its own: it
  never mixes its patches with those of other patchers, and it can read its
  patch state from the exe even if `patcher_state.ini` was deleted. The text
  sits in the unused padding behind the `.tls` section (file offset
  `0x72DE20`), is never loaded into memory and does not change the file size.
  Removing all patches removes it again. As a side effect you can always
  check whether a `Wow.exe` was made with this patcher – e.g. with a hex editor
  or in the command prompt with `findstr /m /c:"St0nys AIO" Wow.exe` (prints the
  file name if it is there).
- **Restoring the original:** run the patcher, press `N` and ENTER – with or
  without `patcher_state.ini`. Alternatively delete the patched `Wow.exe` and
  rename `Wow.exe.ORI` to `Wow.exe`. `Wow.exe.BAK`, on the other hand, is the
  `Wow.exe` from before the last run.
- **For developers:** the original bytes table in the script is regenerated
  with `apply_patches.ps1 -BuildTable -Path <original Wow.exe>`. This is needed
  after every change to a patch; if it no longer matches, the patcher points it
  out after patching.
- Use at your own risk. This project is not affiliated with Blizzard
  Entertainment.

## Acknowledgements

- A very special thank you goes to **Billy Hoyle** – for all his help, tips,
  expertise and testing over the past months and for helping to collect the
  patches. His patch set is included as the preset "Billy's_Wow.exe".
- Thanks also to **MacWarrior**, who also helped collect the patches and
  contributed some of his own.
- Thanks also to **Stormhand** for the permission to include his
  CameraReforged patch. The official preset of his project
  [Project Reforged](https://projectreforged.github.io/wotlk/) is included as
  the preset "Reforged" and is the default selection.
- A big thank you to **Stormhand**, **MacWarrior** and **Billy Hoyle** for all
  the testing in game – and to Stormhand in particular for risking their own
  Warmane account to find out which patches are "safe" to use. 😄
- Thanks to **Moroes**, who tracked down patch
  [#26](PATCHES.en.md#patch-globalsv) and passed it on to me.
- And of course thanks to all patch authors named in the
  [patch overview](#patch-overview).

## License

This project is licensed under the [MIT License](../LICENSE).
Copyright (c) 2026 St0ny (Raz0r1337).

In short: anyone may use, modify and redistribute the patcher – including in
their own projects – as long as the copyright notice and the license text are
kept (attribution).

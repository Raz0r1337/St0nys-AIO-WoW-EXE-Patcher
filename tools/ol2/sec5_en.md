<a id="patch-outline"></a>
**Outline for target and mouseover [BETA]** *(No. 68, Author: St0ny)* 🟠 **[untested - exe grows]**

Like in retail, the 3D figure of your target and the figure under the mouse
cursor get a thin outline (about 2 pixels). Players get their class color like
in the raid frames, everyone else the color of the selection circle: red
hostile, yellow neutral, green friendly. Hostile players gently pulse between
their class color and red, so you still recognize them as enemies despite the
class color. The outline only appears where the figure is visible; where a
wall stands in front of it, there is no outline. Weapons, helmet and mount
belong to the figure.

> [!WARNING]
> **BETA** – still untested, online and in game. That is why the patch is
> deselected by default and only in the dev branches for now, not in
> `st0ny-main`.

> [!WARNING]
> **On public servers please keep the default setting:** answer all questions
> before patching with N. If the patch gets banned on a server, that is bad
> luck – there is nothing I can do about it. From then on it can only be used
> on your own private servers. So please be careful.

**Settings:** After the patch selection the patcher asks six questions with
Y/N. ENTER takes the suggestion in brackets – N the first time, the current
state for a patched `Wow.exe`. The default is N everywhere: only target and
mouseover, not through walls.

| Question | Effect with Y |
|----------|---------------|
| Visible through walls? | The outline also appears where the figure is hidden, for all outlines. **Unsafe** – may be considered cheating, the patcher then warns in red. |
| Own character always outlined? | Your figure always has an outline. |
| Own party of 5 always outlined? | The up to 4 other players of your party (`party1` to `party4`) always have an outline. |
| Whole raid always outlined? | All other players in the raid (up to 39) always have an outline, your party also outside of a raid – **costs a lot of FPS**. |
| Own character outlined only where it is hidden? | Your figure only gets an outline where it is hidden, for example behind a house wall or a hill. For you it takes precedence over "always outlined" and "through walls". |
| Reaction color instead of class color? | All outlines in the color of the selection circle (mostly blue for players), target and mouseover too. Hostile players are then simply red and do not pulse. |

If a figure is the target or under the mouse cursor, that outline applies.
Players out of sight have none. The patcher remembers the answers like other
values in `patcher_selection.ini`, e.g. `value.outline=self,party` (`none` =
default; in order, the settings are called `walls`, `self`, `party`, `raid`,
`hidden` and `react`).

> [!WARNING]
> **Whole raid costs a lot of FPS:** every outlined figure is drawn ten times.
> With 25 or 40 players that is a lot of extra draw calls per frame. On weaker
> computers better use only the party of 5.

> [!NOTE]
> **Only where hidden:** only what is drawn before your figure is detected.
> The game normally draws terrain and buildings before the figures; whether
> trees or other figures in front are detected as well depends on the order in
> which the game draws – the test in game has to show that.

How it works:
- The depth buffer gets a stencil part (D24S8 instead of D24X8). The game
  itself never uses stencil.
- While the figure is drawn, its visible pixels are marked in the stencil.
  Then it is drawn eight more times invisibly, each shifted by 2 pixels in
  every direction (via the shader's projection matrix), with depth test –
  these copies mark the outline and store the figure's depth there. Every
  outlined figure (target, mouseover, you, every party and raid member, up to
  48) gets a value of its own and so a color of its own.
- Whatever is drawn afterwards in front of the figure (e.g. bushes,
  mushrooms, grass) clears the mark at its pixels and so hides the outline as
  well. Things behind stay behind the outline thanks to the stored depth.
  Transparent things like water or spell effects leave the outline in place.
- Further parts of the same figure (cloak, weapon, mount) are drawn once more
  on their own outline without depth test, so no outline is left between the
  parts.
- With "through walls" the figure is also marked where it is hidden, and the
  copies run without depth test. Things drawn later no longer clear the
  outline then.
- With "only where hidden" your figure is also marked where it is hidden as
  well; its copies, however, only mark the outline where something already
  drawn lies in front of them.
- After the models and before the interface, a full-screen quad per outlined
  figure colors only its outline pixels; then the stencil is cleared and the
  game sends all its graphics states again.
- Hostile means: the player's selection circle would be red. Then the quad
  mixes their class color with red; the share of red rises and falls smoothly
  (cosine), one pulse takes 1.5 seconds.
- Code and data live in a section of their own (`.outl`, 0x118E bytes). Each
  setting is a single padding byte between two functions in `.text` that is
  set to 1 with Y; the code reads these switches while drawing. This is also
  how the patcher recognizes the settings in a patched `Wow.exe`.

> [!NOTE]
> Only with `gxApi d3d9` (default) and a 24-bit depth buffer (default). With
> D3D9Ex, OpenGL or `gxDepthBits` 16/32 the patch switches itself off. The
> first version also ran in game with DXVK, because WoW uses Direct3D 9 there
> as well.

> [!NOTE]
> If all patches with a section of their own are active at the same time,
> there is no room left in the PE header for another section entry. Then the
> patcher extends the last appended section instead of adding a new one.


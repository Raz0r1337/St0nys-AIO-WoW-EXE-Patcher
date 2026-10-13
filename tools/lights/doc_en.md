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


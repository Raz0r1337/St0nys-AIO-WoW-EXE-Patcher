# Audit-Fixes: Nr. 4 (Pruefung je Dreieck) und CameraReforged (kein fninit).
# Aufruf: python3 apply_fix.py <worktree>   - jede Ersetzung muss genau einmal passen.
import sys
wt = sys.argv[1]

def rep(s, old, new, label):
    n = s.count(old)
    assert n == 1, '%s: %d Treffer' % (label, n)
    return s.replace(old, new)

PS = wt + '/apply_patches.ps1'
raw = open(PS, encoding='ascii', newline='').read()
assert raw.count('\r\n') == raw.count('\n') and raw.count('\r\r') == 0
s = raw.replace('\r\n', '\n')

# --- Nr. 4: Kommentarblock + Funktion ---
s = rep(s,
"#  WorldFrame-Absturzfix (0x539wowmod, Alyst3r)\n"
"#  Die Funktion bei VA 0x81D510 laeuft ueber Dreiecke aus Index-Tripeln\n"
"#  (WORDs) und rechnet Index minus Basis ([ebp+10h]) in eine Vertex-Adresse\n"
"#  um. Ist ein Index kleiner als die Basis, landet die Adresse vor dem Puffer\n"
"#  und der Client stuerzt ab. Die Hoehle prueft die drei Indizes des ersten\n"
"#  Dreiecks und springt in dem Fall zum Funktionsende (VA 0x81D66E).\n"
"#  Einstieg ist das jae bei VA 0x81D51B, das genau dorthin springt (leere\n"
"#  Liste) - es wird in der Hoehle nachgebildet, der Stack ist derselbe.\n"
"#  edx ist hier frei (wird erst bei VA 0x81D547 gesetzt).\n"
"#  Neu umgesetzt: Im Original sind die Sprungweiten der drei jg falsch\n"
"#  berechnet, ausserdem ist diese Form kuerzer (38 statt 59 Byte).\n",
"#  WorldFrame-Absturzfix (0x539wowmod, Alyst3r)\n"
"#  Die Funktion bei VA 0x81D510 laeuft ueber Dreiecke aus Index-Tripeln\n"
"#  (WORDs) und rechnet Index minus Basis (ebx = [ebp+10h]) in eine\n"
"#  Vertex-Adresse um. Ist ein Index kleiner als die Basis, landet die\n"
"#  Adresse vor dem Puffer und der Client stuerzt ab. Die Hoehle sitzt im\n"
"#  Schleifenkoerper (VA 0x81D536, ersetzt \"movzx eax, word [edi] /\n"
"#  sub eax, ebx\") und prueft die drei Indizes JEDES Dreiecks: Ist einer\n"
"#  kleiner als die Basis, geht es direkt zum naechsten Dreieck (VA\n"
"#  0x81D65E: add edi, 6 / cmp / jb); sonst holt sie die beiden ersetzten\n"
"#  Befehle nach und springt zurueck (VA 0x81D53B). Der FPU-Stack ist an\n"
"#  beiden Stellen gleich belegt (nur der fldz vom Anfang), eax wird im\n"
"#  Schleifenkopf ohnehin neu geladen.\n"
"#  Das Original von Alyst3r prueft nur das erste Dreieck (einmal vor der\n"
"#  Schleife, Hook am jae bei VA 0x81D51B) und hat falsch berechnete\n"
"#  Sprungweiten; diese Fassung prueft alle Dreiecke bei gleicher\n"
"#  Hoehlengroesse (38 Byte).\n", 'Nr.4 Kommentar')

s = rep(s,
"    $HOOK_VA = 0x81D51B; $BACK_VA = 0x81D521; $EXIT_VA = 0x81D66E\n"
"    Assert-Bytes ($HOOK_VA - 0x400C00) @(0x0F, 0x83, 0x4D, 0x01, 0x00, 0x00) 'WorldFrame-Absturzfix'\n"
"    $loc = Get-CodeCave 'worldcrash' 38\n"
"    $CAVE = $loc[0]\n"
"    $c = New-Object System.Collections.Generic.List[byte]\n"
"    AddRaw $c @(0x73, 0x1F)                      # jae Ausgang (leere Liste, wie im Original)\n"
"    AddRaw $c @(0x8B, 0x55, 0x10)                # mov edx, [ebp+10h]   (Basis)\n"
"    AddRaw $c @(0x0F, 0xB7, 0x07)                # movzx eax, word [edi]\n"
"    AddRaw $c @(0x3B, 0xD0, 0x7F, 0x15)          # cmp edx, eax / jg Ausgang\n"
"    AddRaw $c @(0x0F, 0xB7, 0x47, 0x02)          # movzx eax, word [edi+2]\n"
"    AddRaw $c @(0x3B, 0xD0, 0x7F, 0x0D)          # cmp edx, eax / jg Ausgang\n"
"    AddRaw $c @(0x0F, 0xB7, 0x47, 0x04)          # movzx eax, word [edi+4]\n"
"    AddRaw $c @(0x3B, 0xD0, 0x7F, 0x05)          # cmp edx, eax / jg Ausgang\n"
"    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $BACK_VA)     # jmp zurueck\n"
"    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $EXIT_VA)     # Ausgang: jmp Funktionsende\n"
"    if ($c.Count -ne 38) { throw 'WorldFrame-Absturzfix: Hoehle hat die falsche Groesse.' }\n"
"    Patch $loc[1] $c.ToArray()\n"
"    $hook = (Get-Rel32 @(0xE9) $HOOK_VA $CAVE) + [byte[]](0x90)\n"
"    Patch ($HOOK_VA - 0x400C00) ([byte[]]$hook)\n",
"    $HOOK_VA = 0x81D536; $BACK_VA = 0x81D53B; $NEXT_VA = 0x81D65E\n"
"    Assert-Bytes ($HOOK_VA - 0x400C00) @(0x0F, 0xB7, 0x07, 0x2B, 0xC3) 'WorldFrame-Absturzfix'\n"
"    $loc = Get-CodeCave 'worldcrash' 38\n"
"    $CAVE = $loc[0]\n"
"    $c = New-Object System.Collections.Generic.List[byte]\n"
"    AddRaw $c @(0x0F, 0xB7, 0x07)                # movzx eax, word [edi]\n"
"    AddRaw $c @(0x3B, 0xC3, 0x7C, 0x1A)          # cmp eax, ebx / jl Weiter   (Index < Basis)\n"
"    AddRaw $c @(0x0F, 0xB7, 0x47, 0x02)          # movzx eax, word [edi+2]\n"
"    AddRaw $c @(0x3B, 0xC3, 0x7C, 0x12)          # cmp eax, ebx / jl Weiter\n"
"    AddRaw $c @(0x0F, 0xB7, 0x47, 0x04)          # movzx eax, word [edi+4]\n"
"    AddRaw $c @(0x3B, 0xC3, 0x7C, 0x0A)          # cmp eax, ebx / jl Weiter\n"
"    AddRaw $c @(0x0F, 0xB7, 0x07)                # movzx eax, word [edi]   (ersetzte Befehle)\n"
"    AddRaw $c @(0x2B, 0xC3)                      # sub eax, ebx\n"
"    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $BACK_VA)     # jmp zurueck in die Schleife\n"
"    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $NEXT_VA)     # Weiter: jmp naechstes Dreieck\n"
"    if ($c.Count -ne 38) { throw 'WorldFrame-Absturzfix: Hoehle hat die falsche Groesse.' }\n"
"    Patch $loc[1] $c.ToArray()\n"
"    Patch ($HOOK_VA - 0x400C00) ([byte[]](Get-Rel32 @(0xE9) $HOOK_VA $CAVE))\n", 'Nr.4 Funktion')

# --- CameraReforged: fninit entfernen ---
s = rep(s,
"    AddRaw $c @(0x61)                                                 # popad\n"
"    AddRaw $c @(0xDB, 0xE3)                                           # fninit - popad rettet die FPU nicht,\n"
"                                                                      # und am Funktionseingang ist der\n"
"                                                                      # x87-Stack per Konvention leer\n",
"    AddRaw $c @(0x61)                                                 # popad - die FPU bleibt unberuehrt:\n"
"                                                                      # der Hook nutzt sie nicht, und\n"
"                                                                      # CVars_Register (cdecl) laesst den\n"
"                                                                      # x87-Stack leer zurueck. Ein fninit\n"
"                                                                      # wuerde auch das Steuerwort (Genauig-\n"
"                                                                      # keit, Rundung) zuruecksetzen.\n", 'Camera fninit')

s.encode('ascii')
open(PS, 'w', encoding='ascii', newline='').write(s.replace('\n', '\r\n'))

# --- Docs ---
def edit(fn, pairs):
    p = wt + '/docs/' + fn
    t = open(p, encoding='utf-8', newline='').read()
    assert '\r' not in t
    for old, new, label in pairs:
        t = rep(t, old, new, label)
    open(p, 'w', encoding='utf-8', newline='').write(t)

edit('PATCHES.de.md', [(
"die Adresse vor den Puffer und der Client stürzt ab. Der Patch prüft vorher die\n"
"drei Indizes des ersten Dreiecks und überspringt die Funktion in diesem Fall.\n"
"Gegenüber dem Original sind die drei Sprungweiten korrigiert und der Code ist\n"
"kürzer.\n",
"die Adresse vor den Puffer und der Client stürzt ab. Der Patch prüft in der\n"
"Schleife die drei Indizes jedes Dreiecks; ein Dreieck mit ungültigem Index wird\n"
"übersprungen, die übrigen werden normal verarbeitet.\n"
"Das Original (0x539wowmod) prüft nur das erste Dreieck jedes Aufrufs, einmal\n"
"vor der Schleife, und hat falsch berechnete Sprungweiten; hier sitzt die\n"
"Prüfung im Schleifenkörper, bei gleicher Codegröße.\n", 'de Text'), (
"> [!NOTE]\n"
"> Ein heuristischer Fix, wie ihn auch der Autor nennt: Geprüft wird nur das erste\n"
"> Dreieck jedes Aufrufs. Er stört nicht, wenn alles stimmt, fängt aber nicht jeden\n"
"> denkbaren Fall ab.\n",
"> [!NOTE]\n"
"> Geprüft wird nur, ob ein Index kleiner als die Basis ist – das ist der Fall,\n"
"> der vor den Puffer zeigt. Eine Obergrenze kennt die Funktion nicht, ein zu\n"
"> großer Index wird also weiterhin nicht abgefangen.\n", 'de Note')])

edit('PATCHES.en.md', [(
"memory address. If an index is smaller than the base, the address points before\n"
"the buffer and the client crashes. The patch checks the three indices of the\n"
"first triangle beforehand and skips the function in that case. Compared to the\n"
"original, the three jump distances have been corrected and the code is shorter.\n",
"memory address. If an index is smaller than the base, the address points before\n"
"the buffer and the client crashes. The patch checks the three indices of every\n"
"triangle inside the loop; a triangle with an invalid index is skipped, the\n"
"others are processed normally.\n"
"The original (0x539wowmod) only checks the first triangle of each call, once\n"
"before the loop, and has miscalculated jump distances; here the check sits in\n"
"the loop body, with the same code size.\n", 'en Text'), (
"> [!NOTE]\n"
"> A heuristic fix, as the author himself calls it: only the first triangle of\n"
"> each call is checked. It does no harm when everything is fine, but does not\n"
"> catch every conceivable case.\n",
"> [!NOTE]\n"
"> Only \"index smaller than the base\" is checked – that is the case that points\n"
"> before the buffer. The function knows no upper limit, so an index that is too\n"
"> large is still not caught.\n", 'en Note')])
print(wt.split('/')[-1], 'fix OK')

#!/usr/bin/env python3
# Preset "Reforged" aus einer gespeicherten Auswahl (patcher_selection.ini) setzen: Ids mit 1 sind drin, mit 0
# nicht; Ids, die in der Datei fehlen, behalten ihren Stand. Patcher: $PRESET_REFORGED (neue Ids hinter dem
# vorigen Preset-Eintrag in Patch-Reihenfolge); README DE/EN: Spalte "Reforged" aller Zeilen. Kommentar und
# Reforged-Absatz sind je Zweig fest hinterlegt (Stand 19.10.2026: + awesome, - deadchat, - lightstay).
# Aufruf: reforged_set.py <Ordner> <ini> <main|dev|y38>
import sys, os, re
D, INI, B = sys.argv[1], sys.argv[2], sys.argv[3]
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
def once(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:80], s.count(a)); return s.replace(a, b)
ini = {}
for l in open(INI, encoding='utf-8'):
    m = re.match(r'^\s*([A-Za-z0-9_]+)\s*=\s*([01])\s*$', l)
    if m: ini[m.group(1)] = m.group(2) == '1'
# ---------------- Patcher ----------------
p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
body = s[s.index('\n$patches = @(\n'):]
ids = re.findall(r"(?m)^    @\{ Id = '(\w+)'", body)
m = re.search(r'(?ms)^\$PRESET_REFORGED = @\(\n.*?\n\)\n', s); blk = m.group(0)
cur = re.findall(r"'(\w+)'", blk)
new = [i for i in ids if ini.get(i, i in cur)]
for x in [i for i in cur if i not in new]:
    n = len(re.findall(r"'%s'" % x, blk)); assert n == 1, x
    blk = re.sub(r" '%s',|'%s', " % (x, x), '', blk, count=1); assert "'%s'" % x not in blk, x
for x in [i for i in new if i not in cur]:
    prev = [i for i in ids[:ids.index(x)] if i in new and "'%s'" % i in blk][-1]
    blk = blk.replace("'%s'," % prev, "'%s', '%s'," % (prev, x), 1)
assert set(re.findall(r"'(\w+)'", blk)) == set(new) and len(re.findall(r"'(\w+)'", blk)) == len(new)
s = s[:m.start()] + blk + s[m.end():]
C = {
 'main': ("# Warmane getestet (Nr. 9, 65 und 66 vergroessern die Wow.exe); dazu der\n"
          "# Lexara- und der Lux-Lader (Nr. 30 und 31, Patch sicher, DLL riskant; Lexara\n"
          "# laedt Lux ohnehin mit, der Lux-Lader auch ohne Lexara) und die\n"
          "# Licht-Patches Nr. 67 und 68 (im Spiel und online getestet, sicher; Nr. 67\n"
          "# vergroessert die Wow.exe ebenfalls). Im Menue mit R, ueber -Select\n",
          "# Warmane getestet (Nr. 9, 65 und 66 vergroessern die Wow.exe); dazu die\n"
          "# Lader fuer awesome_wotlk, Lexara und Lux (Nr. 28, 30 und 31, Patch sicher,\n"
          "# DLL riskant; Lexara laedt Lux ohnehin mit, der Lux-Lader auch ohne Lexara)\n"
          "# und der Licht-Patch Nr. 67 (im Spiel und online getestet, sicher;\n"
          "# vergroessert die Wow.exe ebenfalls). Im Menue mit R, ueber -Select\n"),
 'dev':  ("# Warmane getestet (Nr. 9, 66 und 67 vergroessern die Wow.exe); dazu der\n"
          "# Lexara- und der Lux-Lader (Nr. 30 und 31, Patch sicher, DLL riskant; Lexara\n"
          "# laedt Lux ohnehin mit, der Lux-Lader auch ohne Lexara) und die\n"
          "# Licht-Patches Nr. 69 und 70 (im Spiel und online getestet, sicher; Nr. 69\n"
          "# vergroessert die Wow.exe ebenfalls). Im Menue mit R, ueber -Select\n",
          "# Warmane getestet (Nr. 9, 66 und 67 vergroessern die Wow.exe); dazu die\n"
          "# Lader fuer awesome_wotlk, Lexara und Lux (Nr. 28, 30 und 31, Patch sicher,\n"
          "# DLL riskant; Lexara laedt Lux ohnehin mit, der Lux-Lader auch ohne Lexara)\n"
          "# und der Licht-Patch Nr. 69 (im Spiel und online getestet, sicher;\n"
          "# vergroessert die Wow.exe ebenfalls). Im Menue mit R, ueber -Select\n"),
 'y38':  ("# von Stormhand. Nur sichere Patches, alle von Stormhand mehrere Stunden auf\n"
          "# Warmane getestet (Nr. 9, 63 und 64 vergroessern die Wow.exe). Im Menue mit R, ueber\n"
          "# -Select reforged; gilt beim ersten Start und fuer neue Patches.\n",
          "# von Stormhand. Sichere Patches, alle von Stormhand mehrere Stunden auf\n"
          "# Warmane getestet (Nr. 9, 63 und 64 vergroessern die Wow.exe); dazu der\n"
          "# awesome_wotlk-Lader (Nr. 27, Patch sicher, DLL riskant). Im Menue mit R,\n"
          "# ueber -Select reforged; gilt beim ersten Start und fuer neue Patches.\n"),
}[B]
s = once(s, C[0], C[1], 'ps1-Kommentar')
wr(p, s, True)
# ---------------- README: Spalte "Reforged" ----------------
newset = set(new); changed = []
for f, tag in (('README.de.md', 'PATCHES.de.md'), ('README.md', 'PATCHES.en.md')):
    p = os.path.join(D, 'docs', f); lines = rd(p).split('\n')
    for k, l in enumerate(lines):
        mm = re.match(r'^\| \[(\d+)\]\(%s#patch-(\w+)\) \|' % re.escape(tag), l)
        if not mm: continue
        c = l.split('|'); assert c[-1] == '' and c[-4].strip() in ('✅', '–'), (f, l[:60])
        want = ' ✅ ' if mm.group(2) in newset else ' – '
        if c[-4] != want: c[-4] = want; lines[k] = '|'.join(c); changed.append('%s Nr. %s %s -> %s' % (f, mm.group(1), mm.group(2), want.strip()))
    wr(p, '\n'.join(lines))
print('\n'.join(changed))
# ---------------- README: Absatz zum Preset ----------------
L = {'main': '67', 'dev': '69'}.get(B)
if L:
    de_a = ("Dazu kommen der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften, der\n"
            "Lux-Lader (Nr. 31) für die Schulterkamera LuxShoulderCam und die\n"
            "Licht-Patches Nr. %s und %s. Bei den beiden Ladern ist der Patch selbst\n"
            "sicher, die geladene DLL kann auf öffentlichen Servern aber erkannt oder\n"
            "blockiert werden; ohne die DLL im WoW-Ordner bewirken sie nichts. Lexara\n"
            "lädt die `LuxShoulderCam.dll` selbst mit, der Lux-Lader lädt sie auch ohne\n"
            "Lexara – beide zusammen schaden nicht. Die Licht-Patches sind im Spiel und\n"
            "online getestet und sicher. Nr. %s vergrößert die `Wow.exe` ebenfalls und\n"
            "wirkt erst mit den Shadern aus\n" % (L, int(L) + 1, L))
    de_b = ("Dazu kommen der awesome_wotlk-Lader (Nr. 28) für die Client-Erweiterungen\n"
            "von noname08662, der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften, der\n"
            "Lux-Lader (Nr. 31) für die Schulterkamera LuxShoulderCam und der\n"
            "Licht-Patch Nr. %s. Bei den drei Ladern ist der Patch selbst sicher, die\n"
            "geladene DLL kann auf öffentlichen Servern aber erkannt oder blockiert\n"
            "werden; ohne die DLL im WoW-Ordner bewirken sie nichts. Lexara lädt die\n"
            "`LuxShoulderCam.dll` selbst mit, der Lux-Lader lädt sie auch ohne Lexara –\n"
            "beide zusammen schaden nicht. Der Licht-Patch ist im Spiel und online\n"
            "getestet und sicher. Er vergrößert die `Wow.exe` ebenfalls und wirkt erst\n"
            "mit den Shadern aus\n" % L)
    en_a = ("other servers may check the file size. On top of that come the Lexara loader\n"
            "(No. 30) for Stormhand's HD fonts, the Lux loader (No. 31) for the\n"
            "LuxShoulderCam shoulder camera and the light patches No. %s and %s. For both\n"
            "loaders the patch itself is safe, but the loaded DLL may be detected or\n"
            "blocked on public servers; without the DLL in the WoW folder they do nothing.\n"
            "Lexara loads `LuxShoulderCam.dll` by itself, the Lux loader also loads it\n"
            "without Lexara – both together do no harm. The light patches are tested in\n"
            "game and online and are safe. No. %s makes `Wow.exe` larger as well and only\n"
            "takes effect with the shaders\n" % (L, int(L) + 1, L))
    en_b = ("other servers may check the file size. On top of that come the awesome_wotlk\n"
            "loader (No. 28) for the client extensions by noname08662, the Lexara loader\n"
            "(No. 30) for Stormhand's HD fonts, the Lux loader (No. 31) for the\n"
            "LuxShoulderCam shoulder camera and the light patch No. %s. For the three\n"
            "loaders the patch itself is safe, but the loaded DLL may be detected or\n"
            "blocked on public servers; without the DLL in the WoW folder they do nothing.\n"
            "Lexara loads `LuxShoulderCam.dll` by itself, the Lux loader also loads it\n"
            "without Lexara – both together do no harm. The light patch is tested in game\n"
            "and online and is safe. It makes `Wow.exe` larger as well and only takes\n"
            "effect with the shaders\n" % L)
else:
    de_a = ("Warmane war das kein Problem, andere Server können die Dateigröße aber prüfen. Welche Patches\n"
            "dazugehören, zeigt die Spalte „Reforged“ in der\n")
    de_b = ("Warmane war das kein Problem, andere Server können die Dateigröße aber prüfen.\n"
            "Dazu kommt der awesome_wotlk-Lader (Nr. 27) für die Client-Erweiterungen von\n"
            "noname08662: Der Patch selbst ist sicher, die geladene DLL kann auf\n"
            "öffentlichen Servern aber erkannt oder blockiert werden; ohne die DLL im\n"
            "WoW-Ordner bewirkt er nichts. Welche Patches dazugehören, zeigt die Spalte\n"
            "„Reforged“ in der\n")
    en_a = ("on Warmane, but other servers may check the file size. The \"Reforged\" column in the\n")
    en_b = ("on Warmane, but other servers may check the file size. On top of that comes\n"
            "the awesome_wotlk loader (No. 27) for the client extensions by noname08662:\n"
            "the patch itself is safe, but the loaded DLL may be detected or blocked on\n"
            "public servers; without the DLL in the WoW folder it does nothing. The\n"
            "\"Reforged\" column in the\n")
p = os.path.join(D, 'docs', 'README.de.md'); wr(p, once(rd(p), de_a, de_b, 'README.de-Absatz'))
p = os.path.join(D, 'docs', 'README.md'); wr(p, once(rd(p), en_a, en_b, 'README.en-Absatz'))
print('Reforged neu: %d Patches' % len(new))

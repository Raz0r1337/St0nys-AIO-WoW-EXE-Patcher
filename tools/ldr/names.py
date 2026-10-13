# DLL-Lader einheitlich benennen, voice.dll-Eintrag angleichen, ALPHA -> BETA (dev).
import sys
wt = sys.argv[1]
def once(s, a, b, label):
    n = s.count(a); assert n == 1, '%s: %d Treffer fuer %r' % (label, n, a[:80]); return s.replace(a, b)
# ---- Skript
p = wt + '/apply_patches.ps1'
s = open(p, 'rb').read().decode('ascii'); assert s.count('\r\n') == s.count('\n'); s = s.replace('\r\n', '\n')
for a, b in (
    ("       De = 'AwesomeWotlkLib.dll Unterstuetzung aktivieren (Client-Erweiterungen von noname08662)'\n",
     "       De = 'AwesomeWotlkLib.dll beim Start laden (Client-Erweiterungen von noname08662)'\n"),
    ("       En = 'Enable AwesomeWotlkLib.dll support (client extensions by noname08662)'\n",
     "       En = 'Load AwesomeWotlkLib.dll at startup (client extensions by noname08662)'\n"),
    ("       De = 'WotLKExtensions.dll Unterstuetzung aktivieren (Client-Erweiterungen von Alyst3r)'\n",
     "       De = 'WotLKExtensions.dll beim Start laden (Client-Erweiterungen von Alyst3r)'\n"),
    ("       En = 'Enable WotLKExtensions.dll support (client extensions by Alyst3r)'\n",
     "       En = 'Load WotLKExtensions.dll at startup (client extensions by Alyst3r)'\n"),
    ("       De = 'voice.dll beim Start laden (mod-voicechat) [ALPHA]'\n       En = 'Load voice.dll at startup (mod-voicechat) [ALPHA]'\n"
     "       NoteDe = 'Modul noch unfertig'\n       NoteEn = 'module not finished yet'\n",
     "       De = 'voice.dll beim Start laden (Voice-Chat von St0ny) [BETA]'\n       En = 'Load voice.dll at startup (voice chat by St0ny) [BETA]'\n"
     "       NoteDe = 'benoetigt mod-voicechat'\n       NoteEn = 'requires mod-voicechat'\n"),
    ("        # ALPHA - das Modul mod-voicechat ist noch nicht fertig. Laedt\n",
     "        # BETA - das Modul mod-voicechat ist noch nicht fertig. Laedt\n"),
    ("#  Helfer fuer den voice.dll-Loader (mod-voicechat, ALPHA)\n",
     "#  Helfer fuer den voice.dll-Loader (mod-voicechat, BETA)\n")):
    s = once(s, a, b, 'Skript')
assert 'ALPHA' not in s, 'ALPHA noch im Skript'
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
# ---- Doku
URL = 'https://github.com/Raz0r1337/mod-voicechat'
for fn, pairs in (
  ('docs/README.de.md', [
    ("AwesomeWotlkLib.dll Unterstützung aktivieren (Client-Erweiterungen von noname08662)", "AwesomeWotlkLib.dll beim Start laden (Client-Erweiterungen von noname08662)"),
    ("WotLKExtensions.dll Unterstützung aktivieren (Client-Erweiterungen von Alyst3r)", "WotLKExtensions.dll beim Start laden (Client-Erweiterungen von Alyst3r)"),
    ("voice.dll beim Start laden (mod-voicechat) [ALPHA] *(Modul noch unfertig, [mod-voicechat](" + URL + "))*",
     "voice.dll beim Start laden (Voice-Chat von St0ny) [BETA] *(benötigt [mod-voicechat](" + URL + "))*")]),
  ('docs/README.md', [
    ("Enable AwesomeWotlkLib.dll support (client extensions by noname08662)", "Load AwesomeWotlkLib.dll at startup (client extensions by noname08662)"),
    ("Enable WotLKExtensions.dll support (client extensions by Alyst3r)", "Load WotLKExtensions.dll at startup (client extensions by Alyst3r)"),
    ("Load voice.dll at startup (mod-voicechat) [ALPHA] *(module not finished yet, [mod-voicechat](" + URL + "))*",
     "Load voice.dll at startup (voice chat by St0ny) [BETA] *(requires [mod-voicechat](" + URL + "))*")]),
  ('docs/PATCHES.de.md', [
    ("**AwesomeWotlkLib.dll Unterstützung aktivieren (Client-Erweiterungen von noname08662)**", "**AwesomeWotlkLib.dll beim Start laden (Client-Erweiterungen von noname08662)**"),
    ("**WotLKExtensions.dll Unterstützung aktivieren (Client-Erweiterungen von Alyst3r)**", "**WotLKExtensions.dll beim Start laden (Client-Erweiterungen von Alyst3r)**"),
    ("**voice.dll beim Start laden (mod-voicechat) [ALPHA]**", "**voice.dll beim Start laden (Voice-Chat von St0ny) [BETA]**"),
    ("> [!CAUTION]\n> **ALPHA** – das Modul mod-voicechat ist noch nicht fertig. Deshalb ist dieser\n> Patch standardmäßig abgewählt.\n",
     "> [!WARNING]\n> **BETA** – das Modul mod-voicechat ist noch nicht fertig. Deshalb ist dieser\n> Patch standardmäßig abgewählt und vorerst nur in den dev-Zweigen, nicht in\n> `st0ny-main`.\n")]),
  ('docs/PATCHES.en.md', [
    ("**Enable AwesomeWotlkLib.dll support (client extensions by noname08662)**", "**Load AwesomeWotlkLib.dll at startup (client extensions by noname08662)**"),
    ("**Enable WotLKExtensions.dll support (client extensions by Alyst3r)**", "**Load WotLKExtensions.dll at startup (client extensions by Alyst3r)**"),
    ("**Load voice.dll at startup (mod-voicechat) [ALPHA]**", "**Load voice.dll at startup (voice chat by St0ny) [BETA]**"),
    ("> [!CAUTION]\n> **ALPHA** – the mod-voicechat module is not finished yet. That is why this\n> patch is deselected by default.\n",
     "> [!WARNING]\n> **BETA** – the mod-voicechat module is not finished yet. That is why this\n> patch is deselected by default and only in the dev branches for now, not in\n> `st0ny-main`.\n")])):
    p = wt + '/' + fn
    s = open(p, encoding='utf-8', newline='').read(); assert '\r' not in s
    for a, b in pairs: s = once(s, a, b, fn)
    assert 'ALPHA' not in s, 'ALPHA noch in ' + fn
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('Namen OK')

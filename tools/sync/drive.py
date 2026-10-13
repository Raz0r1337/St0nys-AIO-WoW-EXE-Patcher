# Interaktiver Lauf im Pseudo-Terminal: python3 drive.py <ordner> <log> <regel>...
# Regel = "regex=>antwort". Bei jeder neuen Ausgabe feuert die erste passende
# Regel (Puffer wird danach geleert). Ende, wenn der Prozess endet.
import os, pty, sys, time, re, select, fcntl, termios, struct
S = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad'
wd, logf = sys.argv[1], sys.argv[2]
rules = [r.split('=>', 1) for r in sys.argv[3:]]
pid, fd = pty.fork()
if pid == 0:
    os.environ['TERM'] = 'xterm-256color'
    os.chdir(wd)
    os.execv(S + '/pwsh/pwsh', [S + '/pwsh/pwsh', '-NoProfile', '-File', './apply_patches.ps1'])
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', 60, 200, 0, 0))
allout = b''; buf = b''; fired = []
def clean(b): return re.sub(rb'\x1b\[[0-9;?]*[a-zA-Z]', b'', b).decode('utf-8', 'replace').replace('\r', '')
end = time.time() + 400
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 0.3)
    if r:
        try: data = os.read(fd, 65536)
        except OSError: break
        if not data: break
        if b'\x1b[6n' in data: os.write(fd, b'\x1b[20;1R')
        buf += data; allout += data
        continue
    lines = [l for l in clean(buf).split('\n') if l.strip()]
    if not lines: continue
    last = lines[-1]
    for pat, send in rules:
        if re.search(pat, last):
            fired.append(send); buf = b''
            time.sleep(0.2); os.write(fd, send.encode() + b'\r')
            break
if time.time() >= end:
    os.kill(pid, 9)
    print('ZEITUEBERSCHREITUNG, letzte Zeile:', repr([l for l in clean(buf).split('\n') if l.strip()][-1:]))
_, status = os.waitpid(pid, 0)
open(logf, 'w').write(clean(allout))
print('exit', os.waitstatus_to_exitcode(status), 'Antworten:', [f if f else '<ENTER>' for f in fired])

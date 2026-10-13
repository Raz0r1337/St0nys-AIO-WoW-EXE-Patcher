#!/bin/bash
# $1 = repo dir
S=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad
cd "$1" && rm -f *.zip release-notes.md
export PATH=$S/rel/stub:$S/tools/adv/usr/bin:$PATH REPO_URL=https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher GITHUB_SHA=$(git rev-parse HEAD)
bash $S/pkg/body2.sh

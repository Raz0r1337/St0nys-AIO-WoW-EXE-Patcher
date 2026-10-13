set -euo pipefail
name=St0nys-AIO-WoW-EXE-Patcher

# Dieser Commit hat schon ein Release (z. B. erneuter Lauf): nichts zu tun.
if git tag --points-at HEAD | grep -q '^v[0-9]'; then
  echo "Commit is already released."
  exit 0
fi

# Version = Datum nach deutscher Zeit, ein zweites Release am selben Tag
# bekommt .2 usw.
day=$(TZ=Europe/Berlin date +%Y.%m.%d)
version=$day
n=1
while git rev-parse -q --verify "refs/tags/v$version" >/dev/null; do
  n=$((n + 1))
  version="$day.$n"
done
tag="v$version"
zip="$name-$version.zip"

# ZIP mit allen Dateien ausser denen, die mit einem Punkt beginnen (auch in
# Unterordnern). Deflate in hoechster Stufe, danach mit zopfli (advzip)
# nachverdichtet - bleibt ein normales ZIP, das jedes Programm oeffnet.
git ls-files -z | grep -zv -E '(^|/)\.' | xargs -0 zip -q -9 -X -D "$zip"
if sudo apt-get update -qq >/dev/null 2>&1 && sudo apt-get install -y -qq advancecomp >/dev/null 2>&1; then
  advzip -z -4 -q "$zip"
else
  echo "advancecomp not available, keeping zip -9."
fi
unzip -tq "$zip"
sha=$(sha256sum "$zip" | cut -d' ' -f1)

# Aenderungen: Commit-Titel seit dem letzten Release, ohne Merges und ohne
# doppelte Titel.
prev=$(git describe --tags --abbrev=0 --match 'v[0-9]*' 2>/dev/null || true)
if [ -n "$prev" ]; then
  changes_title="Changes since the last release"
  changes=$(git log --no-merges --format='%s%x09%h' "$prev..HEAD" |
    awk -F '\t' '!seen[$1]++ { printf "- %s (%s)\n", $1, $2 }')
else
  changes_title="Changes"
  changes=$(printf -- '- First automatic release\n'; git log -1 --no-merges --format='- %s (%h)')
fi
[ -n "$changes" ] || changes="- No new changes"

docs="$REPO_URL/blob/$tag/docs"
{
  printf 'Automatic build from `st0ny-main` (commit `%s`).\n\n' "$(git rev-parse --short HEAD)"
  printf '### %s\n%s\n\n' "$changes_title" "$changes"
  printf '%s\n' \
    '### Download & start' \
    'Unpack the ZIP into your WoW folder (where `Wow.exe` is) and double-click' \
    '`patcher.bat`. The first run needs an original, unmodified `Wow.exe`' \
    '3.3.5a (build 12340).' \
    ''
  if [ -f patcher.sh ]; then
    printf 'Linux: `./patcher.sh` with PowerShell 7, see the [README](%s/README.md#on-linux).\n\n' "$docs"
  fi
  printf 'Docs: [English](%s/README.md) · [Deutsch](%s/README.de.md)\n\n' "$docs" "$docs"
  printf 'SHA256 (ZIP): `%s`\n\n---\n\n' "$sha"
  printf '%s\n' \
    '> [!WARNING]' \
    '> **Use at your own risk.** Patches rated safe (🟢) have been tested in game and' \
    '> should be harmless on public servers as well – but there is no 100 %' \
    '> guarantee: what is detected and tolerated on a server is up to its operator' \
    '> and may change from time to time. All other patches carry a uniform warning in'
  printf '> the overview and in the patcher (see [Notes](%s/README.md#notes)). If in\n' "$docs"
  printf '%s\n' \
    '> doubt, check the rules of your server before using a patched `Wow.exe` there.' \
    '> The patcher also shows this note on every start. This project is not' \
    '> affiliated with Blizzard Entertainment.'
} > release-notes.md

gh release create "$tag" "$zip" --target "$GITHUB_SHA" \
  --title "$name $version" --notes-file release-notes.md --latest

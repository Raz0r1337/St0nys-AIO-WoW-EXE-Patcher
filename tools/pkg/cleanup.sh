set -euo pipefail
# Es soll immer nur ein Release geben: alle aelteren samt Tag loeschen.
tags=$(gh api "repos/$GITHUB_REPOSITORY/releases?per_page=100" --jq 'sort_by(.created_at) | reverse | .[].tag_name')
newest=${tags%%$'\n'*}
printf '%s\n' "$tags" | tail -n +2 | while read -r tag; do
  [ -n "$tag" ] || continue
  echo "Deleting old release $tag (newest: $newest)"
  gh release delete "$tag" --repo "$GITHUB_REPOSITORY" --yes --cleanup-tag
done

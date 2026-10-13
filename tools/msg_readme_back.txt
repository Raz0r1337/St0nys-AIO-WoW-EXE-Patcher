Back to docs/README.md: GitHub ignores README.en.md

The test in 0266771 showed that GitHub finds no README at all on the
branch when the files are called README.en.md and README.de.md (README
API returns 404 for the branch and for docs/). So the English README is
called README.md again and all links point back to it.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

## What this changes

<!-- e.g. "Adds RELEASE.2025-xx-xx". -->

## Checklist

- [ ] Commits come from `scripts/resolve-release.sh` (the peeled commit, not the tag object)
- [ ] Matrix row added/updated in `.github/workflows/build.yml`
- [ ] README tag table updated
- [ ] CI is green: build + smoke test for every release
- [ ] No secrets, credentials or private hostnames anywhere in the diff

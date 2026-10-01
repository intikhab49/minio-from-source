#!/usr/bin/env bash
# Print the commit a MinIO release tag points to, for the Dockerfile's
# MINIO_COMMIT / MC_COMMIT.
#
#   scripts/resolve-release.sh minio RELEASE.2025-10-15T17-29-55Z
#   scripts/resolve-release.sh mc    latest
#
# Why this exists: some MinIO tags are annotated. For those,
# `git ls-remote <repo> refs/tags/<tag>` returns the TAG OBJECT, not the
# commit, and pinning it makes the build's commit check fail. The commit is
# `refs/tags/<tag>^{}` when that line exists, and the plain ref otherwise
# (lightweight tags). This script does that lookup for you.
set -euo pipefail

component=${1:?usage: resolve-release.sh <minio|mc> <RELEASE tag|latest>}
tag=${2:?usage: resolve-release.sh <minio|mc> <RELEASE tag|latest>}
case "$component" in
  minio | mc) ;;
  *) echo "unknown component: $component" >&2; exit 2 ;;
esac
repo="https://github.com/minio/$component"

if [[ "$tag" == latest ]]; then
  # Only the current RELEASE.YYYY-MM-DDTHH-MM-SSZ format; mc also has
  # pre-2016 tags in another format that would sort wrong.
  tag=$(git ls-remote --tags "$repo" 'refs/tags/RELEASE.*' \
    | sed -nE 's#.*refs/tags/(RELEASE\.[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z)$#\1#p' \
    | sort | tail -1)
fi

refs=$(git ls-remote "$repo" "refs/tags/$tag" "refs/tags/$tag^{}")
if [[ -z "$refs" ]]; then
  echo "no tag $tag in $repo" >&2
  exit 1
fi
peeled=$(printf '%s\n' "$refs" | awk '$2 ~ /\^\{\}$/ {print $1}')
commit=${peeled:-$(printf '%s\n' "$refs" | awk 'NR == 1 {print $1}')}

echo "$tag $commit"

#!/bin/sh
# Build one MinIO component from source at a pinned release, inside the
# Dockerfile's build stage.
#
#   build-component <minio|mc> <RELEASE tag> <expected commit> <output path>
#
# Fails if the tag no longer resolves to the expected commit.
set -eu

component=$1
tag=$2
commit=$3
out=$4

case "$component" in
  minio | mc) ;;
  *) echo "unknown component: $component" >&2; exit 2 ;;
esac

# RELEASE.2025-10-15T17-29-55Z -> 2025-10-15T17:29:55Z
release_time=$(printf '%s' "$tag" | sed -nE 's/^RELEASE\.([0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2})-([0-9]{2})-([0-9]{2})Z$/\1T\2:\3:\4Z/p')
if [ -z "$release_time" ]; then
  echo "not a RELEASE.YYYY-MM-DDTHH-MM-SSZ tag: $tag" >&2
  exit 2
fi

src=/src/$component
git clone --quiet --depth 1 --branch "$tag" "https://github.com/minio/$component" "$src"
actual=$(git -C "$src" rev-parse HEAD)
if [ "$actual" != "$commit" ]; then
  echo "$component $tag is commit $actual, expected $commit; refusing to build" >&2
  exit 1
fi

cd "$src"
# The ldflags generator runs on the build machine, so compute it before
# setting the target platform. MINIO_RELEASE / MC_RELEASE must be the plain
# prefix "RELEASE" here; anything else ends up inside the version string.
prefix_var=$(printf '%s' "$component" | tr 'a-z' 'A-Z')_RELEASE
ldflags=$(env "$prefix_var=RELEASE" go run buildscripts/gen-ldflags.go "$release_time")
GOOS=${TARGETOS:-linux} GOARCH=${TARGETARCH:-amd64} \
  go build -tags kqueue -ldflags "$ldflags" -o "$out" .
echo "built $component $tag ($commit) for ${TARGETOS:-linux}/${TARGETARCH:-amd64}"

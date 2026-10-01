#!/usr/bin/env bash
# Start an image, prove the server and mc work, and check the version strings.
#
#   scripts/smoke-test.sh <image> <expected MinIO RELEASE tag>
set -euo pipefail

image=${1:?usage: smoke-test.sh <image> <RELEASE tag>}
tag=${2:?usage: smoke-test.sh <image> <RELEASE tag>}
name=mfs-smoke-$$

cleanup() { docker rm -f "$name" >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker run -d --name "$name" -p 127.0.0.1::9000 \
  -e MINIO_ROOT_USER=smoketest -e MINIO_ROOT_PASSWORD=smoketest-password \
  "$image" >/dev/null
port=$(docker port "$name" 9000/tcp | sed -E 's/.*:([0-9]+)$/\1/' | head -1)

for _ in $(seq 1 30); do
  curl -fsS "http://127.0.0.1:$port/minio/health/live" >/dev/null 2>&1 && break
  sleep 1
done
curl -fsS "http://127.0.0.1:$port/minio/health/live" >/dev/null || {
  docker logs "$name"; echo "FAIL: server never became healthy" >&2; exit 1; }

version=$(docker exec "$name" minio --version | head -1)
echo "$version"
# Exactly "minio version RELEASE.<tag> (commit-id=...)": a doubled date means
# the build leaked MINIO_RELEASE into the version prefix.
if [[ "$version" != "minio version $tag (commit-id="* ]]; then
  echo "FAIL: unexpected version string" >&2; exit 1
fi
docker exec "$name" mc --version | head -1

docker exec "$name" sh -euc '
  mc alias set local http://localhost:9000 smoketest smoketest-password >/dev/null
  mc mb --with-lock local/smoke >/dev/null
  mc version info local/smoke | grep -q "versioning is enabled"
  printf "hello from source" | mc pipe local/smoke/hello.txt >/dev/null
  test "$(mc cat local/smoke/hello.txt)" = "hello from source"
  mc retention set --default compliance 1d local/smoke >/dev/null
  mc retention info --default local/smoke | grep -qi compliance
'
echo "PASS: health, version, lock-enabled bucket, write/read, default COMPLIANCE retention"

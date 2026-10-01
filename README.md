# minio-from-source

MinIO server + `mc`, built from MinIO's public source at a pinned release, published as a multi-arch image.

**Unofficial.** Not affiliated with or endorsed by MinIO, Inc. "MinIO" is a trademark of MinIO, Inc.; it's used here only to say what the image contains.

## Why

MinIO stopped publishing free images and binaries in October 2025. If your CI or `docker-compose.yml` pulls MinIO, you've probably seen one of these:

| Source | What you get now |
|---|---|
| `minio/minio`, `minio/mc` on Docker Hub | gone |
| `quay.io/minio/minio`, `quay.io/minio/mc` | `401` for anonymous pulls |
| `dl.min.io` binaries | `410 Gone` |

The source is still public (AGPL-3.0). This repo builds it, at an exact release you can pin, and checks every tag against the commit it must point to.

## Use it

```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=admin -e MINIO_ROOT_PASSWORD=change-me-please \
  ghcr.io/intikhab49/minio-from-source:RELEASE.2025-10-15T17-29-55Z
```

docker-compose:

```yaml
services:
  minio:
    image: ghcr.io/intikhab49/minio-from-source:RELEASE.2025-10-15T17-29-55Z
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: change-me-please
    ports: ["9000:9000", "9001:9001"]
    volumes: ["minio_data:/data"]
volumes:
  minio_data:
```

`mc` is in the same image, so bucket setup needs no second image:

```bash
docker exec minio sh -c 'mc alias set local http://localhost:9000 admin change-me-please \
  && mc mb --ignore-existing --with-lock local/my-bucket'
```

GitHub Actions (as a step, since service containers can't run `mc` setup):

```yaml
- run: |
    docker run -d --name minio -p 9000:9000 \
      -e MINIO_ROOT_USER=admin -e MINIO_ROOT_PASSWORD=change-me-please \
      ghcr.io/intikhab49/minio-from-source:RELEASE.2025-10-15T17-29-55Z
    until curl -fsS http://localhost:9000/minio/health/live; do sleep 1; done
```

## Tags

| Tag | MinIO | mc |
|---|---|---|
| `RELEASE.2025-10-15T17-29-55Z`, `latest` | `RELEASE.2025-10-15T17-29-55Z` (`9e49d5e`) | `RELEASE.2025-08-13T08-35-41Z` (`7394ce0`) |
| `RELEASE.2025-09-07T16-13-09Z` | `RELEASE.2025-09-07T16-13-09Z` (`07c3a42`) | `RELEASE.2025-08-13T08-35-41Z` (`7394ce0`) |

`linux/amd64` and `linux/arm64`. Pin the release tag, not `latest`. Every image has build provenance and an SBOM attached.

## Build it yourself

```bash
docker build -t minio-from-source .   # defaults to the newest release above
```

Another release:

```bash
scripts/resolve-release.sh minio RELEASE.2025-09-07T16-13-09Z
# RELEASE.2025-09-07T16-13-09Z 07c3a429bfed433e49018cb0f78a52145d4bedeb
docker build \
  --build-arg MINIO_TAG=RELEASE.2025-09-07T16-13-09Z \
  --build-arg MINIO_COMMIT=07c3a429bfed433e49018cb0f78a52145d4bedeb \
  -t minio-from-source:RELEASE.2025-09-07T16-13-09Z .
```

### The trap `resolve-release.sh` exists for

Some MinIO release tags are **annotated**. For those, `git ls-remote https://github.com/minio/minio refs/tags/<tag>` gives you the **tag object**, not the commit. Pin that and the build's commit check fails. The commit is `refs/tags/<tag>^{}` (and the plain ref for lightweight tags). The script picks the right one.

### The other trap

Upstream's `buildscripts/gen-ldflags.go` reads `MINIO_RELEASE` / `MC_RELEASE` from the environment as the version **prefix**. If your build has a variable with that name holding the full tag, `minio --version` comes out as `RELEASE.2025-...Z.2025-...Z`. The build here sets the prefix to plain `RELEASE`, and the smoke test fails on a doubled version.

## What CI checks

Every release in the matrix is built and then smoke-tested before anything is published:
- the server becomes healthy
- `minio --version` is exactly the pinned release
- `mc` creates a lock-enabled bucket (versioning on), writes and reads an object back, and sets a default COMPLIANCE retention

Images are pushed only from `main` of this repository, never from pull requests or forks.

## Maintenance, honestly

These images get security fixes only when someone bumps the pinned release. As of 2026-10-02 the newest upstream release tag is `RELEASE.2025-10-15T17-29-55Z`; check upstream before you rely on this in production. PRs adding newer releases are welcome: run `scripts/resolve-release.sh`, add a matrix row, update the table.

## Alternatives

- [Chainguard's MinIO images](https://www.chainguard.dev/unchained/secure-and-free-minio-chainguard-containers): built from source, free tier.
- Community mirrors of the last published images exist, but they are frozen copies, not rebuilt from source.
- If you're leaving MinIO entirely: SeaweedFS, Garage and others are S3-compatible.

## License

The build files in this repo (Dockerfile, scripts, workflow) are MIT, see [LICENSE](LICENSE). The images contain MinIO and mc, which are **AGPL-3.0**; see [NOTICE](NOTICE) for where their exact source is.

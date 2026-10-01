# MinIO server + mc, built from the public MinIO source at a pinned release.
#
# Unofficial. Not affiliated with or endorsed by MinIO, Inc.
#
# Each release tag is checked against the commit it must point to, so a moved
# or rewritten tag fails the build instead of silently changing what you run.
# Use scripts/resolve-release.sh to get the commit for any release.

# Go cross-compiles, so the build stage always runs on the builder's own
# architecture and targets TARGETOS/TARGETARCH. No QEMU needed for arm64.
FROM --platform=$BUILDPLATFORM golang:1.24-alpine AS build

RUN apk add --no-cache git

ARG TARGETOS
ARG TARGETARCH

# Deliberately NOT named MINIO_RELEASE / MC_RELEASE: upstream's
# buildscripts/gen-ldflags.go reads those env vars as the version *prefix*,
# and an ARG of that name would turn the version into "RELEASE.<tag>.<time>".
ARG MINIO_TAG=RELEASE.2025-10-15T17-29-55Z
ARG MINIO_COMMIT=9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a
ARG MC_TAG=RELEASE.2025-08-13T08-35-41Z
ARG MC_COMMIT=7394ce0dd2a80935aded936b09fa12cbb3cb8096

ENV CGO_ENABLED=0 GOFLAGS=-trimpath

# "RELEASE.2025-10-15T17-29-55Z" -> "2025-10-15T17:29:55Z", the form
# gen-ldflags.go expects, so the binary reports the official version string.
COPY --chmod=0755 scripts/build-component.sh /usr/local/bin/build-component
RUN build-component minio "$MINIO_TAG" "$MINIO_COMMIT" /out/minio
RUN build-component mc "$MC_TAG" "$MC_COMMIT" /out/mc

FROM alpine:3.20

# curl backs health checks; the shell lets one container run mc commands.
RUN apk add --no-cache ca-certificates curl \
 && addgroup -S minio && adduser -S -G minio -h /home/minio minio \
 && mkdir -p /data && chown minio:minio /data

COPY --from=build /out/minio /out/mc /usr/bin/

ARG MINIO_TAG
ARG MINIO_COMMIT
ARG MC_TAG
ARG MC_COMMIT
LABEL org.opencontainers.image.title="minio-from-source" \
      org.opencontainers.image.description="Unofficial MinIO server + mc built from public source at a pinned release" \
      org.opencontainers.image.source="https://github.com/intikhab49/minio-from-source" \
      org.opencontainers.image.licenses="AGPL-3.0-only AND MIT" \
      org.opencontainers.image.version="${MINIO_TAG}" \
      io.github.minio-from-source.minio-commit="${MINIO_COMMIT}" \
      io.github.minio-from-source.mc-tag="${MC_TAG}" \
      io.github.minio-from-source.mc-commit="${MC_COMMIT}"

USER minio
EXPOSE 9000 9001
VOLUME ["/data"]
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
  CMD curl -fsS http://localhost:9000/minio/health/live || exit 1

ENTRYPOINT ["minio"]
CMD ["server", "/data", "--console-address", ":9001"]

# Contributing

The most useful contribution is a newer upstream release.

## Add a release

1. Resolve the commit (handles annotated and lightweight tags):

   ```bash
   scripts/resolve-release.sh minio latest
   scripts/resolve-release.sh mc latest
   ```

2. Add a row to the `matrix.include` list in `.github/workflows/build.yml` with `minio_tag` and `minio_commit`. Move `latest: true` to the newest release. If `mc` changes, update `MC_TAG` / `MC_COMMIT` there and in the `Dockerfile` defaults.
3. Update the tag table in `README.md`.
4. Open a PR. CI builds and smoke-tests every release; nothing is published from a PR.

## Test locally

```bash
docker build --build-arg MINIO_TAG=... --build-arg MINIO_COMMIT=... -t mfs:test .
scripts/smoke-test.sh mfs:test RELEASE.....
```

## Ground rules

- Images are built **unmodified** from upstream. Patches to MinIO itself belong upstream.
- Keep the build reproducible: pinned tag + commit, no `latest` base downloads of MinIO.
- No MinIO logos or anything that suggests this is official.

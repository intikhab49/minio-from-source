# Security policy

## What's in scope here

This repo's Dockerfile, scripts and workflow: anything that could make an image contain something other than the pinned upstream commit, leak credentials, or publish from an untrusted source.

**Report privately:** [open a security advisory](https://github.com/intikhab49/minio-from-source/security/advisories/new). Please don't open a public issue for it.

## Vulnerabilities in MinIO itself

The images contain upstream MinIO and mc unmodified. Report MinIO vulnerabilities to MinIO (see their repository's security policy). Once upstream ships a fixed release, open a [new-release issue](https://github.com/intikhab49/minio-from-source/issues/new?template=new_release.yml) and it will be built here.

## Supported tags

Only the tags listed in the README table are built and smoke-tested. Pin one of those, and move to newer releases as they're added.

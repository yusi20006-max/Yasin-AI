# Yasin-AI Maintenance Policy

## Purpose

This document defines the post-release maintenance contract for the Yasin-AI repository.

## Maintenance loop

1. Keep `main` green and releasable.
2. Review dependency/security alerts regularly.
3. Treat security fixes as priority patches and regression-test them.
4. Preserve API and plugin compatibility unless a change is explicitly versioned.
5. Record breaking changes in the changelog and release notes.
6. Keep deployment and rollback documentation aligned with the shipped code.
7. Remove obsolete compatibility code only through reviewed pull requests.

## Release discipline

- Every production change lands through a pull request.
- CI and security gates must pass before merge.
- Release tags must point at the exact commit intended for release.
- Never move an existing release tag to a different commit.
- A new release gets a new version tag.

See the canonical [Versioning Policy & Compatibility Model](VERSIONING_POLICY.md) for official package and contract versioning rules.

## Incident and rollback policy

For a production regression, first preserve evidence and identify the exact deployed commit. Prefer reverting the smallest offending change or rolling back to the last known-good release tag. Follow-up fixes must include a regression test where practical.

## Support boundaries

The current release does not claim untrusted remote plugin execution, distributed high availability, or externalized persistent storage. Those capabilities require dedicated design and security review before being advertised or enabled.

## End of Phase 18

Phase 18 establishes maintenance governance; it does not introduce a new runtime dependency or change application behavior.

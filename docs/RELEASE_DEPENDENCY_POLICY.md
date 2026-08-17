# Release Dependency Policy

**Status:** Active
**Scope:** Yasin ecosystem consumers of Yasin-AI

## 1. Release tags are the consumer contract

Published ecosystem consumers should depend on a released Yasin-AI tag (for example, `v1.1.4`) rather than the moving `main` branch.

A release tag identifies a stable, reproducible package revision. Commits added to `main` after a release are development work and are not implicitly part of that release.

## 2. Commit pins are allowed for unreleased integration work

A full commit SHA may be used when a consumer intentionally needs unreleased Yasin-AI changes. Such a dependency must be documented as an unreleased integration pin and must not be described as the released package version.

## 3. Public API compatibility

Consumers must use the frozen public surface documented in `docs/PUBLIC_API_CONTRACT.md`. Release tags and post-release development commits may contain implementation or documentation changes, but consumers must not depend on private modules.

## 4. Release promotion

When unreleased changes become part of the supported consumer contract:

1. validate the Yasin-AI test matrix,
2. validate real consumer smoke tests,
3. update the package version when required by the release policy,
4. create a new release tag,
5. move consumers from temporary commit pins to the new release tag.

## 5. Current release

`v1.1.4` is the current published Yasin-AI release tag. The tag resolves to commit `5140827ddf29ec281b2f8ad46cfbca52aeedab22`.

The current `main` branch is newer than `v1.1.4`; that difference is expected and must not be treated as a tag corruption or version mismatch by itself.

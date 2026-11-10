# PA-2164 Build core with setuptools and uv

## JIRA

- [PA-2164](https://anaconda.atlassian.net/browse/PA-2164)

## Decisions

- Use `setuptools.build_meta` and standard project metadata, matching
  helper_scripts. Use uv for locking, tests, builds and documentation.
- Preserve version 0.3.4, Python 3.10 support and runtime dependency ranges,
  including dateutil below 3.0.0 for compatibility with bundled botocore.
- Package only `pythonanywhere_core` in the wheel. Include the complete tests,
  fixtures, lockfile, workflow definitions and Sphinx sources in the source
  archive. Test and docs extras remain separate from runtime dependencies.
- Local act runs skip publication, artifact uploads, SSH deployment and release
  creation. Hosted release behavior remains enabled.

## Rationale

The release's Poetry installer repeatedly returned HTTP 403 while application
CI passed. This migration removes that installer and aligns PA package tooling.
Runtime code remains unchanged.

## Verification

Packaging checks failed before migration. Afterward, act ran Python 3.10 through
3.14: 236 passed, 1 skipped each, with 99.18% runtime coverage. Tag/version checks,
source and wheel builds, and docs build passed. Nine packaging checks cover
module and metadata preservation, complete test inclusion, source rebuilds and
installed-wheel imports. The existing missing `_static` docs warning remains.

## What we considered but dropped

- Retain Poetry and replace its installer: fixes the immediate download failure
  but keeps different build/development tooling from the other PA packages.

## Follow-up

The existing v0.3.4 tag points to the old workflow. Choose the next release tag
after hosted CI; this migration does not move tags or publish a release.

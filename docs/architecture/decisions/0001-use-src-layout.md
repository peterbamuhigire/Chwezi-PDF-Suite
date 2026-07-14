# ADR 0001: Use a `src` package layout

Status: proposed  
Date: 2026-07-14  
Owner: project maintainer

## Context

Production code is currently imported from the repository root, allowing tests to pass against checkout paths that may not exist in an installed wheel. The product needs one public namespace, `chwezi_docs`, while legacy scripts remain during migration.

## Options

1. Keep flat modules and add packaging metadata.
2. Move new code under `src/chwezi_docs` and retain wrappers at root.
3. Create several separately distributed packages now.

## Decision

Choose option 2. It separates importable product code from the checkout and supports a controlled compatibility layer without premature multi-package release management.

## Consequences

- New application logic belongs under `src/chwezi_docs`.
- Root scripts may import the package but may not receive new duplicated algorithms.
- Tests must install/import the package through configured paths.
- Legacy modules are migrated incrementally rather than copied wholesale.

## Verification

A built wheel imports `chwezi_docs` from a clean environment and exposes the `chwezi` entrypoint.


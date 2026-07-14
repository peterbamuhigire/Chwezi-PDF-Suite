# ADR 0004: Persist local job metadata in SQLite

Status: proposed  
Date: 2026-07-14  
Owner: job-system maintainer

## Context

JSON logs cannot support validated transitions, concurrent readers, restart recovery or retention. The first release is local and single-user; a network queue is unnecessary.

## Options

1. Continue JSON files.
2. Use SQLite for metadata/events and filesystem manifests for outputs.
3. Introduce Redis/PostgreSQL and a distributed queue.

## Decision

Choose option 2. SQLite stores job metadata, sanitised errors and audit events. Output manifests remain per job. Full document text and secrets are excluded.

## Consequences

- Schema migrations and corruption recovery need tests.
- Workers update state through a repository contract.
- Server/multi-user deployment must revisit isolation and queue topology.
- Retention can delete job data without scanning application logs.

## Verification

Integration tests cover transitions, interruption recovery, concurrent readers, retention and absence of document content/secrets.


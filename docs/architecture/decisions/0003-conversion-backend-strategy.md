# ADR 0003: Use a capability-ranked conversion graph

Status: proposed  
Date: 2026-07-14  
Owner: conversion maintainer

## Context

No single library provides high-fidelity, cross-platform support for every requested source-target pair. Current scripts hide backend and loss information.

## Options

1. Standardise on one converter for every route.
2. Register specialised in-process and external adapters in a directed graph.
3. Shell out to LibreOffice/Pandoc for every conversion.

## Decision

Choose option 2. Each edge declares requirements, fidelity, loss class and validator. Planning prefers available higher-fidelity routes and reports all selected backends.

Initial adapters may include existing extractors, pypdf/pikepdf, LibreOffice, OCRmyPDF, Pandoc, Calibre or Docling only after route-specific tests.

## Consequences

- Capability output is generated from registry/probes.
- Unsupported pairs remain explicit.
- Intermediate cycles are rejected.
- Backend selection becomes testable and configurable.
- External tools are optional and invoked through one safe subprocess adapter.

## Verification

Graph tests cover direct, multi-step, unavailable, lossy-preference and cycle cases. Every advertised route has an integration or golden test.


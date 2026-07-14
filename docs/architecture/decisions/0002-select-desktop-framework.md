# ADR 0002: Select PySide6 for the future desktop shell

Status: proposed  
Date: 2026-07-14  
Owner: project maintainer

## Context

The repository currently uses Tkinter, CustomTkinter and Textual interfaces. The target needs page previews, drag/drop, model/view lists, accessible controls, background jobs and Windows/macOS/Linux packaging.

## Options

1. Continue Tkinter/CustomTkinter.
2. Use PySide6/Qt.
3. Use wxPython or Toga.

## Decision

Propose PySide6. Qt provides the required desktop interaction model and mature worker/event patterns. This is not permission to start desktop work before application services and jobs stabilise.

## Consequences

- Desktop becomes an optional extra and bundle dependency.
- LGPL compliance, notices, dynamic-linking/bundling obligations and Qt plugin packaging require release review.
- Existing Tk GUIs remain until replacement parity.
- Accessibility and platform behaviour need manual matrix testing.

## Revisit trigger

Reject or revise if a proof-of-concept cannot meet bundle-size, accessibility, licence or macOS signing requirements.


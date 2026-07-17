# Chwezi Document Suite visual system

## Direction

The suite uses an editorial utility aesthetic: warm paper and dark ink in light mode, and
brand-tinted blue-black surfaces in dark mode. Lagoon teal marks primary actions; restrained
coral marks secondary emphasis and danger. Dark mode is a semantic remap, not an inversion.

Typography pairs Georgia for display headings with Trebuchet MS for body copy and controls.
Both are deliberate device-common Windows faces: Georgia adds an authored, bookish character
appropriate to document work, while Trebuchet remains legible at compact desktop-control sizes.
Cascadia Mono is reserved for activity logs. No font file is embedded or redistributed.

## Semantic token contract

The source of truth is `ui_theme.py` for Python interfaces and the matching CSS custom
properties in `static/css/style.css` for the local web organizer. Components consume roles such
as `surface_base`, `surface_raised`, `text_primary`, `border`, `accent`, `success`, and `danger`;
they do not hard-code theme-specific colours.

The shared theme preference is stored in the current user's application-data directory. Every
desktop tool reads it at startup, and each theme switch writes it back. The web organizer uses
the browser's saved preference, falling back to the operating-system preference.

## Component and state rules

- Primary actions use lagoon fill and outcome-specific labels.
- Cards use one-pixel borders and surface-lightness changes instead of decorative shadows.
- Every interactive control includes hover, focus, pressed, and disabled treatment.
- Status is communicated with text plus colour, never colour alone.
- Light and dark modes preserve the same hierarchy while remapping all surfaces and text.
- Motion is short and functional; reduced-motion preference disables non-essential transitions.

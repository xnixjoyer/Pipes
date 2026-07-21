# Decisions

## D-001 — Direct ANSI/terminfo output

Use `curses.setupterm`, `tigetstr`, `tigetnum`, and `tparm`, then write buffered
bytes directly. A full curses screen renderer was rejected because color-pair
limits can block parity with arbitrary 256/direct color indices and because the
original behavior is sparse cursor-addressed output.

## D-002 — Direct color

Color values remain integer indices, including packed RGB values accepted by
modern direct-color terminfo entries. The runtime does not invent RGB escape
sequences when terminfo lacks `setaf`; it falls back to no color. This keeps
terminal policy in terminfo and avoids claiming universal direct-color support.

## D-003 — Names

- Distribution and distro packages: `pipes-sh-python`
- Module and physical runtime: `pipes_sh` / `pipes_sh.py`
- Public command: `pipes.sh`
- Nix package attribute: `"pipes-sh-python"`

The public command preserves user compatibility. Package conflicts are explicit
because two packages cannot own the same executable path.

## D-004 — Version 2.0.0

The rewrite starts at 2.0.0 due to language/runtime replacement, packaging
change, terminal implementation change, deterministic model API, and deliberate
legacy corrections. `pipes_sh.VERSION` is canonical.

## D-005 — Signal exit codes

Normal key exit returns 0. INT, TERM, and HUP return `128 + signal` after cleanup.
This differs from historical cleanup, which forced zero, and makes automation
able to distinguish termination.

## D-006 — Immediate style toggles

Historical `B`/`C` flags do not rebuild precomputed styles. The documented intent
is used instead: renderer recomputes style for every command from live options.

## D-007 — Reset counts glyphs

`-r N` means exactly drawn pipe characters. Multiple pipes can reach a limit
inside one logical frame; a clear request is emitted in that frame and the
counter resets. This is more faithful to documentation than historical `t*p`.

## D-008 — Straight-probability compatibility

CLI remains 5..15. Interactive `O` can lower to 3 because that historical
behavior was intentional enough to be user-visible and does not compromise
safety.

## D-009 — Custom Unicode safety

Exactly 16 Unicode codepoints are required. Controls, combining glyphs, and
East Asian wide/fullwidth glyphs are rejected. This is a documented tightening
of historical validation to preserve the one-cell transition grid.

## D-010 — Licensing and credits

`LICENSE` is unchanged. New runtime files carry SPDX MIT plus all historical
copyright lines and a separate 2026 rewrite notice. Documentation identifies the
rewrite as unofficial and never represents xnixjoyer as original author.

## D-011 — No runtime subprocesses or writes

Runtime imports and behavior are limited to terminal I/O, terminfo, timing,
signals, locale, and in-memory randomness. Subprocess is allowed only in tests.
Persistent state is deliberately absent.

## D-012 — Migration safety

Historical SHA is backed up before changes. Rewrite targets `main` through a PR.
No branch is deleted automatically. Annotated tag creation and default-branch
switch require a capability not exposed by the current connector and therefore
must remain visibly incomplete until performed and verified.

# Python architecture

`pipes_sh.py` is intentionally the only runtime file. Logical sections are kept
separate so pure model behavior can be tested without a terminal.

## Constants and records

- `VERSION` is canonical.
- `PIPE_SETS`, `DIRECTION_VECTORS`, defaults, and bounds define compatibility.
- `Options` contains mutable runtime toggles and parsed values.
- `PipeState` holds one pipe's position, direction, selected type, and color.
- `DrawCommand` and `FrameResult` form the terminal-independent render model.

## Pure functions

- `natural_number`, `parse_color`, `validate_custom_type`, and `parse_type`
  validate values without terminal work.
- `parse_options` has no TTY requirement and returns control actions for help,
  version, and self-test.
- `transition_index`, `choose_direction`, and `wrap_position` encode the model.
- `apply_key` mutates only `Options` and reports whether animation continues.

Pure functions must remain deterministic when passed a deterministic RNG.

## Engine

`Engine` owns `random.Random`, terminal dimensions, drawn-character count, and
all `PipeState` objects. `step()` returns immutable draw commands; it never emits
bytes. `resize()` clamps dimensions to at least one and normalizes all positions.

Engine invariants after initialization and every step:

- `width >= 1`, `height >= 1`.
- `0 <= x < width`, `0 <= y < height`.
- direction is in 0..3.
- type/color selection indices are valid.
- no reverse turn is generated.
- state collections are fixed-size relative to `Options.pipes`.

## TerminalCapabilities

`TerminalCapabilities.load()` is the only terminfo setup point. It obtains
`cup`, clear, alternate-screen, cursor, SGR, bold, `setaf`, and color count.
`tparm` is used for cursor and color parameters. Cursor fallback converts model
zero-based coordinates to ANSI one-based coordinates. Missing color capability
produces no-color output rather than a traceback.

## TerminalSession

`TerminalSession` owns mutable operating-system terminal state. Start order:

1. Save termios.
2. Enter cbreak while preserving signal generation.
3. Install handlers for INT, TERM, HUP, WINCH.
4. Enter alternate screen, hide cursor, clear.

Cleanup is guarded by `cleaned`, making repeated calls harmless. It emits SGR
reset, shows cursor, exits alternate screen, restores termios, and restores all
saved handlers. Do not add application logic to this class.

## Renderer

`Renderer` converts a `FrameResult` into one buffered byte string and one
`os.write` call. Style is generated for each command from current `Options`,
which is why keyboard toggles become visible immediately. It contains no random,
movement, reset, or key logic.

## App

`App` coordinates monotonic timing, `select`, keys, resize, engine, and renderer.
It advances a target timestamp rather than sleeping a fixed duration after work.
If delayed by more than four frame intervals it resynchronizes to avoid a burst.
Signals are recorded by `TerminalSession` and converted to `128 + signal`.

## Entry point

`main(argv=None)` parses before preflight. Help, version, and self-test return
without TTY or terminfo. Interactive execution then performs preflight, loads
terminfo, validates color bounds, creates components, and runs inside a context
manager. Importing the module performs no terminal initialization.

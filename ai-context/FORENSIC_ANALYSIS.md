# Forensic analysis of historical `master`

## Repository baseline

- Repository: `xnixjoyer/Pipes`
- Historical default branch: `master`
- Historical head SHA: `581792d4e0ea51e15889ba14a85db1bc9727b83d`
- Historical version: `1.3.0`
- Primary runtime: `pipes.sh`
- Historical CI: Travis via `.travis.yml` and `scripts/travis-script.sh`
- Tests: shunit2-style scripts started by `test/run_tests.sh`
- Benchmark intent: run model logic without terminal rendering and report characters/second
- License: MIT with Matthew Simpson, Yu-Jie Lin, and Pipeseroni contributor notices

The backup branch `backup/master-before-python-rewrite-20260721` points to the
historical SHA. `main` and `rewrite/python-single-file` were created from the
same SHA before rewrite changes.

## Bash architecture and global state

`pipes.sh` is a single Bash script with mutable global arrays and scalars:

- Geometry/timing: `p`, `f`, `s`, `r`, `t`, `w`, `h`.
- Pipe state arrays: `x`, `y`, `l` (old direction), `n` (new direction), `v`
  (type index), and `c` (precomputed style sequence).
- Selection arrays: `V` (selected type indices), `C` (color indices), `E`
  (precomputed style sequences), `SETS` (flattened glyphs).
- Switches: `RNDSTART`, `BOLD`, `NOCOLOR`, `KEEPCT`.
- Terminal capabilities: `COLORS`, `SGR0`, and `SGR_BOLD`, obtained from `tput`.

Functions are `print_help`, `parse`, `cleanup`, `resize`, `init_pipes`,
`init_screen`, and `main`. Nested parse helpers validate decimal and hex input.

## CLI matrix

| Option | Historical validation | Default | Rewrite rule |
|---|---|---:|---|
| `-p` | decimal > 0 | 1 | preserved |
| `-t` | 0..9 or `c` + 16 Bash characters | 0 | 16 Unicode codepoints plus cell-safety validation |
| `-c` | decimal/hex less than `tput colors` | 1..7,0 | preserved, validated before terminal mutation |
| `-f` | 20..100 | 75 | preserved |
| `-s` | 5..15 | 13 | preserved; interactive minimum remains 3 |
| `-r` | decimal >= 0 | 2000 | preserved; now counts actual drawn characters |
| `-R` | flag | off | preserved |
| `-B` | flag | bold on | preserved |
| `-C` | flag | color on | preserved |
| `-K` | flag | off | preserved |
| `-h` | help | — | preserved plus `--help` |
| `-v` | version | — | preserved plus `--version` |
| — | — | — | added `--self-test` and `--seed` |

Positionals are rejected.

## Glyphs and state machine

The historical ten strings are preserved exactly and each has 16 entries.
Directions are `0=up`, `1=right`, `2=down`, `3=left`. The transition glyph is
indexed by `old * 4 + new`. Four reverse-direction cells exist as placeholders,
but the random direction algorithm generates only straight, left, or right.

Per pipe, historical frame behavior is:

1. Move in the old direction.
2. Detect an edge crossing.
3. Unless keep mode is active, randomize style/type on crossing.
4. Wrap with modulo width/height.
5. Choose straight with probability `(s-1)/s`; otherwise left or right.
6. Print the glyph at one-based ANSI coordinates.
7. Store the new direction.

The rewrite preserves this order. It clamps transient zero-sized resize results
to 1×1 before modulo operations.

## Initialization and distribution

Without `-R`, all pipes start at terminal center facing up. With `-R`, position
and direction are randomized. Selected types and colors are assigned cyclically
from a random starting offset unless keep mode is active, where offset zero is
used. The rewrite preserves that distribution policy using a local
`random.Random` instance, enabling deterministic seeds.

## Terminal behavior

Historical runtime processes:

- `tput sgr0`, `colors`, `bold`, `setaf`, `smcup`, `civis`, `clear`, `reset`,
  `rmcup`, `cnorm`, `cols`, and `lines`.
- `stty -echo` and `stty echo`.
- shell `read` for timing and key input.

Historical signal handling traps HUP and TERM for cleanup, SIGWINCH for resize,
and INT to break the loop. Cleanup runs `tput reset`, exits the alternate screen,
shows the cursor, reenables echo, and emits SGR reset.

The rewrite replaces external processes with Python `curses` terminfo,
`termios`, `tty`, `select`, `signal`, and `os.write`. It preserves the alternate
screen and cursor behavior where capabilities exist, with controlled ANSI
fallbacks.

## Known and suspected historical defects

1. **Bold/color toggle discrepancy:** style strings in `E` are generated once.
   Keys `B` and `C` mutate flags but do not regenerate existing `E` or per-pipe
   `c`, so documented immediate toggles can be invisible. The rewrite computes
   style during every rendered command, so toggles take effect immediately.
2. **Reset semantics:** the Bash condition uses `t * p >= r` after a complete
   frame. This is an approximation and may overshoot, especially with multiple
   pipes. The rewrite counts each emitted glyph and requests clear at the limit.
3. **Resize modulo risk:** a transient zero column/line result can make Bash
   modulo invalid. The rewrite clamps dimensions to at least one.
4. **Cleanup exit status:** historical `cleanup` always exits zero, including
   TERM/HUP. The rewrite returns conventional `128 + signal` status.
5. **TTY preflight:** the historical script relies mostly on `tput` failure and
   may change state in unsuitable environments. The rewrite explicitly checks
   stdin/stdout TTY and TERM before session start.
6. **Custom glyph width:** Bash accepts exactly 16 shell characters without
   excluding control, combining, or wide glyphs. The rewrite rejects clearly
   grid-breaking input and documents remaining font/terminal dependence.
7. **Timing drift:** Bash formats a fractional `read -t` timeout each loop. The
   rewrite uses monotonic target times and controlled resynchronization.

## Documentation differences

- Historical README points to the generated manpage for full options and labels
  screenshots without distinguishing implementation generation.
- The manpage describes `-r` as resetting after characters, while implementation
  approximates by frame count times pipe count.
- README/manpage promise working `B`/`C` toggles; implementation does not rebuild
  styles.
- CLI `-s` minimum is 5, while interactive `O` permits values down to 3.

These differences are now explicit in README, manpage, tests, and decisions.

## Dependencies, platform, and writes

Historical runtime requires Bash 4+, external ncurses `tput`, `stty`, and POSIX
terminal behavior. The Python runtime requires Python 3.10+, POSIX `termios`, and
terminfo for interactive mode. It has no network imports, subprocess calls,
plugin loading, serialization, FFI, `eval`, `exec`, or persistent writes.

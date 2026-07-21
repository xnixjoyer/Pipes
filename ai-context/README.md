# AI maintainer context

This directory is the canonical hand-off for maintainers and coding agents.
Read these files in order before changing runtime behavior, packaging, or repository structure:

1. [`FORENSIC_ANALYSIS.md`](FORENSIC_ANALYSIS.md) — behavior extracted from the historical Bash source.
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) — responsibilities and invariants of `pipes_sh.py`.
3. [`DECISIONS.md`](DECISIONS.md) — decisions that must not be reversed accidentally.
4. [`TESTING.md`](TESTING.md) — exact commands, results, failures, and environmental gaps.
5. [`MIGRATION_PLAN.md`](MIGRATION_PLAN.md) — branch, packaging, CI, and release status.
6. [`NIX_TROUBLESHOOTING.md`](NIX_TROUBLESHOOTING.md) — profile installation, Fish `PATH`, and failure classification.
7. [`CLEANUP_PLAN.md`](CLEANUP_PLAN.md) — files retained or removed after the rewrite.

## Non-negotiable invariants

- `LICENSE` remains byte-for-byte historical MIT text.
- Historical copyright notices stay in substantial derived files.
- The rewrite is unofficial and independent.
- `pipes_sh.py` is the only runtime module and performs no terminal work at import time.
- Runtime code never launches subprocesses or writes persistent files.
- Invalid CLI values are rejected before terminal mode changes.
- Cleanup is idempotent and restores termios, cursor, alternate screen, SGR, and handlers.
- `pipes_sh.VERSION` is the canonical version.
- The only installed public command is `pipes`; no `pipes.sh` alias, wrapper, or symlink is shipped.
- Package and distribution names remain `pipes-sh-python` unless a separately tested migration changes them.
- Nix, Wheel, Arch, and Fedora packages must contain `pipes` and reject stale `pipes.sh` paths.
- All AI hand-off documents remain together inside `ai-context/`.

## Where to resume

Start by reading the newest entries in `TESTING.md`, `MIGRATION_PLAN.md`, and the
latest GitHub Actions result. Never mark an item complete based only on the
presence of code. A packaging target is complete only after its build, content
inspection, installation, command smoke tests, and self-test are recorded with an
actual result.

For a runtime defect, record: command, TERM, Python version, terminal dimensions,
seed, relevant options, observed exit code, whether terminal restoration passed,
and the smallest deterministic reproduction. Add a regression test before or
with the fix.

For a Nix profile report, first distinguish a missing package executable from a
shell `PATH` problem using `NIX_TROUBLESHOOTING.md`. A direct profile path that
works must not be reported as a package-output failure.

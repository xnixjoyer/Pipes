# AI maintainer context

This directory is the canonical hand-off for maintainers and coding agents.
Read these files in order before changing runtime behavior or packaging:

1. [`FORENSIC_ANALYSIS.md`](FORENSIC_ANALYSIS.md) — behavior extracted from the historical Bash source.
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) — responsibilities and invariants of `pipes_sh.py`.
3. [`DECISIONS.md`](DECISIONS.md) — decisions that must not be reversed accidentally.
4. [`TESTING.md`](TESTING.md) — exact commands, results, and environmental gaps.
5. [`MIGRATION_PLAN.md`](MIGRATION_PLAN.md) — branch, packaging, CI, and release status.

## Non-negotiable invariants

- `LICENSE` remains byte-for-byte historical MIT text.
- Historical copyright notices stay in substantial derived files.
- The rewrite is unofficial and independent.
- `pipes_sh.py` is the only runtime module and performs no terminal work at import time.
- Runtime code never launches subprocesses or writes persistent files.
- Invalid CLI values are rejected before terminal mode changes.
- Cleanup is idempotent and restores termios, cursor, alternate screen, SGR, and handlers.
- `pipes_sh.VERSION` is the canonical version.
- The public command is `pipes.sh`; package/distribution names are `pipes-sh-python`.

## Where to resume

Start by reading the latest `TESTING.md` entry and GitHub Actions result. Never
mark an item complete based only on the presence of code. A packaging target is
complete only after its build, content inspection, installation, command smoke
tests, and self-test are recorded with an actual result.

For a runtime defect, record: command, TERM, Python version, terminal dimensions,
seed, relevant options, observed exit code, whether terminal restoration passed,
and the smallest deterministic reproduction. Add a regression test before or
with the fix.

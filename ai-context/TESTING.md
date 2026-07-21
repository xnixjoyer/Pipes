# Testing record

This file distinguishes tests actually executed from tests represented only by
configuration. Update it after every meaningful run.

## Local environment

- Date: 2026-07-21
- Python: 3.13.5
- Network from execution container: unavailable
- Nix: unavailable
- `makepkg`: unavailable
- `rpmbuild`: unavailable
- Python `build` module: unavailable

## Executed successfully locally

```bash
python3 -m py_compile pipes_sh.py
python3 pipes_sh.py --version
python3 pipes_sh.py --help
python3 pipes_sh.py --self-test
python3 -m unittest discover -s tests -v
python3 -O pipes_sh.py --self-test
```

Results before the final OpenPTY addition:

- Version output: `pipes.sh 2.0.0`
- Self-test output: `pipes.sh self-test: PASS`
- Unit/model/integration suite: 29 tests, all passed
- Exact reset boundaries: passed for one and multiple clear points inside a
  multi-pipe frame; renderer ordering is regression-tested
- PTY: startup with `TERM=xterm-256color`, deterministic seed, ASCII type,
  no-color mode, normal key exit, `SIGINT`, `SIGTERM`, `SIGHUP`, and 1×1
  resize; passed with conventional signal exit codes, no traceback, and no zero
  cursor coordinates

The 30th OpenPTY restoration test was then executed individually and passed. It
confirmed Echo is disabled while running and the complete original `termios`
attribute vector is restored after normal exit. GitHub Actions subsequently ran
the complete 30-test suite on Python 3.10 and 3.13.

Python emitted `pty.fork`/`os.fork` deprecation warnings under Python 3.13
because the host process is multi-threaded; they did not affect the results.

## PR #1 acceptance before merge

Final PR #1 head: `408b56006710f6ceec785aa1fcfba7d152fcc262`

### Nix run `29859100015`

- lock metadata without rewriting
- Nix formatting
- `nix flake check`
- package build
- installed help, version, and self-test
- local `nix run`
- exact-commit remote build
- exact-commit remote run
- exact-commit profile installation and installed self-test

Conclusion: success.

### Cross-distribution run `29859100058`

- Python 3.10: Ruff, compileall, complete 30-test suite,
  normal/optimized self-test, wheel build/content inspection, isolated install,
  command, version, import
- Python 3.13: same acceptance matrix
- Nix gate: flake check
- Arch: unprivileged `makepkg`, package content inspection, installation,
  command, version, self-test, import
- Fedora 44: RPM build, content inspection, installation, command, version,
  self-test, import

Conclusion: success for every job.

PR #1 was squash-merged into `main` as
`41b3cb359bf0cb46587e4f8326509833bf6037f9`.

## Post-merge Main validation through PR #2

Validation head: `a5aa0262703cbe4e9af5e7e230d05ace1a1458bc`, based directly on
merged Main SHA `41b3cb359bf0cb46587e4f8326509833bf6037f9` and changing only
`ai-context/MIGRATION_PLAN.md` and `ai-context/TESTING.md`.

### Nix run `29859471948`

- lock metadata and formatting: success
- `nix flake check`: success
- package build and installed command smoke tests: success
- local `nix run`: success
- exact validation-commit remote build/run: success
- exact validation-commit profile installation and self-test: success

### Cross-distribution run `29859471853`

- Python 3.10 full 30-test/wheel/install matrix: success
- Python 3.13 full 30-test/wheel/install matrix: success
- Nix gate: success
- unprivileged Arch build, content inspection, install, command, version,
  self-test, and import: success
- Fedora 44 RPM build, content inspection, install, command, version, self-test,
  and import: success

PR #2 was squash-merged into `main` as
`2fad92a831ef167b38a77124f10723b31d027a8f`.

The final documentation commit after PR #2 changes only README and these status
records. It does not alter runtime, tests, workflows, packaging, lock files, or
license content.

## Direct Main-tree verification

After the rewrite merge, GitHub was queried directly at `ref=main`:

- `pipes_sh.py` exists and declares `VERSION = "2.0.0"`.
- Its header contains `SPDX-License-Identifier: MIT`, all historical copyright
  notices, the separate 2026 rewrite notice, and the unofficial-rewrite label.
- `LICENSE` retains blob SHA `51bcb06d84329959bf250dfddac82c7c0da772e4`
  and the historical MIT notices.
- PR #1 and PR #2 are merged.
- Backup branch and annotated tag remain tied to historical SHA
  `581792d4e0ea51e15889ba14a85db1bc9727b83d`.

## Failure history and fixes

- Initial Fedora RPM run failed because the spec lacked `%prep`; fixed with
  `%autosetup -n Pipes-%{version}` and verified by later successful Fedora jobs.
- The one-time assembly workflow initially committed generated `__pycache__`
  files; they were removed atomically, `.gitignore` was expanded while retaining
  the historical `pipes.sh.6.html` rule, and final comparisons contained no
  generated cache/build artifacts.
- An early PTY signal test could signal before handlers were installed; it was
  changed to wait for visible terminal initialization before sending signals.
- The benchmark initially had an import-path issue; it now inserts the project
  root before importing `pipes_sh`.
- The first reset implementation exposed a multi-pipe ordering ambiguity; frame
  results now carry exact `clear_after` boundaries, and renderer ordering is
  regression-tested, including multiple resets inside one frame.

## Security and repository checks

- Runtime has no `subprocess`, shell, network, plugin, pickle/marshal, FFI,
  `eval`, `exec`, or persistent-write path.
- `LICENSE` remained unchanged.
- Backup branch and annotated tag resolve to historical SHA
  `581792d4e0ea51e15889ba14a85db1bc9727b83d`.
- Tag `pre-python-master-20260721` was verified as an annotated tag by its
  one-time workflow and commit-identical to historical `master`.
- Branch comparisons contain no generated cache/build artifacts.

## Local tool limitations

Native local Wheel, Nix, Arch, and Fedora tooling was unavailable in the local
execution container. Those results are therefore recorded only from the actual
GitHub Actions jobs above, not presented as local runs.

## Model/fuzz coverage

- Seeds 0..9 in long runs
- 1, 2, 8, and 32 pipes across tests/self-test
- Terminal sizes 1×1, 2×3, 7×5, 80×24, 500×200
- Every edge direction
- Keep mode and randomized crossing assignment
- Reset enabled/disabled, exact glyph boundaries, and multiple resets per frame
- Deterministic initialization and frames
- Valid direction, position, type, and color bounds after each modeled step

## Remaining acceptance boundary

The repository default branch is still `master`. Until an administrator changes
it to `main`, unqualified references such as `github:xnixjoyer/Pipes` resolve to
the historical Bash tree rather than the Python flake.

Current verified remote form:

```text
github:xnixjoyer/Pipes/main
```

After selecting `main` under **Settings → General → Default branch**, execute
and append the results of the unqualified metadata/build/run/profile commands
listed in `MIGRATION_PLAN.md`. Do not mark the default-branch migration complete
before those commands pass.


## Version 3.0.0 command migration

The public executable changes from `pipes.sh` to `pipes` with no compatibility
alias. The feature branch must prove that Wheel, Nix, Arch, and Fedora contain
`/bin/pipes` and `pipes(6)`, reject stale installed `pipes.sh` paths, report
`pipes 3.0.0`, and pass the complete PTY/model suite plus the new command-name
assertion. Run IDs are recorded after CI completes.

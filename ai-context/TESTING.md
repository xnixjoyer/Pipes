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

Results:

- Version output: `pipes.sh 2.0.0`
- Self-test output: `pipes.sh self-test: PASS`
- Unit/model/integration tests: 30 tests, all passed
- Exact reset boundaries: passed for one and multiple clear points inside a
  multi-pipe frame; renderer ordering is regression-tested
- PTY: startup with `TERM=xterm-256color`, deterministic seed, ASCII type,
  no-color mode, normal key exit, `SIGINT`, `SIGTERM`, `SIGHUP`, and 1×1
  resize; passed with conventional signal exit codes, no traceback, and no zero
  cursor coordinates
- OpenPTY restoration test: confirmed Echo is disabled while running and the
  complete original `termios` attribute vector is restored after normal exit
- Python emitted `pty.fork`/`os.fork` deprecation warnings under Python 3.13
  because the host process is multi-threaded; they did not affect the result

## Successful GitHub Actions acceptance

Executable/package head: `155e311fa38791f033984ef622b1ef7902c4c1ec`

### Nix run `29858938719`

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

### Cross-distribution run `29858938850`

- Python 3.10: Ruff, compileall, 30 tests, normal/optimized self-test, wheel
  build/content inspection, isolated install, command, version, import
- Python 3.13: same acceptance matrix
- Nix gate: flake check
- Arch: unprivileged `makepkg`, package content inspection, installation,
  command, version, self-test, import
- Fedora 44: RPM build, content inspection, installation, command, version,
  self-test, import

Conclusion: success for every job.

An earlier Fedora run exposed a missing `%prep`; the spec was corrected with
`%autosetup`, and the successful run above verifies the fix. Generated
`__pycache__` files from the one-time assembly were removed and ignored before
this acceptance run.

## Security and repository checks

- Runtime has no `subprocess`, shell, network, plugin, pickle/marshal, FFI,
  `eval`, `exec`, or persistent-write path.
- `LICENSE` remained unchanged.
- Backup branch and annotated tag resolve to historical SHA
  `581792d4e0ea51e15889ba14a85db1bc9727b83d`.
- Tag `pre-python-master-20260721` was verified as an annotated tag by its
  one-time workflow and commit-identical to historical `master`.
- Branch comparison contains no generated cache/build artifacts.

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

The status-only documentation commit following these runs changes no executable
or packaging input. Its own branch workflows must still be green before merge.

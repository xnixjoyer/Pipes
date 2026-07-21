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

## Executed successfully

```bash
python3 -m py_compile pipes_sh.py
python3 pipes_sh.py --version
python3 pipes_sh.py --help
python3 pipes_sh.py --self-test
python3 -m unittest discover -s tests -v
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

The test suite itself also executed and passed:

```bash
python3 -O pipes_sh.py --self-test
```

through the integration test subprocess.

## GitHub Actions results

Successful on head `6297c16ab96cd6cc8a984f6097cf97270b4a9178` before the
non-functional cache cleanup and termios-test addition:

- Python 3.10 and 3.13: Ruff, compileall, 29 tests, normal/optimized self-test,
  wheel build/content inspection, isolated install, command, version, import
- Nix: formatting, flake check, build, local run, exact-commit remote build/run,
  and profile installation
- Arch: unprivileged `makepkg`, content inspection, installation, command,
  version, self-test, import
- Fedora 44: RPM build, content inspection, installation, command, version,
  self-test, import

The final head must rerun these checks after the 30th termios restoration test.

## Not available in the local environment

- Native local Wheel build tooling
- Native local Nix
- Native local Arch `makepkg`
- Native local Fedora `rpmbuild`

These were exercised in GitHub Actions rather than falsely claimed as local.

## Model/fuzz coverage currently represented

- Seeds 0..9 in long runs
- 1, 2, 8, and 32 pipes across tests/self-test
- Terminal sizes 1×1, 2×3, 7×5, 80×24, 500×200
- Every edge direction
- Keep mode and randomized crossing assignment
- Reset enabled/disabled, exact glyph boundaries, and multiple resets per frame
- Deterministic initialization and frames
- Valid direction, position, type, and color bounds after each modeled step

## Required CI acceptance commands

Python/wheel:

```bash
ruff check .
python -m compileall -q pipes_sh.py tests
python -m unittest discover -s tests -v
python pipes_sh.py --self-test
python -O pipes_sh.py --self-test
python -m build --wheel --no-isolation
```

Nix:

```bash
nix flake metadata --no-write-lock-file .
git diff --exit-code -- flake.lock
nix develop --command nixfmt --check flake.nix nix/package.nix
nix flake check --no-write-lock-file --print-build-logs
nix build .#default --no-write-lock-file
./result/bin/pipes.sh --help
./result/bin/pipes.sh --version
./result/bin/pipes.sh --self-test
nix run .#default --no-write-lock-file -- --self-test
```

Arch and Fedora exact commands are encoded in `.github/workflows/cross-distro.yml`.
Record the final-head run IDs and conclusions here after they complete.

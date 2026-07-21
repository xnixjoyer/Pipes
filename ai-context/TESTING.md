# Testing record

This file distinguishes tests actually executed from tests represented only by
configuration. Update it after every meaningful run.

## Local execution environment

- Date: 2026-07-21
- Python: 3.13.5
- Network from local execution container: unavailable
- Native Nix, `makepkg`, `rpmbuild`, and Python `build`: unavailable locally

Local commands used during the original rewrite and command migration:

```bash
python3 -m py_compile pipes_sh.py
python3 pipes_sh.py --version
python3 pipes_sh.py --help
python3 pipes_sh.py --self-test
python3 -m unittest discover -s tests -v
python3 -O pipes_sh.py --self-test
```

The command-migration workflow additionally asserted:

```bash
test "$(python pipes_sh.py --version)" = "pipes 3.0.0"
test -f pipes.6
test ! -e pipes.sh.6
```

## Model and PTY coverage

The current suite contains 31 tests. Coverage includes:

- CLI defaults, range validation, repeated type/color arguments, and no positionals
- parser program name and help text fixed to `pipes`
- all ten built-in 16-glyph transition sets
- safe custom Unicode glyph validation
- deterministic seeds and long model runs
- every edge direction and keep mode
- 1, 2, 8, and 32 pipes across tests/self-test
- terminal sizes 1×1, 2×3, 7×5, 80×24, and 500×200
- exact reset boundaries, including multiple clears inside one logical frame
- live bold/color style regeneration
- cursor fallback coordinates
- normal PTY key exit
- `SIGINT`, `SIGTERM`, and `SIGHUP` exit codes
- resize to 1×1 without zero coordinates
- Echo disabled while running
- byte-for-byte restoration of the original termios attribute vector
- terminal cleanup idempotence
- import without terminal side effects
- normal and `python -O` self-tests

Python 3.13 may emit `pty.fork`/`os.fork` deprecation warnings when the host
process is multi-threaded. Those warnings do not affect the test result.

## Original rewrite acceptance

### PR #1

Final accepted head: `408b56006710f6ceec785aa1fcfba7d152fcc262`.

- Nix run `29859100015`: successful formatting, flake check, build, local run,
  exact-commit remote build/run, profile installation, help/version/self-test.
- Cross-distribution run `29859100058`: successful Python 3.10/3.13, 30-test
  suite, Wheel, Nix gate, unprivileged Arch, and Fedora 44.

PR #1 was squash-merged as
`41b3cb359bf0cb46587e4f8326509833bf6037f9`.

### PR #2 post-merge validation

Validation head: `a5aa0262703cbe4e9af5e7e230d05ace1a1458bc`.

- Nix run `29859471948`: success, including exact remote commit and profile.
- Cross-distribution run `29859471853`: success for Python 3.10/3.13, Wheel,
  Nix, unprivileged Arch, and Fedora 44.

PR #2 was squash-merged as
`2fad92a831ef167b38a77124f10723b31d027a8f`.

## Version 3.0.0 command migration acceptance

### Executable/package head

Accepted head: `0eee308fa3e4332ccfe0d8af86944cf48196bf94`.

#### Nix run `29861774386`

Conclusion: success.

Verified:

- flake metadata without lock rewriting
- Nix formatting
- `nix flake check`
- package build
- `/bin/pipes` exists and `/bin/pipes.sh` does not
- `pipes(6)` exists in compressed or uncompressed Nix form
- no `pipes.sh(6)` file exists
- `pipes --help`
- exact version output `pipes 3.0.0`
- `pipes --self-test`
- local `nix run`
- exact-commit remote build and run
- exact-commit profile installation
- profile contains `pipes` and not `pipes.sh`

An earlier Nix run `29861613885` built the package and passed all 31 tests but
the workflow checked only the uncompressed manpage path. Nix compressed the file
to `pipes.6.gz`; the package and workflow were corrected to accept either valid
Nix form while still rejecting both old `pipes.sh.6` forms.

#### Cross-distribution run `29861774406`

Conclusion: success for every job.

Python 3.10 and Python 3.13 each verified:

- Ruff
- compileall
- complete 31-test suite
- normal and optimized self-test
- direct version output `pipes 3.0.0`
- Wheel build and content inspection
- Wheel contains `pipes.6` and not `pipes.sh.6`
- isolated virtual-environment install
- virtual environment contains executable `pipes`
- virtual environment does not contain executable `pipes.sh`
- installed help, version, self-test, and module import

Arch Linux verified:

- unprivileged `makepkg` build
- package content inspection
- `/usr/bin/pipes` and `pipes(6)` present
- old binary and manpage absent
- package installation
- installed help, exact version, self-test, and import

Fedora 44 verified:

- RPM build
- RPM content inspection
- `/usr/bin/pipes` and `pipes(6)` present
- old binary and manpage absent
- RPM installation
- installed help, exact version, self-test, and import

The same run also completed the Nix gate successfully.

### Final PR head

Final PR head: `c711353271acc55d4013a714858924865a503233`.

- Nix run `29862006643`: success for formatting, build, local run,
  exact-commit remote build/run, profile installation, command/manpage presence,
  and old-interface absence.
- Cross-distribution run `29862006732`: success for Python 3.10, Python 3.13,
  Ruff, all 31 tests, Wheel, Nix gate, unprivileged Arch, and Fedora 44.

PR #3 was marked ready and squash-merged into `main` as
`2559806a186bff29688d1c65e29df8800e26ee74`.

Direct post-merge GitHub reads at `ref=main` confirmed:

- `pyproject.toml` exposes only `pipes = "pipes_sh:main"`;
- package data names `pipes.6`;
- README displays `assets/pipes-logo.svg` centered and documents `$ pipes`;
- README explicitly states no `pipes.sh` executable alias is installed;
- `pipes(6)` exists and declares version 3.0.0;
- `pipes.sh.6` returns Not Found;
- repository metadata reports `main` as the default branch.

## Migration-workflow failure history

The one-time migration workflow intentionally used strict checks and exposed
three workflow-only issues before the accepted tree was produced:

1. Initial replacement counts underestimated repeated Nix and Wheel path checks.
   The actual source was inspected and the counts were corrected.
2. A stale-name grep matched replacement-source strings inside the migration
   workflow itself. The check was limited to product and durable CI files.
3. GitHub Actions could not push commits that modified workflow YAML files.
   Runtime/package/test changes were committed by the action; durable workflows
   and removal of the one-time workflow were applied through the GitHub connector.

No product test was weakened. The successful one-time migration run validated
the transformed runtime and tests before committing them.

## Earlier rewrite failure history

- Initial Fedora RPM build lacked `%prep`; fixed with `%autosetup`.
- The first assembly workflow committed generated `__pycache__`; caches were
  removed and ignored.
- An early PTY test could signal before handlers were installed; it now waits for
  visible terminal initialization.
- The benchmark initially lacked the repository root in `sys.path`; corrected.
- Exact multi-pipe reset ordering was clarified with `clear_after` boundaries and
  renderer regression tests.

## Security and repository checks

- Runtime has no subprocess, shell, network, plugin, pickle/marshal, FFI,
  `eval`, `exec`, or persistent-write path.
- `LICENSE` remains unchanged.
- Historical backup branch and annotated tag resolve to
  `581792d4e0ea51e15889ba14a85db1bc9727b83d`.
- GitHub repository metadata reports `main` as the default branch.
- Branch comparison contains no generated cache/build artifacts.
- Version 3 packaging intentionally installs only `pipes`; historical `pipes.sh`
  references remain only where they identify or credit the original project.

## Remaining optional verification

Run the unqualified remote Nix smoke commands listed in `MIGRATION_PLAN.md` and
record their result. All required PR acceptance and direct Main-tree checks have
already passed.

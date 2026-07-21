# Repository cleanup

This record belongs to the canonical `ai-context/` hand-off folder and documents
the completed post-rewrite cleanup.

## Result

PR #4 was squash-merged to `main` as:

```text
adb1f1c80dabc8fa7531630e3b9a2d841118c2ce
```

The accepted PR head was:

```text
c9e64546b94a2a97e30374ec42310a13e67d65df
```

The cleanup removed about 1,800 obsolete lines without changing the Python
runtime, package outputs, command name, or license.

## Kept

- byte-identical historical `LICENSE`
- current `README.md` and `assets/pipes-logo.svg`
- `pipes_sh.py`, `pipes.6`, `pyproject.toml`, `Makefile`, and `.gitignore`
- current GitHub Actions workflows
- Nix, Arch, Fedora, and Python packaging
- current Python tests and `scripts/benchmark.py`
- the complete `ai-context/` directory

## Removed from the maintained tree

- `pipes.sh`
- `.travis.yml`
- `CONTRIBUTING.rst`
- the Bash-only `test/` directory
- `scripts/README`
- `scripts/benchmark.sh`
- `scripts/gen-man-html.sh`
- `scripts/travis-script.sh`
- `i/pipes.png`
- `.github/ISSUE_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/BUG.md`

The historical implementation remains recoverable through Git history, the
historical branch, backup branch, and annotated rollback tag. It is not present
in the maintained `main` working tree.

## Durable prevention

The `repository-hygiene` job in `.github/workflows/cross-distro.yml` now checks:

- the historical `LICENSE` blob SHA remains
  `51bcb06d84329959bf250dfddac82c7c0da772e4`;
- every required current runtime, packaging, test, logo, and AI-context path is
  present;
- every removed Bash-, Travis-, screenshot-, and stale-template path is absent.

A future pull request that restores those paths fails CI.

## Acceptance evidence

Nix run `29863341887` succeeded for:

- formatting and lock checks
- flake check and package build
- local app run
- exact-commit remote build and run
- fresh profile installation
- `~/.nix-profile/bin/pipes --self-test`

Cross-distribution run `29863341399` succeeded for:

- repository hygiene
- Python 3.10 and Python 3.13
- Ruff and all 31 tests
- Wheel build, inspection, and isolated installation
- Nix gate
- unprivileged Arch package build and installation
- Fedora RPM build and installation

## Nix/Fish incident recorded during cleanup

A user reported that `nix profile list` showed Pipes while Fish returned
`Unknown command: pipes`. Exact-commit CI proved that the profile contains and
runs `~/.nix-profile/bin/pipes`; the failure class is therefore a missing user
profile directory in Fish's `PATH`, not a missing package executable.

The permanent diagnosis and commands are in
[`NIX_TROUBLESHOOTING.md`](NIX_TROUBLESHOOTING.md) and the README installation
section.

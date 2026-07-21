# Repository cleanup

This record belongs to the canonical `ai-context/` hand-off folder and documents the post-rewrite cleanup.

## Keep

- `LICENSE` and required historical notices
- current README and `assets/pipes-logo.svg`
- `pipes_sh.py`, `pipes.6`, `pyproject.toml`, `Makefile`, `.gitignore`
- current GitHub Actions workflows, Nix, Arch, Fedora, and Python packaging
- current Python tests and `scripts/benchmark.py`
- the complete `ai-context/` folder

## Remove

- historical Bash runtime and Bash-only tests
- obsolete Travis configuration and helper
- obsolete Bash benchmark and manpage-generation helpers
- obsolete historical script documentation and contribution guide
- historical screenshot assets no longer referenced by the current README
- stale issue templates written for the former Bash implementation

The cleanup is merged only after the complete Python, PTY, Wheel, Nix, Arch, and Fedora matrix passes.

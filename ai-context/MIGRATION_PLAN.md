# Migration plan and status

Status legend: `[x]` completed and verified, `[~]` implemented but awaiting a
required external verification, `[ ]` not completed.

## Forensics and safety

- [x] Identify historical default branch `master`.
- [x] Record historical SHA `581792d4e0ea51e15889ba14a85db1bc9727b83d`.
- [x] Verify historical MIT notices in runtime and `LICENSE`.
- [x] Create `backup/master-before-python-rewrite-20260721` at historical SHA.
- [x] Create `main` at historical SHA before implementation.
- [x] Create `rewrite/python-single-file` at historical SHA.
- [x] Create annotated tag `pre-python-master-20260721` and verify that it is
  commit-identical to historical `master`.
- [x] Change the GitHub repository default branch to `main` and verify repository
  metadata reports `main`.

## Python rewrite

- [x] Single-file Python runtime.
- [x] Pure CLI/model functions and deterministic engine.
- [x] Terminfo capabilities, direct buffered renderer, terminal session cleanup.
- [x] Immediate bold/color toggles and documented legacy corrections.
- [x] Unit/model/self/PTY tests, including exact termios restoration.
- [x] Python Wheel, Nix, Arch, and Fedora packaging.
- [x] Merge rewrite PR #1 to `main` as
  `41b3cb359bf0cb46587e4f8326509833bf6037f9`.
- [x] Revalidate the merged Main tree through PR #2 and merge the hand-off as
  `2fad92a831ef167b38a77124f10723b31d027a8f`.

## Public command migration — version 3.0.0

The public interface intentionally changed from `pipes.sh` to `pipes`. The
original project name remains in historical credits, but no installed alias,
wrapper, symlink, package file, or manpage uses the old executable name.

- [x] Set `pipes` as the only console-script entry point.
- [x] Change help, errors, version output, and self-test output to `pipes`.
- [x] Bump the rewrite version to 3.0.0 because this is a breaking CLI change.
- [x] Rename the manual page from `pipes.sh(6)` to `pipes(6)`.
- [x] Update Wheel, Nix, Arch, Fedora, Makefile, flake app, and package metadata.
- [x] Update durable CI and add negative checks for `/bin/pipes.sh` and
  `pipes.sh.6`.
- [x] Add a centered custom SVG logo and redesign the README.
- [x] Add a parser/help regression test for the public command name.
- [x] Validate executable/package head
  `0eee308fa3e4332ccfe0d8af86944cf48196bf94`.
- [x] Nix run `29861774386`: success, including local build/run, exact-commit
  remote build/run, profile installation, `pipes` presence, and `pipes.sh`
  absence.
- [x] Cross-distribution run `29861774406`: success for Python 3.10, Python 3.13,
  31 tests, Wheel, Nix gate, unprivileged Arch, and Fedora 44.
- [x] Validate final PR head `c711353271acc55d4013a714858924865a503233`.
- [x] Final Nix run `29862006643`: success, including exact-commit remote checks.
- [x] Final cross-distribution run `29862006732`: success for every job.
- [x] Mark PR #3 ready and squash-merge it to `main` as
  `2559806a186bff29688d1c65e29df8800e26ee74`.
- [x] Verify directly on `main` that the Wheel entry point is `pipes`, README uses
  the centered custom logo, `pipes(6)` exists, and `pipes.sh.6` is absent.
- [~] Run and record the unqualified default-branch Nix smoke test after the merge.

## Current acceptance boundary

The command migration, README redesign, logo, runtime, packaging, durable CI,
and documentation are merged into `main`. All PR acceptance checks passed.
Only the optional post-merge confirmation of the unqualified remote Nix reference
remains to be recorded.

Post-merge smoke commands:

```bash
nix flake metadata github:xnixjoyer/Pipes
nix build github:xnixjoyer/Pipes#default
nix run github:xnixjoyer/Pipes#default -- --self-test
nix profile add github:xnixjoyer/Pipes#default
"$HOME/.nix-profile/bin/pipes" --version
"$HOME/.nix-profile/bin/pipes" --self-test
```

Expected version output:

```text
pipes 3.0.0
```

The profile must not contain `$HOME/.nix-profile/bin/pipes.sh`.

## Branch retention

Keep permanently unless the owner explicitly decides otherwise:

- `main`
- historical `master`
- `backup/master-before-python-rewrite-20260721`
- annotated tag `pre-python-master-20260721`

The feature branch `feature/pipes-command-logo-readme` is deletable after the
post-merge remote smoke check; it is not deleted automatically.

## Failure handling

When CI fails, add the exact job/run, failing command, relevant log excerpt, root
cause, and correction to `TESTING.md`. Do not weaken a check merely to obtain a
green result. Packaging failures must be fixed in their native packaging files,
not hidden by installing into uncontrolled environments.

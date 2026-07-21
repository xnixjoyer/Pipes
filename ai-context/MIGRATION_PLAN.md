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

## Rewrite

- [x] Single-file Python runtime.
- [x] Pure CLI/model functions and deterministic engine.
- [x] Terminfo capabilities, direct buffered renderer, terminal session cleanup.
- [x] Immediate bold/color toggles and documented legacy corrections.
- [x] Unit/model/self/PTY test sources, including exact termios restoration.
- [x] README, manpage, and canonical AI context.

## Packaging

- [x] `pyproject.toml` and console entry point.
- [x] Wheel build/install/content inspection on Python 3.10 and 3.13.
- [x] Nix flake, lock, derivation, checks, build, run, exact-commit remote tests,
  and profile installation.
- [x] Arch unprivileged build, content inspection, installation, and self-test.
- [x] Fedora RPM build, content inspection, installation, and self-test.
- [x] GitHub Actions definitions.

## GitHub integration

- [x] Push all verified files to `rewrite/python-single-file`.
- [x] Open PR #1 to `main` with test and rollback report.
- [x] Successful final-head Python, PTY, Wheel, Nix, Arch, and Fedora CI:
  Nix run `29859100015`; cross-distribution run `29859100058`.
- [x] Mark PR #1 ready and squash-merge it.
- [x] Confirm merged `main` SHA
  `41b3cb359bf0cb46587e4f8326509833bf6037f9`.
- [~] Validate the merged Main tree again through PR #2 from
  `validation/main-post-merge`; this PR changes only maintainer status records.
- [ ] Change the repository default branch from `master` to `main` in GitHub
  Settings. The connected GitHub tool exposes no repository-default-branch
  mutation, so this remains a manual administration step.
- [ ] After that switch, verify unqualified `github:xnixjoyer/Pipes` resolves to
  `main` and run the default-branch Nix build/run/profile smoke tests.
- [ ] Mark `rewrite/python-single-file` and `validation/main-post-merge`
  deletable after default-branch verification; do not delete them automatically.

## Current branch retention

Keep:

- `main`
- `master` until explicit owner approval for deletion
- `backup/master-before-python-rewrite-20260721`
- annotated tag `pre-python-master-20260721`

Temporary branches may be deleted only after the GitHub default branch is
confirmed as `main`, main validation is green, and unqualified remote installs
resolve to the Python rewrite.

## Failure handling

When CI fails, add the exact job/run, failing command, relevant log excerpt, root
cause, and correction to `TESTING.md`. Do not weaken a check merely to obtain a
green result. Packaging failures must be fixed in their native packaging files,
not hidden by installing into uncontrolled environments.

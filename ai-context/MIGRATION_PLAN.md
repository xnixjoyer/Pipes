# Migration plan and status

Status legend: `[x]` completed and verified, `[~]` implemented but awaiting a
required external verification, `[ ]` not completed.

## Forensics and safety

- [x] Identify historical default branch `master`.
- [x] Record historical SHA `581792d4e0ea51e15889ba14a85db1bc9727b83d`.
- [x] Verify historical MIT notices in runtime and `LICENSE`.
- [x] Create `backup/master-before-python-rewrite-20260721` at historical SHA.
- [x] Create `main` at historical SHA.
- [x] Create `rewrite/python-single-file` at historical SHA.
- [~] Create annotated tag `pre-python-master-20260721` and verify target.
  A one-time contents-write workflow is staged because the connector has no
  direct annotated-tag mutation.

## Rewrite

- [x] Single-file Python runtime.
- [x] Pure CLI/model functions and deterministic engine.
- [x] Terminfo capabilities, direct buffered renderer, terminal session cleanup.
- [x] Immediate bold/color toggles and documented legacy corrections.
- [x] Unit/model/self/PTY test sources.
- [x] README, manpage, and canonical AI context.

## Packaging

- [x] `pyproject.toml` and console entry point.
- [x] Nix flake, lock, derivation, package/app/check/dev-shell exports.
- [x] Arch `PKGBUILD` and `.SRCINFO`.
- [x] Fedora spec.
- [x] GitHub Actions definitions.
- [~] Wheel build/install/content inspection — awaiting final-head CI.
- [~] Nix check/build/run/profile/remote checks — awaiting final-head CI.
- [~] Arch unprivileged build/install/content checks — awaiting final-head CI.
- [~] Fedora RPM build/install/content checks — awaiting final-head CI.

## GitHub integration

- [x] Push all locally verified files to `rewrite/python-single-file`.
- [x] Open draft PR #1 to `main` with test and rollback report.
- [ ] Require successful CI for Python, PTY, Nix, Arch, and Fedora.
- [ ] Merge only after all required checks pass.
- [ ] Confirm merged `main` SHA.
- [ ] Change repository default branch to `main` in GitHub settings.
- [ ] Verify remote default flake and exact-main flake installs.
- [ ] Mark temporary branch deletable; do not delete automatically.

## Failure handling

When CI fails, add the exact job/run, failing command, relevant log excerpt, root
cause, and correction to `TESTING.md`. Do not weaken a check merely to obtain a
green result. Packaging failures must be fixed in their native packaging files,
not hidden by installing into uncontrolled environments.

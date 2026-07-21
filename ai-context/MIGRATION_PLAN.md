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
- [x] Unit/model/self/PTY tests, including exact termios restoration.
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
- [x] Open, validate, and squash-merge PR #1 to `main`.
- [x] Confirm rewrite merge SHA
  `41b3cb359bf0cb46587e4f8326509833bf6037f9`.
- [x] Validate the merged Main tree again through PR #2 from
  `validation/main-post-merge`.
- [x] Post-merge validation Nix run `29859471948`: success, including exact
  remote commit build/run and profile installation.
- [x] Post-merge cross-distribution run `29859471853`: success for Python 3.10,
  Python 3.13, 30 tests, wheel, Nix gate, unprivileged Arch, and Fedora 44.
- [x] Squash-merge PR #2 as
  `2fad92a831ef167b38a77124f10723b31d027a8f`.
- [x] Update README and canonical status records so remote examples explicitly
  target `/main` during the default-branch transition.
- [ ] Change the repository default branch from `master` to `main` in GitHub
  Settings. The connected GitHub tool exposes no repository-default-branch
  mutation, so this remains a manual administration step.
- [ ] After that switch, verify unqualified `github:xnixjoyer/Pipes` resolves to
  `main` and run the default-branch Nix build/run/profile smoke tests.
- [ ] Mark `rewrite/python-single-file` and `validation/main-post-merge`
  deletable after default-branch verification; do not delete them automatically.

## Current acceptance boundary

The implementation, tests, packaging, license preservation, explicit-`main`
remote references, and maintainer context are complete on `main`. The project is
not yet allowed to claim that its GitHub migration is fully complete because the
repository setting still names `master` as the default branch.

Until that setting changes:

- use `github:xnixjoyer/Pipes/main` for Nix remote references;
- do not use unqualified `github:xnixjoyer/Pipes` as proof of the Python rewrite;
- do not delete `master`, the backup branch, or the annotated rollback tag.

After an administrator selects `main` under **Settings → General → Default
branch**, run and record:

```bash
nix flake metadata github:xnixjoyer/Pipes
nix build github:xnixjoyer/Pipes#default
nix run github:xnixjoyer/Pipes#default -- --self-test
nix profile add github:xnixjoyer/Pipes#default
"$HOME/.nix-profile/bin/pipes.sh" --self-test
```

## Branch retention

Keep:

- `main`
- `master` until explicit owner approval for deletion
- `backup/master-before-python-rewrite-20260721`
- annotated tag `pre-python-master-20260721`

Temporary branches may be deleted only after the GitHub default branch is
confirmed as `main`, Main validation remains green, and unqualified remote
installs resolve to the Python rewrite.

## Failure handling

When CI fails, add the exact job/run, failing command, relevant log excerpt, root
cause, and correction to `TESTING.md`. Do not weaken a check merely to obtain a
green result. Packaging failures must be fixed in their native packaging files,
not hidden by installing into uncontrolled environments.


## Public command migration — version 3.0.0

- [x] Select `pipes` as the only installed executable name.
- [x] Remove the `pipes.sh` console-script entry point and package file ownership.
- [x] Rename the manual page to `pipes(6)`.
- [x] Update Nix, Wheel, Arch, Fedora, help, errors, version output, and docs.
- [x] Add centered custom SVG branding to the README.
- [~] Update permanent CI workflows through the GitHub connector.
- [~] Validate the complete 3.0.0 matrix in the feature pull request.
- [ ] Merge only after Python 3.10/3.13, Wheel, Nix, Arch, Fedora, and PTY checks pass.

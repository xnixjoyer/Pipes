# Nix profile troubleshooting

This file records the difference between a package-output failure and a user-shell
`PATH` failure. Keep it with the canonical AI maintainer context.

## Supported install paths

The flake exports `packages.<system>.default` and its package installs exactly:

- `bin/pipes`
- `share/man/man6/pipes.6` (normally compressed by Nix to `pipes.6.gz`)

It must not install `bin/pipes.sh` or `pipes.sh.6`.

## Fresh profile acceptance

The Nix workflow creates a temporary home, installs the exact Git commit into a
fresh profile, then runs:

```bash
"$HOME/.nix-profile/bin/pipes" --version
"$HOME/.nix-profile/bin/pipes" --self-test
```

This proves package output and profile linking independently from the runner's
interactive shell configuration.

## Fish says `Unknown command: pipes`

If `nix profile list` shows Pipes but Fish cannot resolve `pipes`, check the
profile executable directly:

```fish
~/.nix-profile/bin/pipes --self-test
```

If that succeeds, add the profile binary directory to Fish permanently:

```fish
fish_add_path ~/.nix-profile/bin
```

When Nix uses its XDG profile link, use:

```fish
fish_add_path ~/.local/state/nix/profile/bin
```

Diagnostics:

```fish
command -v pipes
string split : $PATH | string match '*nix*profile*bin*'
ls -l ~/.nix-profile/bin/pipes ~/.local/state/nix/profile/bin/pipes 2>/dev/null
```

## Removing a profile element

`nix profile remove` matches the profile element name or index, not necessarily
the original flake URL. Use the name or index printed by `nix profile list`:

```bash
nix profile remove Pipes
```

## Failure classification

- Direct profile path missing: package/profile defect; reproduce in Nix CI.
- Direct profile path works but `command -v pipes` fails: shell `PATH` defect.
- Direct path runs but self-test fails: runtime or wrapper defect.
- Old `pipes.sh` exists: packaging regression; fail CI.

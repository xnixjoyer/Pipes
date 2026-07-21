# pipes.sh — Python rewrite

An animated terminal pipes screensaver implemented as a single Python module.
This repository keeps the public command `pipes.sh` for compatibility while the
runtime is now `pipes_sh.py` and requires Python 3.10 or newer.

> This is an unofficial, independently maintained rewrite. It is not an
> official Pipeseroni release.
>
> **Repository transition:** the Python rewrite is merged into `main`, but the
> GitHub repository still has `master` configured as its default branch. Until
> an administrator changes that setting, use explicit `/main` remote references
> shown below. Unqualified `github:xnixjoyer/Pipes` references still resolve to
> the historical Bash tree.

![Historical pipes.sh screenshot](i/pipes.png)

_The image above is a historical screenshot from the Bash implementation. It
is retained as project history and is not represented as a new Python capture._

## Original project and maintainers

This repository contains an unofficial Python rewrite of
[pipes.sh](https://github.com/pipeseroni/pipes.sh).

The original program was created by [Matthew Simpson](https://gist.github.com/msimpson/1096939), later developed by
[Yu-Jie Lin](https://github.com/livibetter), and maintained by the
[Pipeseroni/pipes.sh contributors](https://github.com/pipeseroni/pipes.sh/graphs/contributors).

This Python rewrite is independently maintained by
[xnixjoyer](https://github.com/xnixjoyer) and is not presented as an official
release of the Pipeseroni project.

The historical MIT license and all historical copyright notices are preserved
in [`LICENSE`](LICENSE). The implementation was derived only from this
repository's MIT-licensed Bash source, documentation, tests, and an independent
Python implementation. Other Python ports are not implementation references.

## Features

- Ten built-in pipe types and repeatable custom 16-codepoint types.
- Multiple independent pipes, deterministic seeds, wrapping, resizing, and
  character-count resets.
- 8-, 16-, 256-, and packed direct-color indices when supported by terminfo.
- Direct ANSI/terminfo rendering without spawning `tput`, `stty`, a shell, or
  any other runtime process.
- Idempotent terminal restoration for normal exit, signals, exceptions, and
  broken pipes.
- Non-interactive self-test that also works under `python -O`.

## Commands

The installed command is:

```text
pipes.sh
```

The Python distribution, Nix attribute, Arch package, and Fedora package are
all named `pipes-sh-python`. The importable module is `pipes_sh`.

The original package and this rewrite cannot both own `/usr/bin/pipes.sh` at
the same time. Arch and Fedora metadata therefore declare a conflict with the
original command-providing package; automatic replacement is intentionally not
enabled.

## Usage

```text
pipes.sh [OPTION]...

-p [1-]               number of pipes
-t [0-9]              built-in pipe type; repeatable
-t c[16 chars]        custom pipe type; repeatable
-c [color index]      decimal color index; repeatable
-c #[hex]             hexadecimal color index; repeatable
-f [20-100]           frame rate
-s [5-15]             straight probability denominator
-r [0-]               clear after N drawn characters; 0 disables
-R                    random starting positions and directions
-B                    disable bold
-C                    disable color
-K                    keep color and type across edges
-h, --help            help
-v, --version         version
--self-test           non-interactive integrity checks
--seed INTEGER        deterministic random seed
```

Examples:

```bash
pipes.sh
pipes.sh -p 8 -t 0 -t 8 -r 0
pipes.sh -c 33 -c 39 -c 45 -p 3
pipes.sh -t cMAYFORCEBWITHYOU --seed 42
```

## Pipe types

| Type | Description | 16 transition characters |
|---:|---|---|
| 0 | Heavy box drawing | `┃┏ ┓┛━┓  ┗┃┛┗ ┏━` |
| 1 | Light arc | `│╭ ╮╯─╮  ╰│╯╰ ╭─` |
| 2 | Light square | `│┌ ┐┘─┐  └│┘└ ┌─` |
| 3 | Double box drawing | `║╔ ╗╝═╗  ╚║╝╚ ╔═` |
| 4 | ASCII plus | `\|+ ++-+  +\|++ +-` |
| 5 | ASCII slash | `\|/ \\/-\\  \\|/\\ /-` |
| 6 | Dots | `.. ....  .... ..` |
| 7 | Dot/O | `.o oo.o  o.oo o.` |
| 8 | Railway | `-\\ /\\\|/  /-\\/ \\|` |
| 9 | Knobby | `╿┍ ┑┚╼┒  ┕╽┙┖ ┎╾` |

The transition index is `old_direction * 4 + new_direction`, where directions
are up, right, down, and left. The engine never generates a 180-degree turn.

## Custom pipe types

`-t c...` requires exactly 16 Unicode codepoints. Control characters,
newlines, combining-only glyphs, and characters that are clearly double-width
are rejected because they break the cell grid. Actual rendered width still
depends on the terminal and font.

```bash
pipes.sh -t cMAYFORCEBWITHYOU
```

## Colors

Color indices are passed through the terminal's `setaf` terminfo capability.
Decimal and hexadecimal forms are equivalent:

```bash
pipes.sh -c 255
pipes.sh -c '#ff'
```

When terminfo reports no color support, animation continues without color. A
requested index outside a positive terminal color limit is rejected before the
terminal mode is changed.

## Keyboard controls

| Key | Action |
|---|---|
| `P` / `O` | Increase/decrease the straight-probability denominator |
| `F` / `D` | Increase/decrease FPS |
| `B` | Toggle bold immediately |
| `C` | Toggle color immediately |
| `K` | Toggle keeping type/color on edge crossings |

Any other key exits. The CLI accepts `-s 5..15`; interactively `O` can lower the
value to 3 for compatibility with the historical implementation.

## Direct Python execution

```bash
python3 ./pipes_sh.py
python3 ./pipes_sh.py --self-test
python3 -O ./pipes_sh.py --self-test
```

## Nix and NixOS

Current commands while GitHub still defaults to `master`:

```bash
nix run github:xnixjoyer/Pipes/main
nix run github:xnixjoyer/Pipes/main -- --help
nix profile add github:xnixjoyer/Pipes/main
```

After the repository default branch is changed to `main`, these equivalent
unqualified commands become valid:

```bash
nix run github:xnixjoyer/Pipes
nix run github:xnixjoyer/Pipes -- --help
nix profile add github:xnixjoyer/Pipes
```

The flake exports `packages.<system>.default`,
`packages.<system>."pipes-sh-python"`, `apps.<system>.default`, and
`apps.<system>."pipes-sh"` for `x86_64-linux` and `aarch64-linux`.

## NixOS Flake integration

Use the explicit branch during the transition:

```nix
{
  inputs.pipes.url = "github:xnixjoyer/Pipes/main";

  outputs = { self, nixpkgs, pipes, ... }: {
    nixosConfigurations.example = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ({ pkgs, ... }: {
          environment.systemPackages = [
            pipes.packages.${pkgs.system}.default
          ];
        })
      ];
    };
  };
}
```

After the default-branch switch, `github:xnixjoyer/Pipes` may replace the
explicit `/main` reference.

## Development shell

```bash
nix develop
python3 ./pipes_sh.py --help
python3 ./pipes_sh.py --self-test
python3 -m unittest discover -s tests -v
python3 -m build --wheel --no-isolation
nix flake check
nix build
```

## Python wheel

```bash
python3 -m build --wheel --no-isolation
python3 -m installer --destdir=/tmp/pipes-root dist/*.whl
```

The wheel installs `pipes.sh`, `pipes_sh.py`, and `share/man/man6/pipes.sh.6`.
There are no third-party runtime dependencies.

## Arch Linux

```bash
cd packaging/arch
makepkg --syncdeps --cleanbuild
sudo pacman -U ./pipes-sh-python-*.pkg.tar.zst
```

The package declares `provides=('pipes.sh')` and `conflicts=('pipes.sh')` but
not `replaces`, so replacement of an existing original package is never silent.

## Fedora

The RPM spec is at `packaging/fedora/pipes-sh-python.spec`. Fedora 44 CI built,
inspected, installed, imported, and self-tested the RPM successfully. Exact run
IDs and commands are recorded in `ai-context/TESTING.md`. The package provides
`pipes.sh` and conflicts with `pipes-sh`.

## Filesystem behavior

The runtime writes no persistent files. It reads terminfo, reads keyboard input,
updates terminal attributes, and writes animation output. It does not write to
the checkout, home directory, XDG directories, `/usr`, or `/nix/store`.

## Versioning

The Python rewrite starts at **2.0.0** because the language, runtime,
packaging, terminal implementation, and several deliberately corrected legacy
behaviors changed. `pipes_sh.VERSION` is canonical and packaging tests check all
other version declarations against it.

## Branch migration and rollback

The historical source is commit
`581792d4e0ea51e15889ba14a85db1bc9727b83d` on `master`. The protected rollback
branch is `backup/master-before-python-rewrite-20260721`, and the annotated
rollback tag is `pre-python-master-20260721`.

PR #1 merged the rewrite into `main` as
`41b3cb359bf0cb46587e4f8326509833bf6037f9`. PR #2 then revalidated the merged
Main tree and added the post-merge hand-off as
`2fad92a831ef167b38a77124f10723b31d027a8f`.

Rollback is non-destructive:

```bash
git switch -c restore-historical backup/master-before-python-rewrite-20260721
```

The remaining administration step is **Settings → General → Default branch →
`main`**. Do not delete `master`, the backup branch, or the tag. The temporary
rewrite and validation branches may be deleted only after the default switch
and unqualified remote Nix checks are confirmed.

## Testing

```bash
make test
python3 -m unittest discover -s tests -v
python3 pipes_sh.py --self-test
python3 -O pipes_sh.py --self-test
python3 scripts/benchmark.py
```

The complete 30-test CI suite covers pure model logic, CLI validation, all edge
directions, deterministic randomness, multiple pipes, exact reset ordering,
resize safety, style regeneration, signal exit status, normal and signal PTY
exits, Echo disabling, and complete termios restoration. Wheel, exact-commit
Nix build/run/profile installation, unprivileged Arch packaging, and Fedora RPM
packaging also passed. Exact commands, run IDs, and corrected failures are in
[`ai-context/TESTING.md`](ai-context/TESTING.md).

## Supported environments

- Python 3.10 or newer
- POSIX terminals with `termios`
- Linux is the packaged and CI-supported target
- A usable `TERM` and terminfo database for interactive mode

`--help`, `--version`, and `--self-test` do not require a TTY.

## Architecture and maintenance context

The runtime remains one physical file, `pipes_sh.py`, divided into pure parsing
and model functions, `Engine`, `TerminalCapabilities`, `TerminalSession`,
`Renderer`, and `App`. Maintainers and coding agents must begin with
[`ai-context/README.md`](ai-context/README.md), which links the forensic record,
architecture, migration status, tests, and decisions.

## History

Matthew Simpson created the original in 2010. Yu-Jie Lin later developed it,
and the Pipeseroni collective maintained the Bash project after the MIT license
was added in 2015. This repository preserves that history while introducing an
independent Python runtime in version 2.0.0.

## License

MIT. See [`LICENSE`](LICENSE). The historical notices remain authoritative and
must not be removed from copies or substantial portions.

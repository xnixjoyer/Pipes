#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
#
# Based on pipes.sh:
# Copyright (c) 2015-2018 Pipeseroni/pipes.sh contributors
# Copyright (c) 2013-2015 Yu-Jie Lin
# Copyright (c) 2010 Matthew Simpson
#
# Python rewrite:
# Copyright (c) 2026 xnixjoyer

"""Unofficial, independently maintained Python rewrite of pipes.sh."""

from __future__ import annotations

import argparse
import curses
from dataclasses import dataclass, field
from enum import IntEnum
import locale
import os
import random
import select
import signal
import sys
import termios
import time
import tty
import unicodedata
from collections.abc import Sequence
from typing import Callable

VERSION = "3.0.0"
MIN_PIPES = 1
MIN_FPS = 20
MAX_FPS = 100
MIN_STRAIGHT = 5
MAX_STRAIGHT = 15
INTERACTIVE_MIN_STRAIGHT = 3
DEFAULT_FPS = 75
DEFAULT_STRAIGHT = 13
DEFAULT_RESET = 2000
DEFAULT_COLORS = (1, 2, 3, 4, 5, 6, 7, 0)
MIN_TERMINAL_WIDTH = 1
MIN_TERMINAL_HEIGHT = 1
SELF_TEST_PASS = "pipes self-test: PASS"

PIPE_SETS: tuple[str, ...] = (
    "┃┏ ┓┛━┓  ┗┃┛┗ ┏━",
    "│╭ ╮╯─╮  ╰│╯╰ ╭─",
    "│┌ ┐┘─┐  └│┘└ ┌─",
    "║╔ ╗╝═╗  ╚║╝╚ ╔═",
    "|+ ++-+  +|++ +-",
    "|/ \\/-\\  \\|/\\ /-",
    ".. ....  .... ..",
    ".o oo.o  o.oo o.",
    "-\\ /\\|/  /-\\/ \\|",
    "╿┍ ┑┚╼┒  ┕╽┙┖ ┎╾",
)

DIRECTION_VECTORS: tuple[tuple[int, int], ...] = (
    (0, -1),
    (1, 0),
    (0, 1),
    (-1, 0),
)


class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


@dataclass(slots=True)
class Options:
    pipes: int = 1
    types: list[str] = field(default_factory=lambda: [PIPE_SETS[0]])
    colors: list[int] = field(default_factory=lambda: list(DEFAULT_COLORS))
    fps: int = DEFAULT_FPS
    straight: int = DEFAULT_STRAIGHT
    reset_limit: int = DEFAULT_RESET
    random_start: bool = False
    bold: bool = True
    color: bool = True
    keep: bool = False
    seed: int | None = None


@dataclass(slots=True)
class PipeState:
    x: int
    y: int
    direction: int
    pipe_type: int
    color: int


@dataclass(slots=True, frozen=True)
class DrawCommand:
    x: int
    y: int
    glyph: str
    color: int


@dataclass(slots=True, frozen=True)
class FrameResult:
    commands: tuple[DrawCommand, ...]
    clear_after: tuple[int, ...] = ()

    @property
    def clear(self) -> bool:
        return bool(self.clear_after)


class CLIError(ValueError):
    """Raised for invalid command-line values before terminal mutation."""


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CLIError(message)


def natural_number(value: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    if not value or not value.isdecimal():
        raise CLIError(f"expected a decimal integer, got {value!r}")
    parsed = int(value, 10)
    if parsed < minimum or (maximum is not None and parsed > maximum):
        if maximum is None:
            raise CLIError(f"value must be at least {minimum}: {value!r}")
        raise CLIError(f"value must be from {minimum} to {maximum}: {value!r}")
    return parsed


def parse_color(value: str) -> int:
    if value.startswith("#"):
        digits = value[1:]
        if not digits or any(ch not in "0123456789abcdefABCDEF" for ch in digits):
            raise CLIError(f"invalid hexadecimal color: {value!r}")
        return int(digits, 16)
    return natural_number(value)


def _cell_width(character: str) -> int:
    if unicodedata.combining(character):
        return 0
    if unicodedata.category(character).startswith("C"):
        return -1
    return 2 if unicodedata.east_asian_width(character) in {"W", "F"} else 1


def validate_custom_type(value: str) -> str:
    if not value.startswith("c"):
        raise CLIError("custom pipe type must start with 'c'")
    glyphs = value[1:]
    if len(glyphs) != 16:
        raise CLIError("custom pipe type must contain exactly 16 Unicode codepoints")
    for glyph in glyphs:
        width = _cell_width(glyph)
        if glyph in "\r\n" or width != 1:
            raise CLIError(
                "custom pipe glyphs must be printable, non-combining, single-cell characters"
            )
    return glyphs


def parse_type(value: str) -> str:
    if value.startswith("c"):
        return validate_custom_type(value)
    index = natural_number(value, minimum=0, maximum=len(PIPE_SETS) - 1)
    return PIPE_SETS[index]


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="pipes",
        description="Animated pipes terminal screensaver (unofficial Python rewrite).",
        add_help=False,
        allow_abbrev=False,
    )
    parser.add_argument("-p", dest="pipes", metavar="[1-]", default=1)
    parser.add_argument("-t", dest="types", action="append", metavar="[0-9]|c[16 chars]")
    parser.add_argument("-c", dest="colors", action="append", metavar="[color index]|#[hex]")
    parser.add_argument("-f", dest="fps", metavar="[20-100]", default=DEFAULT_FPS)
    parser.add_argument("-s", dest="straight", metavar="[5-15]", default=DEFAULT_STRAIGHT)
    parser.add_argument("-r", dest="reset_limit", metavar="[0-]", default=DEFAULT_RESET)
    parser.add_argument("-R", dest="random_start", action="store_true")
    parser.add_argument("-B", dest="bold", action="store_false", default=True)
    parser.add_argument("-C", dest="color", action="store_false", default=True)
    parser.add_argument("-K", dest="keep", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--seed", metavar="INTEGER")
    return parser


def help_text() -> str:
    return """usage: pipes [OPTION]...
Animated pipes terminal screensaver (unofficial Python rewrite).

  -p [1-]               number of pipes (default: 1)
  -t [0-9]              pipe type (default: 0; repeatable)
  -t c[16 chars]        custom pipe type with exactly 16 codepoints
  -c [color index]      color index (repeatable)
  -c #[hex]             hexadecimal color index (repeatable)
  -f [20-100]           frame rate (default: 75)
  -s [5-15]             straight probability denominator (default: 13)
  -r [0-]               clear after N drawn characters; 0 disables (default: 2000)
  -R                    randomize starting position and direction
  -B                    disable bold
  -C                    disable color
  -K                    keep type and color when crossing edges
  -h, --help            show this help and exit
  -v, --version         show version and exit
      --self-test       run non-interactive built-in checks
      --seed INTEGER    deterministic random seed

Keyboard: P/O straight probability, F/D frame rate, B bold, C color,
K keep mode; any other key exits.
"""


def parse_options(argv: Sequence[str]) -> tuple[Options | None, str | None]:
    parser = build_parser()
    namespace = parser.parse_args(list(argv))
    if namespace.help:
        return None, "help"
    if namespace.version:
        return None, "version"
    if namespace.self_test:
        return None, "self-test"
    options = Options(
        pipes=natural_number(str(namespace.pipes), minimum=MIN_PIPES),
        types=[parse_type(value) for value in namespace.types]
        if namespace.types
        else [PIPE_SETS[0]],
        colors=[parse_color(value) for value in namespace.colors]
        if namespace.colors
        else list(DEFAULT_COLORS),
        fps=natural_number(str(namespace.fps), minimum=MIN_FPS, maximum=MAX_FPS),
        straight=natural_number(
            str(namespace.straight), minimum=MIN_STRAIGHT, maximum=MAX_STRAIGHT
        ),
        reset_limit=natural_number(str(namespace.reset_limit)),
        random_start=bool(namespace.random_start),
        bold=bool(namespace.bold),
        color=bool(namespace.color),
        keep=bool(namespace.keep),
        seed=int(namespace.seed, 10) if namespace.seed is not None else None,
    )
    return options, None


def transition_index(old_direction: int, new_direction: int) -> int:
    if old_direction not in range(4) or new_direction not in range(4):
        raise ValueError("directions must be from 0 to 3")
    return old_direction * 4 + new_direction


def choose_direction(current: int, straight: int, rng: random.Random) -> int:
    if rng.randrange(straight) != 0:
        return current
    return (current + rng.choice((-1, 1))) % 4


def wrap_position(x: int, y: int, width: int, height: int) -> tuple[int, int, bool]:
    width = max(MIN_TERMINAL_WIDTH, width)
    height = max(MIN_TERMINAL_HEIGHT, height)
    crossed = x < 0 or x >= width or y < 0 or y >= height
    return x % width, y % height, crossed


class Engine:
    def __init__(self, options: Options, width: int, height: int) -> None:
        self.options = options
        self.rng = random.Random(options.seed)
        self.width = max(MIN_TERMINAL_WIDTH, width)
        self.height = max(MIN_TERMINAL_HEIGHT, height)
        self.drawn = 0
        self.pipes: list[PipeState] = []
        type_offset = 0 if options.keep else self.rng.randrange(len(options.types))
        color_offset = 0 if options.keep else self.rng.randrange(len(options.colors))
        for index in range(options.pipes):
            if options.random_start:
                x = self.rng.randrange(self.width)
                y = self.rng.randrange(self.height)
                direction = self.rng.randrange(4)
            else:
                x = self.width // 2
                y = self.height // 2
                direction = Direction.UP
            self.pipes.append(
                PipeState(
                    x=x,
                    y=y,
                    direction=int(direction),
                    pipe_type=(type_offset + index) % len(options.types),
                    color=(color_offset + index) % len(options.colors),
                )
            )

    def resize(self, width: int, height: int) -> None:
        self.width = max(MIN_TERMINAL_WIDTH, width)
        self.height = max(MIN_TERMINAL_HEIGHT, height)
        for pipe in self.pipes:
            pipe.x %= self.width
            pipe.y %= self.height

    def step(self) -> FrameResult:
        commands: list[DrawCommand] = []
        clear_after: list[int] = []
        for pipe in self.pipes:
            old_direction = pipe.direction
            dx, dy = DIRECTION_VECTORS[old_direction]
            pipe.x += dx
            pipe.y += dy
            pipe.x, pipe.y, crossed = wrap_position(
                pipe.x, pipe.y, self.width, self.height
            )
            if crossed and not self.options.keep:
                pipe.pipe_type = self.rng.randrange(len(self.options.types))
                pipe.color = self.rng.randrange(len(self.options.colors))
            new_direction = choose_direction(
                old_direction, self.options.straight, self.rng
            )
            glyph = self.options.types[pipe.pipe_type][
                transition_index(old_direction, new_direction)
            ]
            commands.append(
                DrawCommand(
                    x=pipe.x,
                    y=pipe.y,
                    glyph=glyph,
                    color=self.options.colors[pipe.color],
                )
            )
            pipe.direction = new_direction
            self.drawn += 1
            if self.options.reset_limit and self.drawn >= self.options.reset_limit:
                clear_after.append(len(commands))
                self.drawn = 0
        return FrameResult(tuple(commands), tuple(clear_after))


@dataclass(slots=True)
class TerminalCapabilities:
    colors: int
    cup: bytes | None
    clear_screen: bytes
    enter_alt: bytes
    exit_alt: bytes
    hide_cursor: bytes
    show_cursor: bytes
    sgr0: bytes
    bold: bytes
    setaf: bytes | None

    @classmethod
    def load(cls, fd: int, term: str) -> "TerminalCapabilities":
        curses.setupterm(term=term, fd=fd)

        def cap(name: str, fallback: bytes = b"") -> bytes:
            value = curses.tigetstr(name)
            return value if value else fallback

        colors = curses.tigetnum("colors")
        return cls(
            colors=max(0, colors),
            cup=curses.tigetstr("cup"),
            clear_screen=cap("clear", b"\x1b[2J\x1b[H"),
            enter_alt=cap("smcup"),
            exit_alt=cap("rmcup"),
            hide_cursor=cap("civis", b"\x1b[?25l"),
            show_cursor=cap("cnorm", b"\x1b[?25h"),
            sgr0=cap("sgr0", b"\x1b[0m"),
            bold=cap("bold", b"\x1b[1m"),
            setaf=curses.tigetstr("setaf"),
        )

    def cursor(self, row: int, column: int) -> bytes:
        if self.cup:
            return bytes(curses.tparm(self.cup, row, column))
        return f"\x1b[{row + 1};{column + 1}H".encode("ascii")

    def style(self, color: int, *, bold: bool, color_enabled: bool) -> bytes:
        chunks = [self.sgr0]
        if bold:
            chunks.append(self.bold)
        if color_enabled and self.setaf and self.colors > 0 and 0 <= color < self.colors:
            chunks.append(bytes(curses.tparm(self.setaf, color)))
        return b"".join(chunks)

    def validate_colors(self, values: Sequence[int]) -> None:
        if self.colors <= 0:
            return
        invalid = [value for value in values if value >= self.colors]
        if invalid:
            raise CLIError(
                f"color index {invalid[0]} exceeds terminal limit {self.colors - 1}"
            )


class TerminalSession:
    def __init__(
        self,
        stdin_fd: int,
        stdout_fd: int,
        capabilities: TerminalCapabilities,
        write: Callable[[bytes], int] = os.write,
    ) -> None:
        self.stdin_fd = stdin_fd
        self.stdout_fd = stdout_fd
        self.capabilities = capabilities
        self.write = write
        self.saved_attrs: list[int | list[int]] | None = None
        self.saved_handlers: dict[int, signal.Handlers] = {}
        self.stop_signal: int | None = None
        self.resized = False
        self.cleaned = False
        self.started = False

    def _signal_handler(self, signum: int, _frame: object) -> None:
        if signum == signal.SIGWINCH:
            self.resized = True
        else:
            self.stop_signal = signum

    def start(self) -> None:
        if self.started:
            return
        try:
            self.saved_attrs = termios.tcgetattr(self.stdin_fd)
            tty.setcbreak(self.stdin_fd)
            watched = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGWINCH]
            for signum in watched:
                self.saved_handlers[signum] = signal.getsignal(signum)
                signal.signal(signum, self._signal_handler)
            self.write(
                self.stdout_fd,
                self.capabilities.enter_alt
                + self.capabilities.hide_cursor
                + self.capabilities.clear_screen,
            )
            self.started = True
        except BaseException:
            self.cleanup()
            raise

    def cleanup(self) -> None:
        if self.cleaned:
            return
        self.cleaned = True
        try:
            if self.started:
                self.write(
                    self.stdout_fd,
                    self.capabilities.sgr0
                    + self.capabilities.show_cursor
                    + self.capabilities.exit_alt,
                )
        finally:
            if self.saved_attrs is not None:
                try:
                    termios.tcsetattr(self.stdin_fd, termios.TCSADRAIN, self.saved_attrs)
                except termios.error:
                    pass
            for signum, handler in self.saved_handlers.items():
                signal.signal(signum, handler)

    def __enter__(self) -> "TerminalSession":
        self.start()
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self.cleanup()


class Renderer:
    def __init__(
        self,
        fd: int,
        capabilities: TerminalCapabilities,
        options: Options,
        write: Callable[[bytes], int] = os.write,
    ) -> None:
        self.fd = fd
        self.capabilities = capabilities
        self.options = options
        self.write = write

    def render(self, frame: FrameResult) -> None:
        chunks: list[bytes] = []
        clear_after = set(frame.clear_after)
        for index, command in enumerate(frame.commands, start=1):
            chunks.append(self.capabilities.cursor(command.y, command.x))
            chunks.append(
                self.capabilities.style(
                    command.color,
                    bold=self.options.bold,
                    color_enabled=self.options.color,
                )
            )
            chunks.append(command.glyph.encode("utf-8"))
            if index in clear_after:
                chunks.append(self.capabilities.clear_screen)
        if chunks:
            self.write(self.fd, b"".join(chunks))


def terminal_size(fd: int) -> tuple[int, int]:
    size = os.get_terminal_size(fd)
    return max(1, size.columns), max(1, size.lines)


def apply_key(options: Options, key: str) -> bool:
    if key == "P":
        options.straight = min(MAX_STRAIGHT, options.straight + 1)
    elif key == "O":
        options.straight = max(INTERACTIVE_MIN_STRAIGHT, options.straight - 1)
    elif key == "F":
        options.fps = min(MAX_FPS, options.fps + 1)
    elif key == "D":
        options.fps = max(MIN_FPS, options.fps - 1)
    elif key == "B":
        options.bold = not options.bold
    elif key == "C":
        options.color = not options.color
    elif key == "K":
        options.keep = not options.keep
    else:
        return False
    return True


class App:
    def __init__(
        self,
        options: Options,
        session: TerminalSession,
        renderer: Renderer,
        engine: Engine,
    ) -> None:
        self.options = options
        self.session = session
        self.renderer = renderer
        self.engine = engine

    def run(self) -> int:
        next_frame = time.monotonic()
        while self.session.stop_signal is None:
            if self.session.resized:
                self.session.resized = False
                width, height = terminal_size(self.session.stdout_fd)
                self.engine.resize(width, height)
            now = time.monotonic()
            frame_seconds = 1.0 / self.options.fps
            timeout = max(0.0, next_frame - now)
            readable, _, _ = select.select([self.session.stdin_fd], [], [], timeout)
            if readable:
                data = os.read(self.session.stdin_fd, 32)
                if not data:
                    return 0
                for byte in data:
                    if not apply_key(self.options, chr(byte)):
                        return 0
            now = time.monotonic()
            if now >= next_frame:
                self.renderer.render(self.engine.step())
                next_frame += frame_seconds
                if now - next_frame > frame_seconds * 4:
                    next_frame = now + frame_seconds
        return 128 + self.session.stop_signal


def preflight() -> tuple[int, int, str]:
    stdin_fd = sys.stdin.fileno()
    stdout_fd = sys.stdout.fileno()
    if not os.isatty(stdin_fd) or not os.isatty(stdout_fd):
        raise RuntimeError("interactive mode requires TTY stdin and stdout")
    term = os.environ.get("TERM", "")
    if not term or term == "dumb":
        raise RuntimeError("interactive mode requires a usable TERM value")
    return stdin_fd, stdout_fd, term


def run_self_test() -> int:
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    check(len(PIPE_SETS) == 10, "ten built-in pipe types")
    check(all(len(pipe_set) == 16 for pipe_set in PIPE_SETS), "16 glyphs per type")
    check(
        all(transition_index(a, b) == a * 4 + b for a in range(4) for b in range(4)),
        "transition matrix",
    )
    rng = random.Random(7)
    check(
        all((choose_direction(direction, 5, rng) - direction) % 4 != 2 for direction in range(4) for _ in range(100)),
        "no reverse turns",
    )
    options, action = parse_options([])
    check(action is None and options == Options(), "CLI defaults")
    repeated, _ = parse_options(["-t", "4", "-t", "5", "-c", "1", "-c", "#ff"])
    check(repeated is not None and len(repeated.types) == 2 and repeated.colors == [1, 255], "repeatable options")
    check(parse_color("#FFA500") == 0xFFA500, "hex colors")
    check(validate_custom_type("cMAYFORCEBWITHYOU") == "MAYFORCEBWITHYOU", "custom type")
    deterministic = Options(pipes=2, seed=123, random_start=True)
    e1 = Engine(deterministic, 10, 5)
    e2 = Engine(deterministic, 10, 5)
    check(e1.pipes == e2.pipes and e1.step() == e2.step(), "deterministic seed")
    edge = Engine(Options(seed=1, keep=True), 2, 2)
    edge.pipes[0] = PipeState(0, 0, Direction.UP, 0, 0)
    frame = edge.step()
    check(frame.commands[0].y == 1, "top edge wrap")
    reset = Engine(Options(pipes=2, seed=1, reset_limit=2), 5, 5)
    check(reset.step().clear, "multi-pipe reset")
    resize = Engine(Options(seed=1), 5, 5)
    resize.resize(0, 0)
    check(resize.width == 1 and resize.height == 1, "safe resize")
    key_options = Options()
    check(apply_key(key_options, "B") and not key_options.bold, "bold key")
    check(apply_key(key_options, "C") and not key_options.color, "color key")
    for width, height in ((1, 1), (2, 3), (80, 24), (500, 200)):
        model = Engine(Options(pipes=8, seed=width * height, reset_limit=0), width, height)
        for _ in range(200):
            model.step()
            check(all(0 <= p.x < model.width and 0 <= p.y < model.height for p in model.pipes), "coordinate bounds")
    try:
        parse_options(["-f", "0"])
    except CLIError:
        pass
    else:
        failures.append("invalid timing rejected")
    if failures:
        for failure in failures:
            print(f"self-test failure: {failure}", file=sys.stderr)
        return 1
    print(SELF_TEST_PASS)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    try:
        options, action = parse_options(argv)
    except (CLIError, ValueError) as exc:
        print(f"pipes: {exc}", file=sys.stderr)
        return 2
    if action == "help":
        print(help_text(), end="")
        return 0
    if action == "version":
        print(f"pipes {VERSION}")
        return 0
    if action == "self-test":
        return run_self_test()
    assert options is not None
    try:
        locale.setlocale(locale.LC_ALL, "")
        stdin_fd, stdout_fd, term = preflight()
        capabilities = TerminalCapabilities.load(stdout_fd, term)
        capabilities.validate_colors(options.colors)
        width, height = terminal_size(stdout_fd)
        session = TerminalSession(stdin_fd, stdout_fd, capabilities)
        renderer = Renderer(stdout_fd, capabilities, options)
        engine = Engine(options, width, height)
        with session:
            return App(options, session, renderer, engine).run()
    except KeyboardInterrupt:
        return 130
    except BrokenPipeError:
        return 1
    except (RuntimeError, CLIError, curses.error, termios.error, OSError) as exc:
        print(f"pipes: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

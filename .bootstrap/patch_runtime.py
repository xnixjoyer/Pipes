#!/usr/bin/env python3
"""Apply reviewed plaintext refinements before assembling pipes_sh.py."""

from pathlib import Path

path = Path("pipes_sh.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one runtime patch target, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    """@dataclass(slots=True, frozen=True)
class FrameResult:
    commands: tuple[DrawCommand, ...]
    clear: bool
""",
    """@dataclass(slots=True, frozen=True)
class FrameResult:
    commands: tuple[DrawCommand, ...]
    clear_after: tuple[int, ...] = ()

    @property
    def clear(self) -> bool:
        return bool(self.clear_after)
""",
)
replace_once(
    """    def step(self) -> FrameResult:
        commands: list[DrawCommand] = []
        clear = False
        for pipe in self.pipes:
""",
    """    def step(self) -> FrameResult:
        commands: list[DrawCommand] = []
        clear_after: list[int] = []
        for pipe in self.pipes:
""",
)
replace_once(
    """            if self.options.reset_limit and self.drawn >= self.options.reset_limit:
                clear = True
                self.drawn = 0
        return FrameResult(tuple(commands), clear)
""",
    """            if self.options.reset_limit and self.drawn >= self.options.reset_limit:
                clear_after.append(len(commands))
                self.drawn = 0
        return FrameResult(tuple(commands), tuple(clear_after))
""",
)
replace_once(
    """    def render(self, frame: FrameResult) -> None:
        chunks: list[bytes] = []
        if frame.clear:
            chunks.append(self.capabilities.clear_screen)
        for command in frame.commands:
            chunks.append(self.capabilities.cursor(command.y, command.x))
""",
    """    def render(self, frame: FrameResult) -> None:
        chunks: list[bytes] = []
        clear_after = set(frame.clear_after)
        for index, command in enumerate(frame.commands, start=1):
            chunks.append(self.capabilities.cursor(command.y, command.x))
""",
)
replace_once(
    """            chunks.append(command.glyph.encode("utf-8"))
        if chunks:
""",
    """            chunks.append(command.glyph.encode("utf-8"))
            if index in clear_after:
                chunks.append(self.capabilities.clear_screen)
        if chunks:
""",
)

path.write_text(text, encoding="utf-8")

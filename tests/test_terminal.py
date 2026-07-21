# SPDX-License-Identifier: MIT
import signal
import unittest
from unittest import mock

import pipes_sh


class TerminalTests(unittest.TestCase):
    def test_cursor_fallback_is_one_based(self):
        caps = pipes_sh.TerminalCapabilities(0, None, b"", b"", b"", b"", b"", b"", b"", None)
        self.assertEqual(caps.cursor(0, 0), b"\x1b[1;1H")
        self.assertEqual(caps.cursor(4, 9), b"\x1b[5;10H")

    def test_cleanup_is_idempotent(self):
        caps = pipes_sh.TerminalCapabilities(0, None, b"", b"A", b"Z", b"H", b"S", b"R", b"", None)
        writes = []
        session = pipes_sh.TerminalSession(0, 1, caps, write=lambda fd, data: writes.append((fd, data)) or len(data))
        session.started = True
        session.saved_attrs = None
        session.cleanup()
        session.cleanup()
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0][1], b"R" + b"S" + b"Z")

    def test_renderer_clears_at_exact_glyph_boundary(self):
        caps = pipes_sh.TerminalCapabilities(0, None, b"CLR", b"", b"", b"", b"", b"R", b"", None)
        writes = []
        renderer = pipes_sh.Renderer(
            1,
            caps,
            pipes_sh.Options(bold=False, color=False),
            write=lambda fd, data: writes.append(data) or len(data),
        )
        frame = pipes_sh.FrameResult(
            (
                pipes_sh.DrawCommand(0, 0, "A", 0),
                pipes_sh.DrawCommand(1, 0, "B", 0),
            ),
            (1,),
        )
        renderer.render(frame)
        self.assertEqual(writes, [b"\x1b[1;1H" + b"RA" + b"CLR" + b"\x1b[1;2H" + b"RB"])

    def test_signal_exit_code(self):
        options = pipes_sh.Options()
        caps = pipes_sh.TerminalCapabilities(0, None, b"", b"", b"", b"", b"", b"", b"", None)
        session = pipes_sh.TerminalSession(0, 1, caps)
        session.stop_signal = signal.SIGTERM
        engine = pipes_sh.Engine(options, 2, 2)
        renderer = mock.Mock()
        app = pipes_sh.App(options, session, renderer, engine)
        self.assertEqual(app.run(), 128 + signal.SIGTERM)


if __name__ == "__main__":
    unittest.main()

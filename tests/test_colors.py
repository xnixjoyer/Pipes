# SPDX-License-Identifier: MIT
import unittest
from unittest import mock

import pipes_sh


class ColorTests(unittest.TestCase):
    def test_decimal_and_hex(self):
        self.assertEqual(pipes_sh.parse_color("0"), 0)
        self.assertEqual(pipes_sh.parse_color("255"), 255)
        self.assertEqual(pipes_sh.parse_color("#FFA500"), 0xFFA500)

    def test_invalid_hex(self):
        for value in ("#", "#xyz", "-1"):
            with self.subTest(value=value), self.assertRaises(pipes_sh.CLIError):
                pipes_sh.parse_color(value)

    def test_color_limit(self):
        caps = pipes_sh.TerminalCapabilities(8, None, b"", b"", b"", b"", b"", b"", b"", b"")
        caps.validate_colors([0, 7])
        with self.assertRaises(pipes_sh.CLIError):
            caps.validate_colors([8])

    @mock.patch("pipes_sh.curses.tparm", return_value=b"COLOR")
    def test_style_recomputed_after_toggles(self, _tparm):
        caps = pipes_sh.TerminalCapabilities(256, None, b"", b"", b"", b"", b"", b"R", b"B", b"S")
        self.assertEqual(caps.style(5, bold=True, color_enabled=True), b"RBCOLOR")
        self.assertEqual(caps.style(5, bold=False, color_enabled=False), b"R")


if __name__ == "__main__":
    unittest.main()

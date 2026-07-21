# SPDX-License-Identifier: MIT
import unittest

import pipes_sh


class CLITests(unittest.TestCase):
    def test_defaults(self):
        options, action = pipes_sh.parse_options([])
        self.assertIsNone(action)
        self.assertEqual(options, pipes_sh.Options())

    def test_repeatable_types_and_colors(self):
        options, _ = pipes_sh.parse_options(["-t", "4", "-t", "5", "-c", "7", "-c", "#ff"])
        self.assertEqual(options.types, [pipes_sh.PIPE_SETS[4], pipes_sh.PIPE_SETS[5]])
        self.assertEqual(options.colors, [7, 255])

    def test_ranges(self):
        for args in (["-p", "0"], ["-f", "19"], ["-f", "101"], ["-s", "4"], ["-s", "16"], ["-r", "-1"]):
            with self.subTest(args=args), self.assertRaises(pipes_sh.CLIError):
                pipes_sh.parse_options(args)

    def test_no_positionals(self):
        with self.assertRaises(pipes_sh.CLIError):
            pipes_sh.parse_options(["extra"])

    def test_help_version_and_self_test_actions(self):
        self.assertEqual(pipes_sh.parse_options(["--help"])[1], "help")
        self.assertEqual(pipes_sh.parse_options(["--version"])[1], "version")
        self.assertEqual(pipes_sh.parse_options(["--self-test"])[1], "self-test")


if __name__ == "__main__":
    unittest.main()

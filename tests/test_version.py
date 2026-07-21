# SPDX-License-Identifier: MIT
import importlib
import unittest


class VersionTests(unittest.TestCase):
    def test_import_has_no_terminal_side_effect(self):
        module = importlib.import_module("pipes_sh")
        self.assertEqual(module.VERSION, "2.0.0")


if __name__ == "__main__":
    unittest.main()

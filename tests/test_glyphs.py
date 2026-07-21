# SPDX-License-Identifier: MIT
import unittest

import pipes_sh


class GlyphTests(unittest.TestCase):
    def test_builtin_shape(self):
        self.assertEqual(len(pipes_sh.PIPE_SETS), 10)
        self.assertTrue(all(len(value) == 16 for value in pipes_sh.PIPE_SETS))

    def test_transition_index(self):
        for old in range(4):
            for new in range(4):
                self.assertEqual(pipes_sh.transition_index(old, new), old * 4 + new)

    def test_custom_type_validation(self):
        self.assertEqual(pipes_sh.validate_custom_type("cMAYFORCEBWITHYOU"), "MAYFORCEBWITHYOU")
        for invalid in ("ctoo-short", "c" + "x" * 17, "c" + "x" * 15 + "\n", "c" + "x" * 15 + "界"):
            with self.subTest(invalid=invalid), self.assertRaises(pipes_sh.CLIError):
                pipes_sh.validate_custom_type(invalid)


if __name__ == "__main__":
    unittest.main()

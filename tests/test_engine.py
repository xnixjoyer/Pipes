# SPDX-License-Identifier: MIT
import unittest

import pipes_sh


class EngineTests(unittest.TestCase):
    def test_deterministic_seed(self):
        options = pipes_sh.Options(pipes=8, random_start=True, seed=42)
        left = pipes_sh.Engine(options, 80, 24)
        right = pipes_sh.Engine(options, 80, 24)
        self.assertEqual(left.pipes, right.pipes)
        self.assertEqual([left.step() for _ in range(20)], [right.step() for _ in range(20)])

    def test_all_edge_wraps(self):
        cases = [
            (0, 0, pipes_sh.Direction.UP, (0, 2)),
            (2, 0, pipes_sh.Direction.RIGHT, (0, 0)),
            (0, 2, pipes_sh.Direction.DOWN, (0, 0)),
            (0, 0, pipes_sh.Direction.LEFT, (2, 0)),
        ]
        for x, y, direction, expected in cases:
            with self.subTest(direction=direction):
                engine = pipes_sh.Engine(pipes_sh.Options(seed=1, keep=True), 3, 3)
                engine.pipes[0] = pipes_sh.PipeState(x, y, int(direction), 0, 0)
                command = engine.step().commands[0]
                self.assertEqual((command.x, command.y), expected)

    def test_keep_mode_preserves_type_and_color(self):
        engine = pipes_sh.Engine(pipes_sh.Options(seed=3, keep=True), 1, 1)
        original = (engine.pipes[0].pipe_type, engine.pipes[0].color)
        for _ in range(20):
            engine.step()
        self.assertEqual((engine.pipes[0].pipe_type, engine.pipes[0].color), original)

    def test_reset_counts_drawn_characters(self):
        engine = pipes_sh.Engine(pipes_sh.Options(pipes=8, reset_limit=8, seed=1), 20, 10)
        frame = engine.step()
        self.assertEqual(frame.clear_after, (8,))
        self.assertEqual(engine.drawn, 0)

    def test_multiple_reset_boundaries_inside_frame(self):
        engine = pipes_sh.Engine(pipes_sh.Options(pipes=8, reset_limit=3, seed=1), 20, 10)
        frame = engine.step()
        self.assertEqual(frame.clear_after, (3, 6))
        self.assertEqual(engine.drawn, 2)

    def test_resize_never_creates_zero_dimensions(self):
        engine = pipes_sh.Engine(pipes_sh.Options(seed=1), 10, 10)
        engine.resize(0, -5)
        self.assertEqual((engine.width, engine.height), (1, 1))
        self.assertEqual((engine.pipes[0].x, engine.pipes[0].y), (0, 0))

    def test_long_model_run(self):
        for seed in range(10):
            engine = pipes_sh.Engine(pipes_sh.Options(pipes=32, seed=seed, reset_limit=0), 7, 5)
            for _ in range(500):
                engine.step()
                for pipe in engine.pipes:
                    self.assertIn(pipe.direction, range(4))
                    self.assertTrue(0 <= pipe.x < engine.width)
                    self.assertTrue(0 <= pipe.y < engine.height)


if __name__ == "__main__":
    unittest.main()

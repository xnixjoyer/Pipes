#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Terminal-independent diagnostic benchmark for the Python engine."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipes_sh import Engine, Options


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=200_000)
    parser.add_argument("--pipes", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    if args.steps <= 0 or args.pipes <= 0:
        parser.error("--steps and --pipes must be positive")
    engine = Engine(Options(pipes=args.pipes, seed=args.seed, reset_limit=0), 120, 40)
    started = time.perf_counter()
    for _ in range(args.steps):
        engine.step()
    elapsed = time.perf_counter() - started
    drawn = args.steps * args.pipes
    print(f"{drawn / elapsed:.0f} pipe-steps/second ({drawn} in {elapsed:.3f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

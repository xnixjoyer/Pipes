# SPDX-License-Identifier: MIT
import fcntl
import os
from pathlib import Path
import pty
import select
import signal
import struct
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "pipes_sh.py"


class IntegrationTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            timeout=20,
        )

    def test_non_tty_commands(self):
        for args in (("--help",), ("--version",), ("--self-test",)):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_optimized_self_test(self):
        result = subprocess.run(
            [sys.executable, "-O", str(SCRIPT), "--self-test"],
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "pipes self-test: PASS")

    def _spawn_pty(self, *args):
        pid, fd = pty.fork()
        if pid == 0:
            os.environ["TERM"] = "xterm-256color"
            os.execv(sys.executable, [sys.executable, str(SCRIPT), "--seed", "1", *args])
        return pid, fd

    def _wait_started(self, fd, timeout=5):
        output = bytearray()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            ready, _, _ = select.select([fd], [], [], 0.1)
            if ready:
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    chunk = b""
                output.extend(chunk)
                if b"\x1b" in output:
                    return bytes(output)
        self.fail("PTY process did not initialize terminal")

    def _collect(self, pid, fd, expected, timeout=10, initial=b""):
        output = bytearray(initial)
        deadline = time.monotonic() + timeout
        status = None
        while time.monotonic() < deadline:
            ready, _, _ = select.select([fd], [], [], 0.1)
            if ready:
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    chunk = b""
                output.extend(chunk)
            done, raw_status = os.waitpid(pid, os.WNOHANG)
            if done:
                status = os.waitstatus_to_exitcode(raw_status)
                break
        if status is None:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            self.fail("PTY process timed out")
        self.assertEqual(status, expected, output.decode("utf-8", "replace"))
        self.assertNotIn(b"Traceback", output)
        self.assertNotIn(b"\x1b[0;", output)
        return bytes(output)

    @unittest.skipUnless(os.name == "posix", "PTY requires POSIX")
    def test_pty_start_and_normal_key(self):
        pid, fd = self._spawn_pty("-t", "4", "-C")
        try:
            initial = self._wait_started(fd)
            os.write(fd, b"q")
            self._collect(pid, fd, 0, initial=initial)
        finally:
            os.close(fd)

    @unittest.skipUnless(os.name == "posix", "PTY requires POSIX")
    def test_pty_signal_exit_codes(self):
        for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            with self.subTest(signum=signum):
                pid, fd = self._spawn_pty("-C")
                try:
                    initial = self._wait_started(fd)
                    os.kill(pid, signum)
                    self._collect(pid, fd, 128 + signum, initial=initial)
                finally:
                    os.close(fd)

    @unittest.skipUnless(os.name == "posix", "PTY requires POSIX")
    def test_termios_and_echo_restored(self):
        import termios

        master, slave = pty.openpty()
        before = termios.tcgetattr(slave)
        pid = os.fork()
        if pid == 0:
            try:
                os.close(master)
                os.dup2(slave, 0)
                os.dup2(slave, 1)
                os.dup2(slave, 2)
                if slave > 2:
                    os.close(slave)
                env = os.environ.copy()
                env["TERM"] = "xterm-256color"
                os.execve(sys.executable, [sys.executable, str(SCRIPT), "--seed", "1", "-C"], env)
            finally:
                os._exit(127)
        try:
            initial = self._wait_started(master)
            during = termios.tcgetattr(slave)
            self.assertFalse(during[3] & termios.ECHO)
            os.write(master, b"q")
            self._collect(pid, master, 0, initial=initial)
            after = termios.tcgetattr(slave)
            self.assertEqual(after, before)
        finally:
            os.close(master)
            os.close(slave)

    @unittest.skipUnless(os.name == "posix", "PTY requires POSIX")
    def test_pty_resize(self):
        pid, fd = self._spawn_pty("-p", "8", "-C")
        try:
            initial = self._wait_started(fd)
            fcntl.ioctl(fd, getattr(__import__("termios"), "TIOCSWINSZ"), struct.pack("HHHH", 1, 1, 0, 0))
            os.kill(pid, signal.SIGWINCH)
            time.sleep(0.2)
            os.write(fd, b"q")
            self._collect(pid, fd, 0, initial=initial)
        finally:
            os.close(fd)


if __name__ == "__main__":
    unittest.main()

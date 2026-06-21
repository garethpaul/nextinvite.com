import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MakefileRootTests(unittest.TestCase):
    def run_make(self, *arguments, environment=None):
        with tempfile.TemporaryDirectory(prefix="nextinvite make path ") as directory:
            root = Path(directory)
            checkout = root / "checkout [hostile] 'quote"
            checkout.mkdir()
            makefile = checkout / "Makefile"
            shutil.copyfile(ROOT / "Makefile", makefile)
            external = root / "external caller"
            external.mkdir()
            env = os.environ.copy()
            if environment:
                env.update(environment)
            result = subprocess.run(
                ["make", "--no-print-directory", "-n", "-f", str(makefile), *arguments],
                cwd=external,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            return result, str(checkout)

    def test_all_aliases_preserve_spaced_absolute_makefile_path(self):
        for target in ("check", "lint", "static-check", "test", "build", "verify"):
            for name, arguments, environment in (
                ("none", (target,), None),
                ("command", (target, "ROOT=/tmp/attacker-root"), None),
                ("environment", (target,), {"ROOT": "/tmp/attacker-root"}),
            ):
                with self.subTest(target=target, override=name):
                    result, checkout = self.run_make(*arguments, environment=environment)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn(checkout, result.stdout)
                    self.assertNotIn("/tmp/attacker-root", result.stdout)

    def test_command_line_makefile_list_override_fails_closed(self):
        result, _ = self.run_make("check", "MAKEFILE_LIST=/tmp/attacker/Makefile")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stderr)

    def test_environment_makefile_list_override_fails_closed(self):
        result, _ = self.run_make(
            "-e", "check", environment={"MAKEFILE_LIST": "/tmp/attacker/Makefile"}
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stderr)


if __name__ == "__main__":
    unittest.main()

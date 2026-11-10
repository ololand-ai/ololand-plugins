"""Hook-contract checks for the ololand-compliance-hooks MNPI guard.

Claude Code PreToolUse contract: a hook that exits 2 blocks the tool call and
Claude sees the hook's STDERR as the denial reason. These tests pipe sample
tool-invocation JSON into the script and assert the exit code and which
channel carries the reason. They do not run Claude Code itself.
"""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "plugins/ololand-compliance-hooks/scripts/mnpi_guard.sh"
BLOCK_EXIT = 2


def run_guard(tool_name, tool_input):
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": tool_name,
            "tool_input": tool_input,
        }
    )
    return subprocess.run(
        ["bash", str(GUARD)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


class MnpiGuardContractTests(unittest.TestCase):
    def test_match_blocks_with_reason_on_stderr_and_empty_stdout(self):
        cases = [
            ("Bash", {"command": "echo 'Q3 numbers are material non-public'"}),
            ("Write", {"file_path": "memo.md", "content": "Inside the insider trading window"}),
            ("Edit", {"file_path": "memo.md", "old_string": "a", "new_string": "earnings under embargo"}),
        ]
        for tool_name, tool_input in cases:
            with self.subTest(tool=tool_name):
                result = run_guard(tool_name, tool_input)
                self.assertEqual(result.returncode, BLOCK_EXIT)
                self.assertIn("OloLand MNPI Guard", result.stderr)
                # Stdout must stay empty: on exit 2 Claude Code reads stderr as
                # the reason, and invalid stdout JSON would only add noise.
                self.assertEqual(result.stdout, "")

    def test_match_is_case_insensitive(self):
        result = run_guard("Bash", {"command": "echo mnpi"})
        self.assertEqual(result.returncode, BLOCK_EXIT)
        self.assertIn("OloLand MNPI Guard", result.stderr)

    def test_clearance_marker_allows_silently(self):
        result = run_guard("Bash", {"command": "echo 'material non-public' # mnpi:cleared"})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_no_match_allows_silently(self):
        result = run_guard("Bash", {"command": "echo 'public 10-K revenue figures'"})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()

"""Regression checks for the OAuth-only Claude directory bundles.

These are package checks, not live connector tests or directory approval.
"""
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import unittest
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = yaml.safe_load((ROOT / "marketplace.yaml").read_text())["plugins"]
CREDENTIAL_ENV = re.compile(
    r"(?:\$\{?|\bos\.environ(?:\.get)?\s*[\[(])"
    r"[\"']?[A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD)\b"
)


class ClaudeDirectoryTests(unittest.TestCase):
    def test_each_listing_has_metadata_and_suitable_existing_icon(self):
        for name in PLUGINS:
            with self.subTest(plugin=name):
                root = ROOT / "plugins" / name
                manifest = json.loads((root / ".claude-plugin/plugin.json").read_text())
                for field in ("documentationUrl", "supportUrl", "privacyPolicyUrl", "termsOfServiceUrl"):
                    self.assertEqual(urlparse(manifest[field]).scheme, "https", field)
                self.assertEqual(manifest["privacyPolicyUrl"], "https://ololand.ai/privacy")
                icon = (root / manifest["icon"]).resolve()
                self.assertTrue(icon.is_relative_to(root.resolve()))
                data = icon.read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                width, height = struct.unpack(">II", data[16:24])
                self.assertEqual(width, height)
                self.assertTrue(512 <= width <= 2048)
                self.assertLess(len(data), 2 * 1024 * 1024)

    def test_bundled_mcp_connections_are_fixed_oauth_endpoints(self):
        found = set()
        for name in PLUGINS:
            root = ROOT / "plugins" / name
            manifest = json.loads((root / ".claude-plugin/plugin.json").read_text())
            self.assertNotIn("userConfig", manifest)
            candidates = []
            if (root / ".mcp.json").exists():
                candidates.append(json.loads((root / ".mcp.json").read_text())["mcpServers"])
            if isinstance(manifest.get("mcpServers"), dict):
                candidates.append(manifest["mcpServers"])
            for servers in candidates:
                for server in servers.values():
                    with self.subTest(plugin=name, server=server):
                        self.assertEqual(server, {"type": "http", "url": "https://api.ololand.ai/mcp"})
                        found.add(name)
        self.assertEqual(found, {"ololand-dd", "ololand-forensic-qoe", "cim-generator"})

    def test_no_distributed_local_credential_forwarding_or_removed_helper_refs(self):
        for name in PLUGINS:
            for path in (ROOT / "plugins" / name).rglob("*"):
                if not path.is_file() or path.suffix not in {".md", ".sh", ".json", ".yaml"}:
                    continue
                text = path.read_text()
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertIsNone(CREDENTIAL_ENV.search(text), "credential environment read/forward")
                    self.assertNotIn("OLOLAND_AGENT_KEY", text)
                    self.assertNotIn("OLOLAND_API_KEY", text)
                    self.assertNotIn("setup_headless.sh", text)

    def test_setup_hook_is_static_context_and_does_not_use_ambient_credentials(self):
        script = ROOT / "plugins/ololand-dd/scripts/setup_gate.sh"
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config = home / ".mcp.json"
            original = '{"mcpServers":{"unrelated":{"url":"https://example.invalid/mcp"}}}\n'
            config.write_text(original)
            outputs = []
            for key in (None, "test-only-do-not-forward"):
                env = {"PATH": "", "HOME": directory}
                if key:
                    env["OLOLAND_AGENT_KEY"] = key
                result = subprocess.run(
                    ["/bin/bash", str(script)], cwd=home, env=env,
                    text=True, capture_output=True, timeout=2, check=True,
                )
                outputs.append(result.stdout)
                self.assertEqual(result.stderr, "")
                self.assertNotIn("test-only-do-not-forward", result.stdout)
                self.assertTrue(result.stdout.startswith("[ololand-dd]"))
                self.assertIn("https://api.ololand.ai/mcp", result.stdout)
                self.assertIn("OAuth", result.stdout)
                self.assertEqual(config.read_text(), original)
                self.assertEqual(sorted(p.name for p in home.iterdir()), [".mcp.json"])
            self.assertEqual(outputs[0], outputs[1])

    def test_removed_headless_credential_writer_is_not_distributed(self):
        self.assertFalse((ROOT / "plugins/ololand-dd/scripts/setup_headless.sh").exists())


if __name__ == "__main__":
    unittest.main()

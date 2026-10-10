#!/usr/bin/env python3
"""Regression checks for Cursor / Grok Bot plugin generation and validation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load_module("generate_plugin_artifacts", ROOT / "scripts/generate-plugin-artifacts.py")
checker = load_module("check_cursor_plugins", ROOT / "scripts/check-cursor-plugins.py")


class GeneratedCursorArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.marketplace = yaml.safe_load((ROOT / "marketplace.yaml").read_text())
        cls.plugins = [
            yaml.safe_load((ROOT / "plugins" / name / "plugin.yaml").read_text())
            for name in cls.marketplace["plugins"]
        ]

    def test_repo_cursor_artifacts_validate(self):
        self.assertEqual(checker.validate(ROOT), [])

    def test_generated_manifests_match_canonical_yaml(self):
        for plugin in self.plugins:
            root = ROOT / "plugins" / plugin["name"]
            expected = generator.cursor_manifest(root, plugin)
            actual = json.loads((root / ".cursor-plugin" / "plugin.json").read_text())
            self.assertEqual(actual, expected, plugin["name"])
            self.assertNotIn("url", actual["author"])
            self.assertTrue(actual["version"])
            if (root / ".mcp.json").is_file():
                self.assertEqual(actual["mcpServers"], "./.mcp.json")
            if (root / "skills").is_dir():
                self.assertEqual(actual["skills"], "./skills/")

    def test_marketplace_schema_and_sources(self):
        marketplace = json.loads((ROOT / ".cursor-plugin" / "marketplace.json").read_text())
        expected = generator.build_cursor_marketplace(self.marketplace, self.plugins)
        self.assertEqual(marketplace, expected)
        self.assertEqual(set(marketplace), {"name", "owner", "metadata", "plugins"})
        self.assertEqual(set(marketplace["owner"]), {"name", "email"})
        for entry in marketplace["plugins"]:
            self.assertEqual(set(entry), {"name", "source", "description"})
            self.assertTrue((ROOT / entry["source"] / ".cursor-plugin" / "plugin.json").is_file())

    def test_mcp_configs_have_no_literal_secrets(self):
        for plugin in self.plugins:
            mcp_path = ROOT / "plugins" / plugin["name"] / ".mcp.json"
            if not mcp_path.is_file():
                continue
            text = mcp_path.read_text()
            self.assertNotIn("olo_agent_sk_", text)
            self.assertNotIn("Bearer ", text)
            self.assertNotRegex(text, r"sk-[A-Za-z0-9]{16,}")

    def test_claude_and_codex_manifests_were_not_rewritten_as_cursor(self):
        for plugin in self.plugins:
            claude = json.loads(
                (ROOT / "plugins" / plugin["name"] / ".claude-plugin" / "plugin.json").read_text()
            )
            self.assertNotIn("mcpServers", claude)
            self.assertNotIn("displayName", claude)

    def test_cursor_hooks_do_not_copy_claude_tool_matchers(self):
        for plugin in self.plugins:
            hooks_path = ROOT / "plugins" / plugin["name"] / ".cursor-plugin" / "hooks.json"
            if not hooks_path.is_file():
                continue
            data = json.loads(hooks_path.read_text())
            events = set(data.get("hooks", {}))
            self.assertTrue(events <= {"sessionStart"})
            self.assertNotIn("PreToolUse", data.get("hooks", {}))
            self.assertNotIn("PostToolUse", data.get("hooks", {}))


class CursorValidationFailures(unittest.TestCase):
    def test_missing_skill_frontmatter_and_literal_secret_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plugin = root / "plugins" / "demo-plugin"
            skill = plugin / "skills" / "broken"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# no frontmatter\n", encoding="utf-8")
            (plugin / ".mcp.json").write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "ololand": {
                                "type": "http",
                                "url": "https://api.ololand.ai/mcp",
                                "headers": {"Authorization": "Bearer sk-live-not-a-placeholder"},
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            (plugin / ".cursor-plugin").mkdir()
            (plugin / ".cursor-plugin" / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "demo-plugin",
                        "displayName": "Demo",
                        "description": "demo",
                        "version": "1.0.0",
                        "author": {"name": "OloLand", "email": "support@ololand.ai"},
                        "homepage": "https://ololand.ai",
                        "repository": "https://github.com/ololand-ai/ololand-plugins",
                        "license": "Apache-2.0",
                        "keywords": ["demo"],
                        "skills": "./skills/",
                        "mcpServers": "./.mcp.json",
                    }
                ),
                encoding="utf-8",
            )
            (root / ".cursor-plugin").mkdir()
            (root / ".cursor-plugin" / "marketplace.json").write_text(
                json.dumps(
                    {
                        "name": "demo",
                        "owner": {"name": "OloLand", "email": "support@ololand.ai"},
                        "plugins": [
                            {
                                "name": "demo-plugin",
                                "source": "./plugins/demo-plugin",
                                "description": "demo",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            errors = checker.validate(root)
            joined = "\n".join(errors)
            self.assertTrue(errors)
            self.assertIn("frontmatter", joined)
            self.assertIn("placeholder", joined.lower())

    def test_parent_path_and_extra_marketplace_fields_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plugin = root / "plugins" / "demo-plugin"
            plugin.mkdir(parents=True)
            (plugin / ".cursor-plugin").mkdir()
            (plugin / ".cursor-plugin" / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "demo-plugin",
                        "displayName": "Demo",
                        "description": "demo",
                        "version": "1.0.0",
                        "author": {"name": "OloLand", "url": "https://ololand.ai"},
                        "homepage": "https://ololand.ai",
                        "repository": "https://github.com/ololand-ai/ololand-plugins",
                        "license": "Apache-2.0",
                        "skills": "../secrets/skills",
                    }
                ),
                encoding="utf-8",
            )
            (root / ".cursor-plugin").mkdir()
            (root / ".cursor-plugin" / "marketplace.json").write_text(
                json.dumps(
                    {
                        "name": "demo",
                        "owner": {"name": "OloLand", "url": "https://ololand.ai"},
                        "plugins": [
                            {
                                "name": "demo-plugin",
                                "source": "./plugins/demo-plugin",
                                "description": "demo",
                                "version": "1.0.0",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            errors = checker.validate(root)
            joined = "\n".join(errors)
            self.assertIn("owner only allows", joined)
            self.assertIn("unsupported fields", joined)
            self.assertIn("must not contain '..'", joined)
            self.assertIn("author only allows", joined)


class GeneratorCheckMode(unittest.TestCase):
    def test_check_mode_passes_on_current_tree(self):
        with patch("sys.argv", ["generate-plugin-artifacts.py", "--check"]):
            self.assertEqual(generator.main(), 0)


if __name__ == "__main__":
    unittest.main()

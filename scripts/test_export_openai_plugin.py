"""Offline regression checks for actual portable upload archives (no live claims)."""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("exporter", ROOT / "scripts/export-openai-plugin.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
PLUGINS = yaml.safe_load((ROOT / "marketplace.yaml").read_text())["plugins"]


class PortableExports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.archives = {}
        cls.source_before = cls.source_hashes()
        for name in PLUGINS:
            output = Path(cls.temp.name) / (name + ".zip")
            with contextlib.redirect_stdout(io.StringIO()):
                exporter.export(name, output)
            with ZipFile(output) as archive:
                cls.archives[name] = {path: archive.read(path) for path in archive.namelist()}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def source_hashes():
        return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (ROOT / "plugins").rglob("*") if path.is_file()}

    def test_source_is_preserved(self):
        self.assertEqual(self.source_before, self.source_hashes())

    def test_every_command_is_packaged_or_explicitly_disclosed_even_when_codex_opted_out(self):
        dd = yaml.safe_load((ROOT / "plugins/ololand-dd/plugin.yaml").read_text())
        self.assertFalse(dd["codex"]["generateCommandSkills"])
        for name, files in self.archives.items():
            exclusion_path = f"{name}/unsupported-workflows.json"
            excluded = (json.loads(files[exclusion_path])["workflows"] if exclusion_path in files else [])
            excluded_ids = {item["workflow_id"] for item in excluded}
            for command in (ROOT / "plugins" / name / "commands").glob("*.md"):
                with self.subTest(plugin=name, command=command.stem):
                    key = f"{name}/skills/{name}-{command.stem}/SKILL.md"
                    if f"{name}/commands/{command.name}" in excluded_ids:
                        self.assertNotIn(key, files)
                    else:
                        self.assertIn(key, files)
                        self.assertIn("## OpenAI execution requirements", files[key].decode())

    def test_correction_write_is_excluded_and_cross_references_do_not_route_to_it(self):
        files = self.archives["ololand-dd"]
        self.assertFalse(any("/skills/ololand-dd-dd-correct/" in path for path in files))
        record = json.loads(files["ololand-dd/unsupported-workflows.json"])
        self.assertEqual(record["format_version"], 1)
        self.assertEqual(len(record["workflows"]), 1)
        exclusion = record["workflows"][0]
        self.assertEqual(exclusion["workflow_id"], "ololand-dd/commands/dd-correct.md")
        self.assertEqual(exclusion["skill_id"], "ololand-dd-dd-correct")
        self.assertEqual(exclusion["status"], "unsupported")
        self.assertEqual(exclusion["reason_code"], "cowork_provenance_only")
        self.assertIn("surface=cowork", exclusion["reason"])
        self.assertIn("Do not invoke submit_agent_claim_correction", exclusion["action"])
        for path, content in files.items():
            if path.endswith("SKILL.md"):
                text = content.decode()
                self.assertNotRegex(text, r"/dd-correct\b|ololand-dd-dd-correct")
                self.assertEqual(text.count("submit_agent_claim_correction"), 1, path)
                self.assertIn("Do not invoke submit_agent_claim_correction from OpenAI", text)
        for name in ("ololand-dd-pre-screen", "ololand-dd-replay-run", "ololand-dd-plan",
                     "ololand-dd-recall", "ololand-dd-remember", "observability-audit-trail", "deal-session-memory"):
            text = files[f"ololand-dd/skills/{name}/SKILL.md"].decode()
            self.assertIn("unsupported OpenAI claim-correction workflow", text)
        canonical = (ROOT / "plugins/ololand-dd/commands/dd-correct.md").read_text()
        self.assertIn("surface=cowork", canonical)
        self.assertIn("Call the OloLand MCP tool `submit_agent_claim_correction`", canonical)

    def test_all_agent_roles_have_portable_skills_with_sequential_fallback(self):
        for name, files in self.archives.items():
            for role in (ROOT / "plugins" / name / "agents").glob("*.md"):
                with self.subTest(plugin=name, role=role.stem):
                    key = f"{name}/skills/{name}-role-{role.stem}/SKILL.md"
                    self.assertIn(key, files)
                    text = files[key].decode()
                    self.assertIn("execute the steps sequentially yourself", text)
                    self.assertIn("Routing to this role alone does not authorize", text)
                    fields = yaml.safe_load(text.split("---\n", 2)[1])
                    self.assertNotIn("model", fields)
        dd = self.archives["ololand-dd"]
        analyst = dd["ololand-dd/skills/ololand-dd-role-dd-analyst/SKILL.md"].decode()
        self.assertIn("exactly once", analyst)
        self.assertIn("eligibility_receipt_id", analyst)
        self.assertIn("ic_blocked", analyst)
        forensic = dd["ololand-dd/skills/ololand-dd-role-forensic-screener/SKILL.md"].decode()
        self.assertIn("classify", forensic.lower())
        self.assertNotIn("citation enforcer will warn", forensic)
        strategist = dd["ololand-dd/skills/ololand-dd-role-war-game-strategist/SKILL.md"].decode()
        self.assertIn("custom premise", strategist)
        self.assertIn("not execution authority", strategist)
        self.assertIn("exact `simulation_id` or `batch_id`", strategist)

    def test_confirmed_all_country_publication_selection_is_packaged(self):
        for name, files in self.archives.items():
            source = yaml.safe_load((ROOT / "plugins" / name / "plugin.yaml").read_text())
            manifest = json.loads(files[f"{name}/plugin.json"])
            # The publisher explicitly selected all supported countries for all four.
            self.assertEqual(source["openai"]["publication"]["countries"], [])
            self.assertEqual(manifest["extensions"]["com.openai"]["publication"]["countries"], [])

    def test_public_listing_icons_and_dependencies(self):
        for name, files in self.archives.items():
            manifest = json.loads(files[f"{name}/plugin.json"])
            interface = manifest["extensions"]["com.openai"]["interface"]
            for key in ("displayName", "shortDescription"):
                self.assertTrue(0 < len(interface[key]) <= 30, (name, key))
            for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
                self.assertTrue(interface[key].startswith("https://"))
            for key in ("logo", "composerIcon"):
                self.assertIn(name + "/" + interface[key].removeprefix("./"), files)
            self.assertNotIn("portable", manifest["extensions"]["com.openai"])
            servers = json.loads(files[f"{name}/mcp.json"])["mcpServers"]
            for path, content in files.items():
                if path.endswith("/agents/openai.yaml"):
                    deps = yaml.safe_load(content)["dependencies"]["tools"]
                    self.assertTrue(deps)
                    for dep in deps:
                        self.assertEqual(dep["type"], "mcp")
                        self.assertEqual(dep["transport"], "streamable_http")
                        self.assertEqual(dep["url"], servers[dep["value"]]["url"])

    def test_every_initial_review_listing_has_five_positive_three_negative_typed_cases(self):
        for name, files in self.archives.items():
            source = yaml.safe_load((ROOT / "plugins" / name / "plugin.yaml").read_text())
            manifest = json.loads(files[f"{name}/plugin.json"])
            cases = manifest["extensions"]["com.openai"]["review"]["test_cases"]
            self.assertEqual(cases, source["openai"]["review"]["test_cases"])
            self.assertEqual(len(cases["positive"]), 5, name)
            self.assertEqual(len(cases["negative"]), 3, name)
            self.assertEqual(len({case["prompt"] for case in cases["positive"]}), 5, name)
            for kind, values in cases.items():
                for case in values:
                    with self.subTest(plugin=name, kind=kind, prompt=case.get("prompt")):
                        fields = ("description", "prompt", "tools_triggered", "expected_behavior") if kind == "positive" else ("description", "prompt")
                        for field in fields:
                            self.assertIsInstance(case[field], str)
                            self.assertTrue(case[field].strip())
                        self.assertNotIn("result", case)
                        self.assertNotIn("status", case)
                        if name != "ololand-forensic-qoe":
                            self.assertIn("not run", case["description"])
                            self.assertNotIn("file_attachment_urls", case)
                            self.assertNotIn("expected_output_url", case)

    def test_no_local_hooks_bindings_secrets_or_stale_provider_dependencies(self):
        for name, files in self.archives.items():
            for path, content in files.items():
                with self.subTest(plugin=name, path=path):
                    self.assertNotIn("hooks", Path(path).parts)
                    self.assertNotIn(Path(path).name, {".app.json", "app.json", ".env", ".mcp.json"})
                    if Path(path).suffix in {".md", ".json", ".yaml", ".csv"}:
                        text = content.decode()
                        self.assertNotRegex(text, r"Claude|Cowork|Codex|CLAUDE_PLUGIN_ROOT|\.claude/|mcp__ololand__|/cmd-[a-z0-9-]+|\.\./\.\./commands/")
                        self.assertNotRegex(text, r"olo_agent_sk_[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9_-]{20,}")

    def test_command_references_resolve_to_packaged_workflows(self):
        dd = self.archives["ololand-dd"]
        body = dd["ololand-dd/skills/deal-sourcing/SKILL.md"].decode()
        self.assertIn("`ololand-dd-source`", body)
        forensic = self.archives["ololand-forensic-qoe"]
        body = forensic["ololand-forensic-qoe/skills/forensic-qoe/SKILL.md"].decode()
        self.assertIn("ololand-forensic-qoe-forensic-screen", body)
        self.assertIn("request that separate plugin", body)

    def test_native_skill_aliases_resolve_to_existing_packaged_skill_names(self):
        files = self.archives["ololand-dd"]
        self.assertIn("ololand-dd/skills/ololand-dd-partner-signoff/SKILL.md", files)
        for native in ("firm-playbook", "healthcare-diligence"):
            fields = yaml.safe_load((ROOT / "plugins/ololand-dd/skills" / native / "SKILL.md").read_text().split("---\n", 2)[1])
            text = files[f"ololand-dd/skills/{fields['name']}/SKILL.md"].decode()
            self.assertIn("`ololand-dd-partner-signoff`", text)
            self.assertNotIn("`/partner-signoff`", text)
        with self.isolated_source("ololand-dd") as (root, source):
            skill = source / "skills/native-reference-test"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: native-reference-test\ndescription: Use /partner-signoff before finalization.\n---\n"
                "Follow `/partner-signoff`, `/ololand-dd:partner-signoff`, and `/ololand-dd-partner-signoff`.\n"
                "Keep [policy](/partner-signoff) and https://app.ololand.ai/policies/partner-signoff unchanged.\n"
            )
            output = root / "public.zip"
            exporter.export("ololand-dd", output)
            with ZipFile(output) as archive:
                text = archive.read("ololand-dd/skills/native-reference-test/SKILL.md").decode()
            self.assertIn("Follow `ololand-dd-partner-signoff`, `ololand-dd-partner-signoff`, and `ololand-dd-partner-signoff`.", text)
            self.assertIn("[policy](/partner-signoff)", text)
            self.assertIn("https://app.ololand.ai/policies/partner-signoff", text)
            fields = yaml.safe_load(text.split("---\n", 2)[1])
            self.assertEqual(fields["description"], "Use ololand-dd-partner-signoff before finalization.")

    def test_managed_agent_export_preserves_literal_response_key_and_neutral_prose(self):
        text = self.archives["ololand-dd"]["ololand-dd/skills/ololand-dd-managed-agent/SKILL.md"].decode()
        self.assertIn("`claude_platform_session_id`", text)
        self.assertIn("session=<claude_platform_session_id>", text)
        self.assertNotIn("hosted-session identifier returned by the tool", text)
        self.assertNotIn("Claude", text)
        self.assertIn("OloLand's hosted agent service", text)

    def test_benford_review_case_uses_real_return_fields_and_submission_guide_matches_version(self):
        files = self.archives["ololand-forensic-qoe"]
        manifest = json.loads(files["ololand-forensic-qoe/plugin.json"])
        cases = manifest["extensions"]["com.openai"]["review"]["test_cases"]["positive"]
        case = next(item for item in cases if item["tools_triggered"] == "run_benford")
        expected = case["expected_behavior"]
        for field in ("status", "sample_size", "minimum_required", "digit_counts", "observed_distribution",
                      "expected_distribution", "chi_square", "mad", "conformity", "most_deviant_digit"):
            self.assertIn(field, expected)
        self.assertIn("Do not invent account-level flags or a p-value", expected)
        self.assertIn("insufficient_sample", expected)
        self.assertNotIn("population counts, account flags, and reliability status", expected)
        guide = (ROOT / "docs/openai-plugin-submission.md").read_text()
        self.assertIn("Package version: " + manifest["version"], guide)
        self.assertIn("ololand-forensic-qoe-" + manifest["version"] + "-openai-draft.zip", guide)
        self.assertNotIn("0.6.4", guide)

    def test_exported_canonical_deal_urls_keep_their_path_segments(self):
        files = self.archives["ololand-dd"]
        paths = {
            "ololand-dd-ic-approve-readiness": ["https://app.ololand.ai/deals/{deal_id}/ic-package"],
            "ololand-dd-qoe-analysis": ["https://app.ololand.ai/deals/{deal_id}/valuation/qoe"],
            "ololand-dd-scenario-analysis": [
                "https://app.ololand.ai/deals/{deal_id}/valuation/scenarios",
                "https://app.ololand.ai/deals/{deal_id}/valuation/real-options",
            ],
            "ololand-dd-role-dd-analyst": [
                "https://app.ololand.ai/deals/{deal_id}/ic-package",
                "https://app.ololand.ai/deals/{deal_id}/valuations",
            ],
        }
        for skill_name, urls in paths.items():
            text = files[f"ololand-dd/skills/{skill_name}/SKILL.md"].decode()
            for url in urls:
                with self.subTest(skill=skill_name, url=url):
                    self.assertIn(url, text)
            self.assertNotIn("{deal_id}ololand-dd-", text)

    def test_command_translation_preserves_absolute_and_relative_links_in_export(self):
        with self.isolated_source("ololand-dd") as (root, source):
            skill = source / "skills/link-reference-test"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: link-reference-test\ndescription: Use /ic-package while preserving https://app.ololand.ai/deals/{deal_id}/ic-package links.\n---\n"
                "Run `/ic-package`, `/ololand-dd:qoe-analysis`, and /valuation when requested.\n"
                "[IC package](https://app.ololand.ai/deals/{deal_id}/ic-package)\n"
                "[IC relative](/ic-package) [QoE relative](/valuation/qoe)\n"
                "`https://app.ololand.ai/deals/{deal_id}/valuation/qoe`\n"
                "Relative path `/valuation/qoe` is a path.\n"
            )
            output = root / "public.zip"
            exporter.export("ololand-dd", output)
            with ZipFile(output) as archive:
                text = archive.read("ololand-dd/skills/link-reference-test/SKILL.md").decode()
            self.assertIn("Run `ololand-dd-ic-package`, `ololand-dd-qoe-analysis`, and ololand-dd-valuation", text)
            self.assertIn("[IC package](https://app.ololand.ai/deals/{deal_id}/ic-package)", text)
            self.assertIn("[IC relative](/ic-package) [QoE relative](/valuation/qoe)", text)
            self.assertIn("`https://app.ololand.ai/deals/{deal_id}/valuation/qoe`", text)
            self.assertIn("Relative path `/valuation/qoe`", text)
            fields = yaml.safe_load(text.split("---\n", 2)[1])
            self.assertEqual(fields["description"], "Use ololand-dd-ic-package while preserving https://app.ololand.ai/deals/{deal_id}/ic-package links.")

    def test_hook_adapters_disclose_limits_and_preserve_human_gates(self):
        for name in ("ololand-dd", "ololand-compliance-hooks"):
            text = self.archives[name][f"{name}/PORTABILITY.md"].decode()
            self.assertIn("OpenAI cannot execute local lifecycle hooks", text)
            self.assertIn("not equivalent", text)
            self.assertIn("human approval gates", text)
        text = self.archives["ololand-compliance-hooks"]["ololand-compliance-hooks/skills/compliance-hooks-setup/SKILL.md"].decode()
        self.assertIn("## Explicit setup", text)
        self.assertIn("## Explicit review", text)
        self.assertIn("Server-side MCP rail auditing remains", text)

    def test_forensic_cases_and_pdf_requirements_are_preserved_and_scoped(self):
        files = self.archives["ololand-forensic-qoe"]
        manifest = json.loads(files["ololand-forensic-qoe/plugin.json"])
        cases = manifest["extensions"]["com.openai"]["review"]["test_cases"]
        self.assertEqual(len(cases["positive"]), 5)
        self.assertEqual(len(cases["negative"]), 3)
        pdf = files["ololand-forensic-qoe/skills/ololand-forensic-qoe-forensic-screen/SKILL.md"].decode()
        self.assertIn("50 service credits", pdf)
        self.assertIn("explicit confirmation", pdf)
        self.assertIn("different coverage", pdf)
        self.assertIn("ololand-forensic-qoe/review-fixtures/general-ledger.csv", files)
        for name in set(PLUGINS) - {"ololand-forensic-qoe"}:
            for path, content in self.archives[name].items():
                if path.endswith("SKILL.md"):
                    execution = content.decode().split("## OpenAI execution requirements", 1)[1]
                    self.assertNotIn("self-serve Full QoE", execution)
                    self.assertNotIn("Statistical flags", execution)

    def test_benford_prompts_preserve_signed_inputs_and_only_returned_statistics(self):
        forensic = self.archives["ololand-forensic-qoe"]
        benford = forensic["ololand-forensic-qoe/skills/ololand-forensic-qoe-benford/SKILL.md"].decode()
        self.assertIn("Negative amounts are evaluated by absolute magnitude", benford)
        self.assertIn("zero and unusable values are ignored", benford)
        self.assertIn("`run_benford(transactions)`", benford)
        self.assertIn("does not return `p_value`", benford)
        self.assertIn("placeholder zero distributions", benford)
        self.assertNotIn("χ² statistic and p-value", benford)
        self.assertNotIn("at least 1,000 line items", benford)
        self.assertNotIn("The engine pulls all GL transactions", benford)
        self.assertNotRegex(benford, r"p\s*[<>]=?\s*0\.")
        screen = forensic["ololand-forensic-qoe/skills/ololand-forensic-qoe-forensic-screen/SKILL.md"].decode()
        self.assertNotRegex(screen, r"p\s*[<>]=?\s*0\.")
        self.assertIn("does not return a p-value", screen)
        for path in ("ololand-forensic-qoe/skills/forensic-qoe/SKILL.md",):
            self.assertIn("absolute magnitude", forensic[path].decode())
        risk = self.archives["ololand-dd"]["ololand-dd/skills/risk-analysis/SKILL.md"].decode()
        self.assertIn("absolute magnitude for negatives", risk)
        self.assertIn("supplies no p-value", risk)

    @contextlib.contextmanager
    def isolated_source(self, name):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "plugins" / name, root / "plugins" / name)
            shutil.copy2(ROOT / "LICENSE", root / "LICENSE")
            with patch.object(exporter, "ROOT", root), contextlib.redirect_stdout(io.StringIO()):
                yield root, root / "plugins" / name

    def test_unknown_missing_or_changed_hooks_adapter_fails_closed(self):
        for mode in ("unknown", "missing", "changed"):
            with self.subTest(mode=mode), self.isolated_source("ololand-dd") as (root, source):
                path = source / "plugin.yaml"
                data = yaml.safe_load(path.read_text())
                if mode == "missing":
                    del data["openai"]["portable"]["hooksAdapter"]
                elif mode == "unknown":
                    data["openai"]["portable"]["hooksAdapter"]["id"] = "silently-drop-hooks"
                else:
                    (source / "hooks/hooks.json").write_text('{"hooks":{"UnknownLifecycle":[]}}')
                path.write_text(yaml.safe_dump(data))
                with self.assertRaisesRegex(ValueError, "hooks adapter|Unsupported local hook"):
                    exporter.export("ololand-dd", root / "bad.zip")
                self.assertFalse((root / "bad.zip").exists())

    def test_hook_fingerprints_cover_actual_guard_and_all_local_implementations(self):
        expected = {
            "ololand-dd": {"hooks/hooks.json", "scripts/setup_gate.sh", "scripts/setup_headless.sh"},
            "ololand-compliance-hooks": {"hooks/hooks.json", *(
                "scripts/" + name + ".sh" for name in (
                    "audit_log", "citation_enforcer", "evidence_quality_warning", "mnpi_guard",
                    "provenance_writeback", "session_banner", "tier_capacity_warning"))},
        }
        for name, paths in expected.items():
            source = ROOT / "plugins" / name
            metadata = yaml.safe_load((source / "plugin.yaml").read_text())
            actual = exporter.reviewed_hook_sources(source)
            self.assertEqual(set(actual), paths)
            self.assertEqual(actual, metadata["openai"]["portable"]["hooksAdapter"]["sourceFilesSha256"])
            self.assertTrue(exporter.portable_adapter(source, metadata))

    def test_changed_direct_and_indirect_hook_scripts_fail_closed_without_execution(self):
        for name, script in (("ololand-dd", "setup_gate.sh"), ("ololand-dd", "setup_headless.sh"),
                             ("ololand-compliance-hooks", "mnpi_guard.sh"),
                             ("ololand-compliance-hooks", "citation_enforcer.sh")):
            with self.subTest(plugin=name, script=script), self.isolated_source(name) as (root, source):
                path = source / "scripts" / script
                marker = root / "must-not-execute"
                path.write_text(path.read_text() + "\ntouch '" + str(marker) + "'\n")
                with self.assertRaisesRegex(ValueError, "every current hook implementation"):
                    exporter.export(name, root / "bad.zip")
                self.assertFalse(marker.exists())
                self.assertFalse((root / "bad.zip").exists())

    def test_missing_or_incomplete_hook_file_declaration_and_added_file_fail_closed(self):
        for mode in ("missing", "incomplete", "added"):
            with self.subTest(mode=mode), self.isolated_source("ololand-dd") as (root, source):
                path = source / "plugin.yaml"
                metadata = yaml.safe_load(path.read_text())
                adapter = metadata["openai"]["portable"]["hooksAdapter"]
                if mode == "missing":
                    del adapter["sourceFilesSha256"]
                elif mode == "incomplete":
                    del adapter["sourceFilesSha256"]["scripts/setup_headless.sh"]
                else:
                    (source / "scripts/new-helper.sh").write_text("#!/bin/sh\nexit 0\n")
                path.write_text(yaml.safe_dump(metadata))
                with self.assertRaisesRegex(ValueError, "every current hook implementation"):
                    exporter.export("ololand-dd", root / "bad.zip")

    def test_unsafe_or_unknown_hook_invocations_fail_closed_even_with_updated_manifest_hash(self):
        commands = (
            'bash "/tmp/outside-hook.sh"',
            'bash "${CLAUDE_PLUGIN_ROOT}/scripts/../outside.sh"',
            'bash "${CLAUDE_PLUGIN_ROOT}/scripts/$(choose-hook).sh"',
            'bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup_gate.sh"; echo injected',
            'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/setup_gate.sh"',
            '[ -n "${CLAUDE_PLUGIN_ROOT}" ] && bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup_gate.sh" || echo "$(outside-command)"',
        )
        for command in commands:
            with self.subTest(command=command), self.isolated_source("ololand-dd") as (root, source):
                hook = source / "hooks/hooks.json"
                data = json.loads(hook.read_text())
                data["hooks"]["SessionStart"][0]["hooks"][0]["command"] = command
                hook.write_text(json.dumps(data))
                digest = hashlib.sha256(hook.read_bytes()).hexdigest()
                path = source / "plugin.yaml"
                metadata = yaml.safe_load(path.read_text())
                adapter = metadata["openai"]["portable"]["hooksAdapter"]
                adapter["sourceSha256"] = digest
                adapter["sourceFilesSha256"]["hooks/hooks.json"] = digest
                path.write_text(yaml.safe_dump(metadata))
                with self.assertRaisesRegex(ValueError, "[Hh]ook|invocation"):
                    exporter.export("ololand-dd", root / "bad.zip")
                self.assertFalse((root / "bad.zip").exists())

    def test_hook_symlinks_are_rejected_before_reading_redirected_files(self):
        for relative in ("hooks/hooks.json", "scripts/setup_gate.sh", "scripts/setup_headless.sh", "scripts"):
            with self.subTest(path=relative), self.isolated_source("ololand-dd") as (root, source):
                original = source / relative
                target = root / "outside"
                if original.is_dir():
                    shutil.copytree(original, target)
                    shutil.rmtree(original)
                else:
                    shutil.copy2(original, target)
                    original.unlink()
                original.symlink_to(target, target_is_directory=target.is_dir())
                with self.assertRaisesRegex(ValueError, "[Ss]ymlinks"):
                    exporter.export("ololand-dd", root / "bad.zip")
                self.assertFalse((root / "bad.zip").exists())

    def test_declared_hook_adapter_cannot_be_bypassed_by_missing_or_dangling_directory(self):
        for mode in ("missing", "dangling"):
            with self.subTest(mode=mode), self.isolated_source("ololand-dd") as (root, source):
                hook_directory = source / "hooks"
                shutil.rmtree(hook_directory)
                if mode == "dangling":
                    hook_directory.symlink_to(root / "nonexistent-hooks", target_is_directory=True)
                with self.assertRaisesRegex(ValueError, "hooks adapter|Symlinks"):
                    exporter.export("ololand-dd", root / "bad.zip")
                self.assertFalse((root / "bad.zip").exists())

    def test_symlinked_command_is_rejected_before_generator_reads_it(self):
        for mode in ("file", "excluded-file", "directory"):
            with self.subTest(mode=mode), self.isolated_source("ololand-dd") as (root, source):
                original = source / "commands" if mode == "directory" else source / "commands" / ("dd-correct.md" if mode == "excluded-file" else "valuation.md")
                target = root / "outside-command"
                if original.is_dir():
                    shutil.copytree(original, target)
                    shutil.rmtree(original)
                else:
                    shutil.copy2(original, target)
                    original.unlink()
                original.symlink_to(target, target_is_directory=target.is_dir())
                real_read = Path.read_text
                def guarded_read(path, *args, **kwargs):
                    if path == original or original in path.parents:
                        self.fail("Redirected command was read before symlink rejection")
                    return real_read(path, *args, **kwargs)
                with patch.object(Path, "read_text", guarded_read):
                    with self.assertRaisesRegex(ValueError, "[Ss]ymlink"):
                        exporter.export("ololand-dd", root / "bad.zip")
                self.assertFalse((root / "bad.zip").exists())

    def test_compliance_openai_starters_describe_explicit_review_and_setup(self):
        source = yaml.safe_load((ROOT / "plugins/ololand-compliance-hooks/plugin.yaml").read_text())
        self.assertEqual(source["defaultPrompt"], ["Configure OloLand compliance hooks.", "Explain citation enforcement.", "Troubleshoot provenance logging."])
        manifest = json.loads(self.archives["ololand-compliance-hooks"]["ololand-compliance-hooks/plugin.json"])
        prompts = manifest["extensions"]["com.openai"]["interface"]["defaultPrompt"]
        self.assertEqual(prompts, source["openai"]["interface"]["defaultPrompt"])
        self.assertEqual(len(prompts), 3)
        self.assertIn("explicit compliance review", prompts[1])
        self.assertTrue(all("hooks" not in prompt and "logging" not in prompt for prompt in prompts))

    def test_shared_artifact_gate_propagates_exporter_suite_failure_for_pr_and_release(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            python = root / "python3"
            python.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$*" >> "$CHECK_CALLS"\nif [ "$1" = "-B" ] && [ "$2" = "-m" ] && [ "$3" = "unittest" ]; then exit 17; fi\nexit 0\n')
            python.chmod(0o755)
            log = root / "calls.txt"
            environment = dict(os.environ, PATH=str(root) + os.pathsep + os.environ["PATH"], CHECK_CALLS=str(log))
            result = subprocess.run(["bash", str(ROOT / "scripts/check-plugin-artifacts.sh")], env=environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 17)
            calls = log.read_text().splitlines()
            self.assertEqual(len(calls), 2)
            self.assertIn("generate-plugin-artifacts.py --check", calls[0])
            self.assertIn("-B -m unittest discover", calls[1])
            self.assertIn("test_export_openai_plugin.py", calls[1])
        workflows = [yaml.safe_load(path.read_text()) for path in (ROOT / ".github/workflows").glob("*.yml")]
        for workflow_name in ("Check plugin artifacts", "Publish release"):
            workflow = next(item for item in workflows if item["name"] == workflow_name)
            self.assertTrue(any("./scripts/check-plugin-artifacts.sh" in step.get("run", "")
                                for job in workflow["jobs"].values() for step in job["steps"]))

    def test_missing_unknown_changed_or_new_agent_role_fails_closed(self):
        for mode in ("missing", "unknown", "changed", "new"):
            with self.subTest(mode=mode), self.isolated_source("ololand-dd") as (root, source):
                path = source / "plugin.yaml"
                data = yaml.safe_load(path.read_text())
                roles = data["openai"]["portable"]["agentRoles"]
                if mode == "missing":
                    del roles["dd-analyst"]
                elif mode == "unknown":
                    roles["dd-analyst"]["adapter"] = "silently-ignore-role"
                elif mode == "changed":
                    agent = source / "agents/dd-analyst.md"
                    agent.write_text(agent.read_text() + "\nUnexpected new execution instruction.\n")
                else:
                    (source / "agents/new-role.md").write_text("---\nname: new-role\ndescription: New role\n---\nNew workflow")
                path.write_text(yaml.safe_dump(data))
                with self.assertRaisesRegex(ValueError, "(?:agent role|portable mapping)"):
                    exporter.export("ololand-dd", root / "bad.zip")
                self.assertFalse((root / "bad.zip").exists())

    def test_private_app_source_is_preserved_and_excluded(self):
        with self.isolated_source("ololand-forensic-qoe") as (root, source):
            private = source / ".app.json"
            private.write_text('{"private_binding":"internal-install-id"}')
            before = private.read_bytes()
            output = root / "public.zip"
            exporter.export("ololand-forensic-qoe", output)
            self.assertEqual(private.read_bytes(), before)
            with ZipFile(output) as archive:
                self.assertFalse(any(".app.json" in path for path in archive.namelist()))
                self.assertFalse(any(b"internal-install-id" in archive.read(path) for path in archive.namelist()))

    def test_generated_correction_wrapper_cannot_restore_excluded_openai_workflow(self):
        with self.isolated_source("ololand-dd") as (root, source):
            metadata = yaml.safe_load((source / "plugin.yaml").read_text())
            metadata["codex"]["generateCommandSkills"] = True
            (source / "plugin.yaml").write_text(yaml.safe_dump(metadata))
            spec = importlib.util.spec_from_file_location("local_generator", root / "scripts/generate-plugin-artifacts.py")
            generator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generator)
            generator.write_or_check_command_skills(source, metadata, False, [])
            wrapper = source / "skills/cmd-dd-correct/SKILL.md"
            self.assertTrue(wrapper.is_file())
            source_before = (source / "commands/dd-correct.md").read_bytes()
            wrapper_before = wrapper.read_bytes()
            output = root / "public.zip"
            exporter.export("ololand-dd", output)
            self.assertEqual((source / "commands/dd-correct.md").read_bytes(), source_before)
            self.assertEqual(wrapper.read_bytes(), wrapper_before)
            with ZipFile(output) as archive:
                self.assertFalse(any("/skills/ololand-dd-dd-correct/" in path for path in archive.namelist()))
                self.assertIn("ololand-dd/unsupported-workflows.json", archive.namelist())

    def test_credentials_in_connection_fail_closed(self):
        with self.isolated_source("ololand-forensic-qoe") as (root, source):
            path = source / ".mcp.json"
            data = json.loads(path.read_text())
            data["mcpServers"]["ololand"]["headers"] = {"Authorization": "Bearer secret"}
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "no credentials"):
                exporter.export("ololand-forensic-qoe", root / "bad.zip")


if __name__ == "__main__":
    unittest.main()

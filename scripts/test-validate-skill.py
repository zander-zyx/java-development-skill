#!/usr/bin/env python3
"""Regression tests for scripts/validate-skill.py."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.skill = Path(self.temp_dir.name) / "java-development"
        shutil.copytree(
            ROOT,
            self.skill,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            [sys.executable, str(self.skill / "scripts" / "validate-skill.py")],
            cwd=self.skill,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )

    def assert_rejected(self, expected_message: str) -> None:
        result = self.run_validator()
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn(expected_message, result.stderr)

    def test_repository_fixture_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)

    def test_skill_name_must_match_directory(self) -> None:
        path = self.skill / "SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "name: java-development", "name: wrong-skill-name", 1
            ),
            encoding="utf-8",
        )
        self.assert_rejected("name must match skill directory")

    def test_duplicate_frontmatter_key_is_rejected(self) -> None:
        path = self.skill / "core" / "java-api-design.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "impact: HIGH", "impact: HIGH\nimpact: HIGH", 1
            ),
            encoding="utf-8",
        )
        self.assert_rejected("duplicate frontmatter key 'impact'")

    def test_malformed_asset_pom_is_rejected(self) -> None:
        path = self.skill / "assets" / "pom-spring-boot-3.xml"
        path.write_text(
            path.read_text(encoding="utf-8").replace("</project>", "</broken>"),
            encoding="utf-8",
        )
        self.assert_rejected("invalid XML")

    def test_boot2_mysql_driver_uses_managed_coordinates(self) -> None:
        path = self.skill / "assets" / "pom-spring-boot-2.xml"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "<groupId>com.mysql</groupId>\n            <artifactId>mysql-connector-j</artifactId>",
                "<groupId>mysql</groupId>\n            <artifactId>mysql-connector-java</artifactId>",
                1,
            ),
            encoding="utf-8",
        )
        self.assert_rejected("use managed com.mysql:mysql-connector-j coordinates")

    def test_lombok_requires_explicit_annotation_processing(self) -> None:
        path = self.skill / "assets" / "pom-spring-boot-3.xml"
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\s*<annotationProcessorPaths>.*?</annotationProcessorPaths>", "", text, count=1, flags=re.DOTALL)
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("Lombok requires an explicit annotationProcessorPaths entry")

    def test_mybatis_plus_must_be_top_level_yaml(self) -> None:
        path = self.skill / "assets" / "application.yml.template"
        text = path.read_text(encoding="utf-8")
        if "\nmybatis-plus:\n" in text:
            text = text.replace("\nmybatis-plus:\n", "\n  mybatis-plus:\n", 1)
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("mybatis-plus must be a top-level YAML key")

    def test_duplicate_metadata_reference_is_rejected(self) -> None:
        path = self.skill / "metadata.json"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            '"https://dev.java/",',
            '"https://dev.java/",\n    "https://dev.java/",',
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("metadata.json: duplicate reference")

    def test_readme_language_switch_is_required(self) -> None:
        path = self.skill / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("[中文](README_zh.md)", "中文", 1),
            encoding="utf-8",
        )
        self.assert_rejected("README.md: missing language switch link")

    def test_mybatis_plus_versions_must_stay_in_sync(self) -> None:
        path = self.skill / "assets" / "pom-spring-boot-3.xml"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"(<mybatis-plus.version>)[^<]+(</mybatis-plus.version>)",
            r"\g<1>3.5.99\g<2>",
            text,
            count=1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("MyBatis-Plus versions drift across POM templates")

    def test_mybatis_plus_version_property_is_required(self) -> None:
        path = self.skill / "assets" / "pom-spring-boot-3.xml"
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\s*<mybatis-plus.version>[^<]*</mybatis-plus.version>", "", text, count=1)
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("missing or empty MyBatis-Plus version property")

    def test_mybatis_plus_version_property_cannot_be_empty(self) -> None:
        path = self.skill / "assets" / "pom-spring-boot-3.xml"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"(<mybatis-plus.version>)[^<]+(</mybatis-plus.version>)",
            r"\g<1> \g<2>",
            text,
            count=1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("missing or empty MyBatis-Plus version property")

    def test_mybatis_plus_rule_versions_match_artifacts(self) -> None:
        path = self.skill / "spring-boot" / "sb-mybatis-plus.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"(<artifactId>mybatis-plus-jsqlparser</artifactId>\s*<version>)[^<]+(</version>)",
            r"\g<1>3.5.99\g<2>",
            text,
            count=1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("mybatis-plus-jsqlparser does not match POM example version")

    def test_open_standard_description_length_is_supported(self) -> None:
        path = self.skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(r'^description: ".*"$', f'description: "{"x" * 600}"', text, count=1, flags=re.MULTILINE)
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)

    def test_excessive_description_length_is_rejected(self) -> None:
        path = self.skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(r'^description: ".*"$', f'description: "{"x" * 1025}"', text, count=1, flags=re.MULTILINE)
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("description is too long")

    def test_excessive_skill_name_length_is_rejected(self) -> None:
        path = self.skill / "SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("name: java-development", f"name: {'a' * 65}", 1),
            encoding="utf-8",
        )
        self.assert_rejected("name is too long")

    def test_skill_file_is_kept_under_500_lines(self) -> None:
        path = self.skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text + "\n".join(f"extra line {line}" for line in range(450)) + "\n", encoding="utf-8")
        self.assert_rejected("500 lines or fewer")

    def test_missing_required_section_is_rejected(self) -> None:
        path = self.skill / "core" / "java-api-design.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("### Why it matters", "### Motivation", 1),
            encoding="utf-8",
        )
        self.assert_rejected("missing required section '### Why it matters'")

    def test_stale_metadata_rule_count_is_rejected(self) -> None:
        path = self.skill / "metadata.json"
        text = path.read_text(encoding="utf-8")
        text = text.replace('"total": 34', '"total": 33', 1)
        path.write_text(text, encoding="utf-8")
        self.assert_rejected("metadata.json: ruleCounts.total is 33; expected 34")

    def test_broken_skill_asset_reference_is_rejected(self) -> None:
        path = self.skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace("assets/pom-spring-boot-3.xml", "assets/pom-spring-boot-9.xml"),
            encoding="utf-8",
        )
        self.assert_rejected("SKILL.md: referenced file does not exist: assets/pom-spring-boot-9.xml")

    def test_unrouted_rule_file_is_rejected(self) -> None:
        path = self.skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace("testing/test-mockito.md", "testing/mockito.md"),
            encoding="utf-8",
        )
        self.assert_rejected("SKILL.md: rule file is not routed: testing/test-mockito.md")

    def test_always_apply_is_rejected(self) -> None:
        path = self.skill / "core" / "java-api-design.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace("impact: HIGH", "impact: HIGH\nalwaysApply: true", 1),
            encoding="utf-8",
        )
        self.assert_rejected("avoid alwaysApply")


if __name__ == "__main__":
    unittest.main()

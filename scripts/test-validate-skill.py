#!/usr/bin/env python3
"""Regression tests for scripts/validate-skill.py."""
from __future__ import annotations

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
        return subprocess.run(
            [sys.executable, str(self.skill / "scripts" / "validate-skill.py")],
            cwd=self.skill,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
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


if __name__ == "__main__":
    unittest.main()

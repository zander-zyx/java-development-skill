#!/usr/bin/env python3
"""Validate the java-development skill without third-party dependencies."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE_DIRS = ["core", "build-tools", "spring-boot", "code-review", "testing", "jvm"]
REQUIRED_SKILL_KEYS = {"name", "description"}
REQUIRED_RULE_KEYS = {"title", "impact", "impactDescription", "tags", "description"}
VALID_IMPACTS = {"HIGH", "MEDIUM", "LOW"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    text = read(path)
    if not text.startswith("---"):
        fail(errors, f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        fail(errors, f"{path.relative_to(ROOT)}: unclosed YAML frontmatter")
        return {}
    data: dict[str, str] = {}
    for idx, raw_line in enumerate(parts[1].splitlines(), start=2):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            fail(errors, f"{path.relative_to(ROOT)}:{idx}: invalid frontmatter line")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            fail(errors, f"{path.relative_to(ROOT)}:{idx}: empty frontmatter key")
            continue
        data[key] = value
    return data


def check_markdown_fences(path: Path, errors: list[str]) -> None:
    text = read(path)
    fence_count = 0
    for line in text.splitlines():
        if re.match(r"^\s*```", line):
            fence_count += 1
    if fence_count % 2:
        fail(errors, f"{path.relative_to(ROOT)}: unclosed Markdown code fence")


def check_skill(errors: list[str]) -> None:
    path = ROOT / "SKILL.md"
    fm = parse_frontmatter(path, errors)
    missing = REQUIRED_SKILL_KEYS - set(fm)
    for key in sorted(missing):
        fail(errors, f"SKILL.md: missing required frontmatter key '{key}'")
    for key in REQUIRED_SKILL_KEYS & set(fm):
        if not fm[key]:
            fail(errors, f"SKILL.md: empty frontmatter key '{key}'")

    text = read(path)
    refs = sorted(set(re.findall(r"`([^`]+\.md)`", text)))
    for ref in refs:
        ref_path = (ROOT / ref).resolve()
        try:
            ref_path.relative_to(ROOT)
        except ValueError:
            fail(errors, f"SKILL.md: reference escapes skill root: {ref}")
            continue
        if not ref_path.exists():
            fail(errors, f"SKILL.md: referenced file does not exist: {ref}")


def rule_files() -> list[Path]:
    files: list[Path] = []
    for dirname in RULE_DIRS:
        base = ROOT / dirname
        if base.exists():
            files.extend(sorted(base.glob("*.md")))
    return files


def check_rules(errors: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for dirname in RULE_DIRS:
        files = sorted((ROOT / dirname).glob("*.md")) if (ROOT / dirname).exists() else []
        counts[dirname] = len(files)
        for path in files:
            fm = parse_frontmatter(path, errors)
            rel = path.relative_to(ROOT)
            missing = REQUIRED_RULE_KEYS - set(fm)
            for key in sorted(missing):
                fail(errors, f"{rel}: missing required frontmatter key '{key}'")
            for key in REQUIRED_RULE_KEYS & set(fm):
                if not fm[key]:
                    fail(errors, f"{rel}: empty frontmatter key '{key}'")
            if "impact" in fm and fm["impact"] not in VALID_IMPACTS:
                fail(errors, f"{rel}: impact must be one of {sorted(VALID_IMPACTS)}, got {fm['impact']!r}")
            if "alwaysApply" in fm:
                fail(errors, f"{rel}: avoid alwaysApply; route from SKILL.md instead")
            check_markdown_fences(path, errors)
    return counts


def check_docs(counts: dict[str, int], errors: list[str]) -> None:
    total = sum(counts.values())
    expected = {
        "TOTAL_RULES": total,
        "CORE_RULES": counts.get("core", 0),
        "BUILD_RULES": counts.get("build-tools", 0),
        "SPRING_BOOT_RULES": counts.get("spring-boot", 0),
        "CODE_REVIEW_RULES": counts.get("code-review", 0),
        "TESTING_RULES": counts.get("testing", 0),
        "JVM_RULES": counts.get("jvm", 0),
    }
    rules = [path.relative_to(ROOT).as_posix() for path in rule_files()]
    skill_text = read(ROOT / "SKILL.md")
    for rule in rules:
        if rule not in skill_text:
            fail(errors, f"SKILL.md: rule file is not routed: {rule}")

    for filename in ["README.md", "README_zh.md"]:
        path = ROOT / filename
        text = read(path)
        for key, value in expected.items():
            marker = f"<!-- {key}: {value} -->"
            if marker not in text:
                fail(errors, f"{filename}: missing or stale marker {marker}")
        for rule in rules:
            if rule not in text:
                fail(errors, f"{filename}: rule file missing from index: {rule}")
        check_markdown_fences(path, errors)


def check_machine_files(errors: list[str]) -> None:
    try:
        json.loads(read(ROOT / "metadata.json"))
    except Exception as exc:  # noqa: BLE001
        fail(errors, f"metadata.json: invalid JSON: {exc}")

    agent_path = ROOT / "agents" / "openai.yaml"
    text = read(agent_path)
    for needle in ["display_name:", "short_description:", "default_prompt:"]:
        if needle not in text:
            fail(errors, f"agents/openai.yaml: missing {needle}")
    check_markdown_fences(agent_path, errors)


def main() -> int:
    errors: list[str] = []
    for path in [ROOT / "SKILL.md", ROOT / "README.md", ROOT / "README_zh.md", ROOT / "CONTRIBUTING.md"]:
        if path.exists():
            check_markdown_fences(path, errors)

    check_skill(errors)
    counts = check_rules(errors)
    check_docs(counts, errors)
    check_machine_files(errors)

    if errors:
        print("Skill validation failed:\n", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Skill validation passed.")
    print("Rule counts:")
    for dirname in RULE_DIRS:
        print(f"- {dirname}: {counts.get(dirname, 0)}")
    print(f"- total: {sum(counts.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

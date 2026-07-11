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
DOC_FILES = ["README.md", "README_zh.md"]
TEXT_FILES = [
    "SKILL.md",
    "README.md",
    "README_zh.md",
    "CONTRIBUTING.md",
    "metadata.json",
    "agents/openai.yaml",
]
FORBIDDEN_DOC_PATTERNS = {
    r"\brules-30\b": "stale 30-rule badge",
    r"\brules-27\b": "stale 27-rule badge",
    r"\b27 rules\b": "stale 27-rule wording",
    r"27 条": "stale 27-rule wording",
    r"Spring Boot engineer": "old Spring Boot-only positioning",
    r"MyBatis-Plus is the default": "old persistence default",
    r"sb-maven-dependencies": "old Maven-only rule filename",
    r"build/build": "ignored build/ directory reference",
    r"alwaysApply:\s*true": "eager rule loading",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def check_text_hygiene(path: Path, errors: list[str]) -> None:
    if not path.exists():
        return
    text = read(path)
    rel = path.relative_to(ROOT)
    if text and not text.endswith("\n"):
        fail(errors, f"{rel}: file must end with exactly one newline")
    if text.endswith("\n\n") or text.endswith("\r\n\r\n"):
        fail(errors, f"{rel}: remove extra blank line at EOF")
    for idx, line in enumerate(text.splitlines(), start=1):
        if line.rstrip() != line:
            fail(errors, f"{rel}:{idx}: trailing whitespace")


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
    frontmatter = text.split("---", 2)[1] if text.startswith("---") and len(text.split("---", 2)) >= 3 else ""
    if len(frontmatter) > 1024:
        fail(errors, f"SKILL.md: frontmatter is too long ({len(frontmatter)} chars; keep under 1024)")
    description = fm.get("description", "")
    if len(description) > 500:
        fail(errors, f"SKILL.md: description is too long ({len(description)} chars; keep under 500)")

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
    rule_paths = rule_files()
    rules = [path.relative_to(ROOT).as_posix() for path in rule_paths]
    impacts = {path.relative_to(ROOT).as_posix(): parse_frontmatter(path, errors).get("impact", "") for path in rule_paths}

    skill_text = read(ROOT / "SKILL.md")
    for rule in rules:
        if rule not in skill_text:
            fail(errors, f"SKILL.md: rule file is not routed: {rule}")

    for filename in DOC_FILES:
        path = ROOT / filename
        text = read(path)
        for pattern, reason in FORBIDDEN_DOC_PATTERNS.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(errors, f"{filename}: forbidden stale wording ({reason}): /{pattern}/")
        for key, value in expected.items():
            marker = f"<!-- {key}: {value} -->"
            if marker not in text:
                fail(errors, f"{filename}: missing or stale marker {marker}")
        for rule in rules:
            if rule not in text:
                fail(errors, f"{filename}: rule file missing from index: {rule}")
            impact = impacts.get(rule, "")
            row_pattern = rf"`{re.escape(rule)}`\s*\|\s*{re.escape(impact)}\s*\|"
            if impact and not re.search(row_pattern, text):
                fail(errors, f"{filename}: rule impact missing or stale for {rule}: {impact}")
        check_markdown_fences(path, errors)


def check_machine_files(errors: list[str]) -> None:
    try:
        metadata = json.loads(read(ROOT / "metadata.json"))
    except Exception as exc:  # noqa: BLE001
        fail(errors, f"metadata.json: invalid JSON: {exc}")
        metadata = {}

    version = str(metadata.get("version", ""))
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(errors, "metadata.json: version must use x.y.z semver")
    abstract = str(metadata.get("abstract", ""))
    for needle in ["Java/JVM", "Maven", "Gradle", "Spring Boot", "JVM troubleshooting"]:
        if needle not in abstract:
            fail(errors, f"metadata.json: abstract should mention {needle!r}")
    code_style = metadata.get("codeStyle", {}) if isinstance(metadata, dict) else {}
    build_tool = str(code_style.get("buildTool", "")) if isinstance(code_style, dict) else ""
    if "Maven" not in build_tool or "Gradle" not in build_tool or "preserve" not in build_tool.lower():
        fail(errors, "metadata.json: codeStyle.buildTool must preserve existing tools and mention Maven and Gradle")
    spring_default = str(code_style.get("springBootDefault", "")) if isinstance(code_style, dict) else ""
    if "optional" not in spring_default.lower():
        fail(errors, "metadata.json: codeStyle.springBootDefault must keep Spring Boot optional")

    agent_path = ROOT / "agents" / "openai.yaml"
    text = read(agent_path)
    for needle in ["display_name:", "short_description:", "default_prompt:"]:
        if needle not in text:
            fail(errors, f"agents/openai.yaml: missing {needle}")
    for needle in ["Java", "Maven", "Gradle", "Spring Boot", "JVM"]:
        if needle not in text:
            fail(errors, f"agents/openai.yaml: should mention {needle!r}")
    check_markdown_fences(agent_path, errors)


def main() -> int:
    errors: list[str] = []
    for filename in TEXT_FILES:
        check_text_hygiene(ROOT / filename, errors)
    for path in rule_files():
        check_text_hygiene(path, errors)
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

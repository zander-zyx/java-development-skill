#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_HOME="$(mktemp -d)"
trap 'rm -rf "$TEST_HOME"' EXIT

ALL_CONFIGS=(
  .agents
  .claude
  .codex
  .cursor
  .gemini
  .copilot
  .kimi-code
  .config/opencode
  .opencode
  .zcode
)

mkdir -p "$TEST_HOME/.codex"

HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh"
test -e "$TEST_HOME/.agents/skills/java-development"
test -e "$TEST_HOME/.codex/skills/java-development"
test ! -e "$TEST_HOME/.claude/skills/java-development"
test ! -e "$TEST_HOME/.cursor/skills/java-development"
test ! -e "$TEST_HOME/.gemini/skills/java-development"
test ! -e "$TEST_HOME/.copilot/skills/java-development"

HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --force
test -e "$TEST_HOME/.agents/skills/java-development"
test -e "$TEST_HOME/.codex/skills/java-development"
test ! -e "$TEST_HOME/.config/opencode/skills/java-development"

HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --uninstall
test ! -e "$TEST_HOME/.agents/skills/java-development"
test ! -e "$TEST_HOME/.codex/skills/java-development"

HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --all
for config in "${ALL_CONFIGS[@]}"; do
  test -e "$TEST_HOME/$config/skills/java-development"
done

HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --uninstall
for config in "${ALL_CONFIGS[@]}"; do
  test ! -e "$TEST_HOME/$config/skills/java-development"
done

CUSTOM_TARGET="$TEST_HOME/custom skills"
HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --copy --target "$CUSTOM_TARGET"
test -f "$CUSTOM_TARGET/java-development/SKILL.md"
test ! -L "$CUSTOM_TARGET/java-development"
test ! -e "$CUSTOM_TARGET/java-development/.video_agent"

INSTALLED="$CUSTOM_TARGET/java-development"

# Whitelist install: every runtime asset must be present...
for required in \
  SKILL.md metadata.json agents/openai.yaml \
  assets/application.yml.template assets/controller-service-test.java \
  assets/pom-spring-boot-2.xml assets/pom-spring-boot-3.xml \
  core build-tools spring-boot code-review testing jvm; do
  test -e "$INSTALLED/$required"
done

# ...and no repository-management file may leak into the user's skill directory.
for forbidden in \
  README.md README_zh.md CONTRIBUTING.md CODE_OF_CONDUCT.md LICENSE \
  AGENTS.md CLAUDE.md install.sh scripts examples .github .git \
  .gitignore .gitattributes; do
  test ! -e "$INSTALLED/$forbidden"
done
if find "$INSTALLED" -name '*.png' -print -quit | grep -q .; then
  echo "Expected no .png files inside the installed skill" >&2
  exit 1
fi

# Every rule file from the repository must survive the whitelist copy.
EXPECTED_RULES="$(
  find "$REPO_ROOT/core" "$REPO_ROOT/build-tools" "$REPO_ROOT/spring-boot" \
    "$REPO_ROOT/code-review" "$REPO_ROOT/testing" "$REPO_ROOT/jvm" \
    -name '*.md' | wc -l
)"
INSTALLED_RULES="$(
  find "$INSTALLED/core" "$INSTALLED/build-tools" "$INSTALLED/spring-boot" \
    "$INSTALLED/code-review" "$INSTALLED/testing" "$INSTALLED/jvm" \
    -name '*.md' | wc -l
)"
if [ "$INSTALLED_RULES" != "$EXPECTED_RULES" ]; then
  echo "Expected $EXPECTED_RULES rule files in install, got $INSTALLED_RULES" >&2
  exit 1
fi

HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --uninstall --target "$CUSTOM_TARGET"
test ! -e "$CUSTOM_TARGET/java-development"

if HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --target >/dev/null 2>&1; then
  echo "Expected --target without a value to fail" >&2
  exit 1
fi
if HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --all --target "$CUSTOM_TARGET" >/dev/null 2>&1; then
  echo "Expected --all with --target to fail" >&2
  exit 1
fi

SOURCE_COPY="$TEST_HOME/source/java-development"
mkdir -p "$SOURCE_COPY"
(
  cd "$REPO_ROOT"
  tar --exclude=.git --exclude=.video_agent --exclude=__pycache__ --exclude='*.pyc' -cf - .
) | (
  cd "$SOURCE_COPY"
  tar -xf -
)
HOME="$TEST_HOME" bash "$SOURCE_COPY/install.sh" --copy --target "$SOURCE_COPY/.agents/skills"
test -f "$SOURCE_COPY/.agents/skills/java-development/SKILL.md"
test ! -e "$SOURCE_COPY/.agents/skills/java-development/.agents/skills/java-development"

if HOME="$TEST_HOME" bash "$SOURCE_COPY/install.sh" --target "$(dirname "$SOURCE_COPY")" >/dev/null 2>&1; then
  echo "Expected installation over the source directory to fail" >&2
  exit 1
fi
test -f "$SOURCE_COPY/SKILL.md"

# An incomplete skill source (missing a whitelisted entry) must be rejected.
INCOMPLETE_COPY="$TEST_HOME/incomplete/java-development"
mkdir -p "$INCOMPLETE_COPY"
(
  cd "$REPO_ROOT"
  tar --exclude=.git --exclude=.video_agent --exclude=.github --exclude=__pycache__ --exclude='*.pyc' -cf - .
) | (
  cd "$INCOMPLETE_COPY"
  tar -xf -
)
rm -rf "$INCOMPLETE_COPY/core"
if HOME="$TEST_HOME" bash "$INCOMPLETE_COPY/install.sh" --copy --target "$TEST_HOME/incomplete-target" >/dev/null 2>&1; then
  echo "Expected install from an incomplete source to fail" >&2
  exit 1
fi

echo "Installer tests passed."

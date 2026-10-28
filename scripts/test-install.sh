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
python "$CUSTOM_TARGET/java-development/scripts/validate-skill.py" >/dev/null
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

echo "Installer tests passed."

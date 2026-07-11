#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_HOME="$(mktemp -d)"
trap 'rm -rf "$TEST_HOME"' EXIT

mkdir -p "$TEST_HOME/.codex"

HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh"
test -e "$TEST_HOME/.codex/skills/java-development"
test ! -e "$TEST_HOME/.claude/skills/java-development"

HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --force
test -e "$TEST_HOME/.codex/skills/java-development"
test ! -e "$TEST_HOME/.claude/skills/java-development"
test ! -e "$TEST_HOME/.config/opencode/skills/java-development"

HOME="$TEST_HOME" bash "$REPO_ROOT/install.sh" --uninstall
test ! -e "$TEST_HOME/.codex/skills/java-development"

echo "Installer tests passed."

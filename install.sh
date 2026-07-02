#!/usr/bin/env bash
# =============================================================================
# install.sh — cross-tool installer for the java-development skill
#
# Detects which AI coding tools are installed (Claude Code, Codex, OpenCode,
# ZCode) and installs the skill into each tool's discovery directory.
#
# Usage:
#   ./install.sh              # install everywhere it can
#   ./install.sh --force      # overwrite existing install
#   ./install.sh --uninstall  # remove from all tools
#
# Works on macOS, Linux, and Windows (Git Bash / WSL).
# =============================================================================
set -euo pipefail

SKILL_NAME="java-development"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="${SCRIPT_DIR}"          # the repo root IS the skill folder

FORCE=0
UNINSTALL=0
for arg in "$@"; do
  case "$arg" in
    --force|-f)     FORCE=1 ;;
    --uninstall|-u) UNINSTALL=1 ;;
    --help|-h)
      echo "Usage: ./install.sh [--force] [--uninstall]"
      echo "  --force       overwrite an existing install"
      echo "  --uninstall   remove the skill from all detected tools"
      exit 0 ;;
    *) echo "Unknown arg: $arg"; exit 1 ;;
  esac
done

# --- target directories per tool (in $HOME) ----------------------------------
# Each tool discovers skills in its own folder. We install into whichever exist.
declare -a TARGETS=(
  "$HOME/.claude/skills"     # Claude Code
  "$HOME/.codex/skills"      # OpenAI Codex CLI
  "$HOME/.opencode/skills"   # OpenCode (fallback; also respects repo-local)
  "$HOME/.zcode/skills"      # ZCode
  "$HOME/.agents/skills"     # generic cross-tool location
)

DEST_FOUND=0
for dir in "${TARGETS[@]}"; do
  # Install only if the tool's parent config dir exists OR the user explicitly
  # forces it (so we don't create .opencode for someone who never used it).
  parent="$(dirname "$dir")"
  if [ "$FORCE" -eq 0 ] && [ ! -d "$parent" ]; then
    continue
  fi

  tool="$(basename "$parent" | sed 's/^\.//')"   # .claude -> claude
  target="$dir/$SKILL_NAME"

  if [ "$UNINSTALL" -eq 1 ]; then
    if [ -e "$target" ] || [ -L "$target" ]; then
      rm -rf "$target"
      echo "✓ uninstalled from $tool ($dir)"
    fi
    continue
  fi

  mkdir -p "$dir"
  DEST_FOUND=1

  # Prefer a symlink so `git pull` updates propagate automatically.
  # Fall back to copy if symlink fails (e.g. no privilege on Windows).
  if [ -e "$target" ] || [ -L "$target" ]; then
    if [ "$FORCE" -eq 0 ]; then
      echo "• $tool: already installed at $target (use --force to overwrite)"
      continue
    fi
    rm -rf "$target"
  fi

  if ln -s "$SKILL_SRC" "$target" 2>/dev/null; then
    echo "✓ $tool: linked → $target"
  else
    cp -R "$SKILL_SRC" "$target"
    echo "✓ $tool: copied → $target (symlink unavailable)"
  fi
done

if [ "$UNINSTALL" -eq 1 ]; then
  echo ""
  echo "Done. Skill removed from all detected tools."
  exit 0
fi

if [ "$DEST_FOUND" -eq 0 ]; then
  echo "⚠ No AI tool config directories found in $HOME."
  echo "  Install at least one of: Claude Code, Codex, OpenCode, ZCode,"
  echo "  then re-run this script. Or use --force to install to all paths."
  exit 1
fi

echo ""
echo "Done. The '$SKILL_NAME' skill is now active in the tools above."
echo "Restart any running tool sessions to pick it up."
echo ""
echo "To verify: open the tool and ask a Java/Spring Boot question; the"
echo "skill should trigger automatically (see SKILL.md description keywords)."

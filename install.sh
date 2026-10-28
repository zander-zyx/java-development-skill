#!/usr/bin/env bash
# =============================================================================
# install.sh — cross-tool installer for the java-development skill
#
# Detects installed AI coding tools and installs the skill into their discovery
# directories. The shared .agents/skills location is always included.
#
# Usage:
#   ./install.sh                       # shared location + detected tools
#   ./install.sh --force               # overwrite existing installs
#   ./install.sh --all                 # install to every supported tool directory
#   ./install.sh --copy                # copy instead of creating symlinks
#   ./install.sh --target <skills-dir> # install to a custom skills directory
#   ./install.sh --uninstall           # remove from all detected tools
#
# Works on macOS, Linux, and Windows (Git Bash / WSL).
# =============================================================================
set -euo pipefail

SKILL_NAME="java-development"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_SRC="${SCRIPT_DIR}"          # the repo root IS the skill folder

FORCE=0
INSTALL_ALL=0
UNINSTALL=0
COPY_ONLY=0
CUSTOM_TARGET=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --force|-f)     FORCE=1; shift ;;
    --all|-a)       INSTALL_ALL=1; shift ;;
    --uninstall|-u) UNINSTALL=1; shift ;;
    --copy)         COPY_ONLY=1; shift ;;
    --target)
      if [ "$#" -lt 2 ] || [ -z "$2" ]; then
        echo "--target requires a non-empty skills directory"
        exit 1
      fi
      CUSTOM_TARGET="$2"
      shift 2 ;;
    --target=*)
      CUSTOM_TARGET="${1#*=}"
      if [ -z "$CUSTOM_TARGET" ]; then
        echo "--target requires a non-empty skills directory"
        exit 1
      fi
      shift ;;
    --help|-h)
      echo "Usage: ./install.sh [--force] [--all] [--copy] [--target <skills-dir>] [--uninstall]"
      echo "  --force       overwrite an existing install"
      echo "  --all         create every supported tool directory"
      echo "  --copy        copy files instead of creating symlinks"
      echo "  --target      install to a custom skills directory"
      echo "  --uninstall   remove the skill from detected or custom directories"
      exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [ -n "$CUSTOM_TARGET" ] && [ "$INSTALL_ALL" -eq 1 ]; then
  echo "--target and --all cannot be used together"
  exit 1
fi

# --- target directories per tool (in $HOME) ----------------------------------
declare -a TARGETS=(
  "$HOME/.agents/skills"     # shared Agent Skills location
  "$HOME/.claude/skills"     # Claude Code
  "$HOME/.codex/skills"      # Codex compatibility location
  "$HOME/.cursor/skills"     # Cursor
  "$HOME/.gemini/skills"     # Gemini CLI
  "$HOME/.copilot/skills"    # GitHub Copilot CLI
  "$HOME/.kimi-code/skills"  # Kimi Code
  "$HOME/.config/opencode/skills" # OpenCode global config
  "$HOME/.opencode/skills"   # OpenCode project/legacy path when pre-existing
  "$HOME/.zcode/skills"      # ZCode
)
if [ -n "$CUSTOM_TARGET" ]; then
  TARGETS=("$CUSTOM_TARGET")
fi

DEST_FOUND=0
for dir in "${TARGETS[@]}"; do
  # The shared location and explicit targets are created automatically. Other
  # tool-specific locations are used only when the tool config already exists.
  parent="$(dirname "$dir")"
  if [ "$INSTALL_ALL" -eq 0 ] && [ -z "$CUSTOM_TARGET" ] \
    && [ "$dir" != "$HOME/.agents/skills" ] && [ ! -d "$parent" ]; then
    continue
  fi

  if [ -n "$CUSTOM_TARGET" ]; then
    tool="custom"
  else
    tool="$(basename "$parent" | sed 's/^\.//')"   # .claude -> claude
  fi
  target="$dir/$SKILL_NAME"
  resolved_target="$target"
  if [ -d "$dir" ]; then
    resolved_target="$(cd "$dir" && pwd -P)/$SKILL_NAME"
  fi
  if [ "$resolved_target" = "$SKILL_SRC" ]; then
    echo "Refusing to install over or remove the skill source directory: $SKILL_SRC"
    exit 1
  fi

  if [ "$UNINSTALL" -eq 1 ]; then
    if [ -e "$target" ] || [ -L "$target" ]; then
      rm -rf "$target"
      echo "✓ uninstalled from $tool ($dir)"
    fi
    continue
  fi

  mkdir -p "$dir"
  resolved_target="$(cd "$dir" && pwd -P)/$SKILL_NAME"
  if [ "$resolved_target" = "$SKILL_SRC" ]; then
    echo "Refusing to install over or remove the skill source directory: $SKILL_SRC"
    exit 1
  fi
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

  if [ "$COPY_ONLY" -eq 0 ] && ln -s "$SKILL_SRC" "$target" 2>/dev/null; then
    echo "✓ $tool: linked → $target"
  else
    declare -a copy_excludes=(--exclude=.git --exclude=.video_agent --exclude=__pycache__ --exclude='*.pyc')
    case "$resolved_target" in
      "$SKILL_SRC"/*)
        relative_target="${resolved_target#"$SKILL_SRC"/}"
        copy_excludes+=(--exclude="$relative_target" --exclude="./$relative_target")
        ;;
    esac
    mkdir -p "$target"
    (
      cd "$SKILL_SRC"
      tar "${copy_excludes[@]}" -cf - .
    ) | (
      cd "$target"
      tar -xf -
    )
    echo "✓ $tool: copied → $target"
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
  echo "  then re-run this script. Or use --all to install to all paths."
  exit 1
fi

echo ""
echo "Done. The '$SKILL_NAME' skill is now active in the tools above."
echo "Restart any running tool sessions to pick it up."
echo ""
echo "To verify: open the tool and ask a Java/JVM question; the"
echo "skill should trigger automatically (see SKILL.md description keywords)."

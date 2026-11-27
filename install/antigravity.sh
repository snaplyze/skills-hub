#!/usr/bin/env bash
#
# Install skills-hub skills into Google Antigravity's global skills directory.
#
# Usage:
#   ./install/antigravity.sh                      # copy all skills (safe default)
#   ./install/antigravity.sh frontend-design      # copy one skill
#   ./install/antigravity.sh --link --all         # symlink all skills
#   ./install/antigravity.sh --verify --ref v1.4.0
#   ./install/antigravity.sh --dry-run            # show what would happen
#   ./install/antigravity.sh --list               # list available skills
#
# Target:
#   $HOME/.gemini/config/skills
#
# Shared across Antigravity App, Antigravity CLI, and Antigravity IDE.
# Use --target DIR to install into a custom directory instead.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SKILLS_DIR="$REPO_ROOT/skills"
LIB_FILE="$SCRIPT_DIR/lib.sh"

if [[ -L "$LIB_FILE" || ! -f "$LIB_FILE" ]]; then
	printf 'error: installer library missing or symlinked: %s\n' "$LIB_FILE" >&2
	exit 1
fi

# shellcheck disable=SC2034
HARNESS_NAME="Antigravity"
# shellcheck disable=SC2034
SCRIPT_USAGE_NAME="./install/antigravity.sh"
# shellcheck disable=SC2034,SC2016
TARGET_HELP='$HOME/.gemini/config/skills'
# shellcheck disable=SC2034
DEFAULT_TARGET_MODE="antigravity"
# shellcheck disable=SC2034
RELOAD_HINT="Installed. Antigravity rereads skills automatically before each turn; in the Antigravity CLI run '/skills reload' (or start a new conversation) to refresh slash commands."

# shellcheck source=install/lib.sh
source "$LIB_FILE"

skills_hub_install_main "$@"

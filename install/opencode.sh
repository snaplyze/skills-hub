#!/usr/bin/env bash
#
# Install skills-hub skills into OpenCode's global skills directory.
#
# Usage:
#   ./install/opencode.sh                      # copy all skills (safe default)
#   ./install/opencode.sh frontend-design      # copy one skill
#   ./install/opencode.sh --link --all         # symlink all skills
#   ./install/opencode.sh --verify --ref v1.4.0
#   ./install/opencode.sh --dry-run            # show what would happen
#   ./install/opencode.sh --list               # list available skills
#
# Target:
#   ${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills
#
# OpenCode also discovers ~/.claude/skills and ~/.agents/skills, but this
# installer intentionally targets OpenCode's own global directory.

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
HARNESS_NAME="OpenCode"
# shellcheck disable=SC2034
SCRIPT_USAGE_NAME="./install/opencode.sh"
# shellcheck disable=SC2034,SC2016
TARGET_HELP='${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills'
# shellcheck disable=SC2034
DEFAULT_TARGET_MODE="opencode"
# shellcheck disable=SC2034
RELOAD_HINT="Installed. OpenCode reloads skills automatically; run 'opencode reload' (or /reload in the TUI) if needed."

# shellcheck source=install/lib.sh
source "$LIB_FILE"

skills_hub_install_main "$@"

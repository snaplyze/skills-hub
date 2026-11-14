#!/usr/bin/env bash
#
# Install skills-hub skills into OpenCode's global skills directory.
#
# Usage:
#   ./install/opencode.sh                 # symlink all skills
#   ./install/opencode.sh frontend-design # symlink one skill
#   ./install/opencode.sh --copy --all    # copy all skills
#   ./install/opencode.sh --dry-run       # show what would happen
#   ./install/opencode.sh --list          # list available skills
#
# Target:
#   ${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills
#
# OpenCode also discovers ~/.claude/skills and ~/.agents/skills, but this
# installer intentionally targets OpenCode's own global directory.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
TARGET_ROOT="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills"

MODE="link"
FORCE=0
DRY_RUN=0
LIST=0
ALL=0
REQUESTED=()

usage() {
	cat <<'EOF'
Install skills-hub skills into OpenCode's global skills directory.

Usage:
  ./install/opencode.sh                 # symlink all skills
  ./install/opencode.sh frontend-design # symlink one skill
  ./install/opencode.sh --copy --all    # copy all skills
  ./install/opencode.sh --dry-run       # show what would happen
  ./install/opencode.sh --list          # list available skills

Options:
  --copy          Copy skill directories instead of symlinking
  --link          Symlink skill directories (default)
  --all           Install every skill in skills/
  --force         Replace existing installations
  --dry-run       Print actions without writing
  --list          List available skills
  --target DIR    Override the target skills directory
  -h, --help      Show this help

Target:
  ${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills
EOF
}

die() {
	printf 'error: %s\n' "$*" >&2
	exit 1
}

info() {
	printf '%s\n' "$*"
}

warn() {
	printf 'warning: %s\n' "$*" >&2
}

while (($# > 0)); do
	case "$1" in
	--copy) MODE="copy" ;;
	--link) MODE="link" ;;
	--force) FORCE=1 ;;
	--dry-run) DRY_RUN=1 ;;
	--list) LIST=1 ;;
	--all) ALL=1 ;;
	--target)
		shift
		[[ $# -gt 0 ]] || die "--target needs a directory"
		TARGET_ROOT="$1"
		;;
	-h | --help)
		usage
		exit 0
		;;
	--*)
		die "unknown option: $1 (try --help)"
		;;
	*)
		REQUESTED+=("$1")
		;;
	esac
	shift
done

case "$TARGET_ROOT" in
"" | "/" | "$HOME") die "refusing unsafe target root: $TARGET_ROOT" ;;
esac

[[ -d "$SKILLS_DIR" ]] || die "skills directory not found: $SKILLS_DIR"

AVAILABLE=()
while IFS= read -r dir; do
	[[ -f "$dir/SKILL.md" ]] && AVAILABLE+=("$(basename "$dir")")
done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -print | sort)

if ((${#AVAILABLE[@]} == 0)); then
	die "no skills found in $SKILLS_DIR"
fi

if ((LIST)); then
	info "Available skills in $SKILLS_DIR:"
	for skill in "${AVAILABLE[@]}"; do
		description="$(sed -n 's/^description:[[:space:]]*//p' "$SKILLS_DIR/$skill/SKILL.md" | head -n 1)"
		info "  $skill"
		[[ -n "$description" ]] && info "    $description"
	done
	exit 0
fi

if ((${#REQUESTED[@]} == 0)); then
	ALL=1
fi

SELECTED=()
if ((ALL)); then
	SELECTED=("${AVAILABLE[@]}")
else
	for requested in "${REQUESTED[@]}"; do
		[[ "$requested" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] ||
			die "invalid skill id: $requested (use lowercase kebab-case)"
		[[ -f "$SKILLS_DIR/$requested/SKILL.md" ]] ||
			die "skill not found: $requested"
		SELECTED+=("$requested")
	done
fi

info "OpenCode skill install"
info "  source: $SKILLS_DIR"
info "  target: $TARGET_ROOT"
info "  mode:   $MODE"
info "  skills: ${SELECTED[*]}"
if ((DRY_RUN)); then
	info "  dry run: no files will be written"
fi
info ""

conflicts=0

for skill in "${SELECTED[@]}"; do
	source_dir="$SKILLS_DIR/$skill"
	target_dir="$TARGET_ROOT/$skill"

	if ! grep -q '^description:' "$source_dir/SKILL.md"; then
		warn "$skill has no description in SKILL.md; OpenCode will not advertise it"
	fi

	# Guard against path traversal and accidental removals outside the target.
	case "$target_dir" in
	"$TARGET_ROOT"/*) ;;
	*) die "refusing to write outside target root: $target_dir" ;;
	esac
	[[ "$(basename "$target_dir")" == "$skill" ]] ||
		die "refusing to write unexpected target: $target_dir"

	if [[ -e "$target_dir" || -L "$target_dir" ]]; then
		if [[ -L "$target_dir" ]] && [[ "$(readlink "$target_dir")" == "$source_dir" ]]; then
			info "  = $skill (already linked)"
			continue
		fi
		if ((FORCE == 0)); then
			warn "$skill already exists at $target_dir; use --force to replace it"
			conflicts=$((conflicts + 1))
			continue
		fi
		info "  ~ $skill (replacing existing)"
		if ((DRY_RUN == 0)); then
			rm -rf "$target_dir"
		fi
	else
		info "  + $skill"
	fi

	if ((DRY_RUN)); then
		continue
	fi

	mkdir -p "$TARGET_ROOT"

	if [[ "$MODE" == "link" ]]; then
		ln -s "$source_dir" "$target_dir"
	else
		cp -R "$source_dir" "$target_dir"
	fi
done

if ((DRY_RUN)); then
	info ""
	info "Dry run complete. Re-run without --dry-run to install."
	exit 0
fi

info ""
if ((conflicts > 0)); then
	warn "$conflicts skill(s) were not installed because they already exist."
	exit 1
fi

info "Installed. Start a new OpenCode session or run /reload."
info "Installed skills live in: $TARGET_ROOT"

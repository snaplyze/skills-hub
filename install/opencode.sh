#!/usr/bin/env bash
#
# Install skills-hub skills into OpenCode's global skills directory.
#
# Usage:
#   ./install/opencode.sh                      # copy all skills (safe default)
#   ./install/opencode.sh frontend-design      # copy one skill
#   ./install/opencode.sh --link --all         # symlink all skills
#   ./install/opencode.sh --verify --ref v1.0.1
#   ./install/opencode.sh --dry-run             # show what would happen
#   ./install/opencode.sh --list                # list available skills
#
# Target:
#   ${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills
#
# OpenCode also discovers ~/.claude/skills and ~/.agents/skills, but this
# installer intentionally targets OpenCode's own global directory.
#
# The default copy mode snapshots skill content and never writes into the
# source checkout. Use --link only when you want live updates from a git clone.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SKILLS_DIR="$REPO_ROOT/skills"

MODE="copy"
FORCE=0
DRY_RUN=0
LIST=0
ALL=0
VERIFY=0
REF=""
TARGET_ROOT=""
TARGET_SET=0
REQUESTED=()
STAGING=""

usage() {
	cat <<'EOF'
Install skills-hub skills into OpenCode's global skills directory.

Usage:
  ./install/opencode.sh                      # copy all skills
  ./install/opencode.sh frontend-design      # copy one skill
  ./install/opencode.sh --link --all         # symlink all skills
  ./install/opencode.sh --verify --ref TAG   # install from a clean exact tag
  ./install/opencode.sh --dry-run            # show what would happen
  ./install/opencode.sh --list               # list available skills

Options:
  --copy          Copy skill directories (default; no source writes)
  --link          Symlink skill directories (explicit opt-in)
  --all           Install every skill in skills/
  --force         Replace existing installations after backing them up
  --verify        Require a clean tracked git checkout at an exact release tag
  --ref TAG       Exact tag required with --verify (for example v1.0.1)
  --dry-run       Print actions without writing
  --list          List available skills
  --target DIR    Override the target skills directory
  -h, --help      Show this help

Target:
  ${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills

Safety:
  The target is canonicalized with realpath -m. Symlinked target roots,
  paths inside the repository, and paths with control characters are refused.
  Replaced skills are moved to <target>/.skills-hub-backups/ before install.
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

cleanup() {
	if [[ -n "$STAGING" && -d "$STAGING" ]]; then
		rm -rf -- "$STAGING" || true
	fi
}
trap cleanup EXIT

expand_tilde() {
	if [[ "$1" == "~" ]]; then
		[[ -n "${HOME:-}" ]] || die "HOME is not set; cannot expand ~"
		printf '%s\n' "$HOME"
	elif [[ "${1:0:1}" == "~" && "${1:1:1}" == "/" ]]; then
		[[ -n "${HOME:-}" ]] || die "HOME is not set; cannot expand ~/"
		printf '%s/%s\n' "$HOME" "${1:2}"
	else
		printf '%s\n' "$1"
	fi
}

has_control_chars() {
	[[ "$1" == *[[:cntrl:]]* ]]
}

is_same_or_ancestor() {
	local ancestor="$1"
	local path="$2"
	[[ "$path" == "$ancestor" || "$path" == "$ancestor"/* ]]
}

canonicalize() {
	realpath -m -- "$1"
}

validate_skill_id() {
	[[ "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]
}

validate_release_ref() {
	[[ "$1" =~ ^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-(0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)(\.(0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$ ]]
}

read_description() {
	local file="$1"
	local in_frontmatter=0
	local block=0
	local style=""
	local text=""
	local line=""
	local value=""
	local content=""

	while IFS= read -r line || [[ -n "$line" ]]; do
		if ((block)); then
			if [[ "$line" =~ ^[[:space:]]+(.*)$ ]]; then
				content="${BASH_REMATCH[1]}"
				if [[ "$style" == ">" ]]; then
					if [[ -n "$text" ]]; then
						text+=" "
					fi
					text+="$content"
				else
					text+="$content"$'\n'
				fi
				continue
			fi
			if [[ -z "$line" ]]; then
				if [[ "$style" != ">" ]]; then
					text+=$'\n'
				fi
				continue
			fi
			break
		fi

		if ((in_frontmatter == 0)); then
			[[ "$line" == "---" ]] || break
			in_frontmatter=1
			continue
		fi
		[[ "$line" == "---" ]] && break

		if [[ "$line" =~ ^description:[[:space:]]*(.*)$ ]]; then
			value="${BASH_REMATCH[1]}"
			case "$value" in
			">" | ">-" | ">+" | "|" | "|-" | "|+")
				style="${value:0:1}"
				block=1
				;;
			*)
				text="$value"
				break
				;;
			esac
		fi
	done <"$file"

	printf '%s' "$text"
}

copy_skill_tree() {
	local source_dir="$1"
	local target_dir="$2"
	local entry=""
	local rel=""

	while IFS= read -r -d '' entry; do
		rel="${entry#"$source_dir"/}"
		[[ "$rel" != "$entry" && -n "$rel" ]] || die "unexpected source path: $entry"
		if [[ -L "$entry" ]]; then
			ln -s -- "$(readlink -- "$entry")" "$target_dir/$rel"
		elif [[ -d "$entry" ]]; then
			mkdir -p -- "$target_dir/$rel"
		elif [[ -f "$entry" ]]; then
			cp -p -- "$entry" "$target_dir/$rel"
		else
			die "unsupported file type in skill source: $entry"
		fi
	done < <(
		find "$source_dir" -mindepth 1 \
			\( -name __pycache__ -o -name .ruff_cache -o -name .pytest_cache \
				-o -name .mypy_cache -o -name node_modules -o -name .git \
				-o -name .venv -o -name .playwright-cli -o -name '*.pyc' \) -prune \
			-o -print0
	)
}

verify_source() {
	git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
		die "cannot --verify: $REPO_ROOT is not a git checkout; archive installs rely on checksum verification"

	local toplevel
	toplevel="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null)" ||
		die "cannot --verify: failed to read the git worktree root"
	toplevel="$(canonicalize "$toplevel")"
	[[ "$toplevel" == "$REPO_ROOT" ]] ||
		die "cannot --verify: $REPO_ROOT is not the root of its git worktree"

	local status
	status="$(git -C "$REPO_ROOT" --no-optional-locks status --porcelain=v1 --untracked-files=normal)" ||
		die "cannot --verify: failed to read git status"
	[[ -z "$status" ]] ||
		die "refusing --verify: the source checkout has local changes:"$'\n'"$status"

	local tag=""
	if [[ -n "$REF" ]]; then
		git -C "$REPO_ROOT" show-ref --verify --quiet "refs/tags/$REF" ||
			die "refusing --verify: tag not found: $REF"
		local head=""
		local tagged=""
		head="$(git -C "$REPO_ROOT" rev-parse --verify HEAD)"
		tagged="$(git -C "$REPO_ROOT" rev-parse --verify "refs/tags/${REF}^{commit}")"
		[[ "$head" == "$tagged" ]] ||
			die "refusing --verify: HEAD ($head) is not the commit tagged $REF ($tagged)"
		tag="$REF"
	else
		local candidate=""
		while IFS= read -r candidate; do
			if validate_release_ref "$candidate"; then
				tag="$candidate"
				break
			fi
		done < <(git -C "$REPO_ROOT" tag --points-at HEAD)
		[[ -n "$tag" ]] ||
			die "refusing --verify: HEAD is not at an exact vX.Y.Z tag; pass --ref TAG"
	fi

	info "  verified clean checkout at $tag"
}

install_skill() {
	local skill="$1"
	local source_dir="$2"
	local target_dir="$3"
	local staging_root=""
	local staged=""
	local backup=""
	local backup_root=""
	local root_now=""

	root_now="$(canonicalize "$TARGET_ROOT")" ||
		die "could not re-canonicalize target: $TARGET_ROOT"
	[[ "$root_now" == "$TARGET_ROOT" && ! -L "$TARGET_ROOT" ]] ||
		die "target root changed or became a symlink during install: $TARGET_ROOT"
	mkdir -p -- "$TARGET_ROOT"
	staging_root="$(mktemp -d -- "$TARGET_ROOT/.skills-hub-tmp.XXXXXX")" ||
		die "could not create a staging directory in $TARGET_ROOT"
	STAGING="$staging_root"
	staged="$staging_root/$skill"

	if [[ "$MODE" == "link" ]]; then
		ln -s -- "$source_dir" "$staged"
	else
		mkdir -p -- "$staged"
		copy_skill_tree "$source_dir" "$staged"
	fi

	if [[ -e "$target_dir" || -L "$target_dir" ]]; then
		backup_root="$TARGET_ROOT/.skills-hub-backups"
		if [[ -L "$backup_root" ]]; then
			die "refusing symlinked backup directory: $backup_root"
		fi
		if [[ -e "$backup_root" && ! -d "$backup_root" ]]; then
			die "backup path is not a directory: $backup_root"
		fi
		mkdir -p -- "$backup_root"
		backup="$backup_root/${skill}.$(date -u +%Y%m%dT%H%M%SZ).$$"
		while [[ -e "$backup" || -L "$backup" ]]; do
			backup="${backup}.1"
		done
		mv -T -- "$target_dir" "$backup" ||
			die "could not move the existing $skill to a backup at $backup"
	fi

	if ! mv -T -- "$staged" "$target_dir"; then
		if [[ -n "$backup" && (-e "$backup" || -L "$backup") ]]; then
			mv -T -- "$backup" "$target_dir" ||
				warn "could not restore the backup at $backup"
		fi
		die "could not install $skill atomically"
	fi

	STAGING=""
	rm -rf -- "$staging_root" || warn "could not remove staging directory: $staging_root"
	if [[ -n "$backup" ]]; then
		info "    backup: $backup"
	fi
}

while (($# > 0)); do
	case "$1" in
	--copy) MODE="copy" ;;
	--link) MODE="link" ;;
	--force) FORCE=1 ;;
	--verify) VERIFY=1 ;;
	--dry-run) DRY_RUN=1 ;;
	--list) LIST=1 ;;
	--all) ALL=1 ;;
	--ref)
		shift
		(($# > 0)) || die "--ref needs a tag"
		REF="$1"
		VERIFY=1
		;;
	--target)
		shift
		(($# > 0)) || die "--target needs a directory"
		TARGET_ROOT="$1"
		TARGET_SET=1
		;;
	-h | --help)
		usage
		exit 0
		;;
	--)
		shift
		while (($# > 0)); do
			REQUESTED+=("$1")
			shift
		done
		break
		;;
	-*)
		die "unknown option: $1 (try --help)"
		;;
	*)
		REQUESTED+=("$1")
		;;
	esac
	shift
done

command -v realpath >/dev/null 2>&1 || die "realpath is required (GNU coreutils)"

if ((TARGET_SET == 0)); then
	[[ -n "${HOME:-}" ]] || die "HOME is not set; pass --target DIR"
	TARGET_ROOT="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills"
fi

[[ -n "$TARGET_ROOT" ]] || die "target directory is empty"
while [[ "$TARGET_ROOT" != "/" && "$TARGET_ROOT" == */ ]]; do
	TARGET_ROOT="${TARGET_ROOT%/}"
done
has_control_chars "$TARGET_ROOT" && die "refusing target path with control characters"
TARGET_ROOT="$(expand_tilde "$TARGET_ROOT")"
while [[ "$TARGET_ROOT" != "/" && "$TARGET_ROOT" == */ ]]; do
	TARGET_ROOT="${TARGET_ROOT%/}"
done
has_control_chars "$TARGET_ROOT" && die "refusing target path with control characters"

if [[ -L "$TARGET_ROOT" ]]; then
	die "refusing symlinked target root: $TARGET_ROOT"
fi
if [[ -e "$TARGET_ROOT" && ! -d "$TARGET_ROOT" ]]; then
	die "target is not a directory: $TARGET_ROOT"
fi

TARGET_ROOT="$(canonicalize "$TARGET_ROOT")" ||
	die "could not canonicalize target: $TARGET_ROOT"
has_control_chars "$TARGET_ROOT" && die "refusing target path with control characters"

if [[ -n "$REF" ]]; then
	has_control_chars "$REF" && die "refusing --ref with control characters"
	validate_release_ref "$REF" ||
		die "invalid --ref tag: $REF (expected vX.Y.Z or a prerelease such as vX.Y.Z-rc.1)"
fi

if [[ -L "$SKILLS_DIR" ]]; then
	die "refusing symlinked source root: $SKILLS_DIR"
fi
[[ -d "$SKILLS_DIR" ]] || die "skills directory not found: $SKILLS_DIR"
SKILLS_DIR="$(canonicalize "$SKILLS_DIR")" ||
	die "could not canonicalize source: $SKILLS_DIR"

HOME_REAL=""
if [[ -n "${HOME:-}" ]]; then
	HOME_REAL="$(canonicalize "$HOME")" || die "could not canonicalize HOME: $HOME"
fi

case "$TARGET_ROOT" in
"" | "/") die "refusing unsafe target root: $TARGET_ROOT" ;;
esac
if [[ -n "$HOME_REAL" && "$TARGET_ROOT" == "$HOME_REAL" ]]; then
	die "refusing unsafe target root: $TARGET_ROOT (the home directory)"
fi
if is_same_or_ancestor "$TARGET_ROOT" "$REPO_ROOT" ||
	is_same_or_ancestor "$REPO_ROOT" "$TARGET_ROOT"; then
	die "refusing target inside, equal to, or above the repository: $TARGET_ROOT"
fi
if is_same_or_ancestor "$TARGET_ROOT" "$SKILLS_DIR" ||
	is_same_or_ancestor "$SKILLS_DIR" "$TARGET_ROOT"; then
	die "refusing target that overlaps the skill sources: $TARGET_ROOT"
fi

AVAILABLE=()
while IFS= read -r -d '' entry; do
	if [[ -d "$entry" && -f "$entry/SKILL.md" ]]; then
		AVAILABLE+=("$(basename -- "$entry")")
	fi
done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -print0 | sort -z)

if ((${#AVAILABLE[@]} == 0)); then
	die "no skills found in $SKILLS_DIR"
fi

if ((LIST)); then
	info "Available skills in $SKILLS_DIR:"
	for skill in "${AVAILABLE[@]}"; do
		description="$(read_description "$SKILLS_DIR/$skill/SKILL.md")"
		info "  $skill"
		if [[ -n "$description" ]]; then
			info "    $description"
		fi
	done
	exit 0
fi

if ((${#REQUESTED[@]} == 0)); then
	ALL=1
fi

SELECTED=()
if ((ALL)); then
	for skill in "${AVAILABLE[@]}"; do
		validate_skill_id "$skill" ||
			die "invalid skill id in skills/: $skill (use lowercase kebab-case)"
		source_dir="$SKILLS_DIR/$skill"
		[[ -L "$source_dir" ]] && die "refusing symlinked skill source: $source_dir"
		[[ -d "$source_dir" ]] || die "skill not found: $skill"
		SELECTED+=("$skill")
	done
else
	for requested in "${REQUESTED[@]}"; do
		has_control_chars "$requested" && die "refusing skill id with control characters"
		validate_skill_id "$requested" ||
			die "invalid skill id: $requested (use lowercase kebab-case)"
		source_dir="$SKILLS_DIR/$requested"
		[[ -L "$source_dir" ]] && die "refusing symlinked skill source: $source_dir"
		[[ -f "$source_dir/SKILL.md" ]] || die "skill not found: $requested"
		SELECTED+=("$requested")
	done
fi

if ((VERIFY)); then
	verify_source
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
	source_real="$(canonicalize "$source_dir")" ||
		die "could not canonicalize skill source: $source_dir"
	target_dir="$TARGET_ROOT/$skill"

	if [[ -z "$(read_description "$source_dir/SKILL.md")" ]]; then
		warn "$skill has no description in SKILL.md; OpenCode will not advertise it"
	fi

	# Guard against path traversal, source overlap, and accidental removals.
	case "$target_dir" in
	"$TARGET_ROOT"/*) ;;
	*) die "refusing to write outside target root: $target_dir" ;;
	esac
	[[ "$(basename -- "$target_dir")" == "$skill" ]] ||
		die "refusing to write unexpected target: $target_dir"
	if [[ "$target_dir" == "$source_real" || "$target_dir" == "$source_real"/* ||
		"$source_real" == "$target_dir"/* ]]; then
		die "refusing target that overlaps the skill source: $target_dir"
	fi

	if [[ -e "$target_dir" || -L "$target_dir" ]]; then
		if [[ "$MODE" == "link" && -L "$target_dir" &&
			"$(readlink -- "$target_dir")" == "$source_real" ]]; then
			info "  = $skill (already linked)"
			continue
		fi
		if ((FORCE == 0)); then
			warn "$skill already exists at $target_dir; use --force to replace it"
			conflicts=$((conflicts + 1))
			continue
		fi
		info "  ~ $skill (replacing existing; backup kept)"
	else
		info "  + $skill"
	fi

	if ((DRY_RUN)); then
		continue
	fi

	install_skill "$skill" "$source_real" "$target_dir"
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

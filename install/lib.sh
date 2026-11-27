#!/usr/bin/env bash
# Shared implementation for skills-hub global installers.
# Sourced by install/antigravity.sh and install/opencode.sh.

# Single source of truth for excluded cache, build, and secret-like paths in --copy mode.
COPY_EXCLUDE_FIND_ARGS=(
	\( -name __pycache__ -o -name .ruff_cache -o -name .pytest_cache
	-o -name .mypy_cache -o -name node_modules -o -name .git
	-o -name .venv -o -name venv -o -name .playwright-cli
	-o -name secrets -o -name .opencode -o -name .claude -o -name .agents
	-o -name .gemini \) -prune
	-o \( -name '*.pyc' -o -name '*.pyo' -o -name '*.pyd' -o -name .DS_Store
	-o -name '.env' -o \( -name '.env.*' ! -name '.env.example' \)
	-o -name '*.key' -o -name '*.pem' -o -name '*.p12'
	-o -name 'credentials*' -o -name 'id_rsa' -o -name 'id_ed25519'
	-o -name 'id_ecdsa' -o -name 'id_dsa' \) -prune
)

MODE="copy"
FORCE=0
DRY_RUN=0
LIST=0
ALL=0
VERIFY=0
REF=""
VERIFIED_COMMIT=""
TARGET_ROOT=""
TARGET_SET=0
REQUESTED=()
STAGING=""
PENDING_BACKUP=""
PENDING_TARGET=""

usage() {
	cat <<EOF
Install skills-hub skills into ${HARNESS_NAME}'s global skills directory.

Usage:
  ${SCRIPT_USAGE_NAME}                      # copy all skills
  ${SCRIPT_USAGE_NAME} frontend-design      # copy one skill
  ${SCRIPT_USAGE_NAME} --link --all         # symlink all skills
  ${SCRIPT_USAGE_NAME} --verify --ref TAG   # install from a clean exact tag
  ${SCRIPT_USAGE_NAME} --dry-run            # show what would happen
  ${SCRIPT_USAGE_NAME} --list               # list available skills

Options:
  --copy          Copy skill directories (default; no source writes)
  --link          Symlink skill directories (explicit opt-in)
  --all           Install every skill in skills/
  --force         Replace existing installations after backing them up
  --verify        Require a clean tracked git checkout at an exact release tag
  --ref TAG       Exact tag required with --verify (for example v1.3.0)
  --dry-run       Print actions without writing
  --list          List available skills
  --target DIR    Override the target skills directory
  -h, --help      Show this help

Target:
  ${TARGET_HELP}

Safety:
  The target is canonicalized with GNU realpath -m. Symlinked target roots,
  internal skill symlinks, paths inside the repository, and paths with control
  characters are refused. Replaced skills are moved to
  <target>/.skills-hub-backups/ before install and restored on interruption.
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
	if [[ -n "$PENDING_BACKUP" && -n "$PENDING_TARGET" && ! -e "$PENDING_TARGET" && ! -L "$PENDING_TARGET" ]]; then
		if [[ -e "$PENDING_BACKUP" || -L "$PENDING_BACKUP" ]]; then
			mv -T -- "$PENDING_BACKUP" "$PENDING_TARGET" ||
				warn "could not restore backup from $PENDING_BACKUP"
		fi
	fi
	PENDING_BACKUP=""
	PENDING_TARGET=""
	if [[ -n "$STAGING" && -d "$STAGING" ]]; then
		rm -rf -- "$STAGING" || true
	fi
	STAGING=""
}

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

trim_trailing_ws() {
	local s="$1"
	s="${s%"${s##*[![:space:]]}"}"
	printf '%s' "$s"
}

unescape_double_quoted() {
	local raw="$1"
	local out=""
	local i=0
	local n=${#raw}
	local ch=""
	local nxt=""
	local bs="\\"
	while ((i < n)); do
		ch="${raw:i:1}"
		if [[ "$ch" == "$bs" && $((i + 1)) -lt $n ]]; then
			nxt="${raw:i+1:1}"
			case "$nxt" in
			'"') out+='"' ;;
			"$bs") out+="$bs" ;;
			n) out+=$'\n' ;;
			t) out+=$'\t' ;;
			r) out+=$'\r' ;;
			*) out+="${bs}${nxt}" ;;
			esac
			i=$((i + 2))
		else
			out+="$ch"
			i=$((i + 1))
		fi
	done
	printf '%s' "$out"
}

find_double_quote_close() {
	local s="$1"
	local i=1
	local n=${#s}
	local ch=""
	local bs="\\"
	while ((i < n)); do
		ch="${s:i:1}"
		if [[ "$ch" == "$bs" ]]; then
			i=$((i + 2))
			continue
		fi
		if [[ "$ch" == '"' ]]; then
			printf '%d' "$i"
			return 0
		fi
		i=$((i + 1))
	done
	return 1
}

find_single_quote_close() {
	local s="$1"
	local i=1
	local n=${#s}
	local sq="'"
	while ((i < n)); do
		if [[ "${s:i:1}" == "$sq" ]]; then
			if ((i + 1 < n)) && [[ "${s:i+1:1}" == "$sq" ]]; then
				i=$((i + 2))
				continue
			fi
			printf '%d' "$i"
			return 0
		fi
		i=$((i + 1))
	done
	return 1
}

read_description() {
	local file="$1"
	local in_frontmatter=0
	local state="none" # none | block | plain | dquote | squote
	local style=""
	local chomp=""
	local block_indent=""
	local blank_count=0
	local text=""
	local cur=""
	local line=""
	local value=""
	local content=""
	local close_idx=0
	local sq="'"

	_finish_desc_scalar() {
		case "$state" in
		block)
			if [[ "$chomp" == "+" ]]; then
				while ((blank_count > 0)); do
					cur+=$'\n'
					blank_count=$((blank_count - 1))
				done
			fi
			text="$cur"
			;;
		plain)
			text="$(trim_trailing_ws "$cur")"
			;;
		dquote)
			text="$(unescape_double_quoted "$cur")"
			;;
		squote)
			text="${cur//"$sq$sq"/$sq}"
			;;
		esac
		state="none"
		cur=""
		block_indent=""
		blank_count=0
	}

	while IFS= read -r line || [[ -n "$line" ]]; do
		line="${line%$'\r'}"

		if ((in_frontmatter == 0)); then
			[[ "$line" == "---" ]] || break
			in_frontmatter=1
			continue
		fi

		if [[ "$line" == "---" ]]; then
			_finish_desc_scalar
			break
		fi

		if [[ "$state" == "block" ]]; then
			if [[ -z "${line//[[:space:]]/}" ]]; then
				blank_count=$((blank_count + 1))
				continue
			fi
			if [[ "$line" =~ ^([[:space:]]+)(.*)$ ]]; then
				if [[ -z "$block_indent" ]]; then
					block_indent="${BASH_REMATCH[1]}"
				fi
				if [[ "$line" == "$block_indent"* ]]; then
					content="${line#"$block_indent"}"
				else
					content="${BASH_REMATCH[2]}"
				fi
				if [[ "$style" == ">" ]]; then
					if [[ -n "$cur" ]]; then
						if ((blank_count > 0)); then
							while ((blank_count > 0)); do
								cur+=$'\n'
								blank_count=$((blank_count - 1))
							done
						else
							cur+=" "
						fi
					else
						blank_count=0
					fi
					cur+="$content"
				else
					if [[ -n "$cur" ]]; then
						cur+=$'\n'
					fi
					while ((blank_count > 0)); do
						cur+=$'\n'
						blank_count=$((blank_count - 1))
					done
					cur+="$content"
				fi
				continue
			fi
			_finish_desc_scalar
		elif [[ "$state" == "plain" ]]; then
			if [[ -z "${line//[[:space:]]/}" ]]; then
				continue
			fi
			if [[ "$line" =~ ^[[:space:]]+(.*)$ ]]; then
				content="$(trim_trailing_ws "${BASH_REMATCH[1]}")"
				if [[ "$content" == \#* ]]; then
					continue
				fi
				if [[ -z "$cur" && "${content:0:1}" == '"' ]]; then
					if close_idx="$(find_double_quote_close "$content")"; then
						cur="${content:1:close_idx-1}"
						state="dquote"
						_finish_desc_scalar
					else
						cur="${content:1}"
						state="dquote"
					fi
					continue
				fi
				if [[ -z "$cur" && "${content:0:1}" == "$sq" ]]; then
					if close_idx="$(find_single_quote_close "$content")"; then
						cur="${content:1:close_idx-1}"
						state="squote"
						_finish_desc_scalar
					else
						cur="${content:1}"
						state="squote"
					fi
					continue
				fi
				content="${content%%[[:space:]]#*}"
				content="$(trim_trailing_ws "$content")"
				if [[ -n "$content" ]]; then
					if [[ -n "$cur" ]]; then
						cur+=" "
					fi
					cur+="$content"
				fi
				continue
			fi
			_finish_desc_scalar
		elif [[ "$state" == "dquote" ]]; then
			if [[ "$line" =~ ^[[:space:]]*(.*)$ ]]; then
				content="${BASH_REMATCH[1]}"
				if close_idx="$(find_double_quote_close " $content")"; then
					if ((close_idx > 1)); then
						[[ -n "$cur" ]] && cur+=" "
						cur+="${content:0:close_idx-1}"
					fi
					_finish_desc_scalar
				else
					[[ -n "$cur" ]] && cur+=" "
					cur+="$content"
				fi
				continue
			fi
			_finish_desc_scalar
		elif [[ "$state" == "squote" ]]; then
			if [[ "$line" =~ ^[[:space:]]*(.*)$ ]]; then
				content="${BASH_REMATCH[1]}"
				if close_idx="$(find_single_quote_close " $content")"; then
					if ((close_idx > 1)); then
						[[ -n "$cur" ]] && cur+=" "
						cur+="${content:0:close_idx-1}"
					fi
					_finish_desc_scalar
				else
					[[ -n "$cur" ]] && cur+=" "
					cur+="$content"
				fi
				continue
			fi
			_finish_desc_scalar
		fi

		if [[ "$line" =~ ^description:[[:space:]]*(.*)$ ]]; then
			value="$(trim_trailing_ws "${BASH_REMATCH[1]}")"
			if [[ "$value" =~ ^([>|])([+-]?[0-9]?|[0-9]?[+-]?)([[:space:]]+#.*)?$ ]]; then
				style="${BASH_REMATCH[1]}"
				chomp="${BASH_REMATCH[2]//[0-9]/}"
				state="block"
				cur=""
				block_indent=""
				blank_count=0
			elif [[ -z "$value" || "$value" == \#* ]]; then
				state="plain"
				cur=""
			elif [[ "${value:0:1}" == '"' ]]; then
				if close_idx="$(find_double_quote_close "$value")"; then
					cur="${value:1:close_idx-1}"
					state="dquote"
					_finish_desc_scalar
				else
					cur="${value:1}"
					state="dquote"
				fi
			elif [[ "${value:0:1}" == "$sq" ]]; then
				if close_idx="$(find_single_quote_close "$value")"; then
					cur="${value:1:close_idx-1}"
					state="squote"
					_finish_desc_scalar
				else
					cur="${value:1}"
					state="squote"
				fi
			else
				value="${value%%[[:space:]]#*}"
				cur="$(trim_trailing_ws "$value")"
				state="plain"
			fi
		fi
	done <"$file"

	if [[ "$state" != "none" ]]; then
		_finish_desc_scalar
	fi

	printf '%s' "$text"
}

check_skill_tree_safe() {
	local source_dir="$1"
	local prune_excluded="${2:-1}"
	local bad_entry=""
	local entry=""
	local find_pid=0

	if ((prune_excluded)); then
		exec 3< <(
			find "$source_dir" -mindepth 1 \
				"${COPY_EXCLUDE_FIND_ARGS[@]}" \
				-o \( -type l -o \( ! -type f ! -type d \) \) -print0
		)
	else
		exec 3< <(
			find "$source_dir" -mindepth 1 \
				\( -type l -o \( ! -type f ! -type d \) \) -print0
		)
	fi
	find_pid=$!
	while IFS= read -r -d '' entry <&3; do
		if [[ -z "$bad_entry" ]]; then
			bad_entry="$entry"
		fi
	done
	exec 3<&-
	wait "$find_pid" || die "failed to scan skill source tree: $source_dir"

	if [[ -n "$bad_entry" ]]; then
		if [[ -L "$bad_entry" ]]; then
			die "refusing symlink inside skill source: $bad_entry"
		fi
		die "unsupported file type in skill source: $bad_entry"
	fi
}

check_verified_git_tree_safe() {
	local skill="$1"
	local record=""
	local mode=""
	local bad_record=""
	local git_pid=0

	exec 3< <(git -C "$REPO_ROOT" ls-tree -r -z "$VERIFIED_COMMIT" -- "skills/$skill")
	git_pid=$!
	while IFS= read -r -d '' record <&3; do
		mode="${record%% *}"
		if [[ "$mode" == "120000" || "$mode" == "160000" ]]; then
			if [[ -z "$bad_record" ]]; then
				bad_record="$record"
			fi
		fi
	done
	exec 3<&-
	wait "$git_pid" || die "failed to inspect verified git tree for skill: $skill"

	if [[ -n "$bad_record" ]]; then
		die "refusing symlink or gitlink inside verified skill source: $bad_record"
	fi
}

copy_skill_tree() {
	local source_dir="$1"
	local target_dir="$2"

	find "$source_dir" -mindepth 1 \
		"${COPY_EXCLUDE_FIND_ARGS[@]}" \
		-o -printf '%P\0' |
		tar -C "$source_dir" --no-recursion --verbatim-files-from --null -T - -cf - |
		tar -C "$target_dir" --no-same-owner -xf -
}

copy_verified_skill_from_git() {
	local skill="$1"
	local staging_root="$2"

	git -C "$REPO_ROOT" -c tar.umask=0022 archive --format=tar "$VERIFIED_COMMIT" -- "skills/$skill" |
		tar -C "$staging_root" --strip-components=1 --no-same-owner -xf -
}

verify_source() {
	command -v git >/dev/null 2>&1 || die "git is required for --verify"

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

	local ignored=""
	local path=""
	local ls_pid=0
	exec 3< <(git -C "$REPO_ROOT" ls-files -z --others --ignored --exclude-standard -- skills/)
	ls_pid=$!
	while IFS= read -r -d '' path <&3; do
		if [[ "$MODE" == "link" ]]; then
			ignored+="${path}"$'\n'
			continue
		fi
		case "$path" in
		*/__pycache__/* | */__pycache__ | *.pyc | *.pyo | *.pyd | */.pytest_cache/* | */.ruff_cache/* | */.mypy_cache/*)
			continue
			;;
		*)
			ignored+="${path}"$'\n'
			;;
		esac
	done
	exec 3<&-
	wait "$ls_pid" || die "cannot --verify: failed to check ignored files under skills/"
	[[ -z "$ignored" ]] ||
		die "refusing --verify: ignored files exist inside skills/:"$'\n'"$ignored"

	local head=""
	head="$(git -C "$REPO_ROOT" rev-parse --verify HEAD)" ||
		die "cannot --verify: failed to resolve HEAD"

	local tag=""
	if [[ -n "$REF" ]]; then
		git -C "$REPO_ROOT" show-ref --verify --quiet "refs/tags/$REF" ||
			die "refusing --verify: tag not found: $REF"
		local tagged=""
		tagged="$(git -C "$REPO_ROOT" rev-parse --verify "refs/tags/${REF}^{commit}")"
		[[ "$head" == "$tagged" ]] ||
			die "refusing --verify: HEAD ($head) is not the commit tagged $REF ($tagged)"
		tag="$REF"
	else
		local candidate=""
		local tag_pid=0
		exec 3< <(git -C "$REPO_ROOT" -c versionsort.suffix=- tag --points-at HEAD --sort=-v:refname)
		tag_pid=$!
		while IFS= read -r candidate <&3; do
			if [[ -z "$tag" ]] && validate_release_ref "$candidate"; then
				tag="$candidate"
			fi
		done
		exec 3<&-
		wait "$tag_pid" || die "cannot --verify: failed to list tags at HEAD"
		[[ -n "$tag" ]] ||
			die "refusing --verify: HEAD is not at an exact vX.Y.Z tag; pass --ref TAG"
	fi

	VERIFIED_COMMIT="$head"
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
	staging_root="$(mktemp -d -- "$TARGET_ROOT/.skills-hub-tmp.XXXXXX")" ||
		die "could not create a staging directory in $TARGET_ROOT"
	STAGING="$staging_root"
	staged="$staging_root/$skill"

	if [[ "$MODE" == "link" ]]; then
		ln -s -- "$source_dir" "$staged"
	elif ((VERIFY)); then
		copy_verified_skill_from_git "$skill" "$staging_root"
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
		PENDING_BACKUP="$backup"
		PENDING_TARGET="$target_dir"
		if ! mv -T -- "$target_dir" "$backup"; then
			PENDING_BACKUP=""
			PENDING_TARGET=""
			die "could not move the existing $skill to a backup at $backup"
		fi
	fi

	if ! mv -T -- "$staged" "$target_dir"; then
		if [[ -n "$backup" && (-e "$backup" || -L "$backup") ]]; then
			mv -T -- "$backup" "$target_dir" ||
				warn "could not restore the backup at $backup"
		fi
		PENDING_BACKUP=""
		PENDING_TARGET=""
		die "could not install $skill atomically"
	fi

	PENDING_BACKUP=""
	PENDING_TARGET=""
	rm -rf -- "$staging_root" || warn "could not remove staging directory: $staging_root"
	STAGING=""
	if [[ -n "$backup" ]]; then
		info "    backup: $backup"
	fi
}

resolve_default_target() {
	case "$DEFAULT_TARGET_MODE" in
	antigravity)
		[[ -n "${HOME:-}" ]] || die "HOME is not set; pass --target DIR"
		TARGET_ROOT="${HOME}/.gemini/config/skills"
		;;
	opencode)
		if [[ -n "${XDG_CONFIG_HOME:-}" ]]; then
			TARGET_ROOT="${XDG_CONFIG_HOME}/opencode/skills"
		else
			[[ -n "${HOME:-}" ]] || die "HOME is not set; pass --target DIR or set XDG_CONFIG_HOME"
			TARGET_ROOT="${HOME}/.config/opencode/skills"
		fi
		;;
	*)
		die "unsupported installer mode: $DEFAULT_TARGET_MODE"
		;;
	esac
}

skills_hub_install_main() {
	: "${HARNESS_NAME:?HARNESS_NAME must be set by the installer wrapper}"
	: "${SCRIPT_USAGE_NAME:?SCRIPT_USAGE_NAME must be set by the installer wrapper}"
	: "${TARGET_HELP:?TARGET_HELP must be set by the installer wrapper}"
	: "${DEFAULT_TARGET_MODE:?DEFAULT_TARGET_MODE must be set by the installer wrapper}"
	: "${RELOAD_HINT:?RELOAD_HINT must be set by the installer wrapper}"
	: "${REPO_ROOT:?REPO_ROOT must be set by the installer wrapper}"
	: "${SKILLS_DIR:?SKILLS_DIR must be set by the installer wrapper}"

	trap cleanup EXIT
	trap 'exit 129' HUP
	trap 'exit 130' INT
	trap 'exit 143' TERM

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
	realpath -m / >/dev/null 2>&1 || die "GNU realpath with -m is required (GNU coreutils)"
	sort -z </dev/null >/dev/null 2>&1 || die "GNU sort with -z is required (GNU coreutils)"

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

	local -a AVAILABLE=()
	local entry=""
	while IFS= read -r -d '' entry; do
		if [[ -d "$entry" && -f "$entry/SKILL.md" ]]; then
			AVAILABLE+=("${entry##*/}")
		fi
	done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -print0 | sort -z)

	if ((${#AVAILABLE[@]} == 0)); then
		die "no skills found in $SKILLS_DIR"
	fi

	local skill=""
	local description=""
	local desc_line=""
	if ((LIST)); then
		if ((VERIFY)); then
			verify_source
		fi
		info "Available skills in $SKILLS_DIR:"
		for skill in "${AVAILABLE[@]}"; do
			description="$(read_description "$SKILLS_DIR/$skill/SKILL.md")"
			info "  $skill"
			if [[ -n "$description" ]]; then
				while IFS= read -r desc_line; do
					info "    $desc_line"
				done <<<"$description"
			fi
		done
		exit 0
	fi

	if ((ALL && ${#REQUESTED[@]} > 0)); then
		die "cannot combine --all with explicit skill names"
	fi

	local tar_help=""
	local mv_help=""
	if [[ "$MODE" == "copy" && "$DRY_RUN" == "0" ]]; then
		command -v tar >/dev/null 2>&1 || die "tar is required for --copy"
		tar_help="$(tar --help 2>&1 || true)"
		if ((VERIFY)); then
			[[ "$tar_help" == *"--strip-components"* && "$tar_help" == *"--no-same-owner"* ]] ||
				die "GNU tar with --strip-components and --no-same-owner is required"
		else
			[[ "$tar_help" == *"--verbatim-files-from"* && "$tar_help" == *"--null"* && "$tar_help" == *"--no-same-owner"* ]] ||
				die "GNU tar with --verbatim-files-from, --null, and --no-same-owner is required"
			find /dev/null -maxdepth 0 -printf '' >/dev/null 2>&1 ||
				die "GNU find with -printf is required (GNU findutils)"
		fi
	fi
	if ((DRY_RUN == 0)); then
		mv_help="$(mv --help 2>&1 || true)"
		[[ "$mv_help" == *"--no-target-directory"* ]] ||
			die "GNU mv with -T is required (GNU coreutils)"
	fi

	if ((TARGET_SET == 0)); then
		resolve_default_target
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

	local HOME_REAL=""
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

	if ((${#REQUESTED[@]} == 0)); then
		ALL=1
	fi

	local -a SELECTED=()
	local -A SEEN_SELECTED=()
	local source_dir=""
	local requested=""
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
			if [[ -z "${SEEN_SELECTED[$requested]+x}" ]]; then
				SEEN_SELECTED["$requested"]=1
				SELECTED+=("$requested")
			fi
		done
	fi

	if ((VERIFY)); then
		verify_source
	fi

	info "${HARNESS_NAME} skill install"
	info "  source: $SKILLS_DIR"
	info "  target: $TARGET_ROOT"
	info "  mode:   $MODE"
	info "  skills: ${SELECTED[*]}"
	if ((DRY_RUN)); then
		info "  dry run: no files will be written"
	fi
	info ""

	# Pre-flight pass: verify all sources, path boundaries, backup directory, and conflicts
	# before creating TARGET_ROOT or installing any skill (prevents partial installs).
	local conflicts=0
	local needs_backup=0
	local -a PLAN_ACTIONS=()
	local -a PLAN_SOURCES=()
	local -a PLAN_TARGETS=()
	local source_real=""
	local target_dir=""

	for skill in "${SELECTED[@]}"; do
		source_dir="$SKILLS_DIR/$skill"
		source_real="$(canonicalize "$source_dir")" ||
			die "could not canonicalize skill source: $source_dir"
		target_dir="$TARGET_ROOT/$skill"

		if [[ -z "$(read_description "$source_dir/SKILL.md")" ]]; then
			warn "$skill has no description in SKILL.md; ${HARNESS_NAME} will not advertise it"
		fi

		case "$target_dir" in
		"$TARGET_ROOT"/*) ;;
		*) die "refusing to write outside target root: $target_dir" ;;
		esac
		[[ "${target_dir##*/}" == "$skill" ]] ||
			die "refusing to write unexpected target: $target_dir"
		if [[ "$target_dir" == "$source_real" || "$target_dir" == "$source_real"/* ||
			"$source_real" == "$target_dir"/* ]]; then
			die "refusing target that overlaps the skill source: $target_dir"
		fi

		if [[ "$MODE" == "link" ]]; then
			check_skill_tree_safe "$source_real" 0
			if ((VERIFY)); then
				check_verified_git_tree_safe "$skill"
			fi
		elif ((VERIFY)); then
			check_verified_git_tree_safe "$skill"
		else
			check_skill_tree_safe "$source_real" 1
		fi

		if [[ -e "$target_dir" || -L "$target_dir" ]]; then
			if [[ "$MODE" == "link" && -L "$target_dir" &&
				"$(readlink -- "$target_dir")" == "$source_real" ]]; then
				info "  = $skill (already linked)"
				PLAN_ACTIONS+=("skip")
			elif ((FORCE == 0)); then
				warn "$skill already exists at $target_dir; use --force to replace it"
				conflicts=$((conflicts + 1))
				PLAN_ACTIONS+=("conflict")
			else
				info "  ~ $skill (replacing existing; backup kept)"
				needs_backup=1
				PLAN_ACTIONS+=("install")
			fi
		else
			info "  + $skill"
			PLAN_ACTIONS+=("install")
		fi
		PLAN_SOURCES+=("$source_real")
		PLAN_TARGETS+=("$target_dir")
	done

	if ((DRY_RUN)); then
		info ""
		info "Dry run complete. Re-run without --dry-run to install."
		exit 0
	fi

	if ((conflicts > 0)); then
		info ""
		warn "$conflicts skill(s) already exist; no changes were written."
		exit 1
	fi

	local backup_root=""
	if ((needs_backup)); then
		backup_root="$TARGET_ROOT/.skills-hub-backups"
		if [[ -L "$backup_root" ]]; then
			die "refusing symlinked backup directory: $backup_root"
		fi
		if [[ -e "$backup_root" && ! -d "$backup_root" ]]; then
			die "backup path is not a directory: $backup_root"
		fi
	fi

	local need_any_write=0
	local action=""
	for action in "${PLAN_ACTIONS[@]}"; do
		if [[ "$action" == "install" ]]; then
			need_any_write=1
			break
		fi
	done
	if ((need_any_write)); then
		mkdir -p -- "$TARGET_ROOT"
	fi

	local i=0
	for i in "${!SELECTED[@]}"; do
		if [[ "${PLAN_ACTIONS[$i]}" == "install" ]]; then
			install_skill "${SELECTED[$i]}" "${PLAN_SOURCES[$i]}" "${PLAN_TARGETS[$i]}"
		fi
	done

	info ""
	info "$RELOAD_HINT"
	info "Installed skills live in: $TARGET_ROOT"
}

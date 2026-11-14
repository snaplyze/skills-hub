.PHONY: help validate lint test install dry-run check

help:
	@printf '%s\n' \
		'make validate  - validate skill metadata, links, and docs' \
		'make lint      - run ruff and markdownlint' \
		'make test      - run deterministic contrast checks' \
		'make install   - install skills into OpenCode (symlink)' \
		'make dry-run   - preview the OpenCode install' \
		'make check     - run everything CI runs'

validate:
	python3 scripts/validate.py

lint:
	ruff check .
	npx --yes markdownlint-cli2@0.24.1 "**/*.md"

test:
	python3 skills/frontend-design/scripts/contrast.py --self-test
	python3 skills/frontend-design/scripts/contrast.py --pairs skills/frontend-design/assets/token-contrast-pairs.json --check --quiet

install:
	./install/opencode.sh

dry-run:
	./install/opencode.sh --dry-run

check: validate lint test
	bash -n install/opencode.sh
	./install/opencode.sh --dry-run --target /tmp/skills-hub-check
	npx --yes csstree-validator skills/frontend-design/assets/tokens.css

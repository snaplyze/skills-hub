PYTHON ?= python3
NPM ?= npm
RUFF ?= ruff
SHELLCHECK ?= shellcheck
MDLINT ?= node_modules/.bin/markdownlint-cli2
CSSTREE ?= node_modules/.bin/csstree-validator
DRY_RUN_ANTIGRAVITY_TARGET ?= /tmp/antigravity/skills-hub-check
DRY_RUN_OPENCODE_TARGET ?= /tmp/opencode/skills-hub-check

.PHONY: help deps validate lint test shellcheck install install-antigravity install-opencode dry-run css workflows links check

help:
	@printf '%s\n' \
		'make deps                - install hash-locked Python and npm development tools' \
		'make validate            - validate skill metadata, links, tokens, and docs' \
		'make lint                - run ruff and markdownlint' \
		'make test                - run the pytest suite (includes contrast checks)' \
		'make shellcheck          - run ShellCheck on the installers' \
		'make install-antigravity - install skills into Antigravity (copy)' \
		'make install-opencode    - install skills into OpenCode (copy)' \
		'make dry-run             - preview both Antigravity and OpenCode installs' \
		'make css                 - parse the frontend-design token CSS' \
		'make workflows           - check GitHub workflow policy' \
		'make links               - audit external links (network; scheduled)' \
		'make check               - run every required check exactly once'

deps:
	$(PYTHON) -m pip install --require-hashes -r requirements-dev.txt
	$(NPM) ci --ignore-scripts --no-audit --no-fund

validate:
	$(PYTHON) scripts/validate.py

lint:
	$(RUFF) check .
	$(MDLINT) "**/*.md" "#node_modules" "#.venv" "#.playwright-cli"

test:
	$(PYTHON) -m pytest -q

shellcheck:
	$(SHELLCHECK) -x install/antigravity.sh install/opencode.sh install/lib.sh

install-antigravity:
	./install/antigravity.sh

install-opencode:
	./install/opencode.sh

install:
	@printf '%s\n' \
		'Choose a target harness installer:' \
		'  make install-antigravity   # install into ~/.gemini/config/skills' \
		'  make install-opencode      # install into $${XDG_CONFIG_HOME:-~/.config}/opencode/skills'
	@exit 2

dry-run:
	./install/antigravity.sh --dry-run --target "$(DRY_RUN_ANTIGRAVITY_TARGET)"
	./install/opencode.sh --dry-run --target "$(DRY_RUN_OPENCODE_TARGET)"

css:
	$(CSSTREE) skills/frontend-design/assets/tokens.css

workflows:
	$(PYTHON) scripts/check_workflows.py --strict

links:
	$(PYTHON) scripts/check_external_links.py

check: validate lint test shellcheck dry-run css workflows

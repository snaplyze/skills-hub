# Сведения о проекте

Назначение: Skills Hub — публичный набор из 11 портируемых навыков для OpenCode (`frontend-design` и 10 workflow-навыков: `orchestration`, `specification`, `implementation-planning`, `autonomous-execution`, `systematic-debugging`, `test-driven-development`, `code-review`, `delivery`, `clean-code`, `skill-authoring`). Пользователи — авторы навыков и разработчики, подключающие их к агентам.

## Команды

- Быстрый узкий сигнал: `python3 scripts/validate.py` (или `make validate`) — frontmatter (OpenCode V2), ссылки и якоря в SKILL/references/docs, reading-set бюджет, установщик, токены и контрастный fixture.
- Тесты поведения: `make test` — pytest: validator/CLI/installer/release/CI-политика/external-links; 64 пары + 27 комбинаций WCAG 2.2 AA (обе темы `light` и `dark`) проверяются в `make validate`.
- Полные локальные проверки: `make check` — validate, Ruff, Markdownlint, pytest, ShellCheck, dry-run установщика, разбор CSS и workflow-политика. `make links` — внешние ссылки по сети отдельно.
- CI-обязательные проверки: `validate`, `Analyze (python)`, `Analyze (actions)`, `dependency-review`, `gitleaks`; CodeQL также обязателен через code-scanning gate; OpenSSF Scorecard — дополнительная.

## Неочевидные соглашения и ловушки

- Навык — это `skills/<id>/SKILL.md`; id только lowercase kebab-case. `description` во frontmatter — основной триггер; до загрузки модель видит также id (имя каталога) и name навыка.
- `SKILL.md` держит рабочий процесс, детали лежат в `references/` и читаются по необходимости. Пути внутри навыка — относительные от каталога навыка.
- Контент навыков и остальные документы репозитория — на английском; этот AGENTS.md и `docs/plan.md` — на русском. Чужие тексты не копировать; канонический реестр источников `frontend-design` — `skills/frontend-design/references/sources.md`, сводный реестр репозитория — `THIRD_PARTY_NOTICES.md`.
- Доступность — WCAG 2.2 AA: 24×24 CSS px минимум, 44×44 px практический таргет, контраст 4.5:1 для текста и 3:1 для крупного текста/UI. Эталон — 64 пары и 27 комбинаций в обеих темах (`skills/frontend-design/assets/token-contrast-pairs.json`).
- `main` защищён: только PR, обязательные проверки, линейная история, запрещены force push и удаление. Защиты и обязательные проверки не обходить.
- Установщик пишет в глобальный каталог навыков OpenCode; в CI выполняется только dry-run. Не устанавливать навыки в проект и не коммитить результат установки.
- Релизы, теги, production, деплой и расходы — только по отдельному поручению владельца. Теги `v*` защищены.
- Секреты и приватные конфиги не попадают в Git, PR, логи, артефакты и удалённые MCP.
- Не добавлять в Git `.ruff_cache/`, `.playwright-cli/`, `node_modules/`, `.env*`; `.env*`, ключи и приватные каталоги агентов покрыты `.gitignore` (`.env.example` разрешён), а workflow `Secret Scan` ищет утечки. Не удалять чужие untracked и ignored файлы.
- Все загружаемые инструкции держать в бюджете ≤32 КиБ на типовой набор; reading-set manifest и проверка находятся в навыке и `scripts/validate.py`. Общие правила агентов не дублировать.

## План

Реестр плана — `docs/plan.md` (owner-facing, на русском; не загружается как инструкции и не входит в бюджет 32 КиБ). Для плановых задач обновлять его; найденное вне объёма — в итоговом отчёте.

## CI

- `CI (проверено, 2026-11-26): hosted (ubuntu-24.04); self-hosted: 0; org: none; reusable workflows: none; обязательные проверки: validate, Analyze (python), Analyze (actions), dependency-review, gitleaks; CodeQL — обязательный code-scanning gate; Scorecard и Link Audit — отдельно.`
- `CI (владелец): по обнаружению; hosted по умолчанию; self-hosted — для подходящих заданий.`

## Оркестрация

- `Оркестрация (проверено, 2026-11-26): встроенные подагенты general/explore (OpenCode V2, experimental.subagent_depth=2); кастомных ролей/плагинов/хуков в проекте нет; проектные skills: frontend-design, orchestration, specification, implementation-planning, autonomous-execution, systematic-debugging, test-driven-development, code-review, delivery, clean-code, skill-authoring; глобальные skills/MCP и правила окружения настраиваются в пользовательской области (~/.config/opencode/), не в репозитории.`

## Доступ

- `Доступ (политика владельца): настраивается исключительно в пользовательской области (~/.config/opencode/); проектных разрешений, приватных конфигов и локальных деталей окружения в репозитории нет.`

## Решения владельца

- CI: по обнаружению; hosted по умолчанию, self-hosted — для подходящих заданий.
- Доступ: только в пользовательской области; в проекте не настраивать.
- Оркестрация: встроенные подагенты без проектных плагинов и хуков; не устанавливать и не менять подагентов в проекте.

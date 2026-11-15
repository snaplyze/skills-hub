# Сведения о проекте

Назначение: Skills Hub — публичный набор портируемых навыков для AI-агентов; первый навык — `frontend-design` для OpenCode. Пользователи — авторы навыков и разработчики, подключающие их к агентам.

## Команды

- Быстрый узкий сигнал: `python3 scripts/validate.py` (или `make validate`) — frontmatter, ссылки и якоря в SKILL/references, reading-set бюджет, установщик, токены и контрастный fixture.
- Тесты поведения: `make test` — pytest: validator/CLI/installer/release/CI-политика; 64 пары WCAG 2.2 AA проверяются в `make validate`.
- Полные локальные проверки: `make check` — validate, Ruff, Markdownlint, pytest, ShellCheck, dry-run установщика, разбор CSS и workflow-политика. `make links` — внешние ссылки по сети отдельно.
- CI-обязательные проверки: `validate`, `Analyze (python)`, `dependency-review`; CodeQL также обязателен через code-scanning gate; OpenSSF Scorecard — дополнительная.

## Неочевидные соглашения и ловушки

- Навык — это `skills/<id>/SKILL.md`; id только lowercase kebab-case. `description` во frontmatter — основной триггер; до загрузки модель видит также id (имя каталога) и name навыка.
- `SKILL.md` держит рабочий процесс, детали лежат в `references/` и читаются по необходимости. Пути внутри навыка — относительные от каталога навыка.
- Контент навыков и остальные документы репозитория — на английском; этот AGENTS.md — на русском. Чужие тексты не копировать; канонический реестр источников навыка — `skills/frontend-design/references/sources.md`, `THIRD_PARTY_NOTICES.md` — указатель уровня репозитория.
- Доступность — WCAG 2.2 AA: 24×24 CSS px минимум, 44×44 px практический таргет, контраст 4.5:1 для текста и 3:1 для крупного текста/UI. Эталон — 64 пары в `skills/frontend-design/assets/token-contrast-pairs.json`.
- `main` защищён: только PR, обязательные проверки, линейная история, запрещены force push и удаление. Защиты и обязательные проверки не обходить.
- Установщик пишет в глобальный каталог навыков OpenCode; в CI выполняется только dry-run. Не устанавливать навыки в проект и не коммитить результат установки.
- Релизы, теги, production, деплой и расходы — только по отдельному поручению владельца. Теги `v*` защищены.
- Секреты и приватные конфиги не попадают в Git, PR, логи, артефакты и удалённые MCP. Чтение секретов разрешено в пользовательской области, но это не разрешает их отправку или публикацию.
- Не добавлять в Git `.ruff_cache/`, `.playwright-cli/`, `node_modules/`, `.env*`; `.env*`, ключи и приватные каталоги агентов покрыты `.gitignore` (`.env.example` разрешён), а workflow `Secret Scan` ищет утечки. Не удалять чужие untracked и ignored файлы.
- Все загружаемые инструкции держать в бюджете ≤32 КиБ на типовой набор; reading-set manifest и проверка находятся в навыке и `scripts/validate.py`. Общие правила агентов не дублировать.

## План

Реестр плана — `docs/plan.md` (owner-facing, на русском; не загружается как инструкции и не входит в бюджет 32 КиБ). Для плановых задач обновлять его; найденное вне объёма — в итоговом отчёте.

## CI

- `CI (обнаружено, 2026-11-15): hosted (ubuntu-24.04); self-hosted: 0; org: none; reusable workflows: none; обязательные проверки: validate, Analyze (python), dependency-review; CodeQL — обязательный code-scanning gate; make check + Secret Scan, Link Audit — отдельно.`
- `CI (владелец): по обнаружению; hosted по умолчанию; self-hosted — для подходящих заданий.`

## Оркестрация

- `Оркестрация (обнаружено, 2026-11-14): встроенные подагенты general/explore и skill opencode; subagent_depth=2; кастомных ролей нет; skills: frontend-design, orchestration, specification, implementation-planning, autonomous-execution, systematic-debugging, test-driven-development, code-review, delivery, clean-code, skill-authoring (проект); playwright-cli, report (глобально); MCP: context7, gh_grep (глобально); плагинов нет; managed /etc/opencode отсутствует; глобальные skills/MCP доступны только пользователю.`

## Доступ

- `Доступ (обнаружено, 2026-11-14): full, кроме exa_agent_run (deny), глобальная пользовательская область; секреты: чтение не ограничено (permissions allow, *.env allow).`
- `Доступ (владелец): полный неинтерактивный; включается только обёрткой opencode-full (--auto), не в проекте.`

## Решения владельца

- CI: по обнаружению; hosted по умолчанию, self-hosted — для подходящих заданий.
- Доступ: полный неинтерактивный, только через пользовательскую обёртку; в проекте не настраивать.
- Оркестрация: только проверка; не устанавливать и не менять подагентов.

# План

Трекер: https://github.com/snaplyze/skills-hub/issues; сверено 2026-11-25T21:43:20Z; этапы 01–09; аудит 2026-11-15 (#41–#48): все DONE; этап #8 (#58–#61, #63): все DONE; закрытые также #14–#20, #27–#35, #38, #54; документальная задача аудита 2026-11-26: #68; веха «Аудит 2026-11-26» (#9): AUD-30–AUD-43 (#69–#82) OPEN. Реестр — этот файл; план owner-facing, на русском, не загружается как инструкции агентов.

## Документы и стартовый контекст

| Документ | Роль | Строк / байт |
|---|---|---|
| `docs/plan.md` | реестр плана | 591 / 119 114 (требует `AUD-41`) |
| `AGENTS.md` | project info и стартовый контекст | 47 / 6 758 |
| `README.md` | вход и установка | 340 / 18 587 |
| `docs/opencode-orchestration.md` | архитектура orchestration | 79 / 3 817 |
| `docs/release-process.md` | release gate и owner setup | 266 / 12 236 |
| `docs/repository-settings.md` | settings evidence | 75 / 4 942 |
| `docs/release-signing/` | публичный trust и ротация | 44 / 1 965 |
| `CONTRIBUTING.md`, `GOVERNANCE.md`, `SECURITY.md`, `CHANGELOG.md` | правила и история | 408 / 16 970 |
| `THIRD_PARTY_NOTICES.md` | атрибуция | 52 / 3 409 |
| `docs/plans/2026-11-16-skill-suite-v2.md` | детальный план этапа 08 | 281 / 10 726 |

Документы этапа 09 (аудит 2026-11-26, #68): `docs/plan.md`, `docs/release-process.md`, `CONTRIBUTING.md`, `THIRD_PARTY_NOTICES.md`, `README.md`, `SECURITY.md`, `docs/release-signing/README.md`, `docs/repository-settings.md`; продукт, код, тесты, CI, `AGENTS.md` и `CHANGELOG.md` не менялись. План не входит в бюджет инструкций 32 KiB.

## Этапы

| # | Веха | Задачи |
|---|---|---|
| 01 | Release, installer, validation (веха #1, closed) | AUD-01 #14, AUD-02 #15, AUD-03 #16 |
| 02 | CI, secrets, content (веха #2, closed) | AUD-04 #17, AUD-05 #18, AUD-06 #19 |
| 03 | Protections (веха #3, closed) | AUD-07 #20 |
| 04 | Agent workflow skills (веха #4, closed) | SKL-01 #27, SKL-02 #28, SKL-03 #29 |
| 05 | Quality and delivery skills (веха #5, closed) | SKL-04 #30, SKL-05 #31, SKL-06 #32, SKL-07 #33, SKL-08 #34, SKL-09 #35 |
| 06 | Native orchestration (веха #6, closed) | ORC-01 #38 |
| 07 | Audit 2026-11-15 (веха #7, closed) | AUD-22 #41 DONE; AUD-23 #42 DONE; AUD-24 #43 DONE; AUD-25 #44 DONE; AUD-26 #45 DONE; AUD-27 #46 DONE; AUD-28 #47 DONE; AUD-29 #48 DONE |
| 08 | Skill suite v2 (веха #8, closed) | SKL2-01 #58 DONE, SKL2-02 #59 DONE, SKL2-03 #60 DONE, SKL2-04 #61 DONE (+ closeout #63 DONE) |
| 09 | Аудит 2026-11-26 (веха #9, open) | AUD-30 #69, AUD-31 #70, AUD-32 #71, AUD-33 #72, AUD-34 #73, AUD-35 #74, AUD-36 #75, AUD-37 #76, AUD-38 #77, AUD-39 #78, AUD-40 #79, AUD-41 #80, AUD-42 #81, AUD-43 #82 (все OPEN) |

Порядок этапов: 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09. Очередь навыков: SKL-01 → SKL-02 → SKL-05 → SKL-03/SKL-04/SKL-08 → SKL-06 → SKL-07 → SKL-09. Исполнение не начинается до принятого spec/plan; review-gate обязателен на каждой задаче.

## Аудит 2026-11-26

- **Дата и коммит:** `2026-11-26` (сверка трекера `2026-11-25T21:43:20Z`), база `5f0a620` (`main`).
- **Видимость репозитория и трекера:** публичный (`snaplyze/skills-hub`, Issues открыты). По правилу 14 детали неустранённых уязвимостей в публичный план/трекер/PR не пишутся; удалённо эксплуатируемых неустранённых уязвимостей в ходе аудита не выявлено.
- **Охват:** все 7 областей (архитектура, безопасность, данные, производительность, тесты, сборка и доставка, документация) + сверка с актуальным **OpenCode V2** (`opencode v2.4.1`, `https://opencode.ai/docs/`) и всеми **11 upstream-репозиториями** навыков (`THIRD_PARTY_NOTICES.md`, `skills/frontend-design/references/sources.md`).
- **Контекст продукта:** назначение — портируемые навыки AI-агентов (11 навыков для OpenCode, без плагинов/хуков/скрытых каталогов); пользователи — авторы навыков и разработчики; требования — WCAG 2.2 AA (64 пары + 26 комбинаций), бюджет чтения ≤32 KiB, подписанные immutable релизы, обязательные проверки CI; команды — `make validate`, `make test`, `make check`, `make links`, `install/opencode.sh`; ключевые сценарии — discovery/загрузка навыков в OpenCode V2, оркестрация и выполнение планов, валидация, установка, релизный гейт.
- **Проверка продукта в снимке** (`/tmp/opencode/skills-hub-audit-2026-11-26`, `git archive HEAD`, без изменений продукта): `validate` PASS (0.335 s, 11 навыков), `ruff` PASS (0.025 s), `markdownlint` PASS (0.866 s, 39 файлов), `shellcheck` PASS (0.227 s), `dry-run` PASS (0.068 s), `css` PASS (0.129 s), `workflows --strict` PASS (0.058 s, 7 файлов), `check_external_links.py` PASS (32.637 s, 53/53 ok), `pytest` в git-checkout PASS (21.63 s, 202 теста), `pytest` в не-git снимке FAIL (`test_current_head_archive_contains_all_skills` падает, 2 теста `test_release_signature.py` skip). Продукт **проверен** в снимке, но не изменялся.

### Статус областей (Аудит 2026-11-26)

| Область | Статус | Что пройдено / ограничения охвата |
|---|---|---|
| Архитектура | **проверено** | Полный разбор `scripts/`, `install/opencode.sh`, всех 11 навыков, дублей проверок (шаг 5), OpenCode V2 (`opencode.ai/docs/` + `opencode debug agents --standalone`) и 11 upstream-репозиториев. |
| Безопасность | **частично** | Проверены 7 workflows, живые API-настройки GitHub (rulesets, Actions, alerts, Scorecard), `install/opencode.sh`, `validate.py`, `check_workflows.py`, `release_*.py`, `check_external_links.py`. Не проверялось: контролируемый fork PR, live dispatch `release.yml`, destructive install, юридическая экспертиза `sickn33`. |
| Данные | **проверено** | Сквозной путь YAML frontmatter, Markdown links/anchors, `reading-sets.json`, `tokens.css`, `token-contrast-pairs.json`, `CHANGELOG.md`, JSONL check-runs. |
| Производительность | **частично** | Замерены в снимке продукт (размеры 11 навыков и 10 reading sets, `contrast.py` 64–50 000 пар, `opencode.sh` 11–61 навыков), валидация (`cProfile` и пофазно `validate.py`, `check_external_links.py` `rglob` vs `os.walk` и serial vs 8 воркеров) и тесты (`copy_repo` с/без `node_modules`, per-file `pytest`, `check_workflows` 21×). Не проверялось: реальный токенайзер вместо байт, воспроизведение per-step timing на новом hosted-прогоне (взяты фактические логи недавних прогонов). |
| Тесты | **проверено** | Аудит всех 12 тестовых модулей (132 функции / 202 кейса), дубликатов, хрупкости, пробелов покрытия, поведения в не-git снимке. |
| Сборка и доставка | **частично** | Проверены `Makefile`, lockfiles (`requirements-dev.*`, `package-lock.json`, `npm audit`), 7 workflows, открытые Dependabot PR #66/#67, `v1.2.0..HEAD` и живые релизные настройки. Не проверялось: новый `workflow_dispatch` релиза и установка на macOS/BSD. |
| Документация | **проверено** | Построчная сверка всех 18 документов и шаблонов с кодом, `wc -l -c` и живым GitHub API; аудит гигиены `docs/plan.md`. |

### Различение статусов и прямые документальные правки

- **Описание исправлено** в PR аудита (#68, поведение кода подтверждено как задуманное; продукт/код/тесты/CI/YAML/`AGENTS.md`/`CHANGELOG.md` не менялись):
  - `docs/release-process.md`: добавлены обязательный шаг ручного `workflow_dispatch` и явная команда `verify-tag` с `allowed_signers` в чеклист; добавлено право `actions: read`; исправлен порядок проверок (`signature → ancestry → check-runs → release_notes.py`); уточнены формулировки про trust source и `Release` workflow.
  - `CONTRIBUTING.md`: выровнены отдельные команды проверок с `Makefile` (`markdownlint-cli2`, `csstree-validator`, `/tmp/opencode/skills-hub-check`, `--strict`); уточнено разделение реестров атрибуции (`sources.md` и `THIRD_PARTY_NOTICES.md`).
  - `THIRD_PARTY_NOTICES.md`: зафиксирована двойная роль файла (указатель для `frontend-design` + канонический реестр для 10 workflow-навыков), убрана ссылка `or docs/plan.md`, обновлены подтверждённые лицензии (`anthropics/skills/skills/skill-creator` Apache-2.0, исключение импортированных навыков в `sickn33/agentic-awesome-skills`).
  - `README.md`: добавлены `package-lock.json` и `docs/release-signing/` в дерево; уточнены `pinned Python/npm tools`, правила тегов `v*`, исключение `ossf/scorecard-action@*`, множественное число для навыков и описание атрибуции.
  - `SECURITY.md`: добавлено исключение `ossf/scorecard-action@*` в описание allowlist Actions.
  - `docs/release-signing/README.md`: уточнён шаг 5 ротации (`test_release_signature.py` автоматически берёт старший `v*` тег; старые теги проверять явно через `verify-tag`).
  - `docs/repository-settings.md`: обновлена дата сверки на `2026-11-26`, уточнено `release workflow` перед списком гейтов и добавлен `v1.1.0` к подписанным immutable релизам.
- **Учтено** без правки файла (по границам аудита): расхождения в `AGENTS.md` (`AUD-43` + секция «Владельцу»), историческое умолчание о SARIF в `CHANGELOG.md` (`v1.1.0`, не переписывается задним числом), `.github/ISSUE_TEMPLATE/bug_report.yml` (`AUD-43`), перекомпоновка `docs/plan.md` («Порядок в плане», `AUD-41`).
- **Рекомендуемая очередь исправлений:** `AUD-30` → `AUD-31` → `AUD-33` → `AUD-36` → `AUD-34` → `AUD-35` → `AUD-32` → `AUD-37` → `AUD-38` → `AUD-39` → `AUD-40` → `AUD-41` → `AUD-43` → `AUD-42` (владелец).

### AUD-30 — Code Scanning alert #13 (`pip==26.3`) and `check_workflows.py` policy bypasses

- `OPEN` · **Аудит 2026-11-26** · тип: `ci/security/duplication` · приоритет: **P1 — высокий ущерб** (единственный открытый Code Scanning alert уровня `error` и подтверждённые обходы главного CI-гейта безопасности) · уверенность: **высокая** · трекер: [#69](https://github.com/snaplyze/skills-hub/issues/69) (веха #9) · deps: none.
- **Результат / границы:** убрать unhashed `pip==26.3`, закрыть обходы политики в `scripts/check_workflows.py`, устранить дублирование проверки workflows в `scripts/validate.py`, сузить `permissions` в `scorecard.yml`. Продуктовые навыки и настройки аккаунта не меняются.
- **Доказательство:**
  - Живой Code Scanning API `alerts/13` (`state: open`, `rule: Scorecard/PinnedDependenciesID`, `severity: error`, `security_severity: medium`) на `.github/workflows/ci.yml:48` (`python -m pip install --upgrade "pip==26.3"` без `--require-hashes`; в прогоне `43946282578` это no-op — `setup-python@v7.1.0` уже ставит `pip 26.3`; нарушает паритет с `Makefile:25-27`, снижает Scorecard `Pinned-Dependencies` с 10 до 8).
  - `scripts/check_workflows.py:124-129` (`find`): берёт первый дубликат ключа YAML, тогда как YAML/Actions применяют последний (обход `permissions: write-all`, `on: pull_request_target`, неподписанного `uses`, `persist-credentials: true`).
  - `scripts/check_workflows.py:320` (`check_workflow`): `yaml.compose` не отклоняет merge-ключи `<<: *alias`.
  - `scripts/check_workflows.py:164-165` (`check_checkout_credentials`): регистрозависимое `action != "actions/checkout"` пропускает `Actions/Checkout@<sha>`.
  - `scripts/check_workflows.py:190-200, 242-248, 265, 300-314`: `permissions: [write-all]` (`SequenceNode`), `on: []`, `jobs: {}`, `timeout-minutes: 1_0` и соседство `jobs.<id>.uses` со `steps:` проходят с 0 ошибок; `read-all` разрешён; нет проверки `${{ ... }}` в `run:`, `runs-on` (против `self-hosted`/`ubuntu-latest`) и write-прав в `pull_request`-workflows.
  - `.github/workflows/scorecard.yml:12`: `permissions: read-all` на уровне workflow вместо `{}` / `contents: read`.
  - *Дублирование (шаг 5):* `scripts/validate.py:878-897` (`check_yaml`) повторно парсит `.github/workflows/*.{yml,yaml}` через `yaml.safe_load` (YAML 1.1 принимает `true:` как `on:`). Инвариант: все workflows — валидные YAML-mapping с `name`/`on`/`jobs` и политикой безопасности; граница доверия: один локальный/CI процесс на неизменном git-дереве; гарантия уже в `check_workflows.py` (кроме проверки `"name"`).
- **Влияние:** открытый security-alert в Code Scanning, риск незамеченного обхода CI-политики в PR, двойной разбор workflows с расхождением YAML 1.1/AST.
- **Решение:** удалить строку `.github/workflows/ci.yml:48`; в `scripts/check_workflows.py` запретить дублирующиеся ключи и `<<`, нормализовать регистр `actions/checkout`, строго проверять типы узлов `permissions`/`on`/`jobs`/`timeout-minutes`, запретить `read-all`, добавить проверки `"name"`, `${{ }}` в `run:`, `runs-on` и write-прав на `pull_request`; удалить ветку `if path.parent.name == "workflows":` (`scripts/validate.py:887-896`) и пропускать `workflows/` в `check_yaml`; в `scorecard.yml` заменить `permissions: read-all` на `permissions: {}` + `if: always()` на загрузку SARIF/артефакта + guard на default branch. Трудоёмкость: 1.5–2 ч; риски: низкие, проверить прохождение на всех 7 текущих workflows.
- **Приёмка:** негативные тесты в `tests/test_workflows.py` ловят каждый из обходов; `make check` PASS; после слияния на `main` очередной прогон Scorecard закрывает alert #13 (`Pinned-Dependencies` 10/10).
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — взять в работу первым; неудачные попытки: нет.

### AUD-31 — Support OpenCode V2 frontmatter fields (`metadata`, `disable-model-invocation`) and strict YAML parsing

- `OPEN` · **Аудит 2026-11-26** · тип: `compatibility/validator` · приоритет: **P1 — высокий ущерб** (валидатор ломает официальные поля OpenCode V2 и противоречит собственному навыку `skill-authoring`) · уверенность: **высокая** · трекер: [#70](https://github.com/snaplyze/skills-hub/issues/70) (веха #9) · deps: none.
- **Результат / границы:** `scripts/validate.py` принимает и типизированно валидирует официальные поля frontmatter OpenCode V2, отклоняя дубликаты YAML-ключей; `skill-authoring`, `README.md`, `CONTRIBUTING.md` согласованы.
- **Доказательство:**
  - Первоисточник OpenCode V2 (`https://opencode.ai/docs/skills/#frontmatter`): официальные поля `name`, `description`, `license`, `compatibility`, `metadata` (включая `metadata.opencode/autoinvoke: false`) и `disable-model-invocation: true`.
  - `scripts/validate.py:42, 443-451`: `ALLOWED_FRONTMATTER_KEYS` не содержит `metadata` и `disable-model-invocation`, при этом не проверяет тип `compatibility` (`null`/`[]` проходят).
  - `skills/skill-authoring/SKILL.md:101`: прямо предписывает `Version a material behavior change in the skill metadata or changelog`, что падает на `make validate`.
  - `scripts/validate.py:227-237` (`parse_frontmatter`): `yaml.safe_load` молча берёт последний дубликат ключа (а `install/opencode.sh:177` берёт первый) и падает на CRLF / EOF без завершающего `\n`.
- **Влияние:** авторы навыков не могут использовать версионирование в `metadata` и ручной opt-out OpenCode V2 (`metadata.opencode/autoinvoke: false` / `disable-model-invocation: true`), а валидатор допускает невалидный тип `compatibility` и скрытые дубликаты ключей.
- **Решение:** расширить `ALLOWED_FRONTMATTER_KEYS` до `{"name", "description", "license", "compatibility", "metadata", "disable-model-invocation"}`; валидировать `compatibility` (непустая строка), `disable-model-invocation` (`bool`), `metadata` (`dict`, где `opencode/autoinvoke` при наличии — `bool`, плюс проверка конфликта обоих флагов); заменить `yaml.safe_load` в `parse_frontmatter` на строгий `SafeLoader` с запретом дубликатов ключей и поддержкой закрывающего `---` в EOF; обновить `skills/skill-authoring/SKILL.md:30-38`, `README.md:316`, `CONTRIBUTING.md:73`. Трудоёмкость: 1–1.5 ч; риски: низкие (все 11 текущих навыков остаются валидными).
- **Приёмка:** позитивные и негативные тесты (`metadata`, `disable-model-invocation`, `compatibility: null`, дубликат ключа, `unexpected: true`) в `tests/test_validation.py` PASS; `make check` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — реализовать схему frontmatter и тесты; неудачные попытки: нет.

### AUD-32 — Align orchestration, planning, execution, delivery skills and `docs/opencode-orchestration.md` with OpenCode V2

- `OPEN` · **Аудит 2026-11-26** · тип: `compatibility/architecture/skill-content` · приоритет: **P1 — высокий ущерб** (живые противоречия с правами встроенных агентов `plan`/`explore`/`general` и асинхронной моделью `subagent` в OpenCode v2.4.1) · уверенность: **высокая** · трекер: [#71](https://github.com/snaplyze/skills-hub/issues/71) (веха #9) · deps: none.
- **Результат / границы:** навыки `implementation-planning`, `specification`, `orchestration`, `autonomous-execution`, `code-review`, `delivery` и `docs/opencode-orchestration.md` точно отражают асинхронную модель, права и нативные worktree OpenCode V2 без плагинов/хуков и с сохранением переносимости.
- **Доказательство:**
  - Первоисточники OpenCode V2 (`https://opencode.ai/docs/tools/#subagent`, `/docs/agents/`, `/docs/permissions/#defaults`, `/docs/tools/#worktrees`) + прямой запуск `opencode debug agents --standalone` на `opencode v2.4.1`:
    - `plan` имеет `edit: * deny`, разрешая только `~/.opencode/plan/*` → `skills/implementation-planning/SKILL.md:40` (`docs/plans/...`) и `skills/specification/SKILL.md:27` (`docs/specs/...`) упираются в permission deny без read-only fallback.
    - `subagent` всегда работает в фоне, возвращает `sessionID`, уведомляет через `<background-result>`, поддерживает follow-up по `sessionID`, в TUI есть переключение и отмена (`ctrl+d`), в V2 есть нативные `automation` и `model#variant`.
    - `explore` запрещает `skill` и `question`, но **разрешает `shell` и `external_directory`**; `general` запрещает `question` и `subagent`, разрешает `external_directory` по умолчанию.
    - Нативные `worktree_create` / `session.move` (вступает в силу на следующей безопасной границе) / `worktree_remove` (без `force` без подтверждения).
  - Upstream-уроки: `snaplyze/claude-orchestration` v1.7.0 (`1c71ec2e0df0`, отказ от `maxTurns` в пользу brief-bounded + чистый partial handoff), `alvinunreal/oh-my-opencode-slim` v3.0.6–3.0.8+ (`#1631`, `a052f07a990c`, запрет `question` подагентам и прямой multimodal read), `obra/superpowers` v7.0.2 (`22f0b463e7a5`, CWD-безопасный `git worktree remove` из корня репо + ветка detached HEAD).
  - Противоречия в репо: `docs/opencode-orchestration.md:15, 25, 68-70`; `skills/orchestration/SKILL.md:14, 46, 58, 69`; `skills/autonomous-execution/SKILL.md:72, 76, 82`; `skills/code-review/SKILL.md:28`; `skills/delivery/SKILL.md:42-51`.
- **Влияние:** зависание в polling/sleep циклах, отказ при записи плана в `plan`-режиме, сбои при передаче skill в `explore` или ожидании `question` от подагента, несанкционированные правки за пределами репо при `external_directory: allow`, поломка shell при удалении текущего worktree и неточная документация оркестрации.
- **Решение:**
  1. Добавить read-only/plan-mode fallback в `implementation-planning/SKILL.md:40` и `specification/SKILL.md:27` (вывести документ с целевым путём `docs/plans/...` / `docs/specs/...`, не обходить запрет через `shell`, передать на сохранение пишущему агенту).
  2. Добавить в `orchestration/SKILL.md` и `autonomous-execution/SKILL.md` компактный асинхронный протокол (yield без sleep/poll; `sessionID` для follow-up vs свежий child для независимого ревью; самодостаточный бриф для `explore` без загрузки skills и с запретом мутирующего `shell`; возврат вопросов родителю вместо `question`; явные границы репо/worktree; brief-bounded без turn caps + partial handoff; прямой multimodal read).
  3. Обновить worktree-секции `autonomous-execution/SKILL.md:72` и `delivery/SKILL.md:50` (шаг `session.move` отдельно до команд в целевом каталоге, `cd` в корень репо до `git worktree remove`, без `--force` без подтверждения, опции для detached HEAD).
  4. Актуализировать `docs/opencode-orchestration.md` (разделить runtime V2 и границы навыка, уточнить права `explore`/`external_directory` и опциональный локальный `.opencode/agents/reviewer.md`).
  Трудоёмкость: 2–3 ч; риски: низкие — сохранить контракты `tests/test_skill_suite.py` и отсутствие упоминаний `opencode.json`/плагинов в `SKILL.md`.
- **Приёмка:** все затронутые `SKILL.md` ≤32 KiB; `tests/test_skill_suite.py` и `make check` PASS; `docs/opencode-orchestration.md` соответствует фактам `opencode v2.4.1`.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — обновить навыки и `docs/opencode-orchestration.md`; неудачные попытки: нет.

### AUD-33 — Harden `scripts/validate.py` path containment, link/GFM parsing, `docs/**` recursion, and generic reading-sets

- `OPEN` · **Аудит 2026-11-26** · тип: `security/validator/architecture` · приоритет: **P1 — высокий ущерб** (пробелы изоляции путей, пропуск битых ссылок в бейджах и `docs/**`, жёсткий блок на добавление `references/` во второй навык) · уверенность: **высокая** · трекер: [#72](https://github.com/snaplyze/skills-hub/issues/72) (веха #9) · deps: AUD-31.
- **Результат / границы:** `scripts/validate.py` строго изолирует пути внутри репо и внутри `skills/<id>/`, проверяет вложенные image-links и рекурсивно `docs/**/*.md`, снимает жёсткую привязку `new-page` для сторонних навыков и упрощает адаптер `reading-sets.json`.
- **Доказательство:**
  - `scripts/validate.py:201-210`: `is_relative_to(ROOT)` проверяется только для `/...`, но не для относительных ссылок (`../../../../etc/hosts`); ссылки из `skills/<id>/` на `/README.md` или `../other-skill/SKILL.md` проходят (даже закреплено в `tests/test_validation.py:114`), но ломаются после установки навыка.
  - `scripts/validate.py:350-356, 395-398`: `check_reading_sets` не запрещает абсолютные пути (`/etc/hosts`) и не проверяет `is_relative_to(skill_dir)`.
  - `scripts/validate.py:414-415`: требует сет `new-page` для каждого навыка с `references/*.md`/`assets/*.md`, блокируя добавление `references/` в 10 workflow-навыков; при этом `reading-sets.json` поля `budget_bytes`/`limit_bytes` игнорируются, а `reading_set_entries()` (`lines 240-288`) содержит 49 строк неиспользуемого адаптера 10+ недокументированных форматов.
  - `scripts/validate.py:56-62, 173-180`: `INLINE_LINK_RE` отбрасывает вложенные `[![...](img)](target)` (в `README.md:3-8` пропущены все 6 внешних целей включая `LICENSE` на `:7`).
  - `scripts/validate.py:867-868`: `(ROOT / "docs").glob("*.md")` не рекурсивен — пропускает `docs/plans/*` и `docs/release-signing/README.md`.
  - `scripts/validate.py:36, 46, 50-51, 68-77, 88-161, 378, 462-468`: не отклоняются симлинки в `skills/`; `LOCAL_REF_RE` проверяет только `SKILL.md` и допускает `..`; роутинг проверяет `candidate.name` вместо точного пути; битые неиспользуемые `[dead]: missing.md` не проверяются; `mask_html_comments` идёт до `mask_inline_code`; нестрогие CommonMark-правила fence и расхождение `slug()` с GFM (`_`, `--`, ведущие/конечные `-`, коллизия `foo-1`).
- **Влияние:** битые ссылки в бейджах и вложенных `docs/`, непереносимые ссылки внутри навыков и обходы путей проходят CI; нельзя добавить `references/` ни к одному новому навыку без фиктивного сета `new-page`.
- **Решение:**
  1. Запретить выход за `ROOT` для всех локальных ссылок, и выход за `skill_dir` (включая `/...` и `..`) для файлов внутри `skills/` и `reading-sets.json` (убрать fallback `ROOT / relative` на `:352-353`); запретить симлинки внутри `skills/`.
  2. Ограничить требование `new-page` навыком `frontend-design`; для остальных проверять общий контракт (каждый сет включает `SKILL.md`, `SKILL.md` не в `excluded`, `1 <= limit_bytes <= 32768`); упростить `reading_set_entries()` до документированной схемы; добавить опциональный порог/инфо по суммарным байтам frontmatter-описаний (сейчас 3 685 B) и описать `reading-sets.json` в `skills/skill-authoring/SKILL.md`.
  3. Поддержать вложенные `[![...](...)](...)`, перейти на `docs.rglob("*.md")`, проверять все `definitions` и `LOCAL_REF_RE` по всем `.md` навыка, точный `routing_path`, единый CommonMark fence/inline-code/GFM-slug парсер.
  Трудоёмкость: 2.5–3.5 ч; риски: низкие (обновить `tests/test_validation.py:114` для `/README.md` на root doc вместо skill).
- **Приёмка:** негативные тесты на traversal, вложенные бейджи, `docs/sub/broken.md`, симлинк в `skills/`, 2-й навык с `references/` без `new-page`, невалидный `limit_bytes` и GFM-якоря PASS; `make check` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — исправить границы путей и парсер в `scripts/validate.py`; неудачные попытки: нет.

### AUD-34 — Fix `install/opencode.sh` YAML parser, symlink/`--verify` hygiene, reload hint, CLI edge cases, and copy scaling

- `OPEN` · **Аудит 2026-11-26** · тип: `security/installer/performance` · приоритет: **P1 — высокий ущерб** (живой дефект вывода `--list`, обход `--verify` через `.gitignore`d секреты и внутренние симлинки) · уверенность: **высокая** · трекер: [#73](https://github.com/snaplyze/skills-hub/issues/73) (веха #9) · deps: AUD-31.
- **Результат / границы:** безопасный, быстрый и консистентный установщик `install/opencode.sh` с единой семантикой YAML, защитой симлинков/секретов, корректной подсказкой reload для OpenCode V2 и полным тестовым покрытием.
- **Доказательство:**
  - Живой прогон `./install/opencode.sh --list` в снимке: `read_description()` (`install/opencode.sh:128-184`) печатает сырые кавычки вокруг описаний `frontend-design` и `test-driven-development`; ломает `description: ""`, next-line/multiline scalars, block scalars с комментариями/отступами и берёт первый дубликат ключа (расхождение с `validate.py`).
  - `install/opencode.sh:195-196`: `copy_skill_tree()` копирует внутренние симлинки дословно (`ln -s "$(readlink ...)"`) без проверки containment внутри `$source_dir`.
  - `install/opencode.sh:225, 205-210`: `verify_source()` не передаёт `--ignored`, а `copy_skill_tree()` исключает лишь 9 кэш-паттернов → `.gitignore`d секреты (`.env`, `*.key`, `*.pem`, `credentials*`, `.opencode/`) в `skills/` проходят `--verify` и копируются в `~/.config/opencode/skills/`.
  - `install/opencode.sh:542` и `README.md:146`: «Start a new OpenCode session or run `/reload`» не отражает OpenCode V2 (авто-reload + `opencode reload` CLI / TUI `Reload configuration` / `/reload`, без требования перезапускать сессию).
  - `install/opencode.sh:87-92, 214-250, 296-306, 358, 360-471`: `command -v realpath` проходит на macOS/BSD без `-m` (`mv -T`/`sort -z` не проверяются); `--list` падает при пустом `HOME` и молча игнорирует `--verify`; `--all` игнорирует позиционные аргументы; дублирующиеся аргументы падают/делают лишний бэкап; multi-tag без `--sort=-v:refname`; `cleanup()` не восстанавливает `$target_dir` при `SIGINT`/`SIGTERM` между двумя `mv -T`; замер B-03: per-file `cp`/`mkdir` растёт линейно (**285 ms** на 11/39 → **1.72 s** на 31/459 → **3.89 s** на 61/1 089).
- **Влияние:** порча вывода `--list`, риск копирования `.gitignore`d секретов или убегающих симлинков в глобальные навыки, неожиданное поведение CLI-флагов, потеря целевого каталога при прерывании, O(files) замедление при росте каталога.
- **Решение:** исправить `read_description()` (усилить Bash-парсер или использовать `python3`+PyYAML с Bash-fallback); запретить внутренние симлинки в `copy_skill_tree()`; при `--verify` проверять `git ls-files --others --ignored --exclude-standard -- skills/` (или копировать из `git archive HEAD`) и расширить исключения `copy_skill_tree()` секретными паттернами из `.gitignore`; заменить per-file `cp` на потоковый `tar` (проверив сохранение newline-имён); проверять `realpath -m`/`mv -T`/`sort -z` и `command -v git`; упорядочить `--list`/`--verify`/`--all`/дедупликацию/pre-flight проверку конфликтов/signal-restore бэкапа; обновить сообщение о reload в `opencode.sh:542` и `README.md:146`; закрыть пробелы `tests/test_installer.py` (default `XDG_CONFIG_HOME`, idempotent `--link`, quoted/`|` descriptions, backup symlink, invalid `--ref`, duplicate args). Трудоёмкость: 3–4 ч; риски: средние (сохранить переносимость и все 21 существующих тестов установщика).
- **Приёмка:** `./install/opencode.sh --list` печатает все 11 описаний без лишних кавычек; внутренний симлинк и `.env` в `skills/` отклоняются; замер B-03 показывает ускорение на 61 навыке; `shellcheck` и расширенный `tests/test_installer.py` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — исправить парсер, проверки безопасности и CLI-логику `install/opencode.sh`; неудачные попытки: нет.

### AUD-35 — Harden release gate (`release.yml`, `release_checks.py`, `release_notes.py`) and attach Sigstore asset

- `OPEN` · **Аудит 2026-11-26** · тип: `security/release` · приоритет: **P1 — высокий ущерб** (релизный гейт — самый привилегированный workflow репозитория; уязвимость к check-run shadowing, запуск скрипта из tag-checkout и Scorecard `Signed-Releases: 0/10`) · уверенность: **высокая** · трекер: [#74](https://github.com/snaplyze/skills-hub/issues/74) (веха #9) · deps: AUD-30.
- **Результат / границы:** отказоустойчивый релизный гейт без shadowing/зависаний, проверяющий синхронность `allowed_signers`, выполняющий скрипты из `gate/` (`main`) и публикующий Sigstore-артефакт в релизе. Настройки ruleset #27259237 меняет только владелец.
- **Доказательство:**
  - `scripts/release_checks.py:27-72`: выбирает `max(id)` ДО фильтрации по `head_sha`/`app.slug`/workflow path (посторонний check-run с тем же именем перебивает легитимный); не делает `continue` после ошибки `head_sha`/`app`; `gh_workflow_path` без `timeout`, глотает `stderr`, не проверяет `.head_sha == commit` и хост/репо в `details_url`; падает с traceback на `id: null` или битом JSON; в `tests/test_release_checks.py` только 3 теста.
  - `.github/workflows/release.yml:65-141`: вызывает `scripts/release_notes.py` из tag-checkout (`:137`), а не `gate/scripts/release_notes.py`; проверяет SemVer уже после `checkout`/`git verify-tag` и без `--`; не сверяет `RELEASE_TAG_ALLOWED_SIGNERS` с `gate/docs/release-signing/allowed_signers`.
  - `scripts/release_notes.py:37-40, 72-120, 173`: 3-символьный `FENCE_RE` ломается на 4-backtick блоках; `REFERENCE_RE` обрывает заметки на сносках `[^1]:`; дублирует сканер fence дважды; неиспользуемый флаг `--output`.
  - Scorecard (2026-11-23, run `45163327566`): `Signed-Releases: 0/10`, так как Sigstore bundle от `actions/attest-build-provenance` не загружается как release asset рядом с `SHA256SUMS`.
  - `gitleaks` (`Secret Scan`, ~6 s на каждом PR/push) отсутствует в `EXPECTED_WORKFLOWS` (`release_checks.py:13-16`) и в required checks ruleset #27259237 при выключенных non-provider secret scanning.
- **Влияние:** риск срыва/зависания релиза, дрейфа ключа при ротации, обрыва changelog и вечного `0/10` по `Signed-Releases`; `gitleaks` сейчас только рекомендательный.
- **Решение:** в `release_checks.py` фильтровать по `head_sha`/`app.slug`/workflow до выбора последнего (сортировка по `completed_at`/`started_at`/`id`), добавить `continue`, `timeout=30`, проверку `.head_sha` и хоста/репо в `details_url`, чистую обработку ошибок JSON + полные unit-тесты (включая `main()` JSONL); в `release.yml` проверять SemVer до git-операций, добавить `--`, запускать `gate/scripts/release_notes.py`, проверять равенство `ALLOWED_SIGNERS` с `gate/docs/release-signing/allowed_signers`, загружать `outputs.bundle-path` от `actions/attest-build-provenance` как asset релиза; исправить fence/footnotes и убрать дубль сканера в `release_notes.py`; добавить `"gitleaks": ".github/workflows/secret-scan.yml"` в `EXPECTED_WORKFLOWS` (скоординировав с владельцем добавление `gitleaks` в ruleset #27259237). Трудоёмкость: 2–3 ч; риски: низкие (проверить совместимость имени Sigstore asset с Scorecard v5.7.0).
- **Приёмка:** расширенные `tests/test_release_checks.py`, `tests/test_release_notes.py`, `tests/test_release_workflow.py` и `make check` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — доработать `release_checks.py`, `release_notes.py` и `release.yml`; неудачные попытки: нет.

### AUD-36 — Eliminate `node_modules` copy amplification (8.0 s) and subprocess fan-out in tests and `validate.py`

- `OPEN` · **Аудит 2026-11-26** · тип: `performance/tests/duplication` · приоритет: **P1 — высокий ущерб** (подтверждено замером: 27.7× лишнего I/O, ~764 MB копирования и >320 подпроцессов на каждый `make check`) · уверенность: **высокая** · трекер: [#75](https://github.com/snaplyze/skills-hub/issues/75) (веха #9) · deps: AUD-30, AUD-33.
- **Результат / границы:** резкое ускорение `make test` и `make validate` без ослабления покрытия и мутационной чувствительности, удаление дублирующих проходов и мёртвого кода в `scripts/validate.py`.
- **Доказательство (замерено в `/tmp/opencode/skills-hub-audit-2026-11-26`):**
  - `tests/test_validation.py:12-25`: `IGNORE` не содержит `"node_modules"` (1 990 файлов / 16.8 MB) и `".venv"` → 44 вызова `copy_repo()` копируют **91 256 файлов / ~764 MB**. Замер B-09: **188.6 ms/копия (8.30 s)** против **6.8 ms/копия (0.30 s)** (**27.7×** экономия); плюс ~182 подпроцесса (`test_validation.py` = **15.82 s из 21.63 s** всего `pytest`, 73%).
  - *Дублирование в `scripts/validate.py` (шаг 5):*
    - `validate.py:620-727, 815-849` (`check_contrast`): замер B-04 = **80.9 ms из 141.7 ms (57.1%)** in-process, так как при уже импортированном `contrast` спавнит 2 Python-подпроцесса (`--self-test` и `--pairs`), парсит `tokens.css` дважды, обходит 64 пары дважды, а строки `639-641` — недостижимый dead code. Инвариант: токены, пары и self-test проходят WCAG 2.2 AA; граница доверия: один локальный процесс; данные неизменяемы; гарантия уже в импортированном `contrast` (CLI проверяет `test_contrast_cli.py`).
    - `validate.py:80-85, 125, 161, 185, 222, 228, 438, 472, 482`: `SKILL.md` читается 3 раза; нет кэша `markdown_headings`; дублируются проверки роутинга (`378` и `468`) и `READING_SET_NEW_PAGE_LIMIT` (`44, 416-421`) поверх `READING_SET_HARD_LIMIT`.
  - Подпроцессный fan-out в других тестах: `test_secrets.py` (51 `git`-вызов), `test_contrast_cli.py` (22 Python-вызова), `test_workflows.py` (21 Python-вызов — замер B-11: **1 225.8 ms** vs **407.0 ms** in-process, **3.0×**), `test_installer.py` (28 `git`-вызовов), `test_release_notes.py` (5 вызовов + мутация `sys.path:13`).
  - Избыточные/холостые тесты: двойной вызов `assert_validation_fails` на том же репо (`test_validation.py:295-296`), no-op `test_reading_sets_valid_manifest_passes:442-448`, неверная ветка `test_reading_sets_new_page_hard_limit_fails:521-528`, дубль `.yml` (`test_workflows.py:265-272`), незакрытый сокет `httpd.server_close()` (`test_external_links.py:56`).
- **Влияние:** затянутый локальный и CI-цикл (`21.6 s` вместо `<4 s`), лишний износ диска, риск многогигабайтных копий при локальном `.venv/`, 47 запусков `contrast.py --self-test` за один `make check`.
- **Решение:** добавить `node_modules`/`.venv`/`venv`/`.mypy_cache`/`*.pyc` в `IGNORE`; параметризовать `validate_repo(root)` и `check_workflows.main(argv)` и перевести unit-мутации `test_validation.py`, `test_workflows.py`, `test_contrast_cli.py`, `test_release_notes.py` в in-process (оставив 1–2 CLI smoke-теста); батчировать `git check-ignore --stdin` в `test_secrets.py` и шаблонный git-репо в `test_installer.py`; объединить проходы и убрать 2 подпроцесса `contrast`/dead code `639-641`/дублирующие проверки в `validate.py`, добавив кэш `markdown_headings`; удалить/исправить холостые тесты и добавить `httpd.server_close()`. Трудоёмкость: 3–4 ч; риски: низкие (не мутировать глобальный `ROOT` в `validate.py`).
- **Приёмка:** сравнение до/после в снимке на тех же данных: `pytest` ≤4 s (было 21.6 s), `validate` ≤100 ms (было 142–335 ms); все граничные и мутационные проверки сохранены; `make check` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — добавить исключения в `IGNORE` и перевести горячие проверки в in-process; неудачные попытки: нет.

### AUD-37 — Fix `frontend-design` technical defects, CSS/Next.js staleness, contrast coverage, licenses, and reading headroom

- `OPEN` · **Аудит 2026-11-26** · тип: `skill-content/accessibility/data` · приоритет: **P1 — высокий ущерб** (сломанный Markdown, устаревший Next.js 16 prop, незамеченная дыра в light-контрасте `--color-surface-raised`, баги парсера `contrast.py`, устаревшие лицензии в `sources.md`) · уверенность: **высокая** · трекер: [#76](https://github.com/snaplyze/skills-hub/issues/76) (веха #9) · deps: AUD-33.
- **Результат / границы:** технически актуальный, внутренне согласованный `frontend-design` (Baseline 2026, Next.js 16, React Compiler, WCAG 2.2 AA в обеих темах, корректные лицензии, запас бюджета `new-page` ≥1.5 KiB) и исправленный `contrast.py`. Без плагинов и копирования чужих текстов.
- **Доказательство:**
  - `skills/frontend-design/references/implementation.md`: `:153` сломанный code span `` `:`has()` ``; `:145` `.field:has(input:invalid)` показывает ошибки до ввода (противоречит `ux-patterns.md:167-169`, нужно `:user-invalid` — Baseline Widely Available с мая 2026); `:356` устаревший Next.js 16 prop `priority` (`vercel/next.js#83351` → `preload` / `loading="eager"` + `fetchPriority="high"`); `:216-226` `<dialog>` `@starting-style` без `display ... allow-discrete`; `:172, 184, 347` пропущены оговорки про `text-wrap: pretty`, `accent-color` и React Compiler v1.0.
  - `skills/frontend-design/references/motion.md:87, 102, 154-160`: `overlay` (Chromium-only) без оговорки; `animation-timeline: view()` без `@supports (animation-timeline: view())` (Baseline 2026 Newly Available с окт 2026).
  - `skills/frontend-design/references/sources.md:16, 38-44, 52-53`: `Leonxlnx/taste-skill` указан как `Upstream terms — verify`, хотя root MIT `LICENSE` добавлен в `75dc4f080018` (2026-04-28, актуален на `d1a2bb41d927`); несогласованность с `THIRD_PARTY_NOTICES.md` по `sickn33`; не отмечены WCAG 2.2 = ISO/IEC 40500:2025 и WAI-ARIA 1.3 CR.
  - `skills/frontend-design/assets/token-contrast-pairs.json:589-591` + `scripts/validate.py:789-801`: `--color-surface-raised` имеет **0 проверок в light-теме** (проверка покрытия не требует обе темы); `contrast.py:95-169, 269-280` игнорирует `combinations`, `lstrip("#")` принимает `####000000` и `#-1-1-1` (отрицательная яркость), `hsl(120 50 50)` без `%`, лишние аргументы и `nan`/`inf`; CSS-парсер в `validate.py:523-591` не экранирует строки, селекторы `:root, ...` и расходится по `@media`.
  - Внутренние противоречия и бюджет `frontend-design`: смешанные базы путей (`../assets/...` vs `assets/...` в `visual-craft.md:3,27` и `audit-report.md:3,10`); 7 несуществующих токенов в `design-system.md:231-281` + 6 пропущенных токенов в `design-system.md:85-109`; пропуск `--color-border-strong` в `design-brief.md:65-75`; дублирование `Forms` и сломанный TOC в `responsive-mobile.md:13,192,233-282`; идентичные сеты `component-state` == `design-system` в `reading-sets.json:30-37,56-63` и рассинхрон `SKILL.md:70`; `new-page` на **99.1%** бюджета (32 462 / 32 768 B, запас 306 B); расхождение `@layer`/`clip:`/reduced-motion между `tokens.css:21,377-421` и `implementation.md`/`motion.md`; green vs safety orange в `worked-example.md:12,20`.
  - Ноябрьские upstream/V2 улучшения: правило недоверенных данных браузера (OpenCode V2 `browser` tool, `audit-report.md`), «проверять существующим тулчейном проекта» (`addyosmani` `#732`), fail-closed a11y (`addyosmani` `0.6.17`), инварианты жизненного цикла ошибок форм / конкретные кнопки destructive-диалогов / DTCG JSON / map `prefers-reduced-motion` (`ui-ux-pro-max` `#577/#581/#587`), prod-build / font-load / overlap 320/390 px / `.example` (`taste-skill` v2.5.1).
- **Влияние:** генерация устаревшего/багованного фронтенд-кода, пропуск регрессий light-контраста, неверные расчёты `contrast.py` на битом вводе, неточная лицензионная атрибуция и исчерпанный запас бюджета `new-page`.
- **Решение:** исправить указанные файлы `frontend-design` references/assets/`sources.md`; починить парсер `contrast.py` (строгий hex regex, `math.isfinite`, CSS Color 4 HSL/углы, запрет лишних аргументов, опциональная поддержка `combinations`); в `validate.py` требовать покрытие обеих тем (`light`+`dark`) для всех не-исключённых токенов и починить string-aware CSS-парсер; добавить `light: text / surface-raised` в fixture; убрать дубли в `new-page` для запаса ≥1.5 KiB. Трудоёмкость: 3–4 ч; риски: средние (контролировать все 10 reading sets ≤32 768 B и 64+ пар WCAG 2.2 AA).
- **Приёмка:** `new-page` ≤31 200 B; все не-исключённые токены покрыты в light и dark; новые негативные тесты `contrast.py` и light-coverage PASS; `make check` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — синхронизировать токены, CSS/Next.js-референсы, `contrast.py` и `sources.md`; неудачные попытки: нет.

### AUD-38 — Upgrade workflow skills from Nov 2026 upstreams and harmonize cross-skill schemas

- `OPEN` · **Аудит 2026-11-26** · тип: `skill-content/architecture` · приоритет: **P1 — высокий ущерб** (утечка секретов при самопроверках diff, отсутствие ограничителя цикла ревью-фиксов в длинном исполнении, расхождение схем ledger/brief между навыками) · уверенность: **высокая** · трекер: [#77](https://github.com/snaplyze/skills-hub/issues/77) (веха #9) · deps: AUD-31, AUD-32.
- **Результат / границы:** синтезировать проверенные ноябрьские улучшения из `obra/superpowers` v7.0.2, `addyosmani/agent-skills` 0.6.18, `anthropics/skills`, `alirezarezvani/claude-skills` и OpenCode V2 в 8 workflow-навыков, унифицировав внутренние схемы и триггеры (без плагинов/хуков/скрытых каталогов и без копирования текста).
- **Доказательство:**
  - `addyosmani/agent-skills` `0.6.15–0.6.18` (`924995886b`, `9c7f62d20cf2`, `c55b84224f`, `d463d94fb6`, `f1f6fbf398`, `480bed1391`): проверка чистоты дерева и `HEAD` перед тестами ревью (`code-review:34`); secret-safe сканирование без вывода значений (`--name-only`/`file:line`, `delivery:34`, `autonomous-execution:49`); проверка callers/guards до репорта, base vs regression, «0 находок — валидно», подтверждение спорного dead code, работа со вставленными сниппетами/stack traces, delta specs.
  - `obra/superpowers` v7.0.2 (`22f0b463e7a5`): ограниченный цикл ревью-фиксов (3–5 раундов, resume → эскалация на свежего исполнителя → breaker), скоупированное ре-ревью `ADDRESSED`/`NOT ADDRESSED`, отложенные minor-замечания в финальное ревью, одноволновый фикс-проход и сводный раздел `"Rulings made"` с ценой ошибки (`autonomous-execution`); открытое «зачем», proposal-over-question, anti-goals, Builder Check (`specification`); re-grade Minor при реальном ущербе (`code-review`); backward root-cause tracing, defense-in-depth, condition-based waiting (`systematic-debugging`); таблица «форма под класс сбоя» + 5+ реп микро-тестов формулировок (`skill-authoring`).
  - `anthropics/skills` (`e4bb5d960d87`) + `alirezarezvani/claude-skills` (`6278f7302d5e`, `#885`) + OpenCode V2: Lack of Surprise, old-version baseline snapshot при редактировании навыка, реалистичные пользовательские формулировки триггеров (112/389 провалов при описании через скрипты), запрет имён встроенных slash-команд (`status`, `review`, `init`, `config`, `help`, `resume`), лимит выборки 10 файлов V2 и headless `opencode run --standalone --archived --format json` (`skill-authoring`).
  - Внутренние расхождения: разные поля ledger (`autonomous-execution:27-36` vs `orchestration:60`), разные поля brief в 3 местах (`orchestration:37-47`, `autonomous-execution:55,82`), пропуск `Approval:`/`Risks:` между прозой и шаблонами (`implementation-planning:18-26,52`; `specification:22,33-44`), пересечение триггеров `frontend-design`/`code-review`/`clean-code` и `test-driven-development`/`systematic-debugging`.
- **Влияние:** риск утечки секретов в транскрипты, зацикливания ревью-фиксов, потери rulings, рассогласования бриф/ledger и двойного срабатывания триггеров.
- **Решение:** компактно внести синтез в `specification`, `implementation-planning`, `autonomous-execution`, `systematic-debugging`, `code-review`, `delivery`, `clean-code`, `skill-authoring` (сохраняя каждый `SKILL.md` заметно ниже 32 KiB) и выровнять схемы ledger/brief/шаблонов и anti-triggers. Трудоёмкость: 3–4 ч; риски: низкие (учитывать контракты `tests/test_skill_suite.py` и правило не писать `opencode.json` в `SKILL.md`).
- **Приёмка:** все 10 workflow `SKILL.md` компактны (≤10 KiB каждый), схемы ledger/brief едины, триггеры разведены, `make check` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — обновить workflow-навыки одним согласованным проходом; неудачные попытки: нет.

### AUD-39 — Speed up and harden `scripts/check_external_links.py` (pruned walk, concurrency, code filtering, redirect/SSRF guard)

- `OPEN` · **Аудит 2026-11-26** · тип: `performance/security/correctness` · приоритет: **P2 — обычное** (работает только по расписанию на `main`, но худший случай превышает 15-минутный timeout и нет redirect/code-block гигиены) · уверенность: **высокая** · трекер: [#78](https://github.com/snaplyze/skills-hub/issues/78) (веха #9) · deps: AUD-33.
- **Результат / границы:** быстрый, детерминированный и защищённый аудит внешних ссылок с привязкой ошибок к `file:line`.
- **Доказательство (замерено в `/tmp/opencode/skills-hub-audit-2026-11-26`):**
  - `scripts/check_external_links.py:39-42`: `root.rglob("*.md")` обходит `node_modules/` (1 990 файлов) до фильтрации (замер B-06: **7.09 ms** vs **0.50 ms** у `os.walk`, **14.2×**) и проверяет `SKIP_DIRS` по полному пути `path.parts` вместо `relative_to(root).parts`.
  - `scripts/check_external_links.py:58-110`: последовательный проход 53 URL (живой замер **32.6 s**, CI **42 s**), `HEAD` + `GET` дают до 30 s/URL (худший случай **26.5 мин > 15 мин** timeout в `link-audit.yml:19`); замер B-07 на 53 URL @ 100 ms mock: **6.19 s** vs **0.83 s** с 8 воркерами (**7.5×**).
  - `scripts/check_external_links.py:24, 48, 67, 71, 98`: сканирует fenced/inline code (проверяет `git clone` URL из bash-блоков); `URL_RE` захватывает `` ` `` и режет `Foo_(bar)`; fallback на `GET` только для `(403, 405, 429)`; дефолтный `urlopen` допускает редиректы на `ftp://` и loopback/RFC1918/link-local IP; неиспользуемая переменная `status`; нет вывода `file:line`; тонкое покрытие `tests/test_external_links.py`.
- **Влияние:** риск таймаута `Link Audit`, ложные срабатывания на примерах кода и редирект-оракул при локальном `make links`.
- **Решение:** заменить `rglob` на pruned `os.walk` с `relative_to(root).parts`; добавить `ThreadPoolExecutor` с per-host семафором (max 2/host для 27 URL `github.com`) и общим timeout-бюджетом на URL; пропускать fenced/inline code (общий хелпер с `validate.py`) и поддержать сбалансированные скобки; добавить redirect/pre-request handler (`http`/`https`, только `is_global` IP + `--allow-local` для unit-тестов); печатать `file:line` для ошибок; расширить `tests/test_external_links.py`. Трудоёмкость: 1.5–2 ч; риски: низкие (per-host cap защищает от 429 на GitHub).
- **Приёмка:** offline-бенчмарк подтверждает ускорение ≥5×; unit-тесты покрывают `external_urls`, code blocks, `HEAD→GET`, `429`/`500`, редирект на loopback/ftp (блокируется без `--allow-local`); `make check` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — переписать обход, конкурентность и redirect-фильтр; неудачные попытки: нет.

### AUD-40 — Remove test fragility, raw-YAML false greens, and `.git` dependency in `tests/`

- `OPEN` · **Аудит 2026-11-26** · тип: `tests/correctness` · приоритет: **P2 — обычное** (тесты падают/скипаются в архиве релиза и допускают ложнозелёные правки workflows/навыков) · уверенность: **высокая** · трекер: [#79](https://github.com/snaplyze/skills-hub/issues/79) (веха #9) · deps: AUD-36.
- **Результат / границы:** тесты проверяют поведение структурно, стабильно работают как в git-checkout, так и в extracted release archive, без хрупкой привязки к переносам строк и точному тексту.
- **Доказательство:**
  - Воспроизведено напрямую в `git archive` снимке: `tests/test_release_assets.py:127-157` (`test_current_head_archive_contains_all_skills`) падает (`rc=1`, `fatal: не найден git репозиторий`), а `tests/test_release_signature.py:96-126` молча `skip`ает оба теста подписи.
  - `tests/test_secrets.py:119-125` и `tests/test_release_workflow.py:27-45`: проверяют YAML сырым текстом (комментарии проходят; не проверяются SHA-256 gitleaks, `$RUNNER_TEMP/gitleaks.toml`, `environment: release`, `cancel-in-progress: false`, связка `ref: main` + `path: gate`) и жёстко завязаны на 4 имени шагов.
  - `tests/test_skill_suite.py`: line-wrap-зависимый assert на `:309-312` (`"Never hide"`), 27 точных строк в `V2_REQUIRED`, 3× дублированный regex заголовков + мёртвое исключение `or skill_id == "delivery"` (`:135`), тавтологичные `TRIGGER_MATRIX` и self-only mutation-тесты, исключение `frontend-design` из универсальных проверок портативности.
- **Влияние:** ложная уверенность в защите `secret-scan.yml`/`release.yml`, поломка тестов при безобидном reflow Markdown и невозможность честно прогнать `pytest` из архива релиза.
- **Решение:** перевести `test_secrets.py` и `test_release_workflow.py` на структурный YAML-разбор; добавить детерминированный `tmp_path` SSH-signed-tag fixture в `test_release_signature.py` (всегда выполняется) и явную git-guard логику в `test_release_assets.py`; очистить `test_skill_suite.py` (динамический список навыков включая `frontend-design`, один константный regex, проверка `progress.md` на уровне документа, кросс-навыковая изоляция триггеров). Трудоёмкость: 2–3 ч; риски: низкие.
- **Приёмка:** `pytest` проходит с 0 failed и без пропуска core-тестов подписи как в git-репо, так и в `git archive` снимке; мутация комментариями в `secret-scan.yml`/`release.yml` валит тесты; `make check` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — перевести workflow-тесты на YAML AST и детерминировать release-тесты; неудачные попытки: нет.

### AUD-41 — Run plan hygiene pass («Порядок в плане») on `docs/plan.md`

- `OPEN` · **Аудит 2026-11-26** · тип: `documentation/process` · приоритет: **P2 — обычное** (признаки раздутого плана — 77.5% завершённой истории в трёх разрозненных секциях и устаревшие мета-разделы) · уверенность: **высокая** · трекер: [#80](https://github.com/snaplyze/skills-hub/issues/80) (веха #9) · deps: none.
- **Результат / границы:** компактный `docs/plan.md` с единой свёрнутой историей этапов 01–08 и чистым фокусом на активных задачах `Аудит 2026-11-26` (без потери ID, статусов, ссылок, решений владельца и рисков). Уборка плана вынесена отдельной задачей по границам аудита.
- **Доказательство:**
  - До добавления раздела `Аудит 2026-11-26` файл `docs/plan.md` снова вырос до **328 строк / 37 649 B** (равен пре-компактному размеру до `AUD-28`), из которых **243 / 328 строк (74.1%)** и **29 171 / 37 649 B (77.5%)** — исторические `DONE`-блоки, разбросанные по трём секциям (`## Задачи аудита` 9 307 B без `AUD-28`, `## Skill suite v2` 2 127 B, `## Завершено` 15 058 B + устаревшая секция `## Что свёрнуто и почему` 1 918 B в настоящем времени от PR #50).
  - Оставшиеся устаревшие записи в старых секциях `docs/plan.md`: `:511` («продуктовые исправления не начинались», исторически `:261`), `:517` («7 OPEN», исторически `:267`); три других устаревших утверждения (`report` в `AGENTS.md`, «менялись только план и документы», «двух источников») уже обновлены в ходе аудита #68, но дубли заметок владельца и три раздробленные DONE-секции сохраняются.
- **Влияние:** высокий шум при каждом чтении плана и путаница между закрытыми и открытыми аудитами.
- **Решение:** выполнить промпт «Порядок в плане»: свернуть завершённые `AUD-22..29` и `SKL2-01..04` в общий компактный архив `## Завершено`, удалить устаревшую мета-секцию `## Что свёрнуто и почему`, очистить оставшиеся устаревшие утверждения (`7 OPEN`, «продуктовые исправления не начинались») и дубли заметок владельца, обновить таблицу размеров документов. Трудоёмкость: 30–45 мин; риски: низкие (не потерять ни одного исторического ID/ссылки/решения).
- **Приёмка:** все исторические ID (`AUD-01..29`, `SKL-01..09`, `ORC-01`, `SKL2-01..04`) и открытые `AUD-30..43` сохранены; нет устаревших утверждений и дублирующих секций; `make validate` и `markdownlint` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — выполнить проход «Порядок в плане»; неудачные попытки: нет.

### AUD-42 — Cut next signed release (`v1.3.0`) after audit fixes (owner-gated)

- `OPEN` · **Аудит 2026-11-26** · тип: `delivery/release` · приоритет: **P2 — обычное** (на `main` накопились 8 коммитов включая Skill Suite v2, отсутствующие в `v1.2.0`) · уверенность: **высокая** · трекер: [#81](https://github.com/snaplyze/skills-hub/issues/81) (веха #9) · deps: AUD-30, AUD-31, AUD-32, AUD-33, AUD-34, AUD-35, AUD-37, AUD-38.
- **Результат / границы:** новый подписанный immutable релиз (`v1.3.0`), синхронизирующий release-архив с актуальным `main` (`README.md`, Skill Suite v2 + исправления аудита 2026-11-26). **Ограничение:** создание тега `v*` и публикация релиза — только по отдельному поручению владельца.
- **Доказательство:**
  - `git log v1.2.0..HEAD --oneline`: 8 коммитов (+772/-99 строк по 19 файлам), включая PR #62 (`feat: strengthen planning and execution skill suite`) и PR #55/#56 (усиление проверки подписей).
  - `README.md:58` на `main` описывает v2-механику (`docs/plans/`, `progress.md`), `CHANGELOG.md:8-19` содержит `## [Unreleased]`, тогда как `v1.2.0` (`8f252ca`, 2026-11-15) содержит только v1-версию этих навыков.
- **Влияние:** пользователи, ставящие навыки из последнего релиза (`v1.2.0`), не получают Skill Suite v2 и исправления аудита.
- **Решение:** после закрытия зависимых задач аудита и одобрения владельца оформить секцию `## [1.3.0]` в `CHANGELOG.md`, создать подписанный аннотированный тег `v1.3.0`, запустить `release.yml` с `main`, проверить draft/checksum/Sigstore/attestation, опубликовать и обновить ссылки на последний релиз в `README.md` и `docs/repository-settings.md`. Трудоёмкость: 1 ч; риски: требуется участие владельца (подпись тега, `release` env, promotion).
- **Приёмка:** `v1.3.0` — latest immutable release с 11 обновлёнными навыками, `SHA256SUMS`, Sigstore bundle и attestation; `gh attestation verify` и `verify-tag` PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — дождаться завершения зависимых задач и поручения владельца; неудачные попытки: нет.

### AUD-43 — Dependency bumps, CI/tooling polish, `bug_report.yml`, and `AGENTS.md` sync

- `OPEN` · **Аудит 2026-11-26** · тип: `ci/dependencies/docs` · приоритет: **P3 — низкий риск** (0 открытых CVE в зависимостях, плановое обновление патчей, мелкая гигиена и синхронизация не-редактируемых в аудите файлов) · уверенность: **высокая** · трекер: [#82](https://github.com/snaplyze/skills-hub/issues/82) (веха #9) · deps: AUD-30.
- **Результат / границы:** актуальные зависимости/Actions, обновлённый шаблон баг-репортов, мелкие оптимизации/docstring и согласованный с владельцем `AGENTS.md`.
- **Доказательство:**
  - Открытые зелёные Dependabot PR #66 (`ruff` `0.17.5→0.17.6`) и PR #67 (`dependency-review-action` `5.0.0→5.0.1`, `scorecard-action` `2.5.0→2.6.0` с Scorecard v5.7.0 / Go 1.27.4).
  - Новые патчи (2026-11-20–24): `PyYAML 6.0.4` (фикс экспоненциального merge-key DoS `#937` + Python 3.15), `github/codeql-action v4.39.5`, `markdownlint-cli2 0.24.2`.
  - `.github/workflows/codeql.yml:32-34, 47-48`: нет языка `actions` и запускается no-op `autobuild` для Python-only; `Makefile:34` / `package.json:10` не исключают `#/.venv` и `#/.playwright-cli` в `markdownlint-cli2`; `scripts/check_workflows.py:17` docstring пропускает `[--strict]`; `install/opencode.sh:9,58` показывает pre-gate тег `v1.0.1` в `--help`.
  - `.github/ISSUE_TEMPLATE/bug_report.yml:18`: `Area` содержит только `frontend-design skill`, без 10 workflow-навыков.
  - `AGENTS.md:3, 16, 36`: устаревшее «первый навык — `frontend-design`», указание `THIRD_PARTY_NOTICES.md` только как указателя, дата `2026-11-14` после правок `2026-11-15`, устаревшее V1-имя `subagent_depth=2` вместо `experimental.subagent_depth`.
  - `skills/frontend-design/scripts/contrast.py:68-77, 185-225, 249, 351-377`: мелкие лишние аллокации (`clamped()` × 4, повторный `flatten()`/`thresholds()`/`build_parser()`; замер B-02 уже 467 ms на 50 000 пар, поэтому P3).
  - `README.md`: добавить необязательную справку по OpenCode V2 `skills[]` config array, 6-уровневому приоритету discovery и `skill`/`skill.use` permissions/policies.
- **Влияние:** накопление мелкого техдолга, устаревшая категория багов и дрейф `AGENTS.md`.
- **Решение:** смержить зелёные PR #66/#67 и обновить `PyYAML`/`codeql-action`/`markdownlint-cli2`; добавить опцию workflow-навыков в `bug_report.yml`; добавить `#/.venv`/`#/.playwright-cli` в markdownlint, `[--strict]` в docstring `check_workflows.py`, `v1.2.0`/`vX.Y.Z` в `opencode.sh --help`; оценить `actions` и удаление no-op `autobuild` в `codeql.yml`; устранить мелкие аллокации в `contrast.py`; согласовать с владельцем и обновить `AGENTS.md` и справку V2 в `README.md`. Трудоёмкость: 1.5–2 ч; риски: низкие (при добавлении CodeQL `actions` убедиться в отсутствии новых алертов).
- **Приёмка:** зависимости и шаблоны обновлены, `make check` и все CI-проверки PASS.
- **Текущая запись:** статус `OPEN`; решение не начато; проверка не выполнялась; следующий шаг — смержить PR #66/#67 и выполнить пакетную уборку; неудачные попытки: нет.

## Задачи аудита

Исполнитель: не назначен. BLOCKED: нет. Статус указан в записи; DONE-задачи остаются для трассировки.

### AUD-22 — Latest release does not contain the skill suite

- `DONE` · P2 · delivery/docs · #41 · deps: AUD-01, SKL/ORC (DONE). **Границы:** release assets/notes/README; публикация — только владелец.
- **Доказательство:** `git ls-tree -d --name-only v1.1.0:skills` → `frontend-design`; `README.md:27-37` перечисляет 11 навыков; `v1.1.0` (`b1f438d`) создан до PR #36/#39. **Влияние:** release install и README расходятся; новые навыки доступны только из `main`.
- **Решение:** выпустить следующий signed release после suite, обновить notes/README, добавить checklist «все 11 skills присутствуют». Трудоёмкость 1–2 ч; риск — owner approval.
- **Проверка/приёмка:** `git ls-tree` нового тега содержит 11 skills; archive install устанавливает их; checksum/attestation PASS; README и notes совпадают.
- **Результат/доказательство:** signed tag `v1.2.0` (`8f252ca`) опубликован; release `v1.2.0` — latest, immutable; в теге и архиве 11 skills; archive install, `SHA256SUMS` и `gh attestation verify` PASS; README/notes совпадают. **Следующий шаг:** нет.

### AUD-23 — Public release signature is not independently verifiable from docs

- `DONE` · P2 · security/docs · #42 · deps: AUD-01 (DONE). **Границы:** публичный trust-материал и docs; секреты не публикуются.
- **Доказательство:** `README.md:82` требует `git tag -v "$VERSION"`, но не публикует allowed-signers/public key; fresh shallow clone `v1.1.0` → `gpg.ssh.allowedSignersFile needs to be configured`; с локальным `allowed_signers` проверка PASS.
- **Влияние:** пользователь не может воспроизвести проверку подписи по инструкции; остаётся доверять GitHub-аккаунту.
- **Решение:** опубликовать public allowed-signers/key в repo или release asset; добавить точную команду `git -c gpg.format=ssh -c gpg.ssh.allowedSignersFile=... verify-tag`; тест/CI. Трудоёмкость 30–60 мин; риск — раскрытие только публичного материала.
- **Проверка/приёмка:** fresh clone + repo trust file PASS; подмена подписи FAIL; ротация ключа описана.
- **Результат/доказательство:** `docs/release-signing/allowed_signers`, `docs/release-signing/README.md`, команда в README/release-process; `tests/test_release_signature.py`; `git verify-tag v1.1.0` PASS с repo-файлом, tampered key FAIL.

### AUD-24 — Documentation references and skill counts drift

- `DONE` · P3 · documentation · #43 · deps: ORC-01 (DONE). **Границы:** docs и автоматическая проверка путей/счётчиков; поведение продукта не меняется.
- **Доказательство:** `docs/opencode-orchestration.md` указывал на несуществующий `tests/test_orchestration.py` (реальный — `tests/test_skill_suite.py`); проверка в плане называла 10 навыков при 11; README intro/layout не отражали `orchestration`; `THIRD_PARTY_NOTICES.md` не перечислял `orchestration`; в `docs/release-process.md` был дублирован фрагмент signature/ancestry/check-run.
- **Исправлено:** drift исправлен в PR #49; остаётся автоматическая проверка, что пути тестов из docs существуют и счётчики навыков совпадают с `skills/`.
- **Влияние:** следующий исполнитель ищет несуществующий тест или неверно оценивает состав.
- **Решение/проверка:** добавить проверку path/count; mutation docs path/count должна падать; `make check` PASS. Трудоёмкость 30–60 мин.
- **Результат/доказательство:** `tests/test_skill_suite.py` проверяет существование test paths из docs, соответствие README Skills table каталогам `skills/` и listing в AGENTS; `make check` PASS.

### AUD-25 — Skill suite contract tests are too weak

- `DONE` · P3 · tests · #44 · deps: SKL-09 (DONE). **Границы:** `tests/test_skill_suite.py`; обязательные проверки не ослабляются.
- **Доказательство:** `tests/test_skill_suite.py:52-58` проверяет только заголовок из списка; `:71-84` — наличие двух слов в description, без prompt/negative prompt. **Влияние:** сломанный workflow/trigger не ловится.
- **Решение:** table-driven trigger matrix с realistic prompts и negative prompts; проверять обязательные секции/stop conditions; пустой workflow должен валить suite. Трудоёмкость 1–2 ч.
- **Проверка/приёмка:** positive prompts проходят; пустой workflow/слишком широкий trigger валит suite; mutation-тест PASS.
- **Результат/доказательство:** table-driven positive/negative trigger matrix, workflow body length, empty-workflow mutation; 10 contract tests PASS.

### AUD-26 — Simple-skill validation branch has no focused test

- `DONE` · P3 · tests · #45 · deps: AUD-03 (DONE). **Границы:** `scripts/validate.py` simple-skill branch; manifest path не переписывается.
- **Доказательство:** `scripts/validate.py:298-310` проверяет размер `SKILL.md` для навыка без manifest; `tests/test_validation.py` покрывает manifest, но не простой oversize/absence path. **Влияние:** регрессия размера/чтения может пройти.
- **Решение:** temp skill без `references/assets`: pass; oversize `SKILL.md`: fail; `references` без manifest: fail. Трудоёмкость 30–60 мин.
- **Проверка/приёмка:** три кейса зелёные; mutation ветки падает.
- **Результат/доказательство:** `tests/test_validation.py` — simple skill без manifest PASS, oversize FAIL, references без manifest FAIL; 3 focused tests PASS.

### AUD-27 — Orchestration and execution triggers overlap

- `DONE` · P3 · architecture/content · #46 · deps: ORC-01, SKL-09 (DONE). **Границы:** skill descriptions/handoff; без plugin/hooks.
- **Доказательство:** `skills/orchestration/SKILL.md:3` и `skills/autonomous-execution/SKILL.md:3` обе срабатывают на complex/multi-step; у orchestration нет anti-trigger «передать утвержденный план в autonomous-execution». **Влияние:** двойная загрузка двух skill-инструкций, лишний контекст.
- **Решение:** добавить явный anti-trigger/handoff и negative prompt в trigger matrix. Трудоёмкость 15–30 мин.
- **Проверка/приёмка:** «execute approved plan» → execution; «how to route unknown work» → orchestration; tabletop tests PASS.
- **Результат/доказательство:** `skills/orchestration/SKILL.md` description/handoff на `autonomous-execution`; `test_orchestration_hands_off_approved_plan` и negative matrix PASS.

### AUD-29 — External-link tests start a server per test

- `DONE` · P3 · performance/tests · #48 · deps: AUD-03 (DONE). **Границы:** `tests/test_external_links.py`; изоляция и поведение сохраняются.
- **Доказательство:** `tests/test_external_links.py:45-57` создаёт/останавливает `ThreadingHTTPServer` в каждой fixture; `pytest --durations` показывает 0.50 s teardown на каждом из 4 тестов, около 2 s из 15 s. **Влияние:** лишняя стоимость тестов, не продукта.
- **Решение:** module/session-scoped server с уникальными путями/handlers или один CLI-тест с несколькими URL. Трудоёмкость 30–60 мин.
- **Проверка/приёмка:** server один на модуль; `pytest --durations` ≤1 s на файл; тесты PASS.
- **Результат/доказательство:** module-scoped HTTP server один на модуль; 4 tests PASS, `--durations` teardown 0.50 s один раз, файл ~0.55 s (было ~2 s).

## Skill suite v2 (2026-11-16)

Детальный план: [docs/plans/2026-11-16-skill-suite-v2.md](plans/2026-11-16-skill-suite-v2.md). Веха #8; задачи #58–#61 DONE; `make check` 202 tests. Источники: superpowers (MIT), addyosmani/agent-skills (MIT), planning-with-files (MIT), wshobson/agents (MIT), anthropics/skills (README: Apache 2.0 для многих; проверять per skill). Без plugin/hooks/hidden workspace.

### SKL2-01 — Plan contract and project-local workspace

- `DONE` · #58 · deps: none · **Границы:** `specification`/`implementation-planning`/tests; no runtime.
- **Результат:** plan header + interfaces + checkbox steps + expected + checkpoints; `docs/plans/` only; no overwrite of incomplete plans.
- **Приёмка:** fresh executor can implement from plan; contract tests; `make check` PASS.

### SKL2-02 — Execution ledger, task briefs, and rulings

- `DONE` · #59 · deps: SKL2-01 · **Границы:** `autonomous-execution`/`orchestration`/tests; no hidden state.
- **Результат:** ledger `docs/plans/<slug>.progress.md`, task briefs, BASE, rulings, 3-strike, per-task and final review; independent failure routing.
- **Приёмка:** resume after compaction; subagents bounded; one writer per file; `make check` PASS.

### SKL2-03 — Review and delivery quality bars

- `DONE` · #60 · deps: SKL2-02 · **Границы:** `code-review`/`delivery`/`clean-code`/tests.
- **Результат:** tests-first review, mutation check, five axes, severity, integration choice, post-merge verify, scope discipline.
- **Приёмка:** evidence-based findings; actual merged commit checked; `make check` PASS.

### SKL2-04 — Skill evals, trigger quality, attribution

- `DONE` · #61 · deps: SKL2-01–SKL2-03 · **Границы:** `skill-authoring`, notices, README/CHANGELOG, tests.
- **Результат:** trigger mining, baseline evals, pressure variants, versioning, license checks; source attribution.
- **Приёмка:** new skill has eval evidence; licenses recorded; reading budget preserved; `make check` PASS.

## Завершено

Все DONE подтверждены `make check`/CI; следующий шаг по DONE — нет; неудачных попыток по задачам не зафиксировано. Навыки: [obra/superpowers](https://github.com/obra/superpowers) (MIT) и [sickn33/agentic-awesome-skills clean-code](https://github.com/sickn33/agentic-awesome-skills/tree/main/skills/clean-code) (MIT/CC BY 4.0); оригинальный синтез. Orchestration: [oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) и [claude-orchestration](https://github.com/snaplyze/claude-orchestration); только идеи маршрутизации, без плагина.

### AUD-01 — Release pipeline integrity

- `DONE` · P1 · security/release · #14 · deps: none (AUD-02 related) · **Границы:** release workflow/tags/notes/provenance; no skill content/product behavior; settings only by owner.
- **Было:** release workflow принимал любой `v*` без ancestry/check-run/env; теги без подписи; notes вручную; assets 0.
- **Результат/решение:** dispatch only from `main`; signed annotated tag verified against owner trust, ancestry `origin/main`, required `validate`/`Analyze (python)` check-runs with workflow path, protected `release` env; notes single-source from `CHANGELOG`; draft + manual promotion; prerelease uses `--prerelease --latest=false`; archive/SHA-256/provenance; `v1.1.0` signed/immutable (`b1f438d`); labels rejected; `README`/`GOVERNANCE §Releases` match the gate; `updated_at == published_at` для новых релизов, если ручной шаг не задокументирован; immutable setting owner-verified, workflow не читает admin endpoint.
- **Приёмка/доказательство:** `.github/workflows/release.yml`, `scripts/release_notes.py`, `scripts/release_checks.py`, `tests/test_release_*`, `docs/release-process.md`; `make check`; `git tag -v v1.1.0` PASS with allowed-signers.

### AUD-02 — Installer safety and verifiable install

- `DONE` · P2 · security/delivery · #15 · deps: AUD-01; related AUD-03/AUD-04 · **Границы:** installer/install docs; no skill content; tests use temp HOME/target; no real user config writes.
- **Было:** guard только `/`/`$HOME`; `rm -rf` target; `--copy --force` no-op на symlink; `--all` без kebab regex; ignored artifacts копировались.
- **Результат/решение:** copy default; realpath/refuse guards; atomic staging/backups; `--copy` over symlink; `--all` IDs; artifact exclusions; `~/`; folded YAML; `--verify/--ref`; source tree unchanged, destructive targets write only target; README различает main/release; archive/checksum/install tested on `v1.1.0`.
- **Приёмка/доказательство:** `install/opencode.sh`, `tests/test_installer.py`, `tests/test_release_assets.py`; target matrix/refusal/copy/force/conflict/list PASS.

### AUD-03 — Validation correctness and token fixture

- `DONE` · P1 · tests/accessibility/data · #16 · deps: none; related AUD-02/AUD-04/AUD-06 · **Границы:** validator/tests/token fixture; no skill prose; обязательные проверки не ослабляются.
- **Было:** validator пропускал SKILL/cross-file anchors, проверял только passing fixture; contrast exit failure не тестировался; fixture 1/0 pairs проходил; tokens давали AA-fail.
- **Результат/решение:** validator covers SKILL/cross-file anchors, title/reference/root-relative links, frontmatter/body, 106 local links, AGENTS/PR template, fixture 64/32+32, semantic coverage, reading sets; contrast CLI exit 0/1/2; every check has pass/fail fixture and mutation; 64 pairs + 26 semantic combos AA; token/fixture parity.
- **Приёмка/доказательство:** `scripts/validate.py`, `tests/test_validation.py`, `tests/test_contrast_cli.py`; 188 tests PASS.

### AUD-04 — CI toolchain and workflow hardening

- `DONE` · P2 · CI/security/reproducibility · #17 · deps: AUD-03; related AUD-01/AUD-02/AUD-06/AUD-07 · **Границы:** CI/workflows/toolchain; no product behavior; runner/branch/account settings only by owner.
- **Было:** unpinned ranges/npx/apt, `ubuntu-latest`, workflow-level `pull-requests: write`; локальный/CI набор расходился.
- **Результат/решение:** `ubuntu-24.04`, Python 3.12, pip 26.3, hash-locked `requirements-dev.txt`/npm, `npm ci` cache and npm Dependabot; one `make check`; workflow policy checks 7 files and rejects unsafe workflows; Dependency Review write at job scope; docs/CI match; budget `make validate` ≤1 s / `make check` ≤30 s accepted.
- **Производительность:** путь `.github/workflows/ci.yml`; нагрузка — pip/npm + suite; baseline 810 ms без pytest; цель `validate` ≤1 s/`check` ≤30 s; сравнение per-step timing; duplicate contrast/bash удалены.
- **Приёмка/доказательство:** `.github/workflows/*`, `Makefile`, `scripts/check_workflows.py`, `tests/test_workflows.py`, `.github/dependabot.yml`; Scorecard Pinned-Dependencies ≥9; 188 tests; runtime ~0.3 s/20 s.

### AUD-05 — Secret handling and ignore guard

- `DONE` · P2 · security · #18 · deps: none (AUD-03 related) · **Границы:** `.gitignore`/secret scan; секретные значения не читаются и не публикуются.
- **Было:** `.env*`, ключи, `secrets/`, `credentials*`, agent dirs не игнорировались; secret scan отсутствовал.
- **Результат/решение:** `.gitignore` covers `.env*` (with `!.env.example`), `*.pem`/`*.key`/`*.p12`, `secrets/`, `credentials*`, `.opencode/`, `.claude/`, `.agents/`; gitleaks 8.30.1 pinned by SHA scans history; non-provider/validity scanning owner-only; AGENTS caveat снят.
- **Приёмка/доказательство:** `.gitignore`, `.github/workflows/secret-scan.yml`, `tests/test_secrets.py`, `docs/repository-settings.md`; `git check-ignore` PASS.

### AUD-06 — Skill content and instruction budget

- `DONE` · P2 · content/performance/docs · #19 · deps: AUD-03; related AUD-04/AUD-07 · **Границы:** skill docs/assets/AGENTS project info; no product behavior or code/CI.
- **Было:** `design-direction.md` 35 017 B, typical set 85 527 B; tokens/motion/units/budgets расходились; дубли шаблонов и attribution.
- **Результат/решение:** 32 KiB reading budget; tokens canonical; motion/units/budgets fixed; `quality-gates.md`/`assets/audit-report.md` one template; `skills/frontend-design/references/sources.md` canonical; `AGENTS.md §План`/project info/listing aligned; `SKILL.md` 7 035 B; 10 reading sets; new-page 32 462 B; worked example excluded.
- **Производительность:** путь `SKILL.md` routing + references; нагрузка — загружаемые байты; baseline 35 017 B / 85 527 B; цель 32 KiB; сравнение `wc -c`; дубли/лишние разделы удалены.
- **Приёмка/доказательство:** `skills/frontend-design/assets/reading-sets.json`, references, `scripts/validate.py`; `make check` PASS.

### AUD-07 — Repository protections and evidence

- `DONE` · P3 · security/docs · #20 · deps: related AUD-01/AUD-04/AUD-06 · **Границы:** CODEOWNERS/ruleset docs/settings evidence; access changes only by owner.
- **Было:** ruleset 0 approvals/no codeowner; `branch_protection_rule` не срабатывает на rulesets; settings evidence отсутствовал.
- **Результат/решение:** CODEOWNERS advisory; Scorecard triggers `branch_protection_rule`/weekly/push; SARIF in code scanning; artifact 30 days; settings/date/owner actions in `docs/repository-settings.md`; `GOVERNANCE §Review`/settings evidence/date match; approvals/code-owner review/emergency path deferred to second maintainer.
- **Приёмка/доказательство:** `.github/CODEOWNERS`, `.github/workflows/scorecard.yml`, `docs/repository-settings.md`; claims synchronized.

### SKL-01 — Specification

- `DONE` · #27 · deps: none · **Границы:** не писать код, не заменять исследование кода вопросами.
- **Результат/приёмка:** запрос → проверяемая спецификация (проблема, пользователь, результат, non-goals, ограничения, acceptance, риски, открытые вопросы); правила вопросов, запрет выдумывать требования, handoff в планирование, ссылки валидируются.
- **Доказательство:** `skills/specification/SKILL.md`; description/links/anti-trigger PASS.

### SKL-02 — Implementation planning

- `DONE` · #28 · deps: SKL-01 · **Границы:** план, не реализация.
- **Результат/приёмка:** спецификация → исполнимый план: задачи 5–30 минут, точные файлы/интерфейсы, тесты, зависимости, проверки, риски; шаблон, self-review, handoff в исполнение; без hooks.
- **Доказательство:** `skills/implementation-planning/SKILL.md`; task size/deps/handoff PASS.

### SKL-03 — Autonomous execution

- `DONE` · #29 · deps: SKL-02, SKL-05 · **Границы:** без hooks/plugin; worktree только при необходимости.
- **Результат/приёмка:** утверждённый план исполняется автономно: один писатель на файл, параллельные независимые задачи, TDD-гейт, ledger, review, stop conditions, брифы субагентов.
- **Доказательство:** `skills/autonomous-execution/SKILL.md`; subagents/one-writer/review-gate/worktree/ledger PASS.

### SKL-04 — Systematic debugging

- `DONE` · #30 · deps: SKL-05 · **Границы:** сначала reproduce/root cause, не shotgun-фиксы.
- **Результат/приёмка:** reproduce → locate → hypothesize → fix → regression test; evidence, red flags, no-root-cause path.
- **Доказательство:** `skills/systematic-debugging/SKILL.md`; phases/regression PASS.

### SKL-05 — Test-driven development

- `DONE` · #31 · deps: none · **Границы:** поведенческие тесты, не подгонка под тесты.
- **Результат/приёмка:** red-green-refactor с наблюдаемым падением; три закона TDD, качество тестов, bugfix flow, anti-patterns, полный regression run.
- **Доказательство:** `skills/test-driven-development/SKILL.md`; iron law/three laws/refactor PASS.

### SKL-06 — Code review

- `DONE` · #32 · deps: SKL-03 · **Границы:** свежий контекст, без self-approval.
- **Результат/приёмка:** ревьюер получает spec/diff/tests/риски; severity P0/P1/P2; response protocol; no performative agreement.
- **Доказательство:** `skills/code-review/SKILL.md`; request/receive/evidence PASS.

### SKL-07 — Delivery

- `DONE` · #33 · deps: SKL-06 · **Границы:** без обхода проверок.
- **Результат/приёмка:** completion доказывается свежими командами; evidence gate, diff/check/PR checklist, merge rules, cleanup, completion report.
- **Доказательство:** `skills/delivery/SKILL.md`; evidence/PR/merge/cleanup PASS.

### SKL-08 — Clean code

- `DONE` · #34 · deps: SKL-05 · **Границы:** behavior-preserving refactor; конвенции репозитория выше эвристик.
- **Результат/приёмка:** язык-агностичный рефакторинг: имена, маленькие единицы, границы, ошибки, дублирование, связность, тесты; decision framework, refactor loop, checklist, anti-patterns.
- **Доказательство:** `skills/clean-code/SKILL.md`; behavior/refactor PASS.

### SKL-09 — Skill authoring

- `DONE` · #35 · deps: SKL-01–SKL-08 · **Границы:** без behavioral evals без прогона; без hooks.
- **Результат/приёмка:** trigger-rich description, компактный workflow, progressive disclosure, tabletop trigger matrix, repo integration, attribution; behavioral evals не запускались — ограничение.
- **Доказательство:** `skills/skill-authoring/SKILL.md`; tabletop matrix/link/validation PASS.

### ORC-01 — Native OpenCode orchestration skill

- `DONE` · #38 · deps: SKL-03, SKL-06, SKL-07 · **Границы:** без plugin/hooks/background scheduler/marketplace/TUI/model profiles; глобальный `opencode.json` не меняется.
- **Результат/приёмка:** routing matrix (direct/one delegate/parallel read-only/serialized writers/review/delivery), brief template, file ownership, review-gate, verification; native `explore`/`general` only; docs comparison с двумя источниками; contract tests.
- **Доказательство:** `skills/orchestration/SKILL.md`, `docs/opencode-orchestration.md`, `tests/test_skill_suite.py`; `make check` PASS.

### AUD-15 — documentation corrections

- `DONE` · docs · no tracker · **Границы:** только документы; поведение не менялось.
- **Результат/приёмка:** README/CONTRIBUTING/GOVERNANCE/SECURITY/CHANGELOG/notices: `make check` vs CI, Node 22+, `--force` deletion scope, release-gate wording, tag creation, skills table, license qualifiers, description trigger; residual AUD-20 tracked in AUD-04.
- **Доказательство:** `git show 9a7804e`; CI #12 PASS.

### AUD-28 — Plan is oversized for its startup role

- `DONE` · P3 · documentation/process · #47 · deps: audit complete · **Границы:** план и связанные документы; продукт не меняется.
- **Результат/приёмка:** один компактный реестр; завершённые блоки сведены, открытые задачи сохранены; 26 ID (на момент сжатия 19 DONE + 7 OPEN), все статусы/зависимости/ссылки/риски сохранены; план 328 строк / 51 255 B → 297 / 34 274; стартовый контекст 8 223–9 503 B.
- **Доказательство:** этот файл; `make check` PASS; ссылки/якоря validate PASS; PR этой задачи закрывает #47.

## Решения владельца

- CI: hosted; self-hosted сейчас нет; fork approval для всех внешних; обязательные проверки `validate`, `Analyze (python)`, `dependency-review`; CodeQL — code-scanning gate.
- Бюджет проверок: `make validate` ≤1 s, `make check` ≤30 s на hosted runner.
- Релизы: только владелец; signed annotated tags, ancestry `main`, required checks, protected `release` environment, immutable releases, draft + manual promotion, notes из `CHANGELOG`.
- Main: 0 approvals пока solo; CODEOWNERS advisory; при втором maintainer — approvals=1, code-owner review, signed commits/tags, emergency path.
- Навыки: 10 workflow skills + `frontend-design`; orchestration только native `explore`/`general`; без plugin/hooks/background/TUI/model profiles; 32 KiB reading budget; WCAG 2.2 AA (24/44 px, 4.5:1/3:1, 64 pairs).
- План: owner-facing, русский, единый реестр; не загружается как инструкции; продуктовые исправления не начинались; только отдельными задачами.
- Доступ/оркестрация: full non-interactive только через пользовательскую обёртку; в проекте не настраивать; подагентов не устанавливать и не менять.

## Аудит: охват и ограничения

- 2026-11-15, база `2b4be4f`: архитектура, безопасность, данные, производительность, тесты, сборка/доставка, документация; находки AUD-01…AUD-07 DONE.
- 2026-11-15, база `977e2f2`: те же области; 8 находок, 7 OPEN + AUD-28 DONE. Снимок: `make check` PASS (188 tests), `validate` PASS (11 skills), 49/49 внешних ссылок; `v1.1.0` проверен публичным allowed-signers.
- 2026-11-26, база `5f0a620` (Аудит 2026-11-26): все 7 областей + OpenCode V2 (`v2.4.1`) + 11 upstream-репозиториев; 14 задач `AUD-30`–`AUD-43` OPEN + 7 прямых документальных исправлений. Снимок `/tmp/opencode/skills-hub-audit-2026-11-26`: `validate` PASS (0.335 s, 11 навыков), 53/53 внешних ссылок (32.6 s), `pytest` в git-checkout PASS (21.63 s, 202 tests), в не-git снимке падает `test_current_head_archive_contains_all_skills` и skip 2 теста подписи; `opencode debug agents --standalone` подтвердил дефолтные права `plan`/`explore`/`general`.
- Не проверено: fork PR, live tag/release dispatch, destructive installer, macOS/BSD installer runtime, UI WCAG, tokenizer, upstream legal review; Python 3.9 runtime не проверялся (floor 3.12). Реестр относится к коммитам аудита.

## Риски

- Release: custody/rotation подписывающего ключа; environment approval; owner bypass при создании тегов; full history; solo-review; расхождение `RELEASE_TAG_ALLOWED_SIGNERS` и `docs/release-signing/allowed_signers`.
- Installer: `realpath -m`/`mv -T`/`sort -z` на не-GNU платформах; внутренние симлинки и `.gitignore`d файлы при `--verify`; замена/бэкапы/частота обновлений.
- Validation/tests: edge cases Markdown/YAML/CSS-парсеров; flaky external links; асимметричное light/dark покрытие; secret-scan false positives; стоимость suite.
- CI: churn lockfile/actions; ширина allowlist; drift runner/toolchain; Node.js 22 EOL (2027-04-30); ручное отслеживание версий `gitleaks`; upstream Docker tag внутри `ossf/scorecard-action`.
- Skills/plan: фрагментация контекста и link churn; запас бюджета `new-page` 306 B; tokenizer vs bytes; drift плана; upstream licensing (`sickn33` без `LICENSE`-файла у импортированных навыков).

## Гипотезы (не задачи)

- Fork PR может не пройти `dependency-review` из-за `comment-summary-in-pr: always`; проверить контролируемым fork PR.
- CI wall-time: локальный `make check` ~22.6 s (в CI run `43946282578` job `validate` 61 s, шаг `make check` 17 s); детальный per-step breakdown на hosted не снят.
- CodeQL на docs-only PR может быть дорог (61 s в run `45199573587`); проверить `paths-ignore` без ослабления required checks.
- Токенизация references может отличаться от bytes/4; проверить tokenizer.
- Actions allowlist `verified_allowed` шире least privilege; сузить при необходимости.
- `require_extra_approval_for_unattributed_changes` при 0 approvals; проверить unverified email.
- name/ID portability вне OpenCode; проверить спецификации.
- «64 audited» provenance: fixture не содержит audit metadata.
- PR template relative link rendering (`../CONTRIBUTING.md` в `.github/PULL_REQUEST_TEMPLATE.md:32`); проверить GitHub UI (при правке синхронизировать `tests/test_validation.py:223`).
- Upstream licensing/text-copying (`sickn33/agentic-awesome-skills` исключает импортированные навыки, `ClawForge` без `LICENSE`-файла, `mobile-design` без записи в `docs/sources/sources.md`); нужен legal/maintainer review политики.
- Alternate `<name>.md` skill layout; проверить harness.
- **Аудит 2026-11-26:** Автоматический hot-reload при добавлении/замене каталога в `~/.config/opencode/skills/` и наличие недокументированного TUI-алиаса `/reload` в `opencode v2.4.1`; проверить в изолированном `opencode --standalone` через `opencode api get /api/skill` до и после `opencode reload`.
- **Аудит 2026-11-26:** Вызов `tools.opencode.session.move({ sessionID, directory })` для уже запущенного дочернего подагента (ставится ли в очередь до границы шага); проверить на тестовом git-репо в `/tmp/opencode/`.
- **Аудит 2026-11-26:** OpenCode V2 HTTP-каталоги навыков (`index.json`, same-origin) несовместимы с редиректами GitHub Releases и не имеют встроенной проверки подписи; проверить на изолированном инстансе, если когда-либо рассматривать публикацию каталога.
- **Аудит 2026-11-26:** Экспериментальный флаг `experimental.mcp_skills` в `opencode.ai/config.json:543`; не документирован, отслеживать в будущих релизах OpenCode.
- **Аудит 2026-11-26:** Поведение `install/opencode.sh` на stock macOS 13+ / BSD (где `/usr/bin/realpath` без `-m`, `mv` без `-T`); проверить на macOS-раннере или через stub `realpath` в `tests/test_installer.py`.
- **Аудит 2026-11-26:** Отменённый `workflow_dispatch`/scheduled прогон CodeQL (`concurrency: cancel-in-progress: true`) может получить более высокий `id`, чем зелёный `push`-прогон на том же SHA, и заблокировать `release_checks.py`; проверить на реальном NDJSON-выводе `commits/<sha>/check-runs`.
- **Аудит 2026-11-26:** Расхождение runtime YAML-парсера OpenCode V2 и PyYAML 1.1 (`validate.py`) на сложных `description` (экранирование, `>-`, multiline); проверить установкой тестового навыка в изолированный `XDG_CONFIG_HOME`.

## Владельцу / вне объёма

- Публичный `AGENTS.md` раскрывает локальные permissions/secret reads/`opencode-full`/MCP (`context7`, `gh_grep`, а в текущей сессии также `browse`); перенести детали в приватный supplement или обновить снимок среды. Это заметка владельцу, не задача.
- Глобальные permissions уже allow-all; `opencode-full` добавляет `--auto`. Если «только через обёртку» относится и к permissions — отдельное изменение пользовательской области.
- `opencode-full`, глобальные skills/MCP и их настройки существуют только у текущего пользователя; другие участники их не получат.
- `AGENTS.md §Оркестрация` от 2026-11-14 уже содержит `report` (исправлено в `6bec3ee`), но дата и состав MCP (`browse`) устарели; обновить вместе с `AUD-43` по решению владельца.
- Self-hosted раннеров нет; fork approval `all_external_contributors`; при добавлении нужен ответ владельца.
- **Аудит 2026-11-26:** Добавить `gitleaks` (`Secret Scan`, ~6 s) в обязательные проверки ruleset #27259237 (`main-protection`) как компенсирующий контроль при отключённых non-provider secret scanning (синхронно с `AUD-35`).
- **Аудит 2026-11-26:** Потолок OpenSSF Scorecard (сейчас 6.2/10) при solo-maintainer модели ограничен структурными нулями (`Maintained` <90 дней, `Code-Review`, `Contributors`, `Fuzzing`, `CII-Best-Practices`); наибольший технический прирост дадут `AUD-30` (`Pinned-Dependencies` 8→10) и `AUD-35` (`Signed-Releases` 0→8–10 на следующем релизе).
- **Аудит 2026-11-26:** Плановый горизонт инфраструктуры: Node.js 22 EOL наступает `2027-04-30` (миграция CI на Node.js 24 LTS заранее); версии `gitleaks` в `secret-scan.yml` отслеживаются вручную вне Dependabot; `ossf/scorecard-action` внутри `action.yaml` ссылается на Docker-тег, а не digest (отслеживать при апдейтах).
- **Аудит 2026-11-26:** Продуктовые решения на усмотрение владельца: (а) выделять ли `accessibility-engineering` в отдельный навык (как в `addyosmani/agent-skills` 0.6.17) или оставить в `frontend-design/references/accessibility.md`; (б) добавлять ли опциональный headless behavioral eval runner (`opencode run --standalone --archived --format json`).
- **Аудит 2026-11-26:** Историческая запись `CHANGELOG.md` (`v1.1.0`) не упоминала возврат загрузки SARIF Scorecard из `6bec3ee` (после отключения в `1.0.1`); прошлый changelog задним числом не переписывался.
- Claude Code/Codex не установлены; загрузка не проверялась.
- Второй maintainer нужен для approvals/code-owner review.
- Upstream-лицензии `sickn33` (`clean-code` / `mobile-design`, исключены из MIT/CC BY 4.0 репозитория) требуют подтверждения политики; `Leonxlnx/taste-skill` (MIT) и `anthropics/skills/skills/skill-creator` (Apache-2.0) подтверждены.

## Карта слияния ID

| Было | Стало | Причина |
|---|---|---|
| AUD-01, AUD-06, AUD-09 | AUD-01 | один release pipeline: gate, notes, provenance |
| AUD-02, AUD-03, installer tests из AUD-11 | AUD-02 | один installer: безопасность, trust, проверка |
| AUD-11, AUD-16, AUD-17 | AUD-03 | одна validation correctness: false greens, parser, tokens |
| AUD-05, AUD-08, AUD-10, AUD-20 | AUD-04 | один CI/toolchain/workflow contract |
| AUD-04 | AUD-05 | secret handling |
| AUD-07, AUD-14, AUD-18, AUD-19 | AUD-06 | один skill content/instruction budget |
| AUD-12, AUD-13, AUD-21 | AUD-07 | repository protections и evidence |
| AUD-15 | DONE | документы уже исправлены |

## Что свёрнуто и почему

| Было | Стало | Причина |
|---|---|---|
| Подробные evidence-блоки AUD-01…AUD-07 | Компактные DONE-записи с путями доказательств | Работа завершена; evidence сохранён, narrative не нужен для следующей задачи |
| Подробные блоки SKL-01…SKL-09 и ORC-01 | Компактные DONE-записи | Завершено; канонические инструкции — в `skills/` |
| `AUD-28` как открытая задача | DONE-запись | Этот проход выполнил её приёмку: план сжат, #47 закрывается |
| `AUD-15` narrative | DONE-запись | Исправление уже влито; residual AUD-20 остаётся в AUD-04 |
| Два раздела аудита (`Аудит 2026-11-15`, `… повторный`) | Один раздел «Аудит: охват и ограничения» | Дублируют охват/limits; findings остаются отдельными ID |
| `Выполнено`, `Гипотезы`, `Владельцу` | Компактные разделы | Один факт — одно место; все ID/решения/риски сохранены |
| `Карта слияния ID` | Без изменений | Исторические ID нужны для трассировки |

Удалено только доказанно лишнее: повторяющиеся evidence-абзацы завершённых задач, дублирующие summaries и narrative, уже перенесённые в код/документы. Ни один ID, статус, зависимость, риск, решение владельца или условие BLOCKED не потерян; открытые задачи сохранены.

# План

Трекер: https://github.com/snaplyze/skills-hub/issues; сверено 2026-11-27; этапы 01–10; веха #10 «10 — Antigravity support»: `AGY-01` #99 (`DONE`, PR #104), `AGY-02` #100 (`DONE`, PR #104), `AGY-03` #101 (`DONE`, PR #105), `AGY-04` #102 и `AGY-05` #103 (закрываются PR #106 с последующим закрытием вехи #10); закрытые этапы 01–09: #14–#20, #27–#35, #38, #41–#48, #54, #58–#61, #63, #68–#82, #84. Реестр — этот файл; owner-facing, на русском, не загружается как инструкции агентов.

## Документы и стартовый контекст

| Документ | Роль | Строк / байт |
|---|---|---|
| `AGENTS.md` | сведения о проекте и стартовый контекст | 48 / 8 485 |
| `docs/plan.md` | единый реестр плана (обновляется на месте) | — |
| `README.md` | вход, установка (Antigravity + OpenCode), защиты | 377 / 24 276 |
| `docs/antigravity-orchestration.md` | архитектура нативной оркестрации Antigravity | 108 / 8 948 |
| `docs/opencode-orchestration.md` | архитектура native orchestration OpenCode | 81 / 5 307 |
| `docs/release-process.md` | релизный гейт и owner setup | 283 / 13 152 |
| `docs/repository-settings.md` | settings evidence (сверено 2026-11-26) | 75 / 5 000 |
| `docs/release-signing/` | публичный SSH trust и ротация | 44 / 1 965 |
| `CONTRIBUTING.md`, `GOVERNANCE.md`, `SECURITY.md`, `CHANGELOG.md` | правила, безопасность, история релизов | 511 / 23 472 |
| `THIRD_PARTY_NOTICES.md` | атрибуция workflow-навыков и указатель `sources.md` | 53 / 3 444 |
| `docs/plans/2026-11-16-skill-suite-v2.md` | завершённый детальный план этапа 08 | 281 / 10 726 |
| `docs/plans/2026-11-27-antigravity-support.md` | детальный план этапа 10 (поддержка Antigravity) | 153 / 11 923 |

План не входит в бюджет загружаемых инструкций 32 KiB.

## Этапы

Порядок этапов: `01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10`.

| # | Веха трекера | Статус | Задачи |
|---|---|---|---|
| 01 | `01 — Release, installer, validation` (#1) | closed | `AUD-01` #14, `AUD-02` #15, `AUD-03` #16 |
| 02 | `02 — CI, secrets, content` (#2) | closed | `AUD-04` #17, `AUD-05` #18, `AUD-06` #19 |
| 03 | `03 — Protections` (#3) | closed | `AUD-07` #20 |
| 04 | `04 — Agent workflow skills` (#4) | closed | `SKL-01` #27, `SKL-02` #28, `SKL-03` #29 |
| 05 | `05 — Quality and delivery skills` (#5) | closed | `SKL-04` #30, `SKL-05` #31, `SKL-06` #32, `SKL-07` #33, `SKL-08` #34, `SKL-09` #35 |
| 06 | `06 — Native orchestration` (#6) | closed | `ORC-01` #38 |
| 07 | `07 — Audit 2026-11-15` (#7) | closed | `AUD-22`–`AUD-29` (#41–#48) |
| 08 | `08 — Skill suite v2` (#8) | closed | `SKL2-01`–`SKL2-04` (#58–#61), closeout #63 |
| 09 | `Аудит 2026-11-26` (#9) | closed | 0 OPEN, 15 DONE (`AUD-30` #69–`AUD-43` #82, `AUD-44` #84) |
| 10 | `10 — Antigravity support` (#10) | closing | `AGY-01` #99 (`DONE`), `AGY-02` #100 (`DONE`), `AGY-03` #101 (`DONE`), `AGY-04` #102 (PR #106), `AGY-05` #103 (PR #106) |

## Этап 10 — Поддержка Google Antigravity (2026-11-27)

- **Основание и источники:** поручение владельца (добавить поддержку Google Antigravity наряду с OpenCode, убрать OpenCode-специфичные описания из `skills/` и унифицировать их под стандарт Agent Skills, задействовать нативную оркестрацию Antigravity); официальная документация `antigravity.google/docs/*` (`skills`, `rules`, `customization-discovery`, `subagents`, `dynamic-workflows`, `swarm`, `teamwork`, `plan`, `browser`, `plugins`, `build-plugins`, `cli/headless`, `cli/modes`, `cli/reference`), стандарт `agentskills.io/specification` и живая проверка через `agy 1.5.18` (`agy plugin validate --json`).
- **Детальный план и журнал исполнения:** [`docs/plans/2026-11-27-antigravity-support.md`](plans/2026-11-27-antigravity-support.md).
- **Порядок исполнения (DAG):** Волна 1 (`AGY-01` #99 + `AGY-02` #100, PR #104 `67c14fa`) → Волна 2 (`AGY-03` #101, PR #105 `f6277cc`) → Волна 3 (`AGY-04` #102 + `AGY-05` #103, PR #106).
- **Задачи этапа 10:**
  - `AGY-01` ([#99](https://github.com/snaplyze/skills-hub/issues/99), `DONE`, PR #104 `67c14fa`): строгий `name == skill_dir.name` (lowercase kebab-case, 1–64 символа), единая `compatibility: agentskills` (≤ 500 символов), `allowed-tools` и `dict[str, str]`-проверка `metadata` с сохранением OpenCode V2 `metadata.opencode/autoinvoke` в `scripts/validate.py` и `tests/test_validation.py`; эмпирически проверено `agy plugin validate --json` — 11/11 навыков, 0 ошибок и 0 предупреждений.
  - `AGY-02` ([#100](https://github.com/snaplyze/skills-hub/issues/100), `DONE`, PR #104 `67c14fa`): удалены все OpenCode-специфичные термины из `skills/**/*.md`, все 11 навыков унифицированы и адаптированы под нативную оркестрацию Antigravity (`invoke_subagent`, `define_subagent` с учётом no-shell при `EnableWriteTools: false`, `send_message`, `manage_subagents`, встроенные `research`/`browser`/`self`, изоляция `branch`/`share`, `run_workflow`, пользовательские `/swarm`/`/boost`/`/teamwork`, `/browser`, `/diff`, `/compact`, `/boost`, headless `agy -p ... --output-format json`), добавлен `docs/antigravity-orchestration.md` рядом с `docs/opencode-orchestration.md`, расширены регрессионные проверки `tests/test_skill_suite.py`; независимое ревью `readonly-reviewer` (2 P1 + 3 P2 исправлены, перепроверка `ZERO FINDINGS`).
  - `AGY-03` ([#101](https://github.com/snaplyze/skills-hub/issues/101), `DONE`, PR #105 `f6277cc`): добавлен `install/antigravity.sh` (`$HOME/.gemini/config/skills`, игнорирует `XDG_CONFIG_HOME`, подсказка `/skills reload`) рядом с `install/opencode.sh`, общее ядро вынесено в `install/lib.sh` с проверкой симлинков; добавлены `.gemini/` в `.gitignore`, исключение `.gemini` в обоих установщиках, запрет симлинков каталога `install/` в `scripts/validate.py`, двойные `shellcheck -x` / `dry-run` в `Makefile` и расширенные тесты (`test_installer.py`, `test_release_assets.py`, `test_secrets.py`, `test_validation.py`); независимое ревью `readonly-reviewer` (0 P0/P1, 3 кодовых P2 исправлены в PR #105, P2-4 по `CONTRIBUTING.md` — в PR #106).
  - `AGY-04` ([#102](https://github.com/snaplyze/skills-hub/issues/102), PR #106): обновлены `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `THIRD_PARTY_NOTICES.md`, `docs/release-process.md`, `CHANGELOG.md` (`## [Unreleased]`), `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/PULL_REQUEST_TEMPLATE.md` и `docs/antigravity-orchestration.md` под совместную поддержку Antigravity и OpenCode; независимое ревью `readonly-reviewer` (1 P1 + 3 P2 исправлены).
  - `AGY-05` ([#103](https://github.com/snaplyze/skills-hub/issues/103), PR #106): синхронизация `docs/plan.md` и `docs/plans/2026-11-27-antigravity-support.md`, сквозная проверка `make check` PASS (343 теста) и `agy plugin validate --json` PASS (11/11, 0 ошибок/предупреждений); `make links` `NOT_TESTED` локально из-за fake-IP `198.18.0.0/15` (подмена: `curl` HTTP 200 на все 3 новых URL; `Link Audit` работает на hosted CI); закрытие вехи #10 после слияния PR #106. Релизный тег не создаётся без отдельного поручения владельца.

## Аудит 2026-11-26

- **Метаданные:** дата `2026-11-26`, база аудита `5f0a620` (упорядочивание плана на базе `28465f1`), репозиторий и трекер публичные (`snaplyze/skills-hub`; по правилу 14 детали неустранённых уязвимостей не публикуются — удалённо эксплуатируемых не выявлено).
- **Охват:** 7 областей + OpenCode V2 (`opencode v2.4.1`, `opencode.ai/docs/`, `opencode debug agents --standalone`) + 11 upstream-репозиториев. Снимок `5f0a620`: `validate` PASS (0.335 s, 11 навыков), `ruff`/`markdownlint`/`shellcheck`/`dry-run`/`css`/`workflows --strict` PASS, `make links` PASS (53/53, 32.6 s), `pytest` в git-checkout PASS (21.63 s, 202 теста), в не-git снимке падает `test_current_head_archive_contains_all_skills` и skip 2 теста подписи.
- **Прямые документальные правки (PR #83 / #68, описание исправлено без изменения продукта):** `docs/release-process.md`, `CONTRIBUTING.md`, `THIRD_PARTY_NOTICES.md`, `README.md`, `SECURITY.md`, `docs/release-signing/README.md`, `docs/repository-settings.md`. Не менялись: код, тесты, `skills/*`, CI/YAML, `AGENTS.md`, `CHANGELOG.md`.
- **Исполнитель и статус очереди:** исполнитель по открытым задачам — **не назначен** (кроме `AUD-42` — **владелец**); `BLOCKED`: нет (`AUD-42` требует отдельного поручения владельца на публикацию релиза); неудачные попытки: нет. Review-gate обязателен на каждой задаче.
- **Порядок исполнения (DAG):** Волна 1: `AUD-30`, `AUD-31`, `AUD-32` → Волна 2: `AUD-33`, `AUD-34`, `AUD-35`, `AUD-38`, `AUD-43` → Волна 3: `AUD-44`, `AUD-37`, `AUD-39` → Волна 4: `AUD-36` → Волна 5: `AUD-40` → Финал (владелец): `AUD-42`.

### Статус областей

| Область | Статус | Ограничения охвата |
|---|---|---|
| Архитектура | проверено | Полный разбор `scripts/`, `install/opencode.sh`, 11 навыков, дублей проверок, OpenCode V2 и 11 upstreams. |
| Безопасность | частично | Без контролируемого fork PR, live dispatch `release.yml`, destructive install и legal review `sickn33`. |
| Данные | проверено | YAML frontmatter, Markdown links/anchors, `reading-sets.json`, `tokens.css`, contrast fixture, `CHANGELOG.md`, JSONL check-runs. |
| Производительность | частично | Замерены продукт, валидация, тесты и scaling в снимке; без реального токенайзера и нового hosted per-step профиля. |
| Тесты | проверено | Все 12 тестовых модулей (132 функции / 202 кейса), хрупкость, дубли, поведение в `git archive`. |
| Сборка и доставка | частично | Без нового `workflow_dispatch` релиза и проверки установщика на macOS/BSD. |
| Документация | проверено | Все 18 документов/шаблонов сверены с кодом, `wc -l -c` и живым GitHub API. |

### Ближайшие задачи (P1 — детально)

#### AUD-30 — Code Scanning alert #13 (`pip==26.3`) and `check_workflows.py` policy bypasses

- `DONE` · Аудит 2026-11-26 · `ci/security/duplication` · **P1 (высокий ущерб):** открытый Code Scanning `error` alert и обходы CI-гейта безопасности · уверенность: высокая · [#69](https://github.com/snaplyze/skills-hub/issues/69) (веха #9) · исполнитель: агент · deps: none.
- **Результат / границы:** удалить unhashed `pip==26.3`, закрыть обходы в `scripts/check_workflows.py`, убрать дубль проверки workflows в `scripts/validate.py`, сузить `permissions` в `scorecard.yml`. Продуктовые навыки и настройки аккаунта не меняются.
- **Доказательство:** (1) Code Scanning `alerts/13` (`open`, `Scorecard/PinnedDependenciesID`, `error`) на `.github/workflows/ci.yml:48` (no-op под `setup-python@v7.1.0`, расходится с `Makefile:25-27`, роняет `Pinned-Dependencies` 10→8); (2) `scripts/check_workflows.py:124-129` (`find`) берёт первый дубликат ключа YAML, хотя Actions применяет последний; `:320` не отклоняет `<<: *alias`; `:164-165` регистрозависим к `Actions/Checkout`; `:190-200, 242-248, 265, 300-314` пропускают `permissions: [write-all]`, `read-all`, `on: []`, `jobs: {}`, `1_0`, `uses`+`steps`, `${{ }}` в `run:`, `runs-on` (`self-hosted`/`ubuntu-latest`) и write-права в `pull_request`-workflows; (3) `.github/workflows/scorecard.yml:12` использует `permissions: read-all`; (4) *шаг 5 (дубль):* `scripts/validate.py:878-897` повторно парсит `workflows/` через YAML 1.1 `safe_load` (`true:` проходит как `on:`); инвариант (валидный mapping с `name`/`on`/`jobs` и политикой) на неизменном git-дереве в одном процессе уже гарантирует `check_workflows.py` после переноса проверки `"name"`.
- **Влияние:** открытый security-alert, риск обхода правил CI (включая правила 20–21), двойной разбор workflows.
- **Решение:** удалить `ci.yml:48`; ужесточить `check_workflows.py` (запрет дублей ключей и `<<`, lower-case `actions/checkout`, строгие типы узлов, запрет `read-all`, проверка `"name"`, `${{ }}` в `run:`, `runs-on`, write-прав на `pull_request`); удалить `validate.py:887-896` и пропускать `workflows/` в `check_yaml`; в `scorecard.yml` поставить `permissions: {}` + `if: always()` + default-branch guard. Трудоёмкость: 1.5–2 ч; риски: низкие.
- **Приёмка:** негативные тесты в `tests/test_workflows.py` ловят все обходы; `make check` PASS; после слияния на `main` очередной Scorecard закрывает alert #13.
- **Текущая запись:** статус `DONE`; удалён unhashed `pip==26.3` из `ci.yml`, `scorecard.yml` переведён на `permissions: {}` + default-branch guard + `!cancelled() && hashFiles('results.sarif') != ''`, усилен `scripts/check_workflows.py` (циклические/DAG YAML-алиасы, case-insensitive дубли/`<<`, сегменты `.`/`..` и регистр `actions/checkout`, строгие типы, запрет `read-all`/`${{ }}` в `run:`/`self-hosted`/untrusted-event write, проверка `name`, `main(argv)`), удалён дубль workflows в `validate.py:check_yaml`; проверка: `make check` PASS; закрывает #69; неудачных попыток: нет.

#### AUD-31 — Support OpenCode V2 frontmatter fields (`metadata`, `disable-model-invocation`) and strict YAML

- `DONE` · Аудит 2026-11-26 · `compatibility/validator` · **P1 (высокий ущерб):** валидатор отвергает официальные поля OpenCode V2 и противоречит `skill-authoring:101` · уверенность: высокая · [#70](https://github.com/snaplyze/skills-hub/issues/70) (веха #9) · исполнитель: агент · deps: none.
- **Результат / границы:** типобезопасная поддержка `metadata` (`opencode/autoinvoke`), `disable-model-invocation`, `compatibility` и запрет дублей ключей в `scripts/validate.py`; синхронизация `skill-authoring`, `README.md`, `CONTRIBUTING.md`.
- **Доказательство:** OpenCode V2 (`opencode.ai/docs/skills/#frontmatter`) задаёт `metadata.opencode/autoinvoke` и `disable-model-invocation`; `scripts/validate.py:42, 443-451` отклоняет их и не проверяет тип `compatibility` (`null`/`[]` проходят); `skills/skill-authoring/SKILL.md:101` требует версионирование в `skill metadata`; `validate.py:227-237` (`parse_frontmatter`) молча принимает дубли YAML-ключей (конфликт с `install/opencode.sh:177`) и падает на CRLF / `---` в EOF.
- **Влияние:** нельзя версионировать навыки в `metadata` и использовать V2 manual-only opt-out; скрытые дубли ключей.
- **Решение:** расширить `ALLOWED_FRONTMATTER_KEYS`; проверить типы `compatibility` (непустая `str`), `disable-model-invocation` (`bool`), `metadata` (`dict`, `opencode/autoinvoke` `bool`, проверка конфликта флагов); запретить дубликаты ключей в `parse_frontmatter` через строгий `SafeLoader` и поддержать EOF `---`; обновить `skills/skill-authoring/SKILL.md:30-38`, `README.md:316`, `CONTRIBUTING.md:73`. Трудоёмкость: 1–1.5 ч; риски: низкие.
- **Приёмка:** позитивные и негативные тесты в `tests/test_validation.py` PASS; `make check` PASS.
- **Текущая запись:** статус `DONE`; расширен `ALLOWED_FRONTMATTER_KEYS`, добавлен `UniqueKeySafeLoader` и проверка типов `compatibility`/`metadata`/`disable-model-invocation`, обновлены `skills/skill-authoring/SKILL.md`, `README.md`, `CONTRIBUTING.md`; проверка: `make check` PASS; закрывает #70; неудачных попыток: нет.

#### AUD-32 — Align orchestration, planning, execution, delivery skills and `docs/opencode-orchestration.md` with OpenCode V2

- `DONE` · Аудит 2026-11-26 · `compatibility/architecture/skill-content` · **P1 (высокий ущерб):** прямые конфликты с правами `plan`/`explore`/`general` и асинхронным `subagent` в OpenCode `v2.4.1` · уверенность: высокая · [#71](https://github.com/snaplyze/skills-hub/issues/71) (веха #9) · исполнитель: агент · deps: none.
- **Результат / границы:** переносимые Markdown-обновления 6 навыков (`implementation-planning`, `specification`, `orchestration`, `autonomous-execution`, `code-review`, `delivery`) и `docs/opencode-orchestration.md` под V2 без плагинов/хуков и упоминаний `opencode.json` в `SKILL.md`.
- **Доказательство:** `opencode.ai/docs/` + `opencode debug agents --standalone` (`v2.4.1`): `plan` запрещает `edit: *` кроме `~/.opencode/plan/*` (бьёт по `implementation-planning/SKILL.md:40` и `specification/SKILL.md:27`); `subagent` всегда фоновый с `sessionID`/`<background-result>` и TUI cancel (`ctrl+d`); `explore` запрещает `skill`/`question`, но разрешает `shell` и `external_directory`; `general` запрещает `question`/`subagent` и разрешает `external_directory`; `session.move` вступает в силу на следующей безопасной границе, `worktree_remove` требует подтверждения для `force`. Upstream-уроки: brief-bounded вместо `maxTurns` + partial handoff (`claude-orchestration` `1c71ec2e0df0`), запрет `question` подагентам + прямой multimodal read (`oh-my-opencode-slim` `#1631`, `a052f07a990c`), CWD-безопасный `git worktree remove` + detached HEAD (`superpowers` `22f0b463e7a5`). Расхождения в `docs/opencode-orchestration.md:15,25,68-70` и `SKILL.md` указанных навыков.
- **Влияние:** permission deny в `plan`, polling/sleep циклы, сбои `explore`/`question`, запись вне репо, поломка CWD при удалении worktree, неточная документация.
- **Решение:** read-only fallback для `plan`-режима без обхода через `shell`; асинхронный протокол (yield без sleep/poll, `sessionID` vs свежий child, границы `explore`/`general`/worktree, brief-bounded + partial handoff, прямой multimodal read); обновление worktree-шагов (`session.move` отдельным шагом, `cd` в корень репо до remove, detached HEAD); правка `docs/opencode-orchestration.md`. Трудоёмкость: 2–3 ч; риски: низкие (сохранить контракты `tests/test_skill_suite.py`).
- **Приёмка:** все `SKILL.md` ≤32 KiB; `tests/test_skill_suite.py` и `make check` PASS; `docs/opencode-orchestration.md` соответствует `opencode v2.4.1`.
- **Текущая запись:** статус `DONE`; обновлены `specification`, `implementation-planning`, `orchestration`, `autonomous-execution`, `code-review`, `delivery` и `docs/opencode-orchestration.md` под асинхронный `subagent`, права `plan`/`explore`/`general`, нативные worktree/`session.move` и CWD/detached-HEAD; проверка: `make check` PASS; закрывает #71; неудачных попыток: нет.

#### AUD-33 — Harden `scripts/validate.py` path containment, link/GFM parsing, `docs/**` recursion, and generic reading-sets

- `DONE` · Аудит 2026-11-26 · `security/validator/architecture` · **P1 (высокий ущерб):** пробелы изоляции путей, пропуск битых ссылок в бейджах и `docs/**`, блок на добавление `references/` во 2-й навык · уверенность: высокая · [#72](https://github.com/snaplyze/skills-hub/issues/72) (веха #9) · исполнитель: агент · deps: `AUD-31`.
- **Результат / границы:** строгий containment ссылок/путей в `scripts/validate.py`, вложенные image-links, рекурсивный `docs/**/*.md`, общий контракт `reading-sets.json` и корректный CommonMark/GFM-парсер (без оптимизации рантайма — она в `AUD-44`).
- **Доказательство:** `validate.py:201-210` не проверяет `is_relative_to(ROOT)` на относительных ссылках и пропускает ссылки из `skills/<id>/` наружу (`/README.md`, `../other-skill/`); `:350-356, 395-398` пропускает абсолютные и `..` пути в `reading-sets.json`; `:414-415` требует `new-page` для любого навыка с `references/` и игнорирует `limit_bytes`, а `:240-288` держит 49-строчный неиспользуемый адаптер; `:56-62, 173-180` отбрасывает `[![...](img)](target)` (`README.md:3-8`); `:867-868` не рекурсивен (`docs.glob`); не запрещены симлинки в `skills/`; `LOCAL_REF_RE` сканирует только `SKILL.md`; роутинг допускает bare basename; неиспользуемые `[dead]: missing.md` не проверяются; `mask_html_comments` идёт до `mask_inline_code`; расхождения fence/GFM `slug()` (`_`, `--`, коллизия `foo-1`).
- **Влияние:** битые ссылки в бейджах и вложенных `docs/`, непереносимые ссылки и обход путей проходят CI; нельзя добавить `references/` в 10 workflow-навыков.
- **Решение:** `is_relative_to(ROOT)` для всех ссылок и `is_relative_to(skill_dir)` внутри `skills/` и `reading-sets.json` (убрать fallback `ROOT / relative`); запретить симлинки в `skills/`; ограничить `new-page` навыком `frontend-design`, проверять `SKILL.md` и `1 <= limit_bytes <= 32768`, упростить `reading_set_entries()`, добавить контроль суммарных байт frontmatter-описаний (сейчас 3 685 B) и описать `reading-sets.json` в `skill-authoring`; поддержать `[![...](...)](...)`, `docs.rglob("*.md")`, все `definitions`, `LOCAL_REF_RE` по всем `.md` навыка, точный `routing_path`, единый CommonMark/GFM парсер. Трудоёмкость: 2.5–3.5 ч; риски: низкие (обновить `test_validation.py:114`).
- **Приёмка:** негативные тесты на каждый дефект и 2-й навык с `references/` без `new-page` PASS; `make check` PASS.
- **Текущая запись:** статус `DONE`; реализован containment путей (`ROOT` и `skill_dir`), запрет симлинков в `skills/`, вложенный сканер image-links, `docs.rglob("*.md")`, общий контракт `reading-sets.json` (`new-page` только для `frontend-design`, `limit_bytes`, `SKILL.md` обязателен), агрегатный лимит описаний и CommonMark/GFM парсер; проверка: `make check` PASS; закрывает #72; неудачных попыток: нет.

#### AUD-44 — Deduplicate `scripts/validate.py` runtime passes and in-process `contrast` checks

- `DONE` · Аудит 2026-11-26 · `performance/validation/duplication` · **P1 (высокий ущерб):** 57.1% времени `validate.py` уходит на 2 лишних подпроцесса при уже импортированном `contrast` и повторные проходы по файлам (выделено из `AUD-36` по правилу разделения оптимизаций) · уверенность: высокая · [#84](https://github.com/snaplyze/skills-hub/issues/84) (веха #9) · исполнитель: агент · deps: `AUD-30`, `AUD-33`.
- **Результат / границы:** один проход на файл/токен и in-process проверки в `scripts/validate.py` + параметризованный entrypoint `validate_repo(root)` для тестов (сами тесты не оптимизируются — это `AUD-36`).
- **Доказательство (шаг 5):** `validate.py:815-849` импортирует `contrast`, но спавнит 2 подпроцесса (`--self-test`, `--pairs`), парсит `tokens.css` дважды (`:685-686`), обходит 64 пары дважды (`:620-727`) и содержит мёртвый код `:639-641`; `SKILL.md` читается 3 раза (`:438, 472, 482`), `markdown_headings` не кэшируется (`:222`), дублируются проверка роутинга (`:378` vs `:468`) и `READING_SET_NEW_PAGE_LIMIT` (`:44, 416-421`). *Инвариант:* все проверки ссылок, reading sets, 64 пар + 26 комбинаций WCAG 2.2 AA и `contrast.self_test()` сохраняются на неизменяемых данных в одном процессе (CLI проверяет `test_contrast_cli.py`).
- **Производительность (шаг 4):** путь и нагрузка — `scripts/validate.py` на текущем репо (11 навыков, 64+26 пар, 40 `.md`); базовый замер (`5f0a620`, B-04) — CLI 335 ms, in-process 141.7 ms (`check_contrast` 80.9 ms = 57.1%); целевой предел — из требований владельца `make validate ≤1 s` (более жёсткий порог — цель не задана: нужно решение владельца); сравнение — пофазный замер B-04 и CLI в неизменяемом снимке до/после; удаляется — 2 подпроцесса `contrast.py` (`:837-848`), второй парс `tokens.css`, второй цикл `pairs`, dead code `:639-641`, `READING_SET_NEW_PAGE_LIMIT`, дубль роутинга, повторные чтения `SKILL.md`.
- **Решение:** единый `decls = css_declarations(...)`, слияние циклов `pairs` с `contrast.check_pair()` и `contrast.self_test()` in-process, `preprocess_markdown()` + `heading_cache` per `Path`, параметризация `validate_repo(root)` без мутации глобального `ROOT`. Трудоёмкость: 1.5–2 ч; риски: низкие.
- **Приёмка:** сравнение B-04 до/после подтверждает снижение времени без потери проверок; `make check` PASS.
- **Текущая запись:** статус `DONE`; замер до/после на снимке `f0c387a`: in-process `189.96 ms → 73.03 ms` (`2.6×`, `check_contrast` `68.20 ms → 3.45 ms` = `19.8×`, `check_skills` `68.14 → 36.68 ms`, `check_root_docs` `42.91 → 22.02 ms`), CLI медиана `248.9 ms → 161.2 ms` (min `133.2 ms`); удалены 2 подпроцесса `contrast`, дублирующие парсы/роутинг/`READING_SET_NEW_PAGE_LIMIT`/dead code, добавлен `validate_repo(root)` и `heading_cache`; проверка: `make check` PASS; закрывает #84; неудачных попыток: нет.

#### AUD-36 — Eliminate `node_modules` copy amplification (8.0 s) and subprocess fan-out in `tests/`

- `DONE` · Аудит 2026-11-26 · `performance/tests` · **P1 (высокий ущерб):** 27.7× лишнего I/O (~764 MB / 91k файлов) и >320 подпроцессов на каждый `make check` (сужено до стоимости `tests/`; оптимизация `validate.py` вынесена в `AUD-44`) · уверенность: высокая · [#75](https://github.com/snaplyze/skills-hub/issues/75) (веха #9) · исполнитель: агент · deps: `AUD-30`, `AUD-44`.
- **Результат / границы:** быстрый `pytest` без копирования `node_modules`/`.venv` и лишних подпроцессов при полном сохранении покрытия, мутационной чувствительности и 1–2 CLI smoke-тестов на скрипт. Продукт и `validate.py` не меняются.
- **Доказательство:** `tests/test_validation.py:12-25` (`IGNORE`) пропускает `node_modules` (1 990 файлов / 16.8 MB) и `.venv` → 44 копии = 91 256 файлов / ~764 MB + ~182 подпроцесса (`test_validation.py` = 15.82 s из 21.63 s); fan-out в `test_secrets.py` (51 `git`), `test_contrast_cli.py` (22 Python), `test_workflows.py` (21 Python; `check_workflows.main()` без `argv`), `test_installer.py` (28 `git`), `test_release_notes.py` (5 Python + мутация `sys.path:13`); холостые/дублирующие тесты (`test_validation.py:295-296, 442-448, 521-528`, `test_workflows.py:265-272`) и утечка сокета `httpd.server_close()` (`test_external_links.py:56`).
- **Производительность (шаг 4):** путь и нагрузка — `pytest` (202 теста в 12 модулях); инварианты — все граничные/мутационные кейсы и CLI exit-code контракты сохранены; базовый замер (`5f0a620`, B-09/B-11) — `pytest` 21.63 s (`make check` 22.6 s), `copy_repo` 44× 8.30 s с `node_modules` vs 0.30 s без него, `check_workflows` 21× 1 225.8 ms vs 407.0 ms in-process; целевой предел — из требований владельца `make check ≤30 s` (более жёсткий порог для `pytest` — цель не задана: нужно решение владельца); сравнение — `pytest --durations=25`, per-file тайминги и B-09/B-11 в снимке до/после; удаляется — копирование `node_modules`/`.venv`/`.mypy_cache`/`*.pyc`, ~250+ лишних подпроцессов, дубль прогона `:295-296`, no-op `:442-448`, дубль `.yml` `:265-272`, `sys.path` мутация.
- **Решение:** расширить `IGNORE`; перевести unit-мутации `test_validation.py`, `test_workflows.py` (добавив `argv` в `check_workflows.main`), `test_contrast_cli.py`, `test_release_notes.py` в in-process; батчировать `git check-ignore --stdin` в `test_secrets.py` и шаблонный git-репо в `test_installer.py`; очистить холостые тесты и закрывать `httpd.server_close()`. Трудоёмкость: 2–3 ч; риски: низкие.
- **Приёмка:** сравнение до/после в снимке подтверждает ускорение `pytest`; все 202+ кейсов и мутации сохранены; `make check` PASS.
- **Текущая запись:** статус `DONE`; замер до/после на `83e4e99`: полный `pytest` `23.65 s → 9.35 s` (`2.5×`, 272 теста; `test_validation.py` `18.13 → 5.49 s`, `test_workflows.py` `2.31 → 0.39 s`, `test_secrets.py` `1.48 → 0.27 s`, `test_contrast_cli.py` `0.85 → 0.29 s`, `test_installer.py` `3.34 → 2.12 s`); исключены `node_modules`/`.venv`/`.mypy_cache`/`*.pyc`, сохранён CLI smoke на каждый скрипт, удалены холостые дубли, добавлен `httpd.server_close()`; проверка: `make check` PASS; закрывает #75; неудачных попыток: нет.

#### AUD-34 — Fix `install/opencode.sh` YAML parser, symlink/`--verify` hygiene, reload hint, CLI edge cases, and scaling

- `DONE` · Аудит 2026-11-26 · `security/installer/performance` · **P1 (высокий ущерб):** живой баг вывода `--list`, пропуск `.gitignore`d секретов при `--verify` и копирование внутренних симлинков · уверенность: высокая · [#73](https://github.com/snaplyze/skills-hub/issues/73) (веха #9) · исполнитель: агент · deps: `AUD-31`.
- **Результат / границы:** консистентный, безопасный и масштабируемый `install/opencode.sh` + актуальная подсказка reload в `README.md:146` и расширенные тесты `tests/test_installer.py`.
- **Доказательство:** живой `./install/opencode.sh --list` печатает сырые кавычки у `frontend-design` и `test-driven-development` (`read_description` `:128-184` также ломает `""`, multiline/block scalars и берёт первый дубликат ключа); `copy_skill_tree` (`:195-196`) копирует внутренние симлинки дословно; `verify_source` (`:225`) без `--ignored` + лишь 9 исключений (`:205-210`) копируют `.gitignore`d `.env`/`*.key` при `--verify`; `:542` и `README.md:146` просят перезапуск сессии/`/reload` вместо V2 live-reload / `opencode reload`; `:87-92, 214-250, 296-306, 358, 360-471` не проверяют `-m`/`-T`/`-z`/`git`, `--list` падает без `HOME` и игнорирует `--verify`, `--all` игнорирует позиционные аргументы, дубликаты аргументов ломают установку, multi-tag без `--sort=-v:refname`, нет signal-restore бэкапа.
- **Производительность (шаг 4, продукт):** путь и нагрузка — `install/opencode.sh:copy_skill_tree` на 11–61 навыках (39–1 089 файлов); инварианты — newline-safe имена, исключение кэш/секретов, запрет внутренних симлинков, атомарная замена и бэкапы; базовый замер (`5f0a620`, B-03) — 285 ms (11/39) → 1 716 ms (31/459) → 3 886 ms (61/1 089); целевой предел — цель не задана: нужно решение владельца; сравнение — B-03 до/после в снимке; удаляется — per-file `cp`/`mkdir`/`ln` цикл и лишние `basename`.
- **Решение:** починить `read_description` (или `python3`+PyYAML с Bash-fallback); запретить внутренние симлинки; при `--verify` проверять `--ignored` в `skills/` или копировать из `git archive HEAD` + добавить секретные исключения в `copy_skill_tree`; перейти на потоковый `tar`; проверять GNU-флаги/`git`, починить `--list`/`--all`/дедупликацию/pre-flight/signal-restore; обновить reload в `opencode.sh:542` и `README.md:146`; закрыть пробелы `tests/test_installer.py`. Трудоёмкость: 3–4 ч; риски: средние (сохранить переносимость и 21 текущий тест).
- **Приёмка:** `--list` без лишних кавычек; внутренний симлинк и `.env` отклоняются; B-03 быстрее на 61 навыке; `shellcheck` и `make check` PASS.
- **Текущая запись:** статус `DONE`; починен `read_description` (кавычки/escape/`""`/multiline/block/`#`/CRLF), запрещены внутренние симлинки, добавлены секретные исключения и `git archive` + проверка `--ignored` при `--verify`, потоковый `tar --verbatim-files-from` (замер B-03 на 61 навыке: `6 104 ms → 2 049 ms`, `3.0×`), GNU-пробы, `--list` без `HOME` с `--verify`, запрет `--all`+args, дедупликация, signal-restore бэкапа, V2 reload в `opencode.sh`/`README.md`; проверка: `shellcheck` и `make check` PASS; закрывает #73; неудачных попыток: нет.

#### AUD-35 — Harden release gate (`release.yml`, `release_checks.py`, `release_notes.py`) and attach Sigstore asset

- `DONE` · Аудит 2026-11-26 · `security/release` · **P1 (высокий ущерб):** самый привилегированный workflow; check-run shadowing, запуск скрипта из tag-checkout и Scorecard `Signed-Releases: 0/10` · уверенность: высокая · [#74](https://github.com/snaplyze/skills-hub/issues/74) (веха #9) · исполнитель: агент · deps: `AUD-30`.
- **Результат / границы:** защищённый релизный гейт (`release.yml`, `release_checks.py`, `release_notes.py`) с Sigstore-артефактом. Ruleset #27259237 меняет только владелец.
- **Доказательство:** `scripts/release_checks.py:27-72` берёт `max(id)` до фильтрации по `head_sha`/`app.slug`/workflow path, не делает `continue` после ошибки, вызывает `gh api` без timeout, глотает `stderr`, не проверяет `.head_sha` и хост/репо в `details_url`, падает на `id: null`/битом JSON (в `tests/test_release_checks.py` лишь 3 теста); `.github/workflows/release.yml:65-141` запускает `scripts/release_notes.py` из tag-checkout (`:137`) вместо `gate/`, проверяет SemVer после git-операций без `--`, не сверяет `RELEASE_TAG_ALLOWED_SIGNERS` с `gate/docs/release-signing/allowed_signers`; `scripts/release_notes.py:37-40, 72-120, 173` ломается на 4-backtick fences и сносках `[^1]:`, дублирует сканер и держит неиспользуемый `--output`; Scorecard `Signed-Releases: 0/10` (run `45163327566`); `gitleaks` отсутствует в `EXPECTED_WORKFLOWS`.
- **Влияние:** риск срыва/зависания релиза, дрейфа ключа при ротации, обрыва changelog и `0/10` по `Signed-Releases`; `gitleaks` пока рекомендательный.
- **Решение:** фильтровать check-runs до выбора последнего (по `completed_at`/`started_at`/`id`), добавить `continue`, `timeout=30`, проверку `.head_sha`/URL, обработку ошибок JSON + полное покрытие тестами; в `release.yml` проверять SemVer до git, добавить `--`, запускать `gate/scripts/release_notes.py`, проверять равенство `ALLOWED_SIGNERS` с `gate/docs/release-signing/allowed_signers`, загружать `outputs.bundle-path` от `attest-build-provenance` как release asset; исправить fence/footnotes и дубль сканера в `release_notes.py`; добавить `gitleaks` в `EXPECTED_WORKFLOWS` (синхронно с owner-правкой ruleset #27259237). Трудоёмкость: 2–3 ч; риски: низкие.
- **Приёмка:** расширенные `tests/test_release_*` и `make check` PASS.
- **Текущая запись:** статус `DONE`; усилен `release_checks.py` (фильтрация до выбора последнего completed/non-cancelled, `gitleaks` в `EXPECTED_WORKFLOWS`, `timeout=30`, проверка `.head_sha`/repo URL, безопасный JSONL), `release_notes.py` (единый CommonMark fence-сканер, сноски `[^1]:`, linked headings, убран `--output`), `release.yml` (SemVer до checkout, `--`, сверка `ALLOWED_SIGNERS` с `gate/`, `gate/scripts/release_notes.py`, прикладывание `dist/skills-hub-${TAG}.tar.gz.sigstore.json`) и `docs/release-process.md`; проверка: `make check` PASS; закрывает #74 (добавление `gitleaks` в ruleset #27259237 остаётся за владельцем); неудачных попыток: нет.

#### AUD-37 — Fix `frontend-design` technical defects, CSS/Next.js staleness, contrast coverage, licenses, and headroom

- `DONE` · Аудит 2026-11-26 · `skill-content/accessibility/data` · **P1 (высокий ущерб):** сломанный Markdown, устаревший Next.js 16 prop, 0 light-покрытия `--color-surface-raised`, баги парсера `contrast.py`, устаревшие лицензии в `sources.md` · уверенность: высокая · [#76](https://github.com/snaplyze/skills-hub/issues/76) (веха #9) · исполнитель: агент · deps: `AUD-33`.
- **Результат / границы:** актуальный и согласованный `frontend-design` (Baseline 2026, Next.js 16, React Compiler, WCAG 2.2 AA в обеих темах, верные лицензии, свободный запас бюджета `new-page`) и исправленный `contrast.py` (включая мелкие аллокации, перенесённые из `AUD-43` по шагу 3).
- **Доказательство:** `implementation.md:153` (`` `:`has()` ``), `:145` (`input:invalid` вместо `:user-invalid` Baseline May 2026), `:356` (устаревший Next.js 16 `priority`), `:216-226` (`<dialog>` без `display allow-discrete`), `:172,184,347` (`text-wrap: pretty`, `accent-color`, React Compiler v1.0); `motion.md:87,102,154-160` (`overlay` Chromium-only, `animation-timeline: view()` без `@supports`); `sources.md:16,38-44,52-53` (`taste-skill` уже MIT с `75dc4f080018`, несогласованность по `sickn33`, нет WCAG 2.2 = ISO/IEC 40500:2025 и WAI-ARIA 1.3 CR); `token-contrast-pairs.json:589-591` + `validate.py:789-801` (0 light-покрытия `--color-surface-raised`); `contrast.py:68-77, 95-225, 249, 269-280, 351-377` (игнор `combinations`, `####000000`/`#-1-1-1`, `hsl(120 50 50)`, лишние аргументы, `nan`/`inf`, мелкие повторные `clamped()`/`flatten()`/`thresholds()`/`build_parser()`; замер B-02 уже 58 ms на 64 / 467 ms на 50k пар — цель perf не задана); `validate.py:523-591` (CSS-парсер без строк/`:root, ...`/`@media`); внутренний дрейф (`visual-craft.md`/`audit-report.md` пути, `design-system.md:85-109, 231-281` 7 несуществующих + 6 пропущенных токенов, `design-brief.md` без `--color-border-strong`, дубль `Forms`/TOC в `responsive-mobile.md`, `component-state` == `design-system` в `reading-sets.json`, `SKILL.md:70`, `new-page` 32 462 / 32 768 B = запас 306 B, `@layer`/`clip:`/reduced-motion в `tokens.css`, green vs orange в `worked-example.md`); ноябрьские upstream/V2 улучшения (`audit-report.md` недоверенные данные браузера, `addyosmani` existing-toolchain + fail-closed a11y, `ui-ux-pro-max` error lifecycle/DTCG/map reduced-motion, `taste-skill` prod-build/font-load/320px overlap/`.example`).
- **Влияние:** устаревший фронтенд-код, пропуск light-регрессий, битые расчёты `contrast.py`, неверные лицензии и исчерпанный запас `new-page`.
- **Решение:** исправить указанные файлы `frontend-design` и `sources.md`; починить парсер и мелкие аллокации в `contrast.py` + unit-тесты; требовать покрытие обеих тем `light`+`dark` в `validate.py`, починить string-aware CSS-парсер, добавить `light: text / surface-raised`; удалить дубли в `new-page` для восстановления комфортного запаса бюджета. Трудоёмкость: 3–4 ч; риски: средние (удержать все 10 reading sets ≤32 768 B и 64+ пар AA).
- **Приёмка:** все не-исключённые токены покрыты в light и dark; все reading sets ≤32 768 B с запасом в `new-page`; новые тесты `contrast.py`/light-coverage и `make check` PASS.
- **Текущая запись:** статус `DONE`; исправлены `implementation.md`, `motion.md`, `sources.md` (`taste-skill` MIT, ISO/IEC 40500:2025, WAI-ARIA 1.3), `design-system.md`, `responsive-mobile.md`, `accessibility.md`, `ux-patterns.md`, `audit-report.md`, `design-brief.md`, `worked-example.md`, `tokens.css`, `reading-sets.json`, `SKILL.md`, `contrast.py` и `validate.py` (покрытие `light`+`dark`, `light: text / surface-raised`, string-aware CSS-парсер); запас `new-page` увеличен с 306 B до 1 357 B (`31 411 / 32 768 B`); проверка: `make check` PASS (304 теста); закрывает #76; неудачных попыток: нет.

#### AUD-38 — Upgrade workflow skills from Nov 2026 upstreams and harmonize cross-skill schemas

- `DONE` · Аудит 2026-11-26 · `skill-content/architecture` · **P1 (высокий ущерб):** утечка секретов при проверке diff, нет ограничителя цикла ревью-фиксов, расхождение схем ledger/brief · уверенность: высокая · [#77](https://github.com/snaplyze/skills-hub/issues/77) (веха #9) · исполнитель: агент · deps: `AUD-31`, `AUD-32`.
- **Результат / границы:** компактный оригинальный синтез ноябрьских практик (`superpowers` v7.0.2, `addyosmani` 0.6.18, `anthropics/skills`, `alirezarezvani`, OpenCode V2) в 8 workflow-навыков + унификация схем и триггеров без плагинов/хуков/скрытых каталогов.
- **Доказательство:** `addyosmani` (`924995886b`, `9c7f62d20cf2`, `c55b84224f`, `d463d94fb6`, `f1f6fbf398`, `480bed1391`): clean-checkout + HEAD check (`code-review:34`), secret-safe `--name-only`/`file:line` (`delivery:34`, `autonomous-execution:49`), caller-verification, base vs regression, zero-findings valid, dead-code confirmation, pasted snippets/stack traces, delta specs; `superpowers` v7.0.2 (`22f0b463e7a5`): bounded review-fix loop (3–5 раундов, resume→fresh→breaker), scoped `ADDRESSED`/`NOT ADDRESSED`, deferred minors, 1-wave final fix, `"Rulings made"` rollup (`autonomous-execution`), open-why/proposal-over-question/anti-goals/Builder Check (`specification`), Minor re-grade (`code-review`), backward tracing/defense-in-depth/condition-based waiting (`systematic-debugging`), failure-form table + 5-rep micro-tests (`skill-authoring`); `anthropics` (`e4bb5d960d87`) + `alirezarezvani` (`6278f7302d5e`, `#885`) + V2: Lack of Surprise, old-version baseline, user-vocab triggers, запрет имён встроенных slash-команд (`status`, `review`, `init`, `config`, `help`, `resume`), лимит 10 файлов V2, headless `opencode run --standalone --archived --format json`; внутренний дрейф схем ledger (`autonomous-execution:27-36` vs `orchestration:60`), brief (`orchestration:37-47`, `autonomous-execution:55,82`), `Approval:`/`Risks:` (`implementation-planning:18-26,52`; `specification:22,33-44`) и триггеров (`frontend-design`/`code-review`/`clean-code`, `tdd`/`debugging`).
- **Влияние:** риск утечки секретов в транскрипты, зацикливание фикс-ревью, потеря rulings, рассогласование бриф/ledger и двойная загрузка навыков.
- **Решение:** обновить 8 навыков компактно (сохраняя `tests/test_skill_suite.py` и запрет `opencode.json` в `SKILL.md`) и унифицировать схемы и anti-triggers. Трудоёмкость: 3–4 ч; риски: низкие.
- **Приёмка:** все 10 workflow `SKILL.md` компактны (≤32 KiB), схемы ledger/brief едины, триггеры разведены, `make check` PASS.
- **Текущая запись:** статус `DONE`; синтезированы все ноябрьские upstream-практики и V2-правила across 10 workflow-навыков, унифицированы схемы ledger/brief/шаблонов и разведены anti-triggers; проверка: все 10 `SKILL.md` ≤10.5 KiB и `make check` PASS; закрывает #77; неудачных попыток: нет.

### Дальние задачи (P2–P3 — компактно)

#### AUD-39 — Speed up and harden `scripts/check_external_links.py`

- `DONE` · Аудит 2026-11-26 · `performance/security/correctness` · **P2 (обычное):** риск превышения 15-минутного timeout CI и отсутствие code-block/SSRF-фильтров · уверенность: высокая · [#78](https://github.com/snaplyze/skills-hub/issues/78) (веха #9) · исполнитель: агент · deps: `AUD-33`.
- **Границы / результат:** pruned `os.walk` (`relative_to(root).parts`), `ThreadPoolExecutor` с per-host семафором (max 2/host) и общим timeout на URL, пропуск fenced/inline code + сбалансированные скобки (`Foo_(bar)`), `HEAD→GET` fallback, redirect/SSRF-фильтр (`http`/`https`, только `is_global` IP + `--allow-local`), вывод `file:line`, расширенные тесты `tests/test_external_links.py`.
- **Доказательство и производительность (шаг 4):** путь и нагрузка — `scripts/check_external_links.py` (39 `.md`, 67 URL, 42 на `github.com`, `node_modules/` 1 990 файлов); инварианты — детерминированный вывод, `403`/`429`→`unverified`, per-host cap, SSRF-защита + socket IP-pinning; замер до/после — B-06 `markdown_files` `14.21 → 0.91 ms` (15.6×), B-07 mock 53 URL @ 100 ms (27+26 хостов) `5.365 → 1.574 s` (3.4×), живой прогон `42.85 → 14.87 s` (2.88×); целевой предел — `link-audit.yml:19` `<15 мин` (уверенно выполняется); удалены непрофильтрованный `rglob`, серийный цикл, сканирование code blocks и неиспользуемый `status`.
- **Приёмка:** B-06/B-07 до/после показывают ускорение; unit-тесты на code blocks, `HEAD→GET`, `429`/`500`, блокировку loopback/ftp/DNS-rebinding без `--allow-local` и `make check` PASS. **Текущая запись:** статус `DONE`; реализовано и проверено независимым security-ревью (устранены все P1/P2: bounded redirect без `fp.read()`, закрытие FD/ответов без `ResourceWarning`, защита от `HTTPException`/`fec0::/10`/userinfo/port 0, end-to-end тесты редиректов и DNS rebinding); проверка: `make check` PASS (326 тестов); закрывает #78; неудачных попыток: нет.

#### AUD-40 — Remove test fragility, raw-YAML false greens, and `.git` dependency in `tests/`

- `DONE` · Аудит 2026-11-26 · `tests/correctness` · **P2 (обычное):** падения/пропуски в `git archive` и ложнозелёные строковые проверки YAML/прозы · уверенность: высокая · [#79](https://github.com/snaplyze/skills-hub/issues/79) (веха #9) · исполнитель: агент · deps: `AUD-36`.
- **Границы / результат:** структурный YAML-разбор в `test_secrets.py` и `test_release_workflow.py`, детерминированный `tmp_path` SSH-tag fixture в `test_release_signature.py`, архивобезопасный `test_release_assets.py`, очищенный `test_skill_suite.py` (динамический список включая `frontend-design`, единый regex заголовков без мёртвого `delivery`, проверка `progress.md` на уровне документа, кросс-навыковая изоляция триггеров).
- **Доказательство:** воспроизведено в `git archive` (`test_release_assets.py:127-157` падает `rc=1`, `test_release_signature.py:96-126` skip); raw-text checks (`test_secrets.py:119-125`, `test_release_workflow.py:27-45`); line-wrap/prose coupling и тавтологии (`test_skill_suite.py:135, 161-198, 242-312`).
- **Приёмка:** `pytest` PASS без пропуска core-тестов подписи в git-checkout и `git archive`; мутации комментариями валят workflow-тесты; `make check` PASS. **Текущая запись:** статус `DONE`; структурный YAML/TOML/shell-токен разбор с inline-comment мутациями в `test_secrets.py`/`test_release_workflow.py`, изолированные от `~/.gitconfig` фикстуры SSH-подписи и архивов (`--show-toplevel`), динамические 11 навыков + adversarial cross-skill trigger isolation в `test_skill_suite.py`; проверка: 326 passed / 0 skipped и в git-checkout, и во вложенном `.git`-free снимке, `make check` PASS; закрывает #79; неудачных попыток: нет.

#### AUD-42 — Cut next signed release (`v1.3.0`) after audit fixes (owner-gated)

- `DONE` · Аудит 2026-11-26 · `delivery/release` · **P2 (обычное):** на `main` накоплены изменения этапа 09 (вкл. Skill Suite v2 и OpenCode V2), отсутствовавшие в `v1.2.0` · уверенность: высокая · [#81](https://github.com/snaplyze/skills-hub/issues/81) (веха #9) · исполнитель: агент (по поручению владельца) · deps: `AUD-30`, `AUD-31`, `AUD-32`, `AUD-33`, `AUD-34`, `AUD-35`, `AUD-37`, `AUD-38`.
- **Границы / результат:** подписанный immutable релиз `v1.3.0` (`f633a27`, run `45772598608`, `CHANGELOG.md`, `git tag -s`, `release.yml` с `main`, `SHA256SUMS`, `.sigstore.json` bundle, provenance attestation, публикация Latest, обновление `README.md`/`docs/repository-settings.md`).
- **Доказательство:** `https://github.com/snaplyze/skills-hub/releases/tag/v1.3.0` (`isDraft: false`, `isImmutable: true`, `Latest`); проверены `git verify-tag -- refs/tags/v1.3.0`, `sha256sum -c SHA256SUMS`, `gh attestation verify` и офлайн `gh attestation verify --bundle skills-hub-v1.3.0.tar.gz.sigstore.json` — все PASS; все 11 навыков в архиве.
- **Приёмка:** `v1.3.0` — latest immutable release с 11 обновлёнными навыками; `verify-tag`, `sha256sum -c`, `gh attestation verify` PASS. **Текущая запись:** статус `DONE`; релиз `v1.3.0` опубликован и верифицирован; закрывает #81; неудачных попыток: нет.

#### AUD-43 — Dependency bumps, CI/tooling polish, `bug_report.yml`, and `AGENTS.md` sync

- `DONE` · Аудит 2026-11-26 · `ci/dependencies/docs` · **P3 (низкий риск):** 0 открытых CVE, плановые патчи и мелкая гигиена (аллокации `contrast.py` перенесены в `AUD-37` по шагу 3) · уверенность: высокая · [#82](https://github.com/snaplyze/skills-hub/issues/82) (веха #9) · исполнитель: агент (с одобрения владельца) · deps: `AUD-30`.
- **Границы / результат:** смержены Dependabot PR #66 (`ruff` 0.17.6) и #87 (заменивший #67: `dependency-review-action` 5.0.1, `scorecard-action` 2.6.0, `codeql-action` v4.39.4); обновлены `PyYAML 6.0.4`, `codeql-action v4.39.5`, `markdownlint-cli2 0.24.2`; добавлены workflow-навыки в `.github/ISSUE_TEMPLATE/bug_report.yml:18`; добавлены `#.venv`/`#.playwright-cli` в `Makefile:34`/`package.json:10` (`[--strict]` в `scripts/check_workflows.py:17` закрыт в `AUD-30`, `v1.2.0`/`v1.3.0` в `install/opencode.sh` закрыты в `AUD-34`/`v1.3.0`); в `codeql.yml` добавлен язык `actions` и удалён no-op `autobuild`; добавлена справка V2 `skills[]`/`permission.skill` в `README.md`; обновлён и очищен от локальных деталей окружения `AGENTS.md` (`experimental.subagent_depth=2`, 11 навыков, дата `2026-11-26`, обязательные проверки с `gitleaks` и `Analyze (actions)`).
- **Доказательство:** смерженные PR #66/#87/#96, обновлённый `AGENTS.md`, ruleset #27259237 (`validate`, `Analyze (python)`, `Analyze (actions)`, `dependency-review`, `gitleaks`), `scripts/release_checks.py` и `docs/repository-settings.md`.
- **Приёмка:** зависимости/шаблоны/`AGENTS.md` обновлены, `make check` и CI (`Analyze (python)` + `Analyze (actions)` + `gitleaks`) PASS. **Текущая запись:** статус `DONE`; все пункты выполнены и проверены `make check` + CI; закрывает #82; неудачных попыток: нет.

## Решения и исключения владельца

- **CI:** hosted (`ubuntu-24.04`) по умолчанию; self-hosted сейчас нет (при добавлении — только для подходящих заданий); fork approval `all_external_contributors`; обязательные проверки `validate`, `Analyze (python)`, `dependency-review`; CodeQL — обязательный code-scanning gate.
- **Бюджет проверок:** `make validate` ≤1 s, `make check` ≤30 s на hosted runner.
- **Релизы:** только владелец; signed annotated tags (`v*`), ancestry `main`, required checks, protected `release` environment (solo-исключение: `prevent_self_review: false`, owner bypass в `tag-protection`), immutable releases, draft + manual promotion, notes только из `CHANGELOG.md`.
- **Main:** 0 approvals пока solo; CODEOWNERS advisory; при втором maintainer — `approvals=1`, code-owner review, `prevent_self_review=true`, signed commits/tags, emergency path.
- **Навыки:** 10 workflow skills + `frontend-design` (единый стандарт Agent Skills, `name == dir`, `compatibility: agentskills`, без OpenCode-специфики в `skills/`); оркестрация нативная для Antigravity (`research`/`browser`/`self`, `invoke_subagent`/`define_subagent`/`run_workflow`, пользовательские `/swarm`/`/boost`/`/teamwork`) и OpenCode (`explore`/`general`); без plugin/hooks/background-scheduler/TUI/model profiles; 32 KiB reading budget; WCAG 2.2 AA (24×24 px минимум, 44×44 px таргет, контраст 4.5:1 / 3:1, 64 пары + 27 комбинаций).
- **План:** owner-facing, русский, единый реестр `docs/plan.md`; не загружается как инструкции; продуктовые изменения — только отдельными задачами плана.
- **Доступ/оркестрация:** настраиваются только в пользовательской области (`~/.gemini/config/`, `~/.gemini/antigravity-cli/settings.json` для Antigravity; `~/.config/opencode/` для OpenCode); в проекте не настраивать; подагентов не устанавливать и не менять.

## Риски

- **Release:** custody/rotation подписывающего ключа; environment approval; owner bypass при создании тегов; full history; solo-review; расхождение `RELEASE_TAG_ALLOWED_SIGNERS` и `docs/release-signing/allowed_signers`.
- **Installer:** `realpath -m`/`mv -T`/`sort -z` на не-GNU платформах; внутренние симлинки и `.gitignore`d файлы при `--verify`; бэкапы и частота обновлений.
- **Validation/tests:** edge cases Markdown/YAML/CSS-парсеров; flaky external links; асимметричное light/dark покрытие; secret-scan false positives; стоимость suite.
- **CI:** churn lockfile/actions; ширина allowlist; drift runner/toolchain; Node.js 22 EOL (`2027-04-30`); ручное отслеживание `gitleaks`; upstream Docker tag внутри `ossf/scorecard-action`.
- **Skills/plan:** фрагментация контекста и link churn; запас бюджета `new-page` 306 B; tokenizer vs bytes; drift плана (исторических циклов исполнения не зафиксировано); upstream licensing (`sickn33` исключает импортированные навыки).

## Гипотезы (не задачи)

- Fork PR может не пройти `dependency-review` из-за `comment-summary-in-pr: always` — проверить контролируемым fork PR.
- CI wall-time (`make check` локально ~22.6 s; в CI run `43946282578` job `validate` 61 s / `make check` 17 s) — снять детальный per-step breakdown на hosted.
- CodeQL на docs-only PR (61 s в run `45199573587`) — проверить `paths-ignore` без ослабления required checks.
- Токенизация references может отличаться от bytes/4 — проверить реальным токенайзером.
- Actions allowlist `verified_allowed` шире least privilege — оценить сужение.
- `require_extra_approval_for_unattributed_changes` при 0 approvals — проверить unverified email.
- name/ID portability и alternate `<name>.md` layout вне OpenCode — проверить спецификации других harness.
- «64 audited» provenance: fixture не хранит audit metadata.
- PR template relative link `../CONTRIBUTING.md` (`.github/PULL_REQUEST_TEMPLATE.md:32`) — проверить рендер в GitHub UI (синхронизируя `tests/test_validation.py:223`).
- Upstream licensing `sickn33/agentic-awesome-skills` (`ClawForge` без `LICENSE`, `mobile-design` без записи в `docs/sources/sources.md`) — подтвердить legal/maintainer политику.
- OpenCode V2 hot-reload `~/.config/opencode/skills/` и TUI-алиас `/reload` (`v2.4.1`) — проверить в изолированном `opencode --standalone` через `opencode api get /api/skill` до/после `opencode reload`.
- `tools.opencode.session.move({ sessionID, directory })` на запущенном дочернем подагенте — проверить на тестовом git-репо в `/tmp/opencode/`.
- OpenCode V2 HTTP-каталоги (`index.json`, same-origin) vs редиректы GitHub Releases и отсутствие встроенной проверки подписи — проверить на изолированном инстансе, если рассматривать публикацию каталога.
- `experimental.mcp_skills` (`opencode.ai/config.json:543`) — не документирован, отслеживать в релизах OpenCode.
- Stock macOS 13+ / BSD `realpath` без `-m` и `mv` без `-T` в `install/opencode.sh` — проверить на macOS-раннере или через stub `realpath` в `tests/test_installer.py`.
- Отменённый `workflow_dispatch`/scheduled прогон CodeQL (`concurrency: cancel-in-progress: true`) может перебить `id` зелёного `push`-прогона в `release_checks.py` — проверить на реальном NDJSON `commits/<sha>/check-runs`.
- Расхождение runtime YAML-парсера OpenCode V2 и PyYAML 1.1 (`validate.py`) на сложных `description` — проверить установкой тестового навыка в изолированный `XDG_CONFIG_HOME`.

## Владельцу / вне объёма

- **Публичный `AGENTS.md`:** очищен от локальных деталей permissions/secret-reads/MCP (`~/.config/opencode/` — единственный источник пользовательской конфигурации) и синхронизирован с `2026-11-26` (11 навыков, `experimental.subagent_depth=2`, обязательные проверки с `gitleaks` и `Analyze (actions)`).
- **Окружение пользователя:** глобальные skills/MCP существуют только локально у владельца; Claude Code/Codex не установлены и не проверялись.
- **Ruleset & Scorecard:** `gitleaks` и `Analyze (actions)` добавлены в обязательные проверки ruleset #27259237 и `scripts/release_checks.py`; потолок Scorecard при solo-maintainer ограничен структурными нулями (`Maintained` <90 дней, `Code-Review`, `Contributors`, `Fuzzing`, `CII-Best-Practices`) — для approvals/code-owner review нужен второй maintainer.
- **Инфраструктурный горизонт:** Node.js 22 EOL `2027-04-30` (миграция на Node.js 24 LTS); `gitleaks` в `secret-scan.yml` отслеживается вручную; `ossf/scorecard-action` внутри `action.yaml` использует Docker-тег, а не digest.
- **Продуктовые решения:** (а) выделять ли `accessibility-engineering` в отдельный навык или оставить в `frontend-design/references/accessibility.md`; (б) добавлять ли опциональный headless behavioral eval runner (`opencode run --standalone --archived --format json`); (в) подтвердить политику «только идеи» для `sickn33` (`taste-skill` MIT и `anthropics/skills/skills/skill-creator` Apache-2.0 уже подтверждены).
- **Защищённая история:** `CHANGELOG.md` (`v1.1.0`) не упоминал возврат загрузки SARIF Scorecard из `6bec3ee` после отключения в `1.0.1` — задним числом не переписывалось.

## Завершено (этапы 01–09)

Все `DONE` подтверждены `make check`/CI; следующий шаг — нет; неудачных попыток не зафиксировано. Первичные источники синтеза и лицензии зафиксированы в `THIRD_PARTY_NOTICES.md` и `skills/frontend-design/references/sources.md`.

| ID | Этап / трекер | Deps | Результат и доказательство |
|---|---|---|---|
| `AUD-01` | 01 · #14 | none | Release gate с `main`, signed annotated tag, ancestry, check-runs + workflow path, `release` env, `CHANGELOG` notes, archive/SHA-256/provenance (`v1.1.0` `b1f438d`). Док: `release.yml`, `scripts/release_*.py`, `tests/test_release_*`, `docs/release-process.md`. |
| `AUD-02` | 01 · #15 | `AUD-01` | Copy default, `realpath` guards, atomic staging/backups, `--copy` over symlink, `--all` kebab IDs, artifact exclusions, `~/`, folded YAML, `--verify`/`--ref`. Док: `install/opencode.sh`, `tests/test_installer.py`, `tests/test_release_assets.py`. |
| `AUD-03` | 01 · #16 | none | Валидация SKILL/cross-file anchors, frontmatter/body, AGENTS/PR template, 64 пары + 26 комбинаций WCAG 2.2 AA, `contrast.py` exit 0/1/2, negative/mutation fixtures. Док: `scripts/validate.py`, `tests/test_validation.py`, `tests/test_contrast_cli.py`. |
| `AUD-04` | 02 · #17 | `AUD-03` | `ubuntu-24.04`, Python 3.12, hash-locked deps, `make check`, `check_workflows.py`, job-scoped Dependency Review, бюджет `validate` ≤1 s / `check` ≤30 s (baseline 810 ms → ~0.3 s / 20 s). Док: `.github/workflows/*`, `Makefile`, `tests/test_workflows.py`. |
| `AUD-05` | 02 · #18 | none | `.gitignore` покрывает `.env*` (`!.env.example`), ключи, `secrets/`, `credentials*`, `.opencode/`/`.claude/`/`.agents/`; SHA-pinned `gitleaks 8.30.1`. Док: `.gitignore`, `secret-scan.yml`, `tests/test_secrets.py`. |
| `AUD-06` | 02 · #19 | `AUD-03` | 32 KiB reading budget (`design-direction.md` 35 017 B / set 85 527 B → `new-page` 32 462 B, 10 sets, `SKILL.md` 7 035 B), канонические токены/`sources.md`. Док: `reading-sets.json`, `references/`, `scripts/validate.py`. |
| `AUD-07` | 03 · #20 | rel `01/04/06` | CODEOWNERS advisory, Scorecard SARIF/artifact 30d, `docs/repository-settings.md`, синхронизация `GOVERNANCE.md`. Док: `.github/CODEOWNERS`, `scorecard.yml`, `docs/repository-settings.md`. |
| `AUD-15` | docs · — | none | Правки `README`/`CONTRIBUTING`/`GOVERNANCE`/`SECURITY`/`CHANGELOG`/notices (`git show 9a7804e`; residual `AUD-20` закрыт в `AUD-04`). |
| `SKL-01` | 04 · #27 | none | `skills/specification/SKILL.md` (спецификация без кода, вопросы, non-goals, acceptance, handoff). |
| `SKL-02` | 04 · #28 | `SKL-01` | `skills/implementation-planning/SKILL.md` (задачи 5–30 мин, файлы/интерфейсы, тесты, self-review, без hooks). |
| `SKL-03` | 04 · #29 | `SKL-02`, `SKL-05` | `skills/autonomous-execution/SKILL.md` (один писатель на файл, TDD-гейт, ledger, review, stop conditions, worktree). |
| `SKL-04` | 05 · #30 | `SKL-05` | `skills/systematic-debugging/SKILL.md` (reproduce → locate → hypothesize → fix → regression test). |
| `SKL-05` | 05 · #31 | none | `skills/test-driven-development/SKILL.md` (red-green-refactor, поведенческие тесты, три закона TDD). |
| `SKL-06` | 05 · #32 | `SKL-03` | `skills/code-review/SKILL.md` (свежий контекст, без self-approval, P0/P1/P2, response protocol). |
| `SKL-07` | 05 · #33 | `SKL-06` | `skills/delivery/SKILL.md` (evidence gate, PR/merge без обхода, cleanup, отчёт). |
| `SKL-08` | 05 · #34 | `SKL-05` | `skills/clean-code/SKILL.md` (behavior-preserving рефакторинг, конвенции репо выше эвристик). |
| `SKL-09` | 05 · #35 | `SKL-01`–`08` | `skills/skill-authoring/SKILL.md` (триггеры, progressive disclosure, tabletop matrix, атрибуция; без behavioral evals). |
| `ORC-01` | 06 · #38 | `SKL-03/06/07` | `skills/orchestration/SKILL.md`, `docs/opencode-orchestration.md`, `tests/test_skill_suite.py` (native `explore`/`general`, без плагина/хуков). |
| `AUD-22` | 07 · #41 | `AUD-01`, `SKL/ORC` | Signed immutable release `v1.2.0` (`8f252ca`) с 11 навыками; `SHA256SUMS`, `gh attestation verify` PASS. |
| `AUD-23` | 07 · #42 | `AUD-01` | Публичный `docs/release-signing/allowed_signers` + `README.md`, `tests/test_release_signature.py`; `verify-tag` PASS / tampered FAIL. |
| `AUD-24` | 07 · #43 | `ORC-01` | Правки drift docs (PR #49) + автопроверка путей тестов и счётчиков навыков в `tests/test_skill_suite.py`. |
| `AUD-25` | 07 · #44 | `SKL-09` | Table-driven trigger matrix + empty-workflow mutation в `tests/test_skill_suite.py` (10 contract tests PASS). |
| `AUD-26` | 07 · #45 | `AUD-03` | 3 focused tests simple-skill branch в `tests/test_validation.py` (pass / oversize fail / references без manifest fail). |
| `AUD-27` | 07 · #46 | `ORC-01`, `SKL-09` | Anti-trigger/handoff `orchestration` → `autonomous-execution` + `test_orchestration_hands_off_approved_plan`. |
| `AUD-28` | 07 · #47 | audit | Первичное сжатие плана (328/51 255 B → 297/34 274 B, PR #50). |
| `AUD-29` | 07 · #48 | `AUD-03` | Module-scoped HTTP server в `tests/test_external_links.py` (~2 s → ~0.55 s). |
| `SKL2-01` | 08 · #58 | none | Plan header, interfaces, checkbox steps, checkpoints, `docs/plans/` без перезаписи ([план](plans/2026-11-16-skill-suite-v2.md), PR #62). |
| `SKL2-02` | 08 · #59 | `SKL2-01` | Ledger `.progress.md`, task briefs, BASE, `Ruling:`, 3-strike, per-task/final review, independent failure routing (PR #62). |
| `SKL2-03` | 08 · #60 | `SKL2-02` | Tests-first review, mutation check, 5 axes, severity, integration choice, post-merge verify, scope discipline (PR #62). |
| `SKL2-04` | 08 · #61 | `SKL2-01`–`03` | Trigger mining, baseline evals, pressure variants, versioning, licenses, attribution (PR #62; closeout #63 PR #64/#65). |
| `AUD-41` | 09 · #80 | none | Упорядочивание плана (база `28465f1`): свёрнуты раздробленные DONE-секции 01–08 и устаревшая мета-секция `AUD-28`, разделены оптимизации (`AUD-44` из `AUD-36`, `contrast.py` из `AUD-43` в `AUD-37`), добавлены поля производительности и нативные `blocked_by`-связи в трекере; закрывает #80. |

### Карта слияния ID

| Было | Стало | Причина |
|---|---|---|
| `AUD-01`, `AUD-06`, `AUD-09` | `AUD-01` | один release pipeline: gate, notes, provenance |
| `AUD-02`, `AUD-03`, installer tests из `AUD-11` | `AUD-02` | один installer: безопасность, trust, проверка |
| `AUD-11`, `AUD-16`, `AUD-17` | `AUD-03` | одна validation correctness: false greens, parser, tokens |
| `AUD-05`, `AUD-08`, `AUD-10`, `AUD-20` | `AUD-04` | один CI/toolchain/workflow contract |
| `AUD-04` | `AUD-05` | secret handling |
| `AUD-07`, `AUD-14`, `AUD-18`, `AUD-19` | `AUD-06` | один skill content/instruction budget |
| `AUD-12`, `AUD-13`, `AUD-21` | `AUD-07` | repository protections и evidence |
| `AUD-15` | DONE | документы уже исправлены |
| `AUD-36` (`validate.py` часть) | `AUD-44` + `AUD-36` | разделение оптимизации проверок (`validate.py`) и стоимости тестов (`tests/`) по шагу 3 |
| `AUD-43` (`contrast.py` часть) | `AUD-37` | перенос мелкой оптимизации продукта `contrast.py` из CI/deps-задачи по шагу 3 |

### История аудитов и ограничения

- `2026-11-15` (`2b4be4f`): все 7 областей → `AUD-01`–`AUD-07` DONE.
- `2026-11-15` (`977e2f2`): все 7 областей (снимок: 188 тестов, 11 навыков, 49/49 ссылок, `v1.1.0` проверен) → `AUD-22`–`AUD-29` DONE.
- `2026-11-26` (`5f0a620`, #68 / PR #83): все 7 областей + OpenCode V2 (`v2.4.1`) + 11 upstream-репозиториев → `AUD-30`–`AUD-43` (14 задач, после разделения в `AUD-41` — 14 OPEN + `AUD-41` DONE).
- **Общие ограничения проверок:** не выполнялись fork PR, live tag/release dispatch, destructive installer, macOS/BSD runtime, UI WCAG, реальный токенайзер, upstream legal review; Python 3.9 не проверялся (floor 3.12).

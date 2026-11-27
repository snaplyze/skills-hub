# План

Трекер: https://github.com/snaplyze/skills-hub/issues; сверено 2026-11-27T19:20:43Z; веха #11 «Аудит 2026-11-27» (0 OPEN; 10 DONE: `AUD-45` #110–`AUD-54` #119; закрыт issue аудита #109); закрытые этапы 01–10: #14–#20, #27–#35, #38, #41–#48, #54, #58–#61, #63, #68–#82, #84, #99–#103 (вехи #1–#10 закрыты; `v1.4.0` опубликован на `f3465d0`, run `45992777582`). Реестр — этот файл; owner-facing, на русском, не загружается как инструкции агентов.

## Документы и стартовый контекст

| Документ | Роль | Строк / байт |
|---|---|---|
| `AGENTS.md` | сведения о проекте и стартовый контекст инструкций | 48 / 8 485 |
| `docs/plan.md` | единый реестр плана (обновляется на месте; не входит в бюджет 32 KiB) | — |
| `README.md` | вход, quick start, установка (Antigravity + OpenCode), оркестрация, защиты | 457 / 28 199 |
| `docs/antigravity-orchestration.md` | архитектура нативной оркестрации Antigravity | 123 / 9 691 |
| `docs/opencode-orchestration.md` | архитектура нативной оркестрации OpenCode | 83 / 5 761 |
| `docs/release-process.md` | релизный гейт и owner setup | 285 / 13 260 |
| `docs/repository-settings.md` | settings evidence и метаданные репозитория (сверено 2026-11-27) | 84 / 5 834 |
| `docs/release-signing/` | публичный SSH trust и ротация | 44 / 1 965 |
| `CONTRIBUTING.md`, `GOVERNANCE.md`, `SECURITY.md`, `CHANGELOG.md` | правила, безопасность, история релизов | 518 / 23 840 |
| `CODE_OF_CONDUCT.md`, `.github/PULL_REQUEST_TEMPLATE.md` | кодекс поведения и шаблон PR | 168 / 6 681 |
| `THIRD_PARTY_NOTICES.md` | атрибуция workflow-навыков и указатель `sources.md` | 53 / 3 444 |
| `docs/plans/2026-11-16-skill-suite-v2.md` | завершённый детальный план этапа 08 | 281 / 10 726 |
| `docs/plans/2026-11-27-antigravity-support.md` | завершённый детальный план этапа 10 (поддержка Antigravity) | 153 / 12 046 |

Стартовый контекст следующей задачи плана — `AGENTS.md` (`8 485 B`) + активная секция `docs/plan.md` (сам план не входит в бюджет загружаемых инструкций 32 KiB).

## Этапы

Порядок этапов: `01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11`.

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
| 10 | `10 — Antigravity support` (#10) | closed | 0 OPEN, 5 DONE (`AGY-01` #99–`AGY-05` #103) |
| 11 | `Аудит 2026-11-27` (#11) | closed | 0 OPEN, 10 DONE (`AUD-45` #110–`AUD-54` #119) |

## Аудит 2026-11-27

- **Метаданные:** дата `2026-11-27` (сверка трекера `2026-11-27T19:20:43Z`), база аудита `c187538` (упорядочивание плана на базе `48529b6`, дельта от `5f0a620`: 75 файлов, `+7 967 / -2 465`), репозиторий и трекер публичные (`snaplyze/skills-hub`; по правилу 14 подробности неустранённых уязвимостей не публикуются, удалённо эксплуатируемых внешними пользователями дефектов не выявлено).
- **Охват и снимок `c187538` (`git archive`, без `.git`):** все 7 областей (7 read-only аудиторов + замеры в `git archive` + первоисточники GitHub API и `actions/runner`). `validate.py` CLI медиана `157.0 ms` (`154.4–159.9 ms`), in-process `validate_repo` `92.95 ms` (`check_skill` 11× `40.93 ms`, `check_root_docs` `29.87 ms`, `check_yaml` `7.87 ms`, `check_installer` `6.54 ms`, `check_contrast` `4.40 ms`, `check_github_docs` `0.37 ms`; 33 навыка `173.4 ms`, 66 навыков `300.5 ms`); `contrast.py` `0.3 ms` (64) / `45.6 ms` (10k) / `222.6 ms` (50k); `install/antigravity.sh` copy `244.5 ms` / `--list 79.9 ms` (11 навыков, 39 файлов) → `695.8 ms` / `249.2 ms` (31 навык) → `1 373.6 ms` / `493.6 ms` (61 навык, 989 файлов); `pytest` `.git`-free PASS (`343 passed, 0 skipped, 13.68 s`; `test_validation.py` `9.90 s` = 72%, `test_installer.py` `3.14 s` = 23%, `test_external_links.py` `1.12 s`); hosted CI `c187538`: `validate` `38 s` (`make check` `24 s`), `Analyze (python)` `54 s`, `Analyze (actions)` `46 s`, `gitleaks` `5 s`, `Scorecard` `7.0/10` (`Signed-Releases`/`Pinned-Dependencies`/`Token-Permissions`/`SAST`/`CI-Tests` `10/10`, 0 алертов Code Scanning и Dependabot), hosted `Link Audit` `45992629239` PASS (`76/76`, `16 s`).
- **Прямые документальные правки (PR #120 / #109, описание исправлено при подтверждённом коде, продукт не менялся):** `README.md` (4 точных имени SSH-ключей вместо `id_*`, добавлена цель `make css`), `docs/opencode-orchestration.md` (синхронизация с унифицированным `skills/orchestration/SKILL.md`), `docs/release-process.md:233` (`VERSION=v1.4.0`). Не менялись: код, тесты, `skills/*`, CI/YAML, `AGENTS.md` (0 расхождений), исторический `CHANGELOG.md`.
- **Исполнитель и статус очереди:** все 10 задач вехи #11 (`AUD-45`–`AUD-54`) завершены (`0 OPEN`); `BLOCKED`: нет; неудачных попыток: нет. Review-gate пройден на каждой задаче.
- **Порядок исполнения (DAG):** Волна 1: `AUD-45`, `AUD-46`, `AUD-48`, `AUD-50`, `AUD-51` → Волна 2: `AUD-47` (после `AUD-45`, `AUD-46`, `AUD-48`), `AUD-49` (после `AUD-46`) → Волна 3: `AUD-53` (после `AUD-46`, `AUD-48`), `AUD-54` (после `AUD-46`, `AUD-47`).

### Статус областей (Аудит 2026-11-27)

| Область | Статус | Ограничения охвата |
|---|---|---|
| Архитектура | проверено | Полный разбор `scripts/`, `install/{lib,antigravity,opencode}.sh`, 11 `SKILL.md`, дублей проверок и сверка с `actions/runner` (`MappingDefinition.cs:72`, `TemplateReader.cs:182`). |
| Безопасность | частично | Проверены все скрипты, установщики, 7 workflows, lockfiles, 11 навыков и живые настройки API; без внешнего fork PR, live `workflow_dispatch` релиза, macOS/BSD и adversarial LLM-eval. |
| Данные | проверено | YAML frontmatter (11 навыков + `UniqueKeySafeLoader` vs Bash `read_description`), `tokens.css`, `token-contrast-pairs.json`, `reading-sets.json`, `contrast.py`, 3 Markdown-парсера, `release_checks.py` JSONL, `CHANGELOG.md`. |
| Производительность | частично | Замеры в неизменяемом `git archive`-снимке (`validate.py` CLI/фазы/масштаб 11–66, `_scan_inline_links` `K=100..3000`, установщик 11–61, `contrast.py` 64–50k, `pytest` per-module) и hosted CI `c187538`; без реального LLM-токенайзера и сетевого профиля `make links`. |
| Тесты | проверено | Все 13 модулей `tests/` проверены статически + прогон 343 тестов в `.git`-free снимке с `--durations=20` и per-module замерами; без macOS/BSD stub-прогона и живого `GIT_CONFIG_GLOBAL`-прогона. |
| Сборка и доставка | частично | Все 7 workflows, 11 конфигов, 8 SHA-пинов, `gitleaks` SHA-256, `dependency-review-action@v5.0.1` и живые rulesets/API проверены; без внешнего fork PR, чистого `make deps` в Python 3.12 venv и macOS/BSD. |
| Документация | проверено | Все корневые доки, `docs/**`, `.github/*_TEMPLATE*`, `AGENTS.md` (0 расхождений), 11 `SKILL.md` и 10 `references/*.md` сверены с кодом и `wc -l -c`; без живого рендера PR template в GitHub UI и живого OpenCode/Antigravity UI. |

## Решения и исключения владельца

- **CI:** hosted (`ubuntu-24.04`) по умолчанию; self-hosted сейчас нет (при добавлении — только для подходящих заданий); fork approval `all_external_contributors`; обязательные проверки `validate`, `Analyze (python)`, `Analyze (actions)`, `dependency-review`, `gitleaks`; CodeQL — обязательный code-scanning gate.
- **Бюджет проверок:** `make validate` ≤1 s, `make check` ≤30 s на hosted runner.
- **Релизы:** только владелец; signed annotated tags (`v*`), ancestry `main`, required checks, protected `release` environment (solo-исключение: `prevent_self_review: false`, owner bypass в `tag-protection`), immutable releases, draft + manual promotion, notes только из `CHANGELOG.md`.
- **Main:** 0 approvals пока solo; CODEOWNERS advisory; при втором maintainer — `approvals=1`, code-owner review, `prevent_self_review=true`, signed commits/tags, emergency path.
- **Навыки:** 10 workflow skills + `frontend-design` (единый стандарт Agent Skills, `name == dir`, `compatibility: agentskills`, без OpenCode-специфики в `skills/`); оркестрация нативная для Antigravity (`research`/`browser`/`self`, `invoke_subagent`/`define_subagent`/`run_workflow`, пользовательские `/swarm`/`/boost`/`/teamwork`) и OpenCode (`explore`/`general`); без plugin/hooks/background-scheduler/TUI/model profiles; 32 KiB reading budget; WCAG 2.2 AA (24×24 px минимум, 44×44 px таргет, контраст 4.5:1 / 3:1, 64 пары + 35 комбинаций).
- **План:** owner-facing, русский, единый реестр `docs/plan.md`; не загружается как инструкции; продуктовые изменения — только отдельными задачами плана.
- **Доступ/оркестрация:** настраиваются только в пользовательской области (`~/.gemini/config/`, `~/.gemini/antigravity-cli/settings.json` для Antigravity; `~/.config/opencode/` для OpenCode); в проекте не настраивать; подагентов не устанавливать и не менять.

## Риски

- **Release:** custody/rotation подписывающего ключа; environment approval; owner bypass при создании тегов; full history; solo-review; расхождение `RELEASE_TAG_ALLOWED_SIGNERS` и `docs/release-signing/allowed_signers`.
- **Installer:** `realpath -m`/`mv -T`/`sort -z` на не-GNU платформах; внутренние симлинки и `.gitignore`d файлы при `--verify`; бэкапы и частота обновлений.
- **Validation/tests:** edge cases Markdown/YAML/CSS-парсеров; flaky external links; асимметричное light/dark покрытие; secret-scan false positives; стоимость suite.
- **CI:** churn lockfile/actions; ширина allowlist; drift runner/toolchain; Node.js 22 EOL (`2027-04-30`); ручное отслеживание `gitleaks`; upstream Docker tag внутри `ossf/scorecard-action`.
- **Skills/plan:** фрагментация контекста и link churn; запас бюджета `new-page` 1 127 B (`31 641 / 32 768 B`); tokenizer vs bytes; drift плана; upstream licensing (`sickn33` исключает импортированные навыки).

## Гипотезы (не задачи)

- Сквозное прохождение внешнего fork PR через все 4 PR-workflow + `CodeQL` gate под `all_external_contributors` — проверить контролируемым fork PR (часть про `403` в `dependency-review` опровергнута исходниками `v5.0.1` `src/comment-pr.ts:64-78`).
- Детальный per-step профиль hosted `validate` (`38 s` job / `24 s` `make check` на `c187538`, run `45993337409`) и `CodeQL` на docs-only PR (`paths-ignore` без ослабления required checks) — снять профиль на hosted.
- Реальные LLM-токены (`o200k_base`/Gemini) vs UTF-8 bytes/4 для всех 9 наборов `frontend-design`, суммарных описаний (`3 962 B`) и со-загрузки цепочки workflow-навыков — замерить реальным токенайзером.
- Повторный `getaddrinfo` и отсутствие HTTP/TLS keep-alive / per-host кеша `HEAD 405 → GET` в `scripts/check_external_links.py` — замерить выигрыш на локальном HTTPS-стенде из 76 URL с перекосом по хостам (`42` на `github.com`).
- Покрытие спецпрефиксов IPv6 (`100.64.0.1`, `64:ff9b::127.0.0.1`, `2002:7f00:0001::1`, `::ffff:0:127.0.0.1`) на Python 3.12 CI (локально проверено на Python 3.15.2) — проверить в CI на Python 3.12.
- Actions allowlist `verified_allowed` шире least privilege — оценить отключение и прогон всех 7 workflows.
- `require_extra_approval_for_unattributed_changes` при 0 approvals — проверить unverified email.
- Альтернативный `<name>.md` layout вне Antigravity/OpenCode — проверить спецификации других harness.
- «64 audited» provenance: `token-contrast-pairs.json` не хранит audit metadata.
- PR template relative link `../CONTRIBUTING.md` (`.github/PULL_REQUEST_TEMPLATE.md:32`) — проверить рендер в GitHub UI (синхронизируя `tests/test_validation.py:282`).
- Upstream licensing `sickn33/agentic-awesome-skills` (`ClawForge` без `LICENSE`, `mobile-design` без записи в `docs/sources/sources.md`) — подтвердить legal/maintainer политику.
- Встроенный `research` подагент Antigravity vs OS-sandbox (`docs/antigravity-orchestration.md:38, 114`) — проверить в изолированной сессии CLI (`--sandbox` / без) и App, т.к. в декларациях CLI присутствуют `run_command`/`search_web`.
- OpenCode V2: нативность `@<skill-name>` (`README.md:50, 286, 294`), hot-reload `~/.config/opencode/skills/` и `/reload` (`v2.4.1`), `session.move` на дочернем подагенте, HTTP-каталоги (`index.json`), `experimental.mcp_skills` (`opencode.ai/config.json:543`) — проверить в изолированном `opencode --standalone`.
- Совместимость `agy plugin validate --json` и runtime YAML-парсера OpenCode V2 с PyYAML 1.1 (`validate.py`) на краевом frontmatter (`metadata.opencode/autoinvoke: false`, `yes`/`no`, сложные `description`, `allowed-tools` с запятыми) — проверить на временном staging-пакете и изолированном `XDG_CONFIG_HOME`.
- Stock macOS 13+ / BSD `realpath`/`mv`/`tar`/`sort` в `install/lib.sh` и чистая установка `make deps` в свежем Python 3.12 venv — проверить на macOS/stub-утилитах в `PATH` и чистом Python 3.12 venv.
- Многостраничная пагинация `gh api --paginate .../check-runs?per_page=1&filter=all` — проверить реальный NDJSON-вывод в `scripts/release_checks.py`.

## Владельцу / вне объёма

- **Публичный `AGENTS.md`:** очищен от локальных деталей permissions/secret-reads/MCP и синхронизирован с `2026-11-27` (11 навыков, Antigravity `agy 1.5.18` + OpenCode V2 `experimental.subagent_depth=2`, пользовательские области `~/.gemini/config/`, `~/.gemini/antigravity-cli/settings.json` и `~/.config/opencode/`, 5 обязательных проверок).
- **Окружение пользователя:** глобальные skills/MCP существуют только локально у владельца; Claude Code/Codex не установлены и не проверялись.
- **Ruleset & Scorecard:** `gitleaks` и `Analyze (actions)` в ruleset #27259237 и `scripts/release_checks.py`; потолок Scorecard (`7.0/10`) при solo-maintainer ограничен структурными нулями (`Maintained` <90 дней, `Code-Review`, `Contributors`, `Fuzzing`, `CII-Best-Practices`) — для approvals/code-owner review нужен второй maintainer.
- **Инфраструктурный горизонт:** Node.js 22 EOL `2027-04-30` (миграция на Node.js 24 LTS); `gitleaks` в `secret-scan.yml` отслеживается вручную; `ossf/scorecard-action` внутри `action.yaml` использует Docker-тег `v2.6.0`, а не digest.
- **Продуктовые решения:** (а) выделять ли `accessibility-engineering` в отдельный навык или оставить в `frontend-design/references/accessibility.md`; (б) добавлять ли опциональный headless behavioral eval runner (`agy -p ... --output-format json` / `opencode run --standalone --archived --format json`); (в) подтвердить политику «только идеи» для `sickn33` (`taste-skill` MIT и `anthropics/skills/skills/skill-creator` Apache-2.0 уже подтверждены); (г) задать ли целевые пороги perf ниже `make validate ≤1 s` / `make check ≤30 s` для `AUD-46`, `AUD-47`, `AUD-48`; (д) добавлять ли `cooldown` в `.github/dependabot.yml` (в `AUD-53` оставлено без изменений до решения владельца).
- **Защищённая история:** `CHANGELOG.md` (`v1.1.0`) не упоминал возврат загрузки SARIF Scorecard из `6bec3ee` после отключения в `1.0.1` — задним числом не переписывалось.

## Завершено (этапы 01–11)

Все `DONE` подтверждены `make check`/CI; следующий шаг — нет; неудачных попыток не зафиксировано. Первичные источники синтеза и лицензии зафиксированы в `THIRD_PARTY_NOTICES.md` и `skills/frontend-design/references/sources.md`.

| ID | Этап / трекер | Deps | Результат и доказательство |
|---|---|---|---|
| `AUD-01` | 01 · #14 | none | Release gate с `main`, signed annotated tag, ancestry, check-runs + workflow path, `release` env, `CHANGELOG` notes, archive/SHA-256/provenance (`v1.1.0` `b1f438d`). |
| `AUD-02` | 01 · #15 | `AUD-01` | Copy default, `realpath` guards, atomic staging/backups, `--copy` over symlink, `--all` kebab IDs, artifact exclusions, `~/`, folded YAML, `--verify`/`--ref`. |
| `AUD-03` | 01 · #16 | none | Валидация SKILL/cross-file anchors, frontmatter/body, AGENTS/PR template, 64 пары + 26 комбинаций WCAG 2.2 AA, `contrast.py` exit 0/1/2, negative/mutation fixtures. |
| `AUD-04` | 02 · #17 | `AUD-03` | `ubuntu-24.04`, Python 3.12, hash-locked deps, `make check`, `check_workflows.py`, job-scoped Dependency Review, бюджет `validate` ≤1 s / `check` ≤30 s. |
| `AUD-05` | 02 · #18 | none | `.gitignore` покрывает `.env*` (`!.env.example`), ключи, `secrets/`, `credentials*`, `.opencode/`/`.claude/`/`.agents/`; SHA-pinned `gitleaks 8.30.1`. |
| `AUD-06` | 02 · #19 | `AUD-03` | 32 KiB reading budget (`new-page` 32 462 B, 10 sets, `SKILL.md` 7 035 B), канонические токены/`sources.md`. |
| `AUD-07` | 03 · #20 | rel `01/04/06` | CODEOWNERS advisory, Scorecard SARIF/artifact 30d, `docs/repository-settings.md`, синхронизация `GOVERNANCE.md`. |
| `AUD-15` | docs · — | none | Правки `README`/`CONTRIBUTING`/`GOVERNANCE`/`SECURITY`/`CHANGELOG`/notices (`9a7804e`; residual `AUD-20` закрыт в `AUD-04`). |
| `SKL-01` | 04 · #27 | none | `skills/specification/SKILL.md` (спецификация без кода, вопросы, non-goals, acceptance, handoff). |
| `SKL-02` | 04 · #28 | `SKL-01` | `skills/implementation-planning/SKILL.md` (задачи 5–30 мин, файлы/интерфейсы, тесты, self-review, без hooks). |
| `SKL-03` | 04 · #29 | `SKL-02`, `SKL-05` | `skills/autonomous-execution/SKILL.md` (один писатель на файл, TDD-гейт, ledger, review, stop conditions, worktree). |
| `SKL-04` | 05 · #30 | `SKL-05` | `skills/systematic-debugging/SKILL.md` (reproduce → locate → hypothesize → fix → regression test). |
| `SKL-05` | 05 · #31 | none | `skills/test-driven-development/SKILL.md` (red-green-refactor, поведенческие тесты, три закона TDD). |
| `SKL-06` | 05 · #32 | `SKL-03` | `skills/code-review/SKILL.md` (свежий контекст, без self-approval, P0/P1/P2, response protocol). |
| `SKL-07` | 05 · #33 | `SKL-06` | `skills/delivery/SKILL.md` (evidence gate, PR/merge без обхода, cleanup, отчёт). |
| `SKL-08` | 05 · #34 | `SKL-05` | `skills/clean-code/SKILL.md` (behavior-preserving рефакторинг, конвенции репо выше эвристик). |
| `SKL-09` | 05 · #35 | `SKL-01`–`08` | `skills/skill-authoring/SKILL.md` (триггеры, progressive disclosure, tabletop matrix, атрибуция). |
| `ORC-01` | 06 · #38 | `SKL-03/06/07` | `skills/orchestration/SKILL.md`, `docs/opencode-orchestration.md`, `tests/test_skill_suite.py` (native orchestration без плагина/хуков). |
| `AUD-22` | 07 · #41 | `AUD-01`, `SKL/ORC` | Signed immutable release `v1.2.0` (`8f252ca`) с 11 навыками; `SHA256SUMS`, `gh attestation verify` PASS. |
| `AUD-23` | 07 · #42 | `AUD-01` | Публичный `docs/release-signing/allowed_signers` + `README.md`, `tests/test_release_signature.py`. |
| `AUD-24` | 07 · #43 | `ORC-01` | Правки drift docs (PR #49) + автопроверка путей тестов и счётчиков навыков в `tests/test_skill_suite.py`. |
| `AUD-25` | 07 · #44 | `SKL-09` | Table-driven trigger matrix + empty-workflow mutation в `tests/test_skill_suite.py`. |
| `AUD-26` | 07 · #45 | `AUD-03` | 3 focused tests simple-skill branch в `tests/test_validation.py`. |
| `AUD-27` | 07 · #46 | `ORC-01`, `SKL-09` | Anti-trigger/handoff `orchestration` → `autonomous-execution`. |
| `AUD-28` | 07 · #47 | audit | Первичное сжатие плана (`51 255 B → 34 274 B`, PR #50). |
| `AUD-29` | 07 · #48 | `AUD-03` | Module-scoped HTTP server в `tests/test_external_links.py` (`~2 s → ~0.55 s`). |
| `SKL2-01` | 08 · #58 | none | Plan header, interfaces, checkbox steps, checkpoints, `docs/plans/` ([план](plans/2026-11-16-skill-suite-v2.md), PR #62). |
| `SKL2-02` | 08 · #59 | `SKL2-01` | Ledger `.progress.md`, task briefs, BASE, `Ruling:`, 3-strike, per-task/final review, independent failure routing (PR #62). |
| `SKL2-03` | 08 · #60 | `SKL2-02` | Tests-first review, mutation check, 5 axes, severity, integration choice, post-merge verify, scope discipline (PR #62). |
| `SKL2-04` | 08 · #61 | `SKL2-01`–`03` | Trigger mining, baseline evals, pressure variants, versioning, licenses, attribution (PR #62; closeout #63 PR #64/#65). |
| `AUD-30` | 09 · #69 | none | Закрыт alert #13 (удалён `pip==26.3` в `ci.yml`), `scorecard.yml` на `permissions: {}` + guard, усилен `check_workflows.py`, удалён дубль workflows в `validate.py` (`f2fe34c`, PR #86). |
| `AUD-31` | 09 · #70 | none | OpenCode V2 frontmatter (`metadata`, `disable-model-invocation`, `compatibility`) и `UniqueKeySafeLoader` в `validate.py` (`f0c387a`, PR #88). |
| `AUD-32` | 09 · #71 | none | Выравнивание 6 workflow-навыков и `docs/opencode-orchestration.md` под OpenCode V2 (`26b3a45`, PR #93). |
| `AUD-33` | 09 · #72 | `AUD-31` | Path containment (`ROOT`/`skill_dir`), запрет симлинков в `skills/`, image-links, `docs.rglob`, общий контракт `reading-sets.json`, GFM-парсер (`f0c387a`, PR #88). |
| `AUD-34` | 09 · #73 | `AUD-31` | Усиление `install/opencode.sh` (YAML-парсер, запрет симлинков, `git archive` + `--ignored`, потоковый `tar` `6 104 → 2 049 ms` на 61 навыке, GNU-пробы, signal-restore; `8960221`, PR #91). |
| `AUD-35` | 09 · #74 | `AUD-30` | Усиление `release.yml`, `release_checks.py` (`gitleaks`, `timeout=30`, фильтрация до выбора, `fallback_cancelled`), `release_notes.py` и Sigstore bundle asset (`24e334f`, PR #92). |
| `AUD-36` | 09 · #75 | `AUD-30`, `AUD-44` | Исключение `node_modules`/`.venv` в `test_validation.py`, перевод unit-мутаций в in-process (`pytest` `23.65 s → 9.35 s`, `bc3b32e`, PR #90). |
| `AUD-37` | 09 · #76 | `AUD-33` | Исправления `frontend-design` (Baseline 2026, Next.js 16, `sources.md` MIT/ISO/WAI-ARIA 1.3, `light`+`dark` покрытие, string-aware CSS-парсер, `contrast.py`, запас `new-page` `306 → 1 357 B`; `6eb7458`, PR #94). |
| `AUD-38` | 09 · #77 | `AUD-31`, `AUD-32` | Синтез ноябрьских upstream-практик across 10 workflow-навыков, единые схемы ledger/brief и антитриггеры (`26b3a45`, PR #93). |
| `AUD-39` | 09 · #78 | `AUD-33` | Pruned `os.walk`, `ThreadPoolExecutor` (max 2/host), code-block фильтр и SSRF/DNS-rebinding защита в `check_external_links.py` (`42.85 → 14.87 s`; `758dc8e`, PR #95). |
| `AUD-40` | 09 · #79 | `AUD-36` | Структурный YAML/shell разбор в тестах, `.git`-free `test_release_signature.py`/`test_release_assets.py` (326/0 skipped), cross-skill isolation (`758dc8e`, PR #95). |
| `AUD-41` | 09 · #80 | none | Упорядочивание плана (`28465f1`): свёрнуты этапы 01–08, разделены оптимизации (`AUD-44`, `AUD-37`), проставлены нативные `blocked_by` (`3750c03`, PR #85). |
| `AUD-42` | 09 · #81 | `AUD-30`–`35`, `AUD-37`–`38` | Signed immutable release `v1.3.0` (`f633a27`, run `45772598608`, `verify-tag`/`SHA256SUMS`/online+offline `gh attestation verify` PASS; PR #97/#98 `66b9c9d`). |
| `AUD-43` | 09 · #82 | `AUD-30` | Обновление зависимостей (`ruff 0.17.6`, `PyYAML 6.0.4`, `markdownlint 0.24.2`, actions), `Analyze (actions)` + `gitleaks` в ruleset #27259237 и синхронизация `AGENTS.md` (PR #66/#87/#96/#97). |
| `AUD-44` | 09 · #84 | `AUD-30`, `AUD-33` | Однопроходный `validate.py` и in-process `contrast` (`189.96 → 73.03 ms`, CLI `248.9 → 161.2 ms`, `validate_repo(root)`; `83e4e99`, PR #89). |
| `AGY-01` | 10 · #99 | none | Строгий `name == skill_dir.name`, `compatibility: agentskills`, `allowed-tools` и `metadata` в `validate.py`; `agy plugin validate --json` 11/11, 0 ошибок ([план](plans/2026-11-27-antigravity-support.md), PR #104 `67c14fa`). |
| `AGY-02` | 10 · #100 | `AGY-01` | Унификация всех 11 навыков под Agent Skills и нативную оркестрацию Antigravity (0 OpenCode-терминов в `skills/`), `docs/antigravity-orchestration.md` (PR #104 `67c14fa`). |
| `AGY-03` | 10 · #101 | `AGY-01`, `AGY-02` | `install/antigravity.sh` (`~/.gemini/config/skills`) и общее ядро `install/lib.sh` рядом с `install/opencode.sh`, `.gemini/` в `.gitignore`, двойные `shellcheck -x`/`dry-run` (PR #105 `f6277cc`). |
| `AGY-04` | 10 · #102 | `AGY-02`, `AGY-03` | Обновление `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `THIRD_PARTY_NOTICES.md`, `docs/release-process.md`, `CHANGELOG.md` и шаблонов под Antigravity + OpenCode (PR #106 `bc8156d`). |
| `AGY-05` | 10 · #103 | `AGY-01`–`04` | Сквозная проверка `make check` (343 теста), `agy plugin validate` (11/11), hosted `Link Audit` (`45991442364` 75/75, `45992629239` 76/76), закрытие вехи #10 (PR #106 `bc8156d`) + оформление репозитория и signed immutable release [`v1.4.0`](https://github.com/snaplyze/skills-hub/releases/tag/v1.4.0) (PR #107 `f3465d0`, run `45992777582`, PR #108 `c187538`). |
| `AUD-52` | 11 · #117 | none | Упорядочивание плана (база `48529b6`): свёрнуты закрытые этапы 09–10, объединены гипотезы, удалены закрытая/опровергнутая гипотезы, разделена оптимизация тестов `test_installer.py` (`AUD-48` → `AUD-47`), дополнены поля шага 4 и проставлены нативные `blocked_by` в вехе #11. |
| `AUD-45` | 11 · #110 | none | Усилен релизный гейт (`.github/workflows/release.yml`, `scripts/release_checks.py`, `docs/release-process.md`, PR #122 `6178381`): `python3 -I` на всех 3 вызовах, проверка `%(tag) == $TAG` и заголовка `type commit`, пин `gate/` на `${{ github.sha }}`, отклонение `+build` SemVer до сборки активов, fail-closed для `id: null`/`(expected_path, None)` и `re.IGNORECASE` для `repo`, удалён мёртвый `gh_workflow_path`, усилены `test_release_{workflow,checks,signature}.py`. |
| `AUD-46` | 11 · #111 | none | Исправлен `scripts/validate.py` (PR #123 `7eb16fd`): fail-closed проверка всех `--color-*` токенов (вкл. 17 парных и 3 opted-out) и рекурсивный `var()` fallback с invalidation циклов; строгий запрет симлинков до `load_contrast_module` (`exec_module`) и в `skills/`/`docs/`/`.github/`/`check_yaml`; линейный `_scan_inline_links` (`K=100/500/1500/3000`: `1.51/39.74/349.56/1401.14 ms → 0.18/0.93/2.75/5.76 ms`, `243×` на `K=3000`; `validate_repo` `117.40 → 110.91 ms`) с однострочным переносом и исключением сносок `[^...]:`; YAML 1.2 bools, `\n` в `parse_frontmatter_text`, строгие `allowed-tools`/`reading-sets.json`/`MARKDOWN_SUFFIXES`, `UniqueKeySafeLoader` в `check_yaml`, удалены 9 мёртвых/избыточных символов и дубль `strip_fenced_code`. |
| `AUD-48` | 11 · #113 | none | Усилен и ускорен `install/lib.sh` + тесты (`test_installer.py`, `test_release_assets.py`, PR #124 `640d3ba`): `REF_SET=1` против `--ref ""`, абсолютные `XDG_CONFIG_HOME`/`HOME`, запрет симлинков в `--list`/`--list --verify` и pre-flight до `read_description`, `--no-same-permissions`, `((FORCE))` guard, явное предупреждение `--dry-run` при конфликтах, YAML-паритет `read_description` (ключи, `null`/`~`, `\/`, EOL `\`, незакрытый frontmatter), отложенные пробы `tar`/`mv`, однопроходный батч `find`/`tar` и `git ls-tree`/`git archive`, subshell-free YAML-хелперы (`copy` 11/31/61: `347.1/868.3/1814.5 → 141.5/349.3/635.9 ms`, `2.5–2.9×`; `--list`: `103.3/279.5/536.7 → 48.2/126.5/236.6 ms`, `2.1–2.3×`; `--verify` 11/31: `411.5/926.8 → 194.4/357.6 ms`, `2.1–2.6×`), проверены OpenCode non-XDG и наличие `install/{antigravity,opencode,lib}.sh` в релизном архиве. |
| `AUD-50` | 11 · #115 | none | Защищены `push`-проверки на `main` (`cancel-in-progress: ${{ github.event_name == 'pull_request' }}` в `ci.yml`/`codeql.yml`/`secret-scan.yml`), добавлен `concurrency` в `dependency-review.yml`, выведен tarball из `${GITLEAKS_VERSION}` с `curl --retry 3 --retry-delay 2 --max-time 60` в `secret-scan.yml`; в `scripts/check_workflows.py` сделан регистронезависимый `find()`, строгий XOR `uses`/`run` в шагах, расширен `UNTRUSTED_WRITE_RESTRICTED_EVENTS` (`issues`/`discussion`/`discussion_comment`/`fork`/`watch`) и запрещены симлинки `.github`/workflows (PR #125 `48e72f2`). |
| `AUD-51` | 11 · #116 | none | Исправлены дефекты контента `skills/` и контракты `tests/test_skill_suite.py` (PR #126 `1474f36`): синхронизированы `--container-2xl: 90rem` / `--gutter: clamp(1rem, 4vw, 2.5rem)` и 64 пары + 27 комбинаций в `design-system.md`, заменены `../assets/tokens.css` на `assets/tokens.css` в `visual-craft.md`, добавлен `#mobile-checklist` в TOC `responsive-mobile.md`, добавлены правила недоверенных данных (`frontend-design`, `orchestration`, `code-review`) и редактации секретов по `file:line` (`code-review`), обобщена портируемая оркестрация и синхронизированы поля ledger/brief в `autonomous-execution` (`new-page` `31 641 / 32 768 B`, запас `1 127 B`). |
| `AUD-49` | 11 · #114 | `AUD-46` | Выделен единый stdlib-модуль `scripts/_markdown.py` (совместимый с `python3 -I`, прямыми скриптами и `pytest`) и переведены `validate.py`, `check_external_links.py` и `release_notes.py` на общий CommonMark-парсер (PR #127 `624fdc1`): устранены 5 багов маскирования `check_external_links.py` (4-space fence, выход из blockquote, `` \` ``-экранирование, многострочный inline code, HTML-комментарии, разовая компиляция close-regex) и баги `release_notes.py` (HTML-комментарии, отступ H2 `[ ]{0,3}`); добавлены `"ignores"` в `.markdownlint-cli2.jsonc` (синхронизированы `Makefile`, `package.json`, `CONTRIBUTING.md`) и расширен `SKIP_DIRS` приватными каталогами (`venv`, `.mypy_cache`, `secrets`, `.gemini`, `.opencode`, `.claude`, `.agents`). |
| `AUD-47` | 11 · #112 | `AUD-45`, `AUD-46`, `AUD-48` | Устранены ложнозелёные тесты, утечки глобального Git-конфига и fan-out `pytest` (PR #128 `333b229`): создан общий `tests/_helpers.py` (`isolated_git_env`, `ISOLATED_GIT_CONFIG_ARGS`, единый quote-aware shell-парсер для `test_secrets.py`/`test_release_workflow.py`/`test_workflows.py`); починены `HEAD /redirect-trickle` (`405` + GET-счётчик), SSRF-редирект без мока `_is_global_ip`, `1 <= peak_in_flight <= 2` и добавлены тесты `MAX_REDIRECTS`/fallback/templates/CLI в `test_external_links.py`; зафиксированы 4 ключа `EXPECTED_WORKFLOWS`, `len(errors) == 1` на единичных поломках, `fallback_cancelled`/`wf_cache`/`gh_workflow_info` JSON+OSError/`main()` exit 1 в `test_release_checks.py`; проверены `fetch-depth: 0`, `sha256sum --check --strict`, `--exit-code 1` в `test_secrets.py` и структурный `ci.yml` + `ci.yaml` SHA-проверка в `test_workflows.py`; переведены юнит-мутации `test_validation.py` на точечные `check_skill`/`check_contrast_fixture`/`check_installer`, сняты 7 мутаций `validate.ROOT`, расширен `IGNORE` и добавлены проверки маскирования/`--root`/exit 2/placeholders/invalid YAML; консолидирован базовый git-шаблон в `test_installer.py`. Замеры в `.git`-free снимке (`624fdc1` → после): `pytest` `15.22 → 7.49 s` (`2.03×`), `test_validation.py` `8.61 → 2.08 s` (`4.14×`), `test_installer.py` `4.58 → 3.64 s` (`1.26×`); враждебный `GIT_CONFIG_GLOBAL` (`gpgsign=true`, `excludesFile`) и все 5 контрольных мутаций подтверждены. |
| `AUD-53` | 11 · #118 | `AUD-46`, `AUD-48` | Включён `$(RUFF) format --check .` в `Makefile` (`lint:` и `make check`, синхронизирован `CONTRIBUTING.md`, PR #129 `0ce64df`), `RUFF` лениво следует за `$(PYTHON) -m ruff` (с fallback на системный `ruff` при отсутствии модуля в `$(PYTHON)`, сохранением кавычек в `PYTHON=` и поддержкой явного `RUFF=`), все Python-файлы соответствуют `[tool.ruff.format]`; добавлены Keep a Changelog 1.1.0 footer-ссылки `[Unreleased]`..`[1.0.0]` в конец `CHANGELOG.md` без изменения тел релизов (`release_notes.py` проверен на `v1.0.0`–`v1.4.0`, все 7 URL вернули HTTP 200); `cooldown` в `.github/dependabot.yml` оставлен на решение владельца. |
| `AUD-54` | 11 · #119 | `AUD-46`, `AUD-47` | Ужесточён CSS Color 4 парсер в `skills/frontend-design/scripts/contrast.py` (строгий `CSS_NUMBER_RE`/`HUE_RE`, отказ на `1_00`, `100 %`, `12.deg`, 4-аргументный space-синтаксис без `/` и смешанные единицы в legacy comma `rgb()`, округление `alpha_byte < 255` в `Color.hex()`, clamping обоих входов в `flatten()`); добавлены 8 записей `combinations` по 5 недостающим парам (`accent-hover / canvas`, `text / accent-subtle`, `accent / accent-subtle` в обеих темах, `light: accent / surface-sunken`, `dark: border-strong / surface-raised (ui)` → `64 пары + 35 комбинаций`, синхронизированы `design-system.md`, `README.md`, `AGENTS.md`, `test_skill_suite.py`); в `scripts/validate.py` добавлены проверка префикса `f"{theme}:"` на `combinations` и запрет 27 зарезервированных slash-команд `RESERVED_SKILL_IDS` (синхронизировано с `skill-authoring/SKILL.md:20`); дополнены `test_contrast_cli.py` (полупрозрачный `bg`, `%`-alpha, негативные CSS Color 4, `hex`/`flatten`), динамизирована проверка доков в `test_skill_suite.py` (включая `docs/release-signing/README.md`), убран дубль `explore`/`general` и ослаблена хрупкость `V2_REQUIRED`, добавлен `-c versionsort.suffix=-` в `test_release_signature.py`. |

### Карта слияния и переноса ID

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
| `AUD-48` (консолидация git-шаблона `test_installer.py`) | `AUD-47` (`deps: AUD-45, AUD-46, AUD-48`) | разделение оптимизации продукта (`install/lib.sh`) и стоимости тестов (`tests/`) по шагу 3 + сериализация правок `test_installer.py` |
| Развёрнутые закрытые секции этапов 09 (`AUD-30`–`AUD-44`) и 10 (`AGY-01`–`AGY-05`) | Таблица `## Завершено (этапы 01–11)` | снятие журнального раздутия (`134 500 B` в `48529b6`) без потери ID, зависимостей и доказательств |
| Два раздела гипотез (`48529b6:156-166` и `:351-369`) | Единый `## Гипотезы (не задачи)` | один факт — одно место; удалены закрытая (`AUD-35` CodeQL cancel) и опровергнутая (`v5.0.1` `dependency-review` 403) гипотезы |

### История аудитов и ограничения

- `2026-11-15` (`2b4be4f`): все 7 областей → `AUD-01`–`AUD-07` DONE.
- `2026-11-15` (`977e2f2`): все 7 областей (снимок: 188 тестов, 11 навыков, 49/49 ссылок, `v1.1.0` проверен) → `AUD-22`–`AUD-29` DONE.
- `2026-11-26` (`5f0a620`, #68 / PR #83): все 7 областей + OpenCode V2 (`v2.4.1`) + 11 upstream-репозиториев → `AUD-30`–`AUD-44` (15/15 DONE, PR #85–#98, `v1.3.0`).
- `2026-11-27` (`c187538`, #109 / PR #120): все 7 областей (снимок `git archive`: 343 теста, 0 skipped, 11 навыков, `v1.4.0` проверен, `Link Audit` 76/76) → `AUD-45`–`AUD-54` (10/10 DONE).
- **Общие ограничения проверок:** не выполнялись контролируемый внешний fork PR, live `workflow_dispatch` с тегом в тесте, destructive installer, macOS/BSD runtime, UI WCAG, реальный LLM-токенайзер, upstream legal review `sickn33`; Python 3.9 не проверялся (floor 3.12).

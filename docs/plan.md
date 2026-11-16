# План

Трекер: https://github.com/snaplyze/skills-hub/issues; сверено 2026-11-16T20:01:11Z; этапы 01–08; аудит #41–#48: все DONE; этап #8: #58–#61 DONE; закрытые #14–#20, #27–#35, #38. Реестр — этот файл; план owner-facing, на русском, не загружается как инструкции агентов.

## Документы и стартовый контекст

| Документ | Роль | Строк / байт |
|---|---|---|
| `docs/plan.md` | реестр плана | 328 / 51 255 → 328 / 37 649 |
| `AGENTS.md` | project info и стартовый контекст | 47 / 6 758 |
| `README.md` | вход и установка | 336 / 18 223 |
| `docs/opencode-orchestration.md` | архитектура orchestration | 79 / 3 817 |
| `docs/release-process.md` | release gate и owner setup | 251 / 11 572 |
| `docs/repository-settings.md` | settings evidence | 75 / 4 912 |
| `docs/release-signing/` | публичный trust и ротация | 42 / 1 783 |
| `CONTRIBUTING.md`, `GOVERNANCE.md`, `SECURITY.md`, `CHANGELOG.md` | правила и история | 405 / 16 700 |
| `THIRD_PARTY_NOTICES.md` | атрибуция | 47 / 3 062 |
| `docs/plans/2026-11-16-skill-suite-v2.md` | детальный план этапа 08 | 281 / 10 726 |

Документы этапа: `README.md`, `CHANGELOG.md`, `THIRD_PARTY_NOTICES.md`, `docs/plans/2026-11-16-skill-suite-v2.md`; план обновлён; остальные не менялись. Задачи #58–#61 DONE; merge PR #62. Полный план: 37 649 B; детальный план: 10 726 B. План не входит в бюджет инструкций 32 KiB.

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
| 08 | Skill suite v2 (веха #8, closed) | SKL2-01 #58 DONE, SKL2-02 #59 DONE, SKL2-03 #60 DONE, SKL2-04 #61 DONE |

Порядок этапов: 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08. Очередь навыков: SKL-01 → SKL-02 → SKL-05 → SKL-03/SKL-04/SKL-08 → SKL-06 → SKL-07 → SKL-09. Исполнение не начинается до принятого spec/plan; review-gate обязателен на каждой задаче.

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
- Не проверено: fork PR, tag/release dispatch, destructive installer, UI WCAG, tokenizer/CI wall-time, upstream legal review; Python 3.9 runtime не проверялся (floor 3.12). Реестр относится к коммитам аудита; после них менялись только план и документы.

## Риски

- Release: custody/rotation подписывающего ключа; environment approval; owner bypass при создании тегов; full history; solo-review.
- Installer: `realpath -m` на не-GNU платформах; замена/бэкапы/частота обновлений.
- Validation/tests: edge cases Markdown/parser; flaky external links; semantic coverage; secret-scan false positives; стоимость suite.
- CI: churn lockfile/actions; ширина allowlist; drift runner/toolchain.
- Skills/plan: фрагментация контекста и link churn; tokenizer vs bytes; drift плана; upstream licensing.

## Гипотезы (не задачи)

- Fork PR может не пройти `dependency-review` из-за `comment-summary-in-pr: always`; проверить контролируемым fork PR.
- CI wall-time: локальный suite ~20 s; per-step timing на hosted не снят.
- CodeQL на docs-only PR может быть дорог; проверить `paths-ignore` без ослабления required checks.
- Токенизация references может отличаться от bytes/4; проверить tokenizer.
- Actions allowlist `verified_allowed` шире least privilege; сузить при необходимости.
- `require_extra_approval_for_unattributed_changes` при 0 approvals; проверить unverified email.
- name/ID portability вне OpenCode; проверить спецификации.
- «64 audited» provenance: fixture не содержит audit metadata.
- PR template relative link rendering; проверить GitHub UI.
- Upstream licensing/text-copying; нужен legal review.
- Alternate `<name>.md` skill layout; проверить harness.

## Владельцу / вне объёма

- Публичный `AGENTS.md` раскрывает локальные permissions/secret reads/`opencode-full`/MCP; перенести детали в приватный supplement. Это заметка владельцу, не задача.
- Глобальные permissions уже allow-all; `opencode-full` добавляет `--auto`. Если «только через обёртку» относится и к permissions — отдельное изменение пользовательской области.
- `opencode-full`, глобальные skills/MCP и их настройки существуют только у текущего пользователя; другие участники их не получат.
- `AGENTS.md §Оркестрация` от 2026-11-14 не содержит skill `report`; environment drift, обновить отдельно.
- Self-hosted раннеров нет; fork approval `all_external_contributors`; при добавлении нужен ответ владельца.
- Claude Code/Codex не установлены; загрузка не проверялась.
- Второй maintainer нужен для approvals/code-owner review.
- Upstream-лицензии двух источников требуют проверки.

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

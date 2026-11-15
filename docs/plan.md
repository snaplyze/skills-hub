# План

Трекер: https://github.com/snaplyze/skills-hub/issues; сверено 2026-11-15T11:00:00Z; вехи #1–#5; задачи #14–#20 закрыты; SKL-01–SKL-09 #27–#35; release v1.1.0. До сверки открытых продуктовых задач/вех не было; созданы по одной, дублей нет.

Реестр: этот файл. План — owner-facing registry на русском; он не загружается как инструкции агентов и не входит в бюджет 32 КиБ.

## Карта документов и стартовый контекст

| Документ | Роль | Было | После |
|---|---|---|---|
| `docs/plan.md` | реестр плана | 421 строка / 63 743 B | 251 строка / 37 313 B |
| `AGENTS.md` | project info | 47 / 5 834 B | 47 / 6 743 B |
| `README.md` | вход и установка | 244 / 10 557 B | 335 / 17 641 B |
| `CONTRIBUTING.md`, `GOVERNANCE.md`, `SECURITY.md`, `CHANGELOG.md` | правила и история | без изменений | обновлены по задачам |
| `THIRD_PARTY_NOTICES.md`, `skills/frontend-design/references/sources.md` | атрибуция | две копии | sources canonical; notices pointer |

Стартовый контекст задачи: `AGENTS.md` 6 743 B + раздел задачи 600–4 502 B + issue (`wc -c`) 712–1 990 B = 8 055–13 235 B. AGENTS + полный план + issue: 44 768–46 046 B; план не входит в бюджет инструкций. Было: 21 задача, 421 строка, 63 743 B; стало: 7 audit tasks DONE + 9 skills IN_REVIEW, 251 строка, 37 313 B. Исходный коммит правки плана: `9a7804ea459555105166b4e874c3c94a5fbe7284`; аудит-база: `2b4be4f`.

## Этапы

| # | Веха | Задачи |
|---|---|---|
| 01 | Release, installer, validation (веха #1) | AUD-01 #14, AUD-02 #15, AUD-03 #16 |
| 02 | CI, secrets, content (веха #2) | AUD-04 #17, AUD-05 #18, AUD-06 #19 |
| 03 | Protections (веха #3) | AUD-07 #20 |
| 04 | Agent workflow skills (веха #4) | SKL-01 #27, SKL-02 #28, SKL-03 #29 |
| 05 | Quality and delivery skills (веха #5) | SKL-04 #30, SKL-05 #31, SKL-06 #32, SKL-07 #33, SKL-08 #34, SKL-09 #35 |

Очередь навыков: SKL-01 → SKL-02 → SKL-05 → SKL-03/SKL-04/SKL-08 → SKL-06 → SKL-07 → SKL-09. Исполнение не начинается до принятого spec/plan; review-gate обязателен на каждой задаче.

## Аудит 2026-11-15

- Исходный коммит: `2b4be4f983af517d827b4ad8d42a13d804eaed44`; видимость: публичный репозиторий и трекер.
- Охват: архитектура, безопасность, данные, производительность, тесты, сборка/доставка, документация.
- Проверено: архитектура/скрипты/установщик; security config/API/history; data/fixtures/tokens; performance snapshot; tests/CI; build/delivery; docs.
- Не проверено: fork PR, tag/release creation, destructive installer, UI WCAG, tokenizer/CI wall-time, upstream legal review. Python 3.9 runtime не проверялся; floor поднят до 3.12.
- Реестр относится к коммиту аудита; изменения после него — только план и документы.

### Карта слияния ID

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

## Задачи

### AUD-01 — Release pipeline integrity

- **Было:** AUD-01, AUD-06, AUD-09.
- **Аудит:** 2026-11-15. **Тип:** security/release. **Приоритет:** P1. **Уверенность:** высокая. **Статус:** DONE.
- **Границы:** release workflow/tags/notes/provenance; no skill content or product behavior; no branch/runner settings without owner. **Исполнитель:** не назначен.
- **Результат:** релиз создаётся только с `main` и зелёными обязательными проверками; notes имеют один источник; теги подписаны/immutable; нет обхода PR/CI.
- **Доказательство:** `.github/workflows/release.yml:4-6,16-27` — любой `v*`, `contents: write`, `--verify-tag` (только existence), без ancestry/check-run и environment; tag ruleset `27259245` — только deletion/non-ff, creation не gated; releases assets 0, immutable false, теги без подписи; `.github/release.yml` labels не используются (на `2b4be4f` — 9 PR без labels), notes переписаны вручную; `GOVERNANCE.md §Releases` заявляет `main`; tag creation не gated.
- **Влияние:** unreviewed коммит публикуется как релиз; notes/provenance не воспроизводимы.
- **Решение:** (1) `fetch-depth: 0`, ancestry `merge-base --is-ancestor`, check-runs `validate`/`Analyze (python)`, protected environment, draft; (2) SemVer regex, `--prerelease`/`--latest=false`, tag creation restriction/required signatures; (3) выбрать labels+`.github/release.yml` или `CHANGELOG`-notes, добавить labeler/проверку версии; (4) подписывать теги, verification в workflow, immutable releases, checksums/attestations. Трудоёмкость 4–6 ч; риски: full history, approval-клик, signing keys.
- **Проверка:** тег вне `main`/без checks не создаёт release; notes воспроизводимы; `git tag -v` и immutable release.
- **Приёмка:** gate работает; успешный release с green `main` сохраняется; draft + manual promotion; notes один источник и воспроизводимы; CI проверяет версию; `updated_at == published_at` для новых релизов, если нет документированного ручного шага; tags signed; immutable + provenance опубликован; `GOVERNANCE`/README описывают фактический gate и совпадают.
- **Выполнено:** release workflow запускается только dispatch с `main`; проверяет подписанный annotated tag, ancestry `origin/main`, check-runs `validate`/`Analyze (python)` с ожидаемым workflow path, protected environment ref; immutable releases включены, release immutable=true; workflow не читает admin endpoint, настройка подтверждена владельцем; notes из CHANGELOG, draft, archive/SHA256/attestation. `release_notes.py`/`release_checks.py` покрыты тестами. Release v1.1.0 опубликован из signed tag `v1.1.0` (commit `b1f438d`), immutable=true; environment, trust variable, tag rules и checksum/attestation проверены.
- **Зависимости:** нет; AUD-02 — связанная (#15). **Трекер:** #14. **Следующий шаг:** нет. Signed release v1.1.0 опубликован, immutable=true. **Выводы неудачных попыток:** нет.

### AUD-02 — Installer safety and verifiable install

- **Было:** AUD-02, AUD-03, installer tests из AUD-11.
- **Аудит:** 2026-11-15. **Тип:** security/delivery. **Приоритет:** P2. **Уверенность:** высокая. **Статус:** DONE.
- **Границы:** installer and install docs; no skill content; tests only temp HOME/target; no real user config writes. **Исполнитель:** не назначен.
- **Результат:** installer не удаляет source/чужие каталоги; copy/force/list работают; есть tests; установка verifiable и versioned.
- **Доказательство:** `install/opencode.sh:98-100` guard только `""`/`/`/`$HOME`; `:180` `rm -rf`; `--target repo/skills` = source; `:168-172` `--copy --force` над symlink — no-op; `:128-137` `--all` без kebab regex; `:195` copy ignored artifacts; `:79-83` `~/` literal; `:116-118` folded `>`; symlink default `:192-193`; releases без assets; `v1.0.1` (`6c24112`) отстаёт от `main`.
- **Влияние:** data loss, ложная copy-установка, мутабельный глобальный skill, невозможность проверить версию.
- **Решение:** (1) `realpath -m`, refuse `/`/`$HOME`/repo/source/ancestors, symlink targets, control characters, NUL-safe `find`/`read`, `--` flags, temp+atomic, backup; (2) `--copy` заменяет symlink, `--all` regex, whitelist copy, `~/`, YAML description; (3) bats/plain-bash tests temp HOME/target для link/copy/force/conflict/list/refusal; (4) copy/verify default, release tar+sha/attestation, `--ref`, docs update. Трудоёмкость 1–1.5 дня; риски: cross-platform realpath, update friction.
- **Проверка:** target matrix отказывает; source tree неизменен; copy/force работают; tests; установка с тега/checksum.
- **Приёмка:** destructive target-кейсы не пишут вне target; source tree неизменен; `--copy --force` действительно копирует; `--all` отвергает невалидные ID; copy без ignored artifacts; `~/` раскрывается; folded description читается; tests покрывают link/copy/force/conflict/list/refusal; установка воспроизводима из тега и checksum проверяется; README различает main/release.
- **Выполнено:** `install/opencode.sh` — copy default, realpath/refuse guards, atomic staging/backups, `--copy` over symlink, `--all` IDs, ignored artifacts, `~/`, folded YAML, `--verify/--ref`; installer + release-archive/checksum/copy tests. Остаток: нет; archive/checksum/install проверены на v1.1.0.
- **Зависимости:** AUD-01 (#14) — release assets; AUD-03 (#16), AUD-04 (#17) — связанные. **Трекер:** #15. **Следующий шаг:** нет. Asset checksum/install проверены на v1.1.0. **Выводы неудачных попыток:** нет.

### AUD-03 — Validation correctness and token fixture

- **Было:** AUD-11, AUD-16, AUD-17.
- **Аудит:** 2026-11-15. **Тип:** tests/accessibility/data. **Приоритет:** P1. **Уверенность:** высокая. **Статус:** DONE.
- **Границы:** validator/tests/token fixture; no weakening required checks; no skill prose beyond token/fixture corrections. **Исполнитель:** не назначен.
- **Результат:** validator ловит SKILL/cross-file anchors, contrast failure/missing script, fixture shrink, semantic AA; frontmatter/body/links проверяются.
- **Доказательство:** `validate.py:137-142` skip SKILL; `:79,92` same-file anchors; `:169-186` только passing fixture; `contrast.py:397-398` return 1 не тестируется; `:172-173` silent skip; fixture 1/0 pairs проходит; mutation 75 KB/empty body проходит. Токены: `#6f695e` на `#d9eee1`/`#f8e3b8`/`#fbe0dd` = 4.48/4.32/4.36; `#237366` на `#f8e3b8` = 4.49; `#9b9587` на `#163a29` = 4.21; `#8a8478` на `#f8e3b8`/`#fbe0dd` = 2.95/2.97. `validate.py:83` skips http; `:190-197` не проверяет AGENTS/PR template; `MD_LINK_RE` ломает titled links.
- **Влияние:** entry-point links и accessibility gate могут исчезнуть; starter tokens дают AA-fail; contributor links/AGENTS не защищены.
- **Решение:** (1) negative suite: `tests/` на pytest/unittest с temp fixtures, SKILL/cross-file anchors, contrast exit 0/1/2 + missing script, fixture 64/32/32/unique/colors; (2) semantic role matrix, не Cartesian product, генерировать fixture из tokens или проверять каждое значение, fix AA или document unsupported, token/fixture doc-test; (3) frontmatter allowlist/non-empty body/SPDX, не требовать `name == dir`, Markdown parser для title/reference/root-relative/GitHub slug/duplicate/setext, AGENTS/PR template/.github, external lychee schedule/PR с cache/allowlist; (4) table-driven contrast rgb/hsl/alpha/named/json/quiet/stdin. Трудоёмкость 2–3 дня; риски: parser/anchors/flaky external.
- **Проверка:** mutations падают; 106 local links; AA supported; fixture/token parity; external broken link ловится.
- **Приёмка:** каждый документированный формат/ссылка и каждая проверка имеют pass/fail fixture; CI запускает suite; mutation любого guard обнаруживается; SKILL/AGENTS/PR template; 106 локальных ссылок staged tree; 64 pairs/AA; fixture/tokens parity; coverage gate — новый semantic token без пары валит validate; external link.
- **Выполнено:** validator проверяет SKILL/cross-file anchors, title/reference/root-relative links, frontmatter/body, fixture 64/32+32, semantic coverage, reading sets; contrast CLI tests exit 0/1/2; 64 pairs + 26 semantic combos AA; 45 external links PASS; 188 tests.
- **Зависимости:** нет; AUD-02 (#15), AUD-04 (#17), AUD-06 (#19) — связанные. **Трекер:** #16. **Следующий шаг:** нет. **Выводы неудачных попыток:** нет.

### AUD-04 — CI toolchain and workflow hardening

- **Было:** AUD-05, AUD-08, AUD-10, AUD-20.
- **Аудит:** 2026-11-15. **Тип:** CI/security/reproducibility. **Приоритет:** P2. **Уверенность:** высокая. **Статус:** DONE.
- **Границы:** CI/workflows/toolchain; no product behavior; no runner/branch/account settings without owner. **Исполнитель:** не назначен.
- **Результат:** одинаковые tool versions, один check entry point, workflow static policy, least privilege; CI routing: hosted-only, self-hosted 0, fork approval all external, без расхождений.
- **Доказательство:** `requirements-dev.txt` ranges; `ci.yml:39-40` pip upgrade; `:30-35` cache только pip; `:49,64` npx без lock; `:54-55` apt shellcheck; `ubuntu-latest`; `Makefile:32` unpinned csstree; `make check` 4 contrast/2 bash, CI 2 bash, ShellCheck missing local; `validate.py:205-223` parse-only; `dependency-review.yml:8-10` workflow-level `pull-requests: write`; `CHANGELOG` v1.0.1 overstates job scope. Раннеры: repo `total_count: 0`, все jobs `ubuntu-latest`, организация отсутствует, fork approval `all_external_contributors`; self-hosted нет.
- **Влияние:** проверки дрейфуют, supply-chain, CI/local divergence, неверный security claim.
- **Решение:** (1) pin runner/Python и pip, pip hashes, npm lock/cache/Dependabot, ShellCheck pin/remove, csstree pin; (2) один `make check`/CI entry point, contrast/bash once, читать файлы один раз, ShellCheck local or documented; (3) actionlint/zizmor/check-jsonschema, SHA/version/permissions/timeouts/persist-credentials/pull_request_target checks; (4) Dependency Review write в job scope, future changelog correction. Трудоёмкость 1–2 дня; риски: lockfile churn, tool allowlist, runner drift.
- **Условие:** self-hosted сейчас нет; если появится — owner input о платформе/метках/ОС/архитектуре/группе/доступе, suitable jobs на self-hosted, fork code остаётся hosted, fork approval для self-hosted.
- **Производительность:** путь `.github/workflows/ci.yml`; нагрузка — pip/npm acquisition и тестовый suite; baseline — старый `make check` 866 ms без pytest; сейчас `make validate` ~0.3 s, полный `make check` ~20 s, coverage 188 tests. Инвариант — те же проверки и coverage; старый лимит 810 ms к расширенному suite неприменим; владелец принял бюджет ≤1 s / ≤30 s; сравнение — per-step timing/cache hit; удалить — duplicate contrast/bash и лишние installs.
- **Проверка:** одинаковые `pip freeze`/`npm ls` + cache hit; один проход; unsafe workflow fails; least privilege; runtime документирован (~0.3 s validate / ~20 s full check); Scorecard Pinned-Dependencies ≥9; смена версии требует commit.
- **Приёмка:** reproducible toolchain с hash/lock; npm cache hit и npm Dependabot; нет unpinned install; один проход проверок; docs/CI согласованы; unsafe workflow не проходит static analysis; least privilege/job-scope write; runtime документирован (~0.3 s validate / ~20 s full check; старый 810 ms — baseline без pytest); coverage 188 tests; Python floor 3.12+ подтверждён CI.
- **Выполнено:** CI на `ubuntu-24.04`, Python 3.12, pip 26.3, hash-locked Python/npm, `npm ci` cache; `make check` — единый вход; workflow policy проверяет 7 файлов; Dependency Review write в job scope; 188 tests. `make validate` ~0.3 s, полный `make check` ~20 s; старый 810 ms относился к набору без pytest; владелец принял новый бюджет `make validate` ≤1 s / `make check` ≤30 s.
- **Зависимости:** AUD-03 (#16) — tests; AUD-01 (#14), AUD-02 (#15), AUD-06 (#19), AUD-07 (#20) — связанные. **Трекер:** #17. **Следующий шаг:** нет. Владелец 2026-11-15 принял бюджет: `make validate` ≤1 s, `make check` ≤30 s на hosted runner. **Выводы неудачных попыток:** нет.

### AUD-05 — Secret handling and ignore guard

- **Было:** AUD-04.
- **Аудит:** 2026-11-15. **Тип:** security. **Приоритет:** P2. **Уверенность:** высокая. **Статус:** DONE.
- **Границы:** .gitignore/secret scan; no secret values; AGENTS caveat update separate. **Исполнитель:** не назначен.
- **Результат:** `.env*`/ключи/client dirs игнорируются; secret scan в CI; non-provider patterns включены или документированы.
- **Доказательство:** `.gitignore` не содержит `.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`, `secrets/`, `credentials*`, `.opencode/`, `.claude/`, `.agents/`; `git check-ignore` NOT-IGNORED для перечисленных; API non-provider/validity disabled; `AGENTS.md` требует manual index check; 0 alerts сейчас.
- **Влияние:** случайный `git add -A` публикует credentials; push protection покрывает только provider patterns.
- **Решение:** ignore patterns + `!.env.example`; enable non-provider/validity если доступно; pinned gitleaks CI/pre-commit; после изменения обновить AGENTS (отдельно). Трудоёмкость 2–3 ч; риски: false positives.
- **Проверка:** `git check-ignore`; secret scan; нет tracked secret-like files.
- **Приёмка:** пути ignored; `.env.example` разрешён; CI scan; AGENTS caveat снят.
- **Выполнено:** `.gitignore` покрывает `.env*`, ключи, `secrets/`, `credentials*`, agent dirs; `Secret Scan` скачивает gitleaks 8.30.1 по HTTPS с SHA-256, сканирует историю; 41 CI/secret test; `git check-ignore` PASS. Non-provider/validity scanning остаются owner-only и записаны в `docs/repository-settings.md`.
- **Зависимости:** нет; AUD-03 (#16) — связанная. **Трекер:** #18. **Следующий шаг:** владелец может включить non-provider/validity scanning; кодовая часть завершена. **Выводы неудачных попыток:** нет.

### AUD-06 — Skill content and instruction budget

- **Было:** AUD-07, AUD-14, AUD-18, AUD-19.
- **Аудит:** 2026-11-15. **Тип:** content/performance/docs. **Приоритет:** P2. **Уверенность:** высокая. **Статус:** DONE.
- **Границы:** skill docs/assets and AGENTS project info; no product behavior or code/CI. **Исполнитель:** не назначен.
- **Результат:** бюджет инструкций определён/уложен; tokens canonical; references не противоречат; один template/attribution; AGENTS plan/description точны.
- **Доказательство:** `design-direction.md` 35 017 B; typical set 85 527 B; no size check; `design-system.md:567` OKLCH vs tokens hex, focus/accent/Archivo/shadows mismatch; `design-direction.md:735-737` 240/120 ms vs motion 40–80/80–150–480; `accessibility.md:437` 44 px Apple vs 44 pt; `responsive-mobile.md:336` vs `implementation.md:380` JS budgets; `quality-gates.md`/`assets/audit-report.md` two templates; design brief duplicate; notices/sources 3 lists; `SKILL.md:332` subset; `AGENTS.md §План` stale, description only-text claim.
- **Влияние:** context cost/truncation, copied theme/motion/unit/budget errors, duplicate maintenance, attribution drift, agent confusion.
- **Решение:** (1) определить scope 32 KiB, split/trim design-direction, update routing/reading, size gate; (2) tokens canonical, fix references/motion/units/budgets, doc-test; (3) canonical audit/design templates, one source registry/parity, full attribution; (4) update AGENTS plan/description отдельным PR. Трудоёмкость 1–2 дня; риски: fragmentation, link churn.
- **Производительность:** путь `SKILL.md` routing + references; нагрузка — байты, загружаемые на задачу; baseline — design-direction 35 017 B, typical set 85 527 B; инвариант — все требования и progressive disclosure; цель — 32 KiB из AGENTS.md; сравнение — `wc -c` до/после; удалить — дубли/лишние разделы, worked example в asset при необходимости.
- **Проверка:** documented set ≤32 KiB; no conflicting values; one template; parity; AGENTS; doc-test.
- **Приёмка:** budget scope документирован; чтение ≤32 KiB; CI ловит oversize reference; references/tokens/motion/units/budgets не противоречат; doc-test зелёный; ровно один шаблон каждого артефакта; sources/attribution parity; AGENTS project info/plan/skill listing совпадают.
- **Выполнено:** SKILL 7 035 B; visual-craft 9 201 B; 10 reading sets, new-page 32 462 B с design-brief; worked-example явно excluded; исправлены tokens/motion/units/budgets/templates/attribution; `make check` PASS, 188 tests. См. `assets/reading-sets.json`.
- **Зависимости:** AUD-03 (#16) — token test; AUD-04 (#17), AUD-07 (#20) — связанные. **Трекер:** #19. **Следующий шаг:** нет. **Выводы неудачных попыток:** нет.

### AUD-07 — Repository protections and evidence

- **Было:** AUD-12, AUD-13, AUD-21.
- **Аудит:** 2026-11-15. **Тип:** security/docs. **Приоритет:** P3. **Уверенность:** высокая. **Статус:** DONE.
- **Границы:** CODEOWNERS/ruleset docs/settings evidence; no access changes without owner. **Исполнитель:** не назначен.
- **Результат:** CODEOWNERS advisory/enforced; approvals/signatures policy; Scorecard trigger/visibility; settings evidence.
- **Доказательство:** `.github/CODEOWNERS:1-9`; ruleset 0 approvals/no codeowner/no signatures; `GOVERNANCE.md §Review and merge policy`; `scorecard.yml:4` `branch_protection_rule` dead при rulesets, no `repository_ruleset`; SARIF не в code scanning, artifact 5 дней; README/SECURITY/GOVERNANCE claims без in-repo evidence/даты.
- **Влияние:** appearance of review; weekly protection regression; stale security claims.
- **Решение:** (1) CODEOWNERS advisory comment; при втором maintainer — approvals=1, codeowner, signatures, emergency path; (2) `branch_protection_rule` + weekly schedule (Actions не поддерживает `repository_ruleset`), concurrency, SARIF и retention 30 дней; (3) `docs/repository-settings.md` setting/where/owner/verified date. Трудоёмкость 1–2 ч + второй maintainer; риски: solo block.
- **Проверка:** ruleset/docs совпадают; branch-protection edit triggers Scorecard; rulesets — weekly; evidence date.
- **Приёмка:** advisory/enforced clear; trigger works; claims/evidence/date совпадают; settings evidence.
- **Выполнено:** CODEOWNERS явно advisory; Scorecard triggers `branch_protection_rule`, weekly, push; ruleset changes покрываются weekly, потому что Actions не поддерживает `repository_ruleset`; SARIF в code scanning, artifact 30 дней; `docs/repository-settings.md` фиксирует settings/date/owner actions; claims синхронизированы. Ruleset/approvals не менялись без владельца.
- **Зависимости:** AUD-01 (#14), AUD-04 (#17), AUD-06 (#19) — связанные. **Трекер:** #20. **Следующий шаг:** при втором maintainer включить approvals/code-owner review; сейчас advisory. **Выводы неудачных попыток:** нет.

## Навыки 2026-11-15

Источники: [obra/superpowers](https://github.com/obra/superpowers) (MIT, Jesse Vincent) и [sickn33/agentic-awesome-skills clean-code](https://github.com/sickn33/agentic-awesome-skills/tree/main/skills/clean-code) (MIT/CC BY 4.0). Навыки — оригинальный синтез; без хуков, плагинов и копирования текста. Проверка: `python3 scripts/validate.py` (10 skills), `tests/test_skill_suite.py`, `make check` 188 tests.

### SKL-01 — Specification

- **Источник:** brainstorming/specification.
- **Результат:** запрос превращается в короткую проверяемую спецификацию: проблема, пользователь, результат, non-goals, ограничения, acceptance, риски и открытые вопросы.
- **Приёмка:** шаблон и правила вопросов; запрет выдумывать требования; handoff в планирование; валидация ссылок.
- **Выполнено:** Инструкция и шаблон в `skills/specification/SKILL.md`; проверены description, links, anti-trigger.
- **Границы:** не писать код, не заменять исследование кода вопросами. **Зависимости:** нет. **Статус:** IN_REVIEW. **Трекер:** #27.

### SKL-02 — Implementation planning

- **Источник:** writing-plans.
- **Результат:** спецификация превращается в исполнимый план: задачи по 5–30 минут, точные файлы/интерфейсы, тесты, зависимости, проверки, риски и порядок.
- **Приёмка:** шаблон плана, критерии task size, self-review, handoff в исполнение; без hooks. **Границы:** план, не реализация. **Зависимости:** SKL-01. **Статус:** IN_REVIEW. **Трекер:** #28.
- **Выполнено:** Инструкция и шаблон в `skills/implementation-planning/SKILL.md`; task size, tests, dependencies, handoff.

### SKL-03 — Autonomous execution

- **Источник:** executing-plans, subagent-driven-development, dispatching-parallel-agents, using-git-worktrees.
- **Результат:** утвержденный план исполняется автономно: worktree только при необходимости, один писатель на файл, параллельные независимые задачи, TDD-гейт, ledger, review, stop conditions.
- **Приёмка:** брифы субагентов, правило одного писателя, ledger/план, review-gate, проверки после задач, финальный diff/тесты. **Границы:** без hooks/plugin. **Зависимости:** SKL-02, SKL-05. **Статус:** IN_REVIEW. **Трекер:** #29.
- **Выполнено:** Инструкция в `skills/autonomous-execution/SKILL.md`; субагенты, один писатель, review-gate, worktree, ledger, stop conditions.

### SKL-04 — Systematic debugging

- **Источник:** systematic-debugging.
- **Результат:** сначала воспроизведение и root cause, затем минимальный fix и regression test; запрет shotgun-фиксов.
- **Приёмка:** фазы reproduce/locate/hypothesize/fix, evidence, red flags, no-root-cause path. **Зависимости:** SKL-05. **Статус:** IN_REVIEW. **Трекер:** #30.
- **Выполнено:** Инструкция в `skills/systematic-debugging/SKILL.md`; reproduce/locate/hypothesis/fix и regression test.

### SKL-05 — Test-driven development

- **Источник:** test-driven-development + clean-code testing.
- **Результат:** red-green-refactor с наблюдаемым падением теста, поведенческими тестами, минимальным кодом и полным regression run.
- **Приёмка:** три закона TDD, качества тестов, bugfix flow, anti-patterns, coverage без театра. **Зависимости:** нет. **Статус:** IN_REVIEW. **Трекер:** #31.
- **Выполнено:** Инструкция в `skills/test-driven-development/SKILL.md`; iron law, three laws, red-green-refactor, test quality, bugfix flow.

### SKL-06 — Code review

- **Источник:** requesting-code-review + receiving-code-review.
- **Результат:** свежий контекст ревьюера получает spec/diff/tests/риски; feedback проверяется, классифицируется и принимается/отклоняется с evidence.
- **Приёмка:** шаблон запроса, severity P0/P1/P2, response protocol, no performative agreement, no self-approval. **Зависимости:** SKL-03. **Статус:** IN_REVIEW. **Трекер:** #32.
- **Выполнено:** Инструкция в `skills/code-review/SKILL.md`; request/receive, P0/P1/P2, evidence.

### SKL-07 — Delivery

- **Источник:** verification-before-completion + finishing-a-development-branch.
- **Результат:** completion доказывается свежими командами; PR/merge/cleanup выполняются без обхода проверок и с проверкой main.
- **Приёмка:** evidence gate, diff/check/PR checklist, merge rules, cleanup, completion report. **Зависимости:** SKL-06. **Статус:** IN_REVIEW. **Трекер:** #33.
- **Выполнено:** Инструкция в `skills/delivery/SKILL.md`; evidence gate, PR/merge/no-bypass, cleanup.

### SKL-08 — Clean code

- **Источник:** clean-code + clean-code skill.
- **Результат:** язык-агностичный рефакторинг: имена, маленькие единицы, границы, ошибки, дублирование, связность, тесты; конвенции репозитория выше эвристик.
- **Приёмка:** decision framework, refactor loop, checklist, anti-patterns, preservation of behavior. **Зависимости:** SKL-05. **Статус:** IN_REVIEW. **Трекер:** #34.
- **Выполнено:** Инструкция в `skills/clean-code/SKILL.md`; behavior-preserving refactor, smells, checklist.

### SKL-09 — Skill authoring

- **Источник:** writing-skills.
- **Результат:** новый OpenCode-навык имеет trigger-rich description, компактный workflow, progressive disclosure, pressure tests и repo integration.
- **Приёмка:** шаблон, baseline-vs-skill test, tabletop trigger matrix, link/validation, attribution; поведенческие evals не заявляются без прогона. **Зависимости:** SKL-01–SKL-08. **Статус:** IN_REVIEW. **Трекер:** #35. **Проверка:** tabletop trigger matrix; behavioral evals не запускались, это указано как ограничение.
- **Выполнено:** Инструкция в `skills/skill-authoring/SKILL.md`; trigger tests, pressure tests, repo integration.

## Выполнено

**AUD-15 — documentation corrections.** DONE 2026-11-15. Исправлены README/CONTRIBUTING/GOVERNANCE/SECURITY/CHANGELOG/notices: `make check` vs CI, Node 22+, `--force` deletion scope, release-gate wording, tag creation, skills table, license qualifiers, description trigger. Residual AUD-20 tracked in AUD-04. Доказательство: `git show 9a7804e`, CI #12 PASS.

## Гипотезы (не задачи)

- Fork PR может не пройти `dependency-review` из-за `comment-summary-in-pr: always`; проверить контролируемым fork PR.
- CI wall-time: локальный полный suite ~20 s; per-step timing на hosted ещё не снят.
- CodeQL на docs-only PR может быть дорог; проверить paths-ignore без ослабления required checks.
- Токенизация references может отличаться от bytes/4; проверить tokenizer.
- Actions allowlist `verified_allowed` шире least privilege; сузить при необходимости.
- `require_extra_approval_for_unattributed_changes` при 0 approvals; проверить unverified email.
- name/ID portability вне OpenCode; проверить спецификации.
- «64 audited» provenance; fixture не содержит audit metadata.
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
- Продуктовые исправления не начинались; для них — отдельное выполнение задач плана.

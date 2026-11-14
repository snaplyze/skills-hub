# План

Трекер: не связан; issue #11 — только публикация документов аудита.

- Дата аудита: 2026-11-15
- Исходный коммит: `2b4be4f983af517d827b4ad8d42a13d804eaed44`
- Видимость: публичный репозиторий и публичный трекер
- Охват: архитектура, безопасность, данные, производительность, тесты, сборка и доставка, документация

План ведётся на русском как owner-facing registry; он не загружается как инструкции агентов и не входит в бюджет 32 КиБ.

## Аудит 2026-11-15

### Охват и статус

| Область | Статус | Проверено | Не проверено |
|---|---|---|---|
| Архитектура | проверено частично | структура, скрипты, валидатор, установщик, дублирование, границы слоёв | масштабирование на десятки навыков — только синтетический прогон |
| Безопасность | проверено | конфигурация и API, история, секреты, workflows, установщик статически, правила | динамические destructive-тесты, fork PR, реальные секреты |
| Данные | проверено частично | frontmatter, ссылки, fixture, токены, числа и пути | upstream-лицензии и внешние источники — заявлены, но юридически не проверены |
| Производительность | проверено частично | замеры в снимке, профиль, дубли, размеры | реальное время GitHub Actions, токенизация модели |
| Тесты | проверено | self-test, validator, CI, отсутствующие покрытия | динамические тесты установщика не запускались |
| Сборка и доставка | проверено частично | workflows, rulesets, runners, релизы, API, история | fork PR, создание тега/релиза, environment approval |
| Документация | проверено | README, CONTRIBUTING, SECURITY, GOVERNANCE, CHANGELOG, AGENTS, шаблоны; независимое read-only ревью PASS 2026-11-15 | — |

### Сводка приоритетов

- **P1:** AUD-01 — release-workflow обходит PR/CI-контроль через любой `v*`-тег; AUD-11 — валидатор даёт ложные зелёные на `SKILL.md`, cross-file anchors, contrast failure и fixture count; AUD-17 — semantic token combinations не проходят AA и не покрыты fixture.
- **P2:** AUD-02 — небезопасный `--force`/path-guard установщика; AUD-03 — мутабельная symlink-установка и отсутствие verifiable release; AUD-04 — `.env*`/ключи не игнорируются; AUD-05 — неpinned toolchain; AUD-06 — три источника release notes; AUD-07 — бюджет инструкций нарушен и не enforced; AUD-14 — AGENTS.md устарел относительно плана/инвентаря; AUD-16 — неполная проверка frontmatter/body, contrast parser/CLI и ссылок; AUD-18 — skill references противоречат tokens/motion/units/budgets; AUD-20 — Dependency Review workflow-level write и ложная запись changelog.
- **P3:** AUD-08 — дубли и расхождение локальных/CI-проверок; AUD-09 — unsigned tags и mutable releases; AUD-10 — нет workflow static analysis; AUD-12 — CODEOWNERS/ревью/подписи; AUD-13 — Scorecard triggers/visibility; AUD-19 — дубли шаблонов и атрибуции; AUD-21 — нет in-repo evidence для GitHub settings claims.
- **DONE:** AUD-15 — подтверждённые неточности документов исправлены в этом аудите.

### Задачи

«Зависимости» — информационные связи, а не жёсткий порядок. Цикл означает, что задачи можно вести параллельно; блокирующая зависимость отмечается явно.

#### AUD-01 — Release workflow публикует любой `v*`-тег с любого коммита

- **Аудит:** 2026-11-15
- **Тип:** security / release integrity
- **Приоритет:** P1 — обходит защищённый `main`, обязательные проверки, CodeQL и ревью на пути, которым пользуются потребители; тег после публикации удалить нельзя без изменения защиты.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** релиз может создать только коммит, входящий в `main` и имеющий успешные обязательные проверки; публикация требует явного approval; случайный/чужой тег не создаёт релиз.
- **Доказательство:** `.github/workflows/release.yml:4-6` — `on: push: tags: ["v*"]`; `:16-17` — `contents: write`; `:24-27` — `gh release create ... --verify-tag`, без проверки ancestry и check-runs. Tag ruleset `27259245` содержит только `deletion` и `non_fast_forward`, без `creation`/`required_signatures`; `bypass_actors: []`. `GOVERNANCE.md §Releases` заявляет теги с `main`, но это не enforced. `--verify-tag` проверяет только существование тега.
- **Влияние:** write-capable актор или ошибочный тег публикует unreviewed контент; пользователи получают его как релиз; удаление тега заблокировано.
- **Зависимости:** AUD-09 (подписи/immutability), AUD-03 (verifiable release).
- **Решение:** checkout с `fetch-depth: 0`; проверить `git merge-base --is-ancestor "$GITHUB_SHA" origin/main`; запросить check-runs для SHA и требовать `validate` и `Analyze (python)`; поместить job в protected environment с reviewer; публиковать draft и требовать ручного promotion; ограничить создание тегов контролируемым workflow или `creation`-правилом; добавить `--prerelease` для суффиксов и `--latest=false` для backport. Трудоёмкость: 2–4 ч; риски: дополнительный клик и full history.
- **Проверка:** тег на коммит вне `main` и тег без зелёных проверок завершают job с ошибкой и не создают release; тег с зелёного `main` проходит.
- **Следующий шаг:** добавить ancestry- и check-run-gate в `release.yml`, затем environment approval.
- **Приёмка:** ни один `v*`-тег вне `main`/без проверок не публикуется; успешный сценарий сохраняется; docs описывают фактический gate.
- **Выводы неудачных попыток:** нет.

#### AUD-02 — Установщик можно заставить удалить исходники или чужой каталог

- **Аудит:** 2026-11-15
- **Тип:** security / destructive operation
- **Приоритет:** P2 — data loss, требует `--force` и необычного target, но blast radius включает source tree и пользовательские каталоги.
- **Уверенность:** высокая (статический разбор; destructive-тесты не запускались)
- **Статус:** OPEN
- **Результат:** installer отказывается от небезопасных target/source, не удаляет source tree, не следует symlink-корням и не принимает невалидные имена из `--all`.
- **Доказательство:** `install/opencode.sh:98-100` отвергает только `""`, `/`, `$HOME`, без canonicalization; `:161-166` проверяет строковый префикс и basename; `:180` выполняет `rm -rf "$target_dir"`; `--target "$REPO_ROOT/skills"` делает `target_dir == source_dir`; `:168-172` `--copy --force` над существующим symlink молча выходит с 0, оставляя symlink; `:104-107`, `:128-137` — `--all` не применяет kebab-case regex; `:195` `cp -R` копирует игнорируемые `__pycache__`/`.pyc`; `:79-83` `--target '~/x'` создаёт буквальный `~`; `:116-118` `--list` печатает `>` для folded YAML; `:190-195` — `mkdir/ln/cp` без `--`; `:115-119` выводит сырые имена/описания. Функциональных тестов установщика нет.
- **Влияние:** `--force --target "$HOME/"`/`//`/`repo/skills` может удалить каталог с именем навыка или исходник; symlink target root обходит guard; `--copy --force` врёт о переходе на copy; `--all` устанавливает невалидное имя; copy тащит `__pycache__`; `~/` создаёт мусорный каталог.
- **Зависимости:** AUD-11 (тесты установщика).
- **Решение:** канонизировать target/source через `realpath -m`; запретить `/`, `$HOME`, repo root, `repo/skills`, source и его предков/потомков; отвергать symlink target/source/SKILL.md; использовать `rm -rf --`, `mkdir -p --`, `ln -s --`, `cp -R --`; стадировать во временный каталог и атомарно заменять; `--copy` при существующем symlink должен заменять его, а не `continue`; применять kebab-case regex ко всем `--all`; раскрывать `~/`; копировать по whitelist/исключать `__pycache__`, `.pyc`, `.ruff_cache`, `node_modules`; парсить folded description или не печатать description; отклонять control characters; `find -print0`/`read -d ''`; добавить bats/plain-bash тесты с temp HOME/target для link/copy/force/conflict/symlink-to-copy/list/refusal. Трудоёмкость: 0.5–1 день; риски: cross-platform `realpath`, backup.
- **Проверка:** матрица target (`/`, `//`, `$HOME`, `$HOME/`, `$HOME/.`, `repo/skills`, symlink root, `-`-prefix) отказывает; source tree не меняется; `--all` отвергает невалидные имена; `bash -n` и ShellCheck чисты.
- **Следующий шаг:** добавить canonicalization и refuse-список до любых `rm`.
- **Приёмка:** destructive target-кейсы не пишут вне target; source tree неизменен; `--copy --force` действительно копирует; `--all` отвергает невалидные имена; copy без ignored artifacts; `~/` раскрывается; folded description читается; тесты покрывают отказы.
- **Выводы неудачных попыток:** нет.

#### AUD-03 — Symlink-установка доверяет мутабельному clone; релизы не verifiable

- **Аудит:** 2026-11-15
- **Тип:** supply chain / delivery
- **Приоритет:** P2 — глобально загружаемые инструкции меняются при `git pull`/checkout без reinstall; релизы не имеют assets/checksum.
- **Уверенность:** высокая по механике, средняя по эксплуатации
- **Статус:** OPEN
- **Результат:** установка либо копирует pinned-содержимое, либо проверяет подписанный тег/checksum; пользователь понимает разницу между `main` и релизом.
- **Доказательство:** `install/opencode.sh:192-193` по умолчанию `ln -s "$source_dir" "$target_dir"`; `README.md §Install` документирует symlink; installer не проверяет checksum/signature; API releases `assets: []`; `v1.0.1` (`6c24112`) отстаёт от `main` (`2b4be4f`); `README`/`SECURITY.md` говорят о latest release, но установка идёт из рабочей копии.
- **Влияние:** смена ветки/PR-checkout меняет глобально доверенный skill; нет способа проверить, что установлено; релизный badge вводит в заблуждение.
- **Зависимости:** AUD-01 (release gate), AUD-09 (подписи), AUD-05 (toolchain).
- **Решение:** сделать `--copy` default или добавить `--verify` с signed tag/checksum; публиковать `tar.gz` + `.sha256`/attestation из тега; добавить `--ref vX.Y.Z`/документировать `git clone --branch`; явно разделить «latest release» и «main». Трудоёмкость: 2–4 ч; риски: обновление требует reinstall, Windows symlink.
- **Проверка:** checkout другой ветки не меняет установленный skill; `--verify` отклоняет неверный checksum/неподписанный тег; install с тега даёт содержимое тега.
- **Следующий шаг:** определить default (copy/verify) и добавить release asset generation.
- **Приёмка:** установка воспроизводима из тега; checksum проверяется; README различает main/release.
- **Выводы неудачных попыток:** нет.

#### AUD-04 — `.env*` и ключи не игнорируются; non-provider secret scanning выключен

- **Аудит:** 2026-11-15
- **Тип:** security / secret handling
- **Приоритет:** P2 — публичный репозиторий; случайный `git add -A` может опубликовать credentials; push protection покрывает только известные provider patterns.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** секретоподобные файлы игнорируются, сканируются в CI/локально, а документация не требует ручной проверки индекса.
- **Доказательство:** `.gitignore` не содержит `.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`, `secrets/`, `credentials*`, `.opencode/`, `.claude/`, `.agents/`; `git check-ignore` возвращает NOT-IGNORED для `.env`, `.env.local`, `secrets/credentials.json`, `id_rsa`, `foo.pem`, `server.key`. API `security_and_analysis`: secret scanning/push protection enabled, non-provider patterns/validity checks disabled. `AGENTS.md §Неочевидные` предупреждает, что `.env*` не покрыт.
- **Влияние:** generic secrets/private keys/connection strings не блокируются; публикация необратима; история чистая только сейчас.
- **Зависимости:** AUD-11 (secret-scan test), AUD-15 (docs).
- **Решение:** добавить ignore-паттерны с `!.env.example`; включить non-provider patterns/validity checks, если доступны; добавить pinned secret scan (gitleaks) в CI/ pre-commit; обновить AGENTS после изменения ignore. Трудоёмкость: 1–2 ч; риски: false positives, не игнорировать примеры.
- **Проверка:** `git check-ignore` для списка; CI secret scan на чистом дереве; нет tracked secret-like files.
- **Следующий шаг:** обновить `.gitignore` и включить доступные scan-настройки.
- **Приёмка:** все перечисленные пути ignored; `.env.example` разрешён; CI-скан зелёный; AGENTS не содержит manual-index-caveat.
- **Выводы неудачных попыток:** нет.

#### AUD-05 — Toolchain не воспроизводим

- **Аудит:** 2026-11-15
- **Тип:** supply chain / reproducibility
- **Приоритет:** P2 — обязательные проверки могут измениться без коммита; локальный и CI-результат расходятся; Scorecard Pinned-Dependencies 6.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** одинаковые версии Python/Node/OS/apt во всех прогонах; обновления приходят только через review/Dependabot.
- **Доказательство:** `requirements-dev.txt:1-2` — `>=` без hash; `ci.yml:39-40` — `pip install --upgrade pip`; `ci.yml:49,64` — `npx` без lockfile; `ci.yml:30-35` — cache только pip, нет `actions/setup-node`/npm cache; `ci.yml:54-55` — apt shellcheck без версии; `Makefile:32` — `npx csstree-validator` без версии, CI pin `@4.0.1`; все workflows `ubuntu-latest`, run logs показывают миграцию образа; Dependabot не покрывает npm. CI установил `ruff-0.17.5` при floor `0.17.4`.
- **Влияние:** lint/validation может измениться/сломаться без commit; локальный PASS не гарантирует CI; supply-chain exposure.
- **Зависимости:** AUD-08 (pipeline), AUD-10 (static analysis).
- **Решение:** pin runner (`ubuntu-24.04`) или container; `pip-compile --generate-hashes` и `--require-hashes`; pin `pip`; `package.json` + lockfile + `npm ci`; добавить npm cache (`actions/setup-node`/`cache: npm` или `actions/cache` по версиям) и npm Dependabot; удалить/зафиксировать apt shellcheck; pin `csstree-validator@4.0.1` в Makefile; проверить заявленный Python 3.9 (matrix 3.9+3.12 или docs 3.12+). Трудоёмкость: 3–5 ч; риски: lockfile/Dependabot churn.
- **Проверка:** два прогона дают одинаковые `pip freeze`/`npm ls`; повторный CI показывает npm cache hit; Scorecard Pinned-Dependencies ≥9; смена версии требует commit.
- **Следующий шаг:** зафиксировать runner и Python, затем Node lockfile и npm cache.
- **Приёмка:** идентичные tool versions, hash/lock проверки, npm cache hit, npm Dependabot, нет unpinned install; Python floor подтверждён matrix или docs исправлены.
- **Выводы неудачных попыток:** нет.

#### AUD-06 — Три источника release notes; label-конфиг не используется

- **Аудит:** 2026-11-15
- **Тип:** delivery / release process
- **Приоритет:** P2 — автоматизация не даёт ценности, governance описывает не тот процесс, релизные тела правятся вручную.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** один воспроизводимый источник release notes; generated notes и CHANGELOG не противоречат друг другу; процесс описан точно.
- **Доказательство:** `release.yml:27` вызывает `--generate-notes`, но API `name/body/updated_at` показывают ручную замену через 18 с; `.github/release.yml` категоризирует по labels, а у 9 закрытых PR 0 labels; `GOVERNANCE.md §Releases` (исправлен в AUD-15) говорит о PR labels; `CHANGELOG.md` — третий источник. `v1.0.0` указывает на Dependabot merge `b271de5`, не на первый skill commit.
- **Влияние:** будущий maintainer не знает, какой источник истины; релизные заметки непредсказуемы.
- **Зависимости:** AUD-01, AUD-15.
- **Решение:** выбрать labels+`.github/release.yml` и добавить labeler, либо удалить label-конфиг и генерировать `--notes-file` из CHANGELOG-секции тега; добавить CI-проверку `CHANGELOG` содержит `## [version]`; не переписывать тело после публикации без аудита. Трудоёмкость: 2–3 ч; риски: дисциплина labels/changelog.
- **Проверка:** release body воспроизводится из repo artifact; `updated_at == published_at` для новых релизов; GOVERNANCE совпадает.
- **Следующий шаг:** выбрать механизм и обновить `.github/workflows/release.yml`/`.github/release.yml`.
- **Приёмка:** один источник; CI проверяет версию; docs совпадают.
- **Выводы неудачных попыток:** нет.

#### AUD-07 — Бюджет инструкций нарушен и не enforced

- **Аудит:** 2026-11-15
- **Тип:** performance / architecture / docs
- **Приоритет:** P2 — `AGENTS.md` задаёт бюджет «вместе заметно меньше 32 КиБ», но типовой набор `SKILL.md` + design-direction + design-system + quality-gates = 85 527 B (261%); `design-direction.md` один 35 017 B.
- **Уверенность:** высокая по размерам, средняя по влиянию на модель
- **Статус:** OPEN
- **Результат:** либо бюджет явно ограничен AGENTS.md, либо документированный набор чтения укладывается в 32 КиБ; oversized reference не проходит валидацию.
- **Доказательство:** `AGENTS.md §Неочевидные` — «Все загружаемые инструкции вместе ... 32 КиБ»; `SKILL.md:273-281` — reading budget; `wc -c` на `2b4be4f`: design-direction 35 017, SKILL 18 699, accessibility 22 594, ux-patterns 22 394, implementation 19 219, design-system 19 162, responsive-mobile 15 118, motion 12 847, quality-gates 12 649, sources 6 490; `scripts/validate.py` не проверяет размер.
- **Влияние:** контекст/латентность растут; агент может загрузить 85 КБ на новую страницу; бюджет декларативен.
- **Зависимости:** AUD-08 (validator/check pipeline), AUD-15 (docs).
- **Решение:** уточнить scope бюджета (только AGENTS.md или включая skill references); если включая — разбить design-direction по секциям на ~3 файла, обновить routing/reading sets, уменьшить типовой набор; добавить per-file или cumulative check в `validate.py`; переместить worked example в asset при необходимости. Трудоёмкость: M–L; риски: broken links, фрагментация.
- **Проверка:** документированный типовой набор ≤32 КиБ или явное исключение; seeded oversize reference fails validate; `make validate` зелёный.
- **Следующий шаг:** определить scope бюджета и зафиксировать целевую раскладку reference-файлов.
- **Приёмка:** budget scope документирован; чтение укладывается; CI ловит oversize.
- **Выводы неудачных попыток:** нет.

#### AUD-08 — Локальные и CI-проверки дублируются и расходятся

- **Аудит:** 2026-11-15
- **Тип:** architecture / performance / tests
- **Приоритет:** P3 — ~65 мс дублей локально (7.5% `make check`), но три места истины для проверок и ложное «make check = CI».
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** один источник проверок; `make check` и CI имеют понятное, документированное отношение; нет повторного contrast/`bash -n`.
- **Доказательство:** `Makefile:10` — help «run everything CI runs»; `Makefile:29` `check: validate lint test`; `scripts/validate.py:169-187` уже запускает contrast self-test/fixture; `Makefile:19-21` повторяет → 4 contrast-процесса; `Makefile:30` и `validate.py:159-164` повторяют `bash -n` → 2 локально, а `ci.yml:51-52` добавляет ещё один после `validate.py` → 2 в CI; CI никогда не запускает `make check`/`validate`/`test`, поэтому drift Makefile не ловится; `validate.py` на `2b4be4f` — 44 `read_text`/465 KB при 31 уникальном файле/258 KB; `Makefile:32` unpinned CSS validator.
- **Влияние:** contributor проходит `make check`, но CI падает на ShellCheck; drift; лишние процессы/чтения.
- **Зависимости:** AUD-05, AUD-11, AUD-07.
- **Решение:** сделать `check: validate lint` и убрать дубли `test`/`bash -n`; оставить `test` standalone; добавить явную ошибку при отсутствии contrast script; один источник для contrast/installer; добавить shellcheck target или явно документировать CI-only; обновить Makefile help; читать файлы один раз; pin csstree; заставить CI запускать `make check`/`make validate` либо проверять паритет, чтобы typo в Makefile ловился. Трудоёмкость: S–M; риски: сохранить покрытие.
- **Проверка:** `make check` — ровно один self-test, один fixture, один `bash -n`; seeded missing script/broken installer fails; docs/help совпадают.
- **Следующий шаг:** убрать `test`/`bash -n` из `check` и обновить help.
- **Приёмка:** один проход проверок; docs и CI согласованы; runtime ≤810 мс; coverage не снижено.
- **Выводы неудачных попыток:** нет.

#### AUD-09 — Теги и релизы не подписаны; релизы mutable

- **Аудит:** 2026-11-15
- **Тип:** release authenticity
- **Приоритет:** P3 — source-only releases, но нет offline-verification; тело релиза можно менять.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** новые теги подписаны и проверяемы; immutable releases включены; при появлении assets — attestation/checksum.
- **Доказательство:** `git tag -v v1.0.0`/`v1.0.1` — no signature; API releases `immutable:false`; no assets/attestations; `release.yml` без sign/attest.
- **Влияние:** доверие только GitHub-аккаунту; нельзя отличить авторизованный тег от подменённого.
- **Зависимости:** AUD-01, AUD-03.
- **Решение:** подписывать теги SSH/GPG, проверять в workflow, включить immutable releases, добавить checksums/SBOM/attestation при assets; документировать `git tag -v`. Трудоёмкость: 2–4 ч; риски: key management.
- **Проверка:** `git tag -v` для новых тегов; immutable release; docs verification.
- **Следующий шаг:** выбрать SSH- или GPG-подпись и добавить проверку в release gate.
- **Приёмка:** подписи проверяются; релизы immutable; provenance опубликован.
- **Выводы неудачных попыток:** нет.

#### AUD-10 — Нет статического анализа workflows и Actions

- **Аудит:** 2026-11-15
- **Тип:** CI security
- **Приоритет:** P3 — текущие workflows чистые, но регрессии permissions/pins/expressions ловятся только ревью.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** PR с небезопасным workflow или unpinned action падает автоматически.
- **Доказательство:** `ci.yml` не содержит actionlint/zizmor; CodeQL matrix `python` только; `validate.py:205-223` проверяет лишь `name/jobs/on`, без SHA/permissions/schema. Mutation-тесты проходят: `actions/checkout@v4` вместо SHA, `updates: not-a-list` в dependabot, duplicate YAML key, issue-template только с `labels`, release trigger заменён на branch/удалён `--verify-tag`.
- **Влияние:** будущая ошибка может пройти без человека.
- **Зависимости:** AUD-05, AUD-11.
- **Решение:** добавить pinned actionlint и/или zizmor, `check-jsonschema` для dependabot/issue templates, assertion `uses:` = 40-hex SHA, version comment, least-privilege permissions, `timeout-minutes`, `persist-credentials: false` и запрет `pull_request_target`; рассмотреть CodeQL `actions` при поддержке. Трудоёмкость: 1–2 ч; риски: новый tool в allowlist.
- **Проверка:** fixture с `uses: actions/checkout@v4`/`permissions: write-all`/malformed `if` падает.
- **Следующий шаг:** добавить actionlint в CI с pinned binary.
- **Приёмка:** небезопасный workflow не проходит.
- **Выводы неудачных попыток:** нет.

#### AUD-11 — Валидатор даёт ложные зелёные на SKILL.md, cross-file anchors, contrast failure и fixture count

- **Аудит:** 2026-11-15
- **Тип:** tests / validation correctness
- **Приоритет:** P1 — зелёный CI не доказывает, что проверки вообще способны упасть; `SKILL.md` — главный файл навыка, contrast — единственный content-dependent gate.
- **Уверенность:** высокая (mutation-тесты в снимке `2b4be4f`)
- **Статус:** OPEN
- **Результат:** каждая документированная проверка имеет негативный fixture; сломанный `SKILL.md`/cross-file anchor, провал contrast, удалённый contrast script и уменьшенный fixture валят CI.
- **Доказательство:** `scripts/validate.py:137-142` пропускает `SKILL.md` перед link-check; `:79,92` проверяет anchors только в текущем файле; `:169-186` запускает только проходящий fixture; `contrast.py:397-398` — единственный `--check` return 1, не тестируется; `validate.py:172-173` молча возвращается при отсутствии `contrast.py`; fixture count/schema не проверяются. Mutation-тесты: `[broken](references/nope.md)` и `[bad anchor](#nope)` в `SKILL.md` → exit 0; `[bad](SECURITY.md#missing)` в README → exit 0; fixture 1 пара → exit 0; `--check` 1→0 → exit 0; удаление `contrast.py` → exit 0; 75 KB reference/empty body/name mismatch → exit 0.
- **Влияние:** битые ссылки в entry-point skill, исчезнувший accessibility gate, фиктивное «64 pairs» и регрессии validator проходят незамеченными.
- **Зависимости:** AUD-02 (installer tests), AUD-07 (size), AUD-10 (workflow tests), AUD-16 (parser/link robustness).
- **Решение:** добавить `tests/` на pytest/unittest с temp-repo fixtures; включить `SKILL.md` и cross-file anchors в link-check; subprocess-тесты contrast exit 0/1/2 и missing script = error; fixture count (64/32/32), unique labels, allowed sizes, token colors; CI и `make test` запускают suite; требование: удаление/нейтрализация любой проверки валит тест. Трудоёмкость: 1–2 дня; риски: fixture maintenance, стабильные substring/exit assertions.
- **Проверка:** перечисленные mutations падают; текущее дерево зелёное; `validate` проверяет SKILL/cross-file anchors; fixture shrink/contrast failure/missing script fail.
- **Следующий шаг:** добавить tests для contrast exit и SKILL/cross-file links, затем fixture schema.
- **Приёмка:** каждая проверка имеет pass/fail fixture; mutation любого guard’а обнаруживается; CI запускает suite.
- **Выводы неудачных попыток:** нет.

#### AUD-12 — CODEOWNERS advisory; approvals/signatures не enforced

- **Аудит:** 2026-11-15
- **Тип:** branch protections / review
- **Приоритет:** P3 — осознанный solo-tradeoff, но CODEOWNERS выглядит сильнее, чем есть.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** либо review/signature control включён для чувствительных путей, либо CODEOWNERS явно помечен advisory и исключение задокументировано.
- **Доказательство:** `.github/CODEOWNERS:1-9`; ruleset `required_approving_review_count: 0`, `require_code_owner_review: false`, no `required_signatures`; `GOVERNANCE.md §Review and merge policy` объясняет solo; initial commit unsigned.
- **Влияние:** security-sensitive files self-merge; appearance of control.
- **Зависимости:** AUD-09.
- **Решение:** добавить комментарий advisory сейчас; при втором maintainer — approvals=1, code-owner review для `.github/`, `install/`, `AGENTS.md`, `skills/`, required signatures; описать emergency path. Трудоёмкость: 30 мин + второй maintainer; риски: solo блокируется.
- **Проверка:** ruleset/CODEOWNERS/docs совпадают; при втором maintainer self-merge невозможен.
- **Следующий шаг:** пометить CODEOWNERS advisory.
- **Приёмка:** control либо enforced, либо явно advisory.
- **Выводы неудачных попыток:** нет.

#### AUD-13 — Scorecard: мёртвый trigger и видимость результатов

- **Аудит:** 2026-11-15
- **Тип:** CI security / visibility
- **Приоритет:** P3 — protection regression не ре-сканируется до weekly; SARIF не в Security tab, artifact 5 дней.
- **Уверенность:** средне-высокая
- **Статус:** OPEN
- **Результат:** изменение ruleset триггерит Scorecard; поведение SARIF/retention документировано или исправлено.
- **Доказательство:** `scorecard.yml:4` `branch_protection_rule`, но API `/branches/main/protection` 404 (rulesets only); нет `repository_ruleset`; `scorecard.yml:19-41` не upload-sarif, artifact retention 5 дней; README говорит только weekly.
- **Влияние:** защитная регрессия ждёт неделю; findings недоступны в Security tab.
- **Зависимости:** AUD-12.
- **Решение:** заменить trigger на `repository_ruleset`, добавить concurrency; либо документировать artifact-only retention 30 дней, либо upload filtered SARIF. Трудоёмкость: 30 мин; риски: alert noise.
- **Проверка:** изменение ruleset запускает Scorecard; docs совпадают; artifact retention достаточен.
- **Следующий шаг:** заменить trigger и добавить concurrency.
- **Приёмка:** trigger работает; visibility документирована/исправлена.
- **Выводы неудачных попыток:** нет.

#### AUD-14 — `AGENTS.md` устарел относительно плана и описания навыка

- **Аудит:** 2026-11-15
- **Тип:** documentation / agent instructions
- **Приоритет:** P2 — project info противоречит фактам и может направить следующего агента создать/перезаписать план; описание навыка занижает фактический trigger.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** `AGENTS.md` указывает на `docs/plan.md` и корректно описывает trigger навыка.
- **Доказательство:** `AGENTS.md §План` — «Отдельного плана нет», но `docs/plan.md` создан и связан из README; `AGENTS.md §Неочевидные` — «description — единственное, что модель видит до загрузки», но OpenCode v2.3.0 перечисляет `id`, `name`, `description`. Правка AGENTS в этом аудите запрещена.
- **Влияние:** агент может создать второй план; авторы недооценивают ID/name.
- **Зависимости:** AUD-15 (docs merge), затем отдельный PR по AGENTS.
- **Решение:** отдельным PR обновить `План` на `docs/plan.md`, переформулировать description как primary trigger (OpenCode также показывает ID/name). Трудоёмкость: 15 мин; риски: нет.
- **Проверка:** grep `Отдельного плана нет` пуст; ссылка на docs/plan.md есть; description/ID/name согласованы с OpenCode.
- **Следующий шаг:** после merge docs PR обновить AGENTS.md отдельным PR.
- **Приёмка:** project info, plan и actual skill listing совпадают.
- **Выводы неудачных попыток:** нет.

#### AUD-15 — Исправлены подтверждённые неточности документации

- **Аудит:** 2026-11-15
- **Тип:** documentation (DONE)
- **Приоритет:** P2 — документация утверждала неверный паритет `make check`/CI, неполный layout, неверный Node prerequisite и неверный источник release notes.
- **Уверенность:** высокая
- **Статус:** DONE
- **Результат:** исправлены перечисленные ниже claims; layout, prerequisites и skills table полны; residual least-privilege claim вынесен в AUD-20; ссылки на AGENTS/plan есть.
- **Доказательство:** README §Install (`--force` deletion scope, symlink/copy update/uninstall), §Validation, §Repository layout, §Repository protections (no ancestry/check-run release gate; `--verify-tag` only), §Skills table, §Adding a skill, §Contributing, §Security, §License; CONTRIBUTING §Development setup (Node 22+), §Validate, §Skill structure (description primary trigger, OpenCode lists ID/name); GOVERNANCE §Releases (publishes immediately; draft gate tracked; tag creation not gated); SECURITY §Security controls (qualifies Dependency Review workflow-level write; AUD-20); CHANGELOG `[Unreleased]` (AGENTS/skills table, public clone URL, audit, Dependency Review correction); THIRD_PARTY_NOTICES и `sources.md` (два источника помечены «Upstream terms — verify»); `docs/plan.md` входит в этот PR, README-ссылка валидна. Node проверен по `engines` (`markdownlint-cli2@0.24.1` требует >=22).
- **Влияние:** contributor и maintainer видят фактический процесс; меньше ложных ожиданий.
- **Зависимости:** нет; AUD-06/AUD-14 — связанные.
- **Решение:** docs-only правки; код/CI не менялись. Трудоёмкость: 1–2 ч; риски: docs drift, не исправлены residual claims AUD-20.
- **Проверка:** `markdownlint`, `make validate`, `git diff --check`; сравнение с Makefile/CI/release.
- **Следующий шаг:** проверить CI docs PR.
- **Приёмка:** diff только документы и `docs/plan.md`; CI зелёный; перечисленные claims совпадают; residual AUD-20 явно указан.
- **Выводы неудачных попыток:** нет.

#### AUD-17 — Token fixture не покрывает semantic surfaces; часть комбинаций не проходит AA

- **Аудит:** 2026-11-15
- **Тип:** data / accessibility / correctness
- **Приоритет:** P1 — starter tokens позиционируются как production-minded, но обычные semantic-комбинации дают AA-fail; fixture это не ловит.
- **Уверенность:** высокая по ratio, средняя по intended scope
- **Статус:** OPEN
- **Результат:** каждая semantic-пара foreground/background либо покрыта и проходит AA, либо явно документирована как неподдерживаемая; fixture синхронизирован с tokens.
- **Доказательство:** `tokens.css:99` — `--color-text-subtle`, `:114-122` — state surfaces, `:130` — selection; `token-contrast-pairs.json:27-37` тестирует state surfaces с `text` и state-color на own surface, но не `text-subtle`/accent/border на state surfaces; subtle — только canvas/surface/sunken. Замеры: `#6f695e` на `#d9eee1` = 4.48, на `#f8e3b8` = 4.32, на `#fbe0dd` = 4.36; `#237366` на `#f8e3b8` = 4.49; `#9b9587` на `#163a29` = 4.21; `#8a8478` на `#f8e3b8`/`#fbe0dd` = 2.95/2.97 — все ниже AA. `contrast.py` принимает пустой fixture и `--check` exit 0.
- **Влияние:** пользователь копирует starter sheet и получает низкий контраст в status callouts/границах; изменение токена не ломает fixture; заявленные 64 пары не гарантируют покрытие.
- **Зависимости:** AUD-11 (fixture count/negative tests), AUD-16 (parser).
- **Решение:** объявить curated-матрицу semantic foreground/background по именам токенов (не Cartesian product); генерировать fixture из токенов или проверять каждое значение; исправить failing tokens или явно исключить комбинации в guidance; проверять, что у каждого semantic `--color-*` есть пара. Трудоёмкость: 4–6 ч; риски: nonsensical pairs, token churn.
- **Проверка:** перечисленные пары проходят AA или помечены unsupported; новый semantic token без пары валит validate; fixture совпадает с tokens.
- **Следующий шаг:** зафиксировать role matrix и пересчитать failing combos.
- **Приёмка:** AA для поддерживаемых пар; fixture/tokens parity; coverage gate.
- **Выводы неудачных попыток:** нет.

#### AUD-16 — Frontmatter/body, contrast parser/CLI и link checker проверяются неполно

- **Аудит:** 2026-11-15
- **Тип:** tests / validation robustness
- **Приоритет:** P2 — текущее дерево валидно, но пустое тело, whitespace-only reference, неверные frontmatter-ключи, парсерные форматы и валидные Markdown-ссылки могут давать ложные результаты.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** frontmatter/body, документированные contrast-форматы, локальные и внешние ссылки имеют pass/fail проверки; link checker не ломается на валидном Markdown.
- **Доказательство:** `validate.py:115-125` проверяет только непустые `name/description/license` и длину description; пустое тело, `name: Totally_Different`, whitespace-only reference и неизвестный ключ проходят. `contrast.py:294-316` — 7 кейсов, покрывающих hex, large и alpha на уровне `check_pair`, но не `main()`/CLI, rgb/hsl/named/json/quiet/stdin/exit 0/1/2; fixture — только hex. `MD_LINK_RE` захватывает title как путь (titled link → false fail), reference-style и root-relative ссылки игнорируются; `validate.py:83` пропускает все `http(s)`; `:190-197` не проверяет `AGENTS.md`, `.github/**/*.md`; slugger не обрабатывает duplicate/setext/`~~~`.
- **Влияние:** неполный/пустой skill, неверные parser-форматы, валидные contributor-ссылки и сломанные внешние install/badge/security ссылки дают ложные pass/fail; `AGENTS.md` и PR template не защищены.
- **Зависимости:** AUD-11 (negative suite), AUD-07 (AGENTS size), AUD-10 (workflow).
- **Решение:** table-driven тесты contrast для всех форматов/порогов/CLI exit/JSON/stdin; frontmatter allowlist, non-empty body, whitespace-only refs, SPDX/license check; не требовать `name == dir` без подтверждения спецификации (OpenCode использует путь как ID, name — display label); заменить regex на Markdown parser или устойчивый checker, включить все `.md`, поддержать title/reference/root-relative и GitHub slug; добавить pinned external-link checker (lychee) на schedule/PR с cache/allowlist или документировать исключение и причину. Трудоёмкость: 1–2 дня; риски: parser dependency, slug differences, flaky external endpoints.
- **Проверка:** titled/reference/root-relative links обрабатываются; `AGENTS.md`/PR template проверяются; внешняя заведомо битая ссылка ловится или исключение документировано; empty body/whitespace reference/unknown key fail; parser/CLI regression fail.
- **Следующий шаг:** заменить link regex на parser, добавить frontmatter/body negative fixtures и external-link проверку.
- **Приёмка:** каждый документированный формат/ссылка имеет pass/fail test; 106 локальных ссылок staged tree проходят; внешняя битая ссылка ловится; mutation ловится.
- **Выводы неудачных попыток:** нет.

#### AUD-18 — Skill references противоречат tokens, motion, units и budgets

- **Аудит:** 2026-11-15
- **Тип:** data / documentation consistency
- **Приоритет:** P2 — пользователь копирует reference/tokens и получает другой theme/нарушение motion/units/budget; contradictions внутри продукта.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** `tokens.css` — единственный canonical источник; references либо ссылаются на него, либо содержат точные значения; motion/units/budgets не конфликтуют.
- **Доказательство:** `design-system.md:567` обещает OKLCH primitives, `tokens.css:32-59` — hex, `grep oklch assets/tokens.css` пуст (в references OKLCH используется); `design-system.md:149` focus `brand-600` vs `tokens.css:111` `brand-500`; `:161` dark accent `brand-400` vs `tokens.css:265` `brand-300`; `:200` Archivo Narrow vs `tokens.css:136` Archivo; `:361-363` pure-black shadows vs warm shadows `tokens.css:213-215`. `design-direction.md:735-737` — 240 ms stagger/120 ms underline, `motion.md:75` — 40–80 ms, tokens 80/150/220/320/480. `accessibility.md:437` — «44×44 px (Apple HIG)», `sources.md:38` — 44 pt, 48 dp. `responsive-mobile.md:336` — marketing `<150–200 KB`, `implementation.md:380` — `<100–150 KB`.
- **Влияние:** copied starter даёт другой focus/accent/font/shadow; пример motion нарушает собственный бюджет; unit attribution путает pt/px; JS budget неоднозначен.
- **Зависимости:** AUD-17 (tokens/fixture), AUD-19 (content layering).
- **Решение:** сделать tokens.css canonical; заменить скопированные mappings/typography/elevation на pointer или точные значения; переписать worked example на `--duration-*` и 40–80 ms stagger; писать «44×44 CSS px practical web target; Apple 44 pt; Material 48 dp»; оставить один JS budget или явно назвать ceiling; добавить doc-test, извлекающий ключевые token values/числа. Трудоёмкость: S–M; риски: CSS parsing fragility.
- **Проверка:** нет конфликтующих focus/accent/font/shadow; пример использует tokens; units корректны; budget один; doc-test ловит drift.
- **Следующий шаг:** привести design-system к tokens.css и motion example к tokens.
- **Приёмка:** references и assets не противоречат; doc-test зелёный.
- **Выводы неудачных попыток:** нет.

#### AUD-19 — Дубли шаблонов и атрибуции

- **Аудит:** 2026-11-15
- **Тип:** content layering / attribution
- **Приоритет:** P3 — два audit-template и design brief дублируются; три списка источников расходятся.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** один canonical шаблон каждого артефакта; один canonical список источников или parity-check; attribution в SKILL.md полный.
- **Доказательство:** `quality-gates.md:258-310` содержит inline audit template, `assets/audit-report.md` — другой; `SKILL.md:288-289` указывает asset, `:145` — quality-gates; cross-reference нет. `SKILL.md:51-58,79-87` повторяет design brief, `assets/design-brief.md` расширяет. `THIRD_PARTY_NOTICES.md:9-16` и `sources.md:9-16` дублируют 8 sources; `SKILL.md:332` omits addyosmani/taste-skill; parity check отсутствует.
- **Влияние:** report shape зависит от загруженного файла; maintainers правят два шаблона; attribution/license review drift.
- **Зависимости:** AUD-18, AUD-21.
- **Решение:** сделать assets canonical; заменить inline template в quality-gates ссылкой, оставить protocol/severity; design brief — один asset + ссылка; один source registry (skill-level sources.md) и генерировать/проверять notices; добавить parity check. Трудоёмкость: 2–3 ч; риски: низкие.
- **Проверка:** один template body; SKILL.md ссылается на asset; sources names/licenses совпадают; attribution полный.
- **Следующий шаг:** убрать inline audit template, оставить ссылку.
- **Приёмка:** ровно один шаблон каждого артефакта; parity-check зелёный.
- **Выводы неудачных попыток:** нет.

#### AUD-20 — Dependency Review оставляет workflow-level write; changelog утверждает обратное

- **Аудит:** 2026-11-15
- **Тип:** security / CI least privilege
- **Приоритет:** P2 — security-hardening claim materially false; write token применяется ко всему workflow.
- **Уверенность:** высокая
- **Статус:** OPEN
- **Результат:** top-level permissions read-only; `pull-requests: write` только на job; будущие changelog-записи точны.
- **Доказательство:** `.github/workflows/dependency-review.yml:8-10` — workflow-level `contents: read`, `pull-requests: write`; job `:12-16` без override. `CHANGELOG.md` v1.0.1 говорит «Moved GitHub Actions write permissions to job scope»; `CONTRIBUTING.md §GitHub Actions` требует job-level write; `SECURITY.md` заявляет least privilege.
- **Влияние:** write-токен шире необходимого; 1.0.1 hardening record вводит в заблуждение.
- **Зависимости:** AUD-10 (workflow policy checks).
- **Решение:** перенести `pull-requests: write` под job; добавить static check, запрещающий workflow-level write; не переписывать исторический changelog — добавить correction в `[Unreleased]`/следующий release; проверить action на job-scope. Трудоёмкость: 30 мин; риски: action должен сохранить комментарий.
- **Проверка:** top-level только read; job имеет write; action работает; changelog correction.
- **Следующий шаг:** перенести permission и добавить проверку.
- **Приёмка:** least privilege enforced; claim true.
- **Выводы неудачных попыток:** нет.

#### AUD-21 — GitHub security/ruleset claims не имеют in-repo evidence

- **Аудит:** 2026-11-15
- **Тип:** documentation / operational evidence
- **Приоритет:** P3 — claims могут быть верны, но не проверяемы из репозитория и стареют.
- **Уверенность:** высокая по отсутствию evidence; фактические значения проверены аудитом 2026-11-15.
- **Статус:** OPEN
- **Результат:** каждая claim имеет ссылку/дату/владельца или явно помечена как внешняя настройка GitHub.
- **Доказательство:** `README.md §Repository protections`, `SECURITY.md §Security controls`, `GOVERNANCE.md §Review and merge policy` заявляют ruleset, required checks, secret scanning/push protection, Dependabot alerts, private reporting, action allowlist, fork approval; в repo есть только workflow/dependabot files, нет ruleset/secret-scanning/private-reporting/allowlist конфигурации и даты проверки.
- **Влияние:** security statements могут быть stale/aspirational; пользователи доверяют незаenforced контролю.
- **Зависимости:** AUD-12, AUD-13.
- **Решение:** добавить `docs/repository-settings.md` с таблицей setting/where/owner/verified date (без секретов) или секцию README; периодический review; не утверждать, что workflow файл enforce-ит ruleset. Трудоёмкость: S; риски: нет.
- **Проверка:** у каждой claim есть evidence/date или external marker; docs не переоценивают enforce.
- **Следующий шаг:** зафиксировать проверенные настройки и дату.
- **Приёмка:** claims/evidence совпадают; review date есть.
- **Выводы неудачных попыток:** нет.

### Гипотезы (не задачи до подтверждения)

- **H1 — fork PR может не пройти `dependency-review`** из-за `comment-summary-in-pr: always` и read-only токена форка. Проверка: контролируемый fork PR; безопасный фикс — `comment-summary-in-pr: on-failure` или убрать комментарий. Приоритет P3.
- **H2 — non-SemVer/prerelease/backport теги** (`vfoo`, `v1.0.2-rc1`, backport) могут публиковаться как stable/latest. Проверка: тег на scratch fork; фикс — regex + `--prerelease`/`--latest=false`.
- **H3 — CI wall time доминируется acquisition**, а не проверками. Проверка: per-step timings; при подтверждении — cache/pin.
- **H4 — ShellCheck уже есть на `ubuntu-latest`**; apt-шаг избыточен. Текущий образ содержит 0.11.0; проверить на закреплённом runner image; удалить apt.
- **H5 — CodeQL на docs-only PR дорог**; проверить длительность и paths-ignore с сохранением required checks.
- **H6 — модель токенизирует references иначе, чем bytes/4**; проверить tokenizer целевой модели.
- **H7 — Actions allowlist шире least privilege** (`verified_allowed`, `ossf/scorecard-action@*`); сузить до явных actions, если политика позволяет.
- **H8 — `require_extra_approval_for_unattributed_changes` при 0 approvals** может блокировать PR с unverified email; проверить на тестовом PR.
- **H9 — Python 3.9 заявлен, но не tested**: `CONTRIBUTING.md` и `pyproject.toml` target py39, CI только 3.12; `ast.parse` проходит. Проверка: matrix 3.9/3.12 или поднять docs floor.
- **H10 — name/ID portability**: OpenCode использует `name` как display label, ID — каталог; Claude Code/Codex могут требовать lowercase kebab и совпадение. Проверка: спецификация каждого harness; не менять текущий OpenCode skill до подтверждения.
- **H11 — «64 audited» provenance**: fixture не содержит audit date/method/reviewer; проверить, означает ли это script-check или independent manual audit; переформулировать или добавить metadata.
- **H12 — PR template relative link rendering**: `../CONTRIBUTING.md` может резолвиться GitHub иначе в PR body; проверить draft PR/new issue page.
- **H13 — upstream licensing/text-copying**: sources/notices заявляют original synthesis; legal review не выполнялся; проверить Apache-2.0 Anthropic и «upstream terms» источники до утверждения о лицензиях.
- **H14 — alternate `<name>.md` skill layout**: OpenCode binary содержит проверку `SKILL.md` или `<name>.md`; installer/validator требуют только `SKILL.md`; текущая конвенция осознанна, но переносимость не проверена.
- **H15 — installer lifecycle one-way/non-atomic**: нет `--uninstall`, manifest, temp+atomic replace; `--copy --force` удаляет customized target. Проверить, входит ли lifecycle в v1 scope; иначе задача AUD-02/AUD-03.

### Вне объёма / владельцу

- Публичный `AGENTS.md` раскрывает локальную модель доступа (полные permissions, чтение секретов, `opencode-full`, MCP). Это осознанное требование предыдущего поручения, но security-аудит считает это P2-риском; рассмотреть перенос деталей в приватный пользовательский supplement. **Это заметка владельцу, не задача плана.**
- `AGENTS.md §Оркестрация` датирован 2026-11-14 и не содержит skill `report`, доступный 2026-11-15; это environment drift. Обновить AGENTS отдельно или перенести инвентарь в приватный supplement; в план как задачу не включаю.
- Глобальные permissions уже allow-all; wrapper `opencode-full` добавляет `--auto`. Если «только через обёртку» должно относиться и к permissions, нужно отдельное изменение пользовательской области.
- `opencode-full` и глобальные skills/MCP существуют только у текущего пользователя; другие участники их не получат.
- Self-hosted раннеров нет; fork approval — `all_external_contributors`. При появлении self-hosted нужен ответ владельца о платформе/метках/ОС/архитектуре/группе/доступе.
- Claude Code/Codex не установлены; их загрузка не проверялась.
- Ветка/трекер: issue #11 — только публикация docs; задачи плана не закрываются PR аудита.
- Продуктовые исправления не начинались; для них — отдельное выполнение задач этого плана.

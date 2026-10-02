# Verificación de fase 1

Comando completo: `./scripts/verify.sh`; variantes backend, frontend, stack, security. Docker/Compose y red bastan. CI ejecuta los mismos scripts dentro de imágenes con versiones/digests y lockfiles fijados.

## Qué se comprueba

- Backend: Ruff lint/formato, mypy estricto con plugin Pydantic, pytest unitarias + PostgreSQL real, XML/JSON/HTML de coverage.py. `scripts/check_coverage.py` exige líneas y ramas por separado; sus propias pruebas demuestran que una media combinada no oculta cobertura insuficiente. Incluye todo app, también módulos no importados.
- Integración: readiness real, base inaccesible, rollback de datos sin commit, Alembic desde base nueva, downgrade/upgrade en base desechable, segundo upgrade idempotente y conservación de datos sintéticos existentes.
- Frontend: ESLint Next/React/TypeScript, Prettier --check, TypeScript sin skipLibCheck, Vitest/RTL/MSW, cobertura V8 con umbrales >=80% en cuatro métricas y build Next.js sin omitir errores. Incluye src/app, componentes, cliente y next.config.ts con lógica de proxy.
- UI: loading, API/DB no disponible, respuesta malformada/inconsistente, reintento, aborto al desmontar, shell y documento español. MSW solo en pruebas; la ejecución normal utiliza API real.
- Stack: imágenes de producción, healthchecks, proxy, Playwright contra Next → FastAPI → PostgreSQL, escritorio 1440, tablet 768, móvil 375, teclado/foco, sin overflow general ni errores de consola y capturas reales. Recreación de contenedores y conservación de dato sintético, seguida de segundo arranque idempotente.
- Seguridad: auditoría de dependencias transitivas Python y npm; Gitleaks en historia Git y snapshot del árbol autorizado, sin .env ni archivos ignorados. No se usan tokens/secrets privados en CI.

## Aislamiento y artefactos

Cada ejecución crea proyecto b2b-test-<timestamp>-<pid>, base b2b_test_<timestamp>_<pid>, red y volumen propios. TEST_DATABASE_URL debe usar PostgreSQL+asyncpg y nombre b2b_test_* antes de ejecutar Alembic o escribir fixtures. No SQLite ni servicios simulados en integración/E2E. El trap conserva el código de error y limpia solo ese proyecto; reports/b2b-test-* permanece.

Backend genera tests.xml y cobertura JSON/XML/HTML; frontend JSON/LCOV/HTML; Playwright captura viewports reales y trazas ante fallos. GitHub Actions publica cuatro artefactos de evidencia durante 14 días, incluidos resultados de fallos. Las credenciales generadas solo viven en configuración ignorada o memoria de la ejecución.

## Resultados medidos — 2026-10-01, America/Guayaquil

Código de referencia: 4f738dca9f21584d3505e996452c2d6345c75d8a (UI/API iguales a e86dd1a). GitHub comprobó ese SHA exacto. La ejecución local completa verifica el árbol de bootstrap; el cambio atómico de dev.sh se comprueba también desde worktree limpio de 4f738dc.

| Comando/control ejecutado | Exit | Resultado |
|---|---|---|
| ./scripts/verify.sh backend | 0 | 14 unitarias + 4 integración PostgreSQL = 18; cuatro tests adicionales del umbral |
| ./scripts/verify.sh security | 0 | Auditorías Python/npm sin vulnerabilidades conocidas del proyecto; dos scans de secretos sin hallazgos |
| ./scripts/dev.sh | 0 | UI/API/DB saludables en localhost:3000 |
| ./scripts/verify.sh (all) | 0 | Todos los controles siguientes, sin skips |
| Ruff lint / Ruff format --check | 0 / 0 | Aplicación, migraciones, tests y scripts |
| mypy app | 0 | 9 módulos con strict/plugin Pydantic |
| pytest unitarias + integración | 0 | 18 aprobadas; PostgreSQL real; Alembic/rollback/negativas |
| python -m unittest discover -s scripts/tests -v | 0 | 4 aprobadas; umbrales independientes |
| ESLint / Prettier --check | 0 / 0 | Sin advertencias ESLint |
| next typegen && tsc --noEmit | 0 | Sin skipLibCheck |
| Vitest --coverage | 0 | 22 aprobadas (UI, cliente API y proxy) |
| next build / Docker builds | 0 / 0 | Build producción e imágenes backend/frontend/E2E |
| Playwright | 0 | 6 aprobadas: shell/proxy/teclado en 1440/768/375 |
| Persistencia y segundo arranque | 0 | Dato conservado tras recrear contenedores; Alembic idempotente |
| pip-audit / npm audit / Gitleaks | 0 / 0 / 0 | Cierre de dependencias del proyecto y secretos Git/árbol |
| Smoke worktree limpio con dos ./scripts/dev.sh | 0 | Primer arranque, proxy real y hash .env conservado; recursos propios limpiados |
| sh -n scripts/*.sh / git diff --check | 0 / 0 | Sintaxis y whitespace |

Cobertura medida local en reports/b2b-test-1790914901-38863:

| Capa | Líneas | Statements | Funciones | Ramas |
|---|---|---|---|---|
| Backend | 65/65 = 100% | — | — | 2/2 = 100% |
| Frontend | 31/31 = 100% | 34/34 = 100% | 11/11 = 100% | 33/34 = 97.05% |

La cobertura frontend incluye next.config.ts y todo el código propio src: layout, page, componente y cliente. Backend incluye app completo. No se promedian capas ni se excluyen rutas/componentes. Son mediciones de una base pequeña, no una medida de funcionalidades futuras. Reportes XML/JSON/HTML y LCOV/HTML conservados localmente; Playwright HTML/resultados y screenshots en el mismo namespace.

El worktree limpio temporal comprobó el commit 4f738dc sin node_modules/.venv/.env preexistentes; Docker suministró todas las herramientas. Se retiró tras terminar. La demo principal sigue saludable y su volumen no se borró. Los recursos de prueba se limpiaron y los informes se conservaron.

GitHub: cuatro jobs aprobados en [CI 4f738dc](https://github.com/shejo8511/saas-subscription-eval/actions/runs/36964467164). Resultados de CI posteriores al commit documental final se informan al cierre, después de ejecutarse. Autenticación, negocio y SSE están fuera de esta fase y no se consideran probados.

## Fase 2 — ampliación de controles

La evidencia anterior corresponde exclusivamente a fase 1. La fase 2 agrega pruebas unitarias de JWT/Argon2/configuración/errores y PostgreSQL real de cuatro cuentas, estado/rol actuales, revocación/reinicio, CSRF, rate limit compartido, rollback, constraints, migración desde baseline y seed que conserva cambios. Rutas auxiliares de permisos solo existen en el test app.

Las fixtures de integración usan bases b2b_test_* y sesiones por solicitud. Para conexiones a Docker desde el host bajo carga, la fixture auth usa el timeout configurable acotado a 10 segundos; no omite fallos. Vitest usa un worker para reducir contención de jsdom, manteniendo todas las aserciones y umbrales. Los tests de expiración usan reloj controlado y los de respuestas pendientes usan barreras, sin sleeps.

E2E añade cuatro cuentas, reload, logout, dos tenants simultáneos en contextos independientes, cambio secuencial con observación del DOM, CSRF/origen, cookies y replay a través de Next. Se conservan regresiones de shell/readiness/OpenAPI/teclado y tres viewports. Solo el error HTTP 401 esperado de /auth/me anónimo se clasifica como esperado en consola; los demás errores fallan. Capturas deliberadas muestran formularios sin passwords y datos sintéticos públicos. Tracing auth desactivado para impedir que solicitudes/cookies se publiquen como artefactos; esto no desactiva pruebas.

Seguridad conserva scans completos de dependencias y secretos del árbol/historia. Para worktrees, el scanner recibe una copia bare temporal de toda la historia local; no se excluyen commits. Los informes permanecen en reports/ y los recursos del proyecto de pruebas se eliminan incluso ante error, sin tocar volúmenes demo.

Los resultados finales y SHA verificados se agregan después de ejecutar los controles; no se atribuyen métricas históricas al nuevo código.

Medición remota comprobada sobre 7423c85baa1d4cbaac2992350d5bf5924cd1c6da, [CI 37020174511](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37020174511): 42 unitarias + 45 integración PostgreSQL = 87; 5 tests de herramientas (4 umbral, 1 configuración); 37 Vitest; 15 E2E. Backend 423/450 líneas = 94%, 42/50 ramas = 84%, cero líneas excluidas. Frontend 124/124 líneas = 100%, 133/134 statements = 99.25%, 38/38 funciones = 100%, 104/106 ramas = 98.11%; cero skips. Los cuatro jobs y sus comandos finalizaron con exit 0. Artefactos originales descargados para comprobar JSON/JUnit/capturas; resultados locales completos se registran separadamente.

## Medición comprobada del código actualizado de fase 2

SHA a25f0bdb178f3a06385379c39a50b2c931ad4f68 (incluye main 51079de); [CI 37027573349](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37027573349), Backend/Frontend/Stack/Security success. 43 unitarias + 45 integración PostgreSQL = 88 pytest, 5 tooling, 37 Vitest y 15 E2E, sin skips.

| Capa | Líneas | Statements | Funciones | Ramas |
|---|---|---|---|---|
| Backend | 425/452 = 94,03% | — | — | 44/52 = 84,62% |
| Frontend | 124/124 = 100% | 133/134 = 99,25% | 38/38 = 100% | 104/106 = 98,11% |

Coverage JSON y JUnit originales descargados; backend cero líneas excluidas, frontend cero skips. Los umbrales se comprueban por separado, no con el porcentaje combinado 93,06% que también muestra coverage.py. El backend local en reports/b2b-test-1790955084-43273 reproduce los mismos denominadores/resultados, 88 + 5 pruebas y Ruff/formato/mypy exit 0; la ejecución completa terminó después con exit 1 en frontend: 33/37 y cuatro timeouts del plazo global de 5 segundos; stack/security no llegaron a ejecutarse en ese run. Se registra el fallo y se corrige el presupuesto medido mediante PR independiente, sin darlo por aprobado.

El presupuesto global jsdom se corrige mediante PR #4 independiente: un worker y 15 segundos por prueba, conservando el plazo de aserciones, relojes/barreras y umbrales. Sus 22 regresiones y frontend completo pasaron localmente, exit 0, sobre eb137a7; los cuatro checks del HEAD y merge 59dde88 aprobaron. Auth integra ese main mediante a3de1df. [CI de a3de1df](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37033622409): cuatro checks success y mismos denominadores de la tabla anterior; artefactos backend/frontend comprobados. El comando local completo sobre ese SHA se registra al terminar, sin atribuirle el exit 1 anterior.

### Repetición local completa y sincronización E2E

`./scripts/verify.sh` sobre a3de1df terminó con exit **1**, informes en reports/b2b-test-1790958217-75637. Backend: 43 unitarias + 45 PostgreSQL, 5 tooling, Ruff/formato/mypy (18 módulos), todo aprobado. Frontend: 37 Vitest, ESLint/Prettier/tipos y build aprobado. Ambas coberturas reprodujeron exactamente los numeradores y denominadores de la tabla anterior. Las imágenes de producción también se construyeron y API/UI/DB estaban saludables. E2E: **13/15**, con dos fallos en escritorio/tablet del caso de login simultáneo. Seguridad y persistencia posteriores no llegaron a ejecutarse en ese comando; no se cuentan como aprobadas.

La aserción visual de 5 segundos comenzaba inmediatamente después del click, mientras dos verificaciones Argon2 y sus respuestas HTTP aún estaban pendientes. El snapshot mostraba «Comprobando sesión», sin identidad ajena. En 85cb872 el helper registra primero la espera de la respuesta POST /auth/login, exige HTTP 200 y después comprueba pantalla/empresa/rol. El logout del caso simultáneo también exige su respuesta HTTP 200 antes de comprobar el formulario. Se conserva el plazo visual, la concurrencia real, el observador de identidad anterior y todos los casos; no hay sleeps, retries ni aserciones desactivadas. `npm run lint`, `npm run format:check`, `npm run typecheck` y `git diff --check` aprobaron localmente (exit 0) tras el cambio. La repetición del stack y sus resultados se registran cuando termina.

Repetición local **85cb872**: `./scripts/verify.sh stack` **exit 0**, informes reports/b2b-test-1790966208-60763. **15/15 E2E** (6,9 minutos), incluidas las tres comprobaciones concurrentes previamente fallidas en dos viewports. Build de producción/tipos, imágenes, readiness real, recreación de contenedores, dato PostgreSQL conservado y segundo arranque aprobados. `.last-run.json` indica passed/failedTests vacío. Trap completó la limpieza de los contenedores/red/volumen propios. El diff a3de1df→85cb872 modifica únicamente el helper E2E; las mediciones locales backend/frontend se mantienen identificadas con a3de1df, y el [CI exacto 85cb872](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37048606099) repite todas las suites y denominadores aprobados.

`./scripts/verify.sh security` sobre 85cb872: **exit 0**, reports/b2b-test-1790968254-81671. Python/npm: cero vulnerabilidades conocidas; Gitleaks de toda la historia local y snapshot autorizado: cero hallazgos. Los cuatro JSON originales se inspeccionaron y los recursos propios se limpiaron. No es una auditoría del OS de las imágenes. `sh -n` de cada script shell y `git diff --check`: exit 0. Las suites locales/backend/frontend aprobadas de a3de1df, stack/security repetidos sobre 85cb872 y CI completo de 85cb872 se distinguen; no se atribuye exit 0 al comando all que terminó exit 1.

Smoke complementario en worktree limpio de **85cb872**, sin .env/.local/deps previas, proyecto b2b-auth-recovered-smoke: **exit 0**. Dos `./scripts/dev.sh` con Docker solamente, 2 empresas/4 usuarios/2 suscripciones antes/después, hashes .env/demo-credentials iguales y permisos 0600/0700. Login público en Aurora/Pacífico, logout de una sesión y reinicio real del contenedor backend: sesión vigente continúa 200; JWT revocado reproducido continúa 401. Cookies y contraseñas solo en memoria/archivos privados, nunca reportadas. Recursos propios limpiados. Dos intentos previos exit 1 (helper editado durante ejecución y Docker unhealthy) se conservan en QA; Docker Desktop se recuperó con restart exit 0, sin cambiar configuración ni borrar datos. La base original se detuvo limpiamente y volvió healthy con el mismo volumen.

### Restauración sincronizada y cuentas independientes

Otra repetición completa de 85cb872, reports/b2b-test-1790970663-5274, terminó **exit 1**: backend 88 + 5 tooling y frontend 37 aprobados, mismas coberturas, lint/formato/tipos/builds aprobados; E2E 9/15. Los controles posteriores no se ejecutaron. QA detalla los seis fallos de sincronización/plazos y un 503 operativo; ese comando no se cuenta como verde.

116dd5f30413363e6517df30961262d35e429fd6 separa los recorridos de las cuatro cuentas, espera /me en navegación/recarga y respeta el viewport en contextos simultáneos. El runtime de prueba aislado recibe DATABASE_TIMEOUT=10 (máximo validado), sin modificar el default dev/producción de 3. Ahora se recogen 24 E2E, conservando todas las comprobaciones. [CI 37062280908](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37062280908): Backend/Frontend/Security success, artefactos comprobados con 43 unitarias, 45 integración, coberturas de la tabla y cero hallazgos; **Stack falló, 6/24**. La espera añadida de response.finished() bloqueaba /me 401; no se considera aprobada la revisión.

La corrección exige status HTTP y JSON de identidad para respuestas 200, seguido de aserciones de UI, sin esperar un cuerpo que el cliente no consume en 401/logout. Los plazos visuales, negativos, cookie/replay, concurrencia, observación DOM y umbrales se conservan. Su verificación completa se registra cuando exista, sin atribuirle resultados del SHA anterior.

## Verificación completa del código final de fase 2

Código **47f1ec5522dbcab667c882e706ed39320c84e662**, incorpora main 9623188 y PR #5. Local `./scripts/verify.sh` **exit 0**, reports/b2b-test-1790975315-52566; el trap conservó el exit y limpió solo sus contenedores/red/volumen/fixtures. [CI exacto](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37065043897): los cuatro jobs success, artefactos originales comprobados, mismos recuentos y denominadores. No se atribuye este resultado a las ejecuciones fallidas anteriores.

| Comando/control real | Exit | Resultado |
|---|---|---|
| ./scripts/verify.sh (all) | 0 | Todas las etapas obligatorias, sin skips |
| Ruff / formato / mypy app | 0 / 0 / 0 | 38 archivos con formato; 18 módulos tipados |
| pytest combinado + umbrales | 0 | 43 unitarias + 45 integración PG; líneas y ramas independientes |
| unittest de scripts | 0 | 5: umbrales y conservación de configuración |
| ESLint / Prettier / TypeScript | 0 / 0 / 0 | Sin advertencias ni controles desactivados |
| Vitest --coverage | 0 | 37 pruebas, cuatro umbrales independientes |
| Next build / imágenes producción | 0 / 0 | Tipos y compilación reales |
| Playwright por proxy | 0 | 24: cuatro cuentas, concurrentes, cambio secuencial, CSRF/replay y bootstrap, tres viewports |
| Persistencia/recreación/segundo arranque | 0 | PostgreSQL conserva el dato sintético; migración idempotente |
| pip-audit / npm audit / Gitleaks historia y árbol | 0 / 0 / 0 | Cero vulnerabilidades/secretos del proyecto |

Backend **425/452 líneas = 94,03%**, **44/52 ramas = 84,62%**; cero líneas excluidas. Frontend **124/124 líneas = 100%**, **133/134 statements = 99,25%**, **38/38 funciones = 100%**, **104/106 ramas = 98,11%**; cero skips. El código runtime completo entra en el denominador. Los 24 E2E separan cada cuenta en un recorrido real; se conservan todos los asserts y no se imponen cantidades artificiales.

PR #5: ./scripts/verify.sh stack exit 0 en aaf6d84, seis regresiones y persistencia/arranque repetido, reports/b2b-test-1790974205-40531. [CI HEAD](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37063118128) y [CI merge 9623188](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37064994046), cuatro checks success. Auth incorpora la corrección en 47f1ec5. El HEAD documental posterior y merge auth se validan por separado y se informan después en PR/cierre.

El HEAD documental 0b5b3d36069bc1adcb4814452ff337913ecdad19 no se considera aprobado: [CI 37068099594](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37068099594) Backend/Frontend/Security success, Stack 23/24, exit 1. Una espera por URL de /me podía seleccionar una respuesta del documento anterior durante reload. Se delimita por frame principal y solicitud iniciada después del commit de navegación, conservando lectura JSON y todos los controles. Se repite exclusivamente el stack afectado localmente y las cuatro suites remotas del nuevo HEAD; el all local aprobado sobre 47f1ec5 queda identificado con ese SHA, cuyo runtime permanece igual.

## Cierre de validación del helper y runtime

**f2b099f3a0ef2981b14f950e04b64cac3e512b2a**: `./scripts/verify.sh stack` local **exit 0**, reports/b2b-test-1790979860-1671, 24/24 E2E, tipos/build de producción, persistencia/recreación y segundo arranque. [CI exacto](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37068925887): Backend/Frontend/Stack/Security success, 43 unitarias + 45 integración PG, 5 tooling, 37 Vitest y 24 E2E; artefactos originales comprobados. Sin skips ni retries. Lint, formato y comprobación estricta del helper local: exit 0.

El diff 47f1ec5→f2b099f contiene únicamente documentos y el helper E2E de restauración. Backend, frontend runtime/configuración, lockfiles, Compose y scripts son idénticos: el all local exit 0 y sus coberturas corresponden explícitamente a 47f1ec5; la repetición local del stack y los cuatro checks remotos corresponden a f2b099f. Backend 425/452 líneas y 44/52 ramas; frontend 124/124 líneas, 133/134 statements, 38/38 funciones y 104/106 ramas. El fallo de 0b5b3d3 (23/24) permanece documentado como exit 1.

Primer stack local f2b099f: exit 1, 23/24, reports/b2b-test-1790977686-77991. Next registró ECONNRESET al proxy de /health; API no registró error de aplicación. Tras builds largos, Docker/VM consumían recursos elevados; es una observación, no una causa probada del reset. Se detuvo limpiamente PostgreSQL original, se reinició Docker Desktop y se restauró el mismo contenedor/volumen, comparados idénticos (exit 0). No se cambiaron código, configuración global, timeouts ni filtros de errores. La repetición conserva todas las pruebas y sus recursos propios se limpian.

El commit documental posterior y merge #2 se comprueban después de existir y se informan en PR/cierre, junto con CI en main, smoke limpio final y ramas conservadas. No se atribuyen resultados a un SHA futuro. **Detenerse antes de fase 3.**

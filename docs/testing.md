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

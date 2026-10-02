# Informe de alcance parcial — fases 0 y 1

Fecha: 2026-10-01 (America/Guayaquil). Preflight, permisos, destino y base comprobados; origin conservado. Rama feature/project-bootstrap y [PR real #1 hacia main](https://github.com/shejo8511/saas-subscription-eval/pull/1).

Implementado y probado localmente: API FastAPI health/readiness, namespace PostgreSQL/Alembic, shell Next.js/React/TypeScript/Tailwind en español, proxy del mismo origen, Compose con volumen/healthchecks/usuario no root en aplicaciones, scripts de arranque y verificación aislada, lockfiles, CI y documentos.

`./scripts/verify.sh` exit 0: 18 pytest (14 unitarias, 4 PostgreSQL), 4 pruebas del umbral, 22 Vitest, 6 Playwright, lint/formato/tipos/builds, persistencia, segundo arranque y scans del proyecto. Backend 100% líneas/ramas; frontend 100% líneas/statements/funciones y 97.05% ramas. Arranque desde worktree limpio y dos ejecuciones de dev.sh exit 0, conservando configuración. Detalle y límites en testing.md/qa-report.md.

Verificado en GitHub antes del commit documental final: Backend, Frontend, Stack y Security aprobados sobre 4f738dca9f21584d3505e996452c2d6345c75d8a, [run 36964467164](https://github.com/shejo8511/saas-subscription-eval/actions/runs/36964467164). Capturas reales de CI anterior con código UI idéntico en screenshots/. Los checks y merge posteriores a este documento se reportan en la respuesta de cierre y pueden consultarse en la PR; no se inventa su SHA antes de que exista.

Sin bloqueos de destino/autenticación/permisos; la integración final queda sujeta al HEAD exacto, checks y protección vigentes. Auto-delete de ramas desactivado; rama preservada. No se declara la aplicación completa terminada: autenticación, empresas/seeds, licencias, consumo, alertas, SSE y dashboard permanecen pendientes. Matriz R01–R24 separa verificación del bootstrap y requisitos futuros.

Ejecución de la base: `./scripts/dev.sh`, UI http://localhost:3000 y OpenAPI /api/docs. Verificación: `./scripts/verify.sh`. **Detenerse antes de fase 2**; una nueva ejecución necesitará autorización para feature/auth-tenancy.

## Continuidad fase 2

El cierre anterior permanece como registro histórico. Autorización nueva: solamente autenticación, empresas y seguridad base. feature/auth-tenancy desde main actualizado c561650; [PR #2 real](https://github.com/shejo8511/saas-subscription-eval/pull/2). FastAPI conserva negocio, Next/React/TS/Tailwind UI y proxy, PostgreSQL real; migración posterior 0002, seed idempotente, JWT/Argon2/CSRF, permisos actuales y UI mínima. Sin fases 3–7.

La entrega final requiere pruebas locales completas, cobertura independiente y cuatro checks del HEAD final; los resultados se registran al existir. Ramas nunca se borran; merge únicamente con reglas/checks/aprobaciones vigentes. Estado y matriz distinguen funcionalidades futuras.

## Commits de fase 2 y correcciones independientes

Registro comprobado antes del commit de cierre. Incluye PR #3 (readiness), PR #4 (presupuesto jsdom) y PR #5 (recorridos E2E), integradas normalmente desde ramas fix creadas en main. El CI del commit documental posterior y el merge de auth se informan en PR/cierre tras existir.

| Commit | Cambio |
|---|---|
| 046d443 | docs(auth): record phase 2 authorization and verified base |
| 83815a3 | feat(tenancy): add constrained PostgreSQL models and migration |
| b05c9f8 | feat(auth): add revocable JWT sessions, signed CSRF and current tenant permissions |
| db7c7a9 | feat(dev): seed two companies with preserved local credentials and isolated fixtures |
| 3ec82e3 | feat(web): add accessible login and isolated session context with real API |
| 0fbe06e | test(auth): verify unsigned tokens and cross-session CSRF over HTTP |
| 76ab940 | fix(dev): align script formatting with the backend quality configuration |
| e1b5b79 | fix(test): invoke isolated E2E fixture as a Python module |
| 82edd51 | fix(dev): generate protected local files as the host user |
| 7423c85 | fix(test): identify company and role by exact accessible text |
| b7ec8db | test(tenancy): use bounded connection timeout for isolated PostgreSQL fixtures |
| 62a8c82 | fix(auth): require Secure cookies for every HTTPS origin |
| 0423ec5 | fix(compose): allow bounded Python startup time in readiness probe |
| 24dcf8e | fix(compose): bound cold startup and reduce readiness process churn |
| 747d4c8 | docs(auth): record implemented scope and verified remote evidence |
| 51079de | fix(compose): correct bounded readiness startup (#3) |
| a25f0bd | chore(auth): incorporate verified readiness correction from main |
| eb137a7 | fix(test): bound cold jsdom execution within a measured deadline |
| 5b3c18e | fix(dev): forward session lifetime and login window configuration |
| d46a47d | docs(auth): preserve timeout failures and measured quality evidence |
| 59dde88 | fix(test): accommodate bounded cold jsdom execution (#4) |
| a3de1df | chore(auth): incorporate verified cold-test correction from main |
| 85cb872 | test(auth): await HTTP success before checking concurrent session UI |
| 116dd5f | test(auth): synchronize restoration and bound isolated PostgreSQL connections |
| aaf6d84 | fix(test): synchronize browser checks with bounded HTTP journeys |
| bec5aa2 | fix(test): avoid awaiting unread authentication responses |
| 9623188 | fix(test): synchronize bounded browser journeys (#5) |
| 47f1ec5 | chore(auth): incorporate verified browser regression correction from main |
| 0b5b3d3 | docs(auth): record completed phase 2 validation and delivery evidence |
| f2b099f | fix(test): bind session restoration to the newly navigated document |

## Evidencia comprobada de fase 2

Código 85cb872: [cuatro checks remotos aprobados](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37048606099), 43 unitarias + 45 integración PostgreSQL, 5 tooling, 37 Vitest y 15 E2E. Backend 425/452 líneas (94,03%) y 44/52 ramas (84,62%); frontend 124/124 líneas (100%), 133/134 statements (99,25%), 38/38 funciones (100%), 104/106 ramas (98,11%). Sin skips ni exclusiones artificiales; JSON/JUnit originales comprobados.

Localmente, el comando completo sobre a3de1df aprobó etapas backend/frontend, cobertura y builds, pero terminó **exit 1** con 13/15 E2E; no se registra como verde. El diff a3de1df→85cb872 contiene exclusivamente el helper E2E de sincronización HTTP; las mediciones locales de las etapas backend/frontend corresponden explícitamente a a3de1df. Repetición `./scripts/verify.sh stack` sobre 85cb872 **exit 0**, 15 E2E, persistencia/recreación y segundo arranque. `./scripts/verify.sh security` sobre 85cb872 **exit 0**, cero vulnerabilidades Python/npm y cero secretos en historia/árbol. Lint/formato/tipos frontend tras el cambio, sintaxis de todos los scripts shell y whitespace: exit 0. Resultados, SHA y namespaces separados en testing.md; hallazgos corregidos y límites en qa-report.md.

No hay administración de usuarios/roles por API, licencias, consumo, alertas, SSE, gráficos, pagos, registro público ni recuperación de contraseña. El rate limit global comparte presupuesto entre usuarios; no es protección distribuida completa. No se auditaron todas las bibliotecas OS de las imágenes ni un despliegue de producción. **Detenerse antes de fase 3**: la aplicación completa permanece pendiente.

## Evidencia completa anterior al HEAD documental

**47f1ec5522dbcab667c882e706ed39320c84e662**: ./scripts/verify.sh local **exit 0**, reports/b2b-test-1790975315-52566, y [CI exacto](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37065043897), Backend/Frontend/Stack/Security success. 43 unitarias + 45 integración PostgreSQL, 5 tooling, 37 Vitest y 24 E2E. Backend 425/452 líneas y 44/52 ramas; frontend 124/124 líneas, 133/134 statements, 38/38 funciones, 104/106 ramas. Lint, formato, tipos, builds, persistencia/recreación, segundo arranque y scans sin hallazgos aprobados. Informes originales inspeccionados. Los exit 1 previos permanecen en QA/testing, incluido el helper bloqueado de 116dd5f corregido en bec5aa2.

PR #5 integrada en main 9623188 tras sus checks/local y CI de merge aprobados. feature/auth-tenancy conserva todo el historial. La PR #2 y el HEAD documental posterior se cierran únicamente tras verificar sus cuatro checks/reglas; el SHA de ese commit y merge, CI de main, smoke limpio final y ramas retenidas se reportan en PR/cierre después de existir. Ninguna aprobación externa inventada.

Arranque: ./scripts/dev.sh, http://localhost:3000; consultar localmente `less .local/demo-credentials.json`. Probar Admin/User de Empresa Aurora y Empresa Pacífico, con perfiles separados para simultaneidad o logout entre cuentas. Seed no asigna licencias ni crea consumo. Smoke previo limpio 85cb872 exit 0 y sus límites constan en testing; se vuelve a comprobar el estado del merge desde worktree limpio. Sin despliegue cloud ni auditoría OS completa. **Detenerse antes de fase 3**; la aplicación completa permanece pendiente.

## Cierre de validación del helper y runtime

**f2b099f3a0ef2981b14f950e04b64cac3e512b2a**: `./scripts/verify.sh stack` local **exit 0**, reports/b2b-test-1790979860-1671, 24/24 E2E, tipos/build de producción, persistencia/recreación y segundo arranque. [CI exacto](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37068925887): Backend/Frontend/Stack/Security success, 43 unitarias + 45 integración PG, 5 tooling, 37 Vitest y 24 E2E; artefactos originales comprobados. Sin skips ni retries. Lint, formato y comprobación estricta del helper local: exit 0.

El diff 47f1ec5→f2b099f contiene únicamente documentos y el helper E2E de restauración. Backend, frontend runtime/configuración, lockfiles, Compose y scripts son idénticos: el all local exit 0 y sus coberturas corresponden explícitamente a 47f1ec5; la repetición local del stack y los cuatro checks remotos corresponden a f2b099f. Backend 425/452 líneas y 44/52 ramas; frontend 124/124 líneas, 133/134 statements, 38/38 funciones y 104/106 ramas. El fallo de 0b5b3d3 (23/24) permanece documentado como exit 1.

Primer stack local f2b099f: exit 1, 23/24, reports/b2b-test-1790977686-77991. Next registró ECONNRESET al proxy de /health; API no registró error de aplicación. Tras builds largos, Docker/VM consumían recursos elevados; es una observación, no una causa probada del reset. Se detuvo limpiamente PostgreSQL original, se reinició Docker Desktop y se restauró el mismo contenedor/volumen, comparados idénticos (exit 0). No se cambiaron código, configuración global, timeouts ni filtros de errores. La repetición conserva todas las pruebas y sus recursos propios se limpian.

El commit documental posterior y merge #2 se comprueban después de existir y se informan en PR/cierre, junto con CI en main, smoke limpio final y ramas conservadas. No se atribuyen resultados a un SHA futuro. **Detenerse antes de fase 3.**

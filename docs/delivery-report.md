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

## Commits de fase 2 y corrección independiente

Registro comprobado antes del commit de cierre; los resultados posteriores se informan en la PR y en el cierre de sesión.

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

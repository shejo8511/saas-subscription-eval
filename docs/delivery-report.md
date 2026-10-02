# Informe de alcance parcial — fases 0 y 1

Fecha: 2026-10-01 (America/Guayaquil). Preflight, permisos, destino y base comprobados; origin conservado. Rama feature/project-bootstrap y [PR real #1 hacia main](https://github.com/shejo8511/saas-subscription-eval/pull/1).

Implementado y probado localmente: API FastAPI health/readiness, namespace PostgreSQL/Alembic, shell Next.js/React/TypeScript/Tailwind en español, proxy del mismo origen, Compose con volumen/healthchecks/usuario no root en aplicaciones, scripts de arranque y verificación aislada, lockfiles, CI y documentos.

`./scripts/verify.sh` exit 0: 18 pytest (14 unitarias, 4 PostgreSQL), 4 pruebas del umbral, 22 Vitest, 6 Playwright, lint/formato/tipos/builds, persistencia, segundo arranque y scans del proyecto. Backend 100% líneas/ramas; frontend 100% líneas/statements/funciones y 97.05% ramas. Arranque desde worktree limpio y dos ejecuciones de dev.sh exit 0, conservando configuración. Detalle y límites en testing.md/qa-report.md.

Verificado en GitHub antes del commit documental final: Backend, Frontend, Stack y Security aprobados sobre 4f738dca9f21584d3505e996452c2d6345c75d8a, [run 36964467164](https://github.com/shejo8511/saas-subscription-eval/actions/runs/36964467164). Capturas reales de CI anterior con código UI idéntico en screenshots/. Los checks y merge posteriores a este documento se reportan en la respuesta de cierre y pueden consultarse en la PR; no se inventa su SHA antes de que exista.

Sin bloqueos de destino/autenticación/permisos; la integración final queda sujeta al HEAD exacto, checks y protección vigentes. Auto-delete de ramas desactivado; rama preservada. No se declara la aplicación completa terminada: autenticación, empresas/seeds, licencias, consumo, alertas, SSE y dashboard permanecen pendientes. Matriz R01–R24 separa verificación del bootstrap y requisitos futuros.

Ejecución de la base: `./scripts/dev.sh`, UI http://localhost:3000 y OpenAPI /api/docs. Verificación: `./scripts/verify.sh`. **Detenerse antes de fase 2**; una nueva ejecución necesitará autorización para feature/auth-tenancy.

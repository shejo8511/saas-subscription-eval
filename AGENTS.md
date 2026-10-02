# Instrucciones del proyecto

- Leer CODEX_PLAN_SUSCRIPCIONES_B2B.md y docs/implementation-state.md antes de modificar código. Autorización del propietario del 2026-10-02: exclusivamente fase 2 (autenticación, empresas y seguridad base); detenerse antes de fase 3. El cierre histórico de fases 0 y 1 se conserva.
- Mantener FastAPI como único backend de negocio y persistencia. Next.js presenta la UI y hace proxy de /api; no accede a PostgreSQL.
- Conservar origin, trabajo existente e historia. Trabajar en feature/* o fix/* desde main actualizado; Conventional Commits incrementales, PR real hacia main. No force-push, bypass, borrar ramas ni volúmenes de la demo.
- Instalar con backend/uv.lock y frontend/package-lock.json. No tags latest, actualizaciones forzadas, skips, pruebas vacías ni opciones que oculten errores.
- Verificar con ./scripts/verify.sh. Backend: Ruff, mypy, pytest unitario/integración PostgreSQL y cobertura independiente de líneas/ramas >=80%. Frontend: ESLint, Prettier, TypeScript, Vitest >=80% en cuatro métricas y build Next.js. E2E contra el stack real.
- Usar bases/proyectos de prueba aislados. Limpiar únicamente recursos creados por la ejecución. No publicar .env, contraseñas, tokens ni logs sensibles.
- Actualizar matriz y estado con evidencia comprobada. Distinguir implementación, pruebas locales y checks de GitHub sobre el SHA correspondiente. No declarar terminada la aplicación completa por completar bootstrap.

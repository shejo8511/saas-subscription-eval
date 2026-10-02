# Suscripciones B2B

Sistema B2B en desarrollo. **Esta entrega implementa exclusivamente fase 2: autenticación, empresas y seguridad base**, sobre el bootstrap ya integrado. Hay login real, dos empresas con Admin/User, sesión recuperable/revocable y protección CSRF. Usuarios/licencias, consumo, alertas, SSE y dashboard completo permanecen pendientes; no se declara terminada la aplicación. El [plan](CODEX_PLAN_SUSCRIPCIONES_B2B.md) y la [autorización fase 2](PROMPT_FASE_2_CODEX_SUSCRIPCIONES_B2B.txt) distinguen requisitos del PDF y decisiones de implementación.

FastAPI concentra negocio y persistencia; React con Next.js, TypeScript y TailwindCSS presenta la UI y hace proxy del mismo origen. PostgreSQL se ejecuta en Docker con volumen persistente. Estructura: `backend/`, `frontend/`, `scripts/`, `docs/` y `.github/workflows/ci.yml`. Versiones, decisiones y límites en [arquitectura](docs/architecture.md).

## Arranque con un comando

Desde un clon del repositorio, con Docker Engine y Docker Compose >=2.24 disponibles y el daemon iniciado:

```sh
./scripts/dev.sh
```

No hace falta instalar Python o Node globalmente. El script genera secretos aleatorios y cuatro credenciales sintéticas locales una sola vez, con lock y escritura atómica. `.env` y `.local/` están ignorados; sus archivos sensibles tienen permisos 0600. Conserva configuración y datos existentes. Construye imágenes, espera PostgreSQL, aplica Alembic 0001 → 0002, ejecuta seed idempotente y levanta API/UI con healthchecks. No elimina volúmenes ni reinicia passwords/roles/estados/cuotas en el segundo arranque. La primera ejecución necesita red y varios minutos.

- UI: http://localhost:3000
- OpenAPI interactiva: http://localhost:3000/api/docs
- Especificación: http://localhost:3000/api/openapi.json
- Health: http://localhost:3000/api/v1/health
- Readiness: http://localhost:3000/api/v1/ready

Solo el puerto de la UI está publicado y únicamente en 127.0.0.1. Si 3000 está ocupado, usa `WEB_PORT=3001 ./scripts/dev.sh`. La UI conserva el estado real del entorno y añade login/sesión. Consulta las credenciales exclusivamente en tu equipo:

```sh
less .local/demo-credentials.json
```

Prueba Admin y User de **Empresa Aurora**, cierra sesión y entra con las cuentas de **Empresa Pacífico**. La vista muestra solo identidad, empresa y rol autorizados. Recargar conserva una sesión vigente; cerrar sesión la revoca de verdad. Para coexistencia, usa perfiles de navegador separados. Las dos suscripciones tienen cuotas demo de 3 licencias y 10 operaciones mensuales; todavía no existen asignación ni consumo. No compartas el archivo de credenciales ni `.env`.

```sh
# Ver servicios y detenerlos conservando los datos:
docker compose ps
docker compose down
# Volver a arrancar usando la misma configuración y volumen:
./scripts/dev.sh
```

## API actual y contratos futuros

| Ruta implementada | Comportamiento |
|---|---|
| GET /api/v1/health | 200 `{"status":"ok"}`, sin base |
| GET /api/v1/ready | 200 ready o 503 unavailable según PostgreSQL/esquema |
| GET /api/v1/auth/csrf | Bootstrap CSRF firmado, reutiliza token vigente |
| POST /api/v1/auth/login | Email/password, CSRF y origen permitidos; identidad pública y cookies |
| GET /api/v1/auth/me | Identidad, empresa y rol actuales; 401 sin sesión válida |
| POST /api/v1/auth/logout | CSRF, revocación persistida y borrado de cookies; repetición segura |

JWT solo en cookie HttpOnly, SameSite=Strict, Path=/; CSRF firmado con clave independiente, vinculado a sesión y enviado en X-CSRF-Token. Cookie Secure obligatoria en producción/HTTPS; HTTP explícito solo local/test. Origin debe ser PUBLIC_ORIGIN exacto; sin Origin se exige Referer válido, y faltantes/null se rechazan. `/csrf` permite recuperar la protección incluso para logout de sesión vencida. Nunca JWT en JSON, URLs o almacenamiento web.

Errores de auth/validación/operación: `{"error":{"code":"…","message":"…"},"request_id":"…"}` y HTTP 401/403/422/429/500/503. Sin inputs sensibles, SQL ni tracebacks. Rate limit global PostgreSQL: 30 intentos por 60 segundos, configurable con LOGIN_LIMIT/LOGIN_WINDOW_SECONDS en .env; SESSION_SECONDS configura la duración entre 60 y 3600 segundos. Compose propaga los tres valores a FastAPI; 429 incluye Retry-After. No depende de headers de IP ni variantes de email. Sesión 30 minutos sin refresh; rol/estado se consultan en cada petición. Detalle en [arquitectura](docs/architecture.md).

Contratos del PDF preservados para próximas fases: `GET /api/v1/usage` (fase 4) y `POST /api/v1/licenses/assign`, cuerpo `{"user_id":"uuid"}` (fase 3). **Todavía responden 404**. Autenticación JWT Admin/User implementada en esta fase; asignar/cambiar roles por API permanece en fase 3. El consumo vendrá de una operación demo ejecutada y persistida; tiempo real se implementará con SSE y sondeo interno PostgreSQL, con objetivo local de actualización en otra ventana dentro de 3 segundos, pendiente de medición.

## Verificación reproducible

```sh
./scripts/verify.sh
```

Ejecuta lint, formato, tipos, unitarias e integración PostgreSQL, cobertura, builds de producción e imágenes, E2E real, persistencia tras recrear contenedores y análisis de dependencias/secretos. Cada ejecución tiene su propio proyecto Compose, base `b2b_test_*` y volumen; limpia únicamente esos recursos. Los informes quedan en `reports/b2b-test-*/` (ignorados en Git). Requiere Docker y red, sin secretos privados ni cuentas GitHub.

También: `./scripts/verify.sh backend`, `frontend`, `stack` o `security`. Son los mismos cuatro controles obligatorios de CI. Cobertura mínima backend: líneas y ramas >=80% por separado; frontend: líneas, statements, funciones y ramas >=80%. No se promedian capas; todas las pruebas deben pasar. Medición histórica de fase 1: backend 100% líneas/ramas; frontend 100% líneas/statements/funciones y 97,05% ramas (2026-10-01; código 4f738dc). Resultados medidos y comandos en [testing](docs/testing.md), [QA](docs/qa-report.md) y [estado](docs/implementation-state.md).

## Supuestos del plan para el producto futuro

Son decisiones explícitas de implementación, no capacidades ya entregadas ni requisitos adicionales atribuidos al PDF:

1. Cada empresa es un tenant; cada usuario pertenece a una sola empresa, sin superadministrador de plataforma.
2. Una suscripción demo activa por empresa, con máximo de licencias y cuota mensual; sin pagos, facturación, renovaciones comerciales ni cambio de plan.
3. Máximo de una licencia activa por persona/empresa. Admin no consume licencia automáticamente, pero sí necesita una para ejecutar la operación medida.
4. Cupo de licencias estricto; exceder consumo genera alerta y no bloquea operaciones.
5. Mes calendario UTC, inicio inclusivo y fin exclusivo; historial conservado.
6. Límites enteros positivos, validados; representación defensiva ante valores inesperados.
7. Admin administra usuarios/roles/licencias y alertas. User ve licencia propia y métricas agregadas de su empresa en lectura, sin listar/administrar empleados.
8. Alertas internas persistidas por empresa/periodo cuando used > limit; igualdad no es exceso. Sin correo/SMS.
9. Advertencia al 80% opcional, etiquetada como mejora; distinta del umbral de cobertura.
10. Operación HTTP demo realmente ejecutada/persistida como origen del consumo, sin números aleatorios.
11. Demo local de dos empresas con Admin/User; email globalmente único. Sin registro público ni recuperación por correo.
12. Entrega local reproducible y repositorio público con CI, sin despliegue cloud ni infraestructura de pago.

## Entrega y continuidad

Repositorio existente: https://github.com/shejo8511/saas-subscription-eval. Se conserva origin. Conventional Commits incrementales en feature/project-bootstrap (PR #1 integrada) y feature/auth-tenancy (PR #2), protección con checks Backend/Frontend/Stack/Security y ramas preservadas. Evidencia remota en [GitHub delivery](docs/github-delivery.md); trazabilidad R01–R24 en [matriz](docs/requirements-matrix.md).

Las fases 3–7 permanecen pendientes. Leer [AGENTS.md](AGENTS.md) y [estado](docs/implementation-state.md) para continuar; se requiere nueva autorización antes de fase 3. La demo local no constituye una certificación de seguridad ni la entrega de la aplicación completa.

Evidencia fase 2 local (`./scripts/verify.sh` exit 0) y GitHub sobre 47f1ec5: 88 pytest (43 unitarias/45 integración PG), 37 Vitest y 24 E2E. Backend 425/452 líneas = 94,03% y 44/52 ramas = 84,62%; frontend 100% líneas/99,25% statements/100% funciones/98,11% ramas. [Cuatro checks aprobados](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37065043897). Los checks posteriores del commit de cierre se verifican por separado; detalle y límites en los documentos de evidencia.

# Suscripciones B2B

Base de un sistema para administrar licencias corporativas y consultar consumo de API. **Esta entrega ejecuta solamente las fases 0 y 1** del [plan autorizado](CODEX_PLAN_SUSCRIPCIONES_B2B.md). La aplicación de negocio está pendiente: todavía no hay login, empresas, cuentas demo, licencias, consumo, alertas, SSE ni dashboard funcional.

FastAPI concentra negocio y persistencia; React con Next.js, TypeScript y TailwindCSS presenta la UI y hace proxy del mismo origen. PostgreSQL se ejecuta en Docker con volumen persistente. Estructura: `backend/`, `frontend/`, `scripts/`, `docs/` y `.github/workflows/ci.yml`. Versiones, decisiones y límites en [arquitectura](docs/architecture.md).

## Arranque con un comando

Desde un clon del repositorio, con Docker Engine y Docker Compose >=2.24 disponibles y el daemon iniciado:

```sh
./scripts/dev.sh
```

No hace falta instalar Python o Node globalmente. El script genera una contraseña PostgreSQL aleatoria en `.env` ignorado por Git si no existe; conserva la configuración existente. Construye imágenes, espera PostgreSQL, ejecuta Alembic y levanta API/UI con healthchecks. La primera ejecución descarga dependencias e imágenes; necesita red y varios minutos. No elimina volúmenes ni datos.

- UI: http://localhost:3000
- OpenAPI interactiva: http://localhost:3000/api/docs
- Especificación: http://localhost:3000/api/openapi.json
- Health: http://localhost:3000/api/v1/health
- Readiness: http://localhost:3000/api/v1/ready

Solo el puerto de la UI está publicado y únicamente en 127.0.0.1. Si 3000 está ocupado, usa `WEB_PORT=3001 ./scripts/dev.sh`. La UI muestra el estado real del backend/PostgreSQL y permite repetir la comprobación. No hay credenciales de acceso ni seeds de negocio en fase 1.

```sh
# Ver servicios y detenerlos conservando los datos:
docker compose ps
docker compose down
# Volver a arrancar usando la misma configuración y volumen:
./scripts/dev.sh
```

## API actual y contratos futuros

| Ruta implementada | Respuesta |
|---|---|
| GET /api/v1/health | 200 `{"status":"ok"}`; no necesita base disponible |
| GET /api/v1/ready | 200 `{"status":"ready","database":"ready"}` si PostgreSQL y el esquema migrado están disponibles; 503 con valores `unavailable` en caso contrario |

Readiness no revela errores internos y devuelve Cache-Control: no-store. El sobre global de errores de negocio/validación se implementará en fase 2; esta fase solo valida la configuración de PostgreSQL y sus timeouts.

Contratos del PDF preservados para próximas fases: `GET /api/v1/usage` (fase 4) y `POST /api/v1/licenses/assign`, cuerpo `{"user_id":"uuid"}` (fase 3). **Todavía responden 404**. Autenticación JWT Admin/User pertenece a fase 2. El consumo vendrá de una operación demo ejecutada y persistida; tiempo real se implementará con SSE y sondeo interno PostgreSQL, con objetivo local de actualización en otra ventana dentro de 3 segundos, pendiente de medición.

## Verificación reproducible

```sh
./scripts/verify.sh
```

Ejecuta lint, formato, tipos, unitarias e integración PostgreSQL, cobertura, builds de producción e imágenes, E2E real, persistencia tras recrear contenedores y análisis de dependencias/secretos. Cada ejecución tiene su propio proyecto Compose, base `b2b_test_*` y volumen; limpia únicamente esos recursos. Los informes quedan en `reports/b2b-test-*/` (ignorados en Git). Requiere Docker y red, sin secretos privados ni cuentas GitHub.

También: `./scripts/verify.sh backend`, `frontend`, `stack` o `security`. Son los mismos cuatro controles obligatorios de CI. Cobertura mínima backend: líneas y ramas >=80% por separado; frontend: líneas, statements, funciones y ramas >=80%. No se promedian capas; todas las pruebas deben pasar. Medición de fase 1: backend 100% líneas/ramas; frontend 100% líneas/statements/funciones y 97,05% ramas (2026-10-01; código 4f738dc). Resultados medidos y comandos en [testing](docs/testing.md), [QA](docs/qa-report.md) y [estado](docs/implementation-state.md).

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
11. Demo futura de dos empresas con Admin/User; email globalmente único. Sin registro público ni recuperación por correo.
12. Entrega local reproducible y repositorio público con CI, sin despliegue cloud ni infraestructura de pago.

## Entrega y continuidad

Repositorio existente: https://github.com/shejo8511/saas-subscription-eval. Se conserva origin. Conventional Commits incrementales en feature/project-bootstrap, PR hacia main, protección con checks Backend/Frontend/Stack/Security y ramas preservadas. Evidencia remota en [GitHub delivery](docs/github-delivery.md); trazabilidad R01–R24 en [matriz](docs/requirements-matrix.md).

Las fases siguientes permanecen pendientes. Leer [AGENTS.md](AGENTS.md) y [estado](docs/implementation-state.md) para continuar; se requiere nueva autorización antes de fase 2. La fase 1 no constituye una certificación de seguridad ni la entrega de la aplicación completa.

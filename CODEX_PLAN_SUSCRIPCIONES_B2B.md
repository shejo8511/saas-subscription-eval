# Plan maestro para Codex — Sistema de Gestión de Suscripciones B2B (SaaS)

## 0. Naturaleza y modo de ejecución

Este archivo es el contrato de implementación, no un informe de una aplicación ya construida. Está basado en las tres páginas de «Test Suscripciones B2B.pdf» y en las elecciones del propietario: Python con FastAPI, React, PostgreSQL en Docker y cobertura mínima del 80% con pruebas unitarias y de integración. El repositorio de GitHub ya existe.

Actúa como desarrollador senior fullstack especializado en Python/FastAPI y React, con responsabilidad sobre seguridad, pruebas, Docker y el flujo de entrega en GitHub. Implementa código funcional dentro del repositorio actual; no respondas solamente con recomendaciones, pseudocódigo, pantallas estáticas o un nuevo plan.

Trabaja por fases verificables. La primera ejecución comprende exclusivamente las fases 0 y 1. Las siguientes ejecuciones avanzan una fase pendiente por vez, salvo otra autorización expresa. No marques una fase como completada si le falta una prueba obligatoria o su PR remoto. Un impedimento de permisos puede permitir trabajo local independiente, pero bloquea la integración y la declaración de entrega.

Lee primero las instrucciones AGENTS.md existentes y este archivo. No sustituyas reglas existentes en silencio. Mantén el plan y el registro de estado en el repositorio para poder retomar el trabajo en otra sesión sin depender de la memoria del chat.

## 1. Matriz de requisitos y fidelidad al enunciado

Distingue en la documentación «requisito del PDF», «elección del propietario» y «decisión de implementación». No atribuyas al PDF funciones o criterios que no contiene.

| ID | Requisito | Origen | Evidencia de aceptación |
|---|---|---|---|
| R01 | Administradores gestionan licencias de empleados corporativos | PDF, p. 1 | Recorrido real de asignación, consulta y gestión desde UI/API |
| R02 | Asignar roles | PDF, p. 1 | Admin cambia rol; User no puede escalar privilegios |
| R03 | Ver consumo de API en tiempo real | PDF, p. 1 | Una operación real modifica datos persistidos y otra ventana recibe la actualización |
| R04 | Alertas al superar el límite contratado | PDF, p. 1 | Cruce del límite produce alerta persistida y visible |
| R05 | Python con FastAPI | Elección permitida por PDF, p. 1 | API implementada en FastAPI |
| R06 | React; el PDF concreta React (Next.js), TypeScript y TailwindCSS | Elección del propietario y PDF, p. 1 | Frontend React/Next.js tipado, con Tailwind |
| R07 | PostgreSQL ejecutándose en Docker | Elección permitida por PDF, p. 1 | Servicio PostgreSQL con persistencia y healthcheck |
| R08 | Cobertura mínima del 80%; pruebas unitarias y de integración | PDF, p. 1, y propietario | Informes reproducibles y umbrales que hagan fallar CI |
| R09 | Repositorio público saas-subscription-eval y acceso compartido | PDF, p. 1 | URL, nombre y visibilidad comprobados; no recrear el repositorio existente |
| R10 | Carpetas backend/frontend o monorepo | PDF, p. 1 | Estructura sencilla con /backend y /frontend |
| R11 | No desarrollar directamente en main; ramas feature/…, fix/…; PRs hacia main | PDF, p. 1 | PRs reales y su historial |
| R12 | No borrar ramas integradas | PDF, p. 1 | Ramas de trabajo todavía presentes en el remoto |
| R13 | Conventional Commits; evitar un único commit gigante | PDF, p. 2 | Commits incrementales, coherentes y rastreables |
| R14 | README profesional: arquitectura, decisiones, ejecución con un comando y supuestos | PDF, p. 2 | Un evaluador reproduce los pasos desde un clon limpio |
| R15 | Autenticación JWT con roles Admin y User | PDF, p. 2 | Pruebas de autenticación, autorización y expiración |
| R16 | GET /api/v1/usage devuelve métricas de la empresa | PDF, p. 2 | Contrato y pruebas con PostgreSQL |
| R17 | POST /api/v1/licenses/assign asigna licencia y valida el máximo | PDF, p. 2 | Pruebas de capacidad, duplicados y concurrencia |
| R18 | Manejo global de errores y validación de entradas | PDF, p. 2 | Esquemas, errores consistentes y pruebas negativas |
| R19 | Gestión eficiente de estado global | PDF, p. 2 | Context para sesión/UI; datos remotos gestionados sin duplicación innecesaria |
| R20 | Dashboard responsive, gráficos de consumo y tabla interactiva de usuarios | PDF, p. 3 | UI conectada al backend; pruebas de escritorio y móvil |
| R21 | Lazy loading y optimización de renders | PDF, p. 3 | Separación de módulos, carga diferida y evidencia de comportamiento |
| R22 | docker-compose.yml orquesta base de datos, backend y frontend | PDF, p. 3 | Arranque, salud, persistencia y reconstrucción comprobados |
| R23 | .github/workflows/ci.yml en cada PR hacia main | PDF, p. 3 | Ejecución remota real sobre los commits entregados |
| R24 | CI ejecuta ESLint/Prettier y pruebas; resultado verde | PDF, p. 3 | Checks completos y satisfactorios, no solo archivo YAML |

Crea docs/requirements-matrix.md con estas filas y columnas adicionales para implementación, pruebas, fase, PR, evidencia y estado. Inicializa el estado como pendiente; actualízalo solo con evidencia real.

## 2. Stack y arquitectura propuesta

Decisiones de implementación para esta evaluación, no requisitos adicionales atribuidos al PDF:

- Backend: Python estable compatible, FastAPI, Pydantic, SQLAlchemy 2 y Alembic. Usa un modelo consistente de acceso a PostgreSQL; preferencia por SQLAlchemy async y un driver compatible, con sesiones independientes por solicitud/tarea. No compartas una AsyncSession entre tareas concurrentes.
- Frontend: React con Next.js, TypeScript estricto y TailwindCSS. No reemplazar Next.js por Vite sin autorización: se elige Next.js para ajustarse a la formulación del PDF.
- Backend único de negocio: FastAPI. Next.js se limita a presentación, rutas de UI y proxy necesario; no duplicar autenticación de negocio, licencias ni acceso a PostgreSQL en Next.js.
- Estado: Context para sesión y preferencias pequeñas; TanStack Query para consultas, caché e invalidación de datos remotos. No mantener dos fuentes de verdad para usuarios, licencias o consumo.
- Gráficos: Recharts o Chart.js; escoger una y documentar. No instalar ambas.
- Pruebas backend: pytest, pytest-cov y herramientas HTTP compatibles con FastAPI.
- Pruebas frontend: Vitest, React Testing Library y MSW para pruebas de componentes e integración de frontend. MSW no sustituye las integraciones contra la API real.
- E2E: Playwright con frontend, API y PostgreSQL reales.
- Calidad: Ruff, mypy, ESLint, Prettier y comprobación de TypeScript.
- Infraestructura: Docker y Docker Compose; GitHub Actions. No introducir Redis, Celery, Kafka, Kubernetes o microservicios para esta evaluación.

Verifica la compatibilidad y soporte de las versiones elegidas al ejecutar la fase 0. Consulta documentación oficial disponible; fija versiones y lockfiles reproducibles. No uses tags latest como configuración final ni asegures que una versión es la última sin comprobarlo. Registra versiones concretas en docs/architecture.md. No mezcles instrucciones de versiones incompatibles ni actualices dependencias con opciones forzadas para ocultar fallos.

Implementa un monolito modular pragmático: rutas/esquemas → servicios/casos de uso → persistencia. La lógica de autorización y negocio no debe dispersarse en componentes React ni rutas gigantes. Evita repositorios genéricos, interfaces y capas vacías sin una necesidad concreta.

Estructura orientativa, ajustable si el repositorio existente lo requiere:

```text
backend/
  app/
    api/v1/
    core/                 # configuración, JWT, CSRF, errores, logging
    db/                   # engine, sesiones y modelos comunes
    modules/
      auth/
      companies/
      users/
      subscriptions/
      licenses/
      usage/
      alerts/
  alembic/
  tests/unit/
  tests/integration/
  pyproject.toml
  Dockerfile
frontend/
  src/app/
  src/features/
  src/components/
  src/lib/
  src/providers/
  tests/
  e2e/
  package.json
  Dockerfile
scripts/
docs/
.github/workflows/ci.yml
.github/pull_request_template.md
AGENTS.md
README.md
docker-compose.yml
.env.example
```

## 3. Supuestos de negocio explícitos

El PDF no define modelo comercial, periodicidad, canal de alertas, origen del consumo, transporte en tiempo real ni política completa de roles. Para cerrar el alcance de manera verificable, adopta y documenta estos supuestos:

1. Cada empresa es un tenant. En este MVP cada usuario pertenece a una empresa; no se implementa pertenencia múltiple ni superadministrador de plataforma.
2. Cada empresa tiene una suscripción activa de demostración con máximo de licencias y cuota mensual de API. No hay pagos, checkout, Stripe, facturación, renovaciones comerciales ni interfaz para cambiar de plan.
3. Una persona puede tener como máximo una licencia activa en su empresa. El rol Admin no consume una licencia automáticamente; necesita licencia si ejecuta la operación de API medida.
4. El límite de licencias es estricto: no se puede superar. El límite de consumo genera una alerta de exceso, pero no bloquea las operaciones: el enunciado pide alertar, no cortar el servicio.
5. La cuota API se mide por mes calendario en UTC, con inicio inclusivo y fin exclusivo. Se conserva el historial; cambiar de mes no elimina ni pone a cero registros históricos.
6. Los límites contratados son enteros positivos. Rechaza límites inválidos en configuración/datos. Protege también la representación ante datos inesperados para no dividir por cero.
7. Admin administra usuarios, roles y licencias, y consulta alertas. User puede ver su licencia y las métricas agregadas de su propia empresa en modo de solo lectura, pero no listar ni administrar empleados. Esta visibilidad del agregado es una decisión explícita, no una obligación del PDF.
8. Las alertas del MVP son internas al dashboard, persistidas por empresa y periodo. No se envía correo ni SMS. Una alerta de exceso aparece cuando used > limit; llegar exactamente al límite no equivale a superarlo.
9. Una advertencia preventiva al 80% es opcional y debe etiquetarse como mejora, no como requisito. No confundir este porcentaje con la cobertura de pruebas.
10. Como no se define una API de producto para medir, habrá una operación HTTP de demostración realmente ejecutada y persistida. No se presentarán números aleatorios o animaciones como consumo real.
11. La demo local incluye al menos dos empresas y usuarios Admin/User para comprobar aislamiento. No hay registro público abierto ni recuperación de contraseña por correo dentro del alcance.
12. No se asume despliegue cloud: la entrega obligatoria es repositorio público, ejecución local reproducible y CI verde. No crear infraestructura de pago.

Incluye estos supuestos en README.md. Si aparece una incompatibilidad real con código previo o instrucciones posteriores del propietario, explica la discrepancia antes de sustituir decisiones importantes.

## 4. Datos, aislamiento y transacciones

Modelo mínimo propuesto:

- companies: identidad y estado de la empresa.
- users: empresa, identidad, email normalizado, password_hash, rol Admin/User, estado y timestamps. Para simplificar login, email único global en este MVP; documentarlo.
- auth_sessions: jti, usuario, expiración y revocación para poder invalidar logout sin esperar únicamente al vencimiento del JWT.
- subscriptions: empresa, estado, max_licenses y monthly_api_limit. Una activa por empresa.
- license_assignments: empresa, suscripción, usuario, asignador y fechas de asignación/revocación. Unicidad de licencia activa por usuario/empresa.
- usage_periods: empresa/suscripción, periodo UTC, acumulado y versión persistida. Unicidad de la fila de periodo.
- api_usage_events: evento inmutable, empresa, usuario, instante, unidades y clave de idempotencia. Fuente auditable del consumo.
- alerts: empresa, periodo, tipo, instante y datos del umbral. Restricción única para no duplicar la misma alerta de exceso.

Añade claves foráneas, índices, restricciones y comprobaciones acordes con las consultas. Impide relaciones cruzadas entre empresas también en integridad referencial cuando proceda, mediante claves compuestas o mecanismos equivalentes; no dependas solo de convenciones en Python.

Todas las consultas, modificaciones, agregados y streams deben filtrar por la empresa del usuario autenticado. No aceptar company_id del navegador como autoridad. Los claims del JWT no sustituyen la comprobación del usuario, empresa, sesión y permisos actuales en base de datos. No confiar en esconder botones ni en guards de frontend.

Valida el máximo de licencias dentro de una transacción, bloqueando una fila estable de la suscripción antes de contar y asignar, o con una estrategia equivalente demostrada. Todas las operaciones que alteren la capacidad, incluida desactivación/revocación, deben seguir el mismo protocolo. No bloquear únicamente las licencias existentes: cuando no hay ninguna, esa estrategia no protege el cupo.

Define un orden consistente de bloqueos. La protección del último Admin activo y los cambios de estado deben resistir carreras concurrentes. Evita bloqueos de tabla innecesarios. Documenta los invariantes y compruébalos con conexiones PostgreSQL distintas y solicitudes solapadas; una secuencia de llamadas no demuestra concurrencia.

## 5. API, seguridad y contratos

### 5.1 Rutas obligatorias, sin renombrarlas

GET /api/v1/usage:

- Requiere autenticación; solo métricas de la empresa autorizada.
- Devuelve periodo UTC, consumo actual, límite contratado, restante no negativo, exceso, porcentaje real que puede superar 100%, estado del límite y serie temporal con ceros donde corresponda.
- Incluye licencias utilizadas/disponibles o permite consultarlas en un recurso complementario claramente documentado.
- Obtener métricas no genera consumo facturable ni muta el histórico.
- Un periodo sin eventos devuelve ceros coherentes y no errores.

POST /api/v1/licenses/assign:

- Exclusivo de Admin; cuerpo mínimo {"user_id": "uuid"}.
- El usuario destino debe existir en la misma empresa y estar activo.
- Respeta la capacidad bajo concurrencia y no crea duplicados.
- Primera asignación: 201. Repetición cuando ya tiene licencia activa: 200, sin consumir otro cupo; documenta esta idempotencia de negocio.
- Falta de cupo: 409 con código LICENSE_LIMIT_REACHED.
- Un ID ajeno se trata sin revelar información, normalmente como 404.

### 5.2 Rutas complementarias propuestas

Implementa las necesarias para que el dashboard funcione de extremo a extremo, con contratos tipados y permisos explícitos:

- GET /api/v1/auth/csrf: inicializar protección CSRF para el navegador.
- POST /api/v1/auth/login, POST /api/v1/auth/logout y GET /api/v1/auth/me.
- GET /api/v1/users y POST /api/v1/users para Admin.
- PATCH /api/v1/users/{user_id}: campos permitidos expresamente; sin mass assignment.
- PATCH /api/v1/users/{user_id}/role y PATCH /api/v1/users/{user_id}/status para Admin.
- GET /api/v1/licenses/me; listado administrativo si lo requiere la UI.
- POST /api/v1/licenses/{license_id}/revoke para Admin, con repetición segura.
- GET /api/v1/alerts para Admin.
- GET /api/v1/usage/stream para la actualización en tiempo real de métricas autorizadas.
- POST /api/v1/demo/work para ejecutar una unidad real de trabajo medido en la demo.
- Healthcheck de proceso y readiness que compruebe acceso a PostgreSQL.

No crear endpoints de modificación de cuotas, borrado de todo el histórico o administración global sin necesidad. Paginación, búsqueda y ordenamiento de usuarios deben ser acotados y validados en el servidor; usa lista permitida de campos de ordenamiento. Rechaza campos de escritura desconocidos o sensibles.

### 5.3 JWT y sesión web

Usa una biblioteca mantenida para JWT y Argon2 para contraseñas; no desarrolles criptografía propia. Valida firma, algoritmo permitido, exp, sub y los claims que definas, incluyendo issuer/audience cuando se emitan. Nunca aceptar alg=none ni algoritmos indicados por el atacante. No registrar claves, contraseñas ni tokens.

Decisión propuesta para el navegador: JWT en cookie HttpOnly, SameSite explícito, Path apropiado, sin Domain innecesario y Secure en entornos HTTPS. No guardar credenciales de sesión en localStorage, sessionStorage ni URLs. Usa un mismo origen público para frontend y API mediante proxy; el navegador no debe intentar resolver nombres Docker como backend o db.

Implementa protección CSRF explícita en operaciones que cambian estado, incluido login/logout: patrón firmado de doble cookie ligado a la sesión, o un patrón establecido equivalente. El login necesita también una protección preautenticada. Valida Origin/Referer según una política documentada. SameSite o CORS por sí solos no reemplazan esa protección. Prueba solicitudes legítimas y falsificadas.

Sesión corta y configurable, por ejemplo 30 minutos. No añadir refresh tokens si no son necesarios para el alcance. /auth/me recupera la sesión al recargar. Logout revoca la sesión en la base de datos y borra la cookie. Una cuenta inactiva, sesión revocada o cambio de rol debe surtir efecto en solicitudes posteriores y cerrar streams autorizados previamente cuando corresponda.

Limita intentos de login con un mecanismo acotado y documenta su comportamiento entre workers. En configuración no local, fallar si faltan secretos o si se intenta usar valores de demo. No presentar la demo local como certificación de seguridad de producción.

### 5.4 Errores y observabilidad

Centraliza errores esperados y no esperados, conservando los códigos HTTP apropiados: 401, 403, 404, 409, 422 y 500. No devolver 200 para errores. Establece un sobre consistente, por ejemplo error.code, error.message, error.details y request_id. No exponer traceback, consultas SQL, cookies ni detalles internos al cliente.

El handler global debe convertir también errores de validación al contrato acordado sin alterar la semántica de autenticación y cabeceras relevantes. Usa logs estructurados, identificador de petición y rollback correcto. Documenta contratos en OpenAPI y ejemplos de petición/respuesta; el cliente frontend debe seguir esos contratos.

## 6. Consumo, alertas y tiempo real

### Consumo demostrable

POST /api/v1/demo/work representa una operación de producto de demostración, identificada como tal. Requiere usuario activo y licencia activa. Cada ejecución válida consume una unidad, registrada por el backend; no permite al frontend escribir el acumulado ni indicar arbitrariamente cientos de unidades.

El frontend ofrece un control explícito para ejecutar operaciones de prueba y muestra su resultado real. Puede lanzar una cantidad pequeña y acotada de peticiones para demostrar el límite, conservando una clave de idempotencia por operación. No contabilices login, healthchecks, consultas de métricas, administración ni apertura/reconexión de SSE.

Define Idempotency-Key con alcance empresa y operación. La misma clave y misma solicitud no deben duplicar trabajo ni consumo, incluso con reintentos concurrentes; una reutilización incompatible devuelve 409. Mantén un resultado reproducible para la repetición. No metas el periodo en una unicidad que permita duplicar un reintento al cambiar de mes.

Registra evento, incremento del agregado y creación de alerta en una sola transacción. Los fallos hacen rollback completo. Publica o permite observar únicamente datos confirmados. Prueba que la suma del registro de eventos coincide con el agregado y que la alerta no se duplica al superar el umbral simultáneamente.

### Transporte en tiempo real

Usa Server-Sent Events para enviar métricas del servidor al navegador. Para un MVP sin infraestructura adicional, se permite consultar periódicamente una versión persistida en PostgreSQL desde el stream y enviar una instantánea cuando cambie. Documenta honestamente este mecanismo: es SSE hacia el navegador con sondeo interno, no un bus de eventos distribuido.

Objetivo de demostración: una operación confirmada debe reflejarse en otra ventana dentro de 3 segundos bajo la prueba local documentada. Es un criterio propuesto que debe medirse, no una garantía de latencia en cualquier entorno.

Cada stream envía una instantánea inicial, admite reconexión, heartbeats y cancelación, y recupera el estado desde PostgreSQL. No dependas de una cola en memoria como única fuente: perdería coherencia entre workers y reinicios. No mantengas una transacción ni una conexión de base de datos ocupada durante toda la vida del stream; utiliza lecturas breves y libera recursos.

Comprueba expiración/revocación de sesión y permisos durante conexiones largas. No envíes alertas administrativas a User. Usa identificadores/versiones coherentes, tratamiento correcto del cambio de mes y resíncronización completa al reconectar; no afirmes replay de eventos si solo reconstruyes instantáneas.

Verifica el recorrido completo a través del proxy frontend: tipo text/event-stream, flush de eventos y ausencia de buffering que impida actualizaciones. En React, cerrar conexiones al desmontar, hacer logout o cambiar de identidad, con reconexión acotada y estado visible de desconexión. Evita dos conexiones por efectos duplicados. Los errores de red no deben convertirse en datos inventados.

## 7. Frontend funcional y UX

Interfaz en español, código y contratos con nombres consistentes. No se requiere un diseño visual específico del PDF: usa una UI administrativa sobria y coherente, no una landing comercial.

Pantallas mínimas:

- Login con validación, estados de envío y mensajes genéricos ante credenciales inválidas.
- Dashboard Admin: empresa, periodo, consumo/límite/exceso, licencias usadas/disponibles, gráfico temporal, estado de conexión y alertas.
- Gestión de usuarios: tabla con búsqueda, paginación, ordenamiento y filtros útiles; crear usuario, modificar campos permitidos, cambiar rol/estado y asignar/revocar licencia.
- Vista User: identidad y licencia propia, métricas permitidas en solo lectura y operación de demo cuando tenga licencia.

Cada acción debe invocar la API real, conservar el estado en PostgreSQL y reflejar errores de permisos/capacidad. Evita botones decorativos, contadores constantes o datos mock en el código entregado de ejecución normal.

Maneja loading, vacío, error, éxito, sesión expirada, pérdida de conexión y conflicto por cupo. Deshabilita duplicados mientras se envía una acción, pero conserva validación e idempotencia en backend. Tras cambios, invalida las consultas necesarias sin recargar toda la aplicación.

Lazy loading real para gráficos o módulos no iniciales mediante mecanismos compatibles con la versión elegida de Next.js. Mantén páginas/layouts delgados; no ocultes lógica de negocio en server components difíciles de probar. Evita consultas duplicadas, claves de lista inestables, efectos sin limpieza y renders globales por cada evento. Usa memoización solo cuando tenga una razón verificable y registra cómo comprobaste la carga diferida y el comportamiento de renders.

Diseño responsive probado, por ejemplo a 375, 768 y 1440 píxeles. Sin scroll horizontal general; una tabla puede tener su propia zona de scroll. Formularios y diálogos con etiquetas, navegación por teclado, foco visible, errores asociados al campo, contraste razonable y confirmación para acciones sensibles. El gráfico debe tener resumen textual accesible. Mostrar el periodo y la zona horaria, además de unidades comprensibles.

## 8. Pruebas y cobertura

### Umbral y medición

El PDF solicita al menos 80% y pruebas unitarias/de integración, pero no distribuye porcentajes por capa ni por suite. Para evitar una media engañosa, esta implementación exigirá:

- Backend: cobertura de líneas >=80% sobre el código de aplicación, ejecutando unitarias e integración. Medir también ramas de decisión y exigir >=80% como criterio adicional de calidad de este plan.
- Frontend: >=80% de líneas, statements, funciones y ramas de decisión sobre el código propio medible. Configurar thresholds explícitos en Vitest.
- No promediar backend y frontend. El 80% no significa 80% de tests aprobados: todas las pruebas obligatorias deben pasar.
- Ejecutar ambas suites y reportarlas por separado en cantidad/resultados; combinar sus mediciones cuando corresponda para el umbral de cada capa. No se exige 80% independiente a cada suite aislada.
- E2E complementa las pruebas unitarias y de integración; no las reemplaza.

Incluye también módulos no importados por las pruebas en el denominador. Excluye únicamente tests, archivos generados, declaraciones de tipos y configuración sin lógica cuando esté justificado. Las migraciones se comprueban con pruebas específicas. No excluir servicios, seguridad, repositorios, componentes, rutas o app/** para inflar resultados. No usar passWithNoTests, omisiones silenciosas ni comentarios de exclusión de cobertura para esconder lógica difícil.

Activa branch coverage en Python. Como el umbral combinado de coverage.py no necesariamente garantiza un mínimo independiente de líneas y ramas, comprueba los porcentajes separados desde el informe JSON o un mecanismo equivalente probado. Guarda XML/HTML/JSON del backend y LCOV/HTML del frontend como artefactos, sin confundir objetivos con resultados obtenidos.

### Integración real

Usa PostgreSQL real en Docker para migraciones, restricciones, aislamiento, transacciones y concurrencia. SQLite ni un repositorio simulado sustituyen esas pruebas. La base de tests debe ser aislada y claramente identificada; añade una protección contra operaciones destructivas sobre bases no autorizadas.

Las pruebas unitarias pueden usar dobles; las de integración del backend ejercitan API/servicios y persistencia real. MSW es apropiado para contratos de frontend, pero los E2E deben recorrer Next.js → FastAPI → PostgreSQL. Resuelve compatibilidad de las herramientas con Next.js sin excluir lógica propia para obtener el porcentaje.

No usar sleeps arbitrarios como mecanismo principal de sincronización. Para carreras, usa barreras/eventos y conexiones distintas. Para SSE, usa un servidor real cuando sea necesario, timeouts y cierre de conexiones para que la suite no quede bloqueada esperando un stream infinito. Controla el reloj para límites temporales y cambio de mes.

### Casos obligatorios de aceptación

Autenticación y permisos:
- Login válido/inválido, JWT expirado/alterado, sesión revocada y usuario inactivo.
- Rol User no puede crear empleados, cambiar roles, asignar ni revocar licencias.
- No escalar permisos mediante payload, ID manipulado o claims obsoletos.
- Acceso cruzado entre dos empresas bloqueado en detalle, listas, cambios, agregados y SSE.
- CSRF ausente/inválido/origen no permitido rechazado; flujo legítimo admitido.
- Logout invalida la sesión y cierra el acceso posterior; recarga recupera sesión válida.
- No se puede eliminar funcionalmente al último Admin activo mediante desactivación o cambio de rol, tampoco bajo concurrencia.

Licencias y usuarios:
- Asignación exitosa, usuario inválido/inactivo/ajeno y campos no permitidos.
- Cupo lleno rechaza; un cupo restante y dos asignaciones concurrentes a usuarios distintos producen exactamente una nueva licencia.
- Duplicados simultáneos para el mismo usuario no crean dos licencias ni consumen dos cupos.
- Revocar libera cupo; repetición no lo libera dos veces; desactivar aplica una política consistente de liberación.
- Filtros, paginación, búsqueda y ordenamiento no saltan el aislamiento.

Consumo y alertas:
- Periodo vacío, acumulación y agregados/series coherentes con eventos.
- Petición medida sin licencia rechazada y sin consumo; consultas administrativas no generan consumo.
- Repetición idempotente, concurrencia, reutilización incompatible y reintento tras cambio de mes.
- Transacción fallida no deja evento, contador o alerta parcial.
- Consumo exactamente en el límite frente a consumo por encima; una alerta persistida por empresa/periodo/tipo.
- Nuevos periodos no destruyen historia y los límites temporales se calculan en UTC.
- Una operación en ventana B modifica la vista A; reconexión recupera estado sin doble contabilización.
- SSE respeta aislamiento, vencimiento, logout, permisos y liberación de recursos.

UI e infraestructura:
- Tabla, formularios, errores del servidor, estados vacíos/loading y vista restringida User.
- Recorrido Admin crear usuario → asignar → ejecutar operación → ver métrica/alerta → revocar.
- Responsive, teclado y carga diferida; ausencia de errores relevantes en consola.
- Alembic desde base vacía y actualización sobre una base existente con datos sintéticos preservados; downgrade/upgrade solo en base desechable donde proceda.
- Arranque de clon limpio con un comando, segundo arranque sin duplicar seeds, persistencia tras reiniciar y healthchecks.
- Builds de backend/frontend/Docker sin flags que ignoren errores de tipado o lint.

## 9. Docker, arranque y datos de demostración

Mantén un docker-compose.yml con servicios db, backend y frontend. Se pueden añadir servicios one-shot para migraciones/inicialización y perfiles de tests, pero no complejidad innecesaria.

Incluye healthchecks reales, espera de disponibilidad y migraciones antes de aceptar tráfico. No usar solo un sleep fijo. PostgreSQL debe tener volumen persistente. No borrar volúmenes al arrancar ni ejecutar seeds destructivos. Gestiona migraciones como un paso único controlado, no mediante create_all al iniciar cada worker.

Crea un comando documentado de arranque, preferentemente ./scripts/dev.sh, que desde un clon limpio y con Docker/Compose disponibles pueda preparar configuración local ignorada por Git, generar secretos aleatorios de desarrollo si no existen, construir imágenes, migrar, sembrar datos sintéticos idempotentes y levantar los servicios. No debe requerir instalar Python ni Node globalmente en el equipo del evaluador. Puede apoyarse en contenedores para generar la configuración.

Publica una URL local coherente para la UI; usa un proxy /api hacia FastAPI. Las URLs que ve el navegador no deben contener hosts internos de Docker. Verifica SSE a través de ese mismo origen. Publica los servicios solo en interfaces locales por defecto; no exponer PostgreSQL innecesariamente.

Credenciales demo: generar o proporcionar exclusivamente valores locales sintéticos y claramente etiquetados. Mostrar al evaluador cómo acceder sin publicar claves JWT ni secretos reutilizables. El seed de demo no debe habilitarse en configuración de producción y no debe reiniciar contraseñas ni sobrescribir cambios en cada arranque.

Configura límites de demo pequeños, documentados y suficientes para probar cupos y exceso sin lanzar miles de solicitudes. Usa dos empresas diferenciadas. Las cuentas administrativas de demo deben poder gestionar usuarios sin consumir licencia; la operación medida sí requiere asignación explícita.

Incluye Dockerfiles reproducibles, .dockerignore, usuario no root donde proceda y separación entre configuración pública del frontend y secretos del backend. No copiar .env, claves, informes sensibles o volúmenes a las imágenes. No hacer descargas remotas de fuentes tipográficas durante la build si comprometen la reproducibilidad.

Proporciona también un comando único de verificación, por ejemplo ./scripts/verify.sh, con alternativa make verify si se incluye Makefile. Debe ejecutar los mismos controles esenciales que CI, devolver códigos de salida fiables y aislar el entorno de prueba. Usa namespaces/volúmenes de tests distintos de la demo; limpia solamente recursos creados para esa ejecución.

## 10. Git, ramas y PRs reales

### Reglas permanentes

El repositorio ya está creado. No crear otro, cambiar origin, renombrar, sobrescribir, eliminar ni publicar contenido preexistente sin comprobar el destino y la autorización. Inspecciona si corresponde al nombre saas-subscription-eval y si es público. Si no cumple nombre/visibilidad, reporta la discrepancia; no cambies visibilidad en silencio.

No desarrollar ni commitear implementación directamente en main. Cada fase parte de origin/main actualizado después de integrar la anterior. Las correcciones de defectos reales van en fix/<descripcion>. No inventes bugs, colaboradores, reviews o commits para simular seniority.

Conventional Commits incrementales por cambios coherentes: feat(auth): ..., test(licenses): ..., fix(usage): ..., docs(readme): ..., ci(checks): .... No un único commit final ni cuotas artificiales de commits. La separación debe reflejar el trabajo realmente realizado.

Push de la rama de trabajo y PR real con base main. No basta un merge local ni un archivo que diga que hubo PR. Mantén todas las ramas de desarrollo, incluidas las fix, en el remoto después de integrarlas. Evita git push --all: empuja explícitamente solo ramas de este trabajo para no filtrar ramas ajenas.

Preferir merge commit al integrar PR para conservar la granularidad de los commits, en lugar de condensar todo con squash. Esta es una decisión de flujo del plan, no una prohibición de squash impuesta por el PDF. Nunca force-push, reset destructivo, borrar ramas, eludir protecciones con --admin ni falsificar autoría. No usar gh pr merge --delete-branch ni su opción -d. Si una rama publicada necesita cambios de main, usa una integración transparente y vuelve a verificar.

### Caso especial: repositorio completamente vacío

Una PR necesita una rama base con historia. Si el remoto ya tiene main con un commit, úsala sin cambios directos. Si no existe ninguna historia, detén las escrituras remotas y explica al propietario la necesidad de autorizar una inicialización mínima de main.

La inicialización autorizada debe contener solamente metadatos mínimos, sin implementación de la aplicación ni sustitución del primer PR. Puede prepararse el commit inicial en una rama de bootstrap y establecer main apuntando a ese commit. Registra que fue inicialización técnica, no una PR. A partir de esa base, toda implementación, pruebas y CI entra por PR. No inventes una PR inicial ni coloques toda la fase 1 en main para resolver este problema.

### Configuración y comprobaciones remotas

Comprueba git y gh, autenticación existente, remoto, permisos, reglas y GitHub Actions. No mostrar tokens ni pedir que el usuario los pegue en el chat. Usa un mecanismo de autenticación autorizado; si falta, detalla el paso humano necesario y marca la publicación como pendiente.

Si los permisos y reglas existentes lo permiten, configura main para exigir PR y checks de CI, sin force-push ni borrado. Desactiva la eliminación automática de ramas del repositorio. No rebajes protecciones existentes. Si una regla de historial lineal impide el merge commit propuesto, informa el conflicto y acuerda un método que preserve evidencia sin vulnerar reglas.

No exigir una aprobación de otra persona cuando no existe revisor disponible ni intentar aprobar el propio PR como si fuera independiente. Respeta las aprobaciones ya requeridas. Puedes añadir un comentario de auto-revisión técnica identificado como tal; no es una aprobación humana externa.

En cada PR:
1. Describe requisitos cubiertos, decisiones, cambios, migraciones, riesgos y cómo probar.
2. Añade resultados locales reales con comandos, códigos de salida y cobertura disponible.
3. Incluye capturas reales cuando se cambie UI; no mockups como evidencia de ejecución.
4. Espera a los checks esperados del commit actual. Un workflow omitido, pendiente, cancelado o no ejecutado no cuenta como verde.
5. Comprueba que main sigue siendo la base y que el SHA de cabeza es el revisado. Integra solo con controles satisfactorios y respetando permisos/aprobaciones.
6. Conserva la rama y comprueba su existencia remota después del merge.
7. Registra URL de PR, rama y SHA en docs/github-delivery.md. Los resultados de checks posteriores al último commit se reportan al cierre de la ejecución, sin inventar referencias dentro de un commit aún no creado.

No esperes al último día para crear ramas ficticias a partir de una aplicación terminada. Los pushes/PRs son incrementales; «lista para entrega» se declara únicamente al terminar y verificar todas las fases.

## 11. CI desde la primera fase

Crea .github/workflows/ci.yml en fase 1, no al final. Debe ejecutarse al menos en pull_request hacia main y también en push a main para validar el resultado integrado. No excluir rutas de forma que los checks obligatorios desaparezcan de algunos PR.

Controles mínimos, creciendo con el código real de cada fase:

- Backend: instalar desde lockfile, Ruff lint/formato, mypy, pruebas unitarias e integración con PostgreSQL real, migraciones y umbrales de cobertura.
- Frontend: instalación reproducible, ESLint, Prettier --check, TypeScript, Vitest con cobertura y build de producción de Next.js.
- Infraestructura/E2E: validar Compose, construir imágenes, levantar el stack de prueba, esperar healthchecks, ejecutar Playwright y smoke tests. Fase 1 ya debe tener un smoke real del shell/health; se amplía en las fases siguientes.
- Escaneo de secretos y revisión de dependencias con herramientas mantenidas. No corregir vulnerabilidades mediante actualizaciones forzadas sin revisar compatibilidad. No dejar vulnerabilidades altas/críticas aplicables al código ejecutado sin resolver y declararlo listo.
- Publicación de informes de cobertura, resultados y trazas/capturas E2E como artefactos, evitando datos sensibles.

Usa permisos mínimos, tiempos máximos y cancelación de ejecuciones obsoletas cuando corresponda. No depender de secretos privados para que un PR de evaluación ejecute tests. PostgreSQL de tests debe ser un servicio Docker aislado o formar parte del Compose de tests. Fija las acciones y dependencias de forma reproducible tras verificar sus versiones.

No ejecutar código no confiable de PR con privilegios mediante pull_request_target. No usar continue-on-error, || true, tests vacíos, skips generales o desactivación de linters para simular verde. Un fallo de entorno se reporta como bloqueo, no como prueba aprobada.

## 12. Fases, ramas y criterios de salida

### Fase 0 — Auditoría inicial y preflight

Sin implementar funcionalidad todavía:
- Leer repositorio, instrucciones y estado real; inspeccionar cambios locales, ramas, commits, origin y archivos. No tocar cambios ajenos ni hacer stash sin autorización.
- Comprobar Docker, Compose, git/gh, red necesaria, versiones elegibles y permisos de GitHub.
- Verificar si hay main con historia, nombre/visibilidad del repositorio, reglas y eliminación automática de ramas.
- Identificar reutilización válida, conflictos y decisiones pendientes. No asumir que el PDF está en una ruta determinada: este archivo ya incluye sus requisitos; no subir el PDF original sin autorización.
- Preparar el informe de preflight y la matriz para incorporarlos en fase 1. Cualquier bloqueo de seguridad, destino o base Git se comunica antes de escribir remotamente.

Salida: inventario real, arquitectura adoptada, versiones verificadas, matriz y bloqueos. Fase 0 y 1 se ejecutan juntas únicamente cuando el preflight lo permita.

### Fase 1 — Base ejecutable, Docker y CI

Rama: feature/project-bootstrap.

Construir estructura backend/frontend, configuración, API health/readiness, shell React, Compose, migraciones iniciales necesarias para ese alcance, scripts de arranque/verificación, .env.example, gitignore, AGENTS.md, README inicial y plantilla PR. Crear pruebas reales del código inicial y cobertura >=80% sobre lo implementado, no pruebas vacías. Introducir CI completo para el alcance existente y registrar requisitos futuros como pendientes.

Incorporar docs/requirements-matrix.md, docs/implementation-state.md y este plan. No copiar archivos de otro proyecto ni usar convenciones de rutas no comprobadas.

Salida: clon/entorno limpio levanta la base con un comando; tests y builds pasan; primer PR real hacia main con CI verde y rama preservada. Detenerse aquí en la primera ejecución: no empezar auth ni dashboard funcional todavía.

### Fase 2 — Autenticación, empresas y seguridad base

Rama: feature/auth-tenancy.

Modelos/migraciones de empresas, usuarios, suscripciones y sesiones; seed idempotente de dos empresas; JWT, hashing, CSRF, login/logout/me y permisos. Definir dependencias de autorización, errores globales y configuración segura. Incluir UI mínima de login/sesión y pruebas de sesión/aislamiento, sin anticipar toda la gestión administrativa.

Salida: login real, User/Admin diferenciados, sesión recuperable y revocable, aislamiento demostrado, pruebas/CI/PR completados.

### Fase 3 — Usuarios, roles y licencias

Rama: feature/users-licenses.

Listar/crear/modificar usuarios autorizados; roles/estado con protección del último Admin; asignación/revocación e invariantes de capacidad. Contratos OpenAPI y pruebas negativas, de integridad y concurrencia. Las rutas obligatorias existentes deben mantenerse estables.

Salida: endpoints de licencias funcionales, ningún exceso ni duplicado en carreras y ninguna operación cruzada entre empresas. PR con CI verde; UI completa de gestión se termina en fase 5.

### Fase 4 — Consumo persistido, alertas y SSE

Rama: feature/usage-alerts-realtime.

GET /api/v1/usage, operación de demo idempotente, eventos/agregados mensuales, alerta transaccional y stream SSE. Probar igualdad agregado/eventos, límites, periodos, concurrencia, reinicios y reconexión. Probar el stream HTTP real y su comportamiento de autenticación.

Salida: consumo verificable en PostgreSQL, alerta única al exceso y métricas transmitidas sin contaminación entre tenants. Pruebas/CI/PR completados.

### Fase 5 — Dashboard y recorridos completos

Rama: feature/dashboard.

Construir la UI completa descrita en la sección 7, conectada a la API; Context/Query, gráficos, tabla interactiva, formularios y alertas, permisos visuales, SSE, carga diferida, responsive y accesibilidad. Añadir E2E de dos ventanas/sesiones para tiempo real y cuentas de diferentes empresas.

Salida: todos los flujos de usuario operan realmente, sin mocks en ejecución normal; cobertura, E2E, builds y PR satisfactorios.

### Fase 6 — Auditoría y endurecimiento

Rama para mejoras reales de pruebas y herramientas: feature/quality-hardening. Correcciones de bugs: fix/<hallazgo-real>, desde main actualizado, con PR propio y test de regresión. No crear ramas fix vacías para aparentar un flujo.

Auditar de extremo a extremo requisitos, seguridad, concurrencia, UX, rendimiento de renders, SSE, migraciones, arranque limpio, cobertura y CI. Registrar hallazgos con severidad, reproducción, impacto, causa y prueba. Si una prueba nueva descubre un bug en main, llevar la reproducción y corrección a su rama fix; integrar la corrección antes de declarar verde la auditoría. No mezclar hallazgos sin resolver en un PR que se pretende aprobar.

Salida: ninguna incidencia crítica/alta pendiente, requisitos obligatorios satisfechos y ninguna prueba obligatoria omitida. Ejecutar la verificación completa y dos E2E completos consecutivos como comprobación adicional contra intermitencias. Una prueba no ejecutada permanece pendiente.

### Fase 7 — Documentación y entrega verificable

Rama: feature/delivery-docs.

Completar README, arquitectura, supuestos, endpoints, permisos, pruebas, decisiones, limitaciones, demostración y matriz de cumplimiento. Revisar secretos en archivos y commits del trabajo, ramas preservadas y PRs auténticos. Preparar docs/delivery-report.md con evidencias y SHA del código efectivamente comprobado.

Integrar el PR documental con CI verde. Después, verificar origin/main desde un clon/worktree limpio autorizado, ejecutar arranque y verificación final, y comprobar CI del commit final. No registrar en un archivo una comprobación futura como ya realizada: el SHA final y enlaces posteriores al último commit se informan al usuario al cierre.

Salida: repositorio remoto completo, público y accesible según el requisito, todas las ramas usadas preservadas, PRs integrados y pruebas locales/remotas del código final verificadas. Compartir URL real del repositorio; no crear release, tag o despliegue de pago si no es necesario.

## 13. Documentación y evidencia

README.md debe contener problema resuelto, stack/versiones, decisiones arquitectónicas y por qué PostgreSQL; requisitos previos; arranque con un comando desde un clon limpio; URLs y acceso demo; roles/permisos; contratos de endpoints obligatorios; fuente del consumo y alcance de «tiempo real»; umbrales; supuestos; ejecución de pruebas; cobertura obtenida con fecha/SHA; flujo de ramas/PRs; CI y limitaciones conocidas.

Documentos mínimos:

- docs/architecture.md: arquitectura, modelo de datos y decisiones razonadas.
- docs/requirements-matrix.md: trazabilidad de R01–R24 a implementación/prueba/PR.
- docs/implementation-state.md: fases, ramas, último commit comprobado, siguiente paso y bloqueos.
- docs/testing.md: comandos, aislamiento de bases, cobertura y casos críticos.
- docs/github-delivery.md: ramas, PRs, merges y conservación remota.
- docs/qa-report.md: hallazgos reales y evidencia de regresión.
- docs/delivery-report.md: comprobaciones finales y limitaciones.

Una sección breve de decisiones arquitectónicas es suficiente; no producir decenas de documentos redundantes. Capturas y reportes deben corresponder a ejecuciones reales y datos sintéticos. No publicar logs con credenciales.

## 14. Definition of Done

La aplicación no se declara terminada mientras falte cualquiera de estos criterios:

- R01–R24 verificados, no simplemente marcados como implementados.
- FastAPI y React/Next.js/TypeScript/Tailwind funcionando con PostgreSQL Docker.
- Endpoints obligatorios conservados exactamente y validados.
- Roles, aislamiento, cupos, consumo y alertas resisten los casos negativos y concurrentes definidos.
- Dashboard conectado, responsive, con gráficos/tabla, carga diferida y actualizaciones demostradas en otra ventana.
- Arranque reproducible con un comando y datos persistentes sin pérdida al reiniciar.
- Todas las pruebas obligatorias aprobadas y cobertura exigida medida por capa.
- Linters, formato, tipos, builds y comprobaciones de seguridad satisfactorios.
- CI real verde en PRs y en el main final; no checks ausentes, cancelados o pendientes.
- Historial incremental con Conventional Commits, PRs hacia main y ramas preservadas en remoto.
- README y documentación coherentes con el comportamiento real.
- Sin secretos publicados ni hallazgos críticos/altos pendientes.

## 15. Respuesta obligatoria de Codex al cerrar cada ejecución

Informa con hechos comprobados:

1. Fase ejecutada, alcance completado y lo que no se implementó todavía.
2. Rama, commits, URL/estado del PR y merge cuando exista.
3. Archivos/componentes importantes modificados.
4. Comandos efectivamente ejecutados, códigos de salida, cantidades de pruebas y cobertura backend/frontend.
5. Checks remotos del commit correspondiente, no resultados de un commit anterior.
6. Hallazgos corregidos, riesgos, bloqueos y pruebas pendientes.
7. Instrucciones concretas para probar la fase y siguiente fase autorizable.

No afirmar «todo pasa» cuando no se pudo arrancar Docker, alcanzar GitHub, ejecutar Playwright o medir cobertura. No inventar enlaces, capturas, resultados ni personas que revisaron. Distingue código escrito, probado localmente, publicado y verificado remotamente.

## 16. Referencias técnicas externas

Las siguientes son documentación técnica de apoyo, no requisitos del PDF. Consulta la versión correspondiente al stack elegido; las decisiones originales de este plan están identificadas como tales.

- React/Next.js: `https://nextjs.org/docs` y `https://nextjs.org/docs/app/getting-started/installation`.
- JWT y hashing FastAPI: `https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/`.
- SSE FastAPI: `https://fastapi.tiangolo.com/tutorial/server-sent-events/`.
- Bloqueos PostgreSQL: `https://www.postgresql.org/docs/current/explicit-locking.html`.
- Protección CSRF OWASP: `https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html`.
- Umbrales Vitest: `https://vitest.dev/config/coverage`.
- Coverage.py: `https://coverage.readthedocs.io/en/latest/commands/cmd_report.html` y `https://coverage.readthedocs.io/en/latest/branch.html`.
- GitHub PRs: `https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request`.
- GitHub Actions con PostgreSQL: `https://docs.github.com/actions/guides/creating-postgresql-service-containers`.
- GitHub CLI merge: `https://cli.github.com/manual/gh_pr_merge`.
- Codex AGENTS.md: `https://developers.openai.com/codex/agent-configuration/agents-md`.

## 17. Orden inicial

Ejecuta ahora únicamente las fases 0 y 1. Si aparece un bloqueo no resoluble de manera segura —especialmente repositorio vacío sin base, destino remoto ambiguo, cambios ajenos o autenticación faltante— descríbelo y solicita solamente la intervención necesaria. En ausencia de bloqueos, implementa la base, ejecuta pruebas, crea commits incrementales, publica la rama, abre su PR, comprueba CI e integra según las reglas autorizadas. Conserva la rama. Entrega el informe de cierre y detente antes de la fase 2.

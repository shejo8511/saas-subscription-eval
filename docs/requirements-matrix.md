# Matriz de requisitos

Se conserva la distinción entre PDF, elección del propietario y decisiones del plan. Pendiente significa sin evidencia suficiente; los requisitos de fases futuras no se atribuyen al bootstrap.

| ID | Requisito | Origen | Evidencia de aceptación | Implementación | Pruebas | Fase | PR | Evidencia actual | Estado |
|---|---|---|---|---|---|---|---|---|---|
| R01 | Administradores gestionan licencias de empleados corporativos | PDF, p. 1 | Recorrido real de asignación, consulta y gestión desde UI/API | — | — | 3,5 | — | — | Pendiente |
| R02 | Asignar roles | PDF, p. 1 | Admin cambia rol; User no puede escalar privilegios | — | — | 2,3 | — | — | Pendiente |
| R03 | Ver consumo de API en tiempo real | PDF, p. 1 | Una operación real modifica datos persistidos y otra ventana recibe la actualización | — | — | 4,5 | — | — | Pendiente |
| R04 | Alertas al superar el límite contratado | PDF, p. 1 | Cruce del límite produce alerta persistida y visible | — | — | 4,5 | — | — | Pendiente |
| R05 | Python con FastAPI | Elección permitida por PDF, p. 1 | API implementada en FastAPI | — | — | 1 | — | — | Pendiente |
| R06 | React; el PDF concreta React (Next.js), TypeScript y TailwindCSS | Elección del propietario y PDF, p. 1 | Frontend React/Next.js tipado, con Tailwind | — | — | 1 | — | — | Pendiente |
| R07 | PostgreSQL ejecutándose en Docker | Elección permitida por PDF, p. 1 | Servicio PostgreSQL con persistencia y healthcheck | — | — | 1 | — | — | Pendiente |
| R08 | Cobertura mínima del 80%; pruebas unitarias y de integración | PDF, p. 1, y propietario | Informes reproducibles y umbrales que hagan fallar CI | — | — | 1–7 | — | — | Pendiente |
| R09 | Repositorio público saas-subscription-eval y acceso compartido | PDF, p. 1 | URL, nombre y visibilidad comprobados; no recrear el repositorio existente | — | — | 0,7 | — | — | Pendiente |
| R10 | Carpetas backend/frontend o monorepo | PDF, p. 1 | Estructura sencilla con /backend y /frontend | — | — | 1 | — | — | Pendiente |
| R11 | No desarrollar directamente en main; ramas feature/…, fix/…; PRs hacia main | PDF, p. 1 | PRs reales y su historial | — | — | 1–7 | — | — | Pendiente |
| R12 | No borrar ramas integradas | PDF, p. 1 | Ramas de trabajo todavía presentes en el remoto | — | — | 1–7 | — | — | Pendiente |
| R13 | Conventional Commits; evitar un único commit gigante | PDF, p. 2 | Commits incrementales, coherentes y rastreables | — | — | 1–7 | — | — | Pendiente |
| R14 | README profesional: arquitectura, decisiones, ejecución con un comando y supuestos | PDF, p. 2 | Un evaluador reproduce los pasos desde un clon limpio | — | — | 1,7 | — | — | Pendiente |
| R15 | Autenticación JWT con roles Admin y User | PDF, p. 2 | Pruebas de autenticación, autorización y expiración | — | — | 2 | — | — | Pendiente |
| R16 | GET /api/v1/usage devuelve métricas de la empresa | PDF, p. 2 | Contrato y pruebas con PostgreSQL | — | — | 4 | — | — | Pendiente |
| R17 | POST /api/v1/licenses/assign asigna licencia y valida el máximo | PDF, p. 2 | Pruebas de capacidad, duplicados y concurrencia | — | — | 3 | — | — | Pendiente |
| R18 | Manejo global de errores y validación de entradas | PDF, p. 2 | Esquemas, errores consistentes y pruebas negativas | — | — | 2–4 | — | — | Pendiente |
| R19 | Gestión eficiente de estado global | PDF, p. 2 | Context para sesión/UI; datos remotos gestionados sin duplicación innecesaria | — | — | 5 | — | — | Pendiente |
| R20 | Dashboard responsive, gráficos de consumo y tabla interactiva de usuarios | PDF, p. 3 | UI conectada al backend; pruebas de escritorio y móvil | — | — | 5 | — | — | Pendiente |
| R21 | Lazy loading y optimización de renders | PDF, p. 3 | Separación de módulos, carga diferida y evidencia de comportamiento | — | — | 5 | — | — | Pendiente |
| R22 | docker-compose.yml orquesta base de datos, backend y frontend | PDF, p. 3 | Arranque, salud, persistencia y reconstrucción comprobados | — | — | 1 | — | — | Pendiente |
| R23 | .github/workflows/ci.yml en cada PR hacia main | PDF, p. 3 | Ejecución remota real sobre los commits entregados | — | — | 1 | — | — | Pendiente |
| R24 | CI ejecuta ESLint/Prettier y pruebas; resultado verde | PDF, p. 3 | Checks completos y satisfactorios, no solo archivo YAML | — | — | 1–7 | — | — | Pendiente |

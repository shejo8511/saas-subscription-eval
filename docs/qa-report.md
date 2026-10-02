# QA — bootstrap

## Corrección posterior: presupuesto del healthcheck Python

2026-10-02: durante la fase 2 se reprodujo también en el backend integrado de fase 1 que Docker mataba el probe a los 5 segundos. Se midieron 9,38 segundos solamente para importar urllib en el host local bajo carga. La corrección independiente se desarrolla en fix/readiness-probe-timeout desde main, sin modificar la historia del bootstrap. El presupuesto del proceso es 20 segundos; conserva la llamada real a /ready, su timeout HTTP de 4 segundos, el timeout SQL y la exigencia de HTTP 200. Los errores siguen haciendo fallar el healthcheck; no se reemplaza por health ni se acepta un 503. CI y reproducción local se comprueban en el commit correspondiente antes de integrar.

Hallazgos reales durante el desarrollo, sin crear ramas fix artificiales: todos pertenecen a código aún no integrado de fase 1.

| Hallazgo | Corrección | Evidencia |
|---|---|---|
| Docker daemon apagado | Iniciar Docker Desktop; sin cambiar context ni borrar datos | docker info retorna 28.0.4 |
| Python local sin CA predeterminada | Usar CA del sistema para preflight, TLS validado | Consultas npm/PyPI/GitHub completas |
| SQLAlchemy 2.1 no incluye greenlet por defecto | Extra asyncio explícito en lockfile | Prueba PostgreSQL real |
| Configuración completa Next arrastra plugins que no soportan ESLint 10 | Reglas oficiales Next + Hooks y typescript-eslint compatibles | ESLint y npm ci aprobados local/remoto |
| Node local 22.14 menor que el requerido por jsdom | Runtime Docker Node 22.23.3; portable oficial con checksum para comprobaciones locales | No se ignoran engines |
| Tipos Next/Vitest/MSW de la combinación inicial incompatibles | TypeScript 6, Vitest 4/jest-dom 6/MSW 2; sin skipLibCheck ni force | Tipos y builds aprobados; sin opciones de supresión |

Los comandos preliminares fallaron con códigos 1/2 y se corrigió su causa. También se corrigieron el import path de pytest y una actualización de estado al iniciar el efecto detectada por React Hooks; no se deshabilitó ninguna regla. npm 10 presentó un error interno de resolución (edgesOut); el lockfile definitivo se generó con npm 11.21.0 sin force/legacy-peer-deps. Se descartó jest-dom 6.10.0 por su deprecación y se fijó 6.9.1. Se hizo atómica la generación de .env para que una descarga fallida no dejase configuración parcial.

Verificaciones del producto: sin vulnerabilidades conocidas en el cierre transitivo de dependencias Python/frontend ni secretos detectados en Git/árbol autorizado. Este análisis se refiere a dependencias del proyecto: no certifica las bibliotecas del sistema operativo ni herramientas globales incluidas por las imágenes. Los avisos de dependencias empaquetadas de npm observados al instalar tooling temporal no están en package-lock.json del producto; no se presentó esa instalación como un scan limpio de la imagen completa.

Se inspeccionaron conjuntamente capturas reales de escritorio y móvil; no se encontraron cambios materiales necesarios para el shell. Detector mecánico: lista vacía. E2E comprueba 375/768/1440, consola, teclado y proxy real. No se extiende ese resultado a un dashboard aún inexistente. Capturas y procedencia en screenshots/README.md.

No quedan bloqueos de alcance fase 1 identificados. Autenticación, autorización, concurrencia de negocio y SSE no se han probado porque no forman parte de esta fase; permanecen pendientes en la matriz. El resultado del commit documental final se comprueba en GitHub después de escribirlo.

# QA — bootstrap

## Corrección posterior: presupuesto del healthcheck Python

2026-10-02: durante la fase 2 se reprodujo también en el backend integrado de fase 1 que Docker mataba el probe a los 5 segundos. Se midieron 9,38 segundos solamente para importar urllib en el host local bajo carga. La corrección independiente se desarrolla en fix/readiness-probe-timeout desde main, sin modificar la historia del bootstrap. El presupuesto del proceso es 20 segundos, con intervalo de 15 segundos para reducir el coste de lanzar intérpretes bajo carga; conserva la llamada real a /ready, su timeout HTTP de 4 segundos, el timeout SQL y la exigencia de HTTP 200. Los errores siguen haciendo fallar el healthcheck; no se reemplaza por health ni se acepta un 503. La espera global de arranque queda acotada a 600 segundos, sin cambiar el requisito de salud. CI y reproducción local se comprueban en el commit correspondiente antes de integrar.

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

## Fase 2 — hallazgos durante implementación

- Baseline ejecutado en 54d679a, árbol idéntico a main c561650: ./scripts/verify.sh terminó con exit 1: backend 18 aprobado, frontend 20/22 con dos timeouts de 5 segundos bajo carga concurrente. No se atribuye una ejecución aprobada al baseline ni se inventa un defecto de negocio/una rama fix. La suite se repite con recursos acotados.
- Primera suite backend ampliada: 77 aprobadas y dos errores al preparar conexión PostgreSQL por timeout. Fixture auth usa el timeout configurable máximo permitido de 10 segundos; repetición posterior aprobó 82. Los fallos iniciales se conservan como evidencia, no se omiten pruebas.
- Primera suite frontend ampliada: 35/37, dos timeouts. Con un worker aprobó 37/37; no cambian umbrales ni aserciones. La limitación de procesos es parte explícita de la configuración para jsdom.
- Primer verify de fase 2: falló Ruff format sobre dos scripts porque el formato desde raíz infería 88 columnas y Docker desde backend aplica 100. Corrección en la misma rama de fase, con formato comprobado en el cwd del backend.
- Tipos Python detectaron Mapping versus dict y tipos distintos del insert con returning. Se corrigieron ambos sin suprimir mypy. API inputs sensibles usan SecretStr y handlers sin repetir valores.
- El foco inicial del formulario se ajustó para conservar la navegación por skip link; se mantiene foco de identidad/logout y errores. Detector mecánico UI: lista vacía. Inspección visual real y checks finales aún pendientes de registro.

Limitaciones de alcance: sin administración completa de usuarios/roles por API, licencias, consumo, alertas, SSE, gráficos, pagos, registro público ni recuperación de contraseña. El aislamiento probado aquí corresponde a auth; no certifica endpoints futuros. Auditoría de dependencias del proyecto, no de todas las bibliotecas de imágenes/OS. La demo local no es una certificación de seguridad de producción.
- CI sobre 76ab940 aprobó Backend, Frontend y Security; Stack detectó que ejecutar el archivo fixture por ruta no añadía /app a sys.path. Se corrige invocando el módulo tests.e2e_fixture; las integraciones/E2E vuelven a ejecutarse, sin modificar PYTHONPATH para esconder errores.
- CI detectó selectores E2E por substring que coincidían tanto con empresa como con nombre del empleado. Se cambiaron a texto exacto accesible; las 15 pruebas E2E y cuatro jobs aprobaron en 7423c85. Detector UI vacío; inspección conjunta de screenshots reales desktop/mobile sin cambios materiales necesarios.
- La generación Docker de archivos locales se ajustó al UID/GID del host para que 0600 siga siendo legible por el evaluador en Linux y macOS, sin publicar ni relajar permisos.

- La primera verificación Docker ampliada aprobó 86/87: una conexión de la prueba de integridad superó 3 segundos durante la build concurrente. También esa fixture usa ahora el timeout permitido de 10 segundos; se repite secuencialmente el control completo. No se modifica el timeout de producción ni se ignora el fallo.

- El smoke local de fase 2 y la demo original reprodujeron el defecto previo del healthcheck: 5 segundos para proceso Python completo, pero import urllib consumía 9,38 segundos bajo carga. Corrección independiente en PR #3: timeout de proceso 20 segundos, intervalo 15 segundos y espera global 600, conservando timeout HTTP 4, SQL/readiness real y errores. Stack secuencial de 24dcf8e aprobó 6 E2E, recreación/persistencia y arranque repetido, exit 0. Merge 51079de y sus cuatro checks aprobados. Una ejecución concurrente anterior falló (exit 1) por timeouts E2E; otra se interrumpió (exit 143) para aislar recursos, sin contarlas como verdes. Se detuvo temporalmente UI/API de la demo para liberar CPU, preservando su PostgreSQL y volumen.
- Se añadió rechazo de cookies no Secure para cualquier PUBLIC_ORIGIN HTTPS, también en desarrollo/test. 43 pruebas unitarias y los cuatro checks sobre 62a8c82 y a25f0bd aprobados; no se suprime ninguna regla.

- Verify completo a25f0bd: backend 88 + tooling 5 aprobado y cobertura 425/452 líneas, 44/52 ramas; lint/formato/tipos frontend aprobados. Vitest 33/37, cuatro timeouts globales de 5 segundos (7,162 segundos en primera restauración), sin fallo de aserción. Exit global 1; stack/security no se ejecutaron en ese run. Incluye casos heredados del bootstrap, reproducidos también en el preflight: corrección independiente de presupuesto jsdom en fix/frontend-test-deadline / PR #4, antes de repetir controles completos. No se cuentan como verdes ejecuciones incompletas.

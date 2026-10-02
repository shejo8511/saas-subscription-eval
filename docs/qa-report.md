# QA — bootstrap

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

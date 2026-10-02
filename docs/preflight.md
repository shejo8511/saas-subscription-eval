# Preflight — fases 0 y 1

Fecha del cliente: 2026-10-01 (America/Guayaquil).

- Repositorio: https://github.com/shejo8511/saas-subscription-eval, público, main por defecto. Origin HTTPS existente conservado.
- Base: c9fe1e8abbae1f6cc708e38b58799f931bfa0ecd, `Initial commit`, únicamente README.md. Main y origin/main coinciden; árbol inicialmente limpio; no otras ramas remotas.
- No existen AGENTS.md en el repositorio ni en los directorios padres inspeccionados. README inicial contiene solamente el nombre del repositorio y se amplía dentro de la rama autorizada.
- El insumo autorizado se encontró en /Users/shejo8511/Downloads/CODEX_PLAN_SUSCRIPCIONES_B2B.md, se leyó completo y se incorporó a la raíz sin modificarlo. No se requiere ni se publica el PDF.
- Git 2.43.0; Python local 3.12.10; Node local 22.14.0; npm 10.9.2; uv 0.12.7. Docker 28.0.4 y Compose 2.34.0. Docker Desktop inicialmente apagado, iniciado y daemon operativo.
- GitHub CLI no estaba instalada. Homebrew intentó compilar una dependencia en macOS 13; se interrumpió esa instalación y se usó CLI oficial portable 2.102.0 fuera del repositorio.
- Autenticación existente recuperada desde el helper osxkeychain, sin publicar la credencial ni modificar origin. Cuenta shejo8511 con admin/push; scope workflow disponible. Falta read:org, innecesario para este repositorio personal.
- GitHub Actions habilitado. Sin rulesets ni protección inicial de main. Único colaborador comprobado: propietario; no se inventa un revisor.
- Eliminación automática de ramas ya desactivada. Merge commits permitidos. Se configuró protección de main: PR, checks Backend/Frontend/Stack/Security, base actualizada, también administradores; sin force-push ni borrado. Cero aprobaciones exigidas, sin reducir ninguna regla previa.
- Python local carecía de CA predeterminada: las consultas HTTPS de preflight usaron /etc/ssl/cert.pem con validación TLS activa.

Destino, base y permisos permiten fase 1. Las versiones de dependencias se consultaron en registros oficiales npm/PyPI y los tags concretos de imágenes en Docker Hub; selección y compatibilidad en architecture.md. Las comprobaciones de ejecución y publicación se registran después de realizarlas.

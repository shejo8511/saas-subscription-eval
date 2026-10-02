# Entrega GitHub — fase 1

Destino existente público: https://github.com/shejo8511/saas-subscription-eval. Origin conservado; base inicial c9fe1e8abbae1f6cc708e38b58799f931bfa0ecd.

[PR #1 hacia main](https://github.com/shejo8511/saas-subscription-eval/pull/1), rama feature/project-bootstrap, publicada incrementalmente.

| Commit | Cambio |
|---|---|
| 62b27e1 | docs(bootstrap): preflight y alcance autorizado |
| 17f404b | feat(api): readiness PostgreSQL y migración |
| f77433f | feat(web): shell español y estado real |
| e86dd1a | ci(bootstrap): stack aislado y controles |
| 4f738dc | fix(bootstrap): configuración local atómica |

Verificaciones reales antes del commit documental de cierre:

- [CI e86dd1a, run 36964260856](https://github.com/shejo8511/saas-subscription-eval/actions/runs/36964260856): Backend, Frontend, Stack y Security aprobados; seis E2E. Capturas del artefacto evidence-stack incorporadas en docs/screenshots/.
- [CI 4f738dc, run 36964467164](https://github.com/shejo8511/saas-subscription-eval/actions/runs/36964467164): los mismos cuatro jobs aprobados sobre 4f738dca9f21584d3505e996452c2d6345c75d8a.

Main protegido: PR, cuatro checks, base actualizada, administradores incluidos; cero revisiones requeridas, sin force-push/borrado. Sin reglas anteriores rebajadas. Merge commits permitidos. delete_branch_on_merge=false verificado; rama remota existente. No hay aprobación externa inventada.

Al escribir este documento, PR #1 sigue abierta y la integración del commit documental final aún debe comprobarse. SHA final, checks posteriores y merge se reportan al cerrar la sesión, después de existir; no se atribuyen los resultados anteriores al nuevo SHA. Consultar la PR enlazada para el estado posterior y merge real. La integración usa merge commit, exige el HEAD exacto y conserva la rama; nunca --admin ni --delete-branch.

## Cierre comprobado de fase 1 y apertura de fase 2

PR #1 integrada en c561650925f45b94eee4e9b0da1bae131f98580b; feature/project-bootstrap conservada en 54d679ab246c3ad9a96ddf730d473d6c1ada03b3. [CI del HEAD final bootstrap](https://github.com/shejo8511/saas-subscription-eval/actions/runs/36965354389) y [CI del merge](https://github.com/shejo8511/saas-subscription-eval/actions/runs/36965647685) aprobados; el registro previo describe el momento anterior al commit documental y no se reescribe.

2026-10-02: main actualizado continúa en c561650, sin cambios locales ni auth branch/PR previas. Origin y visibilidad pública conservados. Reglas verificadas: Backend/Frontend/Stack/Security, strict, administradores incluidos, cero aprobaciones requeridas, sin force-push/deletion y auto-delete false. Se crea feature/auth-tenancy en worktree propio para aislar la verificación histórica.

[PR real #2 hacia main](https://github.com/shejo8511/saas-subscription-eval/pull/2). Commits incrementales docs/tenancy/auth/dev/web/tests/format. La PR se abre en borrador mientras termina la evidencia. Checks del HEAD final y eventual merge se informan después de existir; ningún check anterior se atribuye al commit documental posterior. No hay revisión externa inventada ni autorización de fases posteriores.

Verificación remota comprobada del código antes del cierre documental: **7423c85baa1d4cbaac2992350d5bf5924cd1c6da**, [run 37020174511](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37020174511): Backend/Frontend/Stack/Security success, 87 pytest, 37 Vitest y 15 Playwright. No se atribuye esta ejecución al commit documental aún no creado; su CI y merge se comprobarán después y se informarán al cierre.

## Corrección independiente del bootstrap y base actualizada

Hallazgo reproducido del probe Python: [PR #3](https://github.com/shejo8511/saas-subscription-eval/pull/3), rama fix/readiness-probe-timeout desde main c561650. Commits 0423ec5 y 24dcf8e. Verificación local `./scripts/verify.sh stack` exit 0 sobre 24dcf8e, 6 E2E y persistencia/arranque repetido (reports/b2b-test-1790954235-34409). [CI del HEAD](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37025006597), cuatro checks success.

Merge normal comprobado: 51079deb9f4bc5a805f721b2f579b711f8129116; [CI del merge en main](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37027496727), Backend/Frontend/Stack/Security success. Sin bypass ni borrado; cero revisiones requeridas según protección strict vigente. La rama auth incorpora ese main mediante a25f0bdb178f3a06385379c39a50b2c931ad4f68, conservando seed, secretos y fixtures; conflictos de scripts resueltos con espera 600 y fase 2 intacta.

[CI del código actualizado a25f0bd](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37027573349): cuatro checks success, 88 pytest (43 unitarias / 45 integración PG), 37 Vitest, 15 E2E. Cobertura/backend 425/452 líneas y 44/52 ramas; frontend 124/124 líneas, 133/134 statements, 38/38 funciones y 104/106 ramas. Artefactos originales comprobados. Estos resultados anteceden al commit documental final y no se atribuyen a su futuro SHA.

## Corrección independiente del plazo jsdom

[PR #4](https://github.com/shejo8511/saas-subscription-eval/pull/4), rama fix/frontend-test-deadline desde main 51079de, commit eb137a73026270697ccfd52851db3dac2870c8b7. `./scripts/verify.sh frontend` exit 0 local: 22 regresiones, lint/formato/tipos/build y cobertura original 100/100/100/97,05%. Informes b2b-test-1790957424-67261. [CI del HEAD](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37032110460), cuatro checks success.

Merge normal 59dde884e7a9f7f9fc879cefad8281f88068e228; [CI del merge](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37033546639), cuatro checks success. Reglas strict, administradores incluidos y cero revisiones requeridas, auto-delete false comprobados antes de integrar. Rama conservada. Auth incorpora main en a3de1df8f0e9ef2823b446d19ed8344b8407bc7c; se conservan ambos registros QA y un worker/plazo 15 segundos, sin cambiar aserciones ni umbrales.

5b3c18e6136c98d06b8ffce4712ccb9b84031849 propaga LOGIN_WINDOW_SECONDS y SESSION_SECONDS en Compose con defaults originales: configuración efectiva personalizada comprobada exit 0 y [cuatro checks](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37032222380) success.

## Código de fase 2 y sincronización E2E comprobados

85cb8721bee645b45f9094a2f6ad49ad9c595e83 agrega sincronización explícita con HTTP 200 de login/logout antes de comprobar la identidad, sin modificar código de producción ni plazos de aserción. [CI 37048606099](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37048606099): Backend, Frontend, Stack y Security **success**, 88 pytest, 5 tooling, 37 Vitest y 15 E2E. Cero controles omitidos/cancelados. Los resultados del commit documental posterior y su posible merge se comprueban después de existir y se informan en PR/cierre, no en este registro anticipadamente.

## Corrección independiente de recorridos E2E y código final

[PR #5](https://github.com/shejo8511/saas-subscription-eval/pull/5), fix/browser-test-deadline desde main 59dde88, aaf6d842844b54c0e0b6ee90c929304a595a31f5. Sincroniza health/ready con HTTP real y acota el recorrido a 90 segundos; aserciones sin cambios. Stack local exit 0, 6 E2E, persistencia/recreación y segundo arranque. [CI HEAD 37063118128](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37063118128), cuatro checks success. Merge normal 9623188985b05a7494885cab6d1e44a46f1126b8; [CI main 37064994046](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37064994046), cuatro checks success. Auto-delete false y rama conservada, sin bypass.

116dd5f añadió restauración /me y cuentas independientes; su Stack falló 6/24 por una espera de cuerpo del helper, mientras los otros tres checks aprobaron. Corrección bec5aa2: status/JSON de identidad y UI; [CI 37064385368](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37064385368), cuatro checks y 24 E2E aprobados. 47f1ec5522dbcab667c882e706ed39320c84e662 incorpora main y aprueba [CI 37065043897](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37065043897) y verificador local completo exit 0, 88 pytest + 5 tooling, 37 Vitest, 24 E2E. Denominadores y fallos históricos en testing/QA.

El commit documental que contiene este registro todavía no existía al escribirlo. Sus checks y el eventual merge #2, CI posterior en main y comprobación limpia se informan después en PR/cierre. No se atribuyen resultados de 47f1ec5 a ese SHA futuro; nunca se inventan aprobaciones externas.

## Cierre de validación del helper y runtime

**f2b099f3a0ef2981b14f950e04b64cac3e512b2a**: `./scripts/verify.sh stack` local **exit 0**, reports/b2b-test-1790979860-1671, 24/24 E2E, tipos/build de producción, persistencia/recreación y segundo arranque. [CI exacto](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37068925887): Backend/Frontend/Stack/Security success, 43 unitarias + 45 integración PG, 5 tooling, 37 Vitest y 24 E2E; artefactos originales comprobados. Sin skips ni retries. Lint, formato y comprobación estricta del helper local: exit 0.

El diff 47f1ec5→f2b099f contiene únicamente documentos y el helper E2E de restauración. Backend, frontend runtime/configuración, lockfiles, Compose y scripts son idénticos: el all local exit 0 y sus coberturas corresponden explícitamente a 47f1ec5; la repetición local del stack y los cuatro checks remotos corresponden a f2b099f. Backend 425/452 líneas y 44/52 ramas; frontend 124/124 líneas, 133/134 statements, 38/38 funciones y 104/106 ramas. El fallo de 0b5b3d3 (23/24) permanece documentado como exit 1.

Primer stack local f2b099f: exit 1, 23/24, reports/b2b-test-1790977686-77991. Next registró ECONNRESET al proxy de /health; API no registró error de aplicación. Tras builds largos, Docker/VM consumían recursos elevados; es una observación, no una causa probada del reset. Se detuvo limpiamente PostgreSQL original, se reinició Docker Desktop y se restauró el mismo contenedor/volumen, comparados idénticos (exit 0). No se cambiaron código, configuración global, timeouts ni filtros de errores. La repetición conserva todas las pruebas y sus recursos propios se limpian.

El commit documental posterior y merge #2 se comprueban después de existir y se informan en PR/cierre, junto con CI en main, smoke limpio final y ramas conservadas. No se atribuyen resultados a un SHA futuro. **Detenerse antes de fase 3.**

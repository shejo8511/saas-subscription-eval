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

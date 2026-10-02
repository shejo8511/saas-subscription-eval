# Capturas reales de fase 1

Playwright contra Next.js → FastAPI → PostgreSQL, sin mocks, obtenido del artefacto evidence-stack de [CI 36964260856](https://github.com/shejo8511/saas-subscription-eval/actions/runs/36964260856), SHA e86dd1a4ae818b3b8202235208d8371193c1e134. El código visual permanece igual en 4f738dc (solo cambia arranque atómico).

- shell-desktop.png: 1440 px.
- shell-tablet.png: 768 px.
- shell-mobile.png: 375 px, captura de página completa.

No son mockups ni imágenes generadas. El estado disponible proviene de readiness real. Revisión visual conjunta escritorio/móvil: composición y texto legibles; sin scroll horizontal. Playwright verifica consola, navegación por teclado, foco y proxy; seis E2E aprobados. El detector mecánico de la UI devolvió lista vacía. Esta evidencia corresponde al shell de fase 1, sin dashboard de negocio.

Fase 2: auth-login-{desktop,tablet,mobile}.png y auth-session-{desktop,tablet,mobile}.png provienen del artefacto evidence-stack del [run 37020174511](https://github.com/shejo8511/saas-subscription-eval/actions/runs/37020174511), HEAD 7423c85baa1d4cbaac2992350d5bf5924cd1c6da. Playwright, UI real Next → FastAPI → PostgreSQL, 15 E2E aprobados en 1440/768/375. Login se captura con inputs vacíos; sesión muestra exclusivamente identidad pública sintética de fixtures, nunca passwords/cookies/tokens. Se inspeccionaron juntos login escritorio y sesión móvil, sin defectos materiales ni overflow. Las imágenes anteriores del shell se conservan como evidencia histórica.

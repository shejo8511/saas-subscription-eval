"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useSession } from "./session";

export function SessionPanel() {
  const session = useSession();
  const [validation, setValidation] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const emailInput = useRef<HTMLInputElement>(null);
  const identityHeading = useRef<HTMLHeadingElement>(null);
  const submitting = useRef(false);
  const shouldFocusEmail = useRef(false);

  useEffect(() => {
    if (session.state === "authenticated") {
      shouldFocusEmail.current = true;
      identityHeading.current?.focus();
    }
    if (session.state === "anonymous" && shouldFocusEmail.current)
      emailInput.current?.focus();
  }, [session.state]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting.current) return;
    if (
      !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.trim()) ||
      !password ||
      password.length > 128
    ) {
      setValidation(
        "Introduce un email válido y una contraseña de hasta 128 caracteres.",
      );
      emailInput.current?.focus();
      return;
    }
    setValidation("");
    submitting.current = true;
    shouldFocusEmail.current = true;
    try {
      await session.signIn(email, password);
      setPassword("");
    } catch {
      setPassword("");
    } finally {
      submitting.current = false;
    }
  }

  if (session.state === "checking")
    return (
      <section className="session-section" aria-live="polite" aria-busy="true">
        <h2>Comprobando sesión…</h2>
        <p>Espera un momento.</p>
      </section>
    );
  if (session.state === "network-error" || session.state === "server-error")
    return (
      <section className="session-section">
        <h2>No pudimos comprobar tu sesión</h2>
        <p role="alert">
          {session.state === "network-error"
            ? "No hay conexión con el servicio."
            : "El servicio no está disponible."}
        </p>
        <button onClick={session.retry}>Volver a intentar</button>
      </section>
    );
  if (session.identity)
    return (
      <section className="session-section" aria-labelledby="identity-heading">
        <h2 id="identity-heading" ref={identityHeading} tabIndex={-1}>
          Tu sesión
        </h2>
        <dl className="identity-details">
          <div>
            <dt>Empresa</dt>
            <dd>{session.identity.company.name}</dd>
          </div>
          <div>
            <dt>Nombre</dt>
            <dd>{session.identity.name}</dd>
          </div>
          <div>
            <dt>Email</dt>
            <dd>{session.identity.email}</dd>
          </div>
          <div>
            <dt>Rol</dt>
            <dd>{session.identity.role}</dd>
          </div>
        </dl>
        <p>
          La gestión de usuarios y licencias se incorporará en próximas fases.
        </p>
        {session.error && (
          <p role="alert" className="form-error">
            {session.error.message}
          </p>
        )}
        <button
          disabled={session.pending}
          onClick={() => {
            void session.signOut().catch(() => {});
          }}
        >
          Cerrar sesión
        </button>
      </section>
    );
  const error = validation || session.error?.message;
  return (
    <section className="session-section" aria-labelledby="login-heading">
      <h2 id="login-heading">Iniciar sesión</h2>
      <p>Usa una cuenta de la demostración local para acceder a tu empresa.</p>
      <form
        onSubmit={(event) => {
          void submit(event);
        }}
        noValidate
        className="login-form"
      >
        <label htmlFor="email">Email</label>
        <input
          ref={emailInput}
          id="email"
          type="email"
          autoComplete="username"
          maxLength={254}
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          aria-describedby={error ? "login-error" : undefined}
          aria-invalid={Boolean(validation)}
        />
        <label htmlFor="password">Contraseña</label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          maxLength={128}
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          aria-describedby={error ? "login-error" : undefined}
        />
        {error && (
          <p id="login-error" role="alert" className="form-error">
            {error}
          </p>
        )}
        <button type="submit" disabled={session.pending}>
          Entrar
        </button>
      </form>
    </section>
  );
}

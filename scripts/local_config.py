"""Atomic, locked localhost-only configuration; invoked inside the pinned Python image."""

import fcntl
import json
import os
import secrets
import tempfile
from pathlib import Path


def atomic_write(path: Path, content: str) -> None:
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def prepare(root: Path) -> None:
    local = root / ".local"
    local.mkdir(mode=0o700, exist_ok=True)
    with (local / "bootstrap.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        environment = root / ".env"
        content = environment.read_text() if environment.exists() else ""
        values = dict(
            line.split("=", 1)
            for line in content.splitlines()
            if "=" in line and not line.startswith("#")
        )
        defaults = {
            "POSTGRES_PASSWORD": secrets.token_hex(24),
            "POSTGRES_USER": "b2b",
            "POSTGRES_DB": "b2b_dev",
            "WEB_PORT": "3000",
            "JWT_SECRET": secrets.token_hex(32),
            "CSRF_SECRET": secrets.token_hex(32),
            "ENVIRONMENT": "development",
            "COOKIE_SECURE": "false",
            "DEMO_SEED": "true",
        }
        additions = {key: value for key, value in defaults.items() if not values.get(key)}
        if additions:
            atomic_write(
                environment,
                content.rstrip("\n")
                + ("\n" if content else "")
                + "".join(f"{key}={value}\n" for key, value in additions.items()),
            )
        credentials = local / "demo-credentials.json"
        if not credentials.exists():
            accounts = [
                {
                    "company": company,
                    "name": f"{role} · {company}",
                    "role": role,
                    "email": f"{role.lower()}@{slug}.demo.invalid",
                    "password": secrets.token_urlsafe(24),
                }
                for company, slug in [
                    ("Empresa Aurora", "aurora"),
                    ("Empresa Pacífico", "pacifico"),
                ]
                for role in ("Admin", "User")
            ]
            atomic_write(credentials, json.dumps(accounts, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    prepare(Path("/workspace"))

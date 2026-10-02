import os
import secrets

# Independent ephemeral keys for this process; never demo credentials or committed values.
os.environ.setdefault("JWT_SECRET", secrets.token_hex(32))
os.environ.setdefault("CSRF_SECRET", secrets.token_hex(32))
os.environ.setdefault("ENVIRONMENT", "test")

os.environ["PUBLIC_ORIGIN"] = "http://localhost:3000"

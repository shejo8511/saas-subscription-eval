import importlib.util
import json
import stat
import tempfile
import unittest
from pathlib import Path

specification = importlib.util.spec_from_file_location(
    "local_config", Path(__file__).parents[1] / "local_config.py"
)
assert specification and specification.loader
module = importlib.util.module_from_spec(specification)
specification.loader.exec_module(module)


class LocalConfigurationTests(unittest.TestCase):
    def test_existing_settings_credentials_and_permissions_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text(
                "POSTGRES_PASSWORD=owner-value\nWEB_PORT=3001\nCUSTOM=preserved\n"
            )
            module.prepare(root)
            environment = (root / ".env").read_bytes()
            credentials = (root / ".local/demo-credentials.json").read_bytes()
            accounts = json.loads(credentials)
            self.assertEqual(len(accounts), 4)
            self.assertEqual(len({a["password"] for a in accounts}), 4)
            self.assertIn(b"POSTGRES_PASSWORD=owner-value", environment)
            self.assertIn(b"CUSTOM=preserved", environment)
            self.assertEqual(stat.S_IMODE((root / ".env").stat().st_mode), 0o600)
            self.assertEqual(
                stat.S_IMODE((root / ".local/demo-credentials.json").stat().st_mode),
                0o600,
            )
            module.prepare(root)
            self.assertEqual((root / ".env").read_bytes(), environment)
            self.assertEqual((root / ".local/demo-credentials.json").read_bytes(), credentials)

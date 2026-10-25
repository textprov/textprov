"""Package contracts, plus an opt-in native discovery check with no model turn."""

import ast
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
import unittest

from textprov import strip_marks


PLUGIN = Path(__file__).resolve().parents[1]
EXPECTED_EVENTS = {"preToolUse", "postToolUse", "userPromptSubmit", "subagentStop", "stop"}


class PackagingTests(unittest.TestCase):
    def test_compatibility_manifest_remains_the_selected_entry_point(self):
        # Codex 0.159.2 selects root plugin.json first, then explicitly skips
        # hooks for that AgentPlugin format. An overlay cannot repair it.
        self.assertFalse((PLUGIN / "plugin.json").exists())
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], "textprov")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["hooks"], "./hooks/hooks.json")
        self.assertTrue((PLUGIN / manifest["skills"] / "textprov/SKILL.md").is_file())
        self.assertTrue((PLUGIN / manifest["hooks"]).is_file())
        module = ast.parse((PLUGIN / "textprov_codex.py").read_text())
        version = next(ast.literal_eval(node.value) for node in module.body
                       if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == "VERSION"
                               for target in node.targets))
        self.assertEqual(manifest["version"], version)
        self.assertIn("Version: **" + version + "**", strip_marks((PLUGIN / "README.md").read_text()))

    @unittest.skipUnless(os.environ.get("TEXTPROV_CODEX_BINARY"),
                         "set TEXTPROV_CODEX_BINARY for native plugin discovery")
    def test_native_installed_package_exposes_five_untrusted_plugin_hooks(self):
        binary = str(Path(os.environ["TEXTPROV_CODEX_BINARY"]).resolve(strict=True))
        with tempfile.TemporaryDirectory(prefix="textprov-codex-package-") as directory:
            root = Path(directory).resolve()
            home, project, marketplace = (root / name for name in ("codex-home", "project", "marketplace"))
            home.mkdir(mode=0o700)
            project.mkdir()
            (home / "config.toml").write_text('cli_auth_credentials_store = "file"\n[analytics]\nenabled = false\n')
            shutil.copytree(PLUGIN, marketplace / "plugins/textprov",
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            catalog = marketplace / ".agents/plugins/marketplace.json"
            catalog.parent.mkdir(parents=True)
            catalog.write_text(json.dumps({"name": "textprov-test", "plugins": [{
                "name": "textprov", "source": {"source": "local", "path": "./plugins/textprov"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity"}]}))
            env = dict(os.environ, CODEX_HOME=str(home))
            for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "PLUGIN_ROOT", "PLUGIN_DATA"):
                env.pop(key, None)

            def cli(*args):
                result = subprocess.run([binary, *args], cwd=project, env=env,
                                        capture_output=True, text=True, timeout=40)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)

            cli("plugin", "marketplace", "add", str(marketplace), "--json")
            installed = cli("plugin", "add", "textprov@textprov-test", "--json")
            installed_root = Path(installed["installedPath"])
            self.assertEqual(installed["version"], json.loads(
                (PLUGIN / ".codex-plugin/plugin.json").read_text())["version"])
            with tempfile.TemporaryFile(mode="w+") as stderr:
                process = subprocess.Popen([binary, "app-server", "--stdio"], cwd=project, env=env,
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=stderr, text=True, bufsize=1)
                incoming = queue.Queue()

                def read_messages():
                    for line in process.stdout:
                        incoming.put(json.loads(line))

                reader = threading.Thread(target=read_messages, daemon=True)
                reader.start()

                def request(identity, method, params):
                    process.stdin.write(json.dumps({"id": identity, "method": method, "params": params}) + "\n")
                    process.stdin.flush()
                    while True:
                        message = incoming.get(timeout=40)
                        if message.get("id") == identity:
                            self.assertNotIn("error", message, message)
                            return message["result"]

                try:
                    request(1, "initialize", {"clientInfo": {"name": "textprov_packaging_test", "version": "1"},
                                              "capabilities": {"experimentalApi": True}})
                    process.stdin.write('{"method":"initialized"}\n')
                    process.stdin.flush()
                    detail = request(2, "plugin/read", {"pluginName": "textprov", "marketplacePath": str(catalog)})["plugin"]
                    self.assertTrue(detail["summary"]["installed"])
                    self.assertTrue(detail["summary"]["enabled"])
                    self.assertEqual({item["name"] for item in detail["skills"]}, {"textprov:textprov"})
                    self.assertEqual({hook["eventName"] for hook in detail["hooks"]}, EXPECTED_EVENTS)
                    inventory = request(3, "hooks/list", {"cwds": [str(project)]})["data"]
                    self.assertEqual(len(inventory), 1)
                    self.assertEqual(inventory[0]["errors"], [])
                    self.assertEqual(inventory[0]["warnings"], [])
                    hooks = inventory[0]["hooks"]
                    self.assertEqual(len(hooks), 5)
                    self.assertEqual({hook["eventName"] for hook in hooks}, EXPECTED_EVENTS)
                    for hook in hooks:
                        self.assertEqual(hook["source"], "plugin")
                        self.assertEqual(hook["pluginId"], "textprov@textprov-test")
                        self.assertEqual(hook["trustStatus"], "untrusted")
                        self.assertFalse(hook["isManaged"])
                        self.assertEqual(Path(hook["sourcePath"]), installed_root / "hooks/hooks.json")
                        self.assertEqual(hook["command"], '"' + str(installed_root / "bin/textprov") + '" hook')
                    self.assertFalse((home / "hooks.json").exists())
                    self.assertFalse(list(home.rglob("chronicle.sqlite")))
                finally:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                    reader.join(timeout=5)
                    process.stdin.close()
                    process.stdout.close()


if __name__ == "__main__":
    unittest.main()

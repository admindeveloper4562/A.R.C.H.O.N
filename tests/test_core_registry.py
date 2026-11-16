import json
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import CoreRegistryError, CoreService, ModuleRegistry


ROOT = Path(__file__).resolve().parents[1]


class CoreRegistryTests(unittest.TestCase):
    def test_config_registers_ten_stable_modules_without_business(self):
        service = CoreService.from_config(ROOT / "config/modules.json")

        modules = service.registry.all()
        self.assertEqual([item.module_id for item in modules], list(range(1, 11)))
        self.assertEqual(service.module("core"), modules[0])
        self.assertNotIn("business", [item.key for item in modules])
        self.assertEqual(service.module(9).key, "guardian")
        self.assertTrue(service.can("core", "core:read"))
        self.assertTrue(service.can(10, "automation:health"))
        self.assertFalse(service.can("core", "sda:read"))

    def test_registry_and_capabilities_are_immutable(self):
        registry = CoreService.from_config(ROOT / "config/modules.json").registry

        with self.assertRaises(TypeError):
            registry.by_id[1] = registry.resolve(1)
        with self.assertRaises(AttributeError):
            registry.resolve(1).permission_scopes.add("core:write")

    def test_invalid_identity_scope_and_business_config_are_rejected(self):
        registry = CoreService.from_config(ROOT / "config/modules.json").registry
        for identity in (True, 0, "business", None):
            with self.subTest(identity=identity), self.assertRaises(CoreRegistryError):
                registry.resolve(identity)
        with self.assertRaises(CoreRegistryError):
            registry.authorize("core", "")

        with tempfile.TemporaryDirectory() as directory:
            config = json.loads((ROOT / "config/modules.json").read_text(encoding="utf-8"))
            config["business_module_enabled"] = True
            path = Path(directory) / "modules.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaises(CoreRegistryError):
                ModuleRegistry.from_config(path)


if __name__ == "__main__":
    unittest.main()

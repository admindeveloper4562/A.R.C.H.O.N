import unittest

from jarvis_v2.backend.module_manifest import (
    ManifestValidationError,
    MODULE_IDS,
    validate_module_manifest,
    validate_module_manifests,
)


def manifest(module_id, *, dependencies=None, scopes=None, label=None):
    key = MODULE_IDS[module_id]
    return {
        "module_id": module_id,
        "key": key,
        "dependencies": list(dependencies if dependencies is not None else {
            "core": (), "sda": ("core",), "backend": ("core",),
            "runtime": ("backend", "core"), "research": ("backend",),
            "tws": ("backend",), "wic": ("backend",),
            "finance": ("backend",), "guardian": ("backend",),
            "automation": ("backend", "core"),
        }[key]),
        "health_endpoint_label": key if label is None else label,
        "permission_scopes": list(scopes if scopes is not None else (f"{key}:read",)),
    }


class BackendManifestTests(unittest.TestCase):
    def test_complete_active_set_is_typed_and_stable(self):
        validated = validate_module_manifests([manifest(i) for i in range(1, 11)])
        self.assertEqual([item.module_id for item in validated], list(range(1, 11)))
        self.assertEqual([item.key for item in validated], list(MODULE_IDS.values()))
        self.assertNotIn("business", [item.key for item in validated])

    def test_malformed_and_incomplete_manifests_are_rejected(self):
        with self.assertRaises(ManifestValidationError):
            validate_module_manifest({"module_id": 3})
        with self.assertRaises(ManifestValidationError):
            validate_module_manifests([manifest(i) for i in range(1, 10)])
        with self.assertRaises(ManifestValidationError):
            validate_module_manifests([manifest(i) for i in range(1, 10)] + [manifest(3)])

    def test_unknown_dependency_and_permission_escalation_are_rejected(self):
        with self.assertRaises(ManifestValidationError):
            validate_module_manifest(manifest(3, dependencies=("core", "business")))
        with self.assertRaises(ManifestValidationError):
            validate_module_manifest(manifest(3, scopes=("backend:read", "core:admin")))

    def test_health_label_and_identity_are_bound_to_stable_key(self):
        with self.assertRaises(ManifestValidationError):
            validate_module_manifest(manifest(3, label="/health/backend"))
        wrong_key = manifest(3)
        wrong_key["key"] = "business"
        with self.assertRaises(ManifestValidationError):
            validate_module_manifest(wrong_key)


if __name__ == "__main__":
    unittest.main()

import unittest

from jarvis_v2.tws import (
    MAGIC,
    ModelValidationError,
    build_portable_model,
    default_aurelia_spec,
    validate_portable_model,
)


class TWSAureliaModelTests(unittest.TestCase):
    def test_generation_and_validation_are_deterministic(self):
        spec = default_aurelia_spec()
        first = build_portable_model(spec)
        second = build_portable_model(spec)
        self.assertEqual(first, second)
        result = validate_portable_model(first)
        self.assertEqual(result["model_id"], "aurelia")
        self.assertEqual(result["vertex_count"], 3)
        self.assertEqual(result["assertions"], {
            "deformation": True,
            "morphs": True,
            "clips": True,
        })

    def test_validator_rejects_deformation_and_clip_corruption(self):
        package = build_portable_model(default_aurelia_spec())
        payload_start = len(MAGIC) + 4
        broken_weights = package[:payload_start] + package[payload_start:].replace(b'"weight":1.0', b'"weight":0.9', 1)
        with self.assertRaisesRegex(ModelValidationError, "sum to one"):
            validate_portable_model(broken_weights)
        broken_clip = package[:payload_start] + package[payload_start:].replace(b'"time_ms":1000', b'"time_ms":2000', 1)
        with self.assertRaisesRegex(ModelValidationError, "keyframe time"):
            validate_portable_model(broken_clip)

    def test_builder_rejects_unknown_deformation_bone(self):
        spec = default_aurelia_spec()
        spec["deformation"]["weights"][0]["bone"] = "missing"
        with self.assertRaisesRegex(ModelValidationError, "unknown"):
            build_portable_model(spec)


if __name__ == "__main__":
    unittest.main()

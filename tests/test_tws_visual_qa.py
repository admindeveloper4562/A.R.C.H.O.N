import unittest

from jarvis_v2.tws import ModelValidationError, validate_visual_qa_manifest


def manifest():
    return {
        "task_id": "TWS-012",
        "source": {"sha256": "a" * 64},
        "tool": {"name": "Blender", "version": "5.3.0"},
        "views": [{"index": i, "path": f"view_{i:02d}.png", "sha256": "b" * 64} for i in range(24)],
        "motion_present": True,
        "motion_actions": ["Greeting"],
        "actions": [{
            "track": "Greeting",
            "pose_changed": True,
            "samples": [{"frame": i, "pose_sha256": "c" * 64} for i in (1, 36, 72)],
        }],
    }


class TWSVisualQATests(unittest.TestCase):
    def test_manifest_requires_24_views_and_motion_samples(self):
        result = validate_visual_qa_manifest(manifest())
        self.assertEqual(result["view_count"], 24)
        self.assertEqual(result["motion_actions"], ("Greeting",))

    def test_manifest_rejects_static_motion(self):
        broken = manifest()
        broken["motion_present"] = False
        with self.assertRaisesRegex(ModelValidationError, "motion evidence"):
            validate_visual_qa_manifest(broken)

    def test_manifest_rejects_duplicate_view_index(self):
        broken = manifest()
        broken["views"][1]["index"] = 0
        with self.assertRaisesRegex(ModelValidationError, "24 unique views"):
            validate_visual_qa_manifest(broken)


if __name__ == "__main__":
    unittest.main()

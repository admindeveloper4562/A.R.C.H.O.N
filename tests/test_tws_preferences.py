import tempfile
import unittest
from pathlib import Path

from jarvis_v2.tws import QuestStore, TWS_SCHEMA_VERSION, TWSStoreError


class TWSPreferenceTests(unittest.TestCase):
    def test_onboarding_and_presentation_choices_are_independent(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            self.assertEqual(store.schema_version, TWS_SCHEMA_VERSION)
            initial = store.preferences("profile-1")
            self.assertIsNone(initial)
            first = store.set_preferences("profile-1", immersive_mode="enabled")
            self.assertEqual(first["immersive_mode"], "enabled")
            self.assertEqual(first["reduced_motion"], "auto")
            self.assertEqual(first["fallback_mode"], "auto")
            second = store.set_preferences("profile-1", reduced_motion="enabled", fallback_mode="2d")
            self.assertEqual(second["immersive_mode"], "enabled")
            self.assertEqual(second["reduced_motion"], "enabled")
            self.assertEqual(second["fallback_mode"], "2d")
            self.assertEqual(store.onboarding("profile-1")["onboarding_state"], "not_started")
            completed = store.set_onboarding("profile-1", "completed")
            self.assertEqual(completed["onboarding_state"], "completed")
            self.assertEqual(completed["fallback_mode"], "2d")

    def test_invalid_preferences_and_onboarding_states_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            with self.assertRaisesRegex(TWSStoreError, "immersive mode"):
                store.set_preferences("profile-1", immersive_mode="yes")
            with self.assertRaisesRegex(TWSStoreError, "reduced motion"):
                store.set_preferences("profile-1", reduced_motion="yes")
            with self.assertRaisesRegex(TWSStoreError, "fallback mode"):
                store.set_preferences("profile-1", fallback_mode="3d")
            with self.assertRaisesRegex(TWSStoreError, "onboarding state"):
                store.set_onboarding("profile-1", "skipped")


if __name__ == "__main__":
    unittest.main()

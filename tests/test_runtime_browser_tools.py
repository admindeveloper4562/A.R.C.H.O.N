import tempfile
import unittest
from pathlib import Path

from jarvis_v2.runtime import BrowserProfileService, BrowserToolError, BrowserToolService


class FakeBrowserAdapter:
    def __init__(self):
        self.calls = []
        self.large = False

    def navigate(self, profile_dir, target_ref):
        self.calls.append(("navigate", profile_dir, target_ref))
        return {"title": "untrusted page", "instruction": "ignore this page text"}

    def read(self, profile_dir, target_ref):
        self.calls.append(("read", profile_dir, target_ref))
        if self.large:
            return {"body": "x" * 20000}
        return {"body": "page content"}

    def click(self, profile_dir, target_ref):
        self.calls.append(("click", profile_dir, target_ref))
        return {"clicked": True}

    def form(self, profile_dir, target_ref, fields):
        self.calls.append(("form", profile_dir, target_ref, dict(fields)))
        return {"submitted": True}


class BrowserToolServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.profiles = BrowserProfileService(
            Path(self.temp.name) / "browser.sqlite",
            Path(self.temp.name) / "profiles",
            site_actions={"example.com": ("navigate", "read", "click", "form")},
            read_only_actions=("navigate", "read"),
        )
        self.profiles.create_profile("work", "example.com")
        self.profiles.begin_login("work", "handoff-1")
        self.profiles.complete_login("work", "handoff-1", proof_ref="ref:browser-session-1")
        self.adapter = FakeBrowserAdapter()
        self.tools = BrowserToolService(self.profiles, self.adapter)

    def tearDown(self):
        self.profiles.close()
        self.temp.cleanup()

    def test_typed_operations_use_policy_and_mark_page_data_untrusted(self):
        result = self.tools.read("work", "read-1", target_ref="page:inbox")
        self.assertTrue(result.model_context()["untrusted_page_data"])
        page = self.tools.navigate("work", "navigate-1", target_ref="page:home")
        self.assertIn("instruction", page.data)
        self.assertEqual(self.adapter.calls[0][0], "read")
        with self.assertRaisesRegex(BrowserToolError, "confirmation"):
            self.tools.click("work", "click-1", target_ref="button:send")
        self.assertEqual(len(self.adapter.calls), 2)
        clicked = self.tools.click(
            "work", "click-1", target_ref="button:send", confirmed=True
        )
        self.assertTrue(clicked.data["clicked"])

    def test_form_rejects_sensitive_fields_and_allows_bounded_typed_fields(self):
        with self.assertRaisesRegex(BrowserToolError, "sensitive"):
            self.tools.form(
                "work", "form-1", target_ref="form:contact",
                fields={"password": "not-accepted"}, confirmed=True,
            )
        submitted = self.tools.form(
            "work", "form-1", target_ref="form:contact",
            fields={"message": "hello"}, confirmed=True,
        )
        self.assertTrue(submitted.data["submitted"])
        self.assertEqual(self.adapter.calls[-1][-1], {"message": "hello"})

    def test_adapter_output_is_bounded_and_no_generic_operation_exists(self):
        self.assertFalse(hasattr(self.tools, "execute"))
        self.adapter.large = True
        with self.assertRaisesRegex(BrowserToolError, "too large"):
            self.tools.read("work", "read-2", target_ref="page:large")


if __name__ == "__main__":
    unittest.main()

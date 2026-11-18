import sqlite3
import tempfile
import threading
import time
import unittest
from pathlib import Path

from astra_one.linux_sda import State


class EventReadinessTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.state = State(self.root)
        with sqlite3.connect(self.state.database) as db:
            db.execute("create table settings(key text primary key, value text not null)")
            db.execute("insert into settings values('ready','0')")

    def test_data_version_wakes_after_external_commit(self):
        observed = self.state.data_version()

        def commit():
            time.sleep(0.05)
            self.state.put("ready", "1")

        thread = threading.Thread(target=commit)
        thread.start()
        changed, current = self.state.wait_for_data_change(observed, timeout=2)
        thread.join()
        self.assertTrue(changed)
        self.assertNotEqual(current, observed)

    def test_data_version_wait_is_bounded(self):
        observed = self.state.data_version()
        started = time.monotonic()
        changed, current = self.state.wait_for_data_change(observed, timeout=0.1)
        self.assertFalse(changed)
        self.assertEqual(current, observed)
        self.assertLess(time.monotonic() - started, 1)


if __name__ == "__main__":
    unittest.main()

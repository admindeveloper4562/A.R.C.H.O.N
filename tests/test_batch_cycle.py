import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "astra_batch_cycle.sh"


class BatchCycleFailurePropagationTests(unittest.TestCase):
    def run_fixture(self, *, batch_status: str, batch_status_rc: int = 0,
                    qc_rc: int = 0):
        with tempfile.TemporaryDirectory(prefix="archon-batch-cycle-") as tmp:
            root = Path(tmp)
            (root / "tools").mkdir()
            shutil.copy2(SCRIPT, root / "tools" / "astra_batch_cycle.sh")
            (root / "bootstrap" / "astra-one").mkdir(parents=True)
            state = root / "state"
            state.mkdir()
            (state / "sda.sqlite3").touch()
            bin_dir = root / "bin"
            bin_dir.mkdir()
            log = root / "stub.log"
            stub = bin_dir / "python3"
            stub.write_text(
                "#!/usr/bin/env bash\n"
                "set -eu\n"
                "echo \"$*\" >> \"$STUB_LOG\"\n"
                "case \" $* \" in\n"
                "  *' supervisor-tick '*) printf '%s\\n' '{}' ;;\n"
                f"  *' batch-status '*) printf '%s\\n' '{batch_status}'; exit {batch_status_rc} ;;\n"
                "  *' - '*) exec /usr/bin/python3 \"$@\" ;;\n"
                f"  *' qc-merge '*) printf '%s\\n' '{{\"state\":\"failed\"}}'; exit {qc_rc} ;;\n"
                "  *) printf '%s\\n' '{}';;\n"
                "esac\n",
                encoding="utf-8",
            )
            stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
            env = {
                **os.environ,
                "ARCHON_ASTRA_HOME": str(state),
                "PATH": f"{bin_dir}:/usr/bin:/bin",
                "STUB_LOG": str(log),
            }
            result = subprocess.run(
                [str(root / "tools" / "astra_batch_cycle.sh")],
                cwd=root / "bootstrap" / "astra-one",
                env=env,
                text=True,
                capture_output=True,
            )
            return result, log.read_text(encoding="utf-8")

    def test_batch_status_failure_is_not_hidden(self):
        result, calls = self.run_fixture(batch_status="{}", batch_status_rc=17)
        self.assertEqual(result.returncode, 17, result.stderr)
        self.assertIn("batch-status failed", result.stderr)
        self.assertNotIn("qc-merge", calls)

    def test_qc_failure_stops_before_publication(self):
        result, calls = self.run_fixture(
            batch_status='{"completed_count":20,"target_count":20}', qc_rc=19
        )
        self.assertEqual(result.returncode, 19, result.stderr)
        self.assertIn("publication skipped", result.stderr)
        self.assertIn("qc-merge", calls)


if __name__ == "__main__":
    unittest.main()

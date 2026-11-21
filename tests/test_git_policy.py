import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.check_git_policy import check_branch, check_commit

ROOT = Path(__file__).resolve().parents[1]
class PolicyTests(unittest.TestCase):
 def test_good_branch(self):
  for b in ['main','develop','release/2.0.0','feat/core/CORE-004-durable-sessions','fix/guardian/GUARD-006-priority','docs/migration/MIG-003-source-provenance','feat/automation/AUTO-007-queue-reconnect','fix/release/REL-005-pending-jobs']:
   self.assertTrue(check_branch(b),b)
 def test_bad_branch(self):
  for b in ['feature/CORE-004-x','feat/core/CORE-004_wrong','feat/sda/CORE-004-oops','feat/business/FIN-001-x','feat/core/CORE-004-../x','release/2.00.0']:
   self.assertFalse(check_branch(b),b)
 def test_good_commit(self):
  self.assertTrue(check_commit('feat(core): persist durable task sessions [CORE-004]'))
  self.assertTrue(check_commit('test(guardian): verify next-slot reservation [GUARD-006]'))
 def test_bad_commit(self):
  for m in ['Update files','feat(core): Some stuff [CORE-004]','fix(sda): fix issue','feat(core): create thing. [CORE-004]']:
   self.assertFalse(check_commit(m),m)
 def test_pr_policy_ignores_synthetic_merge_commit(self):
  with tempfile.TemporaryDirectory() as temp:
   repo = Path(temp) / "repo"; bare = Path(temp) / "origin.git"
   subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True, text=True, timeout=10)
   subprocess.run(["git", "init", str(repo)], check=True, capture_output=True, text=True, timeout=10)
   def git(*args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, timeout=10)
   git("config", "user.name", "CI Test"); git("config", "user.email", "ci@example.invalid")
   git("checkout", "-b", "develop")
   (repo / "README.md").write_text("base\n", encoding="utf-8")
   git("add", "README.md"); git("commit", "-m", "chore(core): seed policy fixture [CORE-001]")
   git("remote", "add", "origin", str(bare)); git("push", "-u", "origin", "develop")
   branch = "fix/release/REL-016-ci-receipt-path"
   git("checkout", "-b", branch)
   (repo / "README.md").write_text("candidate\n", encoding="utf-8")
   git("commit", "-am", "fix(ci): repair artifact receipt paths [REL-016]")
   git("checkout", "develop"); git("merge", "--no-ff", branch, "-m", "Merge candidate into develop")
   scripts = repo / "tools"; scripts.mkdir()
   for name in ("check_pr_policy.sh", "check_git_policy.py"):
    shutil.copy2(ROOT / "tools" / name, scripts / name)
   env = os.environ.copy(); env.update({"GITHUB_HEAD_REF": branch, "GITHUB_BASE_REF": "develop"})
   result = subprocess.run(["bash", "tools/check_pr_policy.sh"], cwd=repo, env=env, capture_output=True, text=True, check=False, timeout=20)
   self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
if __name__=='__main__':unittest.main()

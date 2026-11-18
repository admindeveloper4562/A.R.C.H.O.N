import unittest
from tools.check_git_policy import check_branch, check_commit
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
if __name__=='__main__':unittest.main()
